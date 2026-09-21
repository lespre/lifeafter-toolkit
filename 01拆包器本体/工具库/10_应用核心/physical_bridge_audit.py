"""Read-only physical-bridge audit for the LifeAfter PC resource snapshot.

This tool deliberately separates three facts:
1. current script configuration proves a logical skin path;
2. current IDX/WPK proves a physical 1DPW entity;
3. only an exact, reproducible path-to-hash relation may join (1) and (2).

It reads E:\\mrzh only. Reports are written under this toolkit's external output
folder; no game package, cache, or payload is modified or executed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import struct
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

TOOLKIT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = TOOLKIT_ROOT / "output" / "physical_bridge_v002"
DEFAULT_DOCS = Path(r"E:\mrzh\Documents")
DEFAULT_HISTORICAL = Path(
    r"C:\Users\Administrator\AppData\Local\hermes\mrzh_weapon_skin_audit\run_002"
)


@dataclass(frozen=True)
class IdxEntry:
    index: int
    resource_hash: str
    package_raw: int
    package_low: int
    offset: int
    payload_size: int
    header_field: int


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_skpw(path: Path) -> list[IdxEntry]:
    """Parse the verified SKPW layout: 0x20 header, 36B records, 4B trailer."""
    data = path.read_bytes()
    if data[:4] != b"SKPW":
        raise ValueError(f"not SKPW: {path}")
    if len(data) < 0x24 or (len(data) - 0x24) % 0x24:
        raise ValueError(f"invalid SKPW geometry: {path} ({len(data)} bytes)")
    entries: list[IdxEntry] = []
    for index, at in enumerate(range(0x20, len(data) - 4, 0x24)):
        resource_hash = data[at : at + 16].hex()
        package_raw = struct.unpack_from("<I", data, at + 20)[0]
        offset, payload_size, header_field = struct.unpack_from("<III", data, at + 24)
        entries.append(
            IdxEntry(
                index=index,
                resource_hash=resource_hash,
                package_raw=package_raw,
                package_low=package_raw & 0xFF,
                offset=offset,
                payload_size=payload_size,
                header_field=header_field,
            )
        )
    return entries


def verify_1dpw_entries(entries: Iterable[IdxEntry], resource_dir: Path, group: str) -> dict:
    """Verify only physical layout; never decode or execute a target payload.

    SKPW's pkg=0xFF is a verified side-slot convention: the resource is stored
    as ``res/<group>/<16-byte IDX hash>``. It is accepted only after the file's
    own 1DPW header repeats that exact hash and IDX metadata below.
    """
    reports: list[dict] = []
    for entry in entries:
        base = asdict(entry)
        if entry.package_low == 0xFF:
            source = resource_dir / group / entry.resource_hash
            source_kind = "side_slot_hash_filename"
        else:
            source = resource_dir / f"{group}{entry.package_low}.wpk"
            source_kind = "wpk_volume"
        if not source.is_file():
            base.update(status="missing_physical_source", source_path=str(source), source_kind=source_kind)
            reports.append(base)
            continue
        expected = 0x30 + entry.payload_size
        size = source.stat().st_size
        if entry.offset < 0 or entry.offset + expected > size:
            base.update(
                status="out_of_bounds",
                source_path=str(source),
                source_size=size,
                expected_total_size=expected,
            )
            reports.append(base)
            continue
        with source.open("rb") as handle:
            handle.seek(entry.offset)
            outer = handle.read(0x30)
        if len(outer) != 0x30:
            base.update(status="short_1dpw_header", source_path=str(source))
            reports.append(base)
            continue
        outer_hash = outer[8:24].hex()
        outer_payload_size = struct.unpack_from("<I", outer, 32)[0]
        outer_header_field = struct.unpack_from("<I", outer, 36)[0]
        status = "verified_1dpw_boundary"
        if outer[:4] != b"1DPW":
            status = "wrong_outer_magic"
        elif outer_hash != entry.resource_hash:
            status = "hash_mismatch"
        elif outer_payload_size != entry.payload_size:
            status = "payload_size_mismatch"
        elif outer_header_field != entry.header_field:
            status = "header_field_mismatch"
        base.update(
            status=status,
            source_path=str(source),
            source_size=size,
            expected_total_size=expected,
            outer_magic=outer[:4].decode("ascii", "replace"),
            outer_resource_hash=outer_hash,
            outer_payload_size=outer_payload_size,
            outer_header_field=outer_header_field,
        )
        reports.append(base)
    return {
        "entry_count": len(reports),
        "verified_count": sum(row["status"] == "verified_1dpw_boundary" for row in reports),
        "failure_count": sum(row["status"] != "verified_1dpw_boundary" for row in reports),
        "side_slot_count": sum(row["package_low"] == 0xFF for row in reports),
        "entries": reports,
    }


def valid_py3_logical_rows(csv_path: Path) -> tuple[dict, list[dict]]:
    """Reuse prior extraction only when both current package and cached payload hash match."""
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8-sig", newline="")))
    py3_rows = [row for row in rows if row.get("source_package_label") == "script_py3"]
    if not py3_rows:
        raise ValueError("no script_py3 logical rows in source CSV")
    package = Path(py3_rows[0]["source_package"])
    package_actual_sha = sha256_file(package) if package.is_file() else ""
    valid: list[dict] = []
    rejected: list[dict] = []
    for row in py3_rows:
        payload = Path(row["source_payload"])
        payload_sha = sha256_file(payload) if payload.is_file() else ""
        row_ok = (
            package_actual_sha == row["source_package_sha256"]
            and payload_sha == row["source_payload_sha256"]
        )
        (valid if row_ok else rejected).append(row)
    summary = {
        "evidence_kind": "unchanged_package_SHA + prior static payload extraction SHA",
        "source_csv": str(csv_path),
        "py3_package": str(package),
        "py3_package_sha256": package_actual_sha,
        "rows_in_csv": len(rows),
        "py3_rows": len(py3_rows),
        "valid_rows": len(valid),
        "rejected_rows": len(rejected),
        "unique_skin_ids": len({row["skin_id"] for row in valid}),
        "unique_logical_paths": len({row["logical_asset_path"] for row in valid}),
        "excluded_reason": "Rows from script_py314 are not accepted because the current package SHA differs from their recorded snapshot.",
    }
    return summary, valid


def candidate_strings(logical_path: str, asset_type: str) -> set[str]:
    normalized = logical_path.replace("/", "\\")
    chunks = [item for item in normalized.split("\\") if item]
    bases = {"\\".join(chunks[index:]) for index in range(len(chunks))}
    expanded: set[str] = set()
    for candidate in bases:
        expanded.add(candidate)
        if asset_type == "gim" and candidate.lower().endswith(".gim"):
            expanded.add(candidate[:-4] + ".mesh")
            expanded.add(candidate[:-4] + ".mtg")
    return expanded


def hash_candidates(rows: Iterable[dict], idx_hashes: set[str]) -> dict:
    """Exact 16-byte checks only. A miss is not converted into a candidate assignment."""
    methods = {
        "md5_utf8": lambda value: hashlib.md5(value.encode("utf-8")).hexdigest(),
        "md5_utf16le": lambda value: hashlib.md5(value.encode("utf-16le")).hexdigest(),
        "sha1_prefix16_utf8": lambda value: hashlib.sha1(value.encode("utf-8")).hexdigest()[:32],
        "sha256_prefix16_utf8": lambda value: hashlib.sha256(value.encode("utf-8")).hexdigest()[:32],
        "blake2s16_utf8": lambda value: hashlib.blake2s(value.encode("utf-8"), digest_size=16).hexdigest(),
    }
    examined = 0
    matches: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for row in rows:
        for candidate in candidate_strings(row["logical_asset_path"], row["asset_type"]):
            for method_name, method in methods.items():
                examined += 1
                digest = method(candidate)
                if digest in idx_hashes:
                    key = (candidate, method_name)
                    if key not in seen:
                        seen.add(key)
                        matches.append(
                            {
                                "skin_id": row["skin_id"],
                                "logical_asset_path": row["logical_asset_path"],
                                "candidate_input": candidate,
                                "method": method_name,
                                "idx_hash": digest,
                            }
                        )
    return {
        "candidate_rows": examined,
        "exact_16_byte_hash_matches": len(matches),
        "matches": matches,
        "boundary": "No approximate, visual, sequence, offset, or filename-neighbor relation is accepted as a bridge.",
    }


def raw_hash_hits(blob: bytes, hashes: Iterable[str]) -> dict:
    """Find exact raw 16-byte IDX hashes with a 4-byte prefix index."""
    prefixes: dict[bytes, list[bytes]] = {}
    for value in hashes:
        raw = bytes.fromhex(value)
        prefixes.setdefault(raw[:4], []).append(raw)
    hits: set[str] = set()
    for offset in range(0, max(0, len(blob) - 15)):
        for raw in prefixes.get(blob[offset : offset + 4], []):
            if blob[offset : offset + 16] == raw:
                hits.add(raw.hex())
    return {"distinct_idx_hash_hits": len(hits), "hashes": sorted(hits)}


def fhpk_layer_evidence(fhpk_path: Path, search_roots: Iterable[Path]) -> dict:
    data = fhpk_path.read_bytes()
    if data[:4] != b"FHPK":
        raise ValueError(f"not FHPK: {fhpk_path}")
    declared = struct.unpack_from("<I", data, 8)[0]
    raw_paths = sorted(
        {
            match.decode("ascii")
            for match in re.findall(
                rb"res/(?:weapon|model|ui)[A-Za-z0-9_./-]*\.npk", data
            )
        }
    )
    present: dict[str, list[str]] = {}
    for relative in raw_paths:
        name = Path(relative).name
        found: list[str] = []
        for root in search_roots:
            if root.is_dir():
                found.extend(str(path) for path in root.rglob(name) if path.is_file())
        present[relative] = sorted(set(found))
    return {
        "fhpk_path": str(fhpk_path),
        "fhpk_declared_entry_count": declared,
        "raw_skin_literal_count": data.count(b"skin_"),
        "layer_paths_found_in_raw_fhpk": raw_paths,
        "layer_archives_present_on_disk": present,
        "present_layer_archive_count": sum(len(value) for value in present.values()),
        "boundary": "FHPK layer paths are an archive-location lead only; they are not treated as an inner logical-path-to-IDX-hash mapping.",
    }


def build_report(documents: Path, historical_root: Path) -> dict:
    resource_dir = documents / "res"
    idx_path = resource_dir / "weapon.idx"
    wpk_path = resource_dir / "weapon3.wpk"
    thx_path = documents / "thd" / "weapon.thx"
    log_path = documents / "loading_records" / "loading_record.bin"
    fhpk_path = documents / "file_hash_pack.bin"
    logical_csv = historical_root / "体验服武器皮肤字符串池索引_002" / "体验服武器皮肤_脚本资源引用.csv"

    logical_summary, logical_rows = valid_py3_logical_rows(logical_csv)
    entries = parse_skpw(idx_path)
    physical = verify_1dpw_entries(entries, resource_dir, "weapon")
    idx_hashes = {entry.resource_hash for entry in entries}
    path_probe = hash_candidates(logical_rows, idx_hashes)
    log_hits = raw_hash_hits(log_path.read_bytes(), idx_hashes)
    fhpk = fhpk_layer_evidence(fhpk_path, [documents.parent, Path(r"E:\lifeafter")])

    sources = [idx_path, wpk_path, thx_path, log_path, fhpk_path]
    source_lock = [
        {"path": str(path), "size": path.stat().st_size, "sha256": sha256_file(path)}
        for path in sources
    ]
    return {
        "audit_version": "physical_bridge_v002",
        "analysis_mode": "read_only_static",
        "source_write_operations": 0,
        "source_lock": source_lock,
        "logical_layer": logical_summary,
        "physical_layer": {
            "idx_path": str(idx_path),
            "idx_sha256": sha256_file(idx_path),
            "wpk_path": str(wpk_path),
            "wpk_sha256": sha256_file(wpk_path),
            "verification": physical,
        },
        "path_to_hash_probe": path_probe,
        "loading_record_exact_idx_hash_probe": log_hits,
        "fhpk_layer_evidence": fhpk,
        "result": {
            "verified_logical_paths": logical_summary["unique_logical_paths"],
            "verified_physical_entities": physical["verified_count"],
            "resolved_path_to_hash_links": path_probe["exact_16_byte_hash_matches"],
            "skin_preview_bindings_created": 0,
            "status": "blocked_missing_demonstrated_path_to_hash_bridge",
            "next_required_artifact": "The resource layer NPK/overlay package or an equivalent native loader mapping that contains logical path plus the exact 16-byte IDX hash.",
            "forbidden_inference": [
                "visual similarity",
                "neighboring IDX index or offset",
                "matching color or dimensions",
                "same resource group alone",
                "filename resemblance",
            ],
        },
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Read-only PC skin physical-bridge audit")
    parser.add_argument("--documents", type=Path, default=DEFAULT_DOCS)
    parser.add_argument("--historical-root", type=Path, default=DEFAULT_HISTORICAL)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    report = build_report(args.documents, args.historical_root)
    args.output.mkdir(parents=True, exist_ok=True)
    report_path = args.output / "physical_bridge_report_v002.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    loaded = json.loads(report_path.read_text(encoding="utf-8"))
    assert loaded["audit_version"] == "physical_bridge_v002"
    assert loaded["result"] == report["result"]
    print(
        json.dumps(
            {
                "report": str(report_path),
                "logical_paths": report["result"]["verified_logical_paths"],
                "physical_entities": report["result"]["verified_physical_entities"],
                "resolved_links": report["result"]["resolved_path_to_hash_links"],
                "status": report["result"]["status"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
