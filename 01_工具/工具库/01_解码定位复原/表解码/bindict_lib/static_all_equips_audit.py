"""Read-only static audit of E:\\mrzh all_equips_data variants.

This program deliberately does not import, marshal, compile, eval, exec, or
otherwise run a game payload.  It reads only explicitly named script archives
under E:\\mrzh and writes derived evidence only under its own audit directory.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import struct
import sys
import zlib
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

try:
    import zstandard as zstd
except ImportError:  # retained as a recorded decode limitation if encountered
    zstd = None

SOURCE_ROOT = Path(r"E:\mrzh")
FORBIDDEN_ROOT_TEXT = r"E:\LifeAfter"
OUT = Path(__file__).resolve().parent

# Explicit, non-recursive inventory: no other drive or client tree is visited.
ARCHIVE_SPECS = (
    ("root_legacy", SOURCE_ROOT / "script.npk"),
    ("documents_legacy", SOURCE_ROOT / "Documents" / "script.npk"),
    ("documents_py3", SOURCE_ROOT / "Documents" / "script.py3.npk"),
    ("documents_py314", SOURCE_ROOT / "Documents" / "script.py314.lc.npk"),
)

KEY = bytes((
    0x60, 0x63, 0x08, 0xD8, 0xA3, 0x2C, 0x78, 0x20,
    0x13, 0xD2, 0x6C, 0x2F, 0x22, 0x6F, 0x68, 0x6D,
))
TARGET_FILE_ID = "0F92F8F525E6D201"
TOKEN = b"all_equips_data"
AUG_TERMS = (
    "AUG",
    "AUG突击步枪",
    "AUG突击体验版",
    "AUG突击典藏版",
    "AUG突击雨战版",
    "AUG突击雪地版",
    "需要生存等级120才能使用",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def ensure_allowed_source(path: Path) -> Path:
    """Canonical allowed-root guard; source files are never opened before this."""
    root = SOURCE_ROOT.resolve(strict=True)
    resolved = path.resolve(strict=True)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise RuntimeError(f"source escapes allowed root: {resolved}") from exc
    # Text-only guard avoids any probing of the prohibited root.
    if str(resolved).casefold().startswith(FORBIDDEN_ROOT_TEXT.casefold()):
        raise RuntimeError("prohibited root rejected")
    return resolved


def aes_ecb(data: bytes) -> bytes:
    usable = len(data) // 16 * 16
    if not usable:
        return data
    decryptor = Cipher(algorithms.AES(KEY), modes.ECB()).decryptor()
    return decryptor.update(data[:usable]) + decryptor.finalize() + data[usable:]


def lz4_block(blob: bytes, expected: int) -> bytes:
    """Small zero-execution LZ4 block reader used only for NPK entry bytes."""
    output = bytearray()
    cursor = 0

    def extension(value: int) -> int:
        nonlocal cursor
        if value == 15:
            while True:
                if cursor >= len(blob):
                    raise ValueError("lz4 extension truncated")
                part = blob[cursor]
                cursor += 1
                value += part
                if part != 255:
                    break
        return value

    while cursor < len(blob) and len(output) < expected:
        token = blob[cursor]
        cursor += 1
        literal_len = extension(token >> 4)
        if cursor + literal_len > len(blob):
            raise ValueError("lz4 literal exceeds input")
        output.extend(blob[cursor:cursor + literal_len])
        cursor += literal_len
        if cursor >= len(blob):
            break
        if cursor + 2 > len(blob):
            raise ValueError("lz4 offset truncated")
        distance = blob[cursor] | (blob[cursor + 1] << 8)
        cursor += 2
        if distance == 0 or distance > len(output):
            raise ValueError("lz4 invalid distance")
        match_len = extension(token & 15) + 4
        source = len(output) - distance
        for _ in range(match_len):
            output.append(output[source])
            source += 1
    if len(output) != expected:
        raise ValueError(f"lz4 output {len(output)} != expected {expected}")
    return bytes(output)


def unpack_entry(packed: bytes, expected_size: int, flag: int) -> tuple[bytes, dict[str, Any]]:
    """Static byte transforms only; returns a decoder trace, never an object."""
    if flag == 2:
        return lz4_block(packed, expected_size), {
            "strategy": "lz4_block", "codec_complete": True,
        }
    if flag == 12:
        if zstd is None:
            raise RuntimeError("zstandard package unavailable")
        result = zstd.ZstdDecompressor().decompress(packed, max_output_size=expected_size)
        return result, {"strategy": "zstd", "codec_complete": True}
    if flag == 0:
        decrypted = aes_ecb(packed) if len(packed) >= 16 else packed
        wrapper_ok = (
            len(decrypted) >= 18
            and struct.unpack_from("<Q", decrypted, 0)[0] == 1
            and decrypted[16:18] in (b"\x78\x9c", b"\x78\xda", b"\x78\x01")
        )
        if wrapper_ok:
            # Both zlib-wrapped and raw-DEFLATE bodies occur after the same
            # verified AES/wrapper boundary.  Require actual stream EOF rather
            # than treating a failed first header interpretation as unreadable.
            errors: list[str] = []
            for wbits, codec_name in ((zlib.MAX_WBITS, "zlib"), (-zlib.MAX_WBITS, "raw_deflate")):
                try:
                    stream = zlib.decompressobj(wbits)
                    result = stream.decompress(decrypted[18:]) + stream.flush()
                    if not stream.eof:
                        errors.append(f"{codec_name}: no EOF")
                        continue
                    return result, {
                        "strategy": f"aes_ecb_then_{codec_name}_wrapper_qword1_at_0",
                        "codec_complete": True,
                        "zlib_unused_bytes": len(stream.unused_data),
                        "zlib_unconsumed_bytes": len(stream.unconsumed_tail),
                    }
                except zlib.error as exc:
                    errors.append(f"{codec_name}: {exc}")
            raise ValueError("; ".join(errors))
        # This is intentionally not called a decoded script payload.  It is kept
        # for literal/path triage only, matching the prior audited extractor.
        return packed, {
            "strategy": "raw_packed_no_verified_flag0_wrapper", "codec_complete": None,
        }
    return packed, {"strategy": f"raw_unhandled_flag_{flag}", "codec_complete": None}


def parse_direct_path(data: bytes) -> str | None:
    """Only accepts a fully bounded leading tI/sI length-framed path."""
    for base in (0, 1, 2):
        if len(data) < base + 6 or data[base:base + 2] not in (b"tI", b"sI"):
            continue
        size = struct.unpack_from("<I", data, base + 2)[0]
        start = base + 6
        end = start + size
        if not (0 < size < 4096 and end <= len(data)):
            continue
        raw = data[start:end]
        try:
            text = raw.decode("utf-8", "strict")
        except UnicodeDecodeError:
            continue
        if text.endswith(".py") and ("\\" in text or "/" in text):
            return text
    return None


def all_offsets(data: bytes, needle: bytes) -> list[int]:
    result: list[int] = []
    offset = 0
    while True:
        offset = data.find(needle, offset)
        if offset < 0:
            return result
        result.append(offset)
        offset += 1  # overlapping terms count by contract


def printable_context(data: bytes, offset: int, size: int, radius: int = 72) -> dict[str, Any]:
    start = max(0, offset - radius)
    end = min(len(data), offset + size + radius)
    raw = data[start:end]
    return {
        "decoded_byte_offset": offset,
        "context_start": start,
        "context_end": end,
        "context_hex": raw.hex(),
        "context_utf8_backslashreplace": raw.decode("utf-8", "backslashreplace"),
    }


def read_package(path: Path, label: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Parse outer NPK header/table without decoding an application payload."""
    path = ensure_allowed_source(path)
    size = path.stat().st_size
    with path.open("rb") as handle:
        raw_header = handle.read(32)
        header = aes_ecb(raw_header)
        if len(header) < 24:
            raise ValueError("NPK header shorter than 24 bytes")
        unknown_qword, magic, version, table_offset, entry_count = struct.unpack("<QIIII", header[:24])
        if entry_count > 1_000_000 or table_offset >= size or table_offset + entry_count * 48 > size:
            raise ValueError("NPK table bounds invalid")
        handle.seek(table_offset)
        raw_table = handle.read(entry_count * 48)
        if len(raw_table) != entry_count * 48:
            raise ValueError("short NPK table read")
    table = aes_ecb(raw_table)
    rows: list[dict[str, Any]] = []
    bounds_errors = 0
    for index in range(entry_count):
        rec = table[index * 48:(index + 1) * 48]
        file_id, offset, packed_size, declared_size, c1, c2, flag = struct.unpack_from("<QIIIIIi", rec, 0)
        valid = offset + packed_size <= size
        if not valid:
            bounds_errors += 1
        rows.append({
            "entry_index": index,
            "file_id": f"{file_id:016X}",
            "offset": offset,
            "packed_size": packed_size,
            "declared_size": declared_size,
            "c1": c1,
            "c2": c2,
            "flag": flag,
            "table_record_hex": rec.hex(),
            "bounds_valid": valid,
        })
    package = {
        "label": label,
        "path": str(path),
        "source_size": size,
        "source_sha256": sha256_file(path),
        "header": {
            "unknown_qword": unknown_qword,
            "magic": magic,
            "version": version,
            "table_offset": table_offset,
            "entry_count": entry_count,
            "raw_header_hex": raw_header.hex(),
            "decrypted_header_hex": header.hex(),
        },
        "table_bounds_errors": bounds_errors,
    }
    return package, rows


