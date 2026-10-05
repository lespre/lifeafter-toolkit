# -*- coding: utf-8 -*-
r"""产物定位器的契约测试（含 stem 撞车的回归）。

★ 回归背景：容器 `script.py314.lc.npk` 与 `Documents\script.py314.lc.npk`
   「取文件名去扩展名」后折成同一个 stem，而实际产物目录是两个不同的
   （`script.py314.lc` 与 `Documents__script.py314.lc`）。
   旧实现直接用 stem 当目录名 ⇒ `Documents\...` 的行会被定位到另一个容器的产物，
   读到内容完全不同的文件（实测过：同名行读到 26 B 的垃圾 vs 2,558 B 的真 marshal）。

★ 性能纪律：**不要在测试里列真实的大目录**（`gres\0000.gpk` 有 54,292 个文件，
  列一次要几十秒，整套 pytest 会被拖到超时）。重活部分用合成小目录验。
"""
import sqlite3
import sys
from pathlib import Path

import pytest

CORE = Path(__file__).resolve().parents[1]
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from toolkit_core import artifact_locator as AL  # noqa: E402

def _real_root():
    """★ 2026-09-29（S5）：真实产物根改为【智能选】——载荷在就用载荷，已清则用还原树。

    老写法写死 `20_提取/.../files`；载荷被架构改造清掉后，`need_real` 会静默 skip，
    悄悄丢掉覆盖。
    """
    try:
        return AL.default_product_root()
    except Exception:
        return Path(r"E:/la拆包项目/03_执行/41_还原树")


REAL_ROOT = _real_root()
DB = Path(r"E:/la拆包项目/03_执行/10_索引/indexes/lifeafter_files.sqlite3")

need_real = pytest.mark.skipif(not REAL_ROOT.is_dir(), reason="产物根不存在")


@pytest.fixture
def fake_root(tmp_path):
    """造出真实世界里那组撞车目录 + 一个普通目录。"""
    a = tmp_path / "script.py314.lc"
    b = tmp_path / "Documents__script.py314.lc"
    c = tmp_path / "0000"
    for d, payload in ((a, b"AAAA"), (b, b"BBBB"), (c, b"CCCC")):
        d.mkdir(parents=True)
        (d / "00000001.bin").write_bytes(payload)
        (d / "00000002.bin").write_bytes(payload + b"1")
    return tmp_path


# ── 纯逻辑（不碰磁盘） ─────────────────────────────────────
def test_stem_of_只做取文件名():
    assert AL.Locator.stem_of(r"gres\0000.gpk") == "0000"
    assert AL.Locator.stem_of("script.py314.lc.npk") == "script.py314.lc"
    assert AL.Locator.stem_of(r"res\ui_02.gpk") == "ui_02"


def test_stem_of_对两个script容器会撞车_这是已知事实():
    """★ 记录事实：stem_of 不是目录名，两个 script 容器会折成同一个值。"""
    a = AL.Locator.stem_of("script.py314.lc.npk")
    b = AL.Locator.stem_of(r"Documents\script.py314.lc.npk")
    assert a == b, "若这个断言失败，说明 stem_of 语义变了，请复核 dir_of 的消解逻辑"


# ── 合成目录上的行为 ─────────────────────────────────────
def test_dir_of_消解script撞车(fake_root):
    loc = AL.Locator(fake_root)
    d1 = loc.dir_of("script.py314.lc.npk")
    d2 = loc.dir_of(r"Documents\script.py314.lc.npk")
    assert d1 != d2, "两个 script 容器必须映射到不同目录（回归点）"
    assert d1.name == "script.py314.lc"
    assert d2.name == "Documents__script.py314.lc"


def test_dir_of_普通容器退回stem(fake_root):
    loc = AL.Locator(fake_root)
    assert loc.dir_of(r"gres\0000.gpk").name == "0000"


