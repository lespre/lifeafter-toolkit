"""Read-only static UTF-8 literal audit for E:\\mrzh script NPK archives.

This program is an archive reader only. It never imports, marshals, compiles,
evaluates, or executes any client/archive payload. It does not enumerate or read
E:\\LifeAfter. All writes are confined to this script's own audit-output folder.

The flag-0 NPK record fields describe the stored encrypted/compressed envelope,
not necessarily the post-deflate output length. Therefore flag-0 AES/raw-deflate
entries are validated by successful bounded raw-deflate completion, rather than by
incorrectly equating the table's stored-size field with decoded byte count.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import os
import struct
import sys
import traceback
import zlib
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, BinaryIO

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

try:
    import zstandard as zstd
except Exception:  # handled explicitly if a flag-12 entry is encountered
    zstd = None

SOURCE_ROOT = Path(r"E:\mrzh")
PROHIBITED_ROOT = Path(r"E:\LifeAfter")
OUT = Path(__file__).resolve().parent

# Required exact UTF-8 literal terms; no normalization, transliteration, or fuzzy match.
TERMS = (
    "极光剑",
    "极光",
    "光剑",
    "帝皇裁决",
    "极光盾",
    "铠甲勇士",
    "帝皇铠甲",
)
TERM_BYTES = {term: term.encode("utf-8") for term in TERMS}

# Existing static audit workflow's package AES key, copied as data only; no target code is imported.
KEY = bytes((
    0x60, 0x63, 0x08, 0xD8, 0xA3, 0x2C, 0x78, 0x20,
    0x13, 0xD2, 0x6C, 0x2F, 0x22, 0x6F, 0x68, 0x6D,
))
RECORD_SIZE = 48
CONTEXT_RADIUS = 80


class DecodeError(RuntimeError):
    """A bounded static decode could not prove a payload is readable."""


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stat_snapshot(path: Path) -> dict[str, int]:
    value = path.stat()
    return {"size": value.st_size, "mtime_ns": value.st_mtime_ns}


def aes_ecb_decrypt(data: bytes) -> bytes:
    """Decrypt complete 16-byte blocks; retain any non-block tail unchanged."""
    complete = (len(data) // 16) * 16
    if not complete:
        return data
    decryptor = Cipher(algorithms.AES(KEY), modes.ECB()).decryptor()
    return decryptor.update(data[:complete]) + decryptor.finalize() + data[complete:]


def raw_deflate_decode(compressed: bytes) -> tuple[bytes, dict[str, Any]]:
    """Decode one raw-deflate stream and require its end marker; preserve tail metadata."""
    decoder = zlib.decompressobj(-zlib.MAX_WBITS)
    try:
        data = decoder.decompress(compressed)
        data += decoder.flush()
    except zlib.error as exc:
        raise DecodeError(f"raw-deflate failed: {exc}") from exc
    if not decoder.eof:
        raise DecodeError("raw-deflate did not reach end-of-stream")
    return data, {
        "raw_deflate_eof": True,
        "raw_deflate_unused_tail_bytes": len(decoder.unused_data),
        "raw_deflate_unconsumed_tail_bytes": len(decoder.unconsumed_tail),
    }


def lz4_block_decode(compressed: bytes, expected_size: int) -> bytes:
    """Strict local LZ4 block reader used for flag-2 records; no code execution."""
    out = bytearray()
    pos = 0

    def extended_length(initial: int) -> int:
        nonlocal pos
        length = initial
        if length == 15:
            while True:
                if pos >= len(compressed):
                    raise DecodeError("LZ4 truncated extended length")
                value = compressed[pos]
                pos += 1
                length += value
                if value != 255:
                    break
        return length

    while pos < len(compressed):
        token = compressed[pos]
        pos += 1
        literal_length = extended_length(token >> 4)
        if pos + literal_length > len(compressed):
            raise DecodeError("LZ4 literal exceeds input")
        out.extend(compressed[pos:pos + literal_length])
        pos += literal_length
        if len(out) > expected_size:
            raise DecodeError("LZ4 output exceeds table decoded-size bound")
        if pos == len(compressed):
            break
        if pos + 2 > len(compressed):
            raise DecodeError("LZ4 missing match offset")
        distance = compressed[pos] | (compressed[pos + 1] << 8)
        pos += 2
        if distance == 0 or distance > len(out):
            raise DecodeError("LZ4 invalid back-reference")
        match_length = extended_length(token & 0x0F) + 4
        source = len(out) - distance
        for _ in range(match_length):
            out.append(out[source])
            source += 1
            if len(out) > expected_size:
                raise DecodeError("LZ4 match exceeds table decoded-size bound")
    if len(out) != expected_size:
        raise DecodeError(f"LZ4 output {len(out)} != table decoded size {expected_size}")
    return bytes(out)


def decode_entry(raw: bytes, table_decoded_size: int, flag: int) -> tuple[bytes, str, dict[str, Any]]:
    """Decode only known archive wrappers. Unknown wrappers are explicitly unreadable."""
    if flag == 2:
        return lz4_block_decode(raw, table_decoded_size), "flag2_lz4_block", {
            "table_decoded_size_bound": table_decoded_size,
        }
    if flag == 12:
        if zstd is None:
            raise DecodeError("flag-12 Zstandard payload but zstandard module unavailable")
        try:
            data = zstd.ZstdDecompressor().decompress(raw, max_output_size=table_decoded_size)
        except Exception as exc:
            raise DecodeError(f"flag-12 zstd failed: {type(exc).__name__}: {exc}") from exc
        if len(data) != table_decoded_size:
            raise DecodeError(f"flag-12 zstd output {len(data)} != table decoded size {table_decoded_size}")
        return data, "flag12_zstd", {"table_decoded_size_bound": table_decoded_size}
    if flag != 0:
        raise DecodeError(f"unsupported NPK entry flag {flag}")

    # Flag 0 normally holds AES-ECB blocks whose plaintext is a small framing header
    # followed by a raw-deflate stream. The table size equals stored size for these rows.
    decrypted = aes_ecb_decrypt(raw)
    if len(decrypted) >= 18:
        frame_kind = struct.unpack_from("<Q", decrypted, 0)[0]
        frame_stored_length = struct.unpack_from("<Q", decrypted, 8)[0]
        zlib_header = decrypted[16:18]
        if frame_kind == 1 and zlib_header in (b"\x78\x01", b"\x78\x9c", b"\x78\xda"):
            data, detail = raw_deflate_decode(decrypted[18:])
            detail.update({
                "frame_kind_u64": frame_kind,
                "frame_stored_length_u64": frame_stored_length,
                "frame_payload_bytes_after_18": len(decrypted) - 18,
                "frame_stored_length_matches_len_minus_19": frame_stored_length == len(decrypted) - 19,
                "zlib_marker_hex": zlib_header.hex(),
                "table_stored_size": table_decoded_size,
            })
            return data, "flag0_aes_ecb_raw_deflate", detail

    # A flag-0 record with no recognized wrapper is still an on-disk raw payload only
    # when its table stored sizes agree. Its status records this lower-level condition.
    if len(raw) != table_decoded_size:
        raise DecodeError(
            f"flag-0 non-wrapper stored length {len(raw)} != table size {table_decoded_size}"
        )
    return raw, "flag0_raw_unwrapped", {"table_stored_size": table_decoded_size}


def discover_archives() -> list[Path]:
    """Find every .npk whose filename contains 'script', below E:\mrzh only."""
    root_real = os.path.normcase(os.path.abspath(str(SOURCE_ROOT)))
    prohibited_real = os.path.normcase(os.path.abspath(str(PROHIBITED_ROOT)))
    found: list[Path] = []
    for directory, dirnames, filenames in os.walk(SOURCE_ROOT, followlinks=False):
        # Never follow reparse/symlink targets; do not descend a LifeAfter-named branch.
        dirnames[:] = [
            name for name in dirnames
            if "lifeafter" not in name.casefold()
            and not os.path.islink(os.path.join(directory, name))
        ]
        for filename in filenames:
            lower = filename.casefold()
            if not (lower.endswith(".npk") and "script" in lower):
                continue
            path = Path(directory) / filename
            absolute = os.path.normcase(os.path.abspath(str(path)))
            if absolute == prohibited_real or absolute.startswith(prohibited_real + os.sep):
                raise RuntimeError(f"prohibited path rejected: {path}")
            if not absolute.startswith(root_real + os.sep):
                raise RuntimeError(f"out-of-scope path rejected: {path}")
            if path.is_symlink() or not path.is_file():
                continue
            found.append(path)
    return sorted(found, key=lambda item: str(item).casefold())


def parse_header_and_records(handle: BinaryIO, package_size: int) -> tuple[dict[str, Any], list[tuple[int, int, int, int, int, int, int, int, str]]]:
    header_raw = handle.read(32)
    if len(header_raw) != 32:
        raise DecodeError(f"short encrypted NPK header: {len(header_raw)} bytes")
    header = aes_ecb_decrypt(header_raw)
    header_u64, magic_u32, version, table_offset, entry_count = struct.unpack_from("<QIIII", header, 0)
    table_bytes = entry_count * RECORD_SIZE
    if table_offset < 0 or table_offset + table_bytes > package_size:
        raise DecodeError(
            f"directory bounds invalid: offset={table_offset} entries={entry_count} size={package_size}"
        )
    handle.seek(table_offset)
    table_raw = handle.read(table_bytes)
    if len(table_raw) != table_bytes:
        raise DecodeError(f"short encrypted directory: expected {table_bytes}, got {len(table_raw)}")
    table = aes_ecb_decrypt(table_raw)
    records: list[tuple[int, int, int, int, int, int, int, int, str]] = []
    for entry_index in range(entry_count):
        start = entry_index * RECORD_SIZE
        record = table[start:start + RECORD_SIZE]
        file_id, packed_offset, packed_size, table_decoded_size, check_a, check_b, flag = struct.unpack_from(
            "<QIIIIIi", record, 0
        )
        records.append((
            packed_offset,
            entry_index,
            file_id,
            packed_size,
            table_decoded_size,
            check_a,
            check_b,
            flag,
            record[32:48].hex(),
        ))
    header_meta = {
        "header_u64": header_u64,
        "header_magic_u32": magic_u32,
        "version": version,
        "table_offset": table_offset,
        "entry_count": entry_count,
        "table_bytes": table_bytes,
        "table_sha256_after_static_aes": hashlib.sha256(table).hexdigest(),
    }
    # Sequential source reads materially reduce disk seek churn; entry_index is retained.
    records.sort(key=lambda value: (value[0], value[1]))
    return header_meta, records


def embedded_logical_path(data: bytes) -> tuple[str, str]:
    """Recover an in-payload path only when its length framing and strict UTF-8 validate."""
    for offset in (0, 1, 2):
        if len(data) < offset + 6:
            continue
        tagged = data[offset:offset + 2] in (b"tI", b"sI")
        length_offset = offset + 2 if tagged else offset
        start = offset + 6 if tagged else offset + 4
        length = struct.unpack_from("<I", data, length_offset)[0]
        if not (0 < length <= 16384 and start + length <= len(data)):
            continue
        raw = data[start:start + length]
        try:
            value = raw.decode("utf-8", "strict")
        except UnicodeDecodeError:
            continue
        if not ("\\" in value or "/" in value or value.endswith((".py", ".nxs", ".pyc"))):
            continue
        if any(ord(char) < 32 and char not in "\r\n\t" for char in value):
            continue
        evidence = f"embedded_{'tagged_' if tagged else ''}length_prefixed_utf8_offset_{offset}"
        return value, evidence
    return "", "unavailable_no_valid_embedded_utf8_path"


def murmur3_x86_32(data: bytes, seed: int) -> int:
    c1 = 0xCC9E2D51
    c2 = 0x1B873593
    state = seed & 0xFFFFFFFF
    boundary = len(data) & ~3
    for offset in range(0, boundary, 4):
        value = int.from_bytes(data[offset:offset + 4], "little")
        value = (value * c1) & 0xFFFFFFFF
        value = ((value << 15) | (value >> 17)) & 0xFFFFFFFF
        value = (value * c2) & 0xFFFFFFFF
        state ^= value
        state = ((state << 13) | (state >> 19)) & 0xFFFFFFFF
        state = (state * 5 + 0xE6546B64) & 0xFFFFFFFF
    tail = data[boundary:]
    value = 0
    if len(tail) >= 3:
        value ^= tail[2] << 16
    if len(tail) >= 2:
        value ^= tail[1] << 8
    if len(tail) >= 1:
        value ^= tail[0]
        value = (value * c1) & 0xFFFFFFFF
        value = ((value << 15) | (value >> 17)) & 0xFFFFFFFF
        value = (value * c2) & 0xFFFFFFFF
        state ^= value
    state ^= len(data)
    state ^= state >> 16
    state = (state * 0x85EBCA6B) & 0xFFFFFFFF
    state ^= state >> 13
    state = (state * 0xC2B2AE35) & 0xFFFFFFFF
    state ^= state >> 16
    return state & 0xFFFFFFFF


def path_file_id(path: str) -> int:
    encoded = path.encode("utf-8")
    low = murmur3_x86_32(encoded, 0x66666666)
    high = murmur3_x86_32(encoded, 0x77777777)
    return (high << 32) | low


def file_id_path_validation(path: str, file_id: int) -> dict[str, Any]:
    candidates = [path]
    if path.casefold().endswith(".py"):
        candidates.append(path[:-3] + ".nxs")
    if path.casefold().endswith(".pyc"):
        candidates.append(path[:-4] + ".nxs")
    for candidate in candidates:
        calculated = path_file_id(candidate)
        if calculated == file_id:
            return {
                "validated": True,
                "hash_input_path": candidate,
                "algorithm": "dual_MurmurHash3_x86_32(seeds_0x77777777||0x66666666)",
            }
    return {
        "validated": False,
        "candidates_tested": candidates,
        "algorithm": "dual_MurmurHash3_x86_32(seeds_0x77777777||0x66666666)",
    }


def display_context(value: bytes) -> str:
    """UTF-8 display that retains invalid/control byte evidence in explicit escapes."""
    text = value.decode("utf-8", "surrogateescape")
    out: list[str] = []
    for char in text:
        code = ord(char)
        if 0xDC80 <= code <= 0xDCFF:
            out.append(f"\\x{code - 0xDC00:02x}")
        elif code < 32 or code == 127:
            out.append(f"\\x{code:02x}")
        else:
            out.append(char)
    return "".join(out)


def literal_hits(data: bytes, term: str) -> list[dict[str, Any]]:
    needle = TERM_BYTES[term]
    result: list[dict[str, Any]] = []
    search_from = 0
    while True:
        offset = data.find(needle, search_from)
        if offset < 0:
            return result
        context_start = max(0, offset - CONTEXT_RADIUS)
        context_end = min(len(data), offset + len(needle) + CONTEXT_RADIUS)
        context = data[context_start:context_end]
        result.append({
            "term": term,
            "term_utf8_hex": needle.hex(),
            "match_offset_in_decoded_payload": offset,
            "match_end_offset_exclusive": offset + len(needle),
            "context_start_offset": context_start,
            "context_end_offset_exclusive": context_end,
            "context_utf8_display": display_context(context),
            "context_hex": context.hex(),
        })
        # Advance one byte deliberately so overlapping byte occurrences are not suppressed.
        search_from = offset + 1


def write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def scan_package(path: Path, source_sha256: str, coverage_writer: csv.DictWriter[str],
                 unreadable_writer: csv.DictWriter[str], path_index: dict[int, set[str]],
                 package_record: dict[str, Any], preliminary_hits: list[dict[str, Any]]) -> None:
    package_size = path.stat().st_size
    package_record.update({
        "path": str(path),
        "source_package_sha256": source_sha256,
        "source_size": package_size,
        "table_parse_status": "not_started",
        "entries_declared": 0,
        "entries_table_valid": 0,
        "entries_scanned": 0,
        "entries_decoded": 0,
        "entries_unreadable": 0,
        "decoded_payload_bytes_scanned": 0,
        "hit_occurrences": 0,
        "decoder_strategy_counts": {},
        "error_examples": [],
    })
    strategies: Counter[str] = Counter()
    try:
        with path.open("rb") as handle:
            header, records = parse_header_and_records(handle, package_size)
            package_record.update(header)
            package_record["table_parse_status"] = "ok"
            package_record["entries_declared"] = header["entry_count"]
            package_record["entries_table_valid"] = len(records)
            for ordinal, record in enumerate(records, start=1):
                (packed_offset, entry_index, file_id, packed_size, table_decoded_size,
                 check_a, check_b, flag, record_tail_hex) = record
                file_id_hex = f"{file_id:016X}"
                base = {
                    "source_package": str(path),
                    "source_package_sha256": source_sha256,
                    "package_version": header["version"],
                    "entry_index": entry_index,
                    "file_id": file_id_hex,
                    "packed_payload_offset_in_archive": packed_offset,
                    "packed_size": packed_size,
                    "table_decoded_size_field": table_decoded_size,
                    "table_check_a": check_a,
                    "table_check_b": check_b,
                    "flag": flag,
                    "record_unused_tail_hex": record_tail_hex,
                    "embedded_logical_path": "",
                    "embedded_path_evidence": "",
                    "decoder_strategy": "",
                    "decode_status": "",
                    "decoded_payload_size": "",
                    "decoded_payload_sha256_if_hit": "",
                    "matched_terms": "",
                    "match_occurrence_count": 0,
                    "error": "",
                }
                package_record["entries_scanned"] += 1
                if packed_offset < 0 or packed_size < 0 or packed_offset + packed_size > package_size:
                    message = f"payload out of bounds: offset={packed_offset} size={packed_size} package_size={package_size}"
                    base.update({"decode_status": "unreadable", "error": message})
                    coverage_writer.writerow(base)
                    unreadable_writer.writerow(base)
                    package_record["entries_unreadable"] += 1
                    if len(package_record["error_examples"]) < 20:
                        package_record["error_examples"].append({"entry_index": entry_index, "file_id": file_id_hex, "error": message})
                    continue
                try:
                    handle.seek(packed_offset)
                    raw = handle.read(packed_size)
                    if len(raw) != packed_size:
                        raise DecodeError(f"short payload read: expected {packed_size}, got {len(raw)}")
                    decoded, strategy, details = decode_entry(raw, table_decoded_size, flag)
                    logical_path, path_evidence = embedded_logical_path(decoded)
                    if logical_path:
                        path_index[file_id].add(logical_path)
                    term_occurrences: list[dict[str, Any]] = []
                    for term in TERMS:
                        term_occurrences.extend(literal_hits(decoded, term))
                    if term_occurrences:
                        decoded_sha256 = hashlib.sha256(decoded).hexdigest()
                        for match in term_occurrences:
                            preliminary_hits.append({
                                **base,
                                "decoded_payload_size": len(decoded),
                                "decoded_payload_sha256_if_hit": decoded_sha256,
                                "embedded_logical_path": logical_path,
                                "embedded_path_evidence": path_evidence,
                                "decoder_strategy": strategy,
                                "decode_status": "decoded_scanned",
                                "decoder_details": details,
                                **match,
                            })
                    counts = Counter(item["term"] for item in term_occurrences)
                    base.update({
                        "embedded_logical_path": logical_path,
                        "embedded_path_evidence": path_evidence,
                        "decoder_strategy": strategy,
                        "decode_status": "decoded_scanned",
                        "decoded_payload_size": len(decoded),
                        "matched_terms": json.dumps(dict(sorted(counts.items())), ensure_ascii=False, separators=(",", ":")),
                        "match_occurrence_count": len(term_occurrences),
                    })
                    coverage_writer.writerow(base)
                    package_record["entries_decoded"] += 1
                    package_record["decoded_payload_bytes_scanned"] += len(decoded)
                    package_record["hit_occurrences"] += len(term_occurrences)
                    strategies[strategy] += 1
                except Exception as exc:
                    message = f"{type(exc).__name__}: {exc}"
                    base.update({"decode_status": "unreadable", "error": message})
                    coverage_writer.writerow(base)
                    unreadable_writer.writerow(base)
                    package_record["entries_unreadable"] += 1
                    if len(package_record["error_examples"]) < 20:
                        package_record["error_examples"].append({"entry_index": entry_index, "file_id": file_id_hex, "error": message})
                if ordinal % 1000 == 0:
                    # Persist evidence periodically without retaining/archive-writing any payload.
                    coverage_writer.writerows([])
                    sys.stdout.write(f"[{path.name}] {ordinal}/{len(records)} entries\n")
                    sys.stdout.flush()
            package_record["decoder_strategy_counts"] = dict(sorted(strategies.items()))
    except Exception as exc:
        package_record["table_parse_status"] = "unreadable"
        package_record["package_error"] = f"{type(exc).__name__}: {exc}"
        package_record["traceback"] = traceback.format_exc(limit=4)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    scanner_path = Path(__file__).resolve()
    coverage_path = OUT / "脚本NPK_entry覆盖清单_002.csv"
    unreadable_path = OUT / "脚本NPK_无法解码条目_002.csv"
    hits_path = OUT / "极光剑_UTF8命中上下文_002.csv"
    term_summary_path = OUT / "极光剑_词项扫描汇总_002.csv"
    report_path = OUT / "体验服脚本_极光剑全文静态扫描_002.json"
    readme_path = OUT / "README_审计边界与修订说明_002.md"

    discovered = discover_archives()
    if not discovered:
        raise RuntimeError("No script*.npk archive found below E:\\mrzh")

    # Compute live source SHA-256 before package reads. This is the provenance value
    # emitted for every matching entry in the final evidence table.
    source_hashes = {str(path): sha256_path(path) for path in discovered}
    source_stats_before = {str(path): stat_snapshot(path) for path in discovered}

    coverage_fields = [
        "source_package", "source_package_sha256", "package_version", "entry_index", "file_id",
        "packed_payload_offset_in_archive", "packed_size", "table_decoded_size_field", "table_check_a",
        "table_check_b", "flag", "record_unused_tail_hex", "embedded_logical_path", "embedded_path_evidence",
        "decoder_strategy", "decode_status", "decoded_payload_size", "decoded_payload_sha256_if_hit",
        "matched_terms", "match_occurrence_count", "error",
    ]
    hit_fields = [
        "term", "term_utf8_hex", "source_package", "source_package_sha256", "package_version",
        "entry_index", "file_id", "logical_path", "logical_path_resolution",
        "logical_path_file_id_validation", "packed_payload_offset_in_archive", "packed_size",
        "table_decoded_size_field", "flag", "decoder_strategy", "decoded_payload_size",
        "decoded_payload_sha256", "match_offset_in_decoded_payload", "match_end_offset_exclusive",
        "context_start_offset", "context_end_offset_exclusive", "context_utf8_display", "context_hex",
    ]

    path_index: dict[int, set[str]] = defaultdict(set)
    preliminary_hits: list[dict[str, Any]] = []
    packages: list[dict[str, Any]] = []
    with coverage_path.open("w", encoding="utf-8-sig", newline="") as coverage_handle, \
         unreadable_path.open("w", encoding="utf-8-sig", newline="") as unreadable_handle:
        coverage_writer = csv.DictWriter(coverage_handle, fieldnames=coverage_fields, extrasaction="ignore")
        unreadable_writer = csv.DictWriter(unreadable_handle, fieldnames=coverage_fields, extrasaction="ignore")
        coverage_writer.writeheader()
        unreadable_writer.writeheader()
        for package_path in discovered:
            package = {}
            scan_package(
                package_path,
                source_hashes[str(package_path)],
                coverage_writer,
                unreadable_writer,
                path_index,
                package,
                preliminary_hits,
            )
            coverage_handle.flush()
            unreadable_handle.flush()
            packages.append(package)
            print(json.dumps({
                "package": str(package_path),
                "table_parse_status": package.get("table_parse_status"),
                "entries_declared": package.get("entries_declared"),
                "entries_decoded": package.get("entries_decoded"),
                "entries_unreadable": package.get("entries_unreadable"),
                "hit_occurrences": package.get("hit_occurrences"),
            }, ensure_ascii=False), flush=True)

    source_stats_after = {str(path): stat_snapshot(path) for path in discovered}
    source_stat_stable = all(source_stats_before[str(path)] == source_stats_after[str(path)] for path in discovered)

    final_hits: list[dict[str, Any]] = []
    for hit in preliminary_hits:
        file_id = int(hit["file_id"], 16)
        direct_path = hit["embedded_logical_path"]
        candidate_paths = sorted(path_index.get(file_id, set()))
        if direct_path:
            logical_path = direct_path
            resolution = hit["embedded_path_evidence"]
        elif len(candidate_paths) == 1:
            logical_path = candidate_paths[0]
            resolution = "same_file_id_cross_archive_embedded_path"
        elif len(candidate_paths) > 1:
            logical_path = ""
            resolution = "unavailable_multiple_cross_archive_paths_for_file_id"
        else:
            logical_path = ""
            resolution = "unavailable_no_embedded_path_for_file_id"
        validation = file_id_path_validation(logical_path, file_id) if logical_path else {
            "validated": False,
            "reason": "no logical path available",
        }
        final_hits.append({
            "term": hit["term"],
            "term_utf8_hex": hit["term_utf8_hex"],
            "source_package": hit["source_package"],
            "source_package_sha256": hit["source_package_sha256"],
            "package_version": hit["package_version"],
            "entry_index": hit["entry_index"],
            "file_id": hit["file_id"],
            "logical_path": logical_path,
            "logical_path_resolution": resolution,
            "logical_path_file_id_validation": json.dumps(validation, ensure_ascii=False, separators=(",", ":")),
            "packed_payload_offset_in_archive": hit["packed_payload_offset_in_archive"],
            "packed_size": hit["packed_size"],
            "table_decoded_size_field": hit["table_decoded_size_field"],
            "flag": hit["flag"],
            "decoder_strategy": hit["decoder_strategy"],
            "decoded_payload_size": hit["decoded_payload_size"],
            "decoded_payload_sha256": hit["decoded_payload_sha256_if_hit"],
            "match_offset_in_decoded_payload": hit["match_offset_in_decoded_payload"],
            "match_end_offset_exclusive": hit["match_end_offset_exclusive"],
            "context_start_offset": hit["context_start_offset"],
            "context_end_offset_exclusive": hit["context_end_offset_exclusive"],
            "context_utf8_display": hit["context_utf8_display"],
            "context_hex": hit["context_hex"],
        })
    final_hits.sort(key=lambda row: (TERMS.index(row["term"]), row["source_package"].casefold(), int(row["entry_index"]), int(row["match_offset_in_decoded_payload"])))
    write_csv_rows(hits_path, hit_fields, final_hits)

    declared_total = sum(int(package.get("entries_declared", 0)) for package in packages)
    table_valid_total = sum(int(package.get("entries_table_valid", 0)) for package in packages)
    scanned_total = sum(int(package.get("entries_scanned", 0)) for package in packages)
    decoded_total = sum(int(package.get("entries_decoded", 0)) for package in packages)
    unreadable_total = sum(int(package.get("entries_unreadable", 0)) for package in packages)
    bytes_scanned_total = sum(int(package.get("decoded_payload_bytes_scanned", 0)) for package in packages)
    package_parse_ok = all(package.get("table_parse_status") == "ok" for package in packages)
    coverage_complete = (
        package_parse_ok
        and source_stat_stable
        and declared_total == table_valid_total == scanned_total == decoded_total
        and unreadable_total == 0
    )

    hits_by_term: dict[str, list[dict[str, Any]]] = {term: [] for term in TERMS}
    for hit in final_hits:
        hits_by_term[hit["term"]].append(hit)
    term_rows: list[dict[str, Any]] = []
    for term in TERMS:
        occurrences = hits_by_term[term]
        if occurrences:
            status = "hit_in_decoded_entries" if coverage_complete else "hit_in_decoded_entries_coverage_incomplete"
        else:
            status = "no_hit_all_entries_decoded" if coverage_complete else "no_hit_in_decoded_entries_coverage_incomplete"
        term_rows.append({
            "term": term,
            "term_utf8_hex": TERM_BYTES[term].hex(),
            "occurrence_count": len(occurrences),
            "distinct_entry_count": len({(item["source_package"], item["entry_index"]) for item in occurrences}),
            "status": status,
            "interpretation_boundary": "Literal-byte evidence only; a hit does not assert item identity, item linkage, or new-release status.",
        })
    write_csv_rows(
        term_summary_path,
        ["term", "term_utf8_hex", "occurrence_count", "distinct_entry_count", "status", "interpretation_boundary"],
        term_rows,
    )

    generated_hashes = {
        "scanner_source_sha256": sha256_path(scanner_path),
        "entry_coverage_csv_sha256": sha256_path(coverage_path),
        "unreadable_entries_csv_sha256": sha256_path(unreadable_path),
        "hit_context_csv_sha256": sha256_path(hits_path),
        "term_summary_csv_sha256": sha256_path(term_summary_path),
    }
    with coverage_path.open("r", encoding="utf-8-sig", newline="") as handle:
        coverage_row_count = sum(1 for _ in csv.DictReader(handle))
    with unreadable_path.open("r", encoding="utf-8-sig", newline="") as handle:
        unreadable_row_count = sum(1 for _ in csv.DictReader(handle))
    with hits_path.open("r", encoding="utf-8-sig", newline="") as handle:
        hit_row_count = sum(1 for _ in csv.DictReader(handle))

    primary = next(row for row in term_rows if row["term"] == "极光剑")
    generic = next(row for row in term_rows if row["term"] == "极光")
    if primary["occurrence_count"]:
        primary_conclusion = "Found literal UTF-8 occurrences of 极光剑; consult the hit-context CSV. No item mapping is asserted."
    elif coverage_complete:
        primary_conclusion = "No literal UTF-8 occurrence of 极光剑 was found in any decoded entry of all discovered script NPK archives."
    else:
        primary_conclusion = "No literal UTF-8 occurrence of 极光剑 was found in decoded entries, but one or more archive entries were not decodable; absence is not conclusive."

    report = {
        "audit_id": "极光剑存在性核查_001_static_utf8_revision_002",
        "created_utc": utc_now(),
        "analysis_mode": "read_only_static_archive_decode_then_exact_UTF8_bytes_scan",
        "scope": {
            "source_root": str(SOURCE_ROOT),
            "archive_discovery_rule": "Every non-symlink .npk below E:\\mrzh whose filename contains script (case-insensitive).",
            "prohibited_root_not_enumerated_or_read": str(PROHIBITED_ROOT),
            "client_or_archive_payload_execution": False,
            "client_or_archive_payload_import": False,
            "source_write_operations": 0,
            "output_writes_confined_to": str(OUT),
        },
        "required_terms": [{"term": term, "utf8_hex": TERM_BYTES[term].hex()} for term in TERMS],
        "source_packages": packages,
        "source_hash_snapshot_before_scan": source_hashes,
        "source_stat_before_scan": source_stats_before,
        "source_stat_after_scan": source_stats_after,
        "source_stat_stable_during_scan": source_stat_stable,
        "coverage": {
            "candidate_archive_count": len(discovered),
            "candidate_archives": [str(path) for path in discovered],
            "entries_declared_total": declared_total,
            "entries_table_valid_total": table_valid_total,
            "entries_scanned_total": scanned_total,
            "entries_decoded_total": decoded_total,
            "entries_unreadable_total": unreadable_total,
            "decoded_payload_bytes_scanned_total": bytes_scanned_total,
            "coverage_complete_for_absence_claims": coverage_complete,
            "entry_coverage_csv": str(coverage_path),
            "entry_coverage_csv_rows": coverage_row_count,
            "unreadable_entries_csv": str(unreadable_path),
            "unreadable_entries_csv_rows": unreadable_row_count,
        },
        "term_results": term_rows,
        "hit_evidence": {
            "hit_context_csv": str(hits_path),
            "hit_context_csv_rows": hit_row_count,
            "logical_path_rule": "Use in-payload strict UTF-8 length-framed path where available; otherwise only a unique same-file-ID path observed in another decoded E:\\mrzh script archive. Ambiguous or absent paths remain unavailable.",
            "file_id_validation_rule": "When a path is available, independently test the dual MurmurHash3 x86_32 file-ID convention against path and .nxs suffix variant; validation result is preserved per hit.",
            "no_string_adjacency_item_mapping": True,
        },
        "integrity": generated_hashes,
        "conclusion": {
            "primary_term": "极光剑",
            "primary_term_occurrences": primary["occurrence_count"],
            "primary_conclusion": primary_conclusion,
            "generic_term": "极光",
            "generic_term_occurrences": generic["occurrence_count"],
            "generic_term_boundary": "Generic 极光 hits are literal observations only. They are not linked to an item, weapon, skin, or new release by proximity to other strings.",
            "other_required_terms_without_hits": [
                row["term"] for row in term_rows if row["term"] != "极光" and row["occurrence_count"] == 0
            ],
        },
        "revision_note": {
            "retained_prior_file": "体验服脚本_极光剑全文静态扫描_001.json",
            "reason_for_revision": "The retained prior artifact treated flag-0 table stored size as post-raw-deflate decoded length, yielding false decode failures. This revision verifies successful raw-deflate end-of-stream and records real decoded sizes instead.",
        },
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    readme = f"""# 体验服“极光剑”静态 UTF-8 存在性核查（修订 002）