def load_entry(package_path: Path, row: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    package_path = ensure_allowed_source(package_path)
    if not row["bounds_valid"]:
        raise ValueError("entry packed range outside package")
    with package_path.open("rb") as handle:
        handle.seek(row["offset"])
        packed = handle.read(row["packed_size"])
    if len(packed) != row["packed_size"]:
        raise ValueError("short packed entry read")
    return unpack_entry(packed, row["declared_size"], row["flag"])


def analyze_pool(
    data: bytes,
    *,
    origin: str,
    marker_offset: int,
    block_length: int,
    count: int,
    offsets_start: int,
    raw_length_offset: int,
    raw_start: int,
    raw_end: int,
    require_tail_marker: bool,
) -> dict[str, Any] | None:
    """Validate a bounded UTF-8 string pool; no string-to-record inference."""
    if not (0 <= marker_offset <= offsets_start <= raw_length_offset < raw_start <= raw_end <= len(data)):
        return None
    if not (0 <= count <= 500_000 and offsets_start + 4 * count == raw_length_offset):
        return None
    raw_length = struct.unpack_from("<I", data, raw_length_offset)[0]
    if raw_end - raw_start != raw_length:
        return None
    offsets = list(struct.unpack_from(f"<{count}I", data, offsets_start)) if count else []
    if offsets and (any(a > b for a, b in zip(offsets, offsets[1:])) or offsets[-1] != raw_length):
        return None
    raw = data[raw_start:raw_end]
    try:
        raw.decode("utf-8", "strict")
    except UnicodeDecodeError:
        return None
    tail = data[raw_end:min(len(data), raw_end + 96)]
    tail_marker_present = b"string_pool" in tail
    if require_tail_marker and not tail_marker_present:
        return None
    start = 0
    matching_slots: list[dict[str, Any]] = []
    invalid_slot_count = 0
    for slot, end in enumerate(offsets):
        item = raw[start:end]
        try:
            text = item.decode("utf-8", "strict")
        except UnicodeDecodeError:
            invalid_slot_count += 1
            start = end
            continue
        terms = [term for term in AUG_TERMS if term in text]
        if terms:
            matching_slots.append({
                "origin": origin,
                "slot": slot,
                "relative_start": start,
                "relative_end": end,
                "payload_start": raw_start + start,
                "payload_end": raw_start + end,
                "utf8_length": end - start,
                "exact_aug_display_string": text == "AUG突击步枪",
                "matching_terms": terms,
                "text": text,
                "raw_hex": item.hex(),
            })
        start = end
    return {
        "origin": origin,
        "marker_offset": marker_offset,
        "block_length": block_length,
        "string_count": count,
        "offsets_start": offsets_start,
        "offsets_end": raw_length_offset,
        "raw_utf8_length": raw_length,
        "raw_start": raw_start,
        "raw_end_exclusive": raw_end,
        "tail_marker_present_within_96": tail_marker_present,
        "tail_hex_96": tail.hex(),
        "invalid_slot_count": invalid_slot_count,
        "matching_slots": matching_slots,
    }


def analyze_end_offset_pool(
    data: bytes,
    *,
    origin: str,
    marker_offset: int,
    block_length: int,
    count: int,
    reserved: int,
    offsets_start: int,
    raw_start: int,
    raw_end: int,
) -> dict[str, Any] | None:
    """Validate x{ body: count/reserved/end-offsets/raw UTF-8, no codec use."""
    if not (0 < count <= 500_000 and reserved == 0):
        return None
    if not (0 <= marker_offset < offsets_start <= raw_start <= raw_end <= len(data)):
        return None
    if offsets_start + 4 * count != raw_start:
        return None
    raw_length = raw_end - raw_start
    offsets = list(struct.unpack_from(f"<{count}I", data, offsets_start))
    if any(a > b for a, b in zip(offsets, offsets[1:])) or offsets[-1] != raw_length:
        return None
    raw = data[raw_start:raw_end]
    try:
        raw.decode("utf-8", "strict")
    except UnicodeDecodeError:
        return None
    start = 0
    matching_slots: list[dict[str, Any]] = []
    invalid_slot_count = 0
    for slot, end in enumerate(offsets):
        item = raw[start:end]
        try:
            text = item.decode("utf-8", "strict")
        except UnicodeDecodeError:
            invalid_slot_count += 1
            start = end
            continue
        terms = [term for term in AUG_TERMS if term in text]
        if terms:
            matching_slots.append({
                "origin": origin,
                "slot": slot,
                "relative_start": start,
                "relative_end": end,
                "payload_start": raw_start + start,
                "payload_end": raw_start + end,
                "utf8_length": end - start,
                "exact_aug_display_string": text == "AUG突击步枪",
                "matching_terms": terms,
                "text": text,
                "raw_hex": item.hex(),
            })
        start = end
    return {
        "origin": origin,
        "marker_offset": marker_offset,
        "frame_magic": "x{",
        "body_length": block_length,
        "body_start": offsets_start - 8,
        "body_end_exclusive": raw_end,
        "string_count": count,
        "reserved_u32": reserved,
        "offsets_start": offsets_start,
        "offsets_end_exclusive": raw_start,
        "raw_utf8_length": raw_length,
        "raw_start": raw_start,
        "raw_end_exclusive": raw_end,
        "length_evidence": "raw_utf8_length = body_length - 8 - 4*string_count; final end offset equals raw_utf8_length",
        "invalid_slot_count": invalid_slot_count,
        "matching_slots": matching_slots,
    }


def find_xbrace_end_offset_pools(data: bytes) -> list[dict[str, Any]]:
    """Find only fully bounded custom x{ length-framed UTF-8 pools."""
    pools: list[dict[str, Any]] = []
    position = 0
    while True:
        position = data.find(b"x{", position)
        if position < 0:
            break
        if position + 14 <= len(data):
            body_length = struct.unpack_from("<I", data, position + 2)[0]
            body_start = position + 6
            body_end = body_start + body_length
            if 8 <= body_length and body_end <= len(data):
                count = struct.unpack_from("<I", data, body_start)[0]
                reserved = struct.unpack_from("<I", data, body_start + 4)[0]
                offsets_start = body_start + 8
                raw_start = offsets_start + 4 * count
                if count <= 500_000 and raw_start <= body_end:
                    parsed = analyze_end_offset_pool(
                        data,
                        origin="xbrace_body_end_offset_utf8_pool",
                        marker_offset=position,
                        block_length=body_length,
                        count=count,
                        reserved=reserved,
                        offsets_start=offsets_start,
                        raw_start=raw_start,
                        raw_end=body_end,
                    )
                    if parsed is not None:
                        pools.append(parsed)
        position += 1
    return pools


def find_brace_end_offset_pools(data: bytes) -> list[dict[str, Any]]:
    """Validate a bounded {+u32 section whose body is a UTF-8 end-offset pool."""
    pools: list[dict[str, Any]] = []
    position = 0
    while True:
        position = data.find(b"{", position)
        if position < 0:
            break
        # The '{' in an x{ frame is intentionally handled by the stronger
        # x{ parser, not counted again as a generic brace section.
        if position > 0 and data[position - 1:position] == b"x":
            position += 1
            continue
        if position + 14 <= len(data):
            section_length = struct.unpack_from("<I", data, position + 1)[0]
            body_start = position + 5
            section_end = body_start + section_length
            if 8 <= section_length and section_end <= len(data):
                count = struct.unpack_from("<I", data, body_start)[0]
                reserved = struct.unpack_from("<I", data, body_start + 4)[0]
                offsets_start = body_start + 8
                raw_start = offsets_start + 4 * count
                if count <= 500_000 and raw_start <= section_end:
                    parsed = analyze_end_offset_pool(
                        data,
                        origin="brace_u32_end_offset_utf8_pool",
                        marker_offset=position,
                        block_length=section_length,
                        count=count,
                        reserved=reserved,
                        offsets_start=offsets_start,
                        raw_start=raw_start,
                        raw_end=section_end,
                    )
                    if parsed is not None:
                        parsed.update({
                            "section_marker_offset": position,
                            "section_magic": "{",
                            "section_length_u32_at_marker_plus_1": section_length,
                            "section_body_start": body_start,
                            "section_end_exclusive": section_end,
                            "length_evidence": "raw_utf8_length = section_length - 8 - 4*string_count; final end offset equals raw_utf8_length",
                        })
                        pools.append(parsed)
        position += 1
    return pools


def find_standard_pools(data: bytes) -> list[dict[str, Any]]:
    """Strictly scan b'I' + u32 framing; accept only fully validated pools."""
    pools: list[dict[str, Any]] = []
    pos = 0
    while True:
        pos = data.find(b"I", pos)
        if pos < 0:
            break
        if pos + 13 <= len(data):
            total = struct.unpack_from("<I", data, pos + 1)[0]
            count = struct.unpack_from("<I", data, pos + 5)[0]
            # block after length: count + offsets + raw_len + raw bytes
            raw_length_offset = pos + 9 + 4 * count
            raw_start = raw_length_offset + 4
            if count <= 500_000 and raw_start <= len(data):
                raw_length = struct.unpack_from("<I", data, raw_length_offset)[0]
                raw_end = raw_start + raw_length
                expected_total = 4 + 4 * count + 4 + raw_length
                if total == expected_total and raw_end <= len(data):
                    parsed = analyze_pool(
                        data,
                        origin="standard_I_u32_block",
                        marker_offset=pos,
                        block_length=total,
                        count=count,
                        offsets_start=pos + 9,
                        raw_length_offset=raw_length_offset,
                        raw_start=raw_start,
                        raw_end=raw_end,
                        require_tail_marker=False,
                    )
                    if parsed is not None:
                        pools.append(parsed)
        pos += 1
    return pools


def find_py314_direct_pool(data: bytes) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """Sample-specific py314 direct pool test from the audited reference."""
    facts: dict[str, Any] = {"tested": True, "layout": "u32@0x2B,count; u32@0x2F,reserved; offsets@0x33"}
    if len(data) < 0x37:
        facts["accepted"] = False
        facts["reason"] = "payload shorter than 0x37"
        return None, facts
    count = struct.unpack_from("<I", data, 0x2B)[0]
    reserved = struct.unpack_from("<I", data, 0x2F)[0]
    facts.update({"count_at_0x2B": count, "reserved_at_0x2F": reserved})
    if count > 500_000:
        facts.update({"accepted": False, "reason": "count too large for bounded probe"})
        return None, facts
    raw_length_offset = 0x33 + 4 * count
    raw_start = raw_length_offset + 4
    if raw_start > len(data):
        facts.update({"accepted": False, "reason": "offset table exceeds payload"})
        return None, facts
    raw_length = struct.unpack_from("<I", data, raw_length_offset)[0]
    raw_end = raw_start + raw_length
    facts.update({"raw_length": raw_length, "raw_start": raw_start, "raw_end": raw_end})
    if raw_end > len(data):
        facts.update({"accepted": False, "reason": "raw UTF-8 region exceeds payload"})
        return None, facts
    parsed = analyze_pool(
        data,
        origin="py314_direct_0x2B_layout",
        marker_offset=0x2B,
        block_length=4 + 4 * count + 4 + raw_length,
        count=count,
        offsets_start=0x33,
        raw_length_offset=raw_length_offset,
        raw_start=raw_start,
        raw_end=raw_end,
        require_tail_marker=True,
    )
    if parsed is None:
        facts.update({"accepted": False, "reason": "pool bounds/UTF-8/tail marker checks failed"})
        return None, facts
    facts["accepted"] = True
    return parsed, facts


def parse_framing(data: bytes) -> dict[str, Any]:
    """Record byte-bounded framing only; neutral field names remain neutral."""
    xbrace_pools = find_xbrace_end_offset_pools(data)
    brace_pools = find_brace_end_offset_pools(data)
    result: dict[str, Any] = {
        "payload_length": len(data),
        "head_128_hex": data[:128].hex(),
        "leading_tI_or_sI_path": parse_direct_path(data),
        "root_code": {"recognized": False},
        "bindict_frame": {"recognized": False},
        "validated_xbrace_end_offset_pool_count": len(xbrace_pools),
        "validated_brace_end_offset_pool_count": len(brace_pools),
    }
    if len(data) >= 0x1A and data[0] in (0x73, 0xF3) and data[0x15] == 0xFB:
        fields = struct.unpack_from("<IIIII", data, 1)
        code_length = struct.unpack_from("<I", data, 0x16)[0]
        code_start = 0x1A
        code_end = code_start + code_length
        root = {
            "recognized": code_end <= len(data),
            "tag_at_0x00": f"0x{data[0]:02X}",
            "five_u32_at_0x01_to_0x14": list(fields),
            "tag_at_0x15": f"0x{data[0x15]:02X}",
            "root_code_length_u32_at_0x16": code_length,
            "root_code_start": code_start,
            "root_code_end_exclusive": code_end,
        }
        if code_end <= len(data):
            root["bytes_after_root_32_hex"] = data[code_end:min(len(data), code_end + 32)].hex()
            q = code_end + 7
            root["post_root_plus_7_offset_Q"] = q
            if q + 6 <= len(data):
                root["bytes_at_Q_32_hex"] = data[q:min(len(data), q + 32)].hex()
                if data[q:q + 2] == b"x{":
                    body_length = struct.unpack_from("<I", data, q + 2)[0]
                    body_start = q + 6
                    body_end = body_start + body_length
                    matched = next((pool for pool in xbrace_pools if pool["marker_offset"] == q), None)
                    if matched is not None:
                        result["bindict_frame"] = {
                            "recognized": True,
                            "layout": "x{ + u32le(body_len) + u32le(string_count) + u32le(reserved=0) + end_offsets[string_count] + raw_UTF8_to_body_end",
                            "Q": q,
                            "body_length_u32_at_Q_plus_2": body_length,
                            "body_start": body_start,
                            "body_end_exclusive": body_end,
                            "string_count_u32_at_body_plus_0": matched["string_count"],
                            "reserved_u32_at_body_plus_4": matched["reserved_u32"],
                            "end_offsets_start": matched["offsets_start"],
                            "end_offsets_end_exclusive": matched["offsets_end_exclusive"],
                            "raw_utf8_start": matched["raw_start"],
                            "raw_utf8_end_exclusive": matched["raw_end_exclusive"],
                            "raw_utf8_length": matched["raw_utf8_length"],
                            "length_evidence": matched["length_evidence"],
                        }
                    else:
                        result["bindict_frame"] = {
                            "recognized": False,
                            "reason": "x{ frame is present but did not satisfy complete reserved/end-offset/strict-UTF8 pool checks",
                            "Q": q,
                            "body_length_u32_at_Q_plus_2": body_length,
                            "body_start": body_start,
                            "body_end_exclusive": body_end,
                            "body_within_payload": body_end <= len(data),
                            "u32_at_body_plus_0_neutral": struct.unpack_from("<I", data, body_start)[0] if body_start + 4 <= len(data) else None,
                            "u32_at_body_plus_4_neutral": struct.unpack_from("<I", data, body_start + 4)[0] if body_start + 8 <= len(data) else None,
                        }
        result["root_code"] = root
    direct_pool, direct_facts = find_py314_direct_pool(data)
    standard_pools = find_standard_pools(data)
    pool_ranges: set[tuple[int, int]] = set()
    pools: list[dict[str, Any]] = []
    for pool in [direct_pool, *standard_pools, *xbrace_pools, *brace_pools]:
        if pool is not None:
            key = (pool["raw_start"], pool["raw_end_exclusive"])
            if key not in pool_ranges:
                pool_ranges.add(key)
                pools.append(pool)
    result["py314_direct_pool_probe"] = direct_facts
    result["validated_string_pools"] = pools
    return result


def clean_csv_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def classify_all_equips_variant(logical_path: str) -> str:
    """Path-name classification only; exact names remain the primary evidence."""
    name = logical_path.replace("\\", "/").rsplit("/", 1)[-1].casefold()
    if name == "all_equips_data.py":
        return "base"
    if "_chs" in name:
        return "CHS_named"
    return "regional_or_other_named"


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: clean_csv_value(row.get(field)) for field in fieldnames})


