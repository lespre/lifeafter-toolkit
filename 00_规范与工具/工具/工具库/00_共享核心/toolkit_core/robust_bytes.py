# -*- coding: utf-8 -*-
r"""解包链路的稳健原语 —— 把踩过的坑一次性封装掉。

## 为什么有这个模块

本项目的解包链路（NPK/GPK/overlay/FSB5…）反复出现同一类 bug：
「偶发解不开」「误判成加密」「差几个字节对不齐」。逐个打补丁治不了根，
因为**每个脚本都自己写一遍** zstd 解压、长度读取、路径处理。
本模块把这些原语收成唯一实现，带边界检查与明确的失败语义。

## 收录的坑（每条都有实测来源）

① zstandard 0.25 的 `decompressobj().decompress()` **只收 1 个参数**；
   传 `max_output_size=` 会 TypeError ⇒ 之前 11 个 overlay 包全解失败。
② 帧切分若要求「帧前必须有 N 个零」会**漏帧**：
   实测 overlay 包只有 153/192 个魔数前面是 0 ⇒ 漏掉 76% 的帧
   （instance.layers.1.1.1 实际 192 帧，只切出 45 帧）。
③ 「某一帧失败就整体 return」会**丢掉部分成功**：
   effect 包前 2 帧解得开、第 3 帧坏，结果什么信息都没留下。
④ 变长记录之间可能有 **0~3 字节对齐填充**，`[4B 长度]` 不在紧邻位置；
   直接把紧邻的 4 字节当长度会读出天文数字 ⇒ 被**误判成加密**。
   正确做法：在 0~3 的 pad 里找「能让后续结构成立」的那个。
⑤ 判断「是否加密」不能只看**大窗口平均熵**：明文（marshal 字节码）
   与常量池混在一起时，16KB 窗口熵可达 7.9，与密文无法区分。
   要按**小窗口/代表项**看，并辅以「能否 marshal / 首字节是否为已知标记」。

## 用法

    from toolkit_core.robust_bytes import (
        decompress_zstd_frames, find_u32_aligned, looks_encrypted,
        safe_stem, strip_crlf, u32_le, u32_be, in_bounds)
"""
from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence

try:
    import zstandard as zstd
except ImportError:                                     # pragma: no cover
    zstd = None

ZSTD_MAGIC = b"\x28\xb5\x2f\xfd"


# ══════════════════════════════════════════════════════════════════════════
# 边界安全的整数读取（不许越界抛异常，越界返回 None）
# ══════════════════════════════════════════════════════════════════════════

def in_bounds(b: bytes, off: int, n: int) -> bool:
    return 0 <= off and off + n <= len(b)


def u32_le(b: bytes, off: int = 0) -> int | None:
    if not in_bounds(b, off, 4):
        return None
    return int.from_bytes(b[off:off + 4], "little")


def u32_be(b: bytes, off: int = 0) -> int | None:
    if not in_bounds(b, off, 4):
        return None
    return int.from_bytes(b[off:off + 4], "big")


# ══════════════════════════════════════════════════════════════════════════
# zstd：切帧 + 解压（坑 ①②③）
# ══════════════════════════════════════════════════════════════════════════

def find_zstd_offsets(b: bytes) -> list[int]:
    """所有 zstd 魔数的位置。

    ★ 不要在「魔数」上加额外前置条件（如必须有 N 个零）—— 那会漏帧（坑②）。
      真正的帧边界由「下一个魔数」界定；帧间的填充字节在末尾剥掉。
    """
    return [m.start() for m in re.finditer(re.escape(ZSTD_MAGIC), b)]


def split_zstd_frames(b: bytes, *, trim_tail_zeros: bool = True) -> list[bytes]:
    """按魔数位置把数据切成若干 zstd 帧。

    trim_tail_zeros：帧尾剥掉 0 填充（帧间对齐），默认开。
    """
    offs = find_zstd_offsets(b)
    if not offs:
        return []
    out = []
    for k, s in enumerate(offs):
        e = offs[k + 1] if k + 1 < len(offs) else len(b)
        if trim_tail_zeros:
            while e > s and b[e - 1] == 0:
                e -= 1
        out.append(b[s:e])
    return out


def decompress_one(frame: bytes) -> bytes | None:
    """解一个 zstd 帧；失败返回 None（不抛）。

    ★ 坑①：`decompressobj().decompress()` 只收 1 个参数，
      传 max_output_size 会 TypeError（zstandard 0.25 实测）。
    """
    if zstd is None or not frame:
        return None
    try:
        o = zstd.ZstdDecompressor().decompressobj()
        d = o.decompress(frame)
        return d if d else None
    except Exception:
        return None


def decompress_zstd_frames(b: bytes, *, max_frames: int = 200_000) -> dict:
    """稳健解压：切帧 → 逐帧解 → 返回「解出多少 / 哪帧坏了」。

    ★ 坑③：坏帧不终止整个流程，已解出的部分照常返回。
    """
    frames = split_zstd_frames(b)
    pieces: list[bytes] = []
    bad: list[int] = []
    for k, fr in enumerate(frames[:max_frames]):
        d = decompress_one(fr)
        if d is None:
            bad.append(k)
        else:
            pieces.append(d)
    blob = b"".join(pieces)
    return {"n_frames": len(frames), "n_ok": len(pieces), "bad_frames": bad,
            "pieces": pieces, "data": blob, "bytes": len(blob),
            "ok": bool(pieces)}


# ══════════════════════════════════════════════════════════════════════════
# 变长记录的对齐探测（坑④）
# ══════════════════════════════════════════════════════════════════════════

