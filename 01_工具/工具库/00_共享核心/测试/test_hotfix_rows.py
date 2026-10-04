# -*- coding: utf-8 -*-
r"""契约测试：行级热更 diff（toolkit_core/hotfix_rows.py）。

★ 这些断言钉的是【血泪教训】，不是实现细节：
  1) 值是 tuple 不是 list —— is_jump 只判 list 会全漏，得出「1 万行都在变」
  2) 不比 start/schema/bitmap（偏移元数据，热更后必变）
  3) 不比 jump: 引用（行号漂移，不是内容变更）
  ⇒ 三者任一破，时装热更表就会给出「1 万+ 假变更」的错结论。
"""
import sys
from pathlib import Path

import pytest

PROJ = Path(r"E:/la拆包项目")
CORE = PROJ / "01_工具/工具库/00_共享核心"
sys.path.insert(0, str(CORE))

from toolkit_core import hotfix_rows as HR   # noqa: E402


# ── ① is_jump：必须同时认 tuple 与 list ─────────────────
@pytest.mark.parametrize("v,expect", [
    (("0x0b", "jump:77562"), True),      # ★ decode 出来的真实形态 = tuple
    (["0x0b", "jump:77562"], True),      # JSON 往返后 = list
    (("0x05", "极地朋克"), False),
    (("0x01", 400), False),
    ("plain", False),
    (None, False),
    (("0x0b", "jump:1"), True),
])
def test_is_jump_认_tuple与list(v, expect):
    assert HR.is_jump(v) is expect, "★ 只判 list 会让整个判据失效（实测踩过）"


# ── ② plain_values：jump 字段被剔掉，真值留下 ─────────────
def test_plain_values_剔jump留真值():
    row = {"values": {
        "name": ("0x05", "极地朋克"),
        "icons": ("0x0b", "jump:84444"),
        "appear_ids": ("0x0b", "jump:84451"),
        "model_id": ("0x01", 3002),
    }}
    p = HR.plain_values(row)
    assert "name" in p and "model_id" in p
    assert "icons" not in p and "appear_ids" not in p


def test_plain_values_空行不炸():
    assert HR.plain_values({}) == {}
    assert HR.plain_values({"values": None}) == {}


# ── ③ cell：剥类型壳 ─────────────────────────────────────
@pytest.mark.parametrize("v,expect", [
    (("0x05", "极地朋克"), "极地朋克"),
    (("0x01", 3002), 3002),
    (("0x0b", "jump:1"), "jump:1"),
    (None, None),
])
def test_cell_剥壳(v, expect):
    assert HR.cell({"values": {"f": v}}, "f") == expect
    assert HR.cell({}, "f") is None


# ── ④ diff_rows：只有真值变才算变更 ──────────────────────
def _row(key, **vals):
    v = {k: (("0x05", x) if isinstance(x, str) else ("0x01", x)) for k, x in vals.items()}
    return {"key": key, "start": 100, "schema": 1, "values": v}


def test_只有jump漂移不算变更():
    """★ 核心断言：行号漂移不是内容变更。"""
    a = {1: _row(1, name="极地朋克", icons="jump:77555")}
    b = {1: _row(1, name="极地朋克", icons="jump:84444")}
    r = HR.diff_rows(a, b)
    assert r["计数"] == {"新增": 0, "移除": 0, "变更": 0}, \
        "★ jump 漂移被当成了变更 —— 会给出上万个假变更"


def test_偏移元数据变化不算变更():
    """★ start/schema 变了也不算 —— 热更后整块挪位必然变。"""
    a = {1: _row(1, name="极地朋克")}
    b = {1: _row(1, name="极地朋克")}
    b[1]["start"] = 999999
    b[1]["schema"] = 4179
    r = HR.diff_rows(a, b)
    assert r["计数"]["变更"] == 0


def test_真值变了要算变更():
    a = {1: _row(1, name="旧名", model_id=1)}
    b = {1: _row(1, name="新名", model_id=1)}
    r = HR.diff_rows(a, b)
    assert r["计数"]["变更"] == 1
    assert r["变更"][0]["name"] == "新名"
    assert "name" in r["变更"][0]["字段"]


def test_新增移除要算清():
    a = {1: _row(1, name="A")}
    b = {1: _row(1, name="A"), 2: _row(2, name="B")}
    r = HR.diff_rows(a, b)
    assert r["计数"] == {"新增": 1, "移除": 0, "变更": 0}
    assert r["新增"][0]["row_key"] == 2
    r2 = HR.diff_rows(b, a)
    assert r2["计数"] == {"新增": 0, "移除": 1, "变更": 0}
    assert r2["移除"][0]["row_key"] == 2


# ── ⑤ render_md：口径必须写在文件里 ─────────────────────
def test_render_md_写明口径():
    a = {1: _row(1, name="A")}
    b = {1: _row(1, name="B")}
    md = HR.render_md({"t_chs.py": HR.diff_rows(a, b)}, "标题")
    assert "jump" in md, "★ 口径没写进交付物 —— 读者会以为 1 万行都变了"
    assert "新增" in md and "移除" in md and "变更" in md


def test_render_md_错误表不炸():
    md = HR.render_md({"t_chs.py": {"错误": "缺 pre 版本"}})
    assert "缺 pre 版本" in md


# ── ⑥ 真实产物契约（有 pre/post 包时才跑）─────────────────
PRE = PROJ / "02_资料/源包/pre_update_20260924_1600/raw/script.py314.lc.npk"
POST = PROJ / "02_资料/源包/post_update_20260924_1610/raw/script.py314.lc.npk"


@pytest.mark.skipif(not (PRE.is_file() and POST.is_file()),
                    reason="缺 pre/post script 包")
def test_真实包_时装族数字可复现():
    """★ 端到端钉数字：重跑必须得到同一组数（防判据被改坏）。"""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_tcli_probe", str(CORE / "命令行" / "toolkit_cli.py"))
    tcli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tcli)
    try:
        names = tcli._load_names_map(None)
    except Exception as exc:                                       # noqa: BLE001
        pytest.skip("名字字典不可用：%s" % exc)
    rep = HR.diff_npk(PRE, POST, ["fashion_data_chs.py", "player_appear_data_chs.py"],
                      names, quiet=True)
    f = rep["fashion_data_chs.py"]["计数"]
    p = rep["player_appear_data_chs.py"]["计数"]
    assert f == {"新增": 87, "移除": 2, "变更": 0}, f
    assert p == {"新增": 44, "移除": 6, "变更": 2}, p
