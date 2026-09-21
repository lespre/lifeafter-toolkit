# -*- coding: utf-8 -*-
"""LifeAfter script NPK lazy reader for the local Wiki.

The reader is deliberately read-only: it indexes only the encrypted NPK table,
then seeks and decodes one requested entry in memory. It never creates an
``entries`` tree and never writes to the source package.
"""
from __future__ import annotations

import hashlib
import re
import struct
import zlib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

try:
    import zstandard as zstd
except ImportError:  # pragma: no cover - environment validation covers this
    zstd = None

KEY = bytes([
    0x60, 0x63, 0x08, 0xD8, 0xA3, 0x2C, 0x78, 0x20,
    0x13, 0xD2, 0x6C, 0x2F, 0x22, 0x6F, 0x68, 0x6D,
])
NPK_ENTRY = struct.Struct("<QIIIIIi")
NPK_ENTRY_STRIDE = 48  # 32B parsed fields + 16B archive-reserved bytes
HEADER = struct.Struct("<QIIII")
MAX_PAGE_SIZE = 100
MAX_PREVIEW_SOURCE_BYTES = 96 * 1024


class SourceChangedError(RuntimeError):
    """The source package changed after the reader created its source lock."""


class NpkFormatError(ValueError):
    """The archive does not pass the bounded NXPK header/index checks."""


@dataclass(frozen=True)
class ScriptNpkEntry:
    entry_index: int
    file_id: int
    offset: int
    packed_size: int
    declared_size: int
    c1: int
    c2: int
    flag: int

    def as_public_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["file_id"] = f"{self.file_id:016X}"
        return result


def _aes_ecb_decrypt(data: bytes) -> bytes:
    """Decrypt all full AES blocks and preserve any trailing short fragment."""
    usable = len(data) // 16 * 16
    if not usable:
        return data
    decryptor = Cipher(algorithms.AES(KEY), modes.ECB()).decryptor()
    return decryptor.update(data[:usable]) + decryptor.finalize() + data[usable:]


def _lz4_block(blob: bytes, expected: int) -> bytes:
    """Decode the raw LZ4 block form used by NXPK flag=2 entries."""
    output = bytearray()
    cursor = 0

    def extend(value: int) -> int:
        nonlocal cursor
        if value == 15:
            while True:
                if cursor >= len(blob):
                    raise NpkFormatError("LZ4 extension truncated")
                extra = blob[cursor]
                cursor += 1
                value += extra
                if extra != 255:
                    return value
        return value

    while cursor < len(blob) and len(output) < expected:
        token = blob[cursor]
        cursor += 1
        literal_length = extend(token >> 4)
        if cursor + literal_length > len(blob):
            raise NpkFormatError("LZ4 literal exceeds packed entry")
        output.extend(blob[cursor:cursor + literal_length])
        cursor += literal_length
        if cursor >= len(blob):
            break
        if cursor + 2 > len(blob):
            raise NpkFormatError("LZ4 distance truncated")
        distance = blob[cursor] | (blob[cursor + 1] << 8)
        cursor += 2
        if distance == 0 or distance > len(output):
            raise NpkFormatError("LZ4 distance invalid")
        match_length = extend(token & 15) + 4
        source = len(output) - distance
        for _ in range(match_length):
            output.append(output[source])
            source += 1

    if len(output) != expected:
        raise NpkFormatError(f"LZ4 output {len(output)} != expected {expected}")
    return bytes(output)