## 范围与约束

- 原始读取范围仅为 `{SOURCE_ROOT}` 下文件名含 `script` 的 `.npk`，共 `{len(discovered)}` 包。
- 未枚举、未读取 `{PROHIBITED_ROOT}`；未启动客户端；未导入、反序列化、编译或执行任何客户端/归档条目。
- 归档目录与每个条目仅作静态 AES/压缩封装解码，再对**解码后的原始字节**作所列 UTF-8 字面量搜索。
- 所有本次写入都局限在本目录；`E:\\mrzh` 写入次数为 0。

## 覆盖

- 目录声明条目：`{declared_total}`
- 已静态解码并扫描条目：`{decoded_total}`
- 无法解码条目：`{unreadable_total}`
- 解码后扫描字节：`{bytes_scanned_total}`
- 是否可作全量未命中结论：`{coverage_complete}`

完整逐条覆盖清单：`{coverage_path.name}`；无法解码条目（如有）：`{unreadable_path.name}`。

## 结论边界

{primary_conclusion}

`极光` 的字面量命中数为 `{generic['occurrence_count']}`。这不构成“极光剑”、某个道具、武器皮肤或新上线内容的映射。**没有使用字符串相邻性、同一字符串池槽位、目录邻近性或视觉相似性来作 item 映射。**

