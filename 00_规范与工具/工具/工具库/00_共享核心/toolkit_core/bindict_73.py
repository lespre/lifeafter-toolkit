# -*- coding: utf-8 -*-
r"""bindict_73.py — 解 `0x73` 包装（NeoX marshal code object）里的 bindict 表。

═══════════════════════════════════════════════════════════════════════════
★ 为什么需要它
   客户端 `com/cdata/*.py` 有两族载荷：
     a) `x{` 表体       → toolkit_core.bindict_table.decode_table_rows 直接能解；
     b) `0x73` 开头     → 本项目以前一律抛 AnotherFamily（hotfix_rows.py:129），
                          实际不是坏数据，是**另一层容器**：一个 NeoX marshal
                          code object，表体躺在它的常量池里（bytes 常量）。
   本模块负责剥这层容器，然后复用 bindict_table 的行解码。

═══════════════════════════════════════════════════════════════════════════
★ 实测布局（weapon_skin_data.py，两版都对上；字节证据见注释）

  文件 = code object（script_decode 结构化解析终点 == 文件长度，逐字节吻合）
      0x00        73                       code 标签
      0x01..0x14  5 × u32                  argcount / posonly / kwonly /
                                           stacksize / flags
      0x15..      fb|7b + u32 len + bytes   co_code
      然后        co_consts(2e + u8 n + 值) …
                  ★ 表体 = 其中一个 bytes 常量：`7b|fb + u32 len + payload`
                    实测：weapon_skin_data.py  offset 264 = `7b e6 00 00 00`
                          → payload 起点 269，长度 11584（旧版）
                          chs 版同构：payload 长 11308/10644
                  ★ 注意 hotfix 记录里的「u32@12 = 1280」是**错位读**：
                    offset 12 是 kwonly 的末字节，offset 13 起才是
                    stacksize=5（00 05 00 00 00 才是 5）。该值不是行数。

  payload（= 表体）布局：
      0x00..0x03  u32 count      ┐ 这两项和 `x{` 表体的 CHS 头一致
      0x04..0x07  u32 reserved=0 │
      0x08..       count × u32 ends
      ★ 基表的 ends **全部为 0**（实测两版 233/248 项全 0）——基表不带自己的
        字面量池，字符串槽位由 `_chs.py` 提供。
      ★ 关键不变量（已实测，可当断言）：`count == len(chs_pool)`。
        旧版 233/233，新版 248/248。
      8+4*count.. u32 de          ← `de` 是「索引尾」相对 data 的偏移
      de 之前     schema 区 + 行区（0x96/0xd6 行）
                  schema 就在 data[4]，实测两版全部行都是 schema_ref=78、标记 0x96
                  （schema：bits=30, n=41 个字段槽）
      data+de     `76 | 01 | 0b` 索引尾

  索引尾（0x76）实测：
      +0  76                索引标签
      +1  01                key 类型
      +2  0b                value 类型（= jump/引用）
      +3  uleb bucket_count   ★ 实测 0x83 0x01 = 131（旧版）；u8 读成 0x83 是
                              巧合，**uleb 才对**——本模块自己按「能否解析出
                              合法节点区」去选，不硬编码
      +n  桶表：bucket_count × 8 字节 = (u32 hash, u32 node_offset)
          ★ hash 升序排列（实测桶 0..7 = 8.9M/39.6M/80.4M/111M/151M…递增）
          ★ node_offset 是 **blob 绝对偏移**，且逐个都指向一个节点记录的首字节
            （旧版 131/131 命中，见 meta["index"]["bucket_offsets_are_node_starts"]）
      …   节点区：连续 (uleb key, uleb row_offset) 对，正好吃到 blob 末尾
          实测旧版 673 B / 131 对，一字节不剩；row_offset 全 < de（落进行区）

★ 未解/不敢说死的地方（如实列出，不用默认值糊）
  1) 桶表第一列 u32 到底是什么哈希：试了 fnv1a/murmur3/crc32/djb2/sdbm/
     java-hash/md5 截断等 13 种对 (key) 和 (uleb bytes) 的候选，**0/131 命中**。
     查找不需要它（节点记录自带 key），所以不阻塞；但它是什么，本题没结论。
  2) 表里存在 8 位 key（如 11101831、11101851），与 7 位主键呈 `base*10+1`：
     20/20 满足 k%10==1 且 base 在同表另有行、同模型不同参数（新旧两版完全一致）
     → 判定为「变体/升阶」编号，**不是解析噪声**；但没有外部真值能独立证实。
  3) `0x76` 索引尾里 hash 与 key 的对应关系没做一致性校验（见 1）。

═══════════════════════════════════════════════════════════════════════════
用法：
    from toolkit_core.bindict_73 import decode_73_table
    rows, unbound, meta = decode_73_table("…/weapon_skin_data.py")   # pool 自动配 _chs
    rows, unbound, meta = decode_73_table(bytes_or_path, pool=[...])

    CLI: 命令行/解码_0x73.py <表.py> [-o OUTDIR] [--format json,tsv]
"""
from __future__ import annotations

