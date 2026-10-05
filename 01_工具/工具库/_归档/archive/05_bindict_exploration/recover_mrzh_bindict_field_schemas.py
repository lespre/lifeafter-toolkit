"""Recover bounded bindict schema layout metadata from experience-server tables.

This does not decode value bytes. It identifies only the exact schema layout:
  field-order permutation[N] + N + N descriptor pairs + terminal byte
using a length equation and a 0..N-1 permutation check.
"""
from __future__ import annotations

import csv
import hashlib
import json
import struct
from pathlib import Path

RUN = Path(__file__).resolve().parent
SCAN = RUN / "体验服武器商品中文表扫描_003"
OUT = RUN / "体验服_Bindict字段Schema_001"
OUT.mkdir(parents=True, exist_ok=True)
BS = chr(92)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def uleb(data: bytes, pos: int, end: int) -> tuple[int, int]:
    value = shift = 0
    while pos < end:
        byte = data[pos]
        pos += 1
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value, pos
        shift += 7
        if shift > 63:
            break
    raise ValueError("invalid/truncated ULEB")


def payload_parts(payload: bytes, logical_path: str) -> tuple[list[str], bytes]:
    if payload[:2] != b"tI":
        raise ValueError("unexpected envelope")
    name_length = struct.unpack_from("<I", payload, 2)[0]
    actual = payload[6:6 + name_length].decode("utf-8", "strict")
    if actual != logical_path:
        raise ValueError("logical path mismatch")
    for marker in range(6 + name_length, len(payload) - 13):
        if payload[marker] != 0x49:
            continue
        block_length, string_count = struct.unpack_from("<II", payload, marker + 1)
        end = marker + 5 + block_length
        offsets_start = marker + 9
        raw_start = offsets_start + 4 * (string_count + 1)
        if not (0 < block_length <= len(payload) - marker - 5 and string_count < 100000 and raw_start <= end):
            continue
        offsets = struct.unpack_from(f"<{string_count + 1}I", payload, offsets_start)
        if offsets[0] != 0 or any(offsets[i] < offsets[i - 1] for i in range(1, len(offsets))) or raw_start + offsets[-1] > end:
            continue
        strings = [payload[raw_start + offsets[i]:raw_start + offsets[i + 1]].decode("utf-8", "replace") for i in range(string_count)]
        return strings, payload[raw_start + offsets[-1]:end]
    raise ValueError("no bounded string-pool/bindict block")


def record_starts(blob: bytes, key_mode: str) -> tuple[int, list[int], int | None]:
    data_end = struct.unpack_from("<I", blob, 0)[0]
    if not (4 <= data_end < len(blob)):
        raise ValueError("invalid data end")
    tail = blob[data_end:]
    if len(tail) < 4 or tail[0] != 0x76:
        raise ValueError("missing hash index")
    count = tail[3]
    if 4 + 8 * count > len(tail):
        raise ValueError("truncated hash index")
    node_offsets = sorted({struct.unpack_from("<I", tail, 4 + 8 * i + 4)[0] for i in range(count)})
    pointers = []
    schema_byte = None
    for ordinal, node_start in enumerate(node_offsets):
        node_end = node_offsets[ordinal + 1] if ordinal + 1 < len(node_offsets) else len(blob)
        if key_mode == "u24":
            pointer, consumed = uleb(blob, node_start + 3, node_end)
        else:
            _key, after_key = uleb(blob, node_start, node_end)
            pointer, consumed = uleb(blob, after_key, node_end)
        if consumed != node_end or not (4 <= pointer < data_end):
            raise ValueError("unvalidated index node")
        if blob[pointer] == 0x96:
            if pointer + 1 >= data_end:
                raise ValueError("truncated record tag")
            if schema_byte is None:
                schema_byte = blob[pointer + 1]
            elif schema_byte != blob[pointer + 1]:
                raise ValueError("mixed record schemas; not a single-schema sample")
        pointers.append(pointer)
    return data_end, sorted(set(pointers)), schema_byte


