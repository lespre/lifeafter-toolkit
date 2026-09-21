# -*- coding: utf-8 -*-
"""la_unpack_core.py — 核心解包器加固共享层（2026-09-20 unpacker upgrade）

本模块是 `01_核心解包器` 的**新增**共享内核，集中承载本期实测确认的四类修复：

1. **压缩类型按载荷魔数 / 试解判定**，不再用 `clen != olen ⇒ zstd` 这种猜测口径。
   - zstd 魔数 ``28 B5 2F FD`` → zstd
   - lz4 block 无魔数 → ``lz4.block.decompress(raw, uncompressed_size=olen)`` 试解，
     成功且长度 == olen 即 LZ4
   - 再退 raw；**判不出来就如实报 ``unresolved``**，绝不假装成功
2. **`.wpk` 包名十进制 / 十六进制候选 + 目录枚举**，并在跳过时记录原因（不静默）。
3. **zstd 解压器每线程一个实例**（``threading.local``），规避共享实例导致的
   ``ACCESS_VIOLATION 0xC0000005`` 静默崩进程。
4. **NPK 条目表全表遍历接口**（``iter_entries`` / ``list_paths`` / ``read_entry``），
   并用 **(包路径, basename)** 作键，避免同名包互相覆盖。

兼容性：本模块只**新增**能力。既有函数名与签名（``aes_ecb`` / ``unpack_entry`` /
``murmur3_x86_32`` / ``path_id`` / ``parse_logical_path`` / ``scan_package``）保持不变，
由 ``npk_reader.py`` 继续导出。
"""
from __future__ import annotations

import hashlib
import os
import re
import struct
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

try:  # native LZ4：比纯 Python 快约两个数量级
    import lz4.block as _lz4_block
except ImportError:  # pragma: no cover - 环境缺库时退化为纯 Python
    _lz4_block = None

try:
    import zstandard as _zstd
except ImportError:  # pragma: no cover
    _zstd = None

# ---------------------------------------------------------------- 常量

AES_KEY = bytes([0x60, 0x63, 0x08, 0xD8, 0xA3, 0x2C, 0x78, 0x20,
                 0x13, 0xD2, 0x6C, 0x2F, 0x22, 0x6F, 0x68, 0x6D])

ZSTD_MAGIC = b"\x28\xb5\x2f\xfd"
ZLIB_MAGICS = (b"\x78\x9c", b"\x78\xda", b"\x78\x01", b"\x78\x5e")

NPK_HEADER_SIZE = 48       # NXPK 头：前 32 B 有效，AES-ECB 逐块解密
NPK_ENTRY_SIZE = 48        # 条目表：48 B/条
NPK_CIPHER_BLOCK = 16

WPK_MAGIC = b"1DPW"
WPK_SLOT_PKG = 255         # 0xFF：条目不在任何 .wpk 里，而在 slot file 目录
IDX_HEADER_SIZE = 32
IDX_ENTRY_SIZE = 36

MAX_TABLE_CACHE = 8

__all__ = [
    "AES_KEY", "ZSTD_MAGIC", "NPK_HEADER_SIZE", "NPK_ENTRY_SIZE",
    "WPK_SLOT_PKG", "IDX_HEADER_SIZE", "IDX_ENTRY_SIZE",
    "aes_ecb_decrypt", "zstd_decompressor", "decompress_zstd",
    "lz4_python_decompress", "decompress_lz4_block",
    "CodecResult", "classify_codec", "UnresolvedCodec",
    "parse_logical_path",
    "SkipLog", "WPKResolutionError",
    "wpk_name_candidates", "enumerate_family_wpk", "resolve_wpk_path",
    "parse_idx_entries",
    "NpkEntry", "NpkArchive", "package_key",
    "iter_entries", "list_paths", "read_entry",
    "clear_table_cache", "table_cache_info",
]


# ================================================================ AES

def aes_ecb_decrypt(data: bytes, key: bytes = AES_KEY) -> bytes:
    """AES-128-ECB 逐 16 B 块解密；长度不足一块时原样返回，尾部不满一块的部分保留。

    与参考实现 ``LA.NPK.Tool/FileSystem/Encryption/NpkCipher.cs`` 一致：
    ECB、无填充（PaddingMode.None）、IV 全零，只处理 ``len // 16`` 个完整块，
    尾部残余字节原样保留。
    """
    usable = len(data) // NPK_CIPHER_BLOCK * NPK_CIPHER_BLOCK
    if not usable:
        return data
    decryptor = Cipher(algorithms.AES(key), modes.ECB()).decryptor()
    return decryptor.update(data[:usable]) + decryptor.finalize() + data[usable:]


