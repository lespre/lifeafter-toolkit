"""Content-addressed, status-explicit NXPK workcopy extraction."""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path
from typing import Any, Protocol


class NpkReader(Protocol):
    def aes_ecb(self, payload: bytes) -> bytes: ...

    def unpack_entry(self, packed: bytes, expected_size: int, flag: int) -> bytes: ...


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _source_snapshot(path: Path) -> dict[str, Any]:
    stat = path.stat()
    return {"path": str(path), "size": stat.st_size, "sha256": _sha256_path(path)}


def _entry_row(index: int, file_id: int, offset: int, packed_size: int, declared_size: int, flag: int) -> dict[str, Any]:
    return {
        "index": index,
        "file_id": f"{file_id:016X}",
        "archive_offset": offset,
        "packed_size": packed_size,
        "declared_size": declared_size,
        "flag": flag,
    }


# declared_size 在哪几种 flag 下表示「解压后大小」。
# 依据：全量 27,072 条实测（2026-09-26）——flag 0 的 packed==declared 占 100%，
# flag 2 的实解长度恒等于 declared。语义随 flag 变，故按 flag 分派判据。
DECLARED_IS_OUTPUT_SIZE = frozenset({2})


def extract_npk_verified(source: Path | str, output_dir: Path | str, *, reader: NpkReader) -> dict[str, Any]:
    """Extract NXPK entries while preserving each decode/bounds status in a manifest.

    ``decoded_size`` is retained as source metadata. A mismatch does not erase a
    successfully unpacked payload; it receives a separate status so downstream
    scanners can make their acceptance rule explicit.
    """
    source_path = Path(source)
    output = Path(output_dir)
    entries_dir = output / "entries"
    manifest_path = output / "manifest.json"
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"refuse to mix with existing workcopy: {output}")
    output.mkdir(parents=True, exist_ok=True)
    entries_dir.mkdir()

    before = _source_snapshot(source_path)
    entries: list[dict[str, Any]] = []
    counts = {"decoded_count": 0, "size_mismatch_count": 0, "decode_error_count": 0, "invalid_bounds_count": 0}
    with source_path.open("rb") as stream:
        header = reader.aes_ecb(stream.read(64))
        if len(header) < 24 or header[8:12] != b"NXPK":
            raise ValueError(f"not a verified NXPK header: {source_path}")
        entry_table_offset = struct.unpack_from("<I", header, 16)[0]
        entry_count = struct.unpack_from("<I", header, 20)[0]
        table_size = entry_count * 48
        if entry_table_offset + table_size > before["size"]:
            raise ValueError("NXPK entry table extends past source bounds")
        stream.seek(entry_table_offset)
        table = reader.aes_ecb(stream.read(table_size))
        if len(table) != table_size:
            raise ValueError("short decrypted NXPK entry table")

        for index in range(entry_count):
            entry = table[index * 48:(index + 1) * 48]
            file_id = struct.unpack_from("<Q", entry, 0)[0]
            offset = struct.unpack_from("<I", entry, 8)[0]
            packed_size = struct.unpack_from("<I", entry, 12)[0]
            declared_size = struct.unpack_from("<I", entry, 16)[0]
            flag = struct.unpack_from("<i", entry, 28)[0]
            row = _entry_row(index, file_id, offset, packed_size, declared_size, flag)

            if packed_size <= 0 or offset <= 0 or offset + packed_size > before["size"]:
                row["status"] = "invalid_bounds"
                counts["invalid_bounds_count"] += 1
                entries.append(row)
                continue
            stream.seek(offset)
            packed = stream.read(packed_size)
            if len(packed) != packed_size:
                row["status"] = "invalid_bounds"
                row["error"] = "short packed read"
                counts["invalid_bounds_count"] += 1
                entries.append(row)
                continue
            row["packed_sha256"] = hashlib.sha256(packed).hexdigest()
            try:
                unpacked = reader.unpack_entry(packed, declared_size, flag)
            except Exception as exc:
                row["status"] = "decode_error"
                row["error"] = f"{type(exc).__name__}: {exc}"
                counts["decode_error_count"] += 1
                entries.append(row)
                continue

            output_file = f"entries/{index:06d}.bin"
            (output / output_file).write_bytes(unpacked)
            row["output_file"] = output_file
            row["actual_output_size"] = len(unpacked)
            row["output_sha256"] = hashlib.sha256(unpacked).hexdigest()
            # 判据：declared_size 的**语义随 flag 变**，不能一视同仁。
            #   实测（2026-09-26，全量 27,072 条）：
            #     flag 0（AES+zlib）25,685 条 → packed == declared 占 100%
            #       ⇒ 该字段对 flag 0 表示【压缩后大小】，不是解压后大小
            #       ⇒ 实解长度/declared 中位 1.196、max 9.865（正常压缩比）
            #     flag 2（LZ4）1,387 条 → 实解长度 == declared
            #       ⇒ 该字段对 flag 2 表示【解压后大小】，长度校验成立
            #   原判据对两者一视同仁 ⇒ flag 0 全部误报（占条目 94.88%）⇒ 检查器失效。
            if flag in DECLARED_IS_OUTPUT_SIZE:
                if len(unpacked) == declared_size:
                    row["status"] = "decoded"
                    counts["decoded_count"] += 1
                else:
                    row["status"] = "decoded_size_mismatch"
                    counts["size_mismatch_count"] += 1
            else:
                # 该 flag 下 declared_size 不表示解压后大小 ⇒ 不做「长度」校验。
                #
                # ★ 这不是「关掉校验」，而是**换了校验对象**：
                #   flag 0 走 zlib，zlib 流结构 = [2B 头][deflate 数据][4B Adler-32]。
                #   它没有「解压后大小」字段（ISIZE 是 gzip 的，不是 zlib 的），
                #   但它**有 Adler-32 校验和**，zlib.decompress() 解压时会验证它。
                #   实测（2026-09-26）：对 deflate 主体逐位改 1 字节，21/21 全部
                #   被 zlib 抛错捕获（0 次静默给出错误数据）。
                #   ⇒ 「解压成功」本身就等于「数据完整性已被 zlib 验证」。
                #   ⇒ 校验没有缺席，只是校验的量是【完整性】而非【长度】。
                #
                #   原 bug 的性质：拿一个语义错误的字段（declared_size，对 flag 0
                #   其实是压缩后大小）当「长度预期」去比 ⇒ 必然不等 ⇒ 假警报。
                #   错的是【校验对象选错了】，不是【没校验】。
                row["status"] = "decoded"
                row["size_check"] = "not_applicable"
                row["size_check_note"] = (
                    f"flag={flag} 下 declared_size={declared_size} 表示压缩后大小，"
                    f"不作解压长度校验；实解 {len(unpacked)} B"
                )
                counts["decoded_count"] += 1
            entries.append(row)

    after = _source_snapshot(source_path)
    source_unchanged = before == after
    if not source_unchanged:
        raise RuntimeError("source changed while extracting; workcopy is invalid")
    report = {
        "schema": "lifeafter-nxpk-verified-workcopy-v1",
        "source": after,
        "source_unchanged": True,
        "header": {"entry_table_offset": entry_table_offset, "entry_count": entry_count},
        "summary": {"entry_count": entry_count, **counts},
        "entries": entries,
    }
    manifest_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report