def _unpack_entry(packed: bytes, declared_size: int, flag: int) -> bytes:
    """Decode exactly one NXPK entry without persisting it anywhere."""
    if flag == 0:
        decoded = _aes_ecb_decrypt(packed)
        # Documents script entries may contain an AES-decrypted wrapper:
        # u64 little-endian 1 + 8 reserved bytes + zlib header at byte 16.
        if (
            len(decoded) >= 18
            and struct.unpack_from("<Q", decoded, 0)[0] == 1
            and decoded[16:18] in (b"\x78\x9c", b"\x78\xda", b"\x78\x01")
        ):
            try:
                return zlib.decompress(decoded[18:])
            except zlib.error:
                return zlib.decompress(decoded[18:], -15)
        return decoded
    if flag == 2:
        return _lz4_block(packed, declared_size)
    if flag == 12:
        if zstd is None:
            raise RuntimeError("当前 Python 环境缺少 zstandard，无法读取 flag=12 条目")
        return zstd.ZstdDecompressor().decompress(packed, max_output_size=declared_size)
    # Unknown flags are not silently reclassified. Returning source bytes would
    # blur "packed exists" and "decoded succeeded", so reject it explicitly.
    raise NpkFormatError(f"unsupported NXPK flag: {flag}")


def _parse_logical_path(data: bytes) -> str:
    """Recover a direct legacy tI/sI path only when its framing is valid."""
    for base in (0, 1, 2):
        if len(data) < base + 6:
            continue
        has_prefix = data[base:base + 2] in (b"tI", b"sI")
        length_offset = base + 2 if has_prefix else base
        length = struct.unpack_from("<I", data, length_offset)[0]
        start = base + 6 if has_prefix else base + 4
        if not (0 < length < 1000 and start + length <= len(data)):
            continue
        candidate = data[start:start + length]
        try:
            value = candidate.decode("utf-8", "strict")
        except UnicodeDecodeError:
            continue
        if ("\\" in value or "/" in value or value.endswith(".py")) and all(
            character.isprintable() or character in "\r\n\t" for character in value
        ):
            return value
    return ""


def _payload_kind(data: bytes) -> str:
    if data.startswith(b"tI"):
        return "legacy_script_wrapper"
    if data.startswith(b"x{"):
        return "bindict_x_container"
    if data.startswith(b"{"):
        return "legacy_string_pool_or_json_candidate"
    if data.startswith(b"DDS "):
        return "dds"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data.startswith(b"PK\x03\x04"):
        return "zip"
    return "unclassified_binary"


def _safe_text_preview(data: bytes, max_chars: int = 1_200) -> dict[str, Any]:
    sample = data[:MAX_PREVIEW_SOURCE_BYTES]
    text = sample.decode("utf-8", "ignore")
    text = "".join(character if (character.isprintable() or character in "\r\n\t") else " " for character in text)
    text = re.sub(r"[ \t\r\n]+", " ", text).strip()
    if not text:
        return {"text": "", "truncated": len(data) > len(sample)}
    return {
        "text": text[:max_chars],
        "truncated": len(text) > max_chars or len(data) > len(sample),
    }