# ================================================================ zstd（线程安全）

_zstd_state = threading.local()


def zstd_decompressor():
    """返回**当前线程**的 ``ZstdDecompressor`` 实例。

    修复：``zstandard.ZstdDecompressor`` 非线程安全；多线程共享同一实例会触发
    ``ACCESS_VIOLATION 0xC0000005``（直接崩进程，Python 层捕不到）。
    每线程一个实例即可，代价是一次构造。
    """
    if _zstd is None:
        raise RuntimeError("zstandard 不可用：请 pip install zstandard")
    instance = getattr(_zstd_state, "decompressor", None)
    if instance is None:
        instance = _zstd.ZstdDecompressor()
        _zstd_state.decompressor = instance
    return instance


def new_zstd_decompressor():
    """显式新建一个实例（每次新建 + 复用 obj 的场景用）。"""
    if _zstd is None:
        raise RuntimeError("zstandard 不可用：请 pip install zstandard")
    return _zstd.ZstdDecompressor()


def decompress_zstd(raw: bytes, expected: int | None = None) -> bytes:
    """zstd 解压：先按 ``expected`` 一次性解，失败再走流式（帧内未写 content size 时）。"""
    if _zstd is None:
        raise RuntimeError("zstandard 不可用：请 pip install zstandard")
    decompressor = zstd_decompressor()
    if expected and expected > 0:
        try:
            return decompressor.decompress(raw, max_output_size=expected + 4096)
        except Exception:
            pass
    import io
    with decompressor.stream_reader(io.BytesIO(raw)) as reader:
        return reader.read()


# ================================================================ LZ4 block

def lz4_python_decompress(blob: bytes, expected: int) -> bytes:
    """纯 Python 的 LZ4 block 解压（原生库不可用时的兜底）。

    保留为独立函数是为了：① 与原生实现做逐字节对拍；② 无 lz4 依赖时仍能工作。
    """
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
        read = len(output) - distance
        for _ in range(match_len):
            output.append(output[read])
            read += 1
    if len(output) != expected:
        raise ValueError(f"lz4 output {len(output)} != expected {expected}")
    return bytes(output)


def decompress_lz4_block(blob: bytes, expected: int, prefer_native: bool = True) -> bytes:
    """LZ4 block 解压：**优先原生** ``lz4.block``，失败再退纯 Python。

    原生实现比纯 Python 快约两个数量级（实测见性能报告），且逐位一致。
    """
    if expected <= 0:
        raise ValueError("lz4 expected size must be positive")
    if prefer_native and _lz4_block is not None:
        try:
            out = _lz4_block.decompress(blob, uncompressed_size=expected)
            if len(out) == expected:
                return out
        except Exception:
            pass
    return lz4_python_decompress(blob, expected)


def lz4_available_native() -> bool:
    return _lz4_block is not None


# ================================================================ 压缩类型判定

class UnresolvedCodec(RuntimeError):
    """无法判定压缩类型。按纪律：如实上报，不假装成功。"""

    def __init__(self, message: str, detail: dict[str, Any] | None = None):
        super().__init__(message)
        self.detail = detail or {}


@dataclass
class CodecResult:
    """一次载荷判定 / 解码的结果。"""

    codec: str                 # 'raw' | 'lz4' | 'zstd' | 'unresolved'
    data: bytes | None         # 解码后明文；unresolved 时为 None
    how: str                   # 判定依据：见 CODEC_HOW_*
    packed_size: int = 0
    decoded_size: int = 0
    flag: int | None = None
    error: str = ""

    @property
    def ok(self) -> bool:
        return self.data is not None

    def as_dict(self) -> dict[str, Any]:
        return {
            "codec": self.codec, "how": self.how, "packed": self.packed_size,
            "decoded": self.decoded_size, "flag": self.flag,
            "out_size": len(self.data) if self.data is not None else None,
            "error": self.error,
        }