def test_撞车的两个容器读到不同文件(fake_root):
    """★ 核心回归：同一行号必须解析到【不同】文件。"""
    loc = AL.Locator(fake_root)
    p1 = loc.path("script.py314.lc.npk", 1)
    p2 = loc.path(r"Documents\script.py314.lc.npk", 1)
    assert p1 is not None and p2 is not None
    assert p1 != p2
    assert p1.read_bytes() == b"AAAA"
    assert p2.read_bytes() == b"BBBB"
    assert loc.path(r"gres\0000.gpk", 1).read_bytes() == b"CCCC"


def test_目录映射只建一次(fake_root):
    loc = AL.Locator(fake_root)
    m1 = loc.rows(r"gres\0000.gpk")
    m2 = loc.rows(r"gres\0000.gpk")
    assert m1 is m2, "同一容器重复取应命中缓存（目录只列一次）"


def test_selfcheck_在合成目录上通过(fake_root):
    loc = AL.Locator(fake_root)
    loc.rows(r"gres\0000.gpk")
    loc.rows("script.py314.lc.npk")
    r = loc.selfcheck()
    assert r["ok"], r.get("mismatch")
    assert r["checked"] > 0


def test_selfcheck_的key是完整路径不是stem(fake_root):
    """★ 回归：_maps 的 key 曾是 stem，改成完整路径后 selfcheck 必须跟着改。"""
    loc = AL.Locator(fake_root)
    loc.rows(r"gres\0000.gpk")
    key = next(iter(loc._maps))
    assert Path(key).is_absolute(), "_maps 的 key 应为目录完整路径"
    assert key == str(fake_root / "0000")


# ── 真实数据（★ 2026-09-30：载荷已删 ⇒ 目录名口径作废，改钉【树】）─────────
@need_real
def test_真实两个script容器解析到不同文件_树():
    """★ 2026-09-30（S5 执行完，初拆载荷已删）改口径。

    老断言钉的是**载荷目录名**（`script.py314.lc` / `Documents__script.py314.lc`）——
    而载荷是「可重建的中间态」，架构改造后已被清掉，目录名随之作废
    （`dir_name_of` 的判据是「规范化名**在产物根里存在**」，载荷一没就必然退回 stem）。

    重新钉【真意图】：两个同名 stem 的容器必须解析到**不同且都存在**的树文件。
    """
    tr = AL.TreeResolver()
    if not tr.available:
        pytest.skip("row_path_map / 还原树 不可用")
    p1 = tr.path("script.py314.lc.npk", 100)
    p2 = tr.path(r"Documents\script.py314.lc.npk", 100)
    assert p1 and p2, "两个容器都应能在树里解析到文件（载荷已不再参与）"
    assert p1 != p2, "两个同名 stem 的容器被折到同一个文件了（正是要防的缺陷）"
    assert p1.is_file() and p2.is_file()


@need_real
def test_真实全部容器在树里都能解析():
    """S1 sidecar（row_path_map）契约：60 个容器**每一个**都有行落在还原树里。

    老断言是 `loc.dir_of(c).is_dir()`（载荷目录存在性）；载荷删后恒假。
    新判据直接钉树：容器 → 行 → 树文件，且文件真的在。
    """
    if not DB.is_file():
        pytest.skip("索引库不存在")
    tr = AL.TreeResolver()
    if not tr.available:
        pytest.skip("row_path_map / 还原树 不可用")
    db = sqlite3.connect("file:%s?mode=ro" % DB.as_posix(), uri=True)
    try:
        conts = [c for (c,) in db.execute("SELECT DISTINCT container FROM entries")]
    finally:
        db.close()
    empty, broken = [], []
    for c in conts:
        rows = tr.rows(c)
        if not rows:
            empty.append(c)
            continue
        sample = list(rows.items())[:3]
        for _r, p in sample:
            if not Path(p).is_file():
                broken.append("%s r%s" % (c, _r))
                break
    assert not empty, "这些容器在树里一行都没有：%s" % empty[:5]
    assert not broken, "这些容器解析出的树文件不存在：%s" % broken[:5]
