# -*- coding: utf-8 -*-
"""locate_skeleton.py — 武器皮肤骨骼定位器（可复用）

用途
    · 由皮肤 id 或任意 .gim 逻辑路径定位同 stem 的 .mesh（含 _lod01/_preview/_shadow/_1/_2/_3 变体），
      解出骨骼块并落盘 SKEL_<id>_skeleton.json；支持全量跑 + 覆盖率汇总。

用法
    python locate_skeleton.py --id 1110024
    python locate_skeleton.py --gim weapon/skin/skin_1006_004/skin_1006_004.gim
    python locate_skeleton.py --all --out <dir>
    python locate_skeleton.py --all --no-variant-fallback      # 复现优化前覆盖率
    python locate_skeleton.py --id 1110024 --dump-mesh <file>  # 另存解压后的 .mesh

定位原理（2026-09 已定标，证据：%TEMP%\\sk_conv.txt）
    · .gpk 条目表 = AES-ECB 解密后 32 B/行 = [o, cmp, dec, c1, c2, fl, u32_6, u32_7]
        表位置：文件头 4096 B AES 解密，header[4:8] ∈ {HPGF, FPGH}，count = u32@20，表自偏移 64
        u32_6 = murmur3_x86_32(path, 0x66666666), u32_7 = murmur3_x86_32(path, 0x77777777)
        路径口径：反斜杠原样、latin1（例：weapon\\skin\\skin_1006_002\\skin_1006_002.mesh）
        载荷：off+36 起，按 flag 解压（0=原始/AES, 2=lz4, 12=zstd 多帧）
    · .gim 是模型文档（c159 对象图），几何/骨骼在 .mesh；两者同 stem。

.mesh 骨骼块（本工具实证，34 模型样本）
    0x00 u32 magic = 34 80 c8 bb
    0x04 u16 version = 4
    0x06 u16 const   = 5
    0x08 u16 bone_flag          1=含骨骼块 / 0=无（无则 u32@0x0A = 文件长度-16）
    0x0A u16 bone_count         （仅 bone_flag==1 有效）
    0x0C..: 父索引区，长度 = bone_count + 1 字节（= 0x0C+count 处即首个骨名）
            实证切分 B：byte[0x0D .. 0x0D+count-1] 对应 bone[1..count-1] 的父索引；0xFF=无父
            校验：parent < self_index（19/21 零违规；1110160/1110161 违规→hierarchy unresolved）
    骨名：起始 = 0x0C + bone_count（= 0x0E + bone_count - 2），步长实测 **32 B（21/21）**，16 B 步长在本批 0 命中
    逐骨块：names_end + 1 起，**92 B × bone_count**，尾部 1×u32（实测 gap = 1 + 92n + 4）
            字段语义 unresolved（无 4x4/3x4 矩阵行结构，未猜）
    sub 表：骨骼块之后，用 (term==1, tv==Σvc, tf==Σfc) 三重校验定位（同 mesh_parse2）

纪律：不猜；拿不到的字段写进 unresolved[]。
"""
import argparse
import glob
import hashlib
import io
import json
import os
import re
import struct
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "10_应用核心")))
try:
    from toolkit_core.resource_resolver import aes_ecb, murmur3_x86_32, unpack_entry  # noqa
except Exception:  # 兜底：允许以 --tools 指定工具库路径
    _tp = os.environ.get("NEOX_TOOLS")
    if _tp:
        sys.path.insert(0, _tp)
    from toolkit_core.resource_resolver import aes_ecb, murmur3_x86_32, unpack_entry  # noqa

DEFAULT_RES = r"E:\mrzh"
DEFAULT_OUT = r"E:\la拆包项目\03拆包产物\_gim_out\skel"
DEFAULT_ROSTER = r"E:\la拆包项目\03拆包产物\_target_1110171\ROSTER_g5_g6.json"
MAGIC = b"\x34\x80\xc8\xbb"
# 变体顺序：主 stem 优先，其后为实测存在的变体（_lod01.._lod03/_preview/_shadow 来自 .gim 文档；
# _1/_2/_3 为同目录兄弟网格，三个皮肤靠它们补到骨骼）
VARIANTS = ["", "_lod01", "_lod02", "_lod03", "_lod04", "_lod1", "_lod2", "_lod3", "_lod4", "_lod0",
            "_preview", "_high", "_1", "_2", "_3", "_shadow"]


def hkey(path):
    b = path.encode("latin1")
    return (murmur3_x86_32(b, 0x66666666), murmur3_x86_32(b, 0x77777777))


