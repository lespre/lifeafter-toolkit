"""Reusable zero-execution decoder for LifeAfter BinDict base/CHS table pairs.

Handles both verified row encodings:
- D6/C6 rows: [marker][uleb schema_ref][uleb bitmap_ref][value stream]
- 96 rows:    [marker][uleb schema_ref][inline bitmap][value stream]
Row boundaries are detected by validating that a candidate offset starts a
recognized row header (marker + schema_ref in the table's known schema set),
never by bare magic-byte matching.  See bindict_rows for scalar decoding.
"""
from __future__ import annotations

import struct
from typing import Any

from toolkit_core.bindict_rows import SCALAR_BOOL, SCALAR_CHS, SCALAR_F32, SCALAR_F64, SCALAR_JUMP, SCALAR_ULEB, SCALAR_ULEB_ALT, SCALAR_ZIGZAG, uleb

ROW_MARKERS = (0x96, 0xD6, 0xC6)
MAPPING_MARKER = 0x36


def parse_chs_pool(body: bytes) -> list[str]:
    """Parse a CHS body: [count][reserved][ends...][utf-8 strings]."""
    count, reserved = struct.unpack_from("<II", body, 0)
    if reserved != 0:
        raise ValueError(f"CHS reserved != 0: {reserved}")
    table_end = 8 + 4 * count
    if table_end > len(body):
        raise ValueError("CHS ends table out of bounds")
    ends = struct.unpack_from(f"<{count}I", body, 8)
    if not all(a < b for a, b in zip(ends, ends[1:])):
        raise ValueError("CHS ends not strictly increasing")
    if ends[-1] != len(body) - table_end:
        raise ValueError("CHS ends not closing pool")
    pool = []
    last = 0
    for end in ends:
        pool.append(body[table_end + last:table_end + end].decode("utf-8"))
        last = end
    return pool


def parse_legacy_chs_pool(payload: bytes, scan_start: int = 0, scan_end: int | None = None) -> list[str]:
    """Parse a legacy single-byte ``{`` CHS pool (not ``x{``).

    Layout: ``7b`` + u32le(body_len) + body where body is the standard
    [count][reserved][ends...][strings].  The marker is located by scanning
    because legacy payloads often carry a 0x73 wrapper or other header bytes
    before the pool (verified on fashion_obtain_handbook_data_chs, entry 20870).
    """
    end = len(payload) if scan_end is None else min(scan_end, len(payload))
    for marker in range(scan_start, end - 5):
        if payload[marker] != 0x7B:
            continue
        body_len = struct.unpack_from("<I", payload, marker + 1)[0]
        body_start = marker + 5
        body_end = body_start + body_len
        if body_end > len(payload) or body_len < 8:
            continue
        count, reserved = struct.unpack_from("<II", payload, body_start)
        if reserved != 0 or not (1 <= count <= 200000):
            continue
        table_end = body_start + 8 + 4 * count
        if table_end > body_end:
            continue
        ends = struct.unpack_from(f"<{count}I", payload, body_start + 8)
        # Equal adjacent ends are valid: they encode an empty string slot.
        if not all(a <= b for a, b in zip(ends, ends[1:])):
            continue
        if ends[-1] != body_end - table_end:
            continue
        pool = []
        last = 0
        try:
            for end_off in ends:
                pool.append(payload[table_end + last:table_end + end_off].decode("utf-8"))
                last = end_off
        except UnicodeDecodeError:
            continue
        return pool
    raise ValueError("no valid legacy { CHS pool found")


def resolve_jump_group(blob: bytes, target: int) -> list[int] | None:
    """Resolve a 0x27 group at ``target``: [27][kind][count] + count x ULEB.

    Returns the ULEB element list, or None if the target is not a valid group.
    """
    if target < 0 or target + 3 > len(blob) or blob[target] != 0x27:
        return None
    kind = blob[target + 1]
    if kind in (0x01, 0x02, 0x05, 0x0B):
        count = blob[target + 2]
        pos = target + 3
        values = []
        for _ in range(count):
            try:
                value, pos = uleb(blob, pos, len(blob))
            except ValueError:
                return None
            values.append(value)
        return values
    # nibble forms: 0x1N = N x float32, 0x2N = N x double (nucleus_entry_data
    # value arrays use 0x12/0x22); plain 0x01/0x02/0x05/0x0B keep ULEB semantics.
    if 0x10 <= kind <= 0x2F and (kind >> 4) in (1, 2):
        count = kind & 0x0F
        fmt = "f" if (kind >> 4) == 1 else "d"
        fmt_rep = "<" + fmt * count
        width = 4 if fmt == "f" else 8
        pos = target + 3
        end = pos + count * width
        if not (1 <= count <= 15) or end > len(blob):
            return None
        try:
            return list(struct.unpack_from(fmt_rep, blob, pos))
        except struct.error:
            return None
    return None


