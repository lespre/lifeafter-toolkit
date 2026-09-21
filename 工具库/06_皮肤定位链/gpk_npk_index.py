# -*- coding: utf-8 -*-
"""gpk_npk_index.py — LifeAfter 资源容器「全量条目索引」/「按候选名查找」工具

覆盖三类容器（共 313 个文件，均在 `--res-root`，默认 `E:\\mrzh`）
--------------------------------------------------------------------------
  A. `.gpk`（HPGF/FPGH 族，`res\\*.gpk` + 根 `res.gpk`，共 56 个）
       文件头 AES-ECB 解密 4096 B；`hdr[4:8] ∈ {b"HPGF", b"FPGH"}`；
       条目数 `n = u32@20`；条目表自文件偏移 64 起、`n × 32 B`、整表 AES-ECB；
       行 `<IIIIIIII>` = (offset, packed_size, decoded_size, c1, c2, flag, u6, u7)；
       载荷自 `block_base + offset + 20` 起。单块家族 `block_base == 16` ⇒ 即 `offset + 36`
       （2026-09-20 修正：本文件此前写死 `payload_delta = 0` 是错的，见 GPK_PAYLOAD_ROW_DELTA 注释）。
       **行内不存文件名**，只存两个 murmur3 半值：u6 = murmur3(path, 0x66666666)（低 32 位）、
       u7 = murmur3(path, 0x77777777)（高 32 位）⇒ 只能按候选名算哈希试。
  B. `.gpk`（gres 族，`Documents\\gres\\*.gpk`，共 35 个）
       头部与 A 不同（`hdr[4:8]` 形如 RPGF/tPGF，`hdr[16:20]` 形如 CPGF/JTGF）。
       本工具尝试解析；解析不出来就如实计入 `unresolved`，**不猜**。
  C. `.fpk`（`res\\*.fpk`，共 64 个）
       从既有 `fpk_fid_index.json`（`fid2info`）读取，不重解析二进制。
  D. `.npk`（共 158 个，含 `Documents\\` 下 5 个脚本包）
       文件头 AES-ECB 解密 `<QIIII>` = (unknown, magic=0x4B50584E, version, table_offset, entry_count)；
       条目表自 `table_offset` 起、`entry_count × 48 B`、整表 AES-ECB；
       行 `<QIIIIIi>` = (file_id, offset, packed_size, decoded_size, c1, c2, flag)；
       载荷自 `offset` 起；file_id = (murmur3(path,0x77777777) << 32) | murmur3(path,0x66666666)，
       与 A 族的 (u7<<32)|u6 **同一约定** ⇒ 三类容器可用同一个 64 位 fid 做统一查找。

用法
----
    # 1) 只做对账（最快，只读表头 + 表，不读载荷）
    python gpk_npk_index.py --count

    # 2) 建全量索引（流式写，JSON 紧凑数组）
    python gpk_npk_index.py --out "E:\\la拆包项目\\03拆包产物\\indexes\\ALL_index_20260918.json"

    # 3) 另存紧凑 TSV（供反复 --find 复用，行格式见 README）
    python gpk_npk_index.py --out <index.json> --tsv <index.tsv>

    # 4) 按候选名查找（无需预建索引：流式只匹配查询集）
    python gpk_npk_index.py --find "common\\env_map\\qiangpi.cube"
    python gpk_npk_index.py --find "common/env_map/qiangpi.cube" --find "res/ui/xxx.tga" --variants
    python gpk_npk_index.py --find "xxx" --index <index.tsv>     # 复用已建 TSV

    # 5) 自带约定自检（用已直证的 res.npk 行号做 ground truth）
    python gpk_npk_index.py --selftest

查找变体（`--variants`）
------------------------
容器只存哈希不存名字，MISS 只是"这些候选名都不在"的证据，不是"资产不存在"的证据。
`--variants` 会在下列维度上展开候选名（笛卡尔积，去重）：
    * 分隔符：`\\` 与 `/` 两种写法；
    * 扩展名换名：`.tga` → `.dds` / `.png`；
    * 去一层目录前缀（`a\\b\\c.dds` → `b\\c.dds`）；
    * 大小写：原样 + 全小写 + 全大写 + 首字母大写；
    * 追加常见后缀：`_lod01`、`_1`（仅当搭配 `--deep-variants`）。

退出码
------
    0 成功（查找模式：命中 ≥1 为 0，0 命中为 5）
    1 用法/参数错误
    2 容器解析失败（全部失败才返回 2；部分失败计入 unresolved）
    3 写盘 IO 失败
    4 与 `--expect` 对账不符（计数模式）

边界（明确不做的事）
--------------------
  * 不修改任何容器、不写 `E:\\mrzh`；
  * 不解压载荷（索引只记 offset/size/flag，不落内容）；
  * 不替代 `fpk_fid_index.json`：fpk 族完全依赖该既有索引，本工具只做搬运与合并；
  * 皮肤贴图 / 特效贴图按名 0 命中是**预期**结果（这类资产进匿名 gpk/npk，名字不在容器里），
    详见同目录 `README_新增工具.md` 的"已知边界"。
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import io
import json
import os
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

# ── 复用项目既有解析器（只读 import，不改动它们）
_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(_HERE, "..", "01_核心解包器"),
           os.path.join(_HERE, "..", "10_应用核心", "toolkit_core"),
           os.path.join(_HERE, "..", "10_应用核心")):
    _p = os.path.abspath(_p)
    if os.path.isdir(_p):
        sys.path.insert(0, _p)

try:
    from npk_reader import aes_ecb, murmur3_x86_32, unpack_entry  # noqa
    _IMPORT_FROM = "01_核心解包器/npk_reader.py"
except Exception:  # noqa
    try:
        from resource_resolver import aes_ecb, murmur3_x86_32, unpack_entry  # noqa
        _IMPORT_FROM = "10_应用核心/toolkit_core/resource_resolver.py"
    except Exception as _exc:  # pragma: no cover
        sys.stderr.write("无法导入 aes_ecb/murmur3_x86_32/unpack_entry：%r\n"
                         "请确认 %s 存在。\n" % (_exc, _HERE))
        raise SystemExit(1)

DEFAULT_RES = r"E:\mrzh"
DEFAULT_FPK_INDEX = r"E:\la拆包项目\03拆包产物\fpk_fid_index.json"
DEFAULT_EXPECT = 3_336_339
NPK_MAGIC = 0x4B50584E
GPK_MAGICS = (b"HPGF", b"FPGH")


# ─────────────────────────────────────────────────────────── fid 约定
def path_id_raw(path: str, encoding: str = "utf-8") -> int:
    """(murmur3(0x77777777) << 32) | murmur3(0x66666666)。UTF-8 与 latin1 对纯 ASCII 等价。"""
    e = path.encode(encoding, "replace")
    return (murmur3_x86_32(e, 0x77777777) << 32) | murmur3_x86_32(e, 0x66666666)


def fid_parts(fid: int):
    """拆成 (u6, u7) = (低 32, 高 32)，与 .gpk 行内字段同序。"""
    return fid & 0xFFFFFFFF, (fid >> 32) & 0xFFFFFFFF


def candidates(name: str, variants: bool, deep: bool = False):
    """构造候选名集合（含编码/分隔符/扩展名/大小写/去一层目录变体）。"""
    out = []

    def add(s):
        if s and s not in out:
            out.append(s)

    add(name)
    slash = name.replace("\\", "/")
    add(slash)
    add(name.replace("/", "\\"))
    if variants:
        for base in {name, slash, name.replace("/", "\\")}:
            stem, ext = os.path.splitext(base)
            low = ext.lower()
            if low == ".tga":
                add(stem + ".dds")
                add(stem + ".png")
            elif low == ".dds":
                add(stem + ".tga")
            elif low == ".png":
                add(stem + ".tga")
            # 去一层目录
            for sep in ("\\", "/"):
                if sep in base:
                    add(base.split(sep, 1)[1])
            for form in (base.lower(), base.upper(), base[:1].upper() + base[1:]):
                add(form)
        if deep:
            stems = {os.path.splitext(b)[0]: os.path.splitext(b)[1] for b in list(out)}
            for st, ex in list(stems.items()):
                for suf in ("_lod01", "_lod02", "_lod1", "_1", "_high", "_preview"):
                    add(st + suf + ex)
    return out


# ─────────────────────────────────────────────────────────── 容器解析
def parse_npk(path: str):
    """返回 (entry_count, rows_iter)；rows_iter 产出 (fid, off, packed, decoded, flag)。"""
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        head = aes_ecb(f.read(32))
        _u, magic, ver, toff, cnt = struct.unpack("<QIIII", head[:24])
        if magic != NPK_MAGIC:
            raise ValueError("NPK magic 不符：0x%X（期望 0x%X）" % (magic, NPK_MAGIC))
        if not (toff < size and cnt < 5_000_000 and toff + cnt * 48 <= size):
            raise ValueError("NPK 表越界：toff=%d cnt=%d size=%d" % (toff, cnt, size))
        f.seek(toff)
        tab = aes_ecb(f.read(cnt * 48))
        if len(tab) != cnt * 48:
            raise ValueError("NPK 表读取不足：%d/%d" % (len(tab), cnt * 48))

        def rows():
            for i in range(cnt):
                fid, off, ps, ds, _c1, _c2, fl = struct.unpack_from("<QIIIIIi", tab, i * 48)
                yield i, fid, off, ps, ds, fl

        return {"kind": "npk", "magic": "0x%X" % magic, "version": ver, "table_offset": toff,
                "bytes": size, "entries": cnt, "sha16": _file_sha16(path)}, rows


GPK_XOR_BLOCKS = 0x46475049   # file header [4] = block_count ^ 该值
GPK_XOR_COUNT = 0x4647504B    # block header [0] = (entry_count+1) ^ 该值（也就是 'KPGF' 的掩码）

# ─────────────────────────────────────────── GPK 载荷位移口径（2026-09-20 修正）
# 历史缺陷：本文件此前写死 `rec["payload_delta"] = 0`，与文首「载荷自 offset + 36 起」
# 的自述自相矛盾，且实测为**错**。
#
# 实测裁定（PUBLIC_REFS_VERIFY.md §4.4 / q3d_e2e.json 的 A_gpk_delta，本轮二次复算）：
#   行内 `off` 是**块内相对位移**，块头 20 B 之后才是载荷 ⇒
#       载荷绝对起点 = block_base + off + 20
#   对单块家族（res 族 / HPGF）block_base == 16 ⇒ 等价于 `offset + 36`，
#   这正是文首那句话的来历；但对多块家族（gres 族）块基址 B ≠ 16，
#   「恒定 +36」本身也不对，必须由 block_base 派生。
#
# 向后兼容约定（**不改名、不删字段**）：
#   * `payload_delta` 保留旧字段名，值仍为 int，但语义由「（错误的）固定 0」修正为
#     **该块的行内位移修正量 = block_base + 20**（这正是历史代码本意想表达的量）。
#   * 旧调用方 `payload = open(f).seek(offset + rec["payload_delta"])` 升级后自动正确。
#   * 新增显式字段 `payload_off_rule`（= "block_base + off + 20"）与 `payload_delta_by_block`，
#     以及逐行命中结果里的 `payload_file_offset`（= off + payload_delta），语义无歧义。
#   * 旧签名（函数名 / 参数 / 返回值个数 / rows 元组 6 元组）一律不变。
GPK_PAYLOAD_ROW_DELTA = 20   # 块头 20 B（块 base +4 = entry_count+1，+8 = block_size，12..47 未用/保留）


def gpk_payload_delta(block_base: int) -> int:
    """该块的行内位移修正量：载荷绝对起点 = 行内 `off` + 本值。

    实测：单块 res 族 block_base=16 ⇒ 36（与文首「offset + 36」逐位一致）。
    """
    return int(block_base) + GPK_PAYLOAD_ROW_DELTA


def parse_gpk(path: str):
    """HPGF 族（`res\\*.gpk` + 根 `res.gpk`，56 个；block_count 实测恒为 1）。

    与 gres 族**同一套块链格式**，只是块数为 1；两者都走 `_gpk_blockchain`。
    历史口径 `n = u32@20` 比真实条目数**多 1**（该字段存的是 count+1），
    已实测：56/56 个 res 族文件按 n 取到的第 n 行 flag 是解密垃圾（如 0x75241C13），
    按 n-1 取则 0/56 越界 ⇒ 本工具用 count+1-1。
    """
    rec, rows, blocks = _gpk_blockchain(path)
    if rec["block_count"] != 1:
        raise ValueError("expected_single_block_got_%d" % rec["block_count"])
    rec["family"] = "HPGF"
    return rec, rows


def parse_gpk_gres(path: str):
    """gres 族（`Documents\\gres\\*.gpk`，35 个）：16 B 文件头 + 块链，每块独立 AES + 独立 32B 表。

    实测（前序独立取证）：35/35 可解析；块链表与 `scan_progress.json` 的
    `block_abs_positions` 逐元素吻合；2,393,893/2,393,893 条真实偏移行与
    `B+off` 处的 20 B 明文 `(comp,dec,c1,c2,flag)` 逐字节一致。
    `off == 1` 表示载荷被去重到另一个卷（不去解，按条目照常入库）。
    """
    rec, rows, blocks = _gpk_blockchain(path)
    rec["family"] = "gres"
    rec["note"] = ("gres = 16 B 头 + 块链；本条目数=全部块的行数之和；"
                   "leading_table_entries 只是第 0 块（偏移 64 处那张表）的行数")
    return rec, rows


def _gpk_blockchain(path: str):
    """统一 GPK 块链读取器。返回 (rec, rows_iter)；rows_iter 产出 (row序号, fid, off, comp, dec, flag)。

    文件头 16 B：`[0]=0 / [4]=block_count ^ 0x46475049 / [8]=2 / [12]=block_count`。
    块 base B：`B+4 = entry_count+1`、`B+8 = block_size`（下一块 = B+block_size，末块为 0）、
    `B+48` 起为 `entry_count × 32 B` 的 AES 表，行 `<8I> = (off, comp, dec, c1, c2, flag, hash_lo, hash_hi)`。
    """
    size = os.path.getsize(path)
    tables, blocks = [], []
    with open(path, "rb") as f:
        outer = aes_ecb(f.read(16))
        if len(outer) < 16:
            raise ValueError("not_blockchain_gpk: 头不足 16 B")
        _zero, masked, two, nblocks = struct.unpack("<IIII", outer)
        if two != 2 or (masked ^ GPK_XOR_BLOCKS) != nblocks or not (0 < nblocks < 100_000):
            raise ValueError("not_blockchain_gpk: [4]=0x%08X [8]=%d [12]=%d 自洽校验失败"
                             % (masked, two, nblocks))
        B = 16
        for k in range(nblocks):
            if B + 48 > size:
                raise ValueError("块 %d 头越界：B=%d size=%d" % (k, B, size))
            f.seek(B)
            bh = aes_ecb(f.read(48))
            if len(bh) < 48:
                raise ValueError("块 %d 头读取不足" % k)
            n1, bsize = struct.unpack_from("<II", bh, 4)
            cnt = n1 - 1
            if not (0 <= cnt <= 4_000_000) or B + 48 + cnt * 32 > size:
                raise ValueError("块 %d 条目数不自洽：count+1=%d block_size=%d B=%d" % (k, n1, bsize, B))
            f.seek(B + 48)
            tab = aes_ecb(f.read(cnt * 32))
            if len(tab) < cnt * 32:
                raise ValueError("块 %d 表读取不足：%d/%d" % (k, len(tab), cnt * 32))
            tables.append((B, cnt, tab))
            blocks.append({"block_index": k, "base": B, "entries": cnt, "block_size": bsize})
            if bsize <= 0 or B + bsize > size:
                break
            B += bsize

    total = sum(c for _b, c, _t in tables)
    # ★ 2026-09-20 修正：`payload_delta` 由错误的固定 0 改为「block_base + 20」。
    #   对单块家族（res 族，block_base==16）即 36 —— 与文首「载荷自 offset + 36 起」一致；
    #   对多块家族（gres 族）逐块不同，故同时给出 per-block 的 `payload_delta`。
    #   顶层 `payload_delta` 取**首块**的值，仅用于兼容只读单块家族的旧调用方；
    #   多块家族请用 `blocks[k]["payload_delta"]` 或 `payload_off`。
    _lead_base = tables[0][0] if tables else 16
    rec = {"kind": "gpk", "magic": "0x%08X" % masked, "bytes": size, "entries": total,
            "block_count": len(tables), "leading_table_entries": tables[0][1] if tables else 0,
            "table_offset": 16 + 48,
            # 兼容旧字段名（旧值 0 是错的）；新语义见上方常量注释
            "payload_delta": gpk_payload_delta(_lead_base),
            # 新增显式字段（无语义歧义）
            "payload_delta_rule": "block_base + 20",
            "payload_delta_is_per_block": len(tables) > 1,
            "payload_delta_by_block": [gpk_payload_delta(b) for b, _c, _t in tables],
            "payload_off_rule": "block_base + off + 20",
            "blocks": blocks,
            "sha16": _file_sha16(path)}
    for _blk, _delta in zip(rec["blocks"], rec["payload_delta_by_block"]):
        _blk["payload_delta"] = _delta
        _blk["payload_off_rule"] = "base + off + %d" % GPK_PAYLOAD_ROW_DELTA

    def rows():
        i = 0
        for _b, cnt, tab in tables:
            # 本块的行内位移修正量；载荷绝对起点 = o + _delta
            _delta = gpk_payload_delta(_b)
            for j in range(cnt):
                o, cm, de, _c1, _c2, fl, lo, hi = struct.unpack_from("<IIIIIIII", tab, j * 32)
                yield i, (hi << 32) | lo, o, cm, de, fl
                i += 1

    return rec, rows, blocks


def _file_sha16(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()[:16]


def _walk_ext(root: str, exts) -> list:
    """递归收集指定扩展名的容器（大小写不敏感）。用 os.walk 而非 glob，避免漏掉深层目录。"""
    hits = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() in exts:
                hits.append(os.path.join(dirpath, fn))
    return sorted(set(hits))


def scan_containers(res_root: str, only: str = "all"):
    """返回按族分组的容器清单（.gpk / .fpk / .npk 全递归，与 91+64+158 的口径一致）。"""
    out = []
    if only in ("all", "gpk"):
        for p in _walk_ext(res_root, {".gpk"}):
            out.append({"path": p, "kind_hint": "gpk"})
    if only in ("all", "fpk"):
        for p in _walk_ext(res_root, {".fpk"}):
            out.append({"path": p, "kind_hint": "fpk"})
    if only in ("all", "npk"):
        for p in _walk_ext(res_root, {".npk"}):
            out.append({"path": p, "kind_hint": "npk"})
    return out


# ─────────────────────────────────────────────────────────── 计数 / 索引
def build(res_root, only, fpk_index, limit=None, verbose=True, dedup=True, reconcile=False):
    conts = scan_containers(res_root, only)
    report = {"containers": [], "unresolved": [], "totals": {}, "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
              "res_root": res_root, "import_from": _IMPORT_FROM}
    by_kind = {"gpk": 0, "fpk": 0, "npk": 0}
    n_files = {"gpk": 0, "fpk": 0, "npk": 0}
    fids = {"gpk": set(), "fpk": set(), "npk": set()}
    # 对账专用集合（仅 --reconcile 时填充）：复刻"老口径"读取器
    rec_sets = {"res_gpk": set(), "gres_lead": set(), "phantom": set(), "gres_all": set()}
    for c in conts:
        p = c["path"]
        rel = os.path.relpath(p, res_root)
        hint = c["kind_hint"]
        if hint == "fpk":
            continue  # fpk 单独走索引文件
        rec = None
        err = None
        is_gres = False
        try:
            if hint == "gpk":
                rec, rows_iter, _bl = _gpk_blockchain(p)
                is_gres = (os.sep + "gres" + os.sep) in p.lower()
                rec["family"] = "gres" if is_gres else "res"
                if reconcile:
                    # 老口径每容器多读 1 行：表尾紧邻的 32 B 被同帧 AES 解成一行垃圾
                    try:
                        with open(p, "rb") as fh:
                            fh.seek(16 + 48 + rec["leading_table_entries"] * 32)
                            ph = aes_ecb(fh.read(32))
                        if len(ph) == 32:
                            _o, _cm, _de, _c1, _c2, _fl, lo, hi = struct.unpack("<IIIIIIII", ph)
                            rec_sets["phantom"].add((hi << 32) | lo)
                            rec["legacy_phantom_fid"] = "%016X" % ((hi << 32) | lo)
                    except Exception:
                        pass
            else:
                rec, rows_iter = parse_npk(p)
        except Exception as exc:
            err = exc
            rec = None
        if rec is None:
            report["unresolved"].append({"container": rel, "kind_hint": hint, "reason": str(err)})
            if verbose:
                print("  ! %-52s %s" % (rel, err))
            continue
        rec["container"] = rel
        by_kind[hint] += rec["entries"]
        n_files[hint] += 1
        if dedup:
            # 每个容器只读一次表：这里顺带收 fid（find/计数都靠它），避免二次 IO
            try:
                lead_n = rec.get("leading_table_entries", rec["entries"])
                for _i, _fid, _o, _ps, _ds, _fl in rows_iter():
                    fids[hint].add(_fid)
                    if reconcile and hint == "gpk":
                        if is_gres:
                            rec_sets["gres_all"].add(_fid)
                            if _i < lead_n:
                                rec_sets["gres_lead"].add(_fid)
                        else:
                            rec_sets["res_gpk"].add(_fid)
            except Exception as exc:
                rec["fid_collect_error"] = repr(exc)
        report["containers"].append(rec)
        if verbose:
            print("  %-4s %-52s entries=%-9d" % (hint, rel, rec["entries"]))

    # fpk：搬运既有索引
    if only in ("all", "fpk"):
        if not fpk_index or not os.path.isfile(fpk_index):
            report["unresolved"].append({"container": "*.fpk(64)", "kind_hint": "fpk",
                                         "reason": "既有索引缺失：%s" % fpk_index})
        else:
            t0 = time.time()
            d = json.load(open(fpk_index, encoding="utf-8"))
            f2i = d.get("fid2info") or {}
            per = {}
            for fid, v in f2i.items():
                per.setdefault(v[0], 0)
                per[v[0]] += 1
                if dedup:
                    fids["fpk"].add(int(fid, 16))
            for name, n in sorted(per.items()):
                report["containers"].append({
                    "container": name, "kind": "fpk" if name.lower().endswith(".fpk") else "npk(alias)",
                    "entries": n, "source": os.path.basename(fpk_index),
                    "note": "搬运既有索引，未重解析二进制"})
                if name.lower().endswith(".fpk"):
                    by_kind["fpk"] += n
                    n_files["fpk"] += 1
            report["fpk_index_detail"] = {"file": fpk_index, "rows_total": len(f2i),
                                          "distinct_containers": len(per),
                                          "load_seconds": round(time.time() - t0, 1),
                                          "per_container": per}
            if verbose:
                print("  fpk  从 %s 搬运 %d 行 / %d 个容器（含非 .fpk 归属 %s）"
                      % (os.path.basename(fpk_index), len(f2i), len(per),
                         [k for k in per if not k.lower().endswith('.fpk')]))

    report["totals"] = {
        "gpk_files": n_files["gpk"], "gpk_entries": by_kind["gpk"],
        "fpk_files": n_files["fpk"], "fpk_entries": by_kind["fpk"],
        "npk_files": n_files["npk"], "npk_entries": by_kind["npk"],
        "all_files": sum(n_files.values()), "all_entries": sum(by_kind.values()),
        "unresolved_containers": len(report["unresolved"]),
    }
    if dedup:
        # 关键口径：容器之间大量重复同一份资产（fpk∩gpk=191 万），
        # 所以"容器条目数"≠"全量条目数"。全量索引口径 = 去重后的 fid 并集。
        union = fids["gpk"] | fids["fpk"] | fids["npk"]
        report["totals"].update({
            "unique_fids_gpk": len(fids["gpk"]), "unique_fids_fpk": len(fids["fpk"]),
            "unique_fids_npk": len(fids["npk"]), "unique_fids_union": len(union),
            "dup_ratio": round(1 - len(union) / max(1, sum(by_kind.values())), 4),
            "intersections": {
                "fpk_and_gpk": len(fids["fpk"] & fids["gpk"]),
                "fpk_and_npk": len(fids["fpk"] & fids["npk"]),
                "gpk_and_npk": len(fids["gpk"] & fids["npk"]),
                "all_three": len(fids["fpk"] & fids["gpk"] & fids["npk"]),
            },
            "note": "unique_fids_union 是全量索引口径；unresolved 容器未计入 ⇒ 真实并集应 ≥ 该值",
        })
    if dedup and reconcile:
        # ── 复刻「老口径」（3,336,339 的出处）并给出差额归因
        legacy = (fids["fpk"] | rec_sets["res_gpk"] | rec_sets["gres_lead"]
                  | rec_sets["phantom"] | fids["npk"])
        corrected = report["totals"]["unique_fids_union"]
        report["totals"]["reconcile"] = {
            "legacy_union": len(legacy),
            "corrected_union": corrected,
            "delta": corrected - len(legacy),
            "legacy_formula": "union( fpk_fid_index(64 fpk) ∪ 91 .gpk 按 n=u32@20 读 ∪ gres 只读第 0 块 ∪ 158 .npk )",
            "legacy_breakdown": {
                "res_gpk_unique": len(rec_sets["res_gpk"]),
                "gres_leading_block_unique": len(rec_sets["gres_lead"]),
                "phantom_rows_from_off_by_one": len(rec_sets["phantom"]),
                "gres_all_blocks_unique": len(rec_sets["gres_all"]),
            },
            "why_legacy_differs": [
                "① 每个 .gpk 容器多算 1 行：真实字段是 entry_count+1，于是多读到表尾紧邻 32 B 的 AES 解密垃圾"
                "（实测 56/56 个 res 族文件第 n 行 flag 非法、第 n-1 行合法；n-1 行 0/56 越界）。91 个容器 ⇒ 多 91 个假 fid。",
                "② gres 族（Documents\\gres，35 个）不是「头+单表」，而是 16 B 头 + 块链（5~164 块，每块独立 AES 表）："
                "老口径只读偏移 64 处的第 0 块，漏掉后续块的全部条目。",
            ],
            "note": "两者对 fpk / npk 完全一致；差额全部来自 .gpk 侧的这两个口径问题。",
        }
    return report


def write_index(report, res_root, out_json, out_tsv, only="all", verbose=True):
    """流式写 JSON（紧凑数组）+ 可选 TSV。返回实际写入的行数。"""
    if out_json:
        os.makedirs(os.path.dirname(os.path.abspath(out_json)), exist_ok=True)
        fh = open(out_json, "w", encoding="utf-8")
        fh.write('{\n "meta": ')
        json.dump({k: report[k] for k in ("generated_at", "res_root", "import_from")}, fh, ensure_ascii=False)
        fh.write(',\n "totals": ')
        json.dump(report["totals"], fh, ensure_ascii=False, indent=1)
        fh.write(',\n "unresolved": ')
        json.dump(report["unresolved"], fh, ensure_ascii=False, indent=1)
        fh.write(',\n "containers": [\n')
    else:
        fh = None
    tsv = open(out_tsv, "w", encoding="utf-8") if out_tsv else None
    if tsv:
        tsv.write("#container\tkind\trow\tfid_hex\toffset\tpacked\tdecoded\tflag\n")

    rows_written = 0
    first = True
    for c in report["containers"]:
        if c.get("source"):  # fpk 搬运项：只有计数，不展开逐行
            if fh:
                fh.write(("" if first else ",\n") + "  " + json.dumps(c, ensure_ascii=False))
                first = False
            continue
        p = os.path.join(res_root, c["container"])
        if c["kind"] == "gpk":
            rec, rows_iter, _bl = _gpk_blockchain(p)   # res 族与 gres 族统一走块链
        else:
            rec, rows_iter = parse_npk(p)
        if fh:
            fh.write(("" if first else ",\n") + "  {\"container\": " + json.dumps(c["container"], ensure_ascii=False)
                     + ", \"kind\": " + json.dumps(c["kind"])
                     + (", \"family\": " + json.dumps(rec.get("family", "")) if rec.get("family") else "")
                     + ", \"block_count\": " + str(rec.get("block_count", 1))
                     + (", \"payload_delta\": " + str(rec["payload_delta"])
                        if "payload_delta" in rec else "")
                     + (", \"payload_off_rule\": " + json.dumps(rec.get("payload_off_rule", ""))
                        if rec.get("payload_off_rule") else "")
                     + ", \"entries\": " + str(rec["entries"]) + ",\n   \"rows\": [")
        first2 = True
        k = 0
        for row in rows_iter():
            k += 1
            i, fid, off, ps, ds, fl = row
            if tsv:
                tsv.write("%s\t%s\t%d\t%016X\t%d\t%d\t%d\t%d\n" % (c["container"], c["kind"], i, fid, off, ps, ds, fl))
            if fh:
                fh.write(("" if first2 else ",") + '["%016X",%d,%d,%d,%d]' % (fid, off, ps, ds, fl))
                first2 = False
            if k % 500000 == 0 and verbose:
                print("    ... %s %d/%d" % (c["container"], k, c["entries"]))
            rows_written += 1
        if fh:
            fh.write("]}")
        first = False
        if verbose:
            print("  wrote %-52s rows=%d" % (c["container"], k))
    if fh:
        fh.write("\n ]\n}\n")
        fh.close()
    if tsv:
        tsv.close()
    return rows_written


def do_find(res_root, only, fpk_index, queries, variants, deep, index_tsv, verbose=True):
    """按候选名查找。无索引时流式匹配查询集（低内存）。"""
    want = {}
    for q in queries:
        for cand in candidates(q, variants, deep):
            for enc in ("utf-8", "latin1"):
                want.setdefault(path_id_raw(cand, enc), set()).add("%s[%s]" % (cand, enc))
    hits = {}
    if index_tsv and os.path.isfile(index_tsv):
        with open(index_tsv, encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("#"):
                    continue
                parts = line.rstrip("\n").split("\t")
                fid = int(parts[3], 16)
                if fid in want:
                    hits.setdefault(fid, []).append({"container": parts[0], "kind": parts[1],
                                                     "row": int(parts[2]), "offset": int(parts[4]),
                                                     "packed": int(parts[5]), "decoded": int(parts[6]),
                                                     "flag": int(parts[7]), "via": "tsv_index"})
    else:
        for c in scan_containers(res_root, only):
            if c["kind_hint"] == "fpk":
                continue
            p = c["path"]
            fn = parse_gpk if c["kind_hint"] == "gpk" else parse_npk
            try:
                rec, rows_iter = fn(p)
            except Exception:
                for fn2 in (parse_gpk_gres,):
                    try:
                        rec, rows_iter = fn2(p)
                        break
                    except Exception:
                        rec = None
                if rec is None:
                    continue
            # 载荷绝对起点 = 行内 off + payload_delta（2026-09-20 修正；旧值 0 是错的）
            _delta = rec.get("payload_delta")
            try:
                for i, fid, off, ps, ds, fl in rows_iter():
                    if fid in want:
                        hits.setdefault(fid, []).append({
                            "container": os.path.relpath(p, res_root), "kind": rec["kind"], "row": i,
                            "offset": off, "packed": ps, "decoded": ds, "flag": fl, "via": "stream",
                            "payload_delta": _delta,
                            "payload_file_offset": (off + _delta) if _delta is not None else None})
            except Exception as exc:
                if verbose:
                    print("  ! 扫描中断 %s: %r" % (os.path.relpath(p, res_root), exc))
        # fpk 族从既有索引查
        if fpk_index and os.path.isfile(fpk_index):
            d = json.load(open(fpk_index, encoding="utf-8"))
            for fid_hex, v in (d.get("fid2info") or {}).items():
                f = int(fid_hex, 16)
                if f in want:
                    hits.setdefault(f, []).append({"container": v[0], "kind": "fpk", "row": v[1],
                                                   "offset": v[2], "packed": v[3], "decoded": v[4],
                                                   "flag": v[7], "via": "fpk_fid_index"})
    # 汇总成"逐条 HIT/MISS"
    detail = []
    for q in queries:
        cands = candidates(q, variants, deep)
        rec = {"查询": q, "候选名数": len(cands), "候选名": cands, "HIT": [], "结果": "MISS"}
        for fid, names in want.items():
            src = sorted({n.split("[")[0] for n in names})
            if not any(c in src for c in cands):
                continue
            for h in hits.get(fid, []):
                rec["HIT"].append(dict(h, fid_hex="%016X" % fid,
                                       u6="%08X" % fid_parts(fid)[0], u7="%08X" % fid_parts(fid)[1],
                                       命中候选名=[n for n in src if n in cands]))
        if rec["HIT"]:
            rec["结果"] = "HIT"
        detail.append(rec)
    return detail, want, hits


def do_selftest(res_root, verbose=True):
    """用已直证的 res.npk 行号做 ground truth，校验 fid 约定与解析链。"""
    truth = {"common\\env_map\\qiangpi.cube": 14213,
             "common\\env_map\\car_studio01.cube": 12100,
             "common\\env_map\\fashion_qiangpi.cube": 4620}
    p = os.path.join(res_root, "res.npk")
    if not os.path.isfile(p):
        return {"ok": False, "reason": "res.npk 不存在：%s" % p}
    rec, rows_iter = parse_npk(p)
    table = {}
    for i, fid, off, ps, ds, fl in rows_iter():
        table[fid] = (i, off, ps, ds, fl)
    out = []
    ok = True
    for name, row in truth.items():
        fid = path_id_raw(name)
        got = table.get(fid)
        good = bool(got) and got[0] == row
        ok = ok and good
        out.append({"path": name, "expect_row": row, "fid_hex": "%016X" % fid,
                    "u6": "%08X" % fid_parts(fid)[0], "u7": "%08X" % fid_parts(fid)[1],
                    "got": None if not got else {"row": got[0], "offset": got[1], "packed": got[2],
                                                 "decoded": got[3], "flag": got[4]},
                    "pass": good})
        if verbose:
            print("  %-42s fid=%016X row=%-6s 期望=%-6d %s" % (name, fid, got[0] if got else "MISS", row,
                                                           "PASS" if good else "FAIL"))
    return {"ok": ok, "res_npk_entries": rec["entries"], "checks": out,
            "basis": "行号 ground truth 来自 %TEMP%\\lead_cube_reenforce.py 文档串"
                     "（res.npk row 14213/12100/4620，前序会话已直证）"}


# ─────────────────────────────────────────────────────────── main
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="gpk_npk_index.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="LifeAfter 容器（56+35 .gpk / 64 .fpk / 158 .npk）全量条目索引与按候选名查找。",
        epilog="退出码：0 成功 / 1 参数错 / 2 容器全失败 / 3 写盘失败 / 4 对账不符 / 5 查找 0 命中")
    ap.add_argument("--res-root", default=DEFAULT_RES, help="游戏资源根（默认 %s）" % DEFAULT_RES)
    ap.add_argument("--fpk-index", default=DEFAULT_FPK_INDEX, help="既有 fpk 索引 JSON")
    ap.add_argument("--only", choices=("all", "gpk", "fpk", "npk"), default="all", help="只处理某一族")
    ap.add_argument("--count", action="store_true", help="只对账计数（默认行为之一）")
    ap.add_argument("--out", metavar="JSON", help="写全量索引 JSON（流式）")
    ap.add_argument("--tsv", metavar="TSV", help="同时/另外写紧凑 TSV（--find 复用）")
    ap.add_argument("--find", action="append", metavar="路径", help="按候选名查找（可重复给多个）")
    ap.add_argument("--index", metavar="TSV", help="查找时复用已建的 TSV 索引")
    ap.add_argument("--variants", action="store_true", help="展开 .tga/.dds/.png、大小写、去一层目录等变体")
    ap.add_argument("--deep-variants", action="store_true", help="再追加 _lod01/_1 等后缀变体")
    ap.add_argument("--expect", type=int, default=DEFAULT_EXPECT, help="对账期望条目数（默认 %d，去重并集口径）" % DEFAULT_EXPECT)
    ap.add_argument("--no-dedup", action="store_true", help="跳过去重 fid 并集统计（省内存，但失去全量口径对账）")
    ap.add_argument("--reconcile", action="store_true",
                    help="复刻历史口径（91 个 gpk 各多 1 行 + gres 只读第 0 块）并输出差额归因，"
                         "用于解释 3,336,339 的出处（会多占内存）")
    ap.add_argument("--selftest", action="store_true", help="用 res.npk 已直证行号自检 fid 约定")
    ap.add_argument("--json", dest="json_out", metavar="PATH", help="把本次运行的计数/查找结果也落一份 JSON")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    v = not args.quiet

    if args.selftest:
        print("== 自检：fid 约定 vs res.npk 已直证行号 ==")
        st = do_selftest(args.res_root, v)
        print(json.dumps({k: st[k] for k in ("ok", "res_npk_entries", "basis")}, ensure_ascii=False))
        if args.json_out:
            json.dump(st, open(args.json_out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        return 0 if st["ok"] else 4

    if args.find:
        print("== 查找 %d 个候选路径（variants=%s）==" % (len(args.find), args.variants))
        detail, want, hits = do_find(args.res_root, args.only, args.fpk_index, args.find,
                                     args.variants, args.deep_variants, args.index, v)
        for d in detail:
            print("\n查询: %s  ⇒ %s（候选 %d 个）" % (d["查询"], d["结果"], d["候选名数"]))
            for h in d["HIT"]:
                print("   HIT %-14s %-10s row=%-7d off=%-12d packed=%-9d decoded=%-9d flag=%-3d fid=%s via=%s"
                      % (h["container"], h["kind"], h["row"], h["offset"], h["packed"], h["decoded"],
                         h["flag"], h["fid_hex"], h["via"]))
                print("       命中候选名: %s" % ", ".join(h["命中候选名"]))
            if not d["HIT"]:
                print("   0 命中。注意：容器只存哈希不存名字 ⇒ MISS 只证明『这些候选名都不在』，"
                      "不证明资产不存在。已试候选名：%s" % ", ".join(d["候选名"][:8]))
        n_hit = sum(1 for d in detail if d["HIT"])
        if args.json_out:
            json.dump({"queries": detail}, open(args.json_out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        return 0 if n_hit else 5

    # 计数 / 建索引
    print("== 扫描容器（res-root=%s, only=%s）==" % (args.res_root, args.only))
    rep = build(args.res_root, args.only, args.fpk_index, verbose=v, dedup=not args.no_dedup,
                reconcile=args.reconcile)
    t = rep["totals"]
    print("\n== 条目数对账 ==")
    print("  .gpk  %3d 个容器  %9d 条" % (t["gpk_files"], t["gpk_entries"]))
    print("  .fpk  %3d 个容器  %9d 条  （源自 %s）" % (t["fpk_files"], t["fpk_entries"], os.path.basename(args.fpk_index)))
    print("  .npk  %3d 个容器  %9d 条" % (t["npk_files"], t["npk_entries"]))
    print("  容器行数合计 %3d 个容器  %9d 条" % (t["all_files"], t["all_entries"]))
    print("  未解析容器：%d 个" % t["unresolved_containers"])
    for u in rep["unresolved"]:
        print("    ! %s : %s" % (u["container"], u["reason"]))
    if not args.no_dedup:
        print("\n  ── 去重口径（容器存的是哈希，同一资产会横跨多个容器）")
        print("  .gpk 去重 fid %9d   .fpk 去重 fid %9d   .npk 去重 fid %9d"
              % (t["unique_fids_gpk"], t["unique_fids_fpk"], t["unique_fids_npk"]))
        print("  交集：fpk∩gpk %d，fpk∩npk %d，gpk∩npk %d，三者 %d"
              % (t["intersections"]["fpk_and_gpk"], t["intersections"]["fpk_and_npk"],
                 t["intersections"]["gpk_and_npk"], t["intersections"]["all_three"]))
        print("  ★ 全量条目数（去重并集）= %d   重复率 %.2f%%"
              % (t["unique_fids_union"], t["dup_ratio"] * 100))
    measured = t.get("unique_fids_union", t["all_entries"])
    delta = measured - args.expect
    print("\n  与 --expect %d 之差：%+d  （口径=%s）"
          % (args.expect, delta, "去重并集" if not args.no_dedup else "容器行数合计"))
    if not args.no_dedup and t["unresolved_containers"]:
        print("  ⚠ %d 个容器未解析未计入并集 ⇒ 真实并集 ≥ %d；若差额 %+d 恰由它们补足则可对平。"
              % (t["unresolved_containers"], measured, -delta))
    rc = t.get("reconcile")
    if rc:
        print("\n  ── 历史口径复刻（3,336,339 的出处）")
        print("  老口径并集 = %d     修正后并集 = %d     差 %+d"
              % (rc["legacy_union"], rc["corrected_union"], rc["delta"]))
        print("  公式：%s" % rc["legacy_formula"])
        b = rc["legacy_breakdown"]
        print("  res-gpk 唯一 %d ; gres 第0块唯一 %d ; 每容器假行 %d 个 ; gres 全块唯一 %d"
              % (b["res_gpk_unique"], b["gres_leading_block_unique"],
                 b["phantom_rows_from_off_by_one"], b["gres_all_blocks_unique"]))
        for s in rc["why_legacy_differs"]:
            print("   · %s" % s)
        print("  ⇒ 老口径 %s 3,336,339" % ("恰等于" if rc["legacy_union"] == args.expect else "不等于"))

    rows_written = None
    if args.out or args.tsv:
        try:
            rows_written = write_index(rep, args.res_root, args.out, args.tsv, args.only, v)
        except OSError as exc:
            sys.stderr.write("写盘失败：%r\n" % (exc,))
            return 3
        print("  索引落盘：%s%s" % (args.out or "-", ("；TSV " + args.tsv) if args.tsv else ""))
        if rows_written is not None:
            print("  展开写出的行数（gpk+npk）：%d" % rows_written)

    if args.json_out:
        payload = dict(rep)
        payload["expect"] = args.expect
        payload["delta_vs_expect"] = delta
        payload["rows_expanded"] = rows_written
        json.dump(payload, open(args.json_out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("  运行台账：%s (%d B)" % (args.json_out, os.path.getsize(args.json_out)))

    if t["all_files"] == 0:
        return 2
    if args.count and delta != 0:
        rc2 = t.get("reconcile")
        # --reconcile 下，只要历史口径能精确复现 --expect，就算对账通过（差额已归因）
        if not (rc2 and rc2["legacy_union"] == args.expect):
            return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