class GpkIndex:
    """91 个 .gpk 容器条目表（只读表，秒级）"""

    def __init__(self, res_dir=DEFAULT_RES, verbose=False):
        self.rows = {}
        self.containers = {}
        pats = [os.path.join(res_dir, "*.gpk"), os.path.join(res_dir, "res", "*.gpk"),
                os.path.join(res_dir, "Documents", "gres", "*.gpk")]
        files = sorted(set(sum((glob.glob(p) for p in pats), [])))
        for g in files:
            try:
                with open(g, "rb") as f:
                    hdr = aes_ecb(f.read(4096))
                    if hdr[4:8] not in (b"HPGF", b"FPGH"):
                        continue
                    n = struct.unpack_from("<I", hdr, 20)[0]
                    f.seek(64)
                    tab = aes_ecb(f.read(n * 32))
            except Exception:
                continue
            self.containers[g] = n
            for i in range(n):
                o, cm, de, c1, c2, fl, u6, u7 = struct.unpack_from("<IIIIIIII", tab, i * 32)
                self.rows[(u6, u7)] = (g, i, o, cm, de, fl)
            if verbose:
                sys.stderr.write("  indexed %-46s rows=%d\n" % (os.path.basename(g), n))

    def find(self, path):
        return self.rows.get(hkey(path))

    def read(self, path):
        """返回 (bytes|None, meta) ; meta = {container,row,off,comp,dec,flag}"""
        r = self.find(path)
        if not r:
            return None, None
        g, i, o, cm, de, fl = r
        with open(g, "rb") as f:
            f.seek(o + 36)
            raw = f.read(cm)
        meta = {"container": os.path.basename(g), "row": i, "off": o, "comp": cm, "dec": de, "flag": fl}
        try:
            return unpack_entry(raw, de, fl), meta
        except Exception as exc:
            meta["error"] = "unpack:%s" % exc
            return None, meta


def find_subtable(d, start, limit):
    for cand in range(start, min(len(d) - 34, limit)):
        if struct.unpack_from("<H", d, cand)[0] != 1:
            continue
        tv, tf = struct.unpack_from("<II", d, cand + 2)
        if tv == 0 or tf == 0:
            continue
        for k in range(1, 65):
            b = cand - 10 * k
            if b < 0:
                break
            subs = [struct.unpack_from("<IIH", d, b + 10 * i) for i in range(k)]
            if sum(s[0] for s in subs) == tv and sum(s[1] for s in subs) == tf:
                return {"sub_table_off": b, "term_off": cand, "k": k, "tv": tv, "tf": tf}
    return None


def detect_names(d, name_off, n, max_stride=64):
    """返回 {stride: [names]} 中所有通过校验的步长"""
    ok_all = {}
    for st in (16, 32, 48, 64):
        names = []
        ok = True
        for i in range(n):
            p = name_off + st * i
            if p + 1 >= len(d):
                ok = False
                break
            e = d.find(b"\x00", p)
            if e < 0 or not (2 <= e - p <= 40) or not re.fullmatch(rb"[\x20-\x7e]+", d[p:e]):
                ok = False
                break
            names.append(d[p:e].decode("latin1"))
        if ok:
            ok_all[st] = names
    return ok_all