def parse_index(blob: bytes) -> list[tuple[int, int]]:
    """Parse the 0x76 index tail. Returns [(key, value_start)] sorted by key.

    Node offset encoding is table-dependent: some tables store the bucket
    offset verbatim (weapon_skin_data), others store it ``<<8`` (box_data).
    Both styles are detected by range-checking against the blob.
    """
    de = struct.unpack_from("<I", blob, 0)[0]
    tail = blob[de:]
    if tail[:3] not in (b"\x76\x01\x0b", b"\x76\x0b\x0b", b"\x76\x05\x0b"):
        # fallback（2026-09-06 optional_hd_exchange_shop_data 002962 实例）：de 前缀缺失表
        # ——表头 count 非 de（如 002962 blob[0:4]=32 行数），0x76 索引尾挂在 blob 末尾。
        # 原路径必然 ValueError=只新增成功可能，零回归；取最靠尾的合法索引头。
        hit = None
        for marker in (b"\x76\x01\x0b", b"\x76\x0b\x0b", b"\x76\x05\x0b"):
            p = blob.rfind(marker)
            if p > 0 and (hit is None or p > hit[0]):
                hit = (p, marker)
        if hit:
            de = hit[0]
            tail = blob[de:]
        else:
            raise ValueError(f"not a supported 0x76 index tail: {tail[:4].hex()}")
    # bucket_count 编码自适应：u8（box_data）或 uleb（py3 common_item_data 等），
    # 用节点偏移范围检测选出正确的一种
    candidates = []
    bc_u8 = tail[3]
    if 4 + 8 * bc_u8 <= len(tail):
        candidates.append((bc_u8, 4))
    try:
        bc_uleb, p_uleb = uleb(tail, 3, len(tail))
        if p_uleb + 8 * bc_uleb <= len(tail):
            candidates.append((bc_uleb, p_uleb))
    except ValueError:
        pass
    chosen = None
    for bc, npos in candidates:
        raw_offs = [struct.unpack_from("<I", tail, npos + 8 * i + 4)[0] for i in range(bc)]
        direct_ok = all(de <= off < len(blob) for off in raw_offs)
        shift_ok = all(de <= (off >> 8) < len(blob) for off in raw_offs)
        if direct_ok or shift_ok:
            chosen = (bc, npos, raw_offs)
            break
    if chosen is None:
        raise ValueError("index bucket count unreadable or offsets out of range")
    bucket_count, node_pos, raw_offs = chosen
    if node_pos + 8 * bucket_count > len(tail):
        raise ValueError("index buckets out of bounds")
    direct_ok = all(de <= off < len(blob) for off in raw_offs)
    shifted = [off >> 8 for off in raw_offs]
    shift_ok = all(de <= off < len(blob) for off in shifted)
    if direct_ok and not shift_ok:
        offs = raw_offs
    elif shift_ok and not direct_ok:
        offs = shifted
    elif direct_ok and shift_ok:
        offs = raw_offs  # verbatim preferred when both valid
    else:
        raise ValueError(f"index node offsets out of range: direct={direct_ok} shift={shift_ok}")
    nodes = sorted(set(offs))
    rows: list[tuple[int, int]] = []
    for idx, node in enumerate(nodes):
        end = nodes[idx + 1] if idx + 1 < len(nodes) else len(blob)
        pos = node
        while pos < end:
            key, pos = uleb(blob, pos, end)
            value_start, pos = uleb(blob, pos, end)
            rows.append((key, value_start))
    rows.sort(key=lambda item: item[0])
    return rows


def _schema_at(blob: bytes, ref: int, pool: list[str]) -> tuple[int, list[tuple[int, int, str]], int]:
    pos = ref
    n, pos = uleb(blob, pos, len(blob))
    bits, pos = uleb(blob, pos, len(blob))
    if not (1 <= n <= 512 and 0 <= bits <= n):
        raise ValueError(f"schema bounds n={n} bits={bits} at {ref}")
    fields: list[tuple[int, int, str]] = []
    for _ in range(n):
        slot, pos = uleb(blob, pos, len(blob))
        if pos >= len(blob):
            raise ValueError("schema truncated")
        type_byte = blob[pos]
        pos += 1
        name = pool[slot] if slot < len(pool) else f"<slot_{slot}>"
        fields.append((slot, type_byte, name))
    return bits, fields, pos


