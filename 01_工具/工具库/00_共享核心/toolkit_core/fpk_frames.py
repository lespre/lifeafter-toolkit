"""Verified sequential reader for LifeAfter FPK Zstd and stored-resource streams."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import zstandard as zstd

FPK_HEADER_SIZE = 32
ZSTD_FRAME_MAGIC = b"\x28\xb5\x2f\xfd"
MAX_INTER_ENTRY_ZERO_PADDING = 3


class FpkFrameError(ValueError):
    """Raised when an FPK stream cannot be consumed at a verified boundary."""


@dataclass(frozen=True)
class FpkFrame:
    index: int
    offset: int
    packed_size: int
    output_size: int
    output_magic: str
    storage: str = "zstd"
    padding_size: int = 0


def _output_magic(payload: bytes) -> str:
    if payload.startswith(b"DDS "):
        return "DDS"
    if payload.startswith(b"\x89PNG\r\n\x1a\n"):
        return "PNG"
    if payload.startswith(b"\xff\xd8\xff"):
        return "JPEG"
    if payload[:1] in (b"{", b"["):
        return "JSON"
    if b"\nsize: " in payload[:512] and b"\nformat:" in payload[:512]:
        return "ATLAS"
    return "OTHER"


def _fill(handle, buffer: bytes, minimum: int, chunk_size: int) -> bytes:
    while len(buffer) < minimum:
        chunk = handle.read(chunk_size)
        if not chunk:
            break
        buffer += chunk
    return buffer


def _trim_zero_padding(raw_extent: bytes) -> tuple[bytes, int]:
    """Remove only the known 1--3 byte FPK separator, preserving real binary tails."""
    padding_size = 0
    while padding_size < MAX_INTER_ENTRY_ZERO_PADDING and raw_extent.endswith(b"\x00"):
        raw_extent = raw_extent[:-1]
        padding_size += 1
    return raw_extent, padding_size


def _find_verified_next_zstd(handle, buffer: bytes, *, chunk_size: int) -> tuple[int, bytes]:
    """Find a real next frame only after a prior frame has reached eof.

    This helper is called exclusively on the bytes following an already verified
    Zstd frame.  A magic candidate is accepted only if a fresh decompressor also
    reaches eof; therefore a magic sequence inside a stored/raw payload is not
    promoted to a boundary merely by four matching bytes.
    """
    search_from = 0
    while True:
        candidate = buffer.find(ZSTD_FRAME_MAGIC, search_from)
        if candidate >= 0:
            probe = buffer[candidate:]
            obj = zstd.ZstdDecompressor().decompressobj()
            try:
                obj.decompress(probe)
            except zstd.ZstdError:
                search_from = candidate + 1
                continue
            if obj.eof:
                return candidate, buffer
            chunk = handle.read(chunk_size)
            if chunk:
                buffer += chunk
                continue
            search_from = candidate + 1
            continue

        previous_length = len(buffer)
        chunk = handle.read(chunk_size)
        if not chunk:
            return len(buffer), buffer
        buffer += chunk
        search_from = max(0, previous_length - (len(ZSTD_FRAME_MAGIC) - 1))


def iter_fpk_frames(path: Path | str, *, chunk_size: int = 8 << 20) -> Iterator[tuple[FpkFrame, bytes]]:
    """Yield sequentially verified Zstd frames and stored/raw inter-frame resources.

    Zstd frame starts are never discovered by scanning compressed bodies.  The
    iterator completes one frame to ``eof`` first.  Only then may it inspect the
    returned ``unused_data``: zero separators are skipped; nonzero bytes are
    emitted as one ``storage='raw'`` resource until the next independently
    verified Zstd frame or EOF.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    source = Path(path)
    decompressor = zstd.ZstdDecompressor()
    with source.open("rb") as handle:
        handle.seek(FPK_HEADER_SIZE)
        buffer = b""
        cursor = FPK_HEADER_SIZE
        index = 0
        while True:
            buffer = _fill(handle, buffer, 1, chunk_size)
            if not buffer:
                return

            while buffer[:1] == b"\x00":
                buffer = buffer[1:]
                cursor += 1
                buffer = _fill(handle, buffer, 1, chunk_size)
                if not buffer:
                    return

            if not buffer.startswith(ZSTD_FRAME_MAGIC):
                raw_offset = cursor
                raw_end, buffer = _find_verified_next_zstd(handle, buffer, chunk_size=chunk_size)
                if raw_end <= 0:
                    raise FpkFrameError(f"non-advancing stored resource at offset {raw_offset}")
                raw_extent = buffer[:raw_end]
                payload, padding_size = _trim_zero_padding(raw_extent)
                if payload:
                    yield FpkFrame(
                        index=index,
                        offset=raw_offset,
                        packed_size=len(raw_extent),
                        output_size=len(payload),
                        output_magic=_output_magic(payload),
                        storage="raw",
                        padding_size=padding_size,
                    ), payload
                    index += 1
                cursor += raw_end
                buffer = buffer[raw_end:]
                continue

            frame_offset = cursor
            obj = decompressor.decompressobj()
            output_parts: list[bytes] = []
            while True:
                try:
                    output_parts.append(obj.decompress(buffer))
                except zstd.ZstdError as exc:
                    raise FpkFrameError(f"Zstd decode failed at offset {frame_offset}: {exc}") from exc
                if obj.eof:
                    unused = obj.unused_data
                    frame_end = handle.tell() - len(unused)
                    if frame_end <= frame_offset:
                        raise FpkFrameError(f"non-advancing Zstd frame at offset {frame_offset}")
                    payload = b"".join(output_parts)
                    yield FpkFrame(
                        index=index,
                        offset=frame_offset,
                        packed_size=frame_end - frame_offset,
                        output_size=len(payload),
                        output_magic=_output_magic(payload),
                    ), payload
                    index += 1
                    cursor = frame_end
                    buffer = unused
                    break
                buffer = handle.read(chunk_size)
                if not buffer:
                    raise FpkFrameError(f"truncated Zstd frame at offset {frame_offset}")