CODEC_HOW_ZSTD_MAGIC = "zstd_magic"
CODEC_HOW_FLAG_LZ4 = "flag2_lz4_trial"
CODEC_HOW_LEN_EQUAL_RAW = "packed_eq_decoded_raw"
CODEC_HOW_FLAG_RAW = "flag0_raw"
CODEC_HOW_LZ4_TRIAL = "lz4_trial"
CODEC_HOW_ZSTD_TRIAL = "zstd_trial"
CODEC_HOW_UNRESOLVED = "unresolved"


def classify_codec(raw: bytes, packed_size: int, decoded_size: int,
                   flag: int | None = None, zlib_wrapped: bool = False) -> CodecResult:
    """按**载荷魔数 / 试解**判定压缩类型并解码（替代 ``clen != olen ⇒ zstd``）。

    判定顺序（每条都会记进 ``how``）：

    1. zstd 魔数 ``28 B5 2F FD`` → zstd
    2. flag 明确表示 LZ4（``flag == 2``）→ 试解 LZ4
    3. ``packed_size == decoded_size`` 且 flag 表示未压缩（``flag == 0``）→ raw
    4. LZ4 试解（成功且长度 == ``decoded_size``）→ lz4
    5. zstd 试解 → zstd
    6. 仍然判不出来 → ``codec='unresolved'``，``data=None``，理由写进 ``error``

    注意：``zlib_wrapped`` 仅用于 NPK 的 flag 0（AES+``i64==1``+zlib）路径，
    该路径由 ``npk_reader.unpack_entry`` 处理，这里不重复实现。
    """
    detail: dict[str, Any] = {"packed": packed_size, "decoded": decoded_size, "flag": flag}
    if not raw:
        return CodecResult("unresolved", None, CODEC_HOW_UNRESOLVED,
                           packed_size, decoded_size, flag, "empty payload")

    # 1) zstd 魔数
    if raw[:4] == ZSTD_MAGIC:
        try:
            out = decompress_zstd(raw, decoded_size)
        except Exception as exc:  # noqa: BLE001
            return CodecResult("unresolved", None, CODEC_HOW_ZSTD_MAGIC,
                               packed_size, decoded_size, flag, f"zstd magic but decode failed: {exc!r}")
        return CodecResult("zstd", out, CODEC_HOW_ZSTD_MAGIC, packed_size, decoded_size, flag)

    # 2) flag 明确指 LZ4
    if flag == 2 and decoded_size > 0:
        try:
            out = decompress_lz4_block(raw, decoded_size)
            return CodecResult("lz4", out, CODEC_HOW_FLAG_LZ4, packed_size, decoded_size, flag)
        except Exception as exc:  # noqa: BLE001
            detail["lz4_error"] = repr(exc)

    # 3) 长度相等 + flag 说未压缩 → raw
    if packed_size == decoded_size and flag in (0, None):
        return CodecResult("raw", raw, CODEC_HOW_LEN_EQUAL_RAW, packed_size, decoded_size, flag)

    # 4) 无魔数 ⇒ LZ4 试解
    if decoded_size > 0:
        try:
            out = decompress_lz4_block(raw, decoded_size)
            return CodecResult("lz4", out, CODEC_HOW_LZ4_TRIAL, packed_size, decoded_size, flag)
        except Exception as exc:  # noqa: BLE001
            detail["lz4_error"] = repr(exc)

    # 5) zstd 试解
    try:
        out = decompress_zstd(raw, decoded_size)
        return CodecResult("zstd", out, CODEC_HOW_ZSTD_TRIAL, packed_size, decoded_size, flag)
    except Exception as exc:  # noqa: BLE001
        detail["zstd_error"] = repr(exc)

    # 6) 如实报 unresolved
    if packed_size == decoded_size:
        return CodecResult("raw", raw, CODEC_HOW_LEN_EQUAL_RAW, packed_size, decoded_size, flag)
    return CodecResult("unresolved", None, CODEC_HOW_UNRESOLVED, packed_size, decoded_size,
                       flag, f"no codec matched: {detail}")


# ================================================================ 逻辑路径

_LOGICAL_PATH_MIN, _LOGICAL_PATH_MAX = 1, 1000


