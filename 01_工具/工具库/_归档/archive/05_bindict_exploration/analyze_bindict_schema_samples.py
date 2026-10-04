"""Read-only structural comparison for test-server bindict table samples.
Never executes payloads or modifies E:\\mrzh. Output is evidence-only.
"""
from __future__ import annotations
import csv
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCAN = ROOT / "体验服武器商品中文表扫描_003"
OUT = ROOT / "bindict结构差分样本_001"
OUT.mkdir(parents=True, exist_ok=True)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_uleb(data: bytes, pos: int, end: int) -> tuple[int, int]:
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


def parse_payload(payload: bytes, logical_path: str) -> dict:
    if payload[:2] != b"tI":
        raise ValueError("unexpected payload head")
    path_len = struct.unpack_from("<I", payload, 2)[0]
    actual_path = payload[6:6 + path_len].decode("utf-8", "strict")
    if actual_path != logical_path:
        raise ValueError(f"logical path mismatch: {actual_path!r}")
    path_end = 6 + path_len

    # Find only a fully bounds-checked standalone `I` string-pool block.
    for marker in range(path_end, len(payload) - 13):
        if payload[marker] != 0x49:
            continue
        block_len, count = struct.unpack_from("<II", payload, marker + 1)
        end = marker + 5 + block_len
        offsets_start = marker + 9
        offsets_end = offsets_start + 4 * (count + 1)
        if not (0 < block_len <= len(payload) - marker - 5 and count < 100000 and offsets_end <= end):
            continue
        offsets = struct.unpack_from(f"<{count + 1}I", payload, offsets_start)
        pool_data_start = offsets_end
        if offsets[0] != 0 or any(offsets[i] < offsets[i - 1] for i in range(1, len(offsets))):
            continue
        if pool_data_start + offsets[-1] > end:
            continue
        try:
            strings = [payload[pool_data_start + offsets[i]: pool_data_start + offsets[i + 1]].decode("utf-8") for i in range(count)]
        except UnicodeDecodeError:
            continue
        return {
            "path_end": path_end,
            "string_marker": marker,
            "string_block_end": end,
            "strings": strings,
            "bindict_blob": payload[pool_data_start + offsets[-1]:end],
        }
    raise ValueError("no validated string-pool block")


def parse_hash_index(blob: bytes) -> tuple[list[dict], list[dict]]:
    # This is a structural parse only. `key` is neutral until codec semantics are known.
    key_hash_offset = struct.unpack_from("<I", blob, 0)[0]
    if not (4 <= key_hash_offset < len(blob)):
        raise ValueError("key-hash offset out of bounds")
    tail = blob[key_hash_offset:]
    if len(tail) < 4 or tail[0] != 0x76:
        raise ValueError("unrecognized key-hash index marker")
    count = tail[3]
    if 4 + 8 * count > len(tail):
        raise ValueError("key-hash index exceeds blob")
    pairs = []
    for i in range(count):
        hash32, node_off = struct.unpack_from("<II", tail, 4 + 8 * i)
        if not (4 <= node_off < len(blob)):
            raise ValueError("node offset out of bounds")
        pairs.append({"hash32": f"{hash32:08X}", "node_offset": node_off})

    node_offsets = sorted({pair["node_offset"] for pair in pairs})
    nodes = []
    for i, node_off in enumerate(node_offsets):
        node_end = node_offsets[i + 1] if i + 1 < len(node_offsets) else len(blob)
        try:
            neutral_key, pos = read_uleb(blob, node_off, node_end)
            record_offset, pos2 = read_uleb(blob, pos, node_end)
        except ValueError:
            nodes.append({"node_offset": node_off, "node_end": node_end, "raw_hex": blob[node_off:node_end].hex(), "parse_status": "unparsed"})
            continue
        nodes.append({
            "node_offset": node_off,
            "node_end": node_end,
            "raw_hex": blob[node_off:node_end].hex(),
            "neutral_key": neutral_key,
            "record_offset": record_offset,
            "bytes_consumed": pos2 - node_off,
            "parse_status": "uleb_pair_candidate",
        })
    return pairs, nodes


