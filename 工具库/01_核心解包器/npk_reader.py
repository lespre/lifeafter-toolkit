"""Read-only UTF-8 term audit for test-server script archives.

This program parses NPK entry tables and only decodes bytes to search literal
terms. It never imports, marshals, executes, or writes into E:\\mrzh.

2026-09-20 unpacker upgrade
---------------------------
既有的公开接口（``aes_ecb`` / ``unpack_entry`` / ``murmur3_x86_32`` /
``path_id`` / ``parse_logical_path`` / ``scan_package``）**名字与签名一律不变**。
本期新增能力集中在 ``la_unpack_core``，并在此重新导出：

* ``iter_entries(path)``  惰性全表遍历（不再只给关键词过滤后的 hits）
* ``list_paths(path)``    全表解内嵌逻辑路径 → ``{file_id: path}``
* ``read_entry(path, ...)`` 按 ``entry_index`` 或 ``file_id`` 取单条
* ``NpkArchive``          表/头只解密一次并缓存

性能：``lz4_block`` 改为**原生优先**（``lz4.block``，比纯 Python 快约两个数量级），
原生不可用时自动退回纯 Python，逐位一致。zstd 解压器改为**每线程一个实例**，
避免共享实例导致的 ``ACCESS_VIOLATION`` 静默崩进程。
"""
from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
import zlib
from collections import Counter
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

try:
    import zstandard as zstd
except ImportError:
    zstd = None

# ``la_unpack_core`` 与本文件同目录；显式入 path，保证被其它目录下的脚本加载也能工作。
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import la_unpack_core as core

SRC = Path(r"E:\mrzh")
# Runtime artifacts belong only under the toolkit's first-level output directory.
OUT = Path(__file__).resolve().parents[2] / "output" / "script_literal_audit_v001"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = OUT / "script_literal_audit_v001.json"
KEY = bytes([0x60, 0x63, 0x08, 0xD8, 0xA3, 0x2C, 0x78, 0x20, 0x13, 0xD2, 0x6C, 0x2F, 0x22, 0x6F, 0x68, 0x6D])
TERMS = ("极光剑", "极光", "光剑", "极光盾", "帝皇裁决", "铠甲勇士", "帝皇铠甲", "帝皇瑞昭", "帝皇铠骑")
TERM_BYTES = {term: term.encode("utf-8") for term in TERMS}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def aes_ecb(data: bytes) -> bytes:
    return core.aes_ecb_decrypt(data)


def lz4_block(blob: bytes, expected: int) -> bytes:
    """LZ4 block 解压（签名不变）。

    2026-09-20：改为**原生优先**。``lz4.block.decompress(blob, uncompressed_size=expected)``
    与纯 Python 版本逐位一致，但快约两个数量级。原生库缺失或失败时自动退回纯 Python。

    实测（264 GB 扫描场景下的单块基准见性能报告）：原生 == 纯 Python，40/40 位一致。
    """
    return core.decompress_lz4_block(blob, expected)


def unpack_entry(packed: bytes, expected_size: int, flag: int) -> bytes:
    """NPK 条目解压：flag 0=AES+zlib；2=lz4；12=zstd。返回明文 bytes（签名不变）。

    2026-09-20 加固：
    * flag 2 走原生 LZ4（``lz4_block``）。
    * flag 12 走 ``core.decompress_zstd``：**每线程一个实例**，修掉共享
      ``ZstdDecompressor`` 引发的 ``ACCESS_VIOLATION 0xC0000005`` 静默崩溃。
    * 其它 flag 不再静默原样返回，改走魔数/试解（``core.classify_codec``），
      判不出来就抛 ``core.UnresolvedCodec``，由调用方记录容器/条目。
    """
    return core.npk_decode_entry(packed, expected_size, flag)