def parse_logical_path(data: bytes) -> str:
    """从已解码载荷里解出内嵌逻辑路径（形如 ``com\\cdata\\xxx.nxs``）。

    NPK 条目名有两种来源：① 包内内嵌路径（本函数）；② 外部 ``FileNames.list``
    双 Murmur3 反查（``path_id``）。两者互补，本函数只做 ①。
    """
    for base in (0, 1, 2):
        if len(data) < base + 6:
            continue
        has_ti = data[base:base + 2] in (b"tI", b"sI")
        length_offset = base + 2 if has_ti else base
        length = struct.unpack_from("<I", data, length_offset)[0]
        start = base + 6 if has_ti else base + 4
        if not (_LOGICAL_PATH_MIN < length < _LOGICAL_PATH_MAX and start + length <= len(data)):
            continue
        candidate = data[start:start + length]
        try:
            text = candidate.decode("utf-8", "strict")
        except UnicodeDecodeError:
            continue
        if ("\\" in text or "/" in text or text.endswith(".py")) and all(
            ord(ch) >= 32 or ch in "\r\n\t" for ch in text
        ):
            return text
    return ""


# ================================================================ 跳过记录

@dataclass
class SkipLog:
    """跳过记录器：**任何跳过都必须留痕**，禁止静默 continue。"""

    stage: str
    items: list[dict[str, Any]] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)
    limit: int = 200

    def record(self, reason: str, **fields: Any) -> None:
        self.counts[reason] = self.counts.get(reason, 0) + 1
        if len(self.items) < self.limit:
            self.items.append({"stage": self.stage, "reason": reason, **fields})

    @property
    def total(self) -> int:
        return sum(self.counts.values())

    def as_dict(self) -> dict[str, Any]:
        return {"stage": self.stage, "total_skipped": self.total,
                "counts": dict(self.counts), "samples": self.items}


# ================================================================ WPK 包名解析

class WPKResolutionError(RuntimeError):
    """无法把 (家族, 包号) 解析到实际 .wpk 文件。"""

    def __init__(self, message: str, detail: dict[str, Any] | None = None):
        super().__init__(message)
        self.detail = detail or {}


def wpk_name_candidates(family: str, pkg: int) -> list[str]:
    """生成候选文件名：**十进制 / 十六进制大写 / 十六进制小写**。

    LA 的资源包在 ``pkg >= 10`` 时用**单个十六进制字母**做后缀：``charactera.wpk``
    （小写）与 ``modelA.wpk``（大写）在同目录下并存，所以两种大小写都要试。
    """
    raw = [
        f"{family}{pkg}.wpk",
        f"{family}{pkg:X}.wpk",
        f"{family}{pkg:x}.wpk",
    ]
    seen: set[str] = set()
    ordered: list[str] = []
    for name in raw:
        if name not in seen:
            seen.add(name)
            ordered.append(name)
    return ordered


def enumerate_family_wpk(directory: str | os.PathLike[str], family: str) -> dict[str, str]:
    """枚举目录下所有 ``<family><后缀>.wpk``，返回 ``{文件名: 后缀}``。

    关键：**以已知 family 为锚点**做前缀匹配，而不是去切分文件名。
    反例：用非贪婪 ``(.+?)([0-9A-Fa-f]+)\\.wpk`` 切 ``scene3.wpk`` 会得到
    ``("scen", "e3")``（因为 ``e`` 也是十六进制字符），family 直接被判错。
    """
    anchored = re.compile(rf"^{re.escape(family)}(?P<sfx>[0-9A-Fa-f]+)\.wpk$", re.IGNORECASE)
    found: dict[str, str] = {}
    try:
        names = os.listdir(directory)
    except OSError:
        return found
    for name in sorted(names):
        match = anchored.match(name)
        if match and os.path.isfile(os.path.join(directory, name)):
            found[name] = match.group("sfx")
    return found


def _actual_on_disk_name(directory: str | os.PathLike[str], name: str) -> str | None:
    """在大小写不敏感的文件系统（Windows）上回填**真实**的磁盘文件名。

    Windows 下 ``isfile("characterA.wpk")`` 对真实文件 ``charactera.wpk`` 也返回 True，
    如果直接采信就会把解析结果报成 ``characterA.wpk``，与实际不符。
    """
    try:
        names = os.listdir(directory)
    except OSError:
        return None
    if name in names:
        return name
    lowered = name.lower()
    for candidate in names:
        if candidate.lower() == lowered:
            return candidate
    return None