import struct
from pathlib import Path
from typing import Any, Iterable, Sequence

from toolkit_core.bindict_rows import uleb

__all__ = [
    "Bindict73Error",
    "decode_73_table",
    "unwrap_container",
    "parse_index_73",
    "extract_body",
    "load_pool_for",
]

ROW_MARKERS = (0x96, 0xD6, 0xC6)
MAPPING_MARKER = 0x36
CODE_TAG = 0x73
BLOB_TAGS = (0x7B, 0xFB)
INDEX_TAG = 0x76


class Bindict73Error(ValueError):
    """载荷不是可解的 0x73 bindict 表。"""


# ─────────────────────────────────────────────────────── 基础读取
def _u32(buf: bytes, off: int) -> int:
    if off < 0 or off + 4 > len(buf):
        raise Bindict73Error("u32 越界 @%d" % off)
    return struct.unpack_from("<I", buf, off)[0]


def _read_src(src: bytes | bytearray | str | Path) -> tuple[bytes, Path | None]:
    if isinstance(src, (bytes, bytearray)):
        return bytes(src), None
    path = Path(src)
    return path.read_bytes(), path


# ─────────────────────────────────────────────────────── 容器剥离
def _looks_like_body(payload: bytes) -> dict[str, Any] | None:
    """结构自校验：payload 像不像一个 bindict 表体。返回 body info 或 None。"""
    if len(payload) < 16:
        return None
    try:
        count = _u32(payload, 0)
        reserved = _u32(payload, 4)
    except Bindict73Error:
        return None
    if reserved != 0 or not (1 <= count <= 200_000):
        return None
    table_end = 8 + 4 * count
    if table_end + 12 > len(payload):
        return None
    ends = struct.unpack_from("<%dI" % count, payload, 8)
    ends_all_zero = all(e == 0 for e in ends)
    data = payload[table_end:]
    de = _u32(data, 0)
    if not (4 < de < len(data) - 3):
        return None
    if data[de] != INDEX_TAG:
        return None
    kt, vt = data[de + 1], data[de + 2]
    if kt not in (0x01, 0x05) or vt not in (0x01, 0x0B):
        return None
    # 行区里至少要有一个真行头（标记 + 可解 schema_ref）
    row_heads = 0
    for pos in range(4, de):
        if data[pos] in ROW_MARKERS:
            try:
                uleb(data, pos + 1, len(data))
            except ValueError:
                continue
            row_heads += 1
    if row_heads == 0:
        return None
    return {
        "count": count,
        "reserved": reserved,
        "ends_all_zero": ends_all_zero,
        "ends_last": ends[-1],
        "body_len": len(payload),
        "blob_off": table_end,
        "de": de,
        "rows_region": [4, de],
        "index_tag": "76 %02x %02x" % (kt, vt),
        "row_markers_seen": row_heads,
    }


def unwrap_container(data: bytes) -> list[dict[str, Any]]:
    """从 0x73 容器里找出所有候选表体（按文件偏移）。

    返回 [{"payload": bytes, "payload_off": int, "payload_len": int,
           "tag": "0x7b", "via": "marshal-bytes-tag"}]。

    实现说明（为什么不导航 marshal 结构）：code object 的常量池顺序解析
    依赖 co_code/co_consts/co_names/… 一长串字段，任何一处偏差就整体错位。
    这里改用「`7b|fb + u32 长度` 标签扫描 + 表体结构自校验」，对无关字节
    免疫；定位到的偏移与 script_decode 的常量表完全一致（测试里对拍）。
    """
    out: list[dict[str, Any]] = []
    n = len(data)
    for i in range(n - 5):
        if data[i] not in BLOB_TAGS:
            continue
        ln = _u32(data, i + 1)
        if not (64 <= ln <= n - i - 5):
            continue
        payload = data[i + 5: i + 5 + ln]
        if _looks_like_body(payload) is None:
            continue
        out.append({
            "payload": payload,
            "payload_off": i + 5,
            "payload_len": ln,
            "tag": "0x%02x" % data[i],
            "via": "marshal-bytes-tag",
        })
    return out