def parse_mesh(d):
    """解析 .mesh 头与骨骼块；所有字段带偏移依据；不确定项进 unresolved"""
    r = {"magic": d[:4].hex(" "), "bytes": len(d), "sha256": hashlib.sha256(d).hexdigest(),
         "unresolved": [], "evidence": {}}
    if d[:4] != MAGIC:
        r["error"] = "magic_mismatch"
        return r
    r["version_u16_0x04"] = struct.unpack_from("<H", d, 4)[0]
    r["const_u16_0x06"] = struct.unpack_from("<H", d, 6)[0]
    flag, n = struct.unpack_from("<HH", d, 8)
    r["bone_flag_u16_0x08"] = flag
    r["bone_count_u16_0x0A"] = n if flag == 1 else 0
    r["evidence"]["header"] = "0x00 magic / 0x04 version / 0x06 const / 0x08 bone_flag / 0x0A bone_count; 无骨骼时 u32@0x0A=文件长度-16（实测 %d）" % (
        struct.unpack_from("<I", d, 0x0A)[0])
    if flag != 1:
        st = find_subtable(d, 0x0E, 0x0E + 4096)
        r["bone_count"] = 0
        r["bones"] = []
        r["skeleton_state"] = "no_bone_block_flag0"
        r["biped_strings"] = d.count(b"biped")
        r["sub_table"] = st
        r["evidence"]["flag0"] = "header bone_flag=0 且全文 'biped' 串计数=%d（双重判据）" % d.count(b"biped")
        # 机器可读布局（固定字段名；供 export_glb.py 直接消费）
        r["layout"] = {
            "mesh_bytes": len(d),
            "skeleton_block_start": None,
            "bone_flag_u16_0x08": flag,
            "bone_count_u16_0x0A": 0,
            "size_field_u32_0x0A": struct.unpack_from("<I", d, 0x0A)[0],
            "parent_area": None, "name_block_off": None, "name_stride": None, "names_end": None,
            "per_bone_block_off": None, "per_bone_stride": None, "per_bone_block_end_exclusive": None,
            "trailer_u32_off": None,
            "sub_table_off": (st or {}).get("sub_table_off"),
            "term_off": (st or {}).get("term_off"), "sub_k": (st or {}).get("k"),
            "sub_tv": (st or {}).get("tv"), "sub_tf": (st or {}).get("tf"),
            "geometry_segment_off": (st or {}).get("sub_table_off"),
            "geometry_segment_formula": None,
            "geometry_segment_basis": "无骨骼块：u32@0x0A=文件长度-16；几何段起点取 sub 表三重校验位（非 骨名区尾公式）",
            "geometry_segment_state": "偏移来自 sub 表三重校验（term==1 && tv==Σv && tf==Σf）；顶点/索引/UV 段起点未逐字段定证",
        }
        return r
    if n == 0:
        r["bone_count"] = 0
        r["skeleton_state"] = "bone_count_zero"
        r["unresolved"].append("bone_flag=1 但 bone_count=0")
        return r
    # 父索引区 + 骨名区
    name_off = 0x0C + n
    r["name_block_off"] = name_off
    r["parent_area"] = {"start": 0x0D, "bytes": n - 1,
                        "hex": d[0x0D:name_off].hex(" ")}
    strides = detect_names(d, name_off, n)
    if not strides:
        r["skeleton_state"] = "name_area_invalid"
        r["unresolved"].append("骨名区在 16/32/48/64 步长下均校验失败")
        return r
    stride = 32 if 32 in strides else sorted(strides)[0]
    names = strides[stride]
    r["name_stride"] = stride
    r["name_stride_candidates"] = sorted(strides)
    if len(strides) > 1:
        r["unresolved"].append("步长歧义：%s 均通过校验，取 %d" % (sorted(strides), stride))
    r["bones"] = names
    r["bone_count"] = len(names)
    names_end = name_off + stride * n
    # 逐骨 92B 块 + 尾部 u32
    sub = find_subtable(d, names_end, names_end + 64 + 92 * n + 4096)
    if sub:
        gap = sub["sub_table_off"] - names_end
        r["per_bone_block"] = {"off": names_end + 1, "stride": 92, "count": n,
                               "trailer_u32_off": sub["sub_table_off"] - 4,
                               "gap_bytes": gap,
                               "formula_check": gap == 1 + 92 * n + 4}
        r["evidence"]["per_bone_block"] = "gap(=sub_table_off-names_end) = 1 + 92n + 4 实测成立：%s（n=%d gap=%d）" % (
            gap == 1 + 92 * n + 4, n, gap)
        if gap != 1 + 92 * n + 4:
            r["unresolved"].append("逐骨块公式不成立（gap=%d 期待 %d）" % (gap, 1 + 92 * n + 4))
        r["unresolved"].append("逐骨 92B 块字段语义未定证（非 4x4/3x4 矩阵行结构；仅给偏移与长度）")
        r["sub_table"] = sub
    else:
        r["unresolved"].append("骨骼块之后未能定位 sub 表（term/tv/tf 三重校验失败）")
    # 层级：切分 B（byte[0x0D .. 0x0D+n-1] → bone[1..n-1]）
    arr = list(d[0x0D:0x0D + (n - 1)])
    viol = [(i + 1, p) for i, p in enumerate(arr) if p != 255 and not (p < i + 1)]
    hierarchy = [{"i": 0, "parent": None, "root": True}]
    for i, p in enumerate(arr):
        hierarchy.append({"i": i + 1, "parent": None if p == 255 else p, "root": p == 255})
    r["hierarchy"] = hierarchy
    r["hierarchy_state"] = "verified_parent_lt_child" if not viol else "unresolved_violations"
    r["evidence"]["hierarchy"] = ("切分 B：byte[0x0D..0x0D+n-1] 对应 bone[1..n-1]，0xFF=无父；"
                                  "校验 parent<self 违规=%d %s" % (len(viol), viol[:5]))
    if viol:
        r["unresolved"].append("父索引校验违规（可能为全局骨号/子集编号）：%s" % viol[:5])
    r["biped_strings"] = d.count(b"biped")
    r["skeleton_state"] = "ok" if not viol else "ok_hierarchy_unresolved"
    # ===== 机器可读布局（固定字段名；供 export_glb.py 直接消费）=====
    # 证据：骨名区尾 + 1 + 92*n + 4 == sub_table_off（sub 表三重校验 term==1 && tv==Sum(v) && tf==Sum(f)）
    names_end = name_off + stride * n
    st = r.get("sub_table") or {}
    parent_arr = [None] + [None if p == 255 else p for p in arr]  # 长度 = n（bone0 恒为根）
    children = [[] for _ in range(n)]
    roots = [0]
    for i in range(1, n):
        if parent_arr[i] is None:
            roots.append(i)
        else:
            children[parent_arr[i]].append(i)
    depth = [None] * n
    stack = [(rt, 0) for rt in reversed(roots)]
    while stack:
        i, dp = stack.pop()
        depth[i] = dp
        for c in reversed(children[i]):
            stack.append((c, dp + 1))
    per_bone_layout = []
    for i in range(n):
        per_bone_layout.append({
            "index": i, "name": names[i],
            "parent": parent_arr[i] if i > 0 else None,
            "depth": depth[i], "children": children[i],
            "raw_92B_off": (r.get("per_bone_block") or {}).get("off") + 92 * i
            if r.get("per_bone_block") else None,
            "raw_92B_bytes": 92,
        })
    r["roots"] = roots
    r["per_bone_layout"] = per_bone_layout
    r["layout"] = {
        "mesh_bytes": len(d),
        "skeleton_block_start": 0x0D,
        "bone_flag_u16_0x08": flag,
        "bone_count_u16_0x0A": n,
        "parent_area": {"off": 0x0D, "bytes": n - 1, "end_exclusive": 0x0D + n - 1,
                        "hex": d[0x0D:name_off].hex(" ")},
        "name_block_off": name_off,
        "name_stride": stride,
        "names_end": names_end,
        "per_bone_block_off": (r.get("per_bone_block") or {}).get("off"),
        "per_bone_stride": 92,
        "per_bone_block_end_exclusive": (r.get("per_bone_block") or {}).get("off") + 92 * n
        if r.get("per_bone_block") else None,
        "trailer_u32_off": (r.get("per_bone_block") or {}).get("trailer_u32_off"),
        "sub_table_off": st.get("sub_table_off"),
        "term_off": st.get("term_off"), "sub_k": st.get("k"),
        "sub_tv": st.get("tv"), "sub_tf": st.get("tf"),
        "geometry_segment_off": st.get("sub_table_off"),
        "geometry_segment_formula": "骨名区尾 + 1 + 92*n + 4 = %d" % (names_end + 1 + 92 * n + 4),
        "geometry_segment_basis": "与该 sub 表三重校验位 sub_table_off 实测相等（term==1 && tv==Σv && tf==Σf）；"
                                  "该偏移起为 LOD/子网格描述区",
        "geometry_segment_state": "偏移已实测自洽；顶点/索引/UV 段起点未逐字段定证（消费方请按 sub_table_off 取用并自行校验）",
    }
    return r


