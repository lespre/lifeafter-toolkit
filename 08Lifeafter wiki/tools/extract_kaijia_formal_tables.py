#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract only the formal-client tables needed for the Kaijia lottery trace.

The source NPK is read-only.  The output is a content-addressed, targeted
workcopy with an explicit manifest; it refuses to merge into an existing
nonempty directory.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import struct
from pathlib import Path
from typing import Any

FORMAL_SOURCE = Path(r"E:\LifeAfter\Documents\script.py314.lc.npk")
FORMAL_SHA256 = "79c0d06f53db02ca4f8ebad97da2cfef22916f963e8cae3461b914d4a39bb85d"
DEFAULT_OUTPUT = Path(
    r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_79c0d06f53db"
)
READER_PATH = Path(
    r"E:\la拆包项目\01拆包器本体\工具库\01_核心解包器\npk_reader.py"
)

# FIDs are verified stable in the official 79c0 package before this extractor
# is allowed to write a workcopy.
TARGETS = {
    "common_lottery_conf_data": "57CB7B9B13B6ED5A",
    "common_lottery_conf_data_chs": "004E1C024F5B3BF9",
    "super_fashion_lottery_conf_data": "7E5A5A83B1F07D31",
    "super_fashion_lottery_conf_data_chs": "512C733C3B263D37",
    "fashion_sale_conf_data": "0E69DCD5072F52FC",
    "fashion_sale_conf_data_chs": "140DF9C194B217A7",
    "reward_pool_data_base": "D558884A36C972C5",
    "reward_pool_data_base_chs": "69E58821939CB515",
}


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_reader() -> Any:
    if not READER_PATH.is_file():
        raise FileNotFoundError(f"NPK reader missing: {READER_PATH}")
    spec = importlib.util.spec_from_file_location("lifeafter_npk_reader", READER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load NPK reader module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def extract(source: Path, output: Path) -> dict[str, Any]:
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"refuse to mix with existing workcopy: {output}")
    if not source.is_file():
        raise FileNotFoundError(f"formal source missing: {source}")

    before_sha = sha256_path(source)
    if before_sha != FORMAL_SHA256:
        raise RuntimeError(
            "formal source SHA changed; do not reuse this targeted-table definition: "
            f"{before_sha}"
        )

    reader = load_reader()
    output.mkdir(parents=True, exist_ok=False)
    entries_dir = output / "entries"
    entries_dir.mkdir()
    report_entries: list[dict[str, Any]] = []

    with source.open("rb") as stream:
        header = reader.aes_ecb(stream.read(64))
        if len(header) < 24 or header[8:12] != b"NXPK":
            raise ValueError("source does not have a valid NXPK header")
        table_offset, entry_count = struct.unpack_from("<II", header, 16)
        stream.seek(table_offset)
        table = reader.aes_ecb(stream.read(entry_count * 48))
        if len(table) != entry_count * 48:
            raise ValueError("short decrypted NXPK entry table")
        index_by_fid = {
            f"{struct.unpack_from('<Q', table, index * 48)[0]:016X}": index
            for index in range(entry_count)
        }

        for name, fid in TARGETS.items():
            index = index_by_fid.get(fid)
            if index is None:
                raise KeyError(f"target FID missing from formal source: {name} {fid}")
            entry = table[index * 48:(index + 1) * 48]
            _file_id, archive_offset, packed_size, declared_size, _a, _b, flag = (
                struct.unpack_from("<QIIIIIi", entry)
            )
            if archive_offset <= 0 or packed_size <= 0:
                raise ValueError(f"invalid source entry bounds: {name}")
            stream.seek(archive_offset)
            packed = stream.read(packed_size)
            if len(packed) != packed_size:
                raise ValueError(f"short packed read: {name}")
            payload = reader.unpack_entry(packed, declared_size, flag)
            relative_path = Path("entries") / f"{index:06d}.bin"
            (output / relative_path).write_bytes(payload)
            report_entries.append({
                "name": name,
                "index": index,
                "file_id": fid,
                "archive_offset": archive_offset,
                "packed_size": packed_size,
                "declared_size": declared_size,
                "flag": flag,
                "packed_sha256": hashlib.sha256(packed).hexdigest(),
                "output_file": str(relative_path).replace("\\", "/"),
                "actual_output_size": len(payload),
                "output_sha256": hashlib.sha256(payload).hexdigest(),
                "xbrace_offset": payload.find(b"x{"),
            })

    after_sha = sha256_path(source)
    if after_sha != before_sha:
        raise RuntimeError("formal source changed while extracting; workcopy is invalid")
    report = {
        "schema": "lifeafter-kaijia-formal-targeted-workcopy-v1",
        "source": {"path": str(source), "sha256": after_sha, "unchanged": True},
        "target_count": len(TARGETS),
        "entries": report_entries,
    }
    (output / "manifest.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=FORMAL_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = extract(args.source, args.output)
    print(json.dumps({
        "source_sha256": report["source"]["sha256"],
        "target_count": report["target_count"],
        "output": str(args.output),
        "entries": [{"name": e["name"], "index": e["index"], "bytes": e["actual_output_size"]}
                    for e in report["entries"]],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
