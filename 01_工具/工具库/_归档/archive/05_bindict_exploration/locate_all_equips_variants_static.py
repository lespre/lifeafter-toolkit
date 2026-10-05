"""Read-only static locator for all_equips_data table variants in E:\mrzh.

It decodes only NPK entries, never imports/executes game payloads. Legacy tI/sI
wrappers supply logical paths; matching file IDs are then looked up in every
script package to establish cross-variant coverage.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import struct
from pathlib import Path

OUT = Path(r"C:\Users\<user>\AppData\Local\hermes\mrzh_weapon_skin_audit\run_002\AUG突击步枪定点核查_001")
ROOT = Path(r"E:\mrzh")
HELPER = Path(r"C:\Users\<user>\AppData\Local\hermes\mrzh_weapon_skin_audit\run_002\audit_mrzh_aurora_script_presence.py")


def load_helper():
    spec = importlib.util.spec_from_file_location("static_npk_helper", HELPER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_table(module, path: Path):
    source_size = path.stat().st_size
    with path.open("rb") as handle:
        header = module.aes_ecb(handle.read(32))
        unknown, magic, version, table_offset, count = struct.unpack_from("<QIIII", header)
        if magic != 0x4B50584E:
            raise ValueError(f"unexpected NPK magic {magic:#x}")
        if table_offset + count * 48 > source_size:
            raise ValueError("entry table outside source bounds")
        handle.seek(table_offset)
        table = module.aes_ecb(handle.read(count * 48))
    return {
        "source_size": source_size,
        "source_sha256": sha256_file(path),
        "unknown": unknown,
        "magic": magic,
        "version": version,
        "table_offset": table_offset,
        "entry_count": count,
    }, table


def scan_legacy_paths(module, path: Path):
    meta, table = read_table(module, path)
    hits, errors, decoded, valid = [], [], 0, 0
    with path.open("rb") as handle:
        for index in range(meta["entry_count"]):
            file_id, offset, packed_size, declared_size, c1, c2, flag = struct.unpack_from(
                "<QIIIIIi", table, index * 48
            )
            if offset + packed_size > meta["source_size"]:
                errors.append({"entry_index": index, "file_id": f"{file_id:016X}", "stage": "bounds"})
                continue
            valid += 1
            handle.seek(offset)
            packed = handle.read(packed_size)
            try:
                payload = module.unpack_entry(packed, declared_size, flag)
                decoded += 1
            except Exception as exc:  # preserve static unpack failures rather than hide them
                errors.append({
                    "entry_index": index,
                    "file_id": f"{file_id:016X}",
                    "stage": "static_unpack",
                    "flag": flag,
                    "error": repr(exc),
                })
                continue
            logical_path = module.parse_logical_path(payload)
            if "all_equips" not in logical_path.lower():
                continue
            hits.append({
                "entry_index": index,
                "file_id": f"{file_id:016X}",
                "logical_path_direct": logical_path,
                "entry_offset": offset,
                "packed_size": packed_size,
                "declared_size": declared_size,
                "flag": flag,
                "payload_size_static": len(payload),
                "payload_sha256": hashlib.sha256(payload).hexdigest(),
                "payload_head_hex": payload[:96].hex(),
            })
    meta.update({
        "entries_table_valid": valid,
        "entries_static_decoded": decoded,
        "entry_errors": errors,
        "all_equips_path_hits": hits,
    })
    return meta, hits


def cross_lookup(module, packages: list[Path], file_ids: set[int]):
    rows = []
    for path in packages:
        meta, table = read_table(module, path)
        found = []
        for index in range(meta["entry_count"]):
            file_id, offset, packed_size, declared_size, c1, c2, flag = struct.unpack_from(
                "<QIIIIIi", table, index * 48
            )
            if file_id not in file_ids:
                continue
            found.append({
                "entry_index": index,
                "file_id": f"{file_id:016X}",
                "entry_offset": offset,
                "packed_size": packed_size,
                "declared_size": declared_size,
                "c1": c1,
                "c2": c2,
                "flag": flag,
            })
        rows.append({"package": str(path), **meta, "matched_file_ids": found})
    return rows


def main():
    module = load_helper()
    legacy = [ROOT / "script.npk", ROOT / "Documents" / "script.npk"]
    all_scripts = [
        ROOT / "script.npk",
        ROOT / "Documents" / "script.npk",
        ROOT / "Documents" / "script.py3.npk",
        ROOT / "Documents" / "script.py314.lc.npk",
    ]
    result = {
        "method": "read-only NPK static unpack + tI/sI logical-path scan; no target-payload import or execution",
        "source_root": str(ROOT),
        "legacy_scans": [],
    }
    unique_by_id = {}
    for path in legacy:
        meta, hits = scan_legacy_paths(module, path)
        result["legacy_scans"].append({"package": str(path), **meta})
        for hit in hits:
            unique_by_id.setdefault(hit["file_id"], hit["logical_path_direct"])
    result["all_equips_logical_path_by_file_id"] = unique_by_id
    result["cross_variant_table_lookup"] = cross_lookup(module, all_scripts, {int(x, 16) for x in unique_by_id})
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / "体验服_all_equips_同源表定位_001.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    json.loads(out.read_text(encoding="utf-8"))
    print(json.dumps({
        "report": str(out),
        "path_count": len(unique_by_id),
        "paths": unique_by_id,
        "legacy_coverage": [
            {k: x[k] for k in ("package", "source_sha256", "entry_count", "entries_static_decoded", "entry_errors")}
            for x in result["legacy_scans"]
        ],
        "cross_matches": [
            {"package": x["package"], "matched": len(x["matched_file_ids"]), "items": x["matched_file_ids"]}
            for x in result["cross_variant_table_lookup"]
        ],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