def gim_document_hint(gpk, gim_path):
    """读取 .gim 模型文档的**存在性证据**：内嵌 mesh 路径 + Sockets/MatrixToBone/BindType 属性名"""
    d, meta = gpk.read(gim_path)
    if d is None:
        return {"gim_path": gim_path, "state": "gim_not_found", **(meta or {})}
    strs = [m.group().decode("latin1") for m in re.finditer(rb"[\x20-\x7e]{3,}", d)]
    paths = [s for s in strs if re.search(r"\.(gim|sfx|mesh)$", s, re.I)]
    sockets = sorted({s for s in strs if s.startswith("Socket_")})
    props = [p for p in ("BindType", "MatrixToBone", "Sockets", "CutBones", "SimpleMeshPathForRenderShadow") if p in strs]
    return {"gim_path": gim_path, "state": "ok", "row": meta["row"], "bytes": len(d),
            "sha16": hashlib.sha256(d).hexdigest()[:16], "embedded_mesh_paths": paths,
            "socket_types": sockets, "skeleton_props": props,
            "biped_in_gim": d.count(b"biped")}


def strip_skeleton_to_standard(d, sk):
    """把带骨骼块的 .mesh 切成“标准（bone_flag=0）布局”：
    = 14 字节头（magic 34 80 c8 bb / version / const / bone_flag=0 / u32@0x0A=文件长度-16）
      + 源文件 geometry_segment_off 起的**原始字节原样**（不重排、不改字节、不补位）。
    依据：① 实测 3/3 无骨骼 mesh 的 u32@0x0A == 文件长度-16；
          ② 实测无骨骼 mesh 的 sub 表（每 10 B 一项）恰好起于 0x0E —— 与 mesh_parse2.py:19-27 的假设一致；
          ③ geometry_segment_off == sub_table_off（sub 表三重校验 term==1 && tv==Σv && tf==Σf 实测成立）。
    返回 (out_bytes|None, info)
    """
    if not d or len(d) < 14:
        return None, {"mode": "refused", "note": "mesh 为空/过短"}
    flag = struct.unpack_from("<H", d, 8)[0] if len(d) >= 10 else None
    if flag != 1:
        return bytes(d), {"mode": "copy_already_standard",
                          "note": "该 mesh 本就无骨骼块（u16@0x08 != 1），原样复制，未改任何字节"}
    lay = (sk or {}).get("layout") or {}
    gs = lay.get("geometry_segment_off")
    if not gs:
        return None, {"mode": "refused", "note": "geometry_segment_off 未定位（sub 表三重校验失败），拒绝猜切点"}
    if not (14 <= gs <= len(d)):
        return None, {"mode": "refused", "note": "geometry_segment_off=%s 越界" % gs}
    hdr = bytearray(d[:14])
    out_len = 14 + (len(d) - gs)
    struct.pack_into("<H", hdr, 8, 0)                  # bone_flag = 0 ⇒ 无骨骼块
    struct.pack_into("<I", hdr, 10, out_len - 16)      # 实测口径：flag0 时 u32@0x0A = 文件长度-16
    out = bytes(hdr) + d[gs:]
    return out, {"mode": "stripped_skeleton_header",
                 "cut_at": gs, "header_bytes": 14,
                 "header_layout": {"0x00": "magic 34 80 c8 bb (原样)",
                                   "0x04": "u16 version (原样 %d)" % struct.unpack_from("<H", d, 4)[0],
                                   "0x06": "u16 const (原样 %d)" % struct.unpack_from("<H", d, 6)[0],
                                   "0x08": "u16 bone_flag = 0 (改写：无骨骼块)",
                                   "0x0A": "u32 = 文件长度-16 = %d (改写：实测 flag0 口径)" % (out_len - 16),
                                   "0x0E": "源文件 offset %d 起原样字节（sub 表正好落在 0x0E，"
                                           "与 mesh_parse2.py:19-27 假设一致）" % gs},
                 "note": "不重排/不改字节/不补位；仅替换 14 字节头。把原 [cut_at:14] 头粘回即可无损还原"}


