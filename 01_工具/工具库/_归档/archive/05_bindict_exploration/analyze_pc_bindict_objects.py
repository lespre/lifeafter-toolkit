"""Read-only static probe for LifeAfter PC BinDict references.

This script decrypts/decompresses only the enclosing NPK members and parses
length-bounded byte structures. It never imports, unmarshals, compiles, evals,
or executes a game payload. All derived files stay under OUT.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json
import math
import struct
import zlib

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

PKG = Path(r"E:/mrzh/Documents/script.py314.lc.npk")
OUT = Path(r"E:/mrzh_audit/run_004_PC_BinDict与1DPW专项_001/02_bindict")
KEY = bytes([
    0x60, 0x63, 0x08, 0xD8, 0xA3, 0x2C, 0x78, 0x20,
    0x13, 0xD2, 0x6C, 0x2F, 0x22, 0x6F, 0x68, 0x6D,
])
BASE_ID = int("1F8E9684E1B97CE0", 16)
CHS_ID = int("94AB0B3FD057EF01", 16)
TARGET_KEYS = (10547, 10548, 10549, 10760, 11005, 11010)
KNOWN_TYPES = {1, 3, 5, 11, 17, 18, 34}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while block := fh.read(1 << 20):
            h.update(block)
    return h.hexdigest()


def aes_ecb_prefix(data: bytes) -> bytes:
    n = len(data) // 16 * 16
    if not n:
        return data
    dec = Cipher(algorithms.AES(KEY), modes.ECB()).decryptor()
    return dec.update(data[:n]) + dec.finalize() + data[n:]


def uleb(data: bytes, pos: int, end: int) -> tuple[int, int, bytes]:
    start = pos
    value = 0
    shift = 0
    for _ in range(10):
        if pos >= end:
            raise ValueError(f"truncated ULEB at {start}")
        byte = data[pos]
        pos += 1
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value, pos, data[start:pos]
        shift += 7
    raise ValueError(f"overlong ULEB at {start}")


def hexdump(data: bytes, start: int, length: int = 96) -> dict:
    lo = max(0, start)
    hi = min(len(data), lo + length)
    rows = []
    for p in range(lo, hi, 16):
        chunk = data[p:min(p + 16, hi)]
        rows.append({
            "offset": p,
            "hex": chunk.hex(" "),
            "ascii": "".join(chr(x) if 32 <= x <= 126 else "." for x in chunk),
        })
    return {"start": lo, "end": hi, "rows": rows}


def unpack_members() -> tuple[dict, dict[int, dict]]:
    source_size = PKG.stat().st_size
    with PKG.open("rb") as fh:
        header = aes_ecb_prefix(fh.read(32))
        if len(header) != 32:
            raise ValueError("short NPK header")
        unknown_q, magic, version, table_offset, entry_count = struct.unpack_from("<QIIII", header)
        if magic != 0x4B50584E:
            raise ValueError(f"bad NPK magic {magic:#x}")
        if table_offset + entry_count * 48 > source_size:
            raise ValueError("NPK table out of source bounds")
        fh.seek(table_offset)
        table = aes_ecb_prefix(fh.read(entry_count * 48))
        members: dict[int, dict] = {}
        for index in range(entry_count):
            record = table[index * 48:(index + 1) * 48]
            file_id, offset, packed_size, declared_size, u4, u5, flag = struct.unpack_from("<QIIIIIi", record)
            if file_id not in (BASE_ID, CHS_ID):
                continue
            if not (0 <= offset <= source_size and offset + packed_size <= source_size):
                raise ValueError(f"member {file_id:016X} out of source bounds")
            if flag != 0:
                raise ValueError(f"unexpected compression flag {flag} for {file_id:016X}")
            fh.seek(offset)
            packed = fh.read(packed_size)
            decrypted = aes_ecb_prefix(packed)
            raw = None
            style = None
            codec_eof = None
            for wbits, name in ((15, "zlib"), (-15, "raw_deflate")):
                try:
                    dobj = zlib.decompressobj(wbits)
                    candidate = dobj.decompress(decrypted[18:]) + dobj.flush()
                    if dobj.eof:
                        raw = candidate
                        style = name
                        codec_eof = True
                        break
                except zlib.error:
                    pass
            if raw is None:
                raise ValueError(f"static decompression failed for {file_id:016X}")
            if len(raw) < 0x1A:
                raise ValueError("short decoded member")
            root_code_len = struct.unpack_from("<I", raw, 0x16)[0]
            q = 0x1A + root_code_len + 7
            if q + 6 > len(raw) or raw[q:q + 2] != b"x{":
                raise ValueError(f"missing x{{ frame for {file_id:016X}")
            body_len = struct.unpack_from("<I", raw, q + 2)[0]
            body_start = q + 6
            body_end = body_start + body_len
            if body_end > len(raw):
                raise ValueError("BinDict frame out of decoded-member bounds")
            body = raw[body_start:body_end]
            members[file_id] = {
                "entry_index": index,
                "entry_offset": offset,
                "packed_size": packed_size,
                "declared_size": declared_size,
                "neutral_u4": u4,
                "neutral_u5": u5,
                "flag": flag,
                "packed_sha256": hashlib.sha256(packed).hexdigest(),
                "decoded_member_size": len(raw),
                "decoded_member_sha256": hashlib.sha256(raw).hexdigest(),
                "unpack_style": style,
                "codec_eof": codec_eof,
                "root_code_len": root_code_len,
                "frame_offset": q,
                "body_offset_in_member": body_start,
                "body_size": len(body),
                "body_sha256": hashlib.sha256(body).hexdigest(),
                "body": body,
            }
    if set(members) != {BASE_ID, CHS_ID}:
        raise ValueError(f"missing target members: found {[f'{x:016X}' for x in members]}")
    package = {
        "path": PKG.as_posix(),
        "size": source_size,
        "sha256": sha256_file(PKG),
        "header_unknown_q": unknown_q,
        "magic": f"0x{magic:08x}",
        "version": version,
        "table_offset": table_offset,
        "entry_count": entry_count,
    }
    return package, members


def parse_chs(body: bytes) -> tuple[list[str], dict]:
    if len(body) < 12:
        raise ValueError("short CHS body")
    count = struct.unpack_from("<I", body, 0)[0]
    candidates = []
    for header_size in (4, 8, 12, 16, 20):
        table_end = header_size + 4 * count
        if table_end > len(body):
            continue
        reserved = body[4:header_size]
        if any(reserved):
            continue
        ends = struct.unpack_from(f"<{count}I", body, header_size) if count else ()
        raw_size = len(body) - table_end
        if count == 0:
            valid = raw_size == 0
        else:
            valid = all(a <= b for a, b in zip(ends, ends[1:])) and ends[-1] == raw_size
        if valid:
            candidates.append((header_size, ends, reserved))
    if len(candidates) != 1:
        raise ValueError(f"CHS framing candidates={[(x[0], len(x[1])) for x in candidates]}")
    header_size, ends, reserved = candidates[0]
    raw = body[header_size + 4 * count:]
    strings = []
    previous = 0
    for end in ends:
        strings.append(raw[previous:end].decode("utf-8", "strict"))
        previous = end
    return strings, {
        "slot_count": count,
        "header_size": header_size,
        "reserved_hex": reserved.hex(),
        "ends_table_offset": header_size,
        "utf8_bytes_offset": header_size + 4 * count,
        "utf8_bytes_size": len(raw),
        "last_end": ends[-1] if ends else None,
    }


def parse_base_blob(body: bytes) -> tuple[bytes, int, dict[int, int], dict]:
    if len(body) < 12:
        raise ValueError("short base body")
    slot_count, reserved = struct.unpack_from("<II", body, 0)
    table_end = 8 + 4 * slot_count
    if reserved != 0 or table_end > len(body):
        raise ValueError("invalid base header")
    if any(body[8:table_end]):
        raise ValueError("base slot region not zero-filled")
    blob = body[table_end:]
    if len(blob) < 8:
        raise ValueError("short base blob")
    data_end = struct.unpack_from("<I", blob, 0)[0]
    if not (4 <= data_end < len(blob)):
        raise ValueError("invalid index start")
    tail = blob[data_end:]
    if len(tail) < 4 or tail[:3] != b"\x76\x01\x0b":
        raise ValueError(f"unexpected index root {tail[:4].hex()}")
    bucket_count = tail[3]
    pairs_end = 4 + 8 * bucket_count
    if pairs_end > len(tail):
        raise ValueError("truncated bucket pairs")
    bucket_pairs = []
    node_starts = set()
    for i in range(bucket_count):
        hash_u, encoded = struct.unpack_from("<II", tail, 4 + 8 * i)
        node_offset = encoded >> 8
        low_meta = encoded & 0xFF
        bucket_pairs.append((hash_u, encoded, node_offset, low_meta))
        node_starts.add(node_offset)
    node_starts = sorted(node_starts)
    if any(not (data_end <= x < len(blob)) for x in node_starts):
        raise ValueError("bucket node offset out of blob bounds")
    rows = []
    for i, start in enumerate(node_starts):
        end = node_starts[i + 1] if i + 1 < len(node_starts) else len(blob)
        pos = start
        while pos < end:
            key, pos, key_raw = uleb(blob, pos, end)
            value_start, pos, ptr_raw = uleb(blob, pos, end)
            rows.append({
                "key_u": key,
                "value_start": value_start,
                "key_uleb_hex": key_raw.hex(),
                "value_start_uleb_hex": ptr_raw.hex(),
                "node_start": start,
            })
        if pos != end:
            raise ValueError("node did not close exactly")
    key_to_start = {x["key_u"]: x["value_start"] for x in rows}
    if len(key_to_start) != len(rows):
        raise ValueError("duplicate index keys")
    if any(not (4 <= x < data_end) for x in key_to_start.values()):
        raise ValueError("indexed value start out of data region")
    if len(set(key_to_start.values())) != len(key_to_start):
        raise ValueError("duplicate indexed value starts")
    return blob, data_end, key_to_start, {
        "slot_count": slot_count,
        "reserved_u32": reserved,
        "header_size": table_end,
        "blob_size": len(blob),
        "blob_sha256": hashlib.sha256(blob).hexdigest(),
        "data_region_start": 4,
        "data_region_end": data_end,
        "index_size": len(blob) - data_end,
        "index_root_hex": tail[:4].hex(),
        "bucket_count": bucket_count,
        "unique_node_count": len(node_starts),
        "indexed_row_count": len(rows),
    }


def parse_schema(blob: bytes, ref: int, slots: list[str]) -> tuple[list[dict], int, int]:
    if not (4 <= ref < len(blob)):
        raise ValueError(f"schema ref out of bounds: {ref}")
    pos = ref
    count, pos, count_raw = uleb(blob, pos, len(blob))
    bitmap_bits, pos, bits_raw = uleb(blob, pos, len(blob))
    if not (1 <= count <= 1024 and 0 <= bitmap_bits <= count):
        raise ValueError("schema count/bitmap bounds")
    fields = []
    for index in range(count):
        slot, pos, slot_raw = uleb(blob, pos, len(blob))
        if pos >= len(blob) or not (0 <= slot < len(slots)):
            raise ValueError("schema slot/type bounds")
        type_byte = blob[pos]
        pos += 1
        if type_byte not in KNOWN_TYPES:
            raise ValueError(f"unknown schema type {type_byte:#x}")
        name = slots[slot]
        if not name or not all(ch.isalnum() or ch == "_" for ch in name):
            raise ValueError(f"schema slot {slot} is not identifier-like: {name!r}")
        fields.append({
            "field_index": index,
            "field_slot": slot,
            "field_name": name,
            "type_byte": type_byte,
            "slot_uleb_hex": slot_raw.hex(),
        })
    return fields, bitmap_bits, pos


def selected_fields(schema: list[dict], bitmap_bits: int, bitmap: bytes) -> list[dict]:
    selected = []
    for index, field in enumerate(schema):
        enabled = index >= bitmap_bits or bool(bitmap[index // 8] & (1 << (index % 8)))
        if enabled:
            selected.append(field)
    return selected


def decode_scalar(blob: bytes, pos: int, end: int, field: dict, slots: list[str]) -> tuple[object, int, str, dict]:
    start = pos
    type_byte = field["type_byte"]
    meta = {"value_operand_start": start}
    if type_byte == 1:
        value, pos, raw = uleb(blob, pos, end)
        kind = "uleb_unsigned_candidate"
        meta["operand_uleb_hex"] = raw.hex()
    elif type_byte == 3:
        if pos >= end:
            raise ValueError("truncated bool byte")
        raw = blob[pos:pos + 1]
        value = bool(blob[pos])
        pos += 1
        kind = "nonzero_bool_candidate"
        meta["raw_hex"] = raw.hex()
    elif type_byte == 5:
        value, pos, raw = uleb(blob, pos, end)
        if not (0 <= value < len(slots)):
            raise ValueError("CHS string ref out of bounds")
        value = {"slot": value, "text": slots[value]}
        kind = "CHS_string_ref"
        meta["operand_uleb_hex"] = raw.hex()
    elif type_byte == 11:
        value, pos, raw = uleb(blob, pos, end)
        value = {"operand_u": value}
        kind = "unresolved_ref_operand"
        meta["operand_uleb_hex"] = raw.hex()
    elif type_byte == 17:
        unsigned, pos, raw = uleb(blob, pos, end)
        value = (unsigned >> 1) ^ (-(unsigned & 1))
        kind = "zigzag_int_candidate"
        meta["operand_uleb_hex"] = raw.hex()
    elif type_byte == 18:
        if pos + 4 > end:
            raise ValueError("truncated f32")
        raw = blob[pos:pos + 4]
        value = struct.unpack_from("<f", blob, pos)[0]
        pos += 4
        kind = "f32_candidate"
        meta["raw_hex"] = raw.hex()
    elif type_byte == 34:
        if pos + 8 > end:
            raise ValueError("truncated f64")
        raw = blob[pos:pos + 8]
        value = struct.unpack_from("<d", blob, pos)[0]
        pos += 8
        kind = "f64_candidate"
        meta["raw_hex"] = raw.hex()
    else:
        raise ValueError(f"unhandled type {type_byte:#x}")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("non-finite float")
    meta["value_operand_end"] = pos
    return value, pos, kind, meta


def decode_d6(blob: bytes, data_end: int, row_start: int, slots: list[str]) -> dict:
    if not (4 <= row_start < data_end) or blob[row_start] != 0xD6:
        raise ValueError("not a bounded D6 row")
    pos = row_start + 1
    schema_ref, pos, schema_raw = uleb(blob, pos, data_end)
    bitmap_ref, pos, bitmap_raw = uleb(blob, pos, data_end)
    schema, bitmap_bits, schema_end = parse_schema(blob, schema_ref, slots)
    bitmap_size = (bitmap_bits + 7) // 8
    if not (4 <= bitmap_ref and bitmap_ref + bitmap_size <= data_end):
        raise ValueError("bitmap ref out of data-region bounds")
    bitmap = blob[bitmap_ref:bitmap_ref + bitmap_size]
    fields = selected_fields(schema, bitmap_bits, bitmap)
    values = []
    for field in fields:
        value, pos, kind, meta = decode_scalar(blob, pos, data_end, field, slots)
        values.append({
            **field,
            "type_byte_hex": f"0x{field['type_byte']:02x}",
            "decode_kind": kind,
            "value": value,
            **meta,
        })
    return {
        "row_start": row_start,
        "row_tag": "0xd6",
        "schema_ref": schema_ref,
        "schema_ref_uleb_hex": schema_raw.hex(),
        "schema_end": schema_end,
        "schema_field_count": len(schema),
        "bitmap_ref": bitmap_ref,
        "bitmap_ref_uleb_hex": bitmap_raw.hex(),
        "bitmap_bits": bitmap_bits,
        "bitmap_hex": bitmap.hex(),
        "selected_field_count": len(fields),
        "value_end": pos,
        "values": values,
    }


def field_value(row: dict, name: str) -> object:
    matches = [x["value"] for x in row["values"] if x["field_name"] == name]
    return matches[0] if len(matches) == 1 else {"match_count": len(matches), "values": matches}


def candidate_addresses(edge: dict, row_start: int, blob_len: int) -> dict:
    operand = edge["value"]["operand_u"]
    start = edge["value_operand_start"]
    end = edge["value_operand_end"]
    raw = {
        "blob_absolute": operand,
        "blob_absolute_plus_4": operand + 4,
        "operand_start_plus": start + operand,
        "operand_end_plus": end + operand,
        "row_start_plus": row_start + operand,
        "operand_start_minus": start - operand,
        "operand_end_minus": end - operand,
        "row_start_minus": row_start - operand,
    }
    return {
        name: {
            "target": target,
            "in_blob": 0 <= target < blob_len,
        }
        for name, target in raw.items()
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    package, members = unpack_members()
    slots, chs_meta = parse_chs(members[CHS_ID]["body"])
    blob, data_end, key_to_start, base_meta = parse_base_blob(members[BASE_ID]["body"])

    d6_rows = {}
    failures = []
    for key, start in key_to_start.items():
        if blob[start] != 0xD6:
            continue
        try:
            d6_rows[key] = decode_d6(blob, data_end, start, slots)
        except Exception as exc:
            failures.append({"key_u": key, "row_start": start, "error": repr(exc)})

    target_rows = {}
    pointer_edges = []
    for key, row in d6_rows.items():
        for value in row["values"]:
            if value["type_byte"] != 11:
                continue
            edge = {
                "source_key_u": key,
                "source_row_start": row["row_start"],
                "field_index": value["field_index"],
                "field_name": value["field_name"],
                "field_slot": value["field_slot"],
                "value_operand_start": value["value_operand_start"],
                "value_operand_end": value["value_operand_end"],
                "operand_uleb_hex": value["operand_uleb_hex"],
                "value": value["value"],
            }
            candidates = candidate_addresses(value, row["row_start"], len(blob))
            for candidate in candidates.values():
                if candidate["in_blob"]:
                    candidate["target_byte"] = blob[candidate["target"]]
                    candidate["target_byte_hex"] = f"0x{blob[candidate['target']]:02x}"
            edge["address_candidates"] = candidates
            pointer_edges.append(edge)

    for key in TARGET_KEYS:
        row = d6_rows.get(key)
        if row is None:
            target_rows[str(key)] = None
            continue
        compact = {
            "key_u": key,
            "row_start": row["row_start"],
            "schema_ref": row["schema_ref"],
            "bitmap_ref": row["bitmap_ref"],
            "value_end": row["value_end"],
            "id": field_value(row, "id"),
            "name": field_value(row, "name"),
            "attrs": field_value(row, "attrs"),
            "pointer_fields": [x for x in row["values"] if x["type_byte"] == 11],
            "row_hexdump": hexdump(blob, row["row_start"], min(512, row["value_end"] - row["row_start"] + 16)),
        }
        target_rows[str(key)] = compact

    mode_tag_counts: dict[str, Counter] = defaultdict(Counter)
    mode_in_bounds = Counter()
    for edge in pointer_edges:
        for mode, candidate in edge["address_candidates"].items():
            if candidate["in_blob"]:
                mode_in_bounds[mode] += 1
                mode_tag_counts[mode][candidate["target_byte_hex"]] += 1

    requested_offsets = sorted({188212, 187449} | {
        value["value"]["operand_u"]
        for row in target_rows.values() if row
        for value in row["pointer_fields"]
        if value["field_name"] == "attrs"
    })
    offset_dumps = {}
    for offset in requested_offsets:
        offset_dumps[str(offset)] = {
            "offset": offset,
            "in_data_region": 4 <= offset < data_end,
            "target_byte": blob[offset] if 0 <= offset < len(blob) else None,
            "target_byte_hex": f"0x{blob[offset]:02x}" if 0 <= offset < len(blob) else None,
            "before": hexdump(blob, max(0, offset - 32), 32),
            "from_target": hexdump(blob, offset, 256) if 0 <= offset < len(blob) else None,
        }

    source_members = {}
    for file_id, item in members.items():
        source_members[f"{file_id:016X}"] = {k: v for k, v in item.items() if k != "body"}

    result = {
        "analysis": "LifeAfter_PC_BinDict_0x0B_static_probe",
        "safety": {
            "source_root": "E:/mrzh",
            "source_read_only": True,
            "output_root": OUT.as_posix(),
            "payload_imported": False,
            "marshal_used": False,
            "exec_eval_compile_used": False,
        },
        "package": package,
        "source_members": source_members,
        "chs": chs_meta,
        "base": base_meta,
        "coverage": {
            "indexed_rows": len(key_to_start),
            "d6_rows": len(d6_rows),
            "d6_decode_failures": len(failures),
            "failure_samples": failures[:30],
            "type_0x0b_edges": len(pointer_edges),
        },
        "target_rows": target_rows,
        "address_mode_probe": {
            "in_bounds_count": dict(mode_in_bounds),
            "target_tag_counts": {mode: dict(counts.most_common()) for mode, counts in mode_tag_counts.items()},
            "note": "Tag concentration is only a discriminator; object grammar is analyzed in the next stage.",
        },
        "requested_offset_dumps": offset_dumps,
        "pointer_edges": pointer_edges,
    }
    output = OUT / "00_current_snapshot_static_probe.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    reparsed = json.loads(output.read_text(encoding="utf-8"))
    assert reparsed["package"]["sha256"] == package["sha256"]
    print(json.dumps({
        "output": output.as_posix(),
        "package": package,
        "base": base_meta,
        "chs": chs_meta,
        "coverage": result["coverage"],
        "target_attrs": {key: (row or {}).get("attrs") for key, row in target_rows.items()},
        "requested_target_tags": {key: value["target_byte_hex"] for key, value in offset_dumps.items()},
        "absolute_top_tags": dict(mode_tag_counts["blob_absolute"].most_common(20)),
    }, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