def resolve_wpk_path(directory: str | os.PathLike[str], family: str, pkg: int,
                     skip_log: SkipLog | None = None) -> tuple[str | None, dict[str, Any]]:
    """把 ``(目录, 家族, 包号)`` 解析为实际 ``.wpk`` 路径。

    返回 ``(路径或 None, 说明)``。``pkg == 255`` 是 slot file 标记（条目不在 .wpk 里），
    会以 ``slot_file`` 记录，不算失败。**解析不到时必定写进 skip_log。**

    解析顺序：① 目录枚举出的**精确**文件名 → ② 候选名（大小写不敏感兜底）。
    先精确后兜底，才不会在 Windows 上把 ``charactera.wpk`` 报成 ``characterA.wpk``。
    """
    info: dict[str, Any] = {"family": family, "pkg": pkg, "directory": str(directory)}
    if pkg == WPK_SLOT_PKG:
        info["resolved_by"] = "slot_file_marker"
        info["note"] = "pkg=255 (0xFF)：条目存放在 slot file，不在任何 .wpk"
        return None, info

    family_files = enumerate_family_wpk(directory, family)
    suffix_forms: dict[str, str] = {}
    for name, sfx in family_files.items():
        for form in (sfx, sfx.lower(), sfx.upper()):
            suffix_forms.setdefault(form, name)
    info["family_wpk_files"] = sorted(family_files)
    info["family_wpk_suffixes"] = sorted(set(family_files.values()))

    candidates = wpk_name_candidates(family, pkg)
    enum_name = (suffix_forms.get(f"{pkg:X}") or suffix_forms.get(f"{pkg:x}")
                 or suffix_forms.get(str(pkg)))
    if enum_name and enum_name not in candidates:
        candidates.append(enum_name)
    info["candidates"] = candidates
    info["enumeration_hit"] = enum_name

    # ① 精确文件名（区分大小写）
    exact = set(family_files)
    for candidate in candidates:
        if candidate in exact:
            info["resolved"] = candidate
            info["resolved_by"] = ("directory_enumeration" if candidate == enum_name
                                   and candidate not in wpk_name_candidates(family, pkg)
                                   else "exact_name")
            return os.path.join(directory, candidate), info

    # ② 大小写不敏感兜底，但回报真实磁盘名
    for candidate in candidates:
        if os.path.isfile(os.path.join(directory, candidate)):
            actual = _actual_on_disk_name(directory, candidate) or candidate
            info["resolved"] = actual
            info["resolved_by"] = "case_insensitive_fallback"
            info["requested_name"] = candidate
            return os.path.join(directory, actual), info

    info["resolved_by"] = "none"
    info["reason"] = "no_candidate_wpk_present"
    if skip_log is not None:
        skip_log.record("wpk_unresolved", **info)
    return None, info


# ================================================================ IDX 表

def parse_idx_entries(idx_path: str | os.PathLike[str]) -> list[dict[str, Any]]:
    """解析 ``.idx`` 条目表：32 B 头 + 36 B/条。

    字段（与 ``MarcosVLl2/NeoXtractor core/wpk/idx_reader.py`` 互相印证）：

    ==========  ====  ==========================================
    记录内偏移   宽度  含义
    ==========  ====  ==========================================
    ``0x00``     16    内容 hash（原始 16 B）
    ``0x14``      1    包号 ``pkg``（即 u32@0x14 的低字节）
    ``0x18``      4    条目在 .wpk 内的偏移
    ``0x1C``      4    **载荷**长度
    ``0x20``      2    **1DPW 头**长度（不要写死 48）
    ==========  ====  ==========================================
    """
    blob = Path(idx_path).read_bytes()
    entries: list[dict[str, Any]] = []
    position = IDX_HEADER_SIZE
    while position + IDX_ENTRY_SIZE <= len(blob):
        digest = blob[position:position + 16]
        _f1, f2, offset, payload_size = struct.unpack_from("<IIII", blob, position + 16)
        header_size = struct.unpack_from("<H", blob, position + 32)[0]
        entries.append({
            "index": len(entries),
            "hash": digest.hex(),
            "pkg": f2 & 0xFF,
            "f2_raw": f2,
            "offset": offset,
            "payload_size": payload_size,
            "header_size": header_size,
            "total_size": header_size + payload_size,
        })
        position += IDX_ENTRY_SIZE
    return entries