def trim_to_standard_streams(out_b, sk):
    """把「14 字节头 + 源几何段」再裁成 mesh_parse2 / export_glb 能直接吃的**单段标准文件**：
    14B 头 + [sub 表 .. UV 流尾] + 原位 16B 尾；其后的附加顶点流块丢弃并登记（偏移/字节/sha16）。
    依据：真实无骨骼 mesh 实测 extra_bytes ∈ {0, n*tv*4}（整除，5/5）；而带骨骼变体实测
          extra_bytes 24/24 均**不整除** ⇒ 骨架 mesh 在 UV 流之后还有附加流，超出 mesh_parse2
          的单段假设（其 extra 计数用 round()，会多算一条流并越界读 vertex color）。
    返回 (bytes|None, info)
    """
    lay = (sk or {}).get("layout") or {}
    k, tv, tf = lay.get("sub_k"), lay.get("sub_tv"), lay.get("sub_tf")
    if out_b is None:
        return None, {"note": "无可裁输入"}
    if not (k and tv and tf):
        return None, {"note": "sub_k/sub_tv/sub_tf 缺失，拒绝裁剪（不猜布局）"}
    after_uv = 0x0E + 10 * k + 2 + 8 + 24 + tv * 6 + tv * 6 + 2 + tf * 6 + tv * 4
    if after_uv + 16 > len(out_b):
        return None, {"note": "after_uv+16=%d 超出文件 %d（sub_k/sub_tv/sub_tf 不可信，拒绝裁剪）"
                              % (after_uv + 16, len(out_b))}
    extra = len(out_b) - after_uv - 16
    if extra % (tv * 4) == 0:
        # 已是自洽的"标准多流"文件（真实无骨骼 mesh 实测 5/5 整除）：**不得裁剪**，
        # 否则会丢合法附加流（例：1110171 extra = 2×tv×4 = 顶点色流）。
        buf = bytearray(out_b)
        struct.pack_into("<I", buf, 10, len(buf) - 16)
        return bytes(buf), {"mode": "already_consistent_no_trim", "kept_bytes": len(buf),
                            "after_uv_off": after_uv, "extra_bytes": extra,
                            "n_extra_streams": extra // (tv * 4), "dropped_bytes": 0,
                            "note": "extra_bytes 整除 tv*4 ⇒ 标准多流布局已自洽，未裁剪（仅重写 u32@0x0A）"}
    buf = bytearray(out_b[:after_uv + 16])
    struct.pack_into("<I", buf, 10, len(buf) - 16)   # flag0 口径：u32@0x0A = 文件长度-16
    dropped = out_b[after_uv + 16:]
    return bytes(buf), {"mode": "standard_single_section",
                        "kept_bytes": len(buf), "after_uv_off": after_uv,
                        "dropped_off": after_uv + 16, "dropped_bytes": len(dropped),
                        "dropped_sha16": hashlib.sha256(dropped).hexdigest()[:16],
                        "note": "标准单段：头 + sub 表..UV 流 + 16B 尾（结构已实测：真实无骨骼 mesh "
                                "extra_bytes 整除）。被丢弃的附加流块已登记偏移/字节/sha16，可回溯；"
                                "该块语义未定证（疑为骨骼索引/权重/切线等附加顶点流）"}