def unpack_entry_ex(packed: bytes, expected_size: int, flag: int) -> core.CodecResult:
    """``unpack_entry`` 的**带判定信息**版本（新增，不破坏旧签名）。

    返回 ``CodecResult(codec, data, how, packed_size, decoded_size, flag, error)``；
    ``codec`` ∈ ``{'raw','lz4','zstd','aes_zlib','unresolved'}``。
    """
    if flag == 0:
        try:
            data = unpack_entry(packed, expected_size, flag)
        except Exception as exc:  # noqa: BLE001
            return core.CodecResult("unresolved", None, "flag0_aes_zlib_failed",
                                    len(packed), expected_size, flag, repr(exc))
        how = "flag0_aes_zlib" if data is not packed else core.CODEC_HOW_FLAG_RAW
        return core.CodecResult("aes_zlib" if data is not packed else "raw", data, how,
                                len(packed), expected_size, flag)
    if flag == 2:
        try:
            data = core.decompress_lz4_block(packed, expected_size)
        except Exception as exc:  # noqa: BLE001
            return core.CodecResult("unresolved", None, core.CODEC_HOW_FLAG_LZ4,
                                    len(packed), expected_size, flag, repr(exc))
        return core.CodecResult("lz4", data, core.CODEC_HOW_FLAG_LZ4,
                                len(packed), expected_size, flag)
    return core.classify_codec(packed, len(packed), expected_size, flag)


def murmur3_x86_32(data: bytes, seed: int) -> int:
    """MurmurHash3 x86 32-bit (used by LifeAfter path_id)."""
    c1, c2 = 0xCC9E2D51, 0x1B873593
    h = seed & 0xFFFFFFFF
    end = len(data) & ~3
    for off in range(0, end, 4):
        k = int.from_bytes(data[off:off + 4], "little")
        k = (k * c1) & 0xFFFFFFFF
        k = ((k << 15) | (k >> 17)) & 0xFFFFFFFF
        k = (k * c2) & 0xFFFFFFFF
        h ^= k
        h = ((h << 13) | (h >> 19)) & 0xFFFFFFFF
        h = (h * 5 + 0xE6546B64) & 0xFFFFFFFF
    tail = data[end:]
    k = 0
    if len(tail) >= 3: k ^= tail[2] << 16
    if len(tail) >= 2: k ^= tail[1] << 8
    if tail:
        k ^= tail[0]
        k = (k * c1) & 0xFFFFFFFF
        k = ((k << 15) | (k >> 17)) & 0xFFFFFFFF
        k = (k * c2) & 0xFFFFFFFF
        h ^= k
    h ^= len(data)
    h ^= h >> 16; h = (h * 0x85EBCA6B) & 0xFFFFFFFF
    h ^= h >> 13; h = (h * 0xC2B2AE35) & 0xFFFFFFFF
    h ^= h >> 16
    return h & 0xFFFFFFFF


def path_id(logical_path: str) -> int:
    """NPK 条目 file_id：双 Murmur3（反斜杠路径、UTF-8）。

    高 32 位 seed=0x77777777，低 32 位 seed=0x66666666。
    已验证：脚本路径（com\\cdata\\xxx.nxs）与资源路径（damoshi_icon\\xxx.png）均匹配。
    """
    e = logical_path.encode("utf-8")
    return (murmur3_x86_32(e, 0x77777777) << 32) | murmur3_x86_32(e, 0x66666666)


def parse_logical_path(data: bytes) -> str:
    """从已解码载荷解内嵌逻辑路径（签名与行为不变，实现委托给 core）。"""
    return core.parse_logical_path(data)


# ================================================================ 本期新增接口
# 旧接口的问题：scan_package() 只返回"关键词过滤后的 hits"，没有全表遍历入口，
# 使用者不得不自己重写条目表遍历（已为此写过三次一次性脚本）。
# 以下为新增的公开接口，全部委托给 la_unpack_core。