# ================================================================ NPK

_TABLE_CACHE: "dict[tuple, dict[str, Any]]" = {}
_TABLE_CACHE_LOCK = threading.Lock()


def clear_table_cache() -> None:
    """清空已解密的 NPK 表缓存。"""
    with _TABLE_CACHE_LOCK:
        _TABLE_CACHE.clear()


def table_cache_info() -> dict[str, Any]:
    with _TABLE_CACHE_LOCK:
        return {"entries": len(_TABLE_CACHE), "max_entries": MAX_TABLE_CACHE,
                "keys": [k[0] for k in _TABLE_CACHE]}


def package_key(path: str | os.PathLike[str]) -> tuple[str, str]:
    """NPK 包的**唯一键**：``(解析后的完整路径, basename)``。

    修复：只用 basename 作键时，同名包会互相覆盖。实测 ``E:\\mrzh`` 下有
    5 个 ``script*.npk`` 却只有 3 个不同 basename，丢了 115,155 ~ 167,120 条。
    """
    resolved = Path(path).resolve()
    return (str(resolved), resolved.name)


@dataclass
class NpkEntry:
    """NPK 条目表里的一条（元数据，不含载荷）。"""

    package: str
    package_name: str
    entry_index: int
    file_id: int
    offset: int
    packed: int
    decoded: int
    crc_packed: int
    crc_decoded: int
    flag: int
    reserved: bytes = b""

    @property
    def file_id_hex(self) -> str:
        return f"{self.file_id:016X}"

    def as_dict(self) -> dict[str, Any]:
        return {
            "package": self.package, "package_name": self.package_name,
            "entry_index": self.entry_index, "file_id": self.file_id_hex,
            "offset": self.offset, "packed": self.packed, "decoded": self.decoded,
            "crc_packed": self.crc_packed, "crc_decoded": self.crc_decoded,
            "flag": self.flag,
        }