def recover_schema(preamble: bytes) -> dict:
    candidates = []
    for start in range(len(preamble)):
        # Need enough bytes for N>=1, N count, 2*N descriptors, and final byte.
        for n in range(1, min(255, len(preamble) - start)):
            end = start + n
            if end >= len(preamble) or preamble[end] != n:
                continue
            if len(preamble) - start != n + 1 + 2 * n + 1:
                continue
            order = list(preamble[start:end])
            if sorted(order) == list(range(n)):
                candidates.append((start, n, order))
    if len(candidates) != 1:
        raise ValueError(f"schema-layout candidate count={len(candidates)}, candidates={[(s, n) for s,n,_ in candidates]}")
    start, n, order = candidates[0]
    descriptors_start = start + n + 1
    descriptor_bytes = preamble[descriptors_start:descriptors_start + 2 * n]
    terminal = preamble[-1]
    return {
        "shared_prefix_length": start,
        "shared_prefix_hex": preamble[:start].hex(),
        "field_count": n,
        "serialized_field_order": order,
        "descriptor_pairs": [[descriptor_bytes[2 * i], descriptor_bytes[2 * i + 1]] for i in range(n)],
        "terminal_byte": terminal,
    }


def main() -> None:
    manifest = json.loads((SCAN / "体验服武器商品表定位.json").read_text(encoding="utf-8"))
    hits = {entry["logical_path"]: entry for entry in manifest["hits"]}
    targets = [
        ("weapon_skin_2_legacy_skin_data.py", "uleb"),
        ("weapon_skin_kind_data.py", "uleb"),
        ("weapon_skin_behavior_res_data.py", "u24"),
        ("weapon_skin_data.py", "u24"),
    ]
    tables = []
    all_rows = []
    for filename, key_mode in targets:
        path = BS.join(["com", "cdata", filename])
        chs_path = path[:-3] + "_chs.py"
        payload = Path(hits[path]["raw_payload_path"]).read_bytes()
        chs_payload = Path(hits[chs_path]["raw_payload_path"]).read_bytes()
        _base_strings, blob = payload_parts(payload, path)
        chs_strings, _ = payload_parts(chs_payload, chs_path)
        data_end, starts, schema_byte = record_starts(blob, key_mode)
        preamble = blob[4:min(starts)]
        schema = recover_schema(preamble)
        if schema["field_count"] > len(chs_strings):
            raise ValueError(f"{filename}: more fields than CHS entries")
        fields = []
        for serial_pos, (field_id, pair) in enumerate(zip(schema["serialized_field_order"], schema["descriptor_pairs"])):
            if pair[1] != field_id:
                raise ValueError(f"{filename}: descriptor field ID {pair[1]} does not equal order field ID {field_id}")
            field = {
                "serial_position": serial_pos,
                "field_id": field_id,
                "field_name": chs_strings[field_id],
                "type_code": pair[0],
                "descriptor_field_id": pair[1],
            }
            fields.append(field)
            all_rows.append({"table": filename, **field})
        tables.append({
            "logical_path": path,
            "file_id": hits[path]["file_id"],
            "payload_sha256": sha256(payload),
            "chs_file_id": hits[chs_path]["file_id"],
            "chs_payload_sha256": sha256(chs_payload),
            "index_key_mode": key_mode,
            "record_count": len(starts),
            "record_tag": "96" if schema_byte is not None else None,
            "record_schema_byte": schema_byte,
            "preamble_length": len(preamble),
            "schema": schema,
            "fields": fields,
            "value_codec_status": "NOT_DECODED; descriptor bytes are preserved but not semantically named.",
        })
    result = {
        "source_lock": "E:\\mrzh only; original packages read-only",
        "conclusion": "Validated only the field-order/schema-descriptor layout. No record value, Chinese skin name, model path, SFX path, or physical asset binding is asserted by this artifact.",
        "schema_layout": "shared_prefix + field-order permutation[N] + N + N two-byte descriptor pairs + one terminal byte",
        "tables": tables,
        "verification": {
            "table_count": len(tables),
            "main_field_count": next(table["schema"]["field_count"] for table in tables if table["logical_path"].endswith("weapon_skin_data.py")),
            "main_fields_are_exact_0_to_39": sorted(next(table["schema"]["serialized_field_order"] for table in tables if table["logical_path"].endswith("weapon_skin_data.py"))) == list(range(40)),
            "all_descriptor_field_ids_match_serialized_field_ids": all(
                field["descriptor_field_id"] == field["field_id"]
                for table in tables for field in table["fields"]
            ),
        },
    }
    json_path = OUT / "体验服_Bindict字段Schema_001.json"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    csv_path = OUT / "体验服_Bindict字段Schema_001.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["table", "serial_position", "field_id", "field_name", "type_code", "descriptor_field_id"])
        writer.writeheader()
        writer.writerows(all_rows)
    print(json.dumps({"output_json": str(json_path), "output_csv": str(csv_path), "verification": result["verification"], "main_order": next(table["schema"]["serialized_field_order"] for table in tables if table["logical_path"].endswith("weapon_skin_data.py"))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
