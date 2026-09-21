# -*- coding: utf-8 -*-
"""cube_faces_export.py — Neox `.dds` cubemap 六面 / 逐级 mip 导出器（face-major 真值切法）

用途
----
把 `B8G8R8A8_UNORM` 的 Neox cubemap `.dds`（典型：`weapon_skin/<skin>/src_cube/<cube>.dds`，
128×128、8 级 mip、`caps2` 含 `DDSCAPS2_CUBEMAP`）按 **face-major** 排布切成 6 张 mip0 PNG，
供 wiki 3D viewer 的 `faces_glob` 直接消费。

为什么默认是 face-major
------------------------
本项目已定证（见 `03拆包产物/_target_1110171/ENV_uniforms_per_prim.json` 的
`cube_layout_conflict` 与环境光审计链，三重独立取证）：这批 `.dds` 的字节排布是
**face-major**——面 i 的 mip 链起始偏移 = `128 + i × Σ_k max(1,w>>k)·max(1,h>>k)·4`，
对 128²/8 级 mip 即 `128 + i × 87380`（=每面 `(128²+64²+…+1²)×4 B`）。

历史缺陷复现：早期提取链误按 **mip-major**（面 i 偏移 `128 + i·w·h·4`）读取，
于是面 0 侥幸正确，面 1..5 变成"小 mip 带 + 下一面 mip0 前若干行"的**分带拼接**图
（本工具 `--layout mip-major` 保留了这一错误切法，仅用于取证复现，不要用于交付）。

用法示例
--------
    # 1) 干跑（默认）：只报差异，不写盘
    python cube_faces_export.py "E:\\...\\1110165\\src_cube\\*.dds"

    # 2) 正式导出：写 PNG，旧文件先备份为 *.bak_mangled_<时间戳>
    python cube_faces_export.py "E:\\...\\src_cube\\qiangpi.dds" \\
        --out "E:\\...\\src_cube\\faces" --apply --backup-tag mangled

    # 3) 连逐级 mip 一起导出（face i 的 m0..m7）
    python cube_faces_export.py <dds> --out <faces_dir> --mips --apply

    # 4) 自检 + 落台账（六面互异 / 与 DDS 字节逐字节吻合 / 旧 vs 新 mean|Δ|）
    python cube_faces_export.py <dds...> --out <faces_dir> --json ledger.json

    # 5) 跨皮肤对照：拿别的皮肤已正确的同名面图做逐像素比对
    python cube_faces_export.py <dds> --ref-dir "E:\\...\\1110129\\src_cube\\faces"

    # 6) 复现历史错误切法（取证专用）
    python cube_faces_export.py <dds> --layout mip-major --dry-run

退出码
------
    0 全部成功
    1 用法/参数错误
    2 至少一个 DDS 解析失败（缺失 / 非 6 面 128² face-major / 尺寸不符）——不会瞎切
    3 自检失败（六面不互异，或与 DDS 字节不吻合）
    4 写盘 IO 失败

边界（明确不做的事）
--------------------
  * 不改 DDS、不改 manifest、不碰 `neox_material.json` / `viewer.json` / `effects.json`；
  * 不做 cube 面序 / 朝向 / 基变换到引擎采样约定的映射（源面序本身仍未定证，
    本工具只保证"面号 ↔ 字节偏移"的正确，不保证"面号 ↔ 空间方向"的正确）；
  * 不解非 `B8G8R8A8` / 非 cubemap / 非方形 2 次幂的 DDS（直接报错，不猜）。
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import io
import json
import os
import shutil
import struct
import sys
import time

# ── UTF-8 强制：Windows 控制台默认 GBK，中文输出会炸。
# 用 reconfigure 而非再包一层 TextIOWrapper —— 后者在「本模块被 import」时会因
# 旧 wrapper 被 GC 而关掉共享的底层 buffer，把调用方的 stdout 一起搞坏。
for _s in ("stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    import numpy as np
    from PIL import Image
except Exception as _exc:  # pragma: no cover - 环境缺库时给出可操作提示
    sys.stderr.write(
        "缺少依赖 numpy/Pillow。请使用带库的解释器，例如：\n"
        "  C:\\Users\\Administrator\\AppData\\Local\\Programs\\Python\\Python311\\python.exe\n"
        "原始错误：%r\n" % (_exc,))
    raise SystemExit(1)

DDS_HEADER_BYTES = 128
DDSCAPS2_CUBEMAP = 0x200
DEFAULT_FACES = 6


# ─────────────────────────────────────────────────────────── DDS 解析
class DdsError(Exception):
    """DDS 不合规（缺失面表 / 尺寸不符 / 非 6 面 face-major）—— 调用方必须停止，不得瞎切。"""


class CubeDds:
    """一个已校验的 Neox cubemap DDS。"""

    def __init__(self, path: str, faces: int = DEFAULT_FACES, require_6face: bool = True):
        self.path = path
        if not os.path.isfile(path):
            raise DdsError("文件不存在：%s" % path)
        with open(path, "rb") as fh:
            self.data = fh.read()
        b = self.data
        if len(b) < DDS_HEADER_BYTES or b[:4] != b"DDS ":
            raise DdsError("不是 DDS（magic=%r，%d B）" % (b[:4], len(b)))
        self.height, self.width = struct.unpack_from("<II", b, 12)
        self.pitch, self.depth = struct.unpack_from("<II", b, 20)
        self.mip_count = struct.unpack_from("<I", b, 28)[0] or 1
        self.pf_flags, self.fourcc, self.rgba_bits = struct.unpack_from("<III", b, 80)
        self.caps2 = struct.unpack_from("<I", b, 112)[0] if len(b) >= 116 else 0
        self.n_faces = faces
        self.sha16 = hashlib.sha256(b).hexdigest()[:16]

        if self.width != self.height:
            raise DdsError("非方形（%dx%d），本工具只处理方形 cubemap" % (self.width, self.height))
        if not (self.caps2 & DDSCAPS2_CUBEMAP):
            raise DdsError("caps2=0x%X 无 DDSCAPS2_CUBEMAP 位，不是 cubemap" % self.caps2)
        # B8G8R8A8_UNORM：4 字节/px，无 FourCC，32 位
        self.is_bgra = (self.fourcc == 0 and self.rgba_bits == 32)
        if not self.is_bgra:
            raise DdsError("像素格式非 B8G8R8A8_UNORM（fourcc=0x%X bits=%d）" % (self.fourcc, self.rgba_bits))

        self.chain_per_face = sum(self._mip_bytes(m) for m in range(self.mip_count))
        if require_6face:
            expect = DDS_HEADER_BYTES + self.n_faces * self.chain_per_face
            if len(b) != expect:
                raise DdsError(
                    "长度不符：实际 %d B ≠ 期望 %d B（128 头 + %d 面 × %d B mip 链）。"
                    "该文件不是 %d 面 %d² face-major cubemap ⇒ 按 A5 规则停在报告，不切。"
                    % (len(b), expect, self.n_faces, self.chain_per_face, self.n_faces, self.width))

    def _mip_bytes(self, m: int) -> int:
        w = max(1, self.width >> m)
        h = max(1, self.height >> m)
        return w * h * 4

    # ── 偏移公式（本工具的核心契约）
    def face_mip_offset(self, face: int, mip: int = 0) -> int:
        """face-major：面 i 的 mip 链起点 = 128 + i × 每面链长；再沿链累加前序 mip。"""
        if not 0 <= face < self.n_faces:
            raise DdsError("面号越界：%d" % face)
        if not 0 <= mip < self.mip_count:
            raise DdsError("mip 级越界：%d（该 DDS mip_count=%d）" % (mip, self.mip_count))
        off = DDS_HEADER_BYTES + face * self.chain_per_face
        for k in range(mip):
            off += self._mip_bytes(k)
        return off

    def mip_major_offset(self, face: int, mip: int = 0) -> int:
        """历史错误切法（仅取证）：只按面跨 mip0 大小，忽略每面后面的小 mip。"""
        off = DDS_HEADER_BYTES + face * self.width * self.height * 4
        cur = self.width
        for _ in range(mip):
            cur = max(1, cur >> 1)
            off += 0  # mip-major 下小 mip 被整段跳过，这正是分带拼接的成因
        return off

    def offset(self, face: int, mip: int, layout: str) -> int:
        return self.mip_major_offset(face, mip) if layout == "mip-major" else self.face_mip_offset(face, mip)

    def raw_bgra(self, face: int, mip: int, layout: str) -> bytes:
        off = self.offset(face, mip, layout)
        n = self._mip_bytes(mip)
        chunk = self.data[off:off + n]
        if len(chunk) != n:
            raise DdsError("面 %d mip %d 越界读取（off=%d 需 %d B）" % (face, mip, off, n))
        return chunk

    def face_rgba(self, face: int, mip: int = 0, layout: str = "face-major"):
        """返回 (H,W,4) uint8 RGBA 数组：BGRA→RGBA，alpha 原样保留。"""
        w = max(1, self.width >> mip)
        h = max(1, self.height >> mip)
        a = np.frombuffer(self.raw_bgra(face, mip, layout), dtype=np.uint8).reshape(h, w, 4)
        return np.ascontiguousarray(a[:, :, [2, 1, 0, 3]])


# ─────────────────────────────────────────────────────────── 工具函数
def rgba_sha16(arr) -> str:
    return hashlib.sha256(np.ascontiguousarray(arr).tobytes()).hexdigest()[:16]


def png_sha16(path: str) -> str | None:
    if not os.path.isfile(path):
        return None
    try:
        with Image.open(path) as im:
            return rgba_sha16(np.asarray(im.convert("RGBA")))
    except Exception:
        return None


def file_sha16(path: str) -> str | None:
    """PNG **文件字节** 的 sha16（用于"改前/改后 sha16+字节"存档口径，区别于像素 sha16）。"""
    if not os.path.isfile(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()[:16]


def mean_abs_diff(arr, png_path: str):
    """arr 为 RGBA 数组，png_path 为对照 PNG。返回 (mean|Δ|, 备注)；形状不符返回 (None, 原因)。"""
    if not os.path.isfile(png_path):
        return None, "对照 PNG 不存在"
    try:
        with Image.open(png_path) as im:
            pa = np.asarray(im.convert("RGBA"))
    except Exception as exc:
        return None, "对照 PNG 无法解码：%r" % (exc,)
    if pa.shape != tuple(arr.shape):
        return None, "形状不符 %s vs %s" % (pa.shape, tuple(arr.shape))
    d = np.abs(arr.astype(np.int16) - pa.astype(np.int16))
    return float(d.mean()), None


def byte_exact_backmatch(arr, dds: CubeDds, face: int, mip: int, layout: str):
    """把 PNG 像素按 RGBA→BGRA 还原，与 DDS 原始字节切片逐字节比对。

    返回 (bool, 首个不等字节偏移|None, 期望/实际字节 hex 片段)。
    """
    got = np.ascontiguousarray(arr[:, :, [2, 1, 0, 3]]).tobytes()
    want = dds.raw_bgra(face, mip, layout)
    if got == want:
        return True, None, None
    n = min(len(got), len(want))
    for i in range(n):
        if got[i] != want[i]:
            return False, i, "want[%d:]=%s got[%d:]=%s" % (i, want[i:i + 8].hex(), i, got[i:i + 8].hex())
    return False, n, "长度不等 %d vs %d" % (len(want), len(got))


def mip_layout_note(dds: CubeDds) -> dict:
    """量化"mip-major 误读"造成的分带结构：第 f 面误读起点落在第 (f-1) 面链的哪个位置。"""
    per_mip0 = dds.width * dds.height * 4
    tail = dds.chain_per_face - per_mip0           # 该面 mip0 之后的小 mip 总字节
    note = {"per_face_mip0_bytes": per_mip0, "per_face_chain_bytes": dds.chain_per_face,
            "small_mip_tail_bytes": tail, "per_face_shift_bytes": tail,
            "explain": ("face-major 文件按 mip-major 读：面 f 的读取起点比其真实链起点晚 f×%d B ⇒ "
                        "读到的前 %d B 是「上一面的小 mip 带」，其余 %d B 才是真面 f 的 mip0 顶部若干行 "
                        "（面 0 因 f=0 而侥幸正确）"
                        % (tail, tail, per_mip0 - tail))}
    if per_mip0:
        note["garbage_rows"] = round(tail / (dds.width * 4), 3)
        note["real_rows"] = round((per_mip0 - tail) / (dds.width * 4), 3)
    return note


# ─────────────────────────────────────────────────────────── 单文件处理
def process_one(dds_path: str, args, idx: int, total: int) -> dict:
    rec = {"dds": os.path.abspath(dds_path), "apply": bool(args.apply), "layout": args.layout,
           "unresolved": [], "faces": []}
    try:
        dds = CubeDds(dds_path, faces=args.faces)
    except DdsError as exc:
        rec["status"] = "dds_rejected"
        rec["error"] = str(exc)
        rec["unresolved"].append("DDS 被拒 ⇒ 未切任何面（按 A5：停在报告里说明，不瞎切）")
        sys.stderr.write("[%d/%d] ✗ %s\n        %s\n" % (idx, total, dds_path, exc))
        return rec

    cube = os.path.splitext(os.path.basename(dds_path))[0]
    out_dir = args.out or os.path.join(os.path.dirname(os.path.abspath(dds_path)), "faces")
    rec.update({"cube": cube, "sha16": dds.sha16, "bytes": len(dds.data), "w": dds.width, "h": dds.height,
                "mip_count": dds.mip_count, "caps2": "0x%X" % dds.caps2,
                "per_face_chain_bytes": dds.chain_per_face, "out_dir": os.path.abspath(out_dir),
                "layout_note": mip_layout_note(dds)})

    print("[%d/%d] %s" % (idx, total, dds_path))
    print("        dds sha16=%s  %dx%d  mips=%d  caps2=0x%X  每面链=%d B  %s"
          % (dds.sha16, dds.width, dds.height, dds.mip_count, dds.caps2, dds.chain_per_face,
             "写盘" if args.apply else "干跑"))
    if args.apply:
        try:
            os.makedirs(out_dir, exist_ok=True)
        except OSError as exc:
            rec["status"] = "io_error"
            rec["error"] = "无法创建输出目录：%r" % (exc,)
            return rec

    ts = args.timestamp
    ok_all, all_distinct = True, True
    for f in range(dds.n_faces):
        levels = range(dds.mip_count) if args.mips else [0]
        for m in levels:
            arr = dds.face_rgba(f, m, args.layout)
            name = "%s_f%d_m%d.png" % (cube, f, m)
            dst = os.path.join(out_dir, name)
            new_sha = rgba_sha16(arr)
            e = {"face": f, "mip": m, "png": name, "new_rgba_sha16": new_sha}

            # (a) 与 DDS 原始字节逐字节吻合（硬自证）
            exact, bad_at, detail = byte_exact_backmatch(arr, dds, f, m, args.layout)
            e["byte_exact_vs_dds"] = exact
            if not exact:
                e["byte_exact_first_bad"] = {"offset": bad_at, "detail": detail}
                ok_all = False

            # (b) 旧 PNG 对照
            old_sha = png_sha16(dst) if os.path.isfile(dst) else None
            e["old_exists"] = old_sha is not None
            e["old_rgba_sha16"] = old_sha
            e["old_file_sha16"] = file_sha16(dst)
            e["old_bytes"] = os.path.getsize(dst) if e["old_exists"] else None
            mabs, why = mean_abs_diff(arr, dst) if e["old_exists"] else (None, "旧 PNG 不存在")
            e["old_vs_new_mean_abs"] = None if mabs is None else round(mabs, 6)
            if why:
                e["old_vs_new_note"] = why
            e["replaced"] = bool(e["old_exists"] and old_sha != new_sha)

            # (c) 跨皮肤 / 跨目录参照（可给多个 --ref-dir，全部必须逐像素一致）
            if args.ref_dir:
                refs = []
                for rd in args.ref_dir:
                    rp = os.path.join(rd, name)
                    rsha = png_sha16(rp)
                    rmabs, rwhy = mean_abs_diff(arr, rp)
                    refs.append({"dir": rd, "png": rp, "exists": rsha is not None, "rgba_sha16": rsha,
                                 "identical": (rsha is not None and rsha == new_sha),
                                 "mean_abs": None if rmabs is None else round(rmabs, 6), "note": rwhy})
                    if rsha is not None and rsha != new_sha:
                        ok_all = False
                e["refs"] = refs
                e["ref_all_identical"] = all(r["identical"] for r in refs)

            # (d) 写盘 + 备份
            if args.apply:
                try:
                    if e["old_exists"] and old_sha != new_sha and args.backup_tag:
                        bak = "%s.bak_%s_%s" % (dst, args.backup_tag, ts)
                        shutil.copy2(dst, bak)
                        e["backup"] = os.path.basename(bak)
                        e["backup_bytes"] = os.path.getsize(bak)
                    Image.fromarray(arr, "RGBA").save(dst, optimize=False)
                    back = png_sha16(dst)
                    e["png_bytes"] = os.path.getsize(dst)
                    e["written_rgba_sha16"] = back
                    e["new_file_sha16"] = file_sha16(dst)
                    e["roundtrip_ok"] = (back == new_sha)
                    if back != new_sha:
                        ok_all = False
                except OSError as exc:
                    e["write_error"] = repr(exc)
                    rec["status"] = "io_error"
                    ok_all = False
            rec["faces"].append(e)
            flag = "=" if not e["replaced"] else "→"
            extra = ""
            if e.get("old_vs_new_mean_abs") is not None:
                extra = "  旧vs新 mean|Δ|=%.4f" % e["old_vs_new_mean_abs"]
            if args.ref_dir and e.get("refs"):
                oks = [r for r in e["refs"] if r["exists"]]
                if oks:
                    extra += "  参照 %d/%d 一致(mean|Δ| max=%s)" % (
                        sum(1 for r in oks if r["identical"]), len(oks),
                        max(r["mean_abs"] for r in oks if r["mean_abs"] is not None))
            print("        f%-2d m%d %s %s%s" % (f, m, flag, name, extra))

    # 六面互异（只对 m0 有意义）
    m0 = [x["new_rgba_sha16"] for x in rec["faces"] if x["mip"] == 0]
    dup = {s: m0.count(s) for s in set(m0) if m0.count(s) > 1}
    all_distinct = not dup and len(m0) == dds.n_faces
    rec["six_faces_distinct"] = all_distinct
    rec["duplicate_m0_sha16"] = dup
    if not all_distinct:
        ok_all = False
    rec["selfcheck_pass"] = bool(ok_all)
    rec["status"] = "ok" if ok_all else "selfcheck_failed"
    print("        自检：六面互异=%s  与 DDS 字节逐字节吻合=%s  ⇒ %s"
          % (all_distinct, all(x["byte_exact_vs_dds"] for x in rec["faces"]),
             "通过" if ok_all else "未通过"))
    return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="cube_faces_export.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Neox cubemap .dds → 6 张 mip0 PNG（face-major 真值切法，BGRA→RGBA，保 alpha），自带自检。",
        epilog="退出码：0 成功 / 1 参数错 / 2 DDS 被拒 / 3 自检失败 / 4 写盘失败")
    ap.add_argument("dds", nargs="*", help="一个或多个 .dds 路径，支持通配符（会被 shell 或本程序展开）")
    ap.add_argument("--out", help="输出目录（默认：<dds 所在目录>/faces）")
    ap.add_argument("--apply", action="store_true", help="真正写盘；不给则干跑（只报差异）")
    ap.add_argument("--mips", action="store_true", help="除 m0 外，逐级导出 m1..m(mip_count-1)")
    ap.add_argument("--layout", choices=("face-major", "mip-major"), default="face-major",
                    help="切法；mip-major 是历史错误切法，仅供取证复现")
    ap.add_argument("--faces", type=int, default=DEFAULT_FACES, help="面数（默认 6）")
    ap.add_argument("--ref-dir", action="append", metavar="DIR",
                    help="参照目录（可重复给）：用同名 <cube>_f{i}_m{m}.png 做逐像素对照（跨皮肤自证）")
    ap.add_argument("--backup-tag", default="mangled",
                    help="覆写旧 PNG 时的备份标签，落盘名 <原名>.bak_<tag>_<时间戳>；置空串则不备份")
    ap.add_argument("--timestamp", default=time.strftime("%Y%m%d_%H%M%S"), help="备份用时间戳（默认当前时刻）")
    ap.add_argument("--json", dest="json_out", help="把逐文件台账写入该 JSON")
    ap.add_argument("--fail-fast", action="store_true", help="首个失败即停")
    ap.add_argument("--list", action="store_true", help="只列展开后的文件清单就退出")
    args = ap.parse_args(argv)

    files = []
    for pat in args.dds:
        hits = sorted(glob.glob(pat)) if any(c in pat for c in "*?[") else [pat]
        if not hits and not any(c in pat for c in "*?["):
            hits = [pat]
        files.extend(hits)
    files = [f for f in files if f.lower().endswith(".dds")]
    seen, uniq = set(), []
    for f in files:
        k = os.path.abspath(f).lower()
        if k not in seen:
            seen.add(k)
            uniq.append(f)
    if not uniq:
        sys.stderr.write("没有可处理的 .dds。用 --help 看用法。\n")
        return 1
    if args.list:
        for f in uniq:
            print(f)
        return 0

    records = []
    rc = 0
    for i, p in enumerate(uniq, 1):
        rec = process_one(p, args, i, len(uniq))
        records.append(rec)
        if rec.get("status") == "dds_rejected":
            rc = max(rc, 2)
        elif rec.get("status") == "io_error":
            rc = max(rc, 4)
        elif rec.get("status") == "selfcheck_failed":
            rc = max(rc, 3)
        if rc and args.fail_fast:
            break

    summary = {
        "tool": "cube_faces_export.py",
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "mode": "apply" if args.apply else "dry-run",
        "layout": args.layout,
        "dds_files": len(uniq),
        "ok": sum(1 for r in records if r.get("status") == "ok"),
        "dds_rejected": sum(1 for r in records if r.get("status") == "dds_rejected"),
        "selfcheck_failed": sum(1 for r in records if r.get("status") == "selfcheck_failed"),
        "io_error": sum(1 for r in records if r.get("status") == "io_error"),
        "totals": {
            "faces_written": sum(1 for r in records for e in r["faces"]
                                 if args.apply and e.get("written_rgba_sha16")),
            "faces_changed": sum(1 for r in records for e in r["faces"] if e.get("replaced")),
            "backups_made": sum(1 for r in records for e in r["faces"] if e.get("backup")),
        },
        "records": records,
    }
    print("\n合计：DDS %d，成功 %d，被拒 %d，自检失败 %d，IO 失败 %d；面写盘 %d，面变更 %d，备份 %d"
          % (summary["dds_files"], summary["ok"], summary["dds_rejected"], summary["selfcheck_failed"],
             summary["io_error"], summary["totals"]["faces_written"], summary["totals"]["faces_changed"],
             summary["totals"]["backups_made"]))
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(summary, fh, ensure_ascii=False, indent=1)
        print("台账：%s (%d B)" % (args.json_out, os.path.getsize(args.json_out)))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
