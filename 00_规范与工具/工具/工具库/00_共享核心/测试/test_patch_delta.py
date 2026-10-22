# -*- coding: utf-8 -*-
"""热更增量取证 —— 防回归契约测试（2026-09-28）。

背景（为什么要这个测试）：
    版本清单里的文件表键名【会随版本漂移】，实测 5 个入口：
        release          files50 · files57 · files57_2
        playertest       files50 · files57 · files57_2
        playertest_bisai files50 · files56 · files56_2
        futuretest       files50 · files55 · files55_2
        playertest_kol_zy files50 · files55 · files55_2

    第一版 diff 硬编码 `files57_2`。release vs playertest 恰好都是 57，
    所以侥幸正确 —— 但 release vs futuretest 就会变成
    「一边 1745 条、一边 0 条」⇒ 静默产出「全部新增」这种错结论。

本测试锁住四件事：
    1. `_pick_file_keys` 能在键名漂移下挑出正确的两组
    2. `diff` 跨不同键名也能对上（不是硬编码）
    3. 取不到文件表时【明确抛错】，而不是静默返回空 diff
    4. `_family` 的家族归并（用于「哪个族有新东西」）
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pytest

from toolkit_core.patch_delta import _family, _pick_file_keys, diff


def _mk(version: str, main_key: str, ext_key: str, files: dict) -> dict:
    """造一份最小清单：真实结构是 files<NN> + files<NN>_2，NN 随版本漂移。"""
    return {
        "version": version,
        "_fetched": {"entry": version.split("_")[-1]},
        "files50": {"bin/a.dll": {"h": 1}},
        main_key: {k: {"hash64": v} for k, v in files.items()},
        ext_key: {k: {"hash64": v} for k, v in files.items()},
    }


# ── 1) 键名漂移
@pytest.mark.parametrize("nn", ["55", "56", "57"])
def test_pick_file_keys_follows_drift(nn):
    doc = _mk("v_%s" % nn, "files" + nn, "files%s_2" % nn, {"res/ui/a.npk": "1"})
    got = _pick_file_keys(doc)
    assert got["main"][0] == "files" + nn, "main 键应跟随漂移"
    assert got["ext"][0] == "files%s_2" % nn, "ext 键应跟随漂移"
    assert got["main"][1] == got["ext"][1]


def test_pick_file_keys_takes_highest_nn_when_multiple():
    """同时存在 files50 / files57 时，取 NN 更大的（50 是恒定的基础集）。"""
    doc = {"files50": {"bin/a.dll": {}}, "files57": {"res/x.npk": {}},
           "files57_2": {"res/x.npk": {}}}
    got = _pick_file_keys(doc)
    assert got["main"][0] == "files57"
    assert got["ext"][0] == "files57_2"


def test_pick_file_keys_missing_ext():
    doc = {"files57": {"res/x.npk": {}}}
    got = _pick_file_keys(doc)
    assert got["main"][0] == "files57"
    assert got["ext"] is None, "没有 _2 时应如实返回 None，不是瞎编"


# ── 2) 跨键名 diff（本测试的核心）
def test_diff_across_different_key_names():
    """release(files57) vs futuretest(files55) 必须能对上，不能一边 0 条。"""
    a = _mk("v57_release", "files57", "files57_2",
            {"res/ui/a.npk": "1", "res/ui/b.npk": "1", "bin/x.dll": "1"})
    b = _mk("v55_futuretest", "files55", "files55_2",
            {"res/ui/a.npk": "1", "res/ui/c.npk": "1", "bin/x.dll": "9"})
    rep = diff(a, b, keys="ext")
    assert rep["a"]["key"] == "files57_2"
    assert rep["b"]["key"] == "files55_2"
    assert rep["added"] == ["res/ui/c.npk"]
    assert rep["removed"] == ["res/ui/b.npk"]
    assert rep["changed"] == ["bin/x.dll"]
    assert rep["same"] == 1
    assert rep["totals"] == {"added": 1, "removed": 1, "changed": 1, "same": 1}


def test_diff_same_key_names_still_works():
    a = _mk("v57_release", "files57", "files57_2", {"res/ui/a.npk": "1"})
    b = _mk("v57_playertest", "files57", "files57_2", {"res/ui/a.npk": "2"})
    rep = diff(a, b, keys="ext")
    assert rep["changed"] == ["res/ui/a.npk"]
    assert rep["totals"]["added"] == 0


# ── 3) 取不到文件表要明确抛错
def test_diff_raises_when_no_file_table():
    """静默返回空 diff 是最危险的 —— 必须抛错。"""
    with pytest.raises(ValueError) as ei:
        diff({"version": "x"}, {"version": "y"}, keys="ext")
    assert "取不到 file 表" in str(ei.value)


def test_diff_raises_when_one_side_empty():
    a = _mk("v57", "files57", "files57_2", {"res/ui/a.npk": "1"})
    with pytest.raises(ValueError):
        diff(a, {"version": "no-files"}, keys="ext")


# ── 4) 家族归并
@pytest.mark.parametrize("path,want", [
    ("res/ui/huodong_icon.layers.1.257.npk", "res/ui/huodong_icon"),
    ("res/ui/shizhuang_icon.layers.1.1.npk", "res/ui/shizhuang_icon"),
    ("res/scene_bw.layers.256.257.npk", "res/scene_bw"),
    ("res/character/players2021/xxx.npk", "res/character/players2021"),
    ("bin/x64-3/a.dll", "bin/x64-3"),
])
def test_family(path, want):
    assert _family(path) == want


def test_family_aggregation_in_report():
    a = _mk("v57", "files57", "files57_2", {})
    b = _mk("v55", "files55", "files55_2", {
        "res/ui/huodong_icon.layers.1.257.npk": "1",
        "res/ui/huodong_icon.layers.1.1.npk": "1",
        "res/ui/shizhuang_icon.layers.1.1.npk": "1",
    })
    rep = diff(a, b, keys="ext")
    assert rep["added_by_family"]["res/ui/huodong_icon"] == 2
    assert rep["added_by_family"]["res/ui/shizhuang_icon"] == 1
