#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""只读复验一个真实 LifeAfter PC UI IDX/WPK 1DPW 条目。

固定证据链（当前 source hash 锁定）：
    ui.idx record[5] -> ui4.wpk @ 0x001DC000 -> 1DPW
    -> WPD1 tag AC -> DTSZ -> strict Zstandard -> DDS -> Pillow

源文件只读；所有派生产物仅写入本脚本所在的指定审计目录。
FPK 是另一容器层，本验证器不读取、也不对其作任何 1DPW 结论。
"""

from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import io
import json
import os
import struct
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from PIL import Image
import zstandard as zstd


SOURCE_ROOT = Path(r"E:\mrzh")
IDX_PATH = Path(r"E:\mrzh\Documents\res\ui.idx")
WPK3_PATH = Path(r"E:\mrzh\Documents\res\ui3.wpk")
WPK4_PATH = Path(r"E:\mrzh\Documents\res\ui4.wpk")
SLOT_DIR = Path(r"E:\mrzh\Documents\res\ui")
TOOL_PATH = Path(r"E:\la拆包项目\01拆包器本体\工具库\01_核心解包器\lifeafter_unpacker_full.py")
OUTPUT_ROOT = Path(r"E:\la拆包项目\03拆包产物\03_WPK_1DPW")

EXPECTED_SOURCE_SHA256 = {
    str(IDX_PATH): "cbba19c9a56e68fc0f68c6a431411aa97c329b4c8da5618eb16da765e6a8341f",
    str(WPK4_PATH): "4bd07c4f0dd8d9d9503c43eb809614e308bb4d04ccbda0e5ac5e5e5421bc07c3",
}
TARGET_RECORD_INDEX = 5  # zero-based
TARGET_HASH_HEX = "77f55b584213beb7a0f0c0410b56ec86"
IDX_HEADER_SIZE = 0x20
IDX_RECORD_SIZE = 0x24
IDX_TRAILER_SIZE = 4

PUBLIC_ALGORITHM_PROVENANCE = {
    "repository": "https://github.com/liubairun/NeoXtractor-IDXWPK",
    "commit": "64ae097d00c60bfec6e1d37076d2bcd3d0b76f02",
    "stage1_source": "core/wpk/decryption.py",
    "nested_source": "core/wpk/payload.py",
    "role": "candidate implementation only; acceptance is based on this target sample's boundaries, hashes, strict codec completion, and Pillow parse",
}


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def norm_resolved(path: Path, *, must_exist: bool) -> Path:
    return path.resolve(strict=must_exist)


def is_under(path: Path, root: Path) -> bool:
    p = os.path.normcase(str(norm_resolved(path, must_exist=path.exists())))
    r = os.path.normcase(str(norm_resolved(root, must_exist=root.exists())))
    try:
        return os.path.commonpath([p, r]) == r
    except ValueError:
        return False


def guard_source(path: Path) -> Path:
    resolved = norm_resolved(path, must_exist=True)
    require(is_under(resolved, SOURCE_ROOT), f"source escapes allowed root: {resolved}")
    require(resolved.is_file(), f"source is not a regular file: {resolved}")
    require(not path.is_symlink(), f"source symlink is prohibited: {path}")
    return resolved


def guard_tool(path: Path) -> Path:
    resolved = norm_resolved(path, must_exist=True)
    allowed = norm_resolved(TOOL_PATH.parent, must_exist=True)
    require(is_under(resolved, allowed), f"tool path escapes tool root: {resolved}")
    require(resolved.is_file(), f"tool is not a regular file: {resolved}")
    return resolved


def guard_output(path: Path) -> Path:
    root = norm_resolved(OUTPUT_ROOT, must_exist=True)
    candidate = path.resolve(strict=False)
    require(is_under(candidate, root), f"output escapes designated root: {candidate}")
    return candidate


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_snapshot(path: Path) -> dict[str, Any]:
    resolved = path.resolve(strict=True)
    before = resolved.stat()
    digest = sha256_file(resolved)
    after = resolved.stat()
    return {
        "path": str(resolved),
        "size": after.st_size,
        "mtime_ns": after.st_mtime_ns,
        "sha256": digest,
        "stable_during_hash": (
            before.st_size == after.st_size
            and before.st_mtime_ns == after.st_mtime_ns
        ),
    }


def write_bytes(path: Path, data: bytes) -> None:
    dst = guard_output(path)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(data)


def write_text(path: Path, text: str, *, newline: str | None = None) -> None:
    dst = guard_output(path)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("w", encoding="utf-8", newline=newline) as stream:
        stream.write(text)


def read_u32(data: bytes, offset: int) -> int:
    require(offset >= 0 and offset + 4 <= len(data), f"u32 out of range at {offset}")
    return struct.unpack_from("<I", data, offset)[0]


def parse_idx(idx_data: bytes) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    require(idx_data[:4] == b"SKPW", f"bad IDX magic: {idx_data[:4].hex()}")
    require(len(idx_data) >= IDX_HEADER_SIZE + IDX_TRAILER_SIZE, "IDX too small")
    declared_count = read_u32(idx_data, 0x0C)
    expected_size = IDX_HEADER_SIZE + declared_count * IDX_RECORD_SIZE + IDX_TRAILER_SIZE
    require(
        len(idx_data) == expected_size,
        f"IDX size mismatch: actual={len(idx_data)} expected={expected_size}",
    )
    size_derived_count = (len(idx_data) - IDX_HEADER_SIZE - IDX_TRAILER_SIZE) // IDX_RECORD_SIZE
    require(size_derived_count == declared_count, "IDX header/size record counts disagree")

    records: list[dict[str, Any]] = []
    for index in range(declared_count):
        rec_offset = IDX_HEADER_SIZE + index * IDX_RECORD_SIZE
        rec = idx_data[rec_offset : rec_offset + IDX_RECORD_SIZE]
        require(len(rec) == IDX_RECORD_SIZE, f"IDX record {index} truncated")
        raw_hash = rec[:16]
        field_0x10, pkg_raw, file_offset, payload_size, header_field = struct.unpack_from(
            "<IIIII", rec, 0x10
        )
        records.append(
            {
                "index_zero_based": index,
                "idx_record_offset": rec_offset,
                "raw_record": rec,
                "hash_bytes": raw_hash,
                "hash_hex": raw_hash.hex(),
                "field_0x10": field_0x10,
                "pkg_raw": pkg_raw,
                "pkg_low8": pkg_raw & 0xFF,
                "file_offset": file_offset,
                "payload_size": payload_size,
                "header_field": header_field,
                "header_size": header_field & 0xFFFF,
                "header_high16": header_field >> 16,
            }
        )

    summary = {
        "magic_ascii": idx_data[:4].decode("ascii"),
        "header_size": IDX_HEADER_SIZE,
        "record_size": IDX_RECORD_SIZE,
        "declared_record_count": declared_count,
        "size_derived_record_count": size_derived_count,
        "file_size": len(idx_data),
        "expected_size_formula": f"0x20 + {declared_count} * 0x24 + 4 = {expected_size}",
        "header_hex": idx_data[:IDX_HEADER_SIZE].hex(),
        "trailer_hex": idx_data[-IDX_TRAILER_SIZE:].hex(),
        "pkg_low8_counts": dict(sorted(Counter(r["pkg_low8"] for r in records).items())),
        "header_size_counts": dict(sorted(Counter(r["header_size"] for r in records).items())),
    }
    return records, summary


def resolve_record_source(record: dict[str, Any]) -> tuple[str, Path]:
    pkg = record["pkg_low8"]
    if pkg == 0xFF:
        return "slot_file", SLOT_DIR / record["hash_hex"]
    return "wpk", IDX_PATH.parent / f"ui{pkg}.wpk"


def inventory_sources(records: list[dict[str, Any]]) -> dict[str, Any]:
    package_paths: dict[int, Path] = {}
    slot_total = 0
    slot_existing = 0
    slot_magic_1dpw = 0
    missing: list[str] = []

    for record in records:
        kind, path = resolve_record_source(record)
        if kind == "slot_file":
            slot_total += 1
            if path.is_file():
                guard_source(path)
                slot_existing += 1
                with path.open("rb") as stream:
                    if stream.read(4) == b"1DPW":
                        slot_magic_1dpw += 1
            else:
                missing.append(str(path))
        else:
            package_paths[record["pkg_low8"]] = path

    packages: list[dict[str, Any]] = []
    for pkg, path in sorted(package_paths.items()):
        exists = path.is_file()
        magic = None
        size = None
        if exists:
            guard_source(path)
            size = path.stat().st_size
            with path.open("rb") as stream:
                magic = stream.read(4).decode("ascii", errors="backslashreplace")
        else:
            missing.append(str(path))
        packages.append(
            {
                "pkg_low8": pkg,
                "path": str(path.resolve(strict=False)),
                "exists": exists,
                "size": size,
                "magic_ascii": magic,
            }
        )

    return {
        "packages": packages,
        "slot_file": {
            "directory": str(SLOT_DIR.resolve(strict=True)),
            "indexed_records": slot_total,
            "existing_files": slot_existing,
            "files_starting_1DPW": slot_magic_1dpw,
        },
        "missing_sources": missing,
        "all_indexed_sources_resolved": not missing,
    }


def derive_wpd1_key(body_len: int, t_value: int) -> bytes:
    require(body_len >= 0, "negative WPD1 body length")
    v10 = (t_value + (body_len & 0xFFFFFFFF)) & 0xFF
    v28 = (
        0x7C2E6B6A00000000
        | (((body_len & 0xFFFFFFFF) << 8) & 0xFFFF0000)
        | (v10 << 8)
        | (body_len % 0xFD)
    )
    v29 = (
        0x5C74656E00003630
        | (((v10 ^ 0x33) << 16) & 0xFFFFFFFF00FFFFFF)
        | ((v10 | 0x2E) << 24)
    )
    return struct.pack("<QQ", v28 & 0xFFFFFFFFFFFFFFFF, v29 & 0xFFFFFFFFFFFFFFFF)


def aes_decrypt_prefix(buf: bytearray, wanted: int, key16: bytes) -> int:
    require(len(key16) == 16, "AES key must be 16 bytes")
    done = (wanted // 16) * 16
    if done <= 0:
        return 0
    decryptor = Cipher(algorithms.AES(key16), modes.ECB()).decryptor()
    buf[:done] = decryptor.update(bytes(buf[:done])) + decryptor.finalize()
    return done


def xor_offset(buf: bytearray, offset: int, wanted: int, seed: int) -> None:
    mirror_len = min(offset, wanted)
    for i in range(mirror_len):
        buf[offset + i] ^= ((seed + i) + buf[i]) & 0xFF
    for i in range(wanted - mirror_len):
        buf[offset + mirror_len + i] ^= (seed + mirror_len + i) & 0xFF


def header_decode(buf: bytearray) -> None:
    n = min(64, len(buf))
    buf[:n] = bytes(value ^ 0x5A for value in buf[:n][::-1])


def decode_wpd1_stage1(
    payload: bytes,
    *,
    apply_header_transform: bool,
    kdf_body_len_override: int | None = None,
    key_override: bytes | None = None,
) -> tuple[bytes, dict[str, Any]]:
    require(len(payload) >= 8, "WPD1 payload shorter than 8-byte control header")
    tag = int.from_bytes(payload[:2], "little")
    p_value = payload[2]
    t_value = payload[3]
    aux4 = payload[4:8]
    body = bytearray(payload[8:])
    actual_body_len = len(body)
    prefix_len = (
        min(actual_body_len, 128 << (p_value - 1))
        if actual_body_len > 0 and p_value != 0
        else 0
    )
    seed = (t_value + actual_body_len) & 0xFFFFFFFF
    kdf_body_len = actual_body_len if kdf_body_len_override is None else kdf_body_len_override
    key16 = key_override if key_override is not None else derive_wpd1_key(kdf_body_len, t_value)

    if tag in (0x4341, 0x4350):
        aes_done = aes_decrypt_prefix(body, prefix_len, key16)
        remaining = max(0, prefix_len - aes_done)
        if remaining:
            xor_offset(body, aes_done, remaining, seed)
    elif tag == 0x4358:
        aes_done = 0
        for i in range(prefix_len):
            body[i] ^= (seed + i) & 0xFF
    else:
        raise AuditError(f"unsupported WPD1 tag 0x{tag:04X}")

    if apply_header_transform:
        header_decode(body)

    trace = {
        "tag_u16le": tag,
        "tag_ascii": payload[:2].decode("ascii", errors="backslashreplace"),
        "p": p_value,
        "t": t_value,
        "aux4_hex_neutral_name": aux4.hex(),
        "actual_body_len": actual_body_len,
        "kdf_body_len": kdf_body_len,
        "derived_or_override_key_hex": key16.hex(),
        "prefix_len": prefix_len,
        "aes_aligned_bytes": aes_done,
        "xor_tail_bytes": max(0, prefix_len - aes_done),
        "header_reverse_xor_5a_applied": apply_header_transform,
        "output_size": len(body),
        "output_head16_hex": bytes(body[:16]).hex(),
        "output_sha256": sha256_bytes(bytes(body)),
    }
    return bytes(body), trace


def strict_dtsz_decompress(stage1: bytes) -> tuple[bytes, dict[str, Any]]:
    require(stage1[:4] == b"DTSZ", f"stage1 is not DTSZ: {stage1[:8].hex()}")
    frame = stage1[4:]
    require(frame[:4] == b"\x28\xB5\x2F\xFD", f"bad Zstd frame magic: {frame[:4].hex()}")
    params = zstd.get_frame_parameters(frame)
    obj = zstd.ZstdDecompressor().decompressobj()
    decoded = obj.decompress(frame) + obj.flush()
    trace = {
        "wrapper_ascii": "DTSZ",
        "wrapper_size": len(stage1),
        "zstd_frame_size": len(frame),
        "zstd_frame_magic_hex": frame[:4].hex(),
        "frame_content_size": params.content_size,
        "frame_window_size": params.window_size,
        "frame_dict_id": params.dict_id,
        "frame_has_checksum": params.has_checksum,
        "decompressor_eof": bool(obj.eof),
        "unused_data_size": len(obj.unused_data),
        "decoded_size": len(decoded),
        "decoded_sha256": sha256_bytes(decoded),
    }
    require(obj.eof, "Zstd frame did not reach EOF")
    require(len(obj.unused_data) == 0, "Zstd frame has trailing unused data")
    require(params.content_size == len(decoded), "Zstd frame content size mismatch")
    return decoded, trace


def inspect_image_bytes(data: bytes) -> dict[str, Any]:
    verify_stream = io.BytesIO(data)
    with Image.open(verify_stream) as image:
        fmt_verify = image.format
        image.verify()

    load_stream = io.BytesIO(data)
    with Image.open(load_stream) as image:
        image.load()
        fmt = image.format
        size = list(image.size)
        mode = image.mode
        frames = int(getattr(image, "n_frames", 1))
        rgba = image.convert("RGBA")
        pixel_bytes = rgba.tobytes()
        pixel_sha = sha256_bytes(pixel_bytes)
        pixel_count = rgba.width * rgba.height
        rgba_values = {
            pixel_bytes[offset : offset + 4]
            for offset in range(0, len(pixel_bytes), 4)
        }
        alpha_values = pixel_bytes[3::4]
        nontransparent = sum(1 for alpha in alpha_values if alpha != 0)
        nonblack_rgb = sum(
            1
            for offset in range(0, len(pixel_bytes), 4)
            if pixel_bytes[offset] or pixel_bytes[offset + 1] or pixel_bytes[offset + 2]
        )

    return {
        "pillow_verify_pass": True,
        "pillow_load_pass": True,
        "format_verify": fmt_verify,
        "format_load": fmt,
        "width": size[0],
        "height": size[1],
        "mode": mode,
        "frames": frames,
        "rgba_pixel_sha256": pixel_sha,
        "pixel_count": pixel_count,
        "unique_rgba_colors": len(rgba_values),
        "alpha_min": min(alpha_values),
        "alpha_max": max(alpha_values),
        "nontransparent_pixels": nontransparent,
        "nonblack_rgb_pixels": nonblack_rgb,
        "not_pure_blank_by_pixel_stats": len(rgba_values) > 1 and nontransparent > 0,
    }


def probe_negative_output(data: bytes) -> dict[str, Any]:
    wrapper = data[:4]
    known_wrapper = wrapper in (b"DTSZ", b"ENON")
    strict_nested_success = False
    final = data
    nested_error = None
    if wrapper == b"DTSZ":
        try:
            final, _ = strict_dtsz_decompress(data)
            strict_nested_success = True
        except Exception as exc:  # expected for a negative control if magic collides
            nested_error = repr(exc)
    elif wrapper == b"ENON":
        final = data[4:]
        strict_nested_success = True

    image_success = False
    image_error_type = None
    try:
        inspect_image_bytes(final)
        image_success = True
    except Exception as exc:  # expected
        # Exception repr/str may embed a BytesIO memory address. Persist only
        # the stable exception class so two identical runs hash identically.
        image_error_type = type(exc).__name__

    accepted_pipeline = known_wrapper and strict_nested_success and image_success
    return {
        "output_size": len(data),
        "output_head16_hex": data[:16].hex(),
        "output_sha256": sha256_bytes(data),
        "known_wrapper_at_offset_0": known_wrapper,
        "strict_nested_success": strict_nested_success,
        "nested_error": nested_error,
        "pillow_image_success": image_success,
        "image_error_type": image_error_type,
        "accepted_pipeline": accepted_pipeline,
        "negative_control_pass": not accepted_pipeline,
    }


def audit_existing_tool() -> dict[str, Any]:
    tool = guard_tool(TOOL_PATH)
    snap = source_snapshot(tool)
    text = tool.read_text(encoding="utf-8")
    old_slice = "blk = wpk[off:off + size]" in text
    strips_48 = "data = blk[48:] if blk[:4] == b'1DPW' else blk" in text
    decoder_markers = {
        "derive_wpd1_key": "derive_wpd1_key" in text or "def derive_key" in text,
        "decode_payload_stage1": "decode_payload_stage1" in text,
        "DTSZ": "DTSZ" in text,
        "ENON": "ENON" in text,
    }
    return {
        "classification": "auxiliary tool-code audit; not a game-data fact source",
        "snapshot": snap,
        "parse_wpk_idx_present": "def parse_wpk_idx" in text,
        "payload_size_used_as_total_slice": old_slice,
        "blind_48_byte_strip_present": strips_48,
        "stage1_decoder_markers": decoder_markers,
        "reusable_for_this_cryptographic_verification": all(decoder_markers.values()),
        "decision": (
            "not reused for WPD1/AC: this snapshot only slices/strips 1DPW and has no AC/PC stage-1 or DTSZ/ENON decoder"
            if not all(decoder_markers.values())
            else "decoder markers present; manual review still required"
        ),
    }


def artifact_row(path: Path, layer: str, description: str) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "layer": layer,
        "description": description,
        "relative_path": path.relative_to(OUTPUT_ROOT).as_posix(),
        "absolute_path": str(path.resolve(strict=True)),
        "size": len(data),
        "sha256": sha256_bytes(data),
        "head16_hex": data[:16].hex(),
    }


def render_markdown(report: dict[str, Any]) -> str:
    target = report["target_record"]
    chain = report["decode_chain"]
    final = chain["final_resource"]
    checks = report["acceptance_checks"]
    negatives = report["negative_controls"]
    source_rows = report["source_snapshots"]
    artifact_rows = report["artifacts"]

    lines = [
        "# PC WPK 真实 1DPW 条目独立复验报告",
        "",
        f"**结论：{report['verdict']}**",
        "",
        report["conclusion_zh"],
        "",
        "## 范围与证据边界",
        "",
        "- 只读事实源：`E:/mrzh`。",
        "- 固定复验 1 条当前 UI IDX 记录，不作 4811 条全量解码覆盖声明。",
        "- 本条链路为 `IDX → ui4.wpk → 1DPW → AC → DTSZ → Zstandard → DDS → Pillow`。",
        "- 未启动客户端，未修改任何原始文件。",
        "- **FPK 是另一容器层；本次未读取 FPK，绝不作“FPK=1DPW”表述。**",
        "- 本样本不覆盖 3 条 PC tag，也不覆盖 ENON 分支；只证明当前哈希锁定 AC/DTSZ 实例及其 1DPW 层已被真实解开。",
        "",
        "## 源锁",
        "",
        "| 路径 | 大小 | SHA-256 | 哈希期间稳定 |",
        "|---|---:|---|---|",
    ]
    for row in source_rows:
        lines.append(
            f"| `{row['path']}` | {row['size']} | `{row['sha256']}` | {row['stable_during_hash']} |"
        )

    lines.extend(
        [
            "",
            "## IDX 与物理边界",
            "",
            f"- IDX：头 `0x20`，记录 `0x24`，声明/按长度推导均为 **{report['idx']['declared_record_count']}** 条，尾部 4 字节。",
            f"- 目标：零基序号 **{target['index_zero_based']}**，IDX 记录偏移 `{target['idx_record_offset_hex']}`，hash `{target['hash_hex']}`。",
            f"- 来源：`{target['source_path']}`，pkg raw `{target['pkg_raw_hex']}` / low8 `{target['pkg_low8']}`。",
            f"- WPK 偏移 `{target['file_offset_hex']}`；头长 `{target['header_size']}`；payload `{target['payload_size']}`；总读取 `{target['total_read_size']}`。",
            f"- `header_field={target['header_field_hex']}`：low16=`0x{target['header_size']:04X}`，high16 padding={target['header_high16']}。",
            f"- 精确条目结束 `{target['entry_end_hex']}`；补零后 `{target['padded_end_hex']}`；下一条 `{target['next_offset_hex']}` 且 magic=`{target['next_magic_ascii']}`。",
            f"- padding 全零：{target['padding_all_zero']}；padding SHA-256 `{target['padding_sha256']}`。",
            "",
            "## 完整解码链",
            "",
            "| 层 | 大小 | 头部 | SHA-256 |",
            "|---|---:|---|---|",
        ]
    )
    for row in artifact_rows:
        lines.append(
            f"| {row['layer']} | {row['size']} | `{row['head16_hex']}` | `{row['sha256']}` |"
        )
    lines.extend(
        [
            "",
            f"- WPD1：tag `{chain['stage1']['tag_ascii']}` / `0x{chain['stage1']['tag_u16le']:04X}`，p={chain['stage1']['p']}，t={chain['stage1']['t']}。",
            f"- body_len={chain['stage1']['actual_body_len']}，AES 前缀={chain['stage1']['aes_aligned_bytes']} 字节，key=`{chain['stage1']['derived_or_override_key_hex']}`。",
            f"- stage-1 首部恢复为 `DTSZ 28 B5 2F FD`；Zstd eof={chain['nested']['decompressor_eof']}，unused={chain['nested']['unused_data_size']}，frame content size={chain['nested']['frame_content_size']}。",
            f"- 最终 DDS：{final['width']}×{final['height']}，mode={final['mode']}；Pillow verify={final['pillow_verify_pass']} / load={final['pillow_load_pass']}。",
            f"- 像素验收：{final['unique_rgba_colors']} 种 RGBA，非透明 {final['nontransparent_pixels']}/{final['pixel_count']}，非黑 RGB {final['nonblack_rgb_pixels']}；不是纯空白={final['not_pure_blank_by_pixel_stats']}。",
            "",
            "## 负对照",
            "",
            "| 对照 | 输出头 | 命中完整 pipeline | 对照通过 |",
            "|---|---|---|---|",
        ]
    )
    for name, row in negatives.items():
        lines.append(
            f"| `{name}` | `{row.get('output_head16_hex', row.get('observed_magic_hex', ''))}` | {row.get('accepted_pipeline', False)} | {row['negative_control_pass']} |"
        )
    lines.extend(
        [
            "",
            "关键负对照包括：把 IDX `payload_size` 错当总长（少读 0x30）、错误 KDF body length、零 AES key、跳过 AC 64 字节头变换、条目偏移 +1。它们均未通过 wrapper→codec→Pillow 完整验收。",
            "",
            "## 现有工具审计",
            "",
            f"- 工具 SHA-256：`{report['existing_tool_audit']['snapshot']['sha256']}`。",
            f"- 结论：{report['existing_tool_audit']['decision']}。",
            "- 因此未把该脚本的“切出 1DPW”冒充解密成功；专项验证器内置并逐层验收 WPD1 算法。",
            "",
            "## 验收检查",
            "",
        ]
    )
    for name, value in checks.items():
        lines.append(f"- {'PASS' if value else 'FAIL'} — `{name}`")
    lines.extend(
        [
            "",
            "## 复跑",
            "",
            "```bat",
            r"py -3 E:\la拆包项目\01拆包器本体\工具库\03_WPK_1DPW\verify_1dpw_entry.py",
            "```",
            "",
            "源 SHA 不同会硬失败，不会静默套用旧 offset。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    script_path = Path(__file__).resolve(strict=True)
    expected_output = OUTPUT_ROOT.resolve(strict=True)
    require(script_path.parent == expected_output, f"verifier must run from designated root: {expected_output}")

    idx_path = guard_source(IDX_PATH)
    wpk4_path = guard_source(WPK4_PATH)
    guard_source(WPK3_PATH)

    source_start = [source_snapshot(idx_path), source_snapshot(wpk4_path)]
    for snap in source_start:
        expected = EXPECTED_SOURCE_SHA256.get(str(Path(snap["path"])))
        require(expected is not None, f"no source lock configured for {snap['path']}")
        require(snap["sha256"] == expected, f"source SHA mismatch for {snap['path']}: {snap['sha256']}")
        require(snap["stable_during_hash"], f"source changed while hashing: {snap['path']}")

    idx_data = idx_path.read_bytes()
    records, idx_summary = parse_idx(idx_data)
    source_inventory = inventory_sources(records)
    require(source_inventory["all_indexed_sources_resolved"], "one or more IDX sources are missing")
    require(all(row["magic_ascii"] == "FKPW" for row in source_inventory["packages"]), "one or more WPK packages lack FKPW")

    require(TARGET_RECORD_INDEX < len(records), "target record index out of range")
    record = records[TARGET_RECORD_INDEX]
    require(record["hash_hex"] == TARGET_HASH_HEX, "target record hash no longer matches source lock")
    source_kind, source_path = resolve_record_source(record)
    require(source_kind == "wpk", "target unexpectedly resolved to slot_file")
    source_path = guard_source(source_path)
    require(source_path == wpk4_path, f"target source is not ui4.wpk: {source_path}")

    wpk_size = source_path.stat().st_size
    with source_path.open("rb") as stream:
        wpk_magic = stream.read(4)
    require(wpk_magic == b"FKPW", f"bad WPK magic: {wpk_magic.hex()}")

    header_size = record["header_size"]
    payload_size = record["payload_size"]
    total_size = header_size + payload_size
    entry_start = record["file_offset"]
    entry_end = entry_start + total_size
    high16 = record["header_high16"]
    computed_padding = (-total_size) % 4096
    padded_end = entry_end + high16
    require(header_size == 0x30, f"unexpected 1DPW header size: {header_size}")
    require(entry_start % 4096 == 0, "entry start is not 4 KiB aligned")
    require(entry_end <= wpk_size, "entry exceeds WPK")
    require(computed_padding == high16, "header high16 does not match 4 KiB padding")
    require(padded_end % 4096 == 0, "padded end is not 4 KiB aligned")

    same_pkg_offsets = sorted(
        {r["file_offset"] for r in records if r["pkg_low8"] == record["pkg_low8"]}
    )
    pos = same_pkg_offsets.index(entry_start)
    previous_offset = same_pkg_offsets[pos - 1] if pos > 0 else None
    next_offset = same_pkg_offsets[pos + 1] if pos + 1 < len(same_pkg_offsets) else wpk_size
    require(next_offset == padded_end, f"next physical boundary mismatch: {next_offset} != {padded_end}")

    with source_path.open("rb") as stream:
        stream.seek(entry_start)
        raw_entry = stream.read(total_size)
        padding = stream.read(high16)
        next_magic = stream.read(4) if next_offset < wpk_size else b"EOF"
    require(len(raw_entry) == total_size, "short exact entry read")
    require(len(padding) == high16, "short padding read")
    require(not any(padding), "nonzero bytes in expected inter-entry padding")
    require(next_magic == b"1DPW", f"next entry magic mismatch: {next_magic.hex()}")

    header = raw_entry[:header_size]
    payload = raw_entry[header_size : header_size + payload_size]
    require(len(payload) == payload_size, "payload slice length mismatch")
    require(header[:4] == b"1DPW", f"bad embedded magic: {header[:4].hex()}")
    embedded_version = read_u32(header, 0x04)
    embedded_hash = header[0x08:0x18]
    embedded_field_0x18 = read_u32(header, 0x18)
    embedded_aux_0x1c = read_u32(header, 0x1C)
    embedded_payload_size = read_u32(header, 0x20)
    embedded_header_field = read_u32(header, 0x24)
    embedded_reserved_0x28 = header[0x28:0x30]
    require(embedded_version == 2, f"unexpected 1DPW version: {embedded_version}")
    require(embedded_hash == record["hash_bytes"], "IDX hash != embedded 1DPW hash")
    require(embedded_payload_size == payload_size, "IDX payload_size != 1DPW +0x20")
    require(embedded_header_field == record["header_field"], "IDX header_field != 1DPW +0x24")
    require(embedded_reserved_0x28 == b"\x00" * 8, "unexpected nonzero 1DPW reserved tail")

    tag = int.from_bytes(payload[:2], "little")
    require(tag == 0x4341, f"target is not AC: 0x{tag:04X}")
    stage1, stage1_trace = decode_wpd1_stage1(payload, apply_header_transform=True)
    require(stage1[:8] == b"DTSZ\x28\xB5\x2F\xFD", f"stage1 wrapper mismatch: {stage1[:8].hex()}")

    final_resource, nested_trace = strict_dtsz_decompress(stage1)
    require(final_resource[:4] == b"DDS ", f"final resource is not DDS: {final_resource[:8].hex()}")
    final_image = inspect_image_bytes(final_resource)
    require(final_image["format_load"] == "DDS", f"Pillow format is not DDS: {final_image['format_load']}")
    dds_header_size = read_u32(final_resource, 0x04)
    dds_height = read_u32(final_resource, 0x0C)
    dds_width = read_u32(final_resource, 0x10)
    require(dds_header_size == 124, f"bad DDS header size: {dds_header_size}")
    require([dds_width, dds_height] == [final_image["width"], final_image["height"]], "DDS/Pillow dimensions disagree")

    # Negative controls. These must fail the complete wrapper -> codec -> Pillow pipeline.
    with source_path.open("rb") as stream:
        stream.seek(entry_start)
        wrong_total_raw = stream.read(payload_size)  # historical bug: payload_size treated as total_size
    wrong_total_payload = wrong_total_raw[header_size:]
    wrong_total_stage1, wrong_total_trace = decode_wpd1_stage1(
        wrong_total_payload, apply_header_transform=True
    )
    negative_controls: dict[str, dict[str, Any]] = {}
    negative_controls["payload_size_misread_as_total_minus_0x30"] = {
        "wrong_raw_read_size": len(wrong_total_raw),
        "wrong_payload_size_after_header": len(wrong_total_payload),
        "wrong_body_len": wrong_total_trace["actual_body_len"],
        **probe_negative_output(wrong_total_stage1),
    }

    wrong_kdf, wrong_kdf_trace = decode_wpd1_stage1(
        payload,
        apply_header_transform=True,
        kdf_body_len_override=stage1_trace["actual_body_len"] - 1,
    )
    negative_controls["kdf_body_len_minus_1"] = {
        "wrong_kdf_body_len": wrong_kdf_trace["kdf_body_len"],
        **probe_negative_output(wrong_kdf),
    }

    zero_key, _ = decode_wpd1_stage1(
        payload,
        apply_header_transform=True,
        key_override=b"\x00" * 16,
    )
    negative_controls["zero_aes_key"] = probe_negative_output(zero_key)

    no_header_transform, _ = decode_wpd1_stage1(
        payload,
        apply_header_transform=False,
    )
    negative_controls["skip_ac_reverse_xor_5a"] = probe_negative_output(no_header_transform)

    with source_path.open("rb") as stream:
        stream.seek(entry_start + 1)
        plus_one_magic = stream.read(4)
    negative_controls["entry_offset_plus_1"] = {
        "observed_magic_hex": plus_one_magic.hex(),
        "expected_1DPW": False,
        "negative_control_pass": plus_one_magic != b"1DPW",
    }
    require(
        all(row["negative_control_pass"] for row in negative_controls.values()),
        "one or more negative controls unexpectedly passed",
    )

    artifacts_dir = guard_output(OUTPUT_ROOT / "artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{TARGET_RECORD_INDEX:06d}_{TARGET_HASH_HEX}"
    outer_path = artifacts_dir / f"{stem}_outer.1dpw"
    payload_path = artifacts_dir / f"{stem}_payload.wpd1"
    stage1_path = artifacts_dir / f"{stem}_stage1.dtsz"
    final_path = artifacts_dir / f"{stem}_final.dds"
    preview_path = artifacts_dir / f"{stem}_preview.png"
    write_bytes(outer_path, raw_entry)
    write_bytes(payload_path, payload)
    write_bytes(stage1_path, stage1)
    write_bytes(final_path, final_resource)

    with Image.open(io.BytesIO(final_resource)) as image:
        image.load()
        rgba = image.convert("RGBA")
        rgba.save(preview_path, format="PNG", compress_level=9, optimize=False)
    preview_info = inspect_image_bytes(preview_path.read_bytes())
    require(preview_info["format_load"] == "PNG", "preview is not PNG")
    require(
        [preview_info["width"], preview_info["height"]]
        == [final_image["width"], final_image["height"]],
        "preview dimensions differ from DDS",
    )
    require(
        preview_info["rgba_pixel_sha256"] == final_image["rgba_pixel_sha256"],
        "preview pixels differ from decoded DDS pixels",
    )

    artifacts = [
        artifact_row(outer_path, "1DPW outer entry", "exact header_size + payload_size slice from ui4.wpk"),
        artifact_row(payload_path, "WPD1 payload", "payload beginning with AC control header"),
        artifact_row(stage1_path, "stage-1 decoded", "DTSZ wrapper plus complete Zstandard frame"),
        artifact_row(final_path, "final resource", "strictly decompressed DDS resource"),
        artifact_row(preview_path, "derived preview", "deterministic PNG conversion; pixels hash-match DDS decode"),
    ]

    manifest_path = OUTPUT_ROOT / "artifact_manifest.csv"
    fieldnames = ["layer", "description", "relative_path", "absolute_path", "size", "sha256", "head16_hex"]
    manifest_buffer = io.StringIO(newline="")
    writer = csv.DictWriter(manifest_buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(artifacts)
    manifest_text = manifest_buffer.getvalue()
    write_text(manifest_path, manifest_text, newline="")

    tool_audit = audit_existing_tool()

    # Re-hash both actual fact sources at end to prove the snapshot stayed fixed for the run.
    source_end = [source_snapshot(idx_path), source_snapshot(wpk4_path)]
    end_by_path = {row["path"]: row for row in source_end}
    source_stable_end_to_end = True
    for start in source_start:
        end = end_by_path[start["path"]]
        if (
            start["sha256"] != end["sha256"]
            or start["size"] != end["size"]
            or start["mtime_ns"] != end["mtime_ns"]
            or not end["stable_during_hash"]
        ):
            source_stable_end_to_end = False
    require(source_stable_end_to_end, "fact source changed during verification")

    target_report = {
        "index_zero_based": TARGET_RECORD_INDEX,
        "idx_record_offset": record["idx_record_offset"],
        "idx_record_offset_hex": f"0x{record['idx_record_offset']:X}",
        "idx_record_sha256": sha256_bytes(record["raw_record"]),
        "hash_hex": record["hash_hex"],
        "field_0x10": record["field_0x10"],
        "pkg_raw": record["pkg_raw"],
        "pkg_raw_hex": f"0x{record['pkg_raw']:08X}",
        "pkg_low8": record["pkg_low8"],
        "source_kind": source_kind,
        "source_path": str(source_path),
        "wpk_magic_ascii": wpk_magic.decode("ascii"),
        "wpk_size": wpk_size,
        "file_offset": entry_start,
        "file_offset_hex": f"0x{entry_start:08X}",
        "payload_size": payload_size,
        "header_field": record["header_field"],
        "header_field_hex": f"0x{record['header_field']:08X}",
        "header_size": header_size,
        "header_high16": high16,
        "computed_4k_padding": computed_padding,
        "total_read_size": total_size,
        "entry_end": entry_end,
        "entry_end_hex": f"0x{entry_end:08X}",
        "padded_end": padded_end,
        "padded_end_hex": f"0x{padded_end:08X}",
        "previous_offset": previous_offset,
        "previous_offset_hex": f"0x{previous_offset:08X}" if previous_offset is not None else None,
        "next_offset": next_offset,
        "next_offset_hex": f"0x{next_offset:08X}",
        "next_magic_ascii": next_magic.decode("ascii"),
        "padding_size": len(padding),
        "padding_all_zero": not any(padding),
        "padding_sha256": sha256_bytes(padding),
        "embedded_1dpw": {
            "magic_ascii": header[:4].decode("ascii"),
            "version": embedded_version,
            "hash_hex": embedded_hash.hex(),
            "field_0x18": embedded_field_0x18,
            "aux_0x1c_u32_neutral_name": embedded_aux_0x1c,
            "payload_size_at_0x20": embedded_payload_size,
            "header_field_at_0x24": embedded_header_field,
            "reserved_0x28_hex": embedded_reserved_0x28.hex(),
            "header_sha256": sha256_bytes(header),
        },
    }

    final_report = {
        **final_image,
        "magic_ascii": final_resource[:4].decode("ascii"),
        "size_bytes": len(final_resource),
        "sha256": sha256_bytes(final_resource),
        "dds_header_size": dds_header_size,
        "dds_declared_width": dds_width,
        "dds_declared_height": dds_height,
        "preview": preview_info,
    }

    acceptance_checks = {
        "source_sha_locks_match": all(
            row["sha256"] == EXPECTED_SOURCE_SHA256[str(Path(row["path"]))]
            for row in source_start
        ),
        "source_stable_end_to_end": source_stable_end_to_end,
        "idx_magic_layout_count_and_trailer": (
            idx_summary["magic_ascii"] == "SKPW"
            and idx_summary["declared_record_count"] == idx_summary["size_derived_record_count"]
        ),
        "all_idx_wpk_and_slot_sources_resolved": source_inventory["all_indexed_sources_resolved"],
        "target_idx_hash_and_pkg_match": record["hash_hex"] == TARGET_HASH_HEX and record["pkg_low8"] == 4,
        "wpk_and_embedded_magics_match": wpk_magic == b"FKPW" and header[:4] == b"1DPW",
        "payload_size_excludes_0x30_header": len(raw_entry) == header_size + payload_size,
        "idx_and_embedded_1dpw_fields_match": (
            embedded_hash == record["hash_bytes"]
            and embedded_payload_size == payload_size
            and embedded_header_field == record["header_field"]
        ),
        "entry_padding_and_next_boundary_match": (
            high16 == computed_padding and padded_end == next_offset and not any(padding) and next_magic == b"1DPW"
        ),
        "wpd1_ac_stage1_restores_dtsz": stage1[:8] == b"DTSZ\x28\xB5\x2F\xFD",
        "zstd_strict_eof_no_unused_and_size_match": (
            nested_trace["decompressor_eof"]
            and nested_trace["unused_data_size"] == 0
            and nested_trace["frame_content_size"] == len(final_resource)
        ),
        "final_dds_manual_header_and_pillow_parse": (
            final_resource[:4] == b"DDS "
            and dds_header_size == 124
            and final_image["pillow_verify_pass"]
            and final_image["pillow_load_pass"]
        ),
        "final_dds_not_pure_blank_by_pixel_stats": final_image[
            "not_pure_blank_by_pixel_stats"
        ],
        "preview_pixels_match_final_dds": (
            preview_info["rgba_pixel_sha256"] == final_image["rgba_pixel_sha256"]
        ),
        "all_negative_controls_rejected": all(
            row["negative_control_pass"] for row in negative_controls.values()
        ),
        "all_artifacts_read_back_with_hashes": all(
            sha256_file(Path(row["absolute_path"])) == row["sha256"] for row in artifacts
        ),
    }
    all_acceptance_pass = all(acceptance_checks.values())
    require(all_acceptance_pass, "one or more acceptance checks failed")

    report: dict[str, Any] = {
        "schema_version": 1,
        "audit_id": "run_004_PC_BinDict与1DPW专项_001/03_1dpw",
        "status": "PASS",
        "verdict": "PASS — 当前哈希锁定真实 WPK 条目的 1DPW/WPD1 AC 层已被事实性解开",
        "conclusion_zh": (
            "对当前 ui.idx SHA-256 锁定快照中的零基记录 5，已从 ui4.wpk 精确读取 0x30+275 字节，"
            "恢复 AC stage-1 的 DTSZ/Zstandard 数据，并严格解出可由 Pillow verify+load 的 240×184 DDS。"
            "正确链通过且五项负对照全部失败，因此这不是只切出 1DPW 外壳或偶然 magic 命中；"
            "该真实 AC/DTSZ 实例的 1DPW 层事实上已破解。"
        ),
        "claim_boundary": {
            "proven": "one current real PC ui4.wpk 1DPW AC/DTSZ entry, with final DDS parser validation",
            "not_proven": [
                "full decode coverage of all current 4811 UI IDX records",
                "the PC-tag branch (3 records in exploratory inventory, not selected here)",
                "the ENON branch",
                "any FPK decoding or relation between FPK and 1DPW",
                "runtime/client behavior",
            ],
        },
        "execution_boundary": {
            "fact_source_root_read_only": str(SOURCE_ROOT.resolve(strict=True)),
            "output_root": str(OUTPUT_ROOT.resolve(strict=True)),
            "client_started": False,
            "source_modified": False,
            "target_payload_executed_or_imported": False,
            "fpk_read": False,
            "fpk_equals_1dpw_claimed": False,
        },
        "source_snapshots": source_start,
        "source_inventory": source_inventory,
        "idx": idx_summary,
        "target_record": target_report,
        "decode_chain": {
            "stage1": stage1_trace,
            "nested": nested_trace,
            "final_resource": final_report,
        },
        "negative_controls": negative_controls,
        "existing_tool_audit": tool_audit,
        "algorithm_provenance": PUBLIC_ALGORITHM_PROVENANCE,
        "artifacts": artifacts,
        "artifact_manifest": {
            "path": str(manifest_path.resolve(strict=True)),
            "rows": len(artifacts),
            "sha256": sha256_file(manifest_path),
        },
        "acceptance_checks": acceptance_checks,
        "all_acceptance_checks_pass": all_acceptance_pass,
        "runtime_versions": {
            "python": sys.version.split()[0],
            "cryptography": importlib.metadata.version("cryptography"),
            "zstandard": importlib.metadata.version("zstandard"),
            "Pillow": importlib.metadata.version("Pillow"),
        },
        "bundle_validation": {
            "json_prewrite_reparse": False,
            "json_final_readback_reparse": False,
            "csv_row_count_matches": False,
        },
    }

    report_path = OUTPUT_ROOT / "verification_report.json"
    markdown_path = OUTPUT_ROOT / "verification_report.md"
    readme_path = OUTPUT_ROOT / "README.md"
    cmd_path = OUTPUT_ROOT / "run_verify.cmd"
    requirements_path = OUTPUT_ROOT / "requirements-verifier.txt"

    readme = """# 03_1dpw — 单条真实 PC WPK 复验包