def _decode_value(blob: bytes, pos: int, type_byte: int, pool: list[str]) -> tuple[Any, int]:
    if type_byte in (SCALAR_ULEB, SCALAR_ULEB_ALT):
        value, pos = uleb(blob, pos, len(blob))
        return value, pos
    if type_byte == SCALAR_BOOL:
        if pos >= len(blob):
            raise ValueError("truncated bool")
        return bool(blob[pos]), pos + 1
    if type_byte == SCALAR_CHS:
        slot, pos = uleb(blob, pos, len(blob))
        return pool[slot] if slot < len(pool) else f"<oob:{slot}>", pos
    if type_byte == SCALAR_JUMP:
        target, pos = uleb(blob, pos, len(blob))
        return f"jump:{target}", pos
    if type_byte == SCALAR_ZIGZAG:
        value, pos = uleb(blob, pos, len(blob))
        return (value >> 1) ^ -(value & 1), pos
    if type_byte == SCALAR_F32:
        if pos + 4 > len(blob):
            raise ValueError("truncated f32")
        return struct.unpack_from("<f", blob, pos)[0], pos + 4
    if type_byte == SCALAR_F64:
        if pos + 8 > len(blob):
            raise ValueError("truncated f64")
        return struct.unpack_from("<d", blob, pos)[0], pos + 8
    raise ValueError(f"unhandled scalar type 0x{type_byte:02x}")


def _collect_schemas(blob: bytes, index_rows: list[tuple[int, int]]) -> set[int]:
    schemas: set[int] = set()
    for _key, start in index_rows:
        if start >= len(blob) or blob[start] not in ROW_MARKERS:
            continue
        try:
            sr, _ = uleb(blob, start + 1, len(blob))
        except ValueError:
            continue
        schemas.add(sr)
    return schemas