def iter_entries(path: str | Path):
    """惰性产出全表条目：``entry_index / file_id / offset / packed / decoded / flag``。

    用法::

        for entry in iter_entries(r"E:\\mrzh\\Documents\\script.npk"):
            print(entry.entry_index, entry.file_id_hex, entry.flag)
    """
    return core.iter_entries(path)


def list_paths(path: str | Path, fast: bool = True, limit: int | None = None) -> dict[int, str]:
    """全表遍历解内嵌逻辑路径，返回 ``{file_id: path}``。

    ``fast=True``（默认）先在载荷头部 512 B 上试解，避开大载荷解压。
    """
    return core.list_paths(path, fast=fast, limit=limit)


def read_entry(path: str | Path, entry_index: int | None = None,
               file_id: int | None = None, decode: bool = True) -> bytes:
    """按 ``entry_index`` 或 ``file_id`` 读取单条载荷（``decode=False`` 取原始载荷）。"""
    return core.read_entry(path, entry_index=entry_index, file_id=file_id, decode=decode)


def package_key(path: str | Path) -> tuple[str, str]:
    """NPK 包唯一键 ``(完整路径, basename)``。

    修复：只用 basename 作键时，同名包会互相覆盖。实测 ``E:\\mrzh`` 下有 5 个
    ``script*.npk`` 但只有 3 个不同 basename，按 basename 归并会丢 115,155 ~ 167,120 条。
    """
    return core.package_key(path)


class NpkArchive(core.NpkArchive):
    """NPK 只读容器：头 + 条目表只解密一次并缓存；支持 context manager。"""


clear_table_cache = core.clear_table_cache
table_cache_info = core.table_cache_info
SkipLog = core.SkipLog
UnresolvedCodec = core.UnresolvedCodec
classify_codec = core.classify_codec


def all_offsets(data: bytes, needle: bytes) -> list[int]:
    found: list[int] = []
    position = 0
    while True:
        position = data.find(needle, position)
        if position < 0:
            return found
        found.append(position)
        position += 1


def context(data: bytes, offset: int, term: str) -> dict[str, Any]:
    before, after = 120, 180
    begin, end = max(0, offset - before), min(len(data), offset + len(term.encode("utf-8")) + after)
    raw = data[begin:end]
    return {
        "decoded_byte_offset": offset,
        "context_start_offset": begin,
        "context_end_offset": end,
        "context_utf8_replace": raw.decode("utf-8", "replace"),
        "context_hex": raw.hex(),
    }


def package_candidates() -> list[Path]:
    # Only script archive candidates; no broad resource rewrite or client execution.
    allowed = []
    for parent in (SRC, SRC / "Documents"):
        if not parent.exists():
            continue
        for path in parent.glob("script*"):
            if path.is_file() and path.suffix.lower() in {".npk", ".lc"}:
                allowed.append(path)
    return sorted(set(allowed), key=lambda item: str(item).lower())


