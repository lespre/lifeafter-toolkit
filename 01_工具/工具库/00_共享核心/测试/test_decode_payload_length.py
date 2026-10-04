# -*- coding: utf-8 -*-
"""载荷长度体检 —— 防回归测试（2026-09-28）。

背景（实测来源）：
    脚本把条目载荷 slice 到 900,000 B 后交给解码器，而该条目 decoded=913,940
    ⇒ ``classify_codec``一路试解失败，最后报

        UnresolvedCodec: flag=12 无法判定压缩类型: no codec matched

    这是**谎报**：把「你给的字节数不对」说成「这个格式解码器不认识」，
    排查方向会被带偏（去查格式、查 flag、查字典），真因只是数据被截断。

修法：
    * ``classify_codec`` 新增 ``declared_packed``：给了就先做长度体检，
      长度不符直接给准确诊断，不再往下试解。
    * ``npk_decode_entry`` 在分派前先拦「给少了」（任何 flag 下都无歧义）。
    * 新增 ``TruncatedPayload``（别名 ``PayloadLengthMismatch``）。
    * 新增判据 ``CODEC_HOW_PAYLOAD_MISMATCH`` / ``CODEC_HOW_ALREADY_DECODED``。

本测试锁住四件事：
    1. 真截断 → TruncatedPayload，且报文里带「给了多少 / 声明多少」
    2. 给的是已解码载荷 → how == already_decoded_payload，且数据原样返回
    3. 正规载荷（len == declared_packed）→ 正常解出，不被体检误拦
    4. 不传 declared_packed → 退回历史行为（不体检），保证向后兼容
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

PACK = Path(__file__).resolve().parents[2] / "01_解码定位复原" / "解包与扫描"


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod          # ★ la_unpack_core 里 @dataclass 需要模块先注册
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def core():
    return _load("la_unpack_core_len_t", PACK / "la_unpack_core.py")


@pytest.fixture(scope="module")
def sample(core):
    """一个真实的 zstd 载荷：明文 4096 B → 压缩后若干字节。"""
    zstandard = pytest.importorskip("zstandard")
    plain = bytes((i * 7) % 251 for i in range(4096))
    packed = zstandard.ZstdCompressor().compress(plain)
    assert packed[:4] == core.ZSTD_MAGIC, "样本必须是 zstd（否则测的不是这条路）"
    return plain, packed


def test_truncated_payload_is_diagnosed_not_miscoded(core, sample):
    """① 给少了 → TruncatedPayload，报文带真实数字。"""
    _, packed = sample
    declared = len(packed)
    given = packed[: declared // 2]

    with pytest.raises(core.TruncatedPayload) as ei:
        core.npk_decode_entry(given, 4096, 12, declared_packed=declared)

    msg = str(ei.value)
    assert str(len(given)) in msg and str(declared) in msg, "报文必须报出「给了多少 / 声明多少」"
    assert ei.value.detail["given"] == len(given)
    assert ei.value.detail["declared_packed"] == declared
    # ★ 关键：不能说成「无法判定压缩类型」
    assert "无法判定压缩类型" not in msg


def test_already_decoded_payload_is_labelled(core, sample):
    """② 给的是已解码载荷 → 明确标记，不假装成某个 codec 解出来的。"""
    plain, _ = sample
    res = core.classify_codec(plain, len(plain), len(plain), 12,
                              declared_packed=42)
    assert res.ok
    assert res.how == core.CODEC_HOW_ALREADY_DECODED
    assert res.data == plain, "已解码载荷必须原样返回"


def test_valid_payload_passes_health_check(core, sample):
    """③ 正规载荷（len == declared_packed）→ 正常解出，不被体检误拦。"""
    plain, packed = sample
    out = core.npk_decode_entry(packed, len(plain), 12, declared_packed=len(packed))
    assert out == plain


def test_over_long_payload_is_mismatch(core, sample):
    """⑤ 给多了（长度既不等于 packed 也不等于 decoded）→ 判为长度不符。"""
    plain, packed = sample
    fat = packed + b"\x00" * 1000
    res = core.classify_codec(fat, len(fat), len(plain), 12,
                              declared_packed=len(packed))
    assert not res.ok
    assert res.how == core.CODEC_HOW_PAYLOAD_MISMATCH
    assert "载荷长度不符" in res.error


def test_backward_compatible_without_declared(core, sample):
    """④ 不传 declared_packed → 历史行为，照样解得出（向后兼容）。"""
    plain, packed = sample
    out = core.npk_decode_entry(packed, len(plain), 12)
    assert out == plain


def test_exception_hierarchy_and_alias(core):
    """新增异常与既有异常同族，调用方 except 不必改。"""
    assert issubclass(core.TruncatedPayload, RuntimeError)
    assert core.PayloadLengthMismatch is core.TruncatedPayload
    assert core.TruncatedPayload is not core.UnresolvedCodec, "两者语义不同，不能合并"