完整逐命中偏移、file ID、logical path、源包 SHA-256 和上下文：`{hits_path.name}`；全部词项状态：`{term_summary_path.name}`。

## 修订原因

保留旧文件 `体验服脚本_极光剑全文静态扫描_001.json` 以保持审计可追溯性。其 flag-0 条目把 NPK 表中的存储大小错误地当成 raw-deflate 解压后的输出大小，产生大量伪“无法解码”。本修订用 raw-deflate 流的成功结束标记验证这类条目，记录实际输出长度，并将真正无法解码的条目单列。
"""
    readme_path.write_text(readme, encoding="utf-8")

    # Final output-contract checks.
    loaded = json.loads(report_path.read_text(encoding="utf-8"))
    if loaded["coverage"]["entry_coverage_csv_rows"] != loaded["coverage"]["entries_scanned_total"]:
        raise RuntimeError("output validation failed: coverage row count != scanned entry count")
    if loaded["coverage"]["unreadable_entries_csv_rows"] != loaded["coverage"]["entries_unreadable_total"]:
        raise RuntimeError("output validation failed: unreadable row count mismatch")
    if loaded["hit_evidence"]["hit_context_csv_rows"] != len(final_hits):
        raise RuntimeError("output validation failed: hit row count mismatch")
    print(json.dumps({
        "report": str(report_path),
        "coverage_complete": coverage_complete,
        "archives": len(discovered),
        "entries_declared": declared_total,
        "entries_decoded": decoded_total,
        "entries_unreadable": unreadable_total,
        "hit_rows": len(final_hits),
        "term_occurrences": {row["term"]: row["occurrence_count"] for row in term_rows},
    }, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