def scan_package(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, str]]:
    """沿用原签名与返回结构：``(package, hits, path_map)``。

    2026-09-20 变化（均不影响返回结构）：
    * 头与条目表改由 ``NpkArchive`` 读取并缓存，**同一文件不再重复解密**。
    * 新增 ``codec_counts`` / ``skipped`` 字段；判不出的压缩类型计入 ``unresolved``
      并留痕，不再静默当作 raw。
    """
    source_size = path.stat().st_size
    package = {
        "path": str(path),
        "package_key": list(package_key(path)),
        "size": source_size,
        "sha256": sha256_file(path),
        "entries_declared": 0,
        "entries_table_valid": 0,
        "entries_decoded": 0,
        "entry_errors": [],
        "flag_counts": {},
        "codec_counts": {},
        "unresolved": [],
    }
    hits: list[dict[str, Any]] = []
    path_map: dict[str, str] = {}
    with NpkArchive(path) as archive:
        package.update({
            "header_magic": 0x4B50584E,
            "package_version": archive.header["version"],
            "table_offset": archive.header["table_offset"],
            "entries_declared": archive.header["entries_declared"],
            "table_cache_hit": archive.header.get("table_cache_hit", False),
        })
        flags = Counter()
        codecs = Counter()
        handle = archive._ensure_handle()
        for entry in archive.iter_entries():
            index = entry.entry_index
            file_id, offset = entry.file_id, entry.offset
            packed_size, decoded_size, flag = entry.packed, entry.decoded, entry.flag
            flags[str(flag)] += 1
            if offset + packed_size > source_size:
                package["entry_errors"].append({"entry_index": index, "file_id": entry.file_id_hex, "stage": "bounds", "error": "packed range outside source"})
                continue
            package["entries_table_valid"] += 1
            handle.seek(offset)
            packed = handle.read(packed_size)
            if len(packed) != packed_size:
                package["entry_errors"].append({"entry_index": index, "file_id": entry.file_id_hex, "stage": "read", "error": "packed read short"})
                continue
            try:
                result = unpack_entry_ex(packed, decoded_size, flag)
                if not result.ok:
                    raise UnresolvedCodec(result.error, result.as_dict())
                data = result.data
                codecs[result.codec] += 1
                # A successful static string scan is valid for any byte payload; we don't claim it executed/decompiled.
                package["entries_decoded"] += 1
            except Exception as exc:
                codecs["unresolved"] += 1
                record = {"entry_index": index, "file_id": entry.file_id_hex, "stage": "static_unpack", "flag": flag, "error": repr(exc)}
                package["entry_errors"].append(record)
                if len(package["unresolved"]) < 200:
                    package["unresolved"].append(record)
                continue
            file_id_hex = entry.file_id_hex
            logical_path = parse_logical_path(data)
            if logical_path:
                old = path_map.get(file_id_hex)
                if old and old != logical_path:
                    package["entry_errors"].append({"entry_index": index, "file_id": file_id_hex, "stage": "logical_path", "error": "conflicting path for identical file ID", "old": old, "new": logical_path})
                else:
                    path_map[file_id_hex] = logical_path
            found_terms = {term: all_offsets(data, needle) for term, needle in TERM_BYTES.items()}
            if any(found_terms.values()):
                hits.append({
                    "package": str(path),
                    "package_key": list(package_key(path)),
                    "package_sha256": package["sha256"],
                    "entry_index": index,
                    "file_id": file_id_hex,
                    "entry_offset": offset,
                    "packed_size": packed_size,
                    "decoded_size_declared": decoded_size,
                    "static_unpack_flag": flag,
                    "codec": result.codec,
                    "logical_path_direct": logical_path,
                    "term_hits": {
                        term: [context(data, item, term) for item in offsets]
                        for term, offsets in found_terms.items() if offsets
                    },
                })
        package["flag_counts"] = dict(flags)
        package["codec_counts"] = dict(codecs)
        package["skipped"] = archive.skip_log.as_dict()
    return package, hits, path_map


def scan_packages(paths: list[Path] | None = None) -> dict[str, Any]:
    """**新增**：扫描多个 NPK，并以 ``(完整路径, basename)`` 作键返回结果。

    这是缺陷 4 的正面修法。旧口径用 basename 作键，同名包会互相覆盖：
    实测 ``E:\\mrzh`` 下 5 个 ``script*.npk`` 只有 3 个不同 basename，
    basename 归并会丢 115,155 ~ 167,120 条条目。

    返回::

        {"packages": {package_key: info, ...},
         "entries_total": int,
         "entries_lost_if_keyed_by_basename": int,
         "basename_collisions": {...}}
    """
    targets = list(paths) if paths is not None else package_candidates()
    packages: dict[tuple[str, str], dict[str, Any]] = {}
    failures: list[dict[str, str]] = []
    for path in targets:
        try:
            info, _hits, _paths = scan_package(path)
            packages[package_key(path)] = info
        except Exception as exc:  # noqa: BLE001
            failures.append({"path": str(path), "error": repr(exc)})

    by_basename: dict[str, list[tuple[str, str]]] = {}
    for key in packages:
        by_basename.setdefault(key[1].lower(), []).append(key)
    collisions = {name: [list(k) for k in keys]
                  for name, keys in by_basename.items() if len(keys) > 1}

    entries_total = sum(p["entries_declared"] for p in packages.values())
    basename_keyed = 0
    for keys in by_basename.values():
        basename_keyed += min(packages[k]["entries_declared"] for k in keys)

    return {
        "package_count": len(packages),
        "unique_basenames": len(by_basename),
        "packages": {f"{k[0]}": v for k, v in packages.items()},
        "package_keys": [list(k) for k in packages],
        "failures": failures,
        "entries_total": entries_total,
        "entries_if_keyed_by_basename": basename_keyed,
        "entries_lost_if_keyed_by_basename": entries_total - basename_keyed,
        "basename_collisions": collisions,
    }


