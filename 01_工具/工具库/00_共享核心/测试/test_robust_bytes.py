# -*- coding: utf-8 -*-
r"""解包原语的防回归契约测试。

这些 bug 每一个都在真实数据上出现过，且都是「偶发/难查」类型：
  · zstandard 参数字数
  · 帧切分漏帧（要求前导零）
  · 失败分支丢部分成功
  · 变长记录的对齐填充
  · 大窗口熵误判「加密」
  · CRLF 污染文件名

本测试把每条钉成断言 —— 改坏就会红。
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from toolkit_core import robust_bytes as RB  # noqa: E402

zstd = pytest.importorskip("zstandard")


# ── ① zstandard 参数字数 ────────────────────────────────────────────────

def test_decompress_one_roundtrip():
    payload = b"x" * 5000
    frame = zstd.ZstdCompressor().compress(payload)
    assert RB.decompress_one(frame) == payload


def test_decompress_one_bad_input_returns_none():
    assert RB.decompress_one(b"not a frame") is None
    assert RB.decompress_one(b"") is None


# ── ② 帧切分不能要求前导零 ──────────────────────────────────────────────

def test_two_frames_without_zero_prefix_are_both_found():
    a = zstd.ZstdCompressor().compress(b"A" * 100)
    b = zstd.ZstdCompressor().compress(b"B" * 100)
    joined = a + b                       # ★ 帧间无 00 00 00
    assert len(RB.find_zstd_offsets(joined)) == 2
    assert len(RB.split_zstd_frames(joined)) == 2


def test_frames_with_zero_padding_still_split():
    a = zstd.ZstdCompressor().compress(b"A" * 100)
    b = zstd.ZstdCompressor().compress(b"B" * 100)
    joined = a + b"\x00\x00\x00" + b
    frames = RB.split_zstd_frames(joined)
    assert len(frames) == 2
    assert RB.decompress_one(frames[0]) == b"A" * 100
    assert RB.decompress_one(frames[1]) == b"B" * 100


# ── ③ 坏帧不能吞掉已解出的部分 ──────────────────────────────────────────

def test_partial_success_is_kept():
    good = zstd.ZstdCompressor().compress(b"GOOD" * 50)
    broken = RB.ZSTD_MAGIC + b"\x00" * 16          # 假帧
    r = RB.decompress_zstd_frames(good + broken)
    assert r["n_ok"] >= 1
    assert r["data"] == b"GOOD" * 50
    assert r["bad_frames"], "坏帧应被记录而不是静默"


def test_all_bad_returns_not_ok():
    r = RB.decompress_zstd_frames(RB.ZSTD_MAGIC + b"\x00" * 16)
    assert r["ok"] is False


# ── ④ 对齐填充 ─────────────────────────────────────────────────────────

def test_aligned_length_found_after_padding():
    rec = b"\x00\x00" + (123).to_bytes(4, "little") + b"z" * 123
    assert RB.find_u32_aligned(rec, 0) == (2, 123)


def test_aligned_length_rejects_out_of_buffer_value():
    # pad=0 处的数看似合理但会让数据越界 ⇒ 必须跳过，取 pad=2 的正确值
    rec = b"\x00\x00" + (123).to_bytes(4, "little") + b"z" * 123
    got = RB.find_u32_aligned(rec, 0)
    assert got is not None and got[1] == 123


def test_aligned_accept_callback():
    rec = b"\x00\x00" + (5).to_bytes(4, "little") + b"\xf3rest"
    got = RB.find_u32_aligned(rec, 0, accept=lambda v, o: rec[o:o + 1] == b"\xf3")
    assert got == (2, 5)


def test_aligned_none_when_nothing_fits():
    assert RB.find_u32_aligned(b"\xff\xff\xff\xff\xff\xff", 0) is None


# ── ⑤ 熵判据：明文不该被判成密文（大窗口平均值会误判）──────────────

# 真实样本：本地 script 容器拆出的条目（明文 marshal 字节码）
# ★ 2026-10-01 层级对标后：老载荷铺法已删 ⇒ 优先在老位置找，找不到就到
#   新层级 <树>/Documents/script.py314.lc.npk/_未命名/ 里扫一个满头是 marshal 的 .bin。
_REAL_MARSHAL_OLD = Path(r"E:/la拆包项目/03_执行/20_提取/全量实测_20260926/"
                         r"files/script.py314.lc/00000000.bin")
_TREE_MARSHAL_DIR = (Path(r"E:/la拆包项目/03_执行/41_还原树")
                     / "Documents" / "script.py314.lc.npk" / "_未命名")


def _find_real_marshal() -> Path:
    if _REAL_MARSHAL_OLD.is_file():
        return _REAL_MARSHAL_OLD
    if _TREE_MARSHAL_DIR.is_dir():
        for p in sorted(_TREE_MARSHAL_DIR.glob("*.bin")):
            try:
                if p.stat().st_size > 1000 and p.read_bytes()[:4] == b"\x73\x00\x00\x00":
                    return p
            except OSError:
                continue
    return _REAL_MARSHAL_OLD


_REAL_MARSHAL = _find_real_marshal()


def test_real_marshal_entry_not_flagged_as_encrypted():
    """★ 本轮最大的误判来源。

    真实的 marshal 字节码条目，大窗口(16KB)平均熵可达 7.9，
    与密文无法区分 ⇒ 必须用「小窗口 + 中位数」判据，且判为【非加密】。
    """
    if not _REAL_MARSHAL.is_file():
        pytest.skip("真实样本不存在：%s" % _REAL_MARSHAL)
    data = _REAL_MARSHAL.read_bytes()
    assert len(data) > 1000
    assert not RB.looks_encrypted(data), \
        "真实 marshal 明文被误判成加密（大窗口平均熵陷阱）"


def test_structurally_rich_plaintext_not_flagged():
    """构造样本：指令区（低熵）+ 字符串常量（低熵）。"""
    import struct
    parts = []
    for i in range(400):
        parts.append(bytes([0x64, 0x00, 0x7a, 0x1c, 0x00, 0x53, 0x00, 0x44, 0x00]) * 4)
        parts.append(b"com_components_avatar_PlayerComp\x00self\x00data\x00"
                     + struct.pack("<I", i))
    plain = b"".join(parts)
    assert len(plain) > 20000
    assert not RB.looks_encrypted(plain), "结构化明文被误判成加密"


def test_true_ciphertext_is_flagged():
    import hashlib
    rnd = b"".join(hashlib.sha256(str(i).encode()).digest() for i in range(1000))
    assert RB.looks_encrypted(rnd)


def test_shannon_sanity():
    assert RB.shannon(b"") == 0.0
    assert RB.shannon(b"\x00" * 1000) == 0.0
    assert abs(RB.shannon(bytes(range(256))) - 8.0) < 1e-6


def test_text_ratio():
    assert RB.text_ratio(b"abcdef") == 1.0
    assert RB.text_ratio(b"\x00\x01\x02") == 0.0


# ── ⑦ 文件名卫生 ───────────────────────────────────────────────────────

@pytest.mark.parametrize("raw,want", [
    ("abc.npk\r", "abc.npk"),
    ("abc.npk\n", "abc.npk"),
    ("abc.npk\r\n", "abc.npk"),
    ("  x  ", "x"),
])
def test_safe_stem_strips_crlf(raw, want):
    assert RB.safe_stem(raw) == want


def test_safe_stem_replaces_bad_chars():
    got = RB.safe_stem("a/b\\c:d*e?f")
    for ch in '<>:"/\\|?*':
        assert ch not in got


def test_safe_stem_fallback_on_empty():
    assert RB.safe_stem("\r\n  ") == "unnamed"
    assert RB.safe_stem("", fallback="x") == "x"


def test_iter_lines_strips_crlf(tmp_path):
    p = tmp_path / "list.txt"
    p.write_bytes(b"a.npk\r\nb.npk\r\nc.npk\n")
    assert list(RB.iter_lines(p)) == ["a.npk", "b.npk", "c.npk"]


# ── 边界读取 ───────────────────────────────────────────────────────────

def test_u32_reads_are_bounds_safe():
    assert RB.u32_le(b"\x01\x00\x00\x00") == 1
    assert RB.u32_be(b"\x00\x00\x00\x01") == 1
    assert RB.u32_le(b"\x01\x00") is None          # 越界不抛
    assert RB.u32_le(b"", -1) is None
    assert RB.u32_le(b"\x01\x00\x00\x00", 1) is None


# ── 自检整体 ───────────────────────────────────────────────────────────

def test_selfcheck_all_green():
    r = RB.selfcheck()
    fails = [k for k, v in r.items() if not v]
    assert not fails, "自检未过：%s" % fails