class NpkArchive:
    """NPK 只读容器。

    设计要点：

    * 头部（48 B）与条目表**只解密一次**并缓存，重复打开同一文件不再重复解密。
    * ``iter_entries()`` 是**纯表遍历**，不碰载荷，用于"快速列举模式"。
    * ``read_entry()`` 才读载荷并按 ``classify_codec`` 判定解码。
    """

    def __init__(self, path: str | os.PathLike[str], use_cache: bool = True):
        self.path = Path(path)
        self.package, self.package_name = package_key(self.path)
        self.use_cache = use_cache
        self.skip_log = SkipLog(stage=f"npk:{self.package_name}")
        self._handle = None
        self._table: bytes = b""
        self.header: dict[str, Any] = {}
        self._entries: list[NpkEntry] = []
        self._load()

    # -------------------------------------------------- 内部
    def _load(self) -> None:
        stat = self.path.stat()
        cache_key = (self.package, stat.st_size, stat.st_mtime_ns)
        cached = None
        if self.use_cache:
            with _TABLE_CACHE_LOCK:
                cached = _TABLE_CACHE.get(cache_key)
        if cached is not None:
            self.header = cached["header"]
            self._table = cached["table"]
            self._entries = cached["entries"]
            self.header["table_cache_hit"] = True
            return

        with self.path.open("rb") as handle:
            raw_header = handle.read(NPK_HEADER_SIZE)
            header = aes_ecb_decrypt(raw_header)
            if len(header) < 24 or header[8:12] != b"NXPK":
                raise ValueError(f"非 NXPK 容器: {self.path}")
            version = struct.unpack_from("<i", header, 12)[0]
            table_offset = struct.unpack_from("<I", header, 16)[0]
            entry_count = struct.unpack_from("<I", header, 20)[0]
            if table_offset >= stat.st_size or entry_count > 4_000_000:
                raise ValueError(f"NPK 表越界: offset={table_offset} count={entry_count}")
            handle.seek(table_offset)
            raw_table = handle.read(entry_count * NPK_ENTRY_SIZE)
        table = aes_ecb_decrypt(raw_table)

        self.header = {
            "path": str(self.path), "package": self.package,
            "package_name": self.package_name, "size": stat.st_size,
            "version": version, "table_offset": table_offset,
            "entries_declared": entry_count,
            "table_cache_hit": False,
        }
        self._table = table
        entries: list[NpkEntry] = []
        for index in range(min(entry_count, len(table) // NPK_ENTRY_SIZE)):
            base = index * NPK_ENTRY_SIZE
            file_id, offset, packed, decoded = struct.unpack_from("<QIII", table, base)
            crc_packed = struct.unpack_from("<I", table, base + 20)[0]
            crc_decoded = struct.unpack_from("<I", table, base + 24)[0]
            flag = struct.unpack_from("<i", table, base + 28)[0]
            entries.append(NpkEntry(
                package=self.package, package_name=self.package_name,
                entry_index=index, file_id=file_id, offset=offset,
                packed=packed, decoded=decoded, crc_packed=crc_packed,
                crc_decoded=crc_decoded, flag=flag, reserved=table[base + 32:base + 48],
            ))
        self._entries = entries
        if self.use_cache:
            with _TABLE_CACHE_LOCK:
                if len(_TABLE_CACHE) >= MAX_TABLE_CACHE:
                    _TABLE_CACHE.pop(next(iter(_TABLE_CACHE)))
                _TABLE_CACHE[cache_key] = {"header": self.header, "table": table, "entries": entries}

    def _ensure_handle(self):
        if self._handle is None or self._handle.closed:
            self._handle = self.path.open("rb")
        return self._handle

    # -------------------------------------------------- 公开
    def close(self) -> None:
        if self._handle is not None and not self._handle.closed:
            self._handle.close()

    def __enter__(self) -> "NpkArchive":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def iter_entries(self) -> Iterator[NpkEntry]:
        """惰性产出**全表**条目（``entry_index/file_id/offset/packed/decoded/flag``）。

        这是此前缺失的能力：``scan_package()`` 只返回关键词过滤后的 hits，
        使用者不得不自己重写表遍历。
        """
        for entry in self._entries:
            yield entry

    def get_entry(self, entry_index: int | None = None,
                  file_id: int | None = None) -> NpkEntry:
        if file_id is not None:
            for entry in self._entries:
                if entry.file_id == file_id:
                    return entry
            raise KeyError(f"file_id {file_id:016X} 不在 {self.package_name}")
        if entry_index is None:
            raise ValueError("必须给 entry_index 或 file_id 之一")
        if not (0 <= entry_index < len(self._entries)):
            raise IndexError(f"entry_index {entry_index} 越界（0..{len(self._entries) - 1}）")
        return self._entries[entry_index]

    def read_entry(self, entry_index: int | None = None, file_id: int | None = None,
                   decode: bool = True) -> bytes:
        """读取单条载荷；``decode=True`` 时按 flag + 魔数/试解解出明文。"""
        entry = self.get_entry(entry_index=entry_index, file_id=file_id)
        return self.read_entry_obj(entry, decode=decode)

    def read_entry_obj(self, entry: NpkEntry, decode: bool = True) -> bytes:
        size = self.path.stat().st_size
        if not (0 <= entry.offset < size) or entry.packed <= 0 or entry.offset + entry.packed > size:
            self.skip_log.record("packed_range_outside_source", **entry.as_dict())
            raise ValueError(f"条目 {entry.entry_index} 载荷越界")
        handle = self._ensure_handle()
        handle.seek(entry.offset)
        packed = handle.read(entry.packed)
        if len(packed) != entry.packed:
            self.skip_log.record("packed_read_short", **entry.as_dict())
            raise ValueError(f"条目 {entry.entry_index} 载荷读取不完整")
        if not decode:
            return packed
        return npk_decode_entry(packed, entry.decoded, entry.flag, entry=entry,
                                skip_log=self.skip_log)

    def list_paths(self, fast: bool = True, limit: int | None = None) -> dict[int, str]:
        """遍历全表解出内嵌逻辑路径，返回 ``{file_id: path}``。

        ``fast=True``：只在载荷**头部若干字节**上试 ``parse_logical_path``，
        不解压大载荷（快很多）。``fast=False``：完整解码后再解路径（更全，更慢）。
        """
        paths: dict[int, str] = {}
        size = self.path.stat().st_size
        handle = self._ensure_handle()
        for index, entry in enumerate(self._entries):
            if limit is not None and index >= limit:
                break
            if not (0 <= entry.offset < size) or entry.packed <= 0 or entry.offset + entry.packed > size:
                self.skip_log.record("list_paths_bounds", **entry.as_dict())
                continue
            found = ""
            if fast:
                handle.seek(entry.offset)
                head = handle.read(min(entry.packed, 512))
                found = parse_logical_path(head)
                if found:
                    paths[entry.file_id] = found
                    continue
                if entry.flag not in (0, 2):
                    self.skip_log.record("list_paths_flag_skipped", **entry.as_dict())
                    continue
            try:
                data = self.read_entry_obj(entry, decode=True)
            except Exception as exc:  # noqa: BLE001
                self.skip_log.record("list_paths_decode_failed", error=repr(exc), **entry.as_dict())
                continue
            found = parse_logical_path(data)
            if found:
                paths[entry.file_id] = found
        return paths


def npk_decode_entry(packed: bytes, decoded_size: int, flag: int,
                     entry: NpkEntry | None = None,
                     skip_log: SkipLog | None = None) -> bytes:
    """NPK 条目解码：flag 0 = AES + (``i64==1`` ? zlib : 原样)；flag 2 = LZ4；其余走魔数/试解。

    与参考实现 ``NpkUnpack.cs`` 对齐的要点：
    - flag 0：先 AES-ECB 解密整块，再判 ``i64@0 == 1``，成立则从偏移 18 起 zlib 解压。
    - flag 2：LZ4 block，``uncompressed_size = decoded_size``。
    - 其它 flag：参考实现直接原样输出；我们**不照抄这个静默行为**，
      改走魔数/试解，判不出来就如实报 unresolved。
    """
    if flag == 0:
        decrypted = aes_ecb_decrypt(packed)
        if (len(decrypted) >= 18
                and struct.unpack_from("<Q", decrypted, 0)[0] == 1
                and decrypted[16:18] in ZLIB_MAGICS):
            import zlib
            try:
                return zlib.decompress(decrypted[18:])
            except zlib.error:
                try:
                    return zlib.decompress(decrypted[18:], -15)
                except zlib.error as exc:
                    if skip_log is not None:
                        skip_log.record("zlib_failed", error=repr(exc),
                                        **(entry.as_dict() if entry else {}))
                    raise
        return decrypted
    if flag == 2:
        return decompress_lz4_block(packed, decoded_size)
    result = classify_codec(packed, len(packed), decoded_size, flag)
    if not result.ok:
        if skip_log is not None:
            skip_log.record("unresolved_codec", codec=result.codec, how=result.how,
                            error=result.error, **(entry.as_dict() if entry else {}))
        raise UnresolvedCodec(f"flag={flag} 无法判定压缩类型: {result.error}",
                              {"flag": flag, "packed": len(packed), "decoded": decoded_size})
    return result.data  # type: ignore[return-value]


# ---------------------------------------------------------------- 模块级便捷函数

def _with_archive(path, fn):
    archive = NpkArchive(path)
    try:
        return fn(archive)
    finally:
        archive.close()


def iter_entries(path: str | os.PathLike[str]) -> Iterator[NpkEntry]:
    """打开 NPK 并惰性产出全表条目（``entry_index/file_id/offset/packed/decoded/flag``）。

    用法::

        for entry in iter_entries(r"E:\\mrzh\\Documents\\script.npk"):
            print(entry.entry_index, entry.file_id_hex, entry.flag)

    注意：返回的是生成器，底层归档对象在生成器结束前保持打开。
    """
    archive = NpkArchive(path)
    try:
        for entry in archive.iter_entries():
            yield entry
    finally:
        archive.close()


def list_paths(path: str | os.PathLike[str], fast: bool = True,
               limit: int | None = None) -> dict[int, str]:
    """返回 ``{file_id: 内嵌逻辑路径}``（全表遍历）。"""
    return _with_archive(path, lambda a: a.list_paths(fast=fast, limit=limit))


def read_entry(path: str | os.PathLike[str], entry_index: int | None = None,
               file_id: int | None = None, decode: bool = True) -> bytes:
    """读取单个 NPK 条目载荷（按 ``entry_index`` 或 ``file_id`` 定位）。"""
    return _with_archive(path, lambda a: a.read_entry(
        entry_index=entry_index, file_id=file_id, decode=decode))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