def locate_skin(gpk, skin_id, gim_path, out_dir, variant_fallback=True, dump_mesh=None):
    gim_path = gim_path.replace("/", "\\")
    stem = gim_path[:-4] if gim_path.lower().endswith(".gim") else gim_path
    rec = {"skin_id": skin_id, "gim_path": gim_path, "mesh_path": None,
           "mesh_variants": [], "reason": None}
    cands = []
    for v in VARIANTS:
        p = stem + v + ".mesh"
        d, meta = gpk.read(p)
        if d is None:
            continue
        flag = struct.unpack_from("<HH", d, 8)[0] if len(d) >= 10 and d[:4] == MAGIC else None
        cands.append({"variant": v or "(main)", "path": p, "row": meta["row"], "flag": flag,
                      "bytes": len(d), "sha16": hashlib.sha256(d).hexdigest()[:16], "_data": d})
    rec["mesh_variants"] = [{k: v for k, v in c.items() if k != "_data"} for c in cands]
    if not cands:
        rec["reason"] = "mesh_not_found_all_variants"
        return rec
    pick = None
    if variant_fallback:
        for c in cands:
            if c["flag"] == 1:
                pick = c
                break
        if pick is None:
            pick = cands[0]
    else:
        pick = cands[0]
    rec["mesh_path"] = pick["path"]
    rec["mesh_row"] = pick["row"]
    rec["mesh_variant"] = pick["variant"]
    rec["mesh_bytes"] = pick["bytes"]
    rec["mesh_sha16"] = pick["sha16"]
    parsed = parse_mesh(pick["_data"])
    rec["skeleton"] = parsed
    rec["bone_count"] = parsed.get("bone_count", 0)
    rec["bones"] = parsed.get("bones", [])
    rec["skeleton_state"] = parsed.get("skeleton_state", parsed.get("error", "unknown"))
    if not rec["bone_count"]:
        rec["gim_document"] = gim_document_hint(gpk, gim_path)
        gd = rec["gim_document"] or {}
        props = gd.get("skeleton_props") or []
        # 源级预测器（实证 21/21 vs 0/13）：gim 声明 CutBones ⇒ 该 mesh 带骨骼块；
        # 无 CutBones 但有 MatrixToBone/Sockets ⇒ 刚性挂接（骨架在角色侧），武器侧无骨骼
        rec["gim_has_cutbones"] = "CutBones" in props
        rec["gim_binding_only"] = ("MatrixToBone" in props or "Sockets" in props) and not rec["gim_has_cutbones"]
        if rec["skeleton_state"] == "no_bone_block_flag0" and rec["gim_binding_only"]:
            rec["reason"] = "no_weapon_skeleton__gim_binding_only"
        else:
            rec["reason"] = rec["skeleton_state"]
    if dump_mesh:
        open(dump_mesh, "wb").write(pick["_data"])
        rec["dumped_mesh"] = dump_mesh
    return rec


