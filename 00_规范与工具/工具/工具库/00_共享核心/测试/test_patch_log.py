# -*- coding: utf-8 -*-
r"""`toolkit_core.patch_log` 契约测试。

钉死这几条（都是实测踩过的）：
  ① XOR 0xAA 是关键（别的键解不出 `Patch Log Start`）
  ② 记录按 `[时间]` 锚点切，不按 `\n`
  ③ 清单是 Python dict repr（单引号）⇒ 必须能解，且单条坏不影响整体
  ④ `rel_variants` 的 bin 渠道后缀映射（`bin/x64-2` ↔ `bin/x64-a50-2`）
  ⑤ `fver` 分布统计 —— 这是「版本推到哪一版」的唯一来源
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve()
CORE = HERE.parents[1]
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from toolkit_core import patch_log as PL  # noqa: E402


def _mk_log(records, manifest_text=""):
    """合成一份补丁日志（按真实格式：记录以不可打印字节分隔 + dict repr 清单）。"""
    sep = "\x00"          # 解 XOR 后的不可打印分隔字节
    body = sep.join("[%s] %s" % (ts, msg) for ts, msg in records)
    raw = (body + sep + manifest_text).encode("utf-8")
    return bytes(b ^ PL.XOR_KEY for b in raw)     # 存盘态 = 加密态


def test_xor_key_is_0xaa():
    """① XOR 0xAA 才行得通；换别的键解不出 `Patch Log Start`。

    ★ 注意：wrong=0x00 是【恒等变换】，传进去的正是密文，解码端 XOR 0xAA 后当然还原
      —— 那个 case 不算「错键」，测试里要排除，否则断言本身就是错的。
    """
    raw = _mk_log([("2026-09-29 20:30:36", "Patch Log Start")])
    assert PL.looks_like_log(raw)
    for wrong in (0xFA, 0xFF, 0x01, 0x55):
        bad = bytes(b ^ wrong for b in raw)
        assert not PL.looks_like_log(bad), "0x%02X 不该解出日志头" % wrong


def test_split_records_by_timestamp_not_newline():
    """② 按 `[时间]` 锚点切；分隔符是 0x00 不是 \\n。"""
    raw = _mk_log([("2026-09-29 20:30:36", "Patch Log Start"),
                   ("2026-09-29 20:31:00", "start download"),
                   ("2026-09-29 20:32:00", "skip 3")])
    text = PL.decode_bytes(raw).decode("utf-8", "replace")
    recs = PL.split_records(text)
    assert len(recs) == 3, recs
    assert recs[0][0] == "2026-09-29 20:30:36"
    assert "Patch Log Start" in recs[0][1]
    assert recs[2][1].startswith("skip")


def test_parse_manifest_python_repr_not_json():
    """③ 清单是单引号 dict repr ⇒ 能逐条解；一条坏不影响其余。"""
    man = ("{'res/ui/a.npk': {'hash': 'aa', 'doc': 123, 'fver': '20260929_172554_pc'}, "
           "{this is broken}, "
           "'bin/x64-2/x64.dll': {'hash': 'bb', 'size': 456}}")
    raw = _mk_log([("2026-09-29 20:30:36", "Patch Log Start")], man)
    text = PL.decode_bytes(raw).decode("utf-8", "replace")
    got = PL.parse_manifest(text)
    assert "res/ui/a.npk" in got
    assert got["res/ui/a.npk"]["doc"] == 123
    assert got["res/ui/a.npk"]["fver"] == "20260929_172554_pc"
    assert got["bin/x64-2/x64.dll"]["size"] == 456


def test_rel_variants_channel_suffix():
    """④ bin 目录带渠道后缀 a50 —— 不做映射会误报「缺文件」。"""
    v = PL.rel_variants("bin/x64-2/CCMsgSdk.x64.dll")
    assert "bin\\x64-2\\CCMsgSdk.x64.dll" in v
    assert "bin\\x64-a50-2\\CCMsgSdk.x64.dll" in v

    v2 = PL.rel_variants("bin/x64-win7/icudtl.dat")
    assert "bin\\x64-a50-win7\\icudtl.dat" in v2

    v3 = PL.rel_variants("bin/x64/lifeafter.exe")
    assert "bin\\x64-a50\\lifeafter.exe" in v3

    # 非 bin 路径不加变体
    v4 = PL.rel_variants("res/ui/a.npk")
    assert v4 == ["res\\ui\\a.npk"]


def test_fvers_distribution_is_version_source():
    """⑤ `fver` 分布 = 「版本推到哪一版」的唯一来源。"""
    man = ("{'res/ui/a.npk': {'fver': '20260929_172554_pc'}, "
           "'res/ui/b.npk': {'fver': '20260929_172554_pc'}, "
           "'res/ui/c.npk': {'fver': '20260928_163420_pc'}}")
    raw = _mk_log([("2026-09-29 20:30:36", "Patch Log Start")], man)
    rep = PL.summarize(PL.decode_bytes(raw).decode("utf-8", "replace"))
    assert rep["fvers"]["20260929_172554_pc"] == 2
    assert rep["fvers"]["20260928_163420_pc"] == 1
    assert rep["session_count"] == 1
    assert rep["manifest_entries"] == 3


def test_summarize_local_check_missing(tmp_path):
    """本地对照：文件在 → exists；不在 → missing（用合成的临时目录）。"""
    man = "{'res/ui/a.npk': {'doc': 10}}"
    raw = _mk_log([("2026-09-29 20:30:36", "Patch Log Start")], man)
    (tmp_path / "Documents").mkdir()
    rep = PL.summarize(PL.decode_bytes(raw).decode("utf-8", "replace"),
                       client_root=tmp_path)
    lc = rep["local_check"]
    assert lc["checked"] == 1
    assert lc["missing"] == 1

    # 放上文件再测一次（大小相同 → match）
    p = tmp_path / "res" / "ui" / "a.npk"
    p.parent.mkdir(parents=True)
    p.write_bytes(b"x" * 10)
    rep2 = PL.summarize(PL.decode_bytes(raw).decode("utf-8", "replace"),
                        client_root=tmp_path)
    lc2 = rep2["local_check"]
    assert lc2["missing"] == 0
    assert lc2["size_mismatch"] == 0


def test_render_md_has_sections():
    man = "{'res/ui/a.npk': {'doc': 10, 'fver': '20260929_172554_pc'}}"
    raw = _mk_log([("2026-09-29 20:30:36", "Patch Log Start")], man)
    rep = PL.summarize(PL.decode_bytes(raw).decode("utf-8", "replace"))
    md = PL.render_md(rep)
    assert "## 会话" in md
    assert "版本串" in md
    assert "20260929_172554_pc" in md


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v", "--no-header", "-q"]))