def artifacts_manifest(exclude: set[str]) -> dict[str, Any]:
    files = []
    for child in sorted(OUT.iterdir(), key=lambda item: item.name.casefold()):
        if child.is_file() and child.name not in exclude:
            files.append({
                "file": child.name,
                "bytes": child.stat().st_size,
                "sha256": sha256_file(child),
            })
    return {"artifact_file_count": len(files), "files": files}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    package_records: list[dict[str, Any]] = []
    package_rows: dict[str, list[dict[str, Any]]] = {}
    scan_counters: dict[str, dict[str, Any]] = {}
    path_map: dict[str, set[str]] = defaultdict(set)
    raw_token_hits: list[dict[str, Any]] = []

    # First pass is a static, one-entry-at-a-time scan.  It never retains or
    # serializes arbitrary payloads, only target discovery facts.
    for label, declared_path in ARCHIVE_SPECS:
        package, rows = read_package(declared_path, label)
        package_records.append(package)
        package_rows[label] = rows
        decoded = 0
        failures: list[dict[str, Any]] = []
        direct_paths = 0
        token_entries = 0
        flags = Counter(row["flag"] for row in rows)
        for row in rows:
            if not row["bounds_valid"]:
                failures.append({"entry_index": row["entry_index"], "file_id": row["file_id"], "stage": "bounds"})
                continue
            try:
                data, trace = load_entry(declared_path, row)
            except Exception as exc:  # exact row retained rather than treated as absence
                failures.append({
                    "entry_index": row["entry_index"], "file_id": row["file_id"],
                    "stage": "static_unpack", "error": repr(exc),
                })
                continue
            decoded += 1
            direct = parse_direct_path(data)
            if direct:
                path_map[row["file_id"]].add(direct)
                direct_paths += 1
            offsets = all_offsets(data, TOKEN)
            if offsets:
                token_entries += 1
                raw_token_hits.append({
                    "package_label": label,
                    "entry_index": row["entry_index"],
                    "file_id": row["file_id"],
                    "direct_logical_path": direct or "",
                    "all_equips_data_token_offsets": offsets,
                    "decoder_strategy": trace["strategy"],
                    "payload_sha256": sha256_bytes(data),
                    "payload_size": len(data),
                })
        scan_counters[label] = {
            "entries_declared": len(rows),
            "entries_static_unpacked": decoded,
            "entry_failures": len(failures),
            "entry_failures_sample_first_50": failures[:50],
            "direct_length_framed_paths": direct_paths,
            "entries_with_raw_all_equips_data_token": token_entries,
            "flag_counts": {str(key): value for key, value in sorted(flags.items())},
        }

    # Candidate IDs are deliberately derived only from a direct bounded logical
    # path (plus the user-supplied current target ID).  A raw token in imports
    # or code is retained as discovery telemetry but is NOT treated as a table.
    target_ids = {TARGET_FILE_ID}
    discovered_paths: dict[str, list[str]] = {}
    for file_id, paths in path_map.items():
        matching = sorted(path for path in paths if "all_equips_data" in path.casefold())
        if matching:
            target_ids.add(file_id)
            discovered_paths[file_id] = matching
    unique_path_map = {
        file_id: sorted(paths) for file_id, paths in path_map.items() if file_id in target_ids
    }
    variant_inventory = [
        {
            "file_id": file_id,
            "logical_path": logical_path,
            "variant_class_from_name_only": classify_all_equips_variant(logical_path),
            "discovery_method": "direct_bounded_tI_or_sI_path_in_same_entry",
        }
        for file_id, paths in sorted(discovered_paths.items())
        for logical_path in paths
    ]
    variant_class_counts = dict(sorted(Counter(item["variant_class_from_name_only"] for item in variant_inventory).items()))

    target_entries: list[dict[str, Any]] = []
    pool_rows: list[dict[str, Any]] = []
    all_raw_aug_rows: list[dict[str, Any]] = []
    for label, declared_path in ARCHIVE_SPECS:
        for row in package_rows[label]:
            if row["file_id"] not in target_ids:
                continue
            target: dict[str, Any] = {
                "package_label": label,
                "package_path": str(ensure_allowed_source(declared_path)),
                "package_sha256": next(p["source_sha256"] for p in package_records if p["label"] == label),
                "file_id": row["file_id"],
                "entry_index": row["entry_index"],
                "entry_offset": row["offset"],
                "packed_size": row["packed_size"],
                "declared_size": row["declared_size"],
                "flag": row["flag"],
                "table_record_hex": row["table_record_hex"],
                "cross_variant_logical_paths": unique_path_map.get(row["file_id"], []),
                "cross_variant_classes_from_name_only": sorted({
                    classify_all_equips_variant(path) for path in unique_path_map.get(row["file_id"], [])
                }),
                "logical_path_resolution": (
                    "direct_length_framed_same_entry" if any(
                        hit["package_label"] == label and hit["entry_index"] == row["entry_index"] and hit["direct_logical_path"]
                        for hit in raw_token_hits
                    ) else ("cross_archive_same_file_id_from_direct_length_framed_entry" if unique_path_map.get(row["file_id"]) else "unresolved")
                ),
            }
            try:
                data, trace = load_entry(declared_path, row)
                target.update({
                    "static_unpack_status": "decoded_or_static_bytes_available",
                    "decoder": trace,
                    "payload_size": len(data),
                    "payload_sha256": sha256_bytes(data),
                    "all_equips_data_raw_token_offsets": all_offsets(data, TOKEN),
                })
                framing = parse_framing(data)
                target["framing"] = framing
                raw_aug: dict[str, list[dict[str, Any]]] = {}
                for term in AUG_TERMS:
                    found = all_offsets(data, term.encode("utf-8"))
                    raw_aug[term] = [printable_context(data, offset, len(term.encode("utf-8"))) for offset in found]
                    for offset in found:
                        all_raw_aug_rows.append({
                            "package_label": label,
                            "file_id": row["file_id"],
                            "entry_index": row["entry_index"],
                            "term": term,
                            "payload_offset": offset,
                            "payload_sha256": target["payload_sha256"],
                        })
                target["raw_aug_term_hits"] = raw_aug
                for pool in framing["validated_string_pools"]:
                    for slot in pool["matching_slots"]:
                        row_out = {
                            "package_label": label,
                            "file_id": row["file_id"],
                            "entry_index": row["entry_index"],
                            "payload_sha256": target["payload_sha256"],
                            **slot,
                        }
                        pool_rows.append(row_out)
                # Evidence boundary: deliberately do not reinterpret a slot byte
                # as a row/key.  We only quantify byte-pattern candidates outside
                # pool ranges and label them non-semantic.
                exact_display_slots = [
                    slot for pool in framing["validated_string_pools"]
                    for slot in pool["matching_slots"] if slot["exact_aug_display_string"]
                ]
                target["record_binding_attempt"] = {
                    "exact_aug_display_slot_count": len(exact_display_slots),
                    "exact_aug_display_slots": [
                        {key: slot[key] for key in ("origin", "slot", "payload_start", "payload_end", "text")}
                        for slot in exact_display_slots
                    ],
                    "conclusion": "blocked_no_validated_value_codec_or_explicit_same_record_key_value_relation",
                    "not_used_as_evidence": "No neighbouring string, pool order, one-byte slot value, varint-looking bytes, or raw numeric coincidence was used to label a record or a numeric stat.",
                }
            except Exception as exc:
                target.update({"static_unpack_status": "unreadable", "error": repr(exc)})
            target_entries.append(target)

    # Compact, auditable tables.
    coverage_rows = []
    for target in target_entries:
        coverage_rows.append({
            "package_label": target["package_label"],
            "file_id": target["file_id"],
            "entry_index": target["entry_index"],
            "cross_variant_logical_paths": target["cross_variant_logical_paths"],
            "logical_path_resolution": target["logical_path_resolution"],
            "entry_offset": target["entry_offset"],
            "packed_size": target["packed_size"],
            "declared_size": target["declared_size"],
            "flag": target["flag"],
            "static_unpack_status": target["static_unpack_status"],
            "payload_size": target.get("payload_size"),
            "payload_sha256": target.get("payload_sha256"),
            "all_equips_data_token_count": len(target.get("all_equips_data_raw_token_offsets", [])),
        })
    write_csv(
        OUT / "all_equips_target_coverage.csv", coverage_rows,
        ["package_label", "file_id", "entry_index", "cross_variant_logical_paths", "logical_path_resolution", "entry_offset", "packed_size", "declared_size", "flag", "static_unpack_status", "payload_size", "payload_sha256", "all_equips_data_token_count"],
    )
    write_csv(
        OUT / "AUG_string_pool_hits.csv", pool_rows,
        ["package_label", "file_id", "entry_index", "payload_sha256", "origin", "slot", "relative_start", "relative_end", "payload_start", "payload_end", "utf8_length", "exact_aug_display_string", "matching_terms", "text", "raw_hex"],
    )
    write_csv(
        OUT / "AUG_raw_term_hits.csv", all_raw_aug_rows,
        ["package_label", "file_id", "entry_index", "term", "payload_offset", "payload_sha256"],
    )

    exact_display_slot_count = sum(1 for row in pool_rows if row["exact_aug_display_string"])
    raw_hit_counts = Counter(row["term"] for row in all_raw_aug_rows)
    report = {
        "analysis_id": "AUG_all_equips_static_001",
        "analysis_mode": "read_only_zero_execution_static_archive_and_payload_framing",
        "scope": {
            "allowed_source_root": str(SOURCE_ROOT),
            "explicit_archive_paths": [str(path) for _, path in ARCHIVE_SPECS],
            "prohibited_source_root": FORBIDDEN_ROOT_TEXT,
            "prohibited_root_used_in_this_script": False,
            "source_write_operations": 0,
            "payload_execution_operations": 0,
            "payload_actions_not_performed": ["import", "marshal.loads", "compile", "exec", "eval", "game start"],
            "output_root": str(OUT),
        },
        "decoder_evidence": {
            "outer_npk": "AES-ECB decoded header/table; 48-byte record bounds checked; flag 0 target entries passed AES-ECB plus completed zlib wrapper extraction.",
            "declared_size_boundary": "NPK declared_size was retained as metadata and never required to equal final zlib byte count.",
        },
        "packages": package_records,
        "scan_coverage": scan_counters,
        "raw_all_equips_token_hits": raw_token_hits,
        "discovered_direct_all_equips_paths_by_file_id": discovered_paths,
        "target_file_ids": sorted(target_ids),
        "target_entries": target_entries,
        "counts": {
            "archive_count": len(package_records),
            "total_declared_entries": sum(item["entries_declared"] for item in scan_counters.values()),
            "total_static_unpacked_entries": sum(item["entries_static_unpacked"] for item in scan_counters.values()),
            "total_static_unpack_failures": sum(item["entry_failures"] for item in scan_counters.values()),
            "raw_all_equips_token_entry_count": len(raw_token_hits),
            "discovered_all_equips_file_id_count": len(discovered_paths),
            "target_entry_variant_count": len(target_entries),
            "validated_string_pool_count": sum(len(item.get("framing", {}).get("validated_string_pools", [])) for item in target_entries),
            "AUG_pool_matching_slot_count": len(pool_rows),
            "exact_AUG_display_string_slot_count": exact_display_slot_count,
            "raw_AUG_term_occurrence_counts": dict(sorted(raw_hit_counts.items())),
        },
        "AUG_record_to_numeric_conclusion": {
            "status": "blocked",
            "what_is_proven": "Exact AUG literals and any fully bounded string-pool slots are located at the offsets in target_entries/AUG_string_pool_hits.csv. The current py314 all_equips_data_yk payload is independently tied to source package SHA and entry 7744/file ID 0F92F8F525E6D201.",
            "what_is_not_proven": "No numeric item ID, attack value, fire-rate, durability, or other concrete AUG structure record/value is reported because no validated BinDict value codec, record-key relation, or same-record string reference was recovered.",
            "precise_blocker": "The static parser can bound the root code and, when present, the x{ body plus neutral slot/opaque-data regions, but it has no verified decoder for the opaque value codec or key/hash representation. String-pool slot order and adjacent strings are expressly excluded as a row mapping method.",
            "next_safe_step": "Obtain a source-level specification or independently validate a zero-execution BinDict key/value decoder against multiple bounded rows. The decoder must demonstrate record boundaries and an explicit key/value link from the AUG display slot to a numeric record before values may be stated.",
        },
        "generated_files": ["all_equips_target_coverage.csv", "AUG_string_pool_hits.csv", "AUG_raw_term_hits.csv", "report.json", "README.md", "static_all_equips_audit.py"],
    }
    report_path = OUT / "report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    read_back = json.loads(report_path.read_text(encoding="utf-8"))
    assert read_back["counts"] == report["counts"]

    readme = """# all_equips_data / AUG read-only static audit\n\n- **Allowed input only:** `E:\\mrzh` named script archives. `E:\\LifeAfter` is excluded and is not accessed by this audit program.\n- **Zero-execution boundary:** no game process start; no import, marshal, compilation, evaluation, or execution of decoded payloads.\n- **Target:** all `all_equips_data` candidates found by direct bounded logical paths and raw token scan, including current py314 `all_equips_data_yk.py` file ID `0F92F8F525E6D201`, entry 7744.\n- **Evidence rule:** exact strings/pool slots prove literal presence only. No string adjacency, pool order, or unvalidated byte pattern is used to infer an AUG record or numeric values.\n\n## Files\n\n- `report.json` — full package coverage, target framing, string pool parse results, and blocker.\n- `all_equips_target_coverage.csv` — exact target entry variants.\n- `AUG_string_pool_hits.csv` — validated pool slots containing AUG terms.\n- `AUG_raw_term_hits.csv` — literal offsets/counts across target payloads.\n- `static_all_equips_audit.py` — reproducible static scanner.\n- `artifact_sha256.json` — hashes for generated artifacts (created after report validation).\n\nThe final evidence boundary and exact offsets are in `report.json`.\n"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")

    manifest = artifacts_manifest({"artifact_sha256.json"})
    manifest_path = OUT / "artifact_sha256.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    loaded_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert loaded_manifest == manifest
    print(json.dumps({
        "output_root": str(OUT),
        "report": str(report_path),
        "report_sha256": sha256_file(report_path),
        "counts": report["counts"],
        "artifact_file_count_excluding_manifest": manifest["artifact_file_count"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