def extract_body(src: bytes | bytearray | str | Path) -> tuple[bytes, dict[str, Any]]:
    """剥容器 → (表体 bytes, container meta)。

    也接受「已经是表体」的输入（直接返回, container.kind='raw_body'）。
    """
    data, _path = _read_src(src)
    info = _looks_like_body(data)
    if info is not None:
        return data, {"kind": "raw_body", "payload_off": 0, "payload_len": len(data),
                      "candidates": 1, "file_len": len(data)}
    cands = unwrap_container(data)
    if not cands:
        raise Bindict73Error(
            "找不到 0x73 表体载荷（文件头 %s）" % data[:4].hex())
    best = max(cands, key=lambda c: c["payload_len"])
    kind = "code_object" if data[:1] == b"\x73" else "marshal_bytes"
    return best["payload"], {
        "kind": kind,
        "file_len": len(data),
        "payload_off": best["payload_off"],
        "payload_len": best["payload_len"],
        "payload_tag": best["tag"],
        "candidates": len(cands),
        "candidate_offsets": [c["payload_off"] for c in cands],
    }


# ─────────────────────────────────────────────────────── 0x76 索引尾
def _parse_node_pairs(data: bytes, start: int, too: int):
    """节点区：连续 (uleb key, uleb row_offset)，必须刚好吃到 too。

    返回 (pairs, record_offsets, consumed_all)。record_offsets 是每条记录的
    **首字节偏移**——桶表的第二列应当逐个指向这些偏移（实测 131/131 命中）。
    """
    pos = start
    pairs: list[tuple[int, int]] = []
    rec_offs: list[int] = []
    try:
        while pos < too:
            rec_offs.append(pos)
            key, pos = uleb(data, pos, too)
            off, pos = uleb(data, pos, too)
            pairs.append((key, off))
    except ValueError:
        return pairs, rec_offs, False
    return pairs, rec_offs, pos == too


def parse_index_73(data: bytes) -> tuple[list[tuple[int, int]], dict[str, Any]]:
    """解 0x76 索引尾 → ([(key, row_start)], meta)。

    只认「能自我验证」的读法：桶数 × 8 字节的桶表、桶偏移全部落在 blob 内、
    节点区恰好解析出「桶数个」对且行偏移全部 < de、key 无重复。
    任何一种候选读法都过不了就当失败（不猜）。
    """
    de = _u32(data, 0)
    if data[de] != INDEX_TAG:
        raise Bindict73Error("blob@%d 不是 0x76 索引尾" % de)
    kt, vt = data[de + 1], data[de + 2]
    tail = data[de:]
    errors: list[str] = []

    for base_name, conv in (
        ("blob", lambda v: v),
        ("tail", lambda v: v + de),
        ("shift8", lambda v: v >> 8),
    ):
        cands: list[tuple[int, int, str]] = []
        bc8 = tail[3]
        if 4 + 8 * bc8 <= len(tail):
            cands.append((bc8, 4, "u8"))
        try:
            bcu, pu = uleb(tail, 3, len(tail))
            if pu + 8 * bcu <= len(tail):
                cands.append((bcu, pu, "uleb"))
        except ValueError:
            pass
        for bc, npos, bc_enc in cands:
            if bc < 1:
                continue
            raw = [struct.unpack_from("<I", tail, npos + 8 * i + 4)[0] for i in range(bc)]
            offs = [conv(v) for v in raw]
            if not all(de <= o < len(data) for o in offs):
                errors.append("bc=%d/%s/base=%s: 桶偏移越界" % (bc, bc_enc, base_name))
                continue
            node_start = min(offs)
            pairs, rec_offs, ok = _parse_node_pairs(data, node_start, len(data))
            if not ok:
                errors.append("bc=%d/%s/base=%s: 节点区没吃到末尾" % (bc, bc_enc, base_name))
                continue
            if len(pairs) != bc:
                errors.append("bc=%d/%s/base=%s: 节点对数 %d≠桶数"
                              % (bc, bc_enc, base_name, len(pairs)))
                continue
            if len({k for k, _ in pairs}) != bc:
                errors.append("bc=%d/%s/base=%s: key 有重复" % (bc, bc_enc, base_name))
                continue
            if not all(0 <= off < de for _, off in pairs):
                errors.append("bc=%d/%s/base=%s: 行偏移不在行区" % (bc, bc_enc, base_name))
                continue
            hashes = [struct.unpack_from("<I", tail, npos + 8 * i)[0] for i in range(bc)]
            bucket_hits_node = len(set(offs) & set(rec_offs))
            aliases: dict[int, list[int]] = {}
            for key, off in pairs:
                aliases.setdefault(off, []).append(key)
            aliases = {o: ks for o, ks in aliases.items() if len(ks) > 1}
            index_rows = sorted(pairs, key=lambda kv: kv[0])
            meta = {
                "tag": "76 %02x %02x" % (kt, vt),
                "de": de,
                "tail_len": len(tail),
                "bucket_count": bc,
                "bucket_count_encoding": bc_enc,
                "bucket_offset_base": base_name,
                "bucket_table_span": [de + npos, de + npos + 8 * bc],
                "node_area_span": [node_start, len(data)],
                "node_records": len(pairs),
                "bucket_offsets_are_node_starts": bucket_hits_node == bc,
                "bucket_node_hits": bucket_hits_node,
                "hashes_sorted_ascending": all(a <= b for a, b in zip(hashes, hashes[1:])),
                "hash_first_last": [hashes[0], hashes[-1]],
                "row_offsets_lt_de": True,
                "alias_row_offsets": {str(k): v for k, v in sorted(aliases.items())},
                "errors_tried": errors,
            }
            return index_rows, meta
    raise Bindict73Error("0x76 索引尾解析失败：%s" % "; ".join(errors[:6]))