def main(argv=None):
    ap = argparse.ArgumentParser(description="武器皮肤骨骼定位器（.gpk path→entry + .mesh 骨骼块解析）")
    ap.add_argument("--id")
    ap.add_argument("--gim")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--roster", default=DEFAULT_ROSTER)
    ap.add_argument("--res", default=DEFAULT_RES)
    ap.add_argument("--no-variant-fallback", action="store_true")
    ap.add_argument("--dump-mesh", help="把选中的 .mesh 原始字节写到该路径；同时写 <路径>.layout.json（机器可读布局）")
    ap.add_argument("--layout-out", help="只写机器可读布局 JSON（固定字段名，供 export_glb.py 消费）")
    ap.add_argument("--geometry-out", help="切掉骨骼头、写成标准布局的 .mesh（单目标=文件路径，--all=目录）；"
                                           "同时写 <输出>.geometry.json")
    ap.add_argument("--geometry-trim", action="store_true",
                    help="配合 --geometry-out：额外写 <输出>.std.mesh（单段标准，mesh_parse2/export_glb 可直接吃；"
                         "丢弃 UV 流之后的附加流块并在 geometry.json 登记）")
    ap.add_argument("--index-only", action="store_true", help="只打印容器索引统计")
    args = ap.parse_args(argv)

    gpk = GpkIndex(args.res, verbose=args.index_only)
    if args.index_only:
        print(json.dumps({"containers_indexed": len(gpk.containers), "rows": len(gpk.rows),
                          "detail": {os.path.basename(k): v for k, v in gpk.containers.items()}},
                         ensure_ascii=False, indent=1))
        return 0

    roster = json.load(io.open(args.roster, encoding="utf-8")) if os.path.exists(args.roster) else None
    rows = []
    if roster:
        rows = [dict(r, level=5) for r in roster.get("g5", [])] + [dict(r, level=6) for r in roster.get("g6", [])]

    os.makedirs(args.out, exist_ok=True)
    tasks = []
    if args.id or args.gim:
        if args.gim:
            tasks.append({"id": args.id or os.path.basename(args.gim).split(".")[0], "model_path": args.gim,
                          "name": None, "level": None})
        else:
            hit = [r for r in rows if str(r.get("id")) == str(args.id)]
            if not hit:
                sys.stderr.write("[FAIL] id %s 不在 ROSTER\n" % args.id)
                return 2
            tasks.append(hit[0])
    elif args.all:
        tasks = rows
    else:
        ap.print_help()
        return 1

    results = []
    for t in tasks:
        sid = str(t.get("id"))
        try:
            rec = locate_skin(gpk, sid, t.get("model_path") or "", args.out,
                              variant_fallback=not args.no_variant_fallback,
                              dump_mesh=args.dump_mesh if (args.id or args.gim) else None)
            rec["name"] = t.get("name")
            rec["level"] = t.get("level")
            rec["model_extra_scale"] = t.get("model_extra_scale")
            if args.id or args.gim:
                for lpath in ([args.dump_mesh + ".layout.json"] if args.dump_mesh else []) + \
                             ([args.layout_out] if args.layout_out else []):
                    if not lpath:
                        continue
                    lay = {"schema": "neox_mesh_layout/v1", "skin_id": sid,
                           "gim_path": rec.get("gim_path"), "mesh_path": rec.get("mesh_path"),
                           "mesh_variant": rec.get("mesh_variant"), "mesh_row": rec.get("mesh_row"),
                           "mesh_sha16": rec.get("mesh_sha16"), "bone_count": rec.get("bone_count"),
                           "skeleton_state": rec.get("skeleton_state"),
                           "layout": (rec.get("skeleton") or {}).get("layout"),
                           "roots": (rec.get("skeleton") or {}).get("roots"),
                           "per_bone_layout": (rec.get("skeleton") or {}).get("per_bone_layout"),
                           "hierarchy": (rec.get("skeleton") or {}).get("hierarchy"),
                           "unresolved": (rec.get("skeleton") or {}).get("unresolved")}
                    io.open(lpath, "w", encoding="utf-8").write(json.dumps(lay, ensure_ascii=False, indent=1))
                    sys.stderr.write("layout -> %s\n" % lpath)
            if args.geometry_out:
                # 单目标：--geometry-out 是**文件路径**；批量：--geometry-out 是**目录**
                single = bool(args.id or args.gim)
                gpath = args.geometry_out if single else os.path.join(args.geometry_out, "%s.mesh" % sid)
                if not single:
                    os.makedirs(args.geometry_out, exist_ok=True)
                src, _m = gpk.read(rec["mesh_path"]) if rec.get("mesh_path") else (None, None)
                out_b, info = strip_skeleton_to_standard(src, rec.get("skeleton"))
                ginfo = {"src_mesh": rec.get("mesh_path"), "src_sha16": rec.get("mesh_sha16"),
                         "src_row": rec.get("mesh_row"), "src_variant": rec.get("mesh_variant"),
                         "geometry_segment_off": ((rec.get("skeleton") or {}).get("layout") or {}
                                                  ).get("geometry_segment_off"),
                         "out_mesh": gpath,
                         "bytes_in": (len(src) if src else None),
                         "bytes_out": (len(out_b) if out_b else None),
                         "bone_count": rec.get("bone_count"),
                         "skin_id": sid, **info}
                # classic 布局的几何段内偏移（相对**输出文件**；= mesh_parse2.py:19-27,71-77 的口径）
                _lay = (rec.get("skeleton") or {}).get("layout") or {}
                _k, _tv, _tf = _lay.get("sub_k"), _lay.get("sub_tv"), _lay.get("sub_tf")
                if out_b is not None and _k and _tv and _tf:
                    _data = 0x0E + 10 * _k + 2 + 8 + 24
                    _nrm = _data + _tv * 6
                    _idx = _nrm + _tv * 6 + 2
                    _uv = _idx + _tf * 6
                    _au = _uv + _tv * 4
                    ginfo["classic_layout"] = {
                        "based_on": "mesh_parse2.py:19-27(0x0E 起每 10B 一项, term+tv+tf 三重校验) / 71-77(流偏移)",
                        "entries_off": 0x0E, "entry_stride": 10, "sub_k": _k,
                        "sub_table_bytes": 10 * _k,
                        "term_off": 0x0E + 10 * _k, "tv": _tv, "tf": _tf,
                        "tv_off": 0x0E + 10 * _k + 2, "tf_off": 0x0E + 10 * _k + 6,
                        "bbox_off": 0x0E + 10 * _k + 10, "bbox_bytes": 24,
                        "pos_off": _data, "pos_bytes": _tv * 6,
                        "nrm_off": _nrm, "nrm_bytes": _tv * 6,
                        "pad_bytes": 2,
                        "idx_off": _idx, "idx_bytes": _tf * 6,
                        "uv_off": _uv, "uv_bytes": _tv * 4,
                        "after_uv": _au, "trailer_off": _au, "trailer_bytes": 16,
                        "stream_bytes_total": _au + 16,
                        "extra_bytes_in_file": len(out_b) - (_au + 16),
                        "note": "纯切文件里 UV 流之后还有附加块（骨架变体实测 24/24 extra 不整除 tv*4）；"
                                ".std.mesh 已把它裁掉并把 offsets 保持在同一位置（前缀完全相同）"}
                else:
                    ginfo["classic_layout"] = {"state": "unresolved",
                                               "note": "sub_k/sub_tv/sub_tf 缺失（sub 表三重校验未过），不给流偏移"}
                if out_b is None:
                    rec["geometry_out"] = ginfo
                    sys.stderr.write("[SKIP] geometry-out %s: %s\n" % (sid, info.get("note")))
                else:
                    io.open(gpath, "wb").write(out_b)
                    ginfo["out_sha16"] = hashlib.sha256(out_b).hexdigest()[:16]
                    if args.geometry_trim:
                        sp = (gpath[:-5] + ".std.mesh") if gpath.lower().endswith(".mesh") \
                            else (gpath + ".std.mesh")
                        if info.get("mode") == "copy_already_standard":
                            # 源本无骨骼块：直接同字节复制，不做任何裁剪（避免丢合法附加流）
                            io.open(sp, "wb").write(out_b)
                            ginfo["standard_trim"] = {"out_mesh": sp, "bytes_out": len(out_b),
                                                      "out_sha16": ginfo["out_sha16"],
                                                      "mode": "already_standard_copy", "dropped_bytes": 0,
                                                      "note": "源 mesh 本就无骨骼块：同字节复制，未裁剪"}
                            sys.stderr.write("geometry(std) -> %s (%d B; 本就标准，未裁剪)\n"
                                             % (sp, len(out_b)))
                        else:
                            std_b, sinfo = trim_to_standard_streams(out_b, rec.get("skeleton"))
                            if std_b is None:
                                ginfo["standard_trim"] = sinfo
                                sys.stderr.write("[SKIP] geometry-trim %s: %s\n" % (sid, sinfo.get("note")))
                            else:
                                io.open(sp, "wb").write(std_b)
                                ginfo["standard_trim"] = {"out_mesh": sp, "bytes_out": len(std_b),
                                                          "out_sha16": hashlib.sha256(std_b).hexdigest()[:16],
                                                          **sinfo}
                                sys.stderr.write("geometry(std) -> %s (%d B; 丢弃尾部附加流 %d B)\n"
                                                 % (sp, len(std_b), sinfo.get("dropped_bytes")))
                    io.open(gpath + ".geometry.json", "w", encoding="utf-8").write(
                        json.dumps(ginfo, ensure_ascii=False, indent=1))
                    rec["geometry_out"] = ginfo
                    sys.stderr.write("geometry -> %s (%d -> %d B)%s\n" % (
                        gpath, len(src), len(out_b), "" if info.get("mode") == "stripped_skeleton_header"
                        else "  [%s]" % info.get("mode")))
        except Exception as exc:  # 单皮肤失败不中断整批
            rec = {"skin_id": sid, "gim_path": t.get("model_path"), "reason": "exception:%s" % exc,
                   "bone_count": 0, "bones": [], "skeleton_state": "exception"}
        results.append(rec)
        outp = os.path.join(args.out, "%s_skeleton.json" % sid)
        io.open(outp, "w", encoding="utf-8").write(json.dumps(rec, ensure_ascii=False, indent=1))
        sys.stderr.write("%-9s %-9s bones=%-3s %s\n" % (
            sid, rec.get("skeleton_state"), rec.get("bone_count"),
            (rec.get("mesh_path") or "")[-52:]))

    # 汇总
    n_ids = len(results)
    hit = sum(1 for r in results if r.get("mesh_path") or r.get("mesh_variants"))
    ok = sum(1 for r in results if (r.get("bone_count") or 0) > 0)
    reasons = Counter(r.get("reason") or r.get("skeleton_state") or "ok" for r in results if not (r.get("bone_count") or 0))
    summary = {"ids": n_ids, "distinct_models": len({r.get("gim_path") for r in results}),
               "mesh_hit_ids": hit, "mesh_hit_rate": round(hit / n_ids, 4) if n_ids else 0,
               "bones_gt0_ids": ok, "bones_gt0_rate": round(ok / n_ids, 4) if n_ids else 0,
               "failure_classes": dict(reasons),
               "out_dir": args.out, "variant_fallback": not args.no_variant_fallback}
    io.open(os.path.join(args.out, "SKEL_summary%s.json" % ("" if not args.no_variant_fallback else "_nofallback")),
            "w", encoding="utf-8").write(json.dumps({"summary": summary, "results": results},
                                                    ensure_ascii=False, indent=1))
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
