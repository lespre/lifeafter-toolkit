# -*- coding: utf-8 -*-
r"""散文件层 `pkg=255`（内容寻址散文件）的契约测试。

★ 回归背景（2026-09-30）：`batch_decrypt_wpk` 只按 `<family><pkg>.wpk` 找补丁层，
  而 `pkg=255` 是哨兵值 —— 该条目**不在任何 .wpk 里**，内容以客户端
  【内容寻址散文件】形式存在：`<res_dir>/<family>/<hash>`（文件名 = 条目 hash 32 位十六进制）。
  原实现拼出 `model255.wpk`、文件不存在 ⇒ `failed += 1; continue` ⇒
  实测 5,588 条里 **464 条（12%）被静默丢弃**（model 226 / character 157 / building 69）。

铁证：`res/building/5359e8fdb411e8c15b9f09689cf41928` 1,051,645 B
      == 条目 header_size 48 + payload_size 1,051,597（完全对上）。
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

PROJ = Path(r"E:\la拆包项目")
RES = Path(r"E:\mrzh\Documents\res")
DEC = PROJ / "01_工具/工具库/01_解码定位复原/容器格式/wpk_1dpw_decryptor.py"

need_client = pytest.mark.skipif(not RES.is_dir(), reason="体验服 res 目录不在")
need_mod = pytest.mark.skipif(not DEC.is_file(), reason="解密器不在")


def _mod():
    name = "_wpk_dec_for_test"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, DEC)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


@need_mod
def test_idx_里有pkg255条目且它们不在任何wpk里():
    m = _mod()
    idxt = RES / "building.idx"
    if not idxt.is_file():
        pytest.skip("building.idx 不在")
    ents = m.parse_idx(str(idxt))
    p255 = [e for e in ents if e.get("pkg") == 255]
    assert p255, "building.idx 里应当有 pkg=255 条目（内容寻址散文件）"
    # 反证：确实没有 building255.wpk 这个补丁层
    assert not (RES / "building255.wpk").exists(), \
        "若存在 building255.wpk，说明 pkg=255 语义变了，请复核本测试与解密器分支"


@need_client
@need_mod
def test_pkg255条目能从内容寻址文件解出(tmp_path):
    """★ 核心回归钉：pkg=255 必须走 `res/<family>/<hash>`，且不再被算作失败。"""
    m = _mod()
    ok, fail = m.batch_decrypt_wpk(str(RES), str(tmp_path), pkg_filter=[255], max_count=5)
    assert ok == 5, "pkg=255 应能解出（修前恒为 ok=0 / fail=5）"
    assert fail == 0, "不应再有 pkg=255 失败：%s" % fail
    outs = [p for p in tmp_path.iterdir() if p.is_file() and p.suffix != ".json"]
    assert len(outs) == 5 and all(p.stat().st_size > 0 for p in outs)
    man = tmp_path / "_manifest.json"
    assert man.is_file()
    import json
    recs = json.loads(man.read_text(encoding="utf-8"))
    assert len(recs) == 5
    assert all(r["entry"]["pkg"] == 255 for r in recs)
    # 落盘内容应与其内容寻址源文件「头 48 字节之后」一致（解码后再比 md5 可能不同，
    # 所以只钉 entry.hash == 源文件名，这是可复算的）
    for r in recs:
        src = RES / str(r["entry"]["family"]) / str(r["entry"]["hash"])
        assert src.is_file(), "内容寻址源文件必须存在：%s" % src
        assert src.stat().st_size == r["entry"]["header_size"] + r["entry"]["payload_size"]


@need_client
@need_mod
def test_全家族pkg255无静默丢失():
    """全家族 pkg=255：idx 声称多少条，就该解出多少条（0 失败）。"""
    m = _mod()
    idxs = sorted(RES.glob("*.idx"))
    if not idxs:
        pytest.skip("res 下没有 .idx")
    total = 0
    for idx in idxs:
        try:
            ents = m.parse_idx(str(idx))
        except Exception:                                           # noqa: BLE001
            continue
        total += sum(1 for e in ents if e.get("pkg") == 255)
    if total == 0:
        pytest.skip("没有 pkg=255 条目")
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        ok, fail = m.batch_decrypt_wpk(str(RES), td, pkg_filter=[255])
    assert ok == total, "pkg=255 解出 %d ≠ idx 声称 %d（有静默丢失）" % (ok, total)
    assert fail == 0, "仍有 %d 条失败" % fail