# ─────────────────────────────────────────────────────── pool
def load_pool_for(path: str | Path) -> list[str]:
    """按 `<stem>_chs.py` 约定取字符串池。"""
    from toolkit_core import bindict_table as BT

    p = Path(path)
    chs = p.with_name(p.stem + "_chs.py")
    if not chs.is_file():
        raise Bindict73Error("找不到配对 _chs：%s" % chs)
    data = chs.read_bytes()
    try:
        body, _cm = extract_body(data)
    except Bindict73Error:
        return BT.parse_legacy_chs_pool(data[12:])
    try:
        return BT.parse_chs_pool(body)
    except ValueError:
        return BT.parse_legacy_chs_pool(data[12:])


# ─────────────────────────────────────────────────────── 主入口
def decode_73_table(
    src: bytes | bytearray | str | Path,
    pool: Sequence[str] | None = None,
    *,
    chs: str | Path | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """解一张 0x73 包装的 bindict 表。

    参数
        src   : 文件路径或原始字节（容器码流 / 裸表体都行）
        pool  : 字符串池；None 时按路径自动找 `<stem>_chs.py`
        chs   : 显式指定 _chs 路径（pool=None 时生效）

    返回 (rows, unbound, meta)
        rows    : bindict_table.decode_table_rows 的行 dict 列表
        unbound : 解不出的行（原样返回，不吞）
        meta    : 容器/表体/索引/统计的自检信息
    """
    from toolkit_core import bindict_table as BT

    data, path = _read_src(src)
    body, cmeta = extract_body(data)
    binfo = _looks_like_body(body)
    if binfo is None:                       # extract_body 已保证, 这里只是防御
        raise Bindict73Error("载荷不是合法表体")

    pool_missing = False
    if pool is None:
        if chs is not None or path is not None:
            try:
                pool = load_pool_for(chs if chs is not None else path)
            except Bindict73Error:
                # 数值表没有 _chs 配对是正常的（字段名就没有字符串池），
                # 用空池解，字段名退化成 <slot_N>，但要如实标出来。
                pool = []
                pool_missing = True
        else:
            pool = []
    pool = list(pool)

    blob = body[binfo["blob_off"]:]
    index_rows, imeta = parse_index_73(blob)

    # 与既有实现交叉验证（不一致就如实报，不静默）
    agree = None
    try:
        legacy = BT.parse_index(blob)
        agree = sorted(legacy) == sorted(index_rows)
    except Exception as exc:                # noqa: BLE001 — 交叉验证失败不该致命
        agree = "legacy parse_index 失败: %s" % exc

    rows, unbound = BT.decode_table_rows(body, pool, index_rows=index_rows)

    seen_rows = [r for r in rows if isinstance(r, dict) and "key" in r]
    meta = {
        "container": cmeta,
        "body": binfo,
        "pool_size": len(pool),
        "pool_matches_count": len(pool) == binfo["count"],
        "index": {k: v for k, v in imeta.items() if not k.startswith("_")},
        "index_agrees_with_bindict_table": agree,
        "rows": {
            "decoded": len(seen_rows),
            "unbound": len(unbound),
            "key_min": min((r["key"] for r in seen_rows), default=None),
            "key_max": max((r["key"] for r in seen_rows), default=None),
            "distinct_starts": len({r.get("start") for r in seen_rows}),
        },
        "warnings": [],
    }
    if not meta["pool_matches_count"]:
        meta["warnings"].append(
            "表体 count=%d 与 pool=%d 不等（不变量被打破，字段名可能错位）"
            % (binfo["count"], len(pool)))
    if agree is not True:
        meta["warnings"].append("与 bindict_table.parse_index 不一致：%r" % (agree,))
    if unbound:
        meta["warnings"].append("有 %d 行解不出（见 unbound）" % len(unbound))
    return rows, unbound, meta
