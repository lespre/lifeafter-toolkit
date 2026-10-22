# -*- coding: utf-8 -*-
"""0x56 / 0x66 / 0x76 哈希索引族的结构解析（只解析索引与节点，不猜行语义）。

已验证（PE pe_20261020，vehicle_basic_conf）：
  blob[0:4] = key_hash_offset（指向索引尾，相对 blob 起点的绝对偏移）
  tail[0]   = 0x56 → 后接 key_type 一字节
              0x66 → 后接 value_type 一字节
              0x76 → 后接 key_type + value_type 两字节
  然后 uleb(entry_count)，再 entry_count 个 8 字节 (hash32, node_offset)
  node 处 = (uleb key, uleb record_offset)

结构性事实：vehicle_basic_conf 的 81 个 node 全部可解，key 82/79/74/73/71…
但 record_offset 指向的区域尚未被证明是行起点（见 00_规范与工具/治理/手册/vehicle_basic_conf_0x56.md）。
"""
from __future__ import annotations

import struct
from typing import Any


def _uleb(blob: bytes, i: int, end: int) -> tuple[int, int]:
    v = 0
    shift = 0
    while i < end:
        c = blob[i]
        v |= (c & 0x7F) << shift
        i += 1
        if not c & 0x80:
            return v, i
        shift += 7
    raise ValueError("uleb 越界")


def parse_hash_index(blob: bytes) -> dict[str, Any]:
    """解析哈希索引尾。返回 {marker, types, entries, pairs, nodes, error}。"""
    out: dict[str, Any] = {"marker": None, "entries": 0, "pairs": [], "nodes": [],
                           "error": None}
    if len(blob) < 8:
        out["error"] = "blob 过短"
        return out
    off = struct.unpack_from("<I", blob, 0)[0]
    if not (4 <= off < len(blob)):
        out["error"] = "key_hash_offset 越界 %d" % off
        return out
    tail = blob[off:]
    marker = tail[0]
    out["marker"] = "0x%02x" % marker
    if marker not in (0x56, 0x66, 0x76):
        out["error"] = "未知索引 marker 0x%02x" % marker
        return out

    cur = 1
    types = {}
    if marker == 0x56:
        types["key_type"] = tail[cur]; cur += 1
    elif marker == 0x66:
        types["value_type"] = tail[cur]; cur += 1
    else:
        types["key_type"] = tail[cur]
        types["value_type"] = tail[cur + 1]
        cur += 2
    out["types"] = types

    try:
        count, cur = _uleb(tail, cur, len(tail))
    except ValueError:
        out["error"] = "entry_count uleb 解析失败"
        return out
    out["entries"] = count
    if cur + 8 * count > len(tail):
        out["error"] = "pairs 越界"
        return out

    pairs = []
    for i in range(count):
        h, node_off = struct.unpack_from("<II", tail, cur + 8 * i)
        pairs.append({"hash32": "%08X" % h, "node_offset": node_off})
    out["pairs"] = pairs

    node_offs = sorted({p["node_offset"] for p in pairs})
    nodes = []
    for i, noff in enumerate(node_offs):
        end = node_offs[i + 1] if i + 1 < len(node_offs) else len(blob)
        try:
            key, pos = _uleb(blob, noff, end)
            rec, pos2 = _uleb(blob, pos, end)
        except ValueError:
            nodes.append({"node_offset": noff, "status": "unparsed",
                          "raw": blob[noff:min(end, noff + 16)].hex()})
            continue
        nodes.append({"node_offset": noff, "key": key, "record_offset": rec,
                      "status": "uleb_pair"})
    out["nodes"] = nodes
    return out


def summarize(blob: bytes) -> str:
    r = parse_hash_index(blob)
    if r["error"]:
        return "哈希索引: %s（marker=%s）" % (r["error"], r["marker"])
    return ("哈希索引 marker=%s 类型=%s 条目=%d 节点=%d（可解 %d）"
            % (r["marker"], r["types"], r["entries"], len(r["nodes"]),
               sum(1 for n in r["nodes"] if n.get("status") == "uleb_pair")))