def decode_table_rows(
    base_body: bytes,
    pool: list[str],
    index_rows: list[tuple[int, int]] | None = None,
    resolve_jumps: bool = False,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Decode every D6/C6/96 row of a base table.

    ``index_rows`` may be supplied for KJ1 tables after their bucket offset
    lists have been resolved to ``(key, row_start)`` pairs.  When omitted,
    the ordinary 0x76 index is parsed from the table blob.

    Returns (rows, unbound). Each row includes decoded scalar ``values`` and
    bounded inline ``0x27`` groups when present.
    """
    count, reserved = struct.unpack_from("<II", base_body, 0)
    if reserved != 0:
        raise ValueError("base reserved != 0")
    table_end = 8 + 4 * count
    blob = base_body[table_end:]
    if index_rows is None:
        index_rows = parse_index(blob)
    known_schemas = _collect_schemas(blob, index_rows)
    has_mapping_rows = any(
        0 <= s < len(blob) and blob[s] == MAPPING_MARKER for _key, s in index_rows
    )
    if not known_schemas and not has_mapping_rows:
        return [], [{"error": "no schemas discovered"}]

    def is_row_head(q: int) -> bool:
        if q >= len(blob):
            return False
        if blob[q] == MAPPING_MARKER:
            return True
        if blob[q] not in ROW_MARKERS:
            return False
        try:
            sr, _ = uleb(blob, q + 1, len(blob))
        except ValueError:
            return False
        return sr in known_schemas

    # 传入 KJ1 行起点时可精确使用下一行边界；普通表也受益，避免在值流
    # 中误判 marker。KJ1 的 de 是索引区起点，数据行必须在它之前。
    de = struct.unpack_from("<I", blob, 0)[0]
    valid_starts = sorted({
        start for _key, start in index_rows
        if 0 <= start < de and is_row_head(start)
    })
    row_end = {
        start: (valid_starts[i + 1] if i + 1 < len(valid_starts) else de)
        for i, start in enumerate(valid_starts)
    }

    rows: list[dict[str, Any]] = []
    unbound: list[dict[str, Any]] = []
    for key, start in index_rows:
        if start >= len(blob) or (blob[start] not in ROW_MARKERS and blob[start] != MAPPING_MARKER):
            unbound.append({"key": key, "start": start, "error": "bad marker"})
            continue
        marker = blob[start]
        if marker == MAPPING_MARKER:
            # 0x36 mapping row: [36][kt][vt][uleb pair_count][n x (key,value)]
            # (verified on common_exchange_shop_data entry 7767: kt=0x01, vt=0x0b)
            if start + 3 > len(blob):
                unbound.append({"key": key, "start": start, "marker": "0x36", "error": "short mapping header"})
                continue
            kt, vt = blob[start + 1], blob[start + 2]
            try:
                pair_count, q = uleb(blob, start + 3, len(blob))
            except ValueError:
                unbound.append({"key": key, "start": start, "marker": "0x36", "error": "bad pair count"})
                continue
            pairs: list[tuple[Any, Any]] = []
            truncated = False
            for _ in range(pair_count):
                try:
                    k_val, q = _decode_value(blob, q, kt, pool)
                    v_val, q = _decode_value(blob, q, vt, pool)
                except ValueError:
                    truncated = True
                    break
                pairs.append((k_val, v_val))
            if truncated:
                unbound.append({"key": key, "start": start, "marker": "0x36",
                                "error": "mapping truncated", "pairs_so_far": len(pairs)})
                continue
            rows.append({"key": key, "start": start, "marker": "0x36",
                         "kt": f"0x{kt:02x}", "vt": f"0x{vt:02x}",
                         "values": {}, "inline_groups": [], "tail": "", "pairs": pairs})
            continue
        pos = start + 1
        schema_ref, pos = uleb(blob, pos, len(blob))
        try:
            bits, fields, _ = _schema_at(blob, schema_ref, pool)
        except ValueError as exc:
            unbound.append({"key": key, "start": start, "marker": hex(marker), "schema": schema_ref, "error": f"schema: {exc}"})
            continue
        if marker == 0x96:
            bitmap_size = (bits + 7) // 8
            bitmap = blob[pos:pos + bitmap_size]
            pos += bitmap_size
        else:
            bitmap_ref, pos = uleb(blob, pos, len(blob))
            bitmap_size = (bits + 7) // 8
            if bitmap_ref + bitmap_size > len(blob):
                unbound.append({"key": key, "start": start, "marker": hex(marker), "schema": schema_ref, "error": "bitmap oob"})
                continue
            bitmap = blob[bitmap_ref:bitmap_ref + bitmap_size]
        nxt = row_end.get(start)
        if nxt is None or nxt <= pos:
            unbound.append({"key": key, "start": start, "marker": hex(marker), "schema": schema_ref, "error": "no row boundary"})
            continue
        # 值流解码
        enabled = [i for i, (_s, t, _n) in enumerate(fields) if i >= bits or (bitmap[i // 8] >> (i % 8)) & 1]
        values: dict[str, Any] = {}
        q = pos
        overrun = False
        for ix in enabled:
            type_byte, name = fields[ix][1], fields[ix][2]
            try:
                value, q = _decode_value(blob, q, type_byte, pool)
            except ValueError:
                overrun = True
                break
            if q > nxt:
                overrun = True
                break
            values[name] = (f"0x{type_byte:02x}", value)
        if overrun:
            unbound.append({"key": key, "start": start, "marker": hex(marker), "schema": schema_ref,
                            "error": "overrun", "consumed": q, "nxt": nxt})
            continue
        if q < nxt and blob[q:q + 1] not in (b"\x27", b"\x36"):
            unbound.append({"key": key, "start": start, "marker": hex(marker), "schema": schema_ref,
                            "error": "inline list variant", "gap": blob[q:nxt][:16].hex(), "gap_len": nxt - q})
            continue
        # 0x27 同构序列：27 + element_type + uleb(count) + count×元素。
        # reward_pool 的 kind=1 且 count=2 即 (item_id, quantity)。
        inline_groups = []
        group_error = None
        while q < nxt and blob[q:q + 1] == b"\x27":
            try:
                kind = blob[q + 1]
                elem_count, q = uleb(blob, q + 2, nxt)
                elements = []
                for _ in range(elem_count):
                    value, q = uleb(blob, q, nxt)
                    elements.append(value)
                inline_groups.append({"kind": hex(kind), "count": elem_count, "elements": elements})
            except (IndexError, ValueError):
                group_error = "truncated 0x27 group"
                break
        if group_error:
            unbound.append({"key": key, "start": start, "marker": hex(marker), "schema": schema_ref,
                            "error": group_error})
            continue
        # 行尾 0x36 映射（36 + key类型 + value类型 + uleb对数 + pairs）——先保留 framing。
        tail_note = ""
        if q < nxt and blob[q:q + 1] == b"\x36":
            try:
                kt, vt = blob[q + 1], blob[q + 2]
                pc, _p2 = uleb(blob, q + 3, nxt)
                tail_note = f"0x36map(k:{kt:#x},v:{vt:#x},n:{pc})"
            except ValueError:
                tail_note = "0x36map(truncated)"
        rows.append({"key": key, "start": start, "marker": hex(marker), "schema": schema_ref,
                     "bitmap": bitmap.hex(), "values": values, "inline_groups": inline_groups,
                     "tail": tail_note})
    if resolve_jumps:
        # 0x27 组有两种引用方式：a) 组的字节落在本行区间内（byte-range 扫描，
        #    对 reward_pool_data_base 成立）；b) 行内 jump 字段指过去（pointer 链，
        #    对 random_item_reward_data_923 成立——byte-range 扫描会拿到邻行的组）。
        # 有 jump 字段时以 pointer 链为准，并把 byte-range 结果标为不可信。
        resolve_row_jumps(blob, rows)
    return rows, unbound


def decode_86_row(blob: bytes, pos: int) -> dict[str, Any]:
    """Decode one 0x86 detail row (D6-style: [86][schema_ref][bitmap_ref][bitmap][values]).

    Verified on optional_hd_exchange_shop_data entry 2949, where 0x36 mapping
    rows' vt=0x0b pairs jump to these rows. Schema @70: n=33 bits=23.
    Returns dict with marker/schema/bitmap_ref/bitmap/value_end/values/fields.
    """
    if pos >= len(blob) or blob[pos] != 0x86:
        raise ValueError(f"not a 0x86 row at {pos}: 0x{blob[pos]:02x}")
    schema_ref, q = uleb(blob, pos + 1, len(blob))
    bitmap_ref, q = uleb(blob, q, len(blob))
    bits, fields, _schema_end = _schema_at(blob, schema_ref, [])
    bitmap_size = (bits + 7) // 8
    bitmap = blob[bitmap_ref:bitmap_ref + bitmap_size]
    values: dict[int, Any] = {}
    for i, (_slot, type_byte, _name) in enumerate(fields):
        enabled = i >= bits or bool(bitmap[i // 8] & (1 << (i % 8)))
        if not enabled:
            continue
        value, q = _decode_value(blob, q, type_byte, [])
        values[i] = value
    return {
        "start": pos,
        "marker": "0x86",
        "schema": schema_ref,
        "bitmap_ref": bitmap_ref,
        "bitmap": bitmap.hex(),
        "value_end": q,
        "values": values,
        "fields": [(slot, hex(t)) for slot, t, _n in fields],
    }


def _read_27_uleb_group(blob: bytes, start: int) -> dict[str, Any] | None:
    """Read a bounded ULEB ``0x27`` group without assigning business meaning.

    ``optional_hd_exchange_shop_data`` stores its small item/cost lists in a
    shared group area.  Depending on the reference form, a field can point at
    the group marker, its count byte, or just before the marker; callers must
    therefore resolve framing first and only label a group in a later,
    separately-calibrated business layer.
    """
    if start < 0 or start + 3 > len(blob) or blob[start] != 0x27:
        return None
    kind = blob[start + 1]
    # kind nibble forms: 0x1N = N x float32, 0x2N = N x double (nucleus_entry_data
    # value arrays use 0x12/0x22); plain 0x01/0x02/0x05/0x0B keep ULEB semantics.
    if kind in (0x01, 0x02, 0x05, 0x0B):
        try:
            count, pos = uleb(blob, start + 2, len(blob))
        except ValueError:
            return None
        if not (1 <= count <= 64):
            return None
        values: list[int] = []
        try:
            for _ in range(count):
                value, pos = uleb(blob, pos, len(blob))
                values.append(value)
        except ValueError:
            return None
        return {"start": start, "end": pos, "kind": kind, "values": values}
    if 0x10 <= kind <= 0x2F and (kind >> 4) in (1, 2):
        count = kind & 0x0F
        fmt = "f" if (kind >> 4) == 1 else "d"
        fmt_rep = "<" + fmt * count
        width = 4 if fmt == "f" else 8
        if not (1 <= count <= 15):
            return None
        pos = start + 3
        end = pos + count * width
        if end > len(blob):
            return None
        try:
            values = list(struct.unpack_from(fmt_rep, blob, pos))
        except struct.error:
            return None
        return {"start": start, "end": end, "kind": kind, "values": values,
                "nibble": True}
    return None


def _resolve_27_group_reference(blob: bytes, reference: int) -> dict[str, Any] | None:
    """Resolve one optional-shop reference to a unique nearby ``0x27`` group.

    Precedence is deliberate and deterministic:
    1. an exact group-start reference;
    2. a reference inside a framed group (the ``0x0b`` form may target count
       or first-element bytes);
    3. a reference up to two bytes before a group marker.

    If a tier has multiple candidates, refuse to guess.  This helper returns
    framing facts only; it never calls a group an item, price, or purchase
    limit.
    """
    if not (0 <= reference < len(blob)):
        return None
    candidates: list[dict[str, Any]] = []
    for start in range(max(0, reference - 8), min(len(blob) - 2, reference + 9)):
        group = _read_27_uleb_group(blob, start)
        if group is not None:
            candidates.append(group)
    if not candidates:
        return None

    exact = [g for g in candidates if g["start"] == reference]
    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        return None

    inside = [g for g in candidates if g["start"] < reference < g["end"]]
    if len(inside) == 1:
        return inside[0]
    if len(inside) > 1:
        return None

    ahead = [g for g in candidates if 0 < g["start"] - reference <= 2]
    if len(ahead) == 1:
        return ahead[0]
    return None


def decode_optional_hd_exchange_records(base_body: bytes) -> list[dict[str, Any]]:
    """Decode raw, non-semantic references of ``optional_hd_exchange_shop``.

    Each returned record retains its full identity:
    ``mapping_row + pair_index + key + detail_start``.  The numeric mapping
    key alone is *not* unique: it is intentionally repeated across the two
    0x36 maps.  ``resolved_groups`` contains only framed 0x27 lists proved to
    be referenced by the corresponding 0x86 record; no group is labelled as
    item/cost/limit here.
    """
    mappings, unbound = decode_table_rows(base_body, [])
    if unbound:
        raise ValueError(f"optional exchange mapping decode failed: {unbound[:3]}")
    count, reserved = struct.unpack_from("<II", base_body, 0)
    if reserved != 0:
        raise ValueError("optional exchange base reserved != 0")
    table_end = 8 + 4 * count
    if table_end > len(base_body):
        raise ValueError("optional exchange table header out of bounds")
    blob = base_body[table_end:]

    records: list[dict[str, Any]] = []
    for mapping_row, mapping in enumerate(mappings):
        if mapping.get("marker") != "0x36":
            raise ValueError(f"expected 0x36 mapping row, got {mapping.get('marker')}")
        for pair_index, (key, value) in enumerate(mapping.get("pairs", [])):
            if not isinstance(value, str) or not value.startswith("jump:"):
                raise ValueError(f"mapping row {mapping_row} pair {pair_index} has non-jump value")
            detail_start = int(value[5:])
            detail = decode_86_row(blob, detail_start)
            resolved_groups: list[dict[str, Any]] = []
            seen: set[tuple[int, int, int]] = set()
            for field_index, field_value in detail["values"].items():
                if isinstance(field_value, str) and field_value.startswith("jump:"):
                    source, reference = "jump", int(field_value[5:])
                elif isinstance(field_value, int):
                    source, reference = "scalar", field_value
                else:
                    continue
                group = _resolve_27_group_reference(blob, reference)
                if group is None:
                    continue
                signature = (field_index, reference, group["start"])
                if signature in seen:
                    continue
                seen.add(signature)
                resolved_groups.append({
                    "field_index": field_index,
                    "slot": detail["fields"][field_index][0],
                    "source": source,
                    "reference": reference,
                    **group,
                })
            records.append({
                "mapping_row": mapping_row,
                "pair_index": pair_index,
                "key": key,
                "detail_start": detail_start,
                "bitmap": detail["bitmap"],
                "resolved_groups": resolved_groups,
            })
    return records


def decode_kj1_table(body: bytes, pool: list[str] | None = None):
    """Decode KJ1-type tables (76 0b 0b index + row offset tables + 07/96 52 rows).

    Structure (verified on common_lottery_conf_data):
      blob = [de u32][data zone][index tail]
      index = 76 0b 0b + uleb bucket_count + 8B nodes (key u32, off u32 verbatim)
      node off -> row offset table (consecutive ULEB pointing to row starts)
      rows: 07-type (6 ULEB) or 96 52-type (uleb 0x96,0x52=10518 + ULEBs + f64 zone)
      + 0x27 groups
    Returns (rows, unbound); each row has key/type/ulebs/groups.
    """
    if len(body) < 12:
        return [], [{"error": "short body"}]
    cnt, _ = struct.unpack_from("<II", body, 0)
    te = 8 + 4 * cnt
    if te > len(body):
        return [], [{"error": "bad count"}]
    blob = body[te:]
    if len(blob) < 8:
        return [], [{"error": "short blob"}]
    de = struct.unpack_from("<I", blob, 0)[0]
    if de < 4 or de >= len(blob) or blob[de:de + 3] != b"\x76\x0b\x0b":
        return [], [{"error": f"not KJ1 index at de={de}"}]
    tail = blob[de:]
    try:
        n, p = uleb(tail, 3, len(tail))
        nodes = [struct.unpack_from("<II", tail, p + i * 8) for i in range(n)]
    except (ValueError, struct.error):
        return [], [{"error": "bad index"}]

    def read_until_group(t):
        vals, q = [], t
        for _ in range(30):
            if q >= len(blob) or blob[q] == 0x27:
                break
            try:
                v, q = uleb(blob, q, len(blob))
            except ValueError:
                break
            vals.append(v)
        groups = []
        while q < len(blob) and blob[q] == 0x27:
            kind, count = blob[q + 1], blob[q + 2]
            q += 3
            elems = []
            for _ in range(count):
                try:
                    v, q = uleb(blob, q, len(blob))
                except ValueError:
                    break
                elems.append(v)
            groups.append({"kind": hex(kind), "count": count, "elements": elems})
        return vals, groups

    # 每个 node 的 offset 指向独立的 ULEB 行偏移桶。旧实现固定读取 200
    # 个值，会越过当前桶进入相邻桶，导致同一批数据被重复解释为海量伪行。
    # 以相邻 bucket offset 为严格边界；最后一个桶止于 blob 末尾。
    valid_offsets = sorted({o for _k, o in nodes if de <= o < len(blob)})
    bucket_end = {
        o: (valid_offsets[i + 1] if i + 1 < len(valid_offsets) else len(blob))
        for i, o in enumerate(valid_offsets)
    }

    rows, unbound = [], []
    for k, o in nodes:
        if not (de <= o < len(blob)):
            unbound.append({"key": k, "error": "node off out of range"})
            continue
        q, end = o, bucket_end[o]
        targets = []
        while q < end:
            try:
                v, q = uleb(blob, q, end)
            except ValueError:
                break
            targets.append(v)
        for t in targets:
            if not (4 <= t < de):
                continue
            vals, groups = read_until_group(t)
            if not vals:
                continue
            row = {"key": k, "start": t, "ulebs": vals, "groups": groups}
            if vals[0] == 7:
                row["type"] = "07"
                if pool and len(vals) > 3 and vals[3] < len(pool):
                    row["lottery_type"] = pool[vals[3]]
            elif vals[0] == 10518:
                row["type"] = "96_52"
            else:
                row["type"] = "other"
            rows.append(row)
    rows.sort(key=lambda r: r["key"])
    return rows, unbound


# ---------------------------------------------------------------------------
# 0x27 pointer-chain resolution（2026-09-11 加入）
#
# 背景：早期实现只用 "行字节区间内的 0x27 组" 当作该行的组。对大多数表可用，
# 但对 random_item_reward_data_<n>（礼包/盒子表）会**整体错一行**：第 K 行区间
# 里扫到的组其实属于第 K+1 行的数据，导致"名称 ↔ 内容"错配。
# 正解：行内 `items` 字段是 SCALAR_JUMP，指向该行自己的组；该组是 pointer 形式
# （kind 0x0b，元素是其它组的偏移），沿链走到底得到叶子组（kind 0x01），
# 叶子元素按 (id, 数量) 交替配对。
# 自证：random_item_reward_data_923 上 17/17 行名称↔内容自洽
#（刑天铠甲→636920130、极光盾交易盒→1110197、火树银花时装→637250110/130、
#  赤月终焉臻藏盒→460620/461620、福鼠迎春臻藏盒→166998/166999 等）。
# ---------------------------------------------------------------------------

MAX_CHAIN_DEPTH = 6


def read_27_group(blob: bytes, pos: int) -> tuple[int, list[int]] | None:
    """Read one framed 0x27 group as (kind, elements) without business meaning."""
    if pos < 0 or pos + 3 > len(blob) or blob[pos] != 0x27:
        return None
    kind = blob[pos + 1]
    try:
        count, q = uleb(blob, pos + 2, len(blob))
    except ValueError:
        return None
    elements: list[int] = []
    for _ in range(count):
        try:
            value, q = uleb(blob, q, len(blob))
        except ValueError:
            return None
        elements.append(value)
    return kind, elements


def resolve_27_chain(blob: bytes, target: int, max_depth: int = MAX_CHAIN_DEPTH) -> dict[str, Any]:
    """Follow a 0x27 pointer chain from ``target``.

    kind 0x0b = pointer group (elements are offsets of further groups);
    kind 0x01 = leaf group (elements alternate id / quantity).

    Returns ``{"pairs": [(id, qty), ...], "leaves": [[...]], "chain": [...],
    "error": None|str}``.  Pairs are only produced from leaf groups, so a
    truncated or cyclic chain yields partial data plus an ``error`` string
    instead of a silent guess.
    """
    pairs: list[tuple[int, int]] = []
    leaves: list[list[int]] = []
    chain: list[str] = []
    seen: set[int] = set()
    error: str | None = None

    def walk(pos: int, depth: int) -> None:
        nonlocal error
        if error is not None:
            return
        if depth > max_depth:
            error = f"chain deeper than {max_depth}"
            return
        if pos in seen:
            error = f"cycle at {pos}"
            return
        seen.add(pos)
        group = read_27_group(blob, pos)
        if group is None:
            error = f"no 0x27 group at {pos}"
            return
        kind, elements = group
        chain.append(f"{pos}:kind{kind:#x}:n{len(elements)}")
        if kind == 0x0B:
            for offset in elements:
                walk(offset, depth + 1)
            return
        if kind == 0x01:
            leaves.append(elements)
            for i in range(0, len(elements) - 1, 2):
                pairs.append((elements[i], elements[i + 1]))
            return
        error = f"unsupported group kind {kind:#x} at {pos}"

    if target < 0 or target >= len(blob):
        return {"pairs": [], "leaves": [], "chain": [], "error": "target out of bounds"}
    walk(target, 0)
    return {"pairs": pairs, "leaves": leaves, "chain": chain, "error": error}


def resolve_row_jumps(blob: bytes, rows: list[dict[str, Any]],
                      fields: tuple[str, ...] | None = None) -> list[dict[str, Any]]:
    """Attach ``resolved`` (per jump field) and demote byte-range groups.

    For every row, each SCALAR_JUMP value is resolved through
    :func:`resolve_27_chain`.  When at least one jump field resolved to a leaf
    group, ``inline_groups`` is kept for audit but flagged via
    ``inline_groups_trusted = False`` because the byte-range scan is known to
    pick up a neighbouring row's groups in that layout.
    """
    for row in rows:
        resolved: dict[str, Any] = {}
        values = row.get("values") or {}
        for name, payload in values.items():
            if fields is not None and name not in fields:
                continue
            if not (isinstance(payload, tuple) and len(payload) == 2):
                continue
            type_byte, value = payload
            if not (isinstance(value, str) and value.startswith("jump:")):
                continue
            target = int(value[5:])
            result = resolve_27_chain(blob, target)
            resolved[name] = {"jump": target, **result}
        row["resolved"] = resolved
        if resolved:
            # 逐表经验（2026-09-11 实测）：
            #  - random_item_reward_data_*：内容 = jump 链（resolved），区间扫描会拿到邻行 → 不可信
            #  - reward_pool_data_base：成员[池id,槽位] = 区间扫描（已与游戏 UI 互相验证）→ 可信
            row["inline_groups_note"] = (
                "byte-range scan; prefer `resolved` for random_item_reward_data_*; "
                "this IS the verified membership source for reward_pool_data_base"
            )
    return rows


def selftest_jump_chains(body: bytes, pool: list[str],
                         expect: dict[int, list[int]] | None = None) -> dict[str, Any]:
    """Self-check pointer-chain resolution against known name→content facts.

    ``expect`` maps row key to the expected first item id of the resolved
    ``items`` field.  Defaults to the random_item_reward_data_923 facts that
    were verified by hand on 2026-09-11 (fashion id blocks cross-checked in
    fashion_data).  Returns ``{"pass": bool, "checks": [...]}`` and must be
    run before trusting this table's name↔content pairing in any report.
    """
    default_expect = {
        923473: 636910130,   # 帝皇铠甲交易盒 → 帝皇铠甲
        923475: 1110177,     # 极光剑交易盒 → 极光剑
        923476: 1110197,     # 极光盾交易盒 → 极光盾
        923485: 636920130,   # 刑天铠甲 → 刑天铠甲
        923486: 636930130,   # 飞影铠甲 → 飞影铠甲
        923488: 637250110,   # 火树银花时装 → 火树银花
        923489: 460620,      # 赤月终焉臻藏盒 → 赤月终焉典藏
        923490: 166998,      # 福鼠迎春臻藏盒 → 福鼠迎春典藏
    }
    table = dict(default_expect)
    if expect:
        table.update(expect)
    rows, _unbound = decode_table_rows(body, pool, resolve_jumps=True)
    by_key = {row["key"]: row for row in rows}
    checks: list[dict[str, Any]] = []
    for key, expected_first in sorted(table.items()):
        row = by_key.get(key)
        if row is None:
            checks.append({"key": key, "pass": False, "reason": "row missing"})
            continue
        entry = (row.get("resolved") or {}).get("items") or {}
        pairs = entry.get("pairs") or []
        first = pairs[0][0] if pairs else None
        checks.append({
            "key": key,
            "pass": first == expected_first,
            "expected_first": expected_first,
            "got_first": first,
            "pairs": pairs,
            "error": entry.get("error"),
        })
    return {"pass": all(c["pass"] for c in checks), "checks": checks, "rows": len(rows)}