def main() -> None:
    packages = package_candidates()
    if not packages:
        raise RuntimeError("No script archive candidates found under E:\\mrzh or E:\\mrzh\\Documents")
    package_results: list[dict[str, Any]] = []
    all_hits: list[dict[str, Any]] = []
    global_paths: dict[str, str] = {}
    package_failures: list[dict[str, str]] = []
    for path in packages:
        try:
            info, hits, local_paths = scan_package(path)
            package_results.append(info)
            all_hits.extend(hits)
            for file_id, logical_path in local_paths.items():
                global_paths.setdefault(file_id, logical_path)
        except Exception as exc:
            package_failures.append({"path": str(path), "error": repr(exc)})
    for hit in all_hits:
        hit["logical_path_file_id_cross_package"] = global_paths.get(hit["file_id"], "")
        hit["logical_path_provenance"] = (
            "direct in same decoded entry" if hit["logical_path_direct"] else
            "same file_id recovered from a different test-server script entry" if hit["logical_path_file_id_cross_package"] else
            "not recovered"
        )
    term_summary = {
        term: {
            "matching_entries": sum(1 for hit in all_hits if term in hit["term_hits"]),
            "total_decoded_byte_occurrences": sum(len(hit["term_hits"].get(term, [])) for hit in all_hits),
            "matching_file_ids": sorted({hit["file_id"] for hit in all_hits if term in hit["term_hits"]}),
        }
        for term in TERMS
    }
    coverage = {
        "candidate_archive_count": len(packages),
        "candidate_archives": [str(path) for path in packages],
        "entries_declared_total": sum(p["entries_declared"] for p in package_results),
        "entries_table_valid_total": sum(p["entries_table_valid"] for p in package_results),
        "entries_static_unpacked_total": sum(p["entries_decoded"] for p in package_results),
        "entry_error_count": sum(len(p["entry_errors"]) for p in package_results),
        "package_failures": package_failures,
    }
    report = {
        "analysis_mode": "read_only_static_literal_UTF8_scan",
        "source_root": str(SRC),
        "source_write_operations": 0,
        "execution_boundary": "No target payload was imported, marshalled, evaluated, compiled, or executed. UTF-8 literals were searched only after static archive extraction.",
        "terms": list(TERMS),
        "coverage": coverage,
        "packages": package_results,
        "term_summary": term_summary,
        "hits": all_hits,
        "interpretation_boundary": "A literal miss proves only absence from successfully static-unpacked script entries in this source snapshot; it does not prove an item cannot be delivered by another unscanned archive, server data, or a later client snapshot.",
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Re-open for syntactic verification before reporting success.
    loaded = json.loads(REPORT.read_text(encoding="utf-8"))
    assert loaded["coverage"] == coverage
    assert loaded["term_summary"] == term_summary
    print(json.dumps({"report": str(REPORT), "coverage": coverage, "term_summary": term_summary}, ensure_ascii=False))


if __name__ == "__main__":
    main()