def find_u32_aligned(b: bytes, off: int, *, max_pad: int = 3,
                     lo: int = 1, hi: int = 8 << 20,
                     require_fits: bool = True,
                     accept=None) -> tuple[int, int] | None:
    """在 [off, off+max_pad] 里找「一个合理的 u32 长度字段」。

    返回 (pad, value)；找不到返回 None。

    ★ 坑④：变长记录之间常有 0~3 字节填充，紧邻的 4 字节未必是长度字段。
      只读紧邻位置会把天文数字当长度 ⇒ 误判成加密/损坏。

    ★★ 单看「值在 lo..hi 内」**不够** —— 实测 pad=0 处常撞上一个
       看似合理、实则错误的整数（如 0x00007b00 = 31488）。
      所以默认再要求 `off+pad+4+value <= len(b)`（数据不能越出缓冲）。
      对「数据不在同一缓冲」的场景，传 require_fits=False 自行判定。

    accept(value, data_off) 可加自定义判据（如「数据首字节必须是 \\xf3」）。
    """
    for pad in range(0, max_pad + 1):
        v = u32_le(b, off + pad)
        if v is None or not (lo <= v <= hi):
            continue
        data_off = off + pad + 4
        if require_fits and data_off + v > len(b):
            continue
        if accept is not None and not accept(v, data_off):
            continue
        return pad, v
    return None


# ══════════════════════════════════════════════════════════════════════════
# 「是否加密」的判据（坑⑤）
# ══════════════════════════════════════════════════════════════════════════

def shannon(b: bytes) -> float:
    if not b:
        return 0.0
    c = Counter(b)
    n = len(b)
    return -sum(v / n * math.log2(v / n) for v in c.values())


def looks_encrypted(seg: bytes, *, window: int = 512, thresh: float = 7.0) -> bool:
    """判断一段数据是否像密文。

    ★ 坑⑤：不能用大窗口平均熵 —— 明文（marshal 字节码）与常量池混在一起时，
      16KB 窗口能到 7.9，和密文分不开。
      这里按【小窗口 + 取中位数】判：密文每个小窗口都接近满熵，
      明文里总有若干低熵窗口把中位数拉下来。
    """
    if len(seg) < window:
        return shannon(seg) >= thresh
    vals = [shannon(seg[i:i + window]) for i in range(0, len(seg) - window + 1, window)]
    if not vals:
        return shannon(seg) >= thresh
    vals.sort()
    med = vals[len(vals) // 2]
    return med >= thresh


def text_ratio(seg: bytes) -> float:
    """可打印字符占比（含制表/换行）。"""
    if not seg:
        return 0.0
    n = sum(1 for c in seg if 32 <= c < 127 or c in (9, 10, 13))
    return n / len(seg)


# ══════════════════════════════════════════════════════════════════════════
# 路径 / 文件名卫生（坑⑦）
# ══════════════════════════════════════════════════════════════════════════

_BAD_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def strip_crlf(s: str) -> str:
    """去掉行尾 CR/LF —— 按行读文件时极易把 \\r 带进文件名。"""
    return s.rstrip("\r\n")


def safe_stem(name: str, *, maxlen: int = 120, fallback: str = "unnamed") -> str:
    """把任意字符串变成安全的文件名主干。

    ★ 坑⑦：清单文件若是 CRLF，`basename` 会把 \\r 带进文件名，
      在 Windows 上造出看似正常、实际无法按名打开的怪文件。
    """
    s = strip_crlf(str(name)).strip()
    s = _BAD_CHARS.sub("_", s)
    s = s.strip(". ")
    if not s:
        return fallback
    if len(s) > maxlen:
        s = s[:maxlen]
    return s


def iter_lines(path: Path | str, *, encoding: str = "utf-8-sig") -> Iterable[str]:
    """按行读，自动剥掉 CR/LF 与 BOM（清单类文件统一走这里）。"""
    with open(path, "r", encoding=encoding, errors="replace") as fh:
        for ln in fh:
            yield strip_crlf(ln)


# ══════════════════════════════════════════════════════════════════════════
# 自检（把坑变成可测的事实）
# ══════════════════════════════════════════════════════════════════════════

def selfcheck() -> dict:
    """跑一遍内建自检，返回逐项结果（供 pytest / CLI 调用）。"""
    import zstandard as _z
    res = {}

    # ① decompressobj 只收 1 个参数
    payload = b"hello world" * 100
    frame = _z.ZstdCompressor().compress(payload)
    res["zstd_single_arg_ok"] = (decompress_one(frame) == payload)

    # ② 三个零不是必要条件
    b = _z.ZstdCompressor().compress(b"A" * 10) + b"\x00\x00" \
        + _z.ZstdCompressor().compress(b"B" * 10)
    res["two_frames_found"] = (len(split_zstd_frames(b)) == 2)

    # ③ 坏帧不终止
    b2 = frame + b"\x28\xb5\x2f\xfd" + b"\x00" * 8
    r = decompress_zstd_frames(b2)
    res["partial_success_kept"] = (r["n_ok"] >= 1 and r["data"] == payload)

    # ④ 对齐探测
    rec = b"\x00\x00" + (123).to_bytes(4, "little") + b"x" * 123
    got = find_u32_aligned(rec, 0)
    res["aligned_len_found"] = (got == (2, 123))

    # ⑤ 熵判据：明文不该被判成密文
    plain = (b"def f():\n    return 1\n" * 200)
    res["plain_not_encrypted"] = (not looks_encrypted(plain))
    res["random_is_encrypted"] = looks_encrypted(bytes(range(256)) * 20)

    # ⑦ 文件名卫生
    res["crlf_stripped"] = (safe_stem("abc.npk\r") == "abc.npk")
    res["bad_chars_replaced"] = ("/" not in safe_stem("a/b\\c:d"))
    res["empty_fallback"] = (safe_stem("\r\n ") == "unnamed")

    return res
