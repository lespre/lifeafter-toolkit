# -*- coding: utf-8 -*-
"""flag 0 的两条路必须可辨识 —— 防回归测试。

背景（2026-09-26 实测）：
    flag 0 解码有两条路：
      判据成立（i64@0==1 且 [16:18] 是 zlib magic）→ 真 zlib 解压
      判据不成立                                    → 原样返回解密后字节
    第二条路【不报错、不标记】，而调用方拿到的长度又可能与 packed 相同
    ⇒ 分不清「解压后的明文」与「原样密文」。

    更糟的是 unpack_entry_ex 原先用 `data is not packed`（身份比较）判 codec，
    而回退返回的 decrypted 也是新对象 ⇒ 回退被误标成 'aes_zlib'。
    实测 180 条样本里 163 条（90.6%）被误标。

本测试锁住三件事：
  1. npk_flag0_decode 对「判据成立的样本」报 aes_zlib，对「不成立的」报 aes_plain
  2. unpack_entry_ex 的 codec 与 how 一致（raw ↔ aes_plain，aes_zlib ↔ aes_zlib）
  3. 一个被破坏头部的样本必须落进 aes_plain（而不是伪装成 aes_zlib）
"""
from __future__ import annotations

import importlib.util
import struct
import sys
from pathlib import Path

import pytest

def _find_pack() -> Path:
    """向上搜索「01_解码定位复原/解包与扫描」——不手算 parents[N]。

    ★ 本文件在 工具库/00_共享核心/tests/ 下，层级比看上去深一层；
      手算 parents[N] 已经错过一次（指向 01_工具 而非 工具库）。
    """
    here = Path(__file__).resolve()
    for up in here.parents:
        cand = up / "01_解码定位复原" / "解包与扫描"
        if cand.is_dir():
            return cand
    raise RuntimeError("找不到 01_解码定位复原/解包与扫描")


PACK = _find_pack()


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod        # ★ la_unpack_core 里 @dataclass 需要模块先注册
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def core():
    return _load("la_unpack_core_t", PACK / "la_unpack_core.py")


@pytest.fixture(scope="module")
def nr():
    return _load("npk_reader_t", PACK / "npk_reader.py")


def _fake_flag0(payload: bytes, compressed: bool) -> bytes:
    """造一个 flag 0 的载荷：AES 加密一段带标记的数据。

    compressed=True  → i64@0=1 且 [16:18] 是 zlib magic ⇒ 走解压
    compressed=False → 标记不符 ⇒ 走回退
    """
    import zlib
    if compressed:
        body = zlib.compress(b"hello-lifeafter" * 20)
        head = struct.pack("<Q", 1) + b"\x00" * 8 + body[:2]
        raw = head + body[2:]
    else:
        raw = struct.pack("<Q", 0xDEADBEEF) + b"\x01" * 8 + payload
    return core_encrypt(raw)


def core_encrypt(data: bytes) -> bytes:
    """用与解码器同一把密钥做 AES-ECB 加密（测试用，反向操作）。"""
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    key = _load("la_unpack_core_k", PACK / "la_unpack_core.py").AES_KEY
    usable = len(data) // 16 * 16
    enc = Cipher(algorithms.AES(key), modes.ECB()).encryptor()
    return enc.update(data[:usable]) + enc.finalize() + data[usable:]


def test_flag0_reports_which_path_was_taken(core):
    """判据成立报 aes_zlib；不成立报 aes_plain（都不抛异常）。"""
    ok = _fake_flag0(b"", compressed=True)
    data, how = core.npk_flag0_decode(ok)
    assert how == core.CODEC_HOW_FLAG0_ZLIB, f"判据成立却报 {how}"
    assert data == b"hello-lifeafter" * 20

    plain = _fake_flag0(b"raw-payload-here", compressed=False)
    data2, how2 = core.npk_flag0_decode(plain)
    assert how2 == core.CODEC_HOW_FLAG0_PLAIN, f"判据不成立却报 {how2}"
    assert len(data2) == len(plain), "回退路径应原样返回（长度等于 packed）"


def test_unpack_ex_codec_agrees_with_how(core, nr):
    """codec 与 how 必须一致 —— 这条就是防「回退被误标成 aes_zlib」。"""
    for compressed, want_codec in ((True, "aes_zlib"), (False, "raw")):
        pkg = _fake_flag0(b"xyz" * 10, compressed=compressed)
        r = nr.unpack_entry_ex(pkg, 0, 0)
        assert r.codec == want_codec, \
            f"compressed={compressed}: codec={r.codec}（应为 {want_codec}）"
        if want_codec == "raw":
            # ★ 关键断言：回退不能伪装成 aes_zlib
            assert r.codec != "aes_zlib", "回退路径又被误标成 aes_zlib 了（旧 bug 回归）"
            assert r.how == core.CODEC_HOW_FLAG0_PLAIN
        else:
            assert r.how == core.CODEC_HOW_FLAG0_ZLIB


def test_broken_header_falls_into_plain_not_zlib(core, nr):
    """破坏 i64@0 判据 ⇒ 必须落进 aes_plain，不能伪装成 aes_zlib。"""
    ok = _fake_flag0(b"", compressed=True)
    bad = bytearray(ok)
    bad[0] ^= 0xFF                     # 破坏 i64@0（AES 解密后应是 1）
    r = nr.unpack_entry_ex(bytes(bad), 0, 0)
    assert r.codec == "raw", f"头部被破坏后 codec={r.codec}（应为 raw）"
    assert r.how == core.CODEC_HOW_FLAG0_PLAIN