入口：`verify_1dpw_entry.py`

```bat
py -3 E:\\mrzh_audit\\run_004_PC_BinDict与1DPW专项_001\\03_1dpw\\verify_1dpw_entry.py
```

成功标准不是命中可打印 magic，而是同时通过：IDX/1DPW 字段与 4 KiB 边界、AC stage-1、完整 DTSZ Zstandard frame（EOF 且无 unused data）、DDS 手工头、Pillow verify/load、输出回读 SHA，以及五项负对照。

事实源只读 `E:/mrzh`；派生文件只在本目录。FPK 是另一层，本包不读取 FPK，也不把 FPK 称为 1DPW。

优先查看：
1. `verification_report.md`
2. `verification_report.json`
3. `artifact_manifest.csv`
4. `artifacts/*_final.dds` 与 `artifacts/*_preview.png`
5. `RUN_HASHES.sha256`
"""
    run_cmd = "@echo off\r\nsetlocal\r\npy -3 \"%~dp0verify_1dpw_entry.py\"\r\nexit /b %ERRORLEVEL%\r\n"
    requirements = "cryptography>=42\nzstandard>=0.22\nPillow>=10\n"
    write_text(readme_path, readme)
    write_text(cmd_path, run_cmd, newline="")
    write_text(requirements_path, requirements)

    preliminary = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    json.loads(preliminary)
    report["bundle_validation"]["json_prewrite_reparse"] = True
    write_text(report_path, json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    write_text(markdown_path, render_markdown(report))

    loaded = json.loads(report_path.read_text(encoding="utf-8"))
    with manifest_path.open("r", encoding="utf-8", newline="") as stream:
        csv_rows = list(csv.DictReader(stream))
    report["bundle_validation"]["json_final_readback_reparse"] = loaded["status"] == "PASS"
    report["bundle_validation"]["csv_row_count_matches"] = len(csv_rows) == len(artifacts)
    require(all(report["bundle_validation"].values()), "bundle JSON/CSV validation failed")

    write_text(report_path, json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    write_text(markdown_path, render_markdown(report))
    final_loaded = json.loads(report_path.read_text(encoding="utf-8"))
    require(final_loaded["all_acceptance_checks_pass"], "final JSON readback lost PASS state")

    bundle_files = [
        script_path,
        report_path,
        markdown_path,
        readme_path,
        cmd_path,
        requirements_path,
        manifest_path,
        outer_path,
        payload_path,
        stage1_path,
        final_path,
        preview_path,
    ]
    hash_lines = []
    for path in sorted(bundle_files, key=lambda p: p.relative_to(OUTPUT_ROOT).as_posix()):
        rel = path.relative_to(OUTPUT_ROOT).as_posix()
        hash_lines.append(f"{sha256_file(path)} *{rel}")
    hashes_path = OUTPUT_ROOT / "RUN_HASHES.sha256"
    # GNU/MSYS sha256sum treats a CR before the filename terminator as part
    # of the filename, so checksum manifests must be LF-only even on Windows.
    write_text(hashes_path, "\n".join(hash_lines) + "\n", newline="")

    print(
        json.dumps(
            {
                "status": "PASS",
                "record_index_zero_based": TARGET_RECORD_INDEX,
                "record_hash": TARGET_HASH_HEX,
                "chain": "IDX -> ui4.wpk -> 1DPW -> AC -> DTSZ -> Zstandard -> DDS -> Pillow",
                "final_dds": str(final_path),
                "final_dds_sha256": sha256_file(final_path),
                "report": str(report_path),
                "hash_manifest": str(hashes_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, OSError, ValueError, struct.error) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