class LiveNpkReader:
    """Bounded, source-locked, on-demand reader for one script NPK package."""

    def __init__(self, package_path: Path | str, server_branch: str):
        self.package_path = Path(package_path)
        self.server_branch = server_branch
        if not self.package_path.is_file():
            raise FileNotFoundError(f"NPK source missing: {self.package_path}")
        self._signature = self._current_signature()
        self.package_sha256 = self._hash_source_locked()
        self._entries = self._read_index_locked()
        self._assert_unchanged()

    def _current_signature(self) -> tuple[int, int]:
        state = self.package_path.stat()
        return state.st_size, state.st_mtime_ns

    def _assert_unchanged(self) -> None:
        if self._current_signature() != self._signature:
            raise SourceChangedError(
                "source package changed after the reader established its lock; restart the local Wiki service"
            )

    def _hash_source_locked(self) -> str:
        digest = hashlib.sha256()
        with self.package_path.open("rb") as handle:
            while block := handle.read(1 << 20):
                digest.update(block)
        self._assert_unchanged()
        return digest.hexdigest()

    def _read_index_locked(self) -> tuple[ScriptNpkEntry, ...]:
        size, _ = self._signature
        with self.package_path.open("rb") as handle:
            raw_header = handle.read(32)
            if len(raw_header) != 32:
                raise NpkFormatError("NPK header too short")
            header = _aes_ecb_decrypt(raw_header)
            _unknown, magic, _version, table_offset, count = HEADER.unpack(header[:24])
            if magic != int.from_bytes(b"NXPK", "little"):
                raise NpkFormatError("not an NXPK archive")
            table_bytes = count * NPK_ENTRY_STRIDE
            if count <= 0 or count > 1_000_000 or table_offset + table_bytes > size:
                raise NpkFormatError("NPK entry table bounds invalid")
            handle.seek(table_offset)
            encrypted_table = handle.read(table_bytes)
            if len(encrypted_table) != table_bytes:
                raise NpkFormatError("NPK entry table read short")
        table = _aes_ecb_decrypt(encrypted_table)
        entries: list[ScriptNpkEntry] = []
        for index in range(count):
            file_id, offset, packed_size, declared_size, c1, c2, flag = NPK_ENTRY.unpack_from(table, index * NPK_ENTRY_STRIDE)
            if offset + packed_size > size:
                raise NpkFormatError(f"entry {index} packed range exceeds source")
            entries.append(ScriptNpkEntry(index, file_id, offset, packed_size, declared_size, c1, c2, flag))
        return tuple(entries)

    def source_metadata(self) -> dict[str, Any]:
        self._assert_unchanged()
        bytes_count, mtime_ns = self._signature
        return {
            "source_id": self.package_path.stem,
            "source_path": str(self.package_path),
            "package_sha256": self.package_sha256,
            "bytes": bytes_count,
            "mtime_ns": mtime_ns,
            "entry_count": len(self._entries),
            "server_branch": self.server_branch,
            "source_write_policy": "read_only",
            "index_storage": "memory_only",
        }

    def list_entries(self, offset: int = 0, limit: int = 50, query: str = "") -> dict[str, Any]:
        self._assert_unchanged()
        if offset < 0:
            raise ValueError("offset must be >= 0")
        if not 1 <= limit <= MAX_PAGE_SIZE:
            raise ValueError(f"limit must be between 1 and {MAX_PAGE_SIZE}")
        query = query.strip().upper()
        matched = self._entries
        if query:
            matched = tuple(
                entry for entry in self._entries
                if query in f"{entry.file_id:016X}" or query == str(entry.entry_index)
            )
        page = matched[offset:offset + limit]
        return {
            "source_package_sha256": self.package_sha256,
            "total": len(matched),
            "offset": offset,
            "limit": limit,
            "entries": [entry.as_public_dict() for entry in page],
        }

    def inspect_entry(self, entry_index: int) -> dict[str, Any]:
        self._assert_unchanged()
        if not 0 <= entry_index < len(self._entries):
            raise IndexError(f"entry index outside source bounds: {entry_index}")
        entry = self._entries[entry_index]
        with self.package_path.open("rb") as handle:
            handle.seek(entry.offset)
            packed = handle.read(entry.packed_size)
        if len(packed) != entry.packed_size:
            raise NpkFormatError("packed entry read short")
        decoded = _unpack_entry(packed, entry.declared_size, entry.flag)
        self._assert_unchanged()
        preview = _safe_text_preview(decoded)
        return {
            "source_package_sha256": self.package_sha256,
            "server_branch": self.server_branch,
            "source_write_policy": "read_only",
            "entry": entry.as_public_dict(),
            "decoded_bytes": len(decoded),
            "decoded_sha256": hashlib.sha256(decoded).hexdigest(),
            "payload_magic_hex": decoded[:16].hex(),
            "payload_kind": _payload_kind(decoded),
            "logical_path_direct": _parse_logical_path(decoded),
            "utf8_preview": preview["text"],
            "utf8_preview_truncated": preview["truncated"],
            "evidence_level": "package_entry_exists",
            "interpretation_boundary": "entry_exists_does_not_prove_runtime_activation",
        }