def analyze_legacy(base_hits: dict) -> dict:
    slash = chr(92)
    base_path = slash.join(["com", "cdata", "weapon_skin_legacy_data.py"])
    chs_path = slash.join(["com", "cdata", "weapon_skin_legacy_data_chs.py"])
    base_payload = Path(base_hits[base_path]["raw_payload_path"]).read_bytes()
    chs_payload = Path(base_hits[chs_path]["raw_payload_path"]).read_bytes()
    base = parse_payload(base_payload, base_path)
    chs = parse_payload(chs_payload, chs_path)
    blob = base["bindict_blob"]
    pairs, nodes = parse_hash_index(blob)

    record_offsets = sorted({n["record_offset"] for n in nodes if n.get("parse_status") == "uleb_pair_candidate" and 4 <= n["record_offset"] < len(blob)})
    records = []
    chinese_slots = {i: s for i, s in enumerate(chs["strings"]) if any("\u4e00" <= char <= "\u9fff" for char in s)}
    for idx, start in enumerate(record_offsets):
        end = record_offsets[idx + 1] if idx + 1 < len(record_offsets) else struct.unpack_from("<I", blob, 0)[0]
        raw = blob[start:end]
        # A literal slot candidate is retained as a candidate, not a decoded reference.
        literal_slots = [{"byte_offset": i, "value": byte, "string": chinese_slots[byte]} for i, byte in enumerate(raw) if byte in chinese_slots]
        records.append({
            "record_offset": start,
            "record_end": end,
            "record_length": len(raw),
            "raw_hex": raw.hex(),
            "starts_96": raw.startswith(b"\x96"),
            "schema_byte": raw[1] if len(raw) >= 2 else None,
            "literal_chinese_slot_candidates": literal_slots,
        })
    candidate_values = sorted({c["value"] for r in records for c in r["literal_chinese_slot_candidates"]})
    return {
        "source_lock": "E:\\mrzh only; original packages read-only",
        "base_table": {"logical_path": base_path, "file_id": base_hits[base_path]["file_id"], "payload_sha256": sha256(base_payload)},
        "chs_table": {"logical_path": chs_path, "file_id": base_hits[chs_path]["file_id"], "payload_sha256": sha256(chs_payload)},
        "structure": {
            "base_string_count": len(base["strings"]),
            "chs_string_count": len(chs["strings"]),
            "key_hash_pairs": pairs,
            "index_nodes": nodes,
            "records": records,
        },
        "chs_chinese_slots": chinese_slots,
        "candidate_coverage": {
            "raw_byte_values_in_chinese_slot_range": candidate_values,
            "all_chinese_slot_values": sorted(chinese_slots),
            "raw_byte_set_match": candidate_values == sorted(chinese_slots),
            "status": "NON_BINDING_HEURISTIC_ONLY",
            "interpretation": "A raw-byte range scan can include control bytes and varint bytes. It is retained only as a differential clue and must not be treated as a string reference, row/name binding, or evidence for the main-table codec.",
        },
    }


def main() -> None:
    manifest = json.loads((SCAN / "体验服武器商品表定位.json").read_text(encoding="utf-8"))
    hits = {entry["logical_path"]: entry for entry in manifest["hits"]}
    result = analyze_legacy(hits)
    output_json = OUT / "体验服_bindict_传世表结构差分_001.json"
    output_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    csv_path = OUT / "体验服_bindict_传世表记录边界_001.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["record_offset", "record_end", "record_length", "starts_96", "schema_byte", "raw_hex", "literal_chinese_slot_candidates"])
        writer.writeheader()
        for row in result["structure"]["records"]:
            copy = dict(row)
            copy["literal_chinese_slot_candidates"] = json.dumps(copy["literal_chinese_slot_candidates"], ensure_ascii=False)
            writer.writerow(copy)
    print(json.dumps({
        "output": str(output_json),
        "records": len(result["structure"]["records"]),
        "schema_bytes": sorted({r["schema_byte"] for r in result["structure"]["records"]}),
        "candidate_coverage": result["candidate_coverage"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
