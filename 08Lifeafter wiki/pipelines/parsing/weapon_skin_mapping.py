# -*- coding: utf-8 -*-
"""Weapon Skin 显式映射表专用解析（Phase 2 — Explicit Mapping Closure）。

背景：`skin_2_sfx_function_map` / `_detail` / `skin_function_item_id_to_anim_name`
三张表用通用 *行内容* decoder 出 0 行（不是标准行式表），但 **索引层完全标准**：

    payload = 公共头(263B) + "x{" + u32 body_len + body
    body    = u32 c0 + c0×4B + blob          # 25444/18793/884 的 c0=0
    blob    = u32 de + ... + [de:] 节点表    # tail[3]=节点数, 节点=(u32 hash, u32 off)
    行表     = parse_index(blob) → [(row_key, row_offset)]，row_offset 指向 blob 内行体

已证（BA8A 快照，2026-09-13）：
  * `skin_2_sfx_function_map` 75 行，row_key = **skin_item_id**（1110xxx），
    节点 hash 与 `weapon_skin_data` 节点 hash **完全同源**（8932426/39624095/80427987…）
  * `skin_2_sfx_function_map_detail` 75 行，同 key 空间，行体更大（每皮肤多条参数）
  * `skin_function_item_id_to_anim_name` 44 行，row_key = **sfx_function row key**（1120xxx）

本模块只负责解析（定位 + 行体结构），不做业务判定，不写 domain artifact。
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO / "tools") not in sys.path:
    sys.path.insert(0, str(REPO / "tools"))

WORKCOPY = Path(r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_BA8A239A\entries")
BA8A_ENTRIES = {
    "skin_2_sfx_function_map": 25444,
    "skin_2_sfx_function_map_detail": 18793,
    "skin_function_item_id_to_anim_name": 884,
    "weapon_skin_data": 11817,
    "weapon_skin_effect_show_data": 3671,
    "weapon_skin_effect_show_data_chs": 19852,
    # 备用来源（ykxq 通道 _chs 变体，仅用于对照，不作为本轮 basis）
    "skin_2_sfx_function_map_chs_variant": 528,
}


def payload_bytes(entry: int, workcopy: Path = WORKCOPY) -> bytes | None:
    for name in (f"{entry:06d}.bin", f"{entry}.bin"):
        p = workcopy / name
        if p.exists():
            return p.read_bytes()
    return None


def split_frame(payload: bytes) -> tuple[bytes, int]:
    """→ (blob, c0)。blob 起点即 de 字段所在处。"""
    o = payload.find(b"x{")
    if o < 0:
        raise RuntimeError("payload has no x{ frame")
    n = int.from_bytes(payload[o + 2:o + 6], "little")
    body = payload[o + 6:o + 6 + n]
    c0 = struct.unpack_from("<I", body, 0)[0]
    return body[8 + 4 * c0:], c0


def node_table(blob: bytes) -> tuple[int, list[tuple[int, int]]]:
    """→ (de, [(hash, off), ...])。"""
    de = struct.unpack_from("<I", blob, 0)[0]
    if de >= len(blob):
        return de, []
    tail = blob[de:]
    bc = tail[3] if len(tail) > 3 else 0
    if not bc or 4 + 8 * bc > len(tail):
        return de, []
    return de, [struct.unpack_from("<II", tail, 4 + 8 * i) for i in range(bc)]


def _parse_index(blob: bytes) -> list[tuple[int, int]]:
    mod = __import__("rebuild_weapon_skin_catalog_current")
    return mod.parse_index(blob)          # 复用仓库既有实现（不重写 uleb/索引扫描）


def _uleb(buf: bytes, i: int, end: int) -> tuple[int, int]:
    mod = __import__("rebuild_weapon_skin_catalog_current")
    return mod.uleb(buf, i, end)


def parse(entry: int, workcopy: Path = WORKCOPY) -> dict:
    """解析一张映射表 → {rows:[{key, offset, refs:[...], raw_len}], nodes, blob_len, c0, de}。"""
    pay = payload_bytes(entry, workcopy)
    if pay is None:
        return {"rows": [], "nodes": [], "status": "payload_unavailable", "entry": entry}
    blob, c0 = split_frame(pay)
    de, nodes = node_table(blob)
    rows = _parse_index(blob)
    out_rows: list[dict] = []
    by_off = sorted(rows, key=lambda x: x[1])
    for idx, (key, off) in enumerate(by_off):
        nxt = by_off[idx + 1][1] if idx + 1 < len(by_off) else len(blob)
        rec = _row_record(blob, off, end_hint=nxt)
        rec["key"] = key
        rec["offset"] = off
        out_rows.append(rec)
    return {"rows": out_rows, "nodes": nodes, "status": "parsed", "entry": entry,
            "blob_len": len(blob), "c0": c0, "de": de}


def _row_record(blob: bytes, off: int, limit: int = 4096, end_hint: int | None = None) -> dict:
    """行体记录：形如 `27 <u8 sub> <u8 n> [n × u24 ref]`（可连续多组）。

    返回 {refs:[...], groups:[(tag,sub,n)], raw_len}；结构未归一时 refs 为空、保留 groups。
    """
    end = min(len(blob), end_hint if end_hint is not None else off + limit)
    i = off
    groups: list[tuple[int, int, int]] = []
    refs: list[int] = []
    raw_start = off
    # 连续解析同一行体的组：tag=0x27 → sub + n + n×u24；tag=0x36 → sub + n + n×u8
    while i + 3 <= end and len(groups) < 512:
        tag = blob[i]
        if tag not in (0x27, 0x36, 0x76):
            break
        sub = blob[i + 1]
        n = blob[i + 2]
        if tag in (0x27, 0x76):
            need = i + 3 + 3 * n
            if need > end:
                break
            refs.extend(int.from_bytes(blob[i + 3 + 3 * k:i + 6 + 3 * k], "little") for k in range(n))  # u24
            groups.append((tag, sub, n))
            i = need
        else:
            need = i + 3 + n
            if need > end:
                break
            groups.append((tag, sub, n))
            i = need
    return {"refs": refs, "groups": groups, "raw_len": i - raw_start}


def summarize(table: str, workcopy: Path = WORKCOPY) -> dict:
    """给 bindings builder 用的摘要（键空间 + 规模），避免其直接碰 payload 细节。"""
    entry = BA8A_ENTRIES.get(table)
    if entry is None:
        return {"status": "unknown_table", "table": table}
    got = parse(entry, workcopy)
    rows = got["rows"]
    keys = sorted(r["key"] for r in rows)
    ref_total = sum(len(r["refs"]) for r in rows)
    refs_per_row = sorted({len(r["refs"]) for r in rows})
    return {"status": got["status"], "table": table, "entry": entry, "rows": len(rows),
            "key_min": keys[0] if keys else None, "key_max": keys[-1] if keys else None,
            "refs_total": ref_total, "refs_per_row_set": refs_per_row[:12],
            "nodes": len(got["nodes"]), "snapshot": "test-documents-ba8a239a"}


def row_refs(blob: bytes, off: int, end: int) -> list[int]:
    """只取 **0x27 组** 的 u24 refs（排除行内嵌的 0x76 索引组）。

    1110162 的行体 = 0x27(n=3) + 0x76(n=11)：只有 0x27 的 3 个 ref 才属于 skin→sfx 映射；
    把 0x76 一起算进去会得到 14，正是此前"3 vs 14 异常"的来源。
    """
    refs: list[int] = []
    j = off
    while j + 3 <= end and blob[j] in (0x27, 0x36, 0x76):
        tag, _sub, n = blob[j], blob[j + 1], blob[j + 2]
        if tag == 0x27:
            if j + 3 + 3 * n > end:
                break
            refs += [int.from_bytes(blob[j + 3 + 3 * k:j + 6 + 3 * k], "little") for k in range(n)]
            j += 3 + 3 * n
        elif tag == 0x76:
            if j + 3 + 3 * n > end:
                break
            j += 3 + 3 * n
        else:
            j += 3 + n
    return refs


def ref_pairs(table: str, skin_sfx_keys: dict, workcopy: Path = WORKCOPY) -> dict:
    """skin → [(ref, sfx_row_key)]，按 0x27 组顺序与 sfx 行 key 升序对齐（逐元素）。"""
    entry = BA8A_ENTRIES.get(table)
    got = parse(entry, workcopy)
    if not got["rows"]:
        return {}
    pay = payload_bytes(entry, workcopy)
    blob, _c0 = split_frame(pay)
    offs = sorted(r["offset"] for r in got["rows"])
    out: dict = {}
    for r in got["rows"]:
        cand = [o for o in offs if o > r["offset"]]
        end = cand[0] if cand else len(blob)
        refs = row_refs(blob, r["offset"], end)
        keys = sorted(skin_sfx_keys.get(r["key"], []))
        out[r["key"]] = {"refs": refs, "keys": keys,
                         "pairs": list(zip(refs, keys)) if len(refs) == len(keys) else [],
                         "match": len(refs) == len(keys)}
    return out
