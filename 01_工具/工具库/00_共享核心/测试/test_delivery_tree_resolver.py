# -*- coding: utf-8 -*-
r"""契约测试：交付链上「行 → 文件」必须走【树优先】定位器，且 0 命中不许静默。

## 为什么钉这个

2026-10-17 一次热更交付里，同**一类**退化在同一个 bundle 上躺了四处，症状全是
「跑完了、有产物、但数字是 0」：

```
① content_index.build()   → indexed 0          （候选哈希 0 个）
② CLI 帧哈希比对          → 候选哈希 0 个       （142,664 帧只定位 430）
③ hotfix_bundle 交付物化  → 91,049 条「产物缺失」（02_媒体文件 恒 0）
④ CLI _artifact_locator() → locate/tables 等命令假阴性
```

根因一处：`artifact_locator.Locator` 只会按「初拆载荷的 `<容器stem>/<8位行号>.<ext>` 铺法」
找文件；载荷删掉 / 换成还原树之后它**对每一行都返回 None 且不报错**。
正解是 `UnifiedResolver`（树优先、提取兜底）或 `TreeResolver`。

所以这里钉三件事：
  1. TreeResolver 能从 row_path_map + 还原树里拿到文件（正面能力）；
  2. content_index 走注入的定位器，且 **0 命中必须带 warning**（反静默）；
  3. `hotfix_bundle` 与 `toolkit_cli` 的源码 AST 里**不许再出现 `AL.Locator(...)`**（防回归）。
"""
from __future__ import annotations

import ast
import sqlite3
from pathlib import Path

import pytest

from toolkit_core import artifact_locator as AL
from toolkit_core import content_index as CI

CORE = Path(__file__).resolve().parents[1]
DELIVERY_CHAIN = [CORE / "toolkit_core" / "hotfix_bundle.py",
                  CORE / "命令行" / "toolkit_cli.py"]

CONT = r"Documents\gres\0007.gpk"
REL = r"Documents\gres\0007.gpk\_未命名\00000042.vkpl"
BODY = b"VKPL\x01\x00\x00\x00\x01\x00\x00\x00" + b"\x00" * 20


def _make_tree(tmp: Path) -> Path:
    tree = tmp / "41_还原树"
    f = tree / REL.replace("\\", "/")
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_bytes(BODY)
    return tree


def _make_rowmap(tmp: Path, tree: Path, rows) -> Path:
    """rows = [(容器, 行号, 树内相对路径)]；建 sidecar 表（in_tree=1）。"""
    db = tmp / "row_path_map.db"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE rows (container TEXT NOT NULL, row_index INTEGER NOT NULL, "
                "fid_hex TEXT, path TEXT, in_tree INTEGER, PRIMARY KEY (container, row_index))")
    con.executemany("INSERT INTO rows VALUES (?,?,?,?,1)",
                    [(c, r, None, p) for c, r, p in rows])
    con.commit()
    con.close()
    return db


def _make_index_db(tmp: Path, rows) -> Path:
    """最小主索引库：content_index 只读 entries 的 (container,row_index,decoded)。"""
    db = tmp / "lifeafter_files.sqlite3"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE entries (container TEXT, row_index INTEGER, fid_hex TEXT, "
                "kind TEXT, offset INTEGER, payload_offset INTEGER, packed INTEGER, "
                "decoded INTEGER, flag INTEGER)")
    con.executemany("INSERT INTO entries (container,row_index,decoded) VALUES (?,?,?)", rows)
    con.commit()
    con.close()
    return db


def test_tree_resolver_reads_file_from_tree(tmp_path):
    """正面能力：row_path_map + 还原树 → 真文件（这条过了才谈得上修别的）。"""
    tree = _make_tree(tmp_path)
    db = _make_rowmap(tmp_path, tree, [(CONT, 42, REL)])
    tr = AL.TreeResolver(tree, db)
    assert tr.available is True
    p = tr.path(CONT, 42)
    assert p is not None and p.is_file() and p.read_bytes() == BODY
    assert tr.path(CONT, 43) is None          # 不存在的行照实返回 None
    print("TreeResolver.stats:", tr.stats())


def test_content_index_resolves_from_tree(tmp_path):
    """content_index 必须用注入的【树】定位器把行算出来（老 Locator 在这里恒 0）。"""
    tree = _make_tree(tmp_path)
    db = _make_rowmap(tmp_path, tree, [(CONT, 42, REL)])
    idx = _make_index_db(tmp_path, [(CONT, 42, 6), (CONT, 43, 99)])
    rep = CI.build(idx, tmp_path / "不存在的载荷根", [CONT],
                   resolver=AL.UnifiedResolver(tree, db=db), quiet=True)
    assert rep["todo"] == 2
    assert rep["indexed"] == 1, "树里那行必须被算到（行 43 树里没有，照实 0）"
    assert rep["resolver"] == "UnifiedResolver"


def test_content_index_zero_hit_is_not_silent(tmp_path):
    """反静默：一行都定位不到时必须给 warning —— 这不是「本次没有内容」。"""
    idx = _make_index_db(tmp_path, [(CONT, 42, 6)])
    empty = tmp_path / "没有任何产物的根"
    rep = CI.build(idx, empty, [CONT], resolver=AL.UnifiedResolver(empty), quiet=True)
    assert rep["indexed"] == 0
    assert rep.get("warning"), "0 命中不给 warning 就是本类事故的温床"


def test_content_index_default_resolver_is_tree_first(tmp_path, monkeypatch):
    """不给 resolver 时的默认值也必须是树优先（不能退回只查载荷）。"""
    tree = _make_tree(tmp_path)
    db = _make_rowmap(tmp_path, tree, [(CONT, 42, REL)])
    idx = _make_index_db(tmp_path, [(CONT, 42, 6)])
    monkeypatch.setattr(AL, "default_tree_root", lambda: tree)
    monkeypatch.setattr(AL, "row_path_map_db", lambda: db)
    rep = CI.build(idx, tmp_path / "不存在的载荷根", [CONT], quiet=True)
    assert rep["indexed"] == 1, "默认定位器没走还原树"


def test_bundle_locator_is_tree_first(tmp_path):
    """交付物化用的定位器必须是 UnifiedResolver。"""
    from toolkit_core import hotfix_bundle as HB
    b = HB.Bundle(tmp_path / "out")
    loc = b.locator()
    assert isinstance(loc, AL.UnifiedResolver), type(loc)


def test_cli_artifact_locator_is_tree_first():
    """locate / tables copies 等命令共用的 `_artifact_locator()` 也必须是树优先。"""
    import toolkit_cli
    loc = toolkit_cli._artifact_locator()
    assert isinstance(loc, AL.UnifiedResolver), type(loc)


@pytest.mark.parametrize("path", DELIVERY_CHAIN, ids=lambda p: p.name)
def test_delivery_chain_has_no_extract_only_locator(path):
    """AST 级防回归：交付链源码里不许再 `AL.Locator(...)`。

    只禁 `AL.Locator`（初拆载荷专用）；`CP.Locator`（container_probe 自己的、已内置
    树优先）与注释/文档字符串不在管辖内 —— 所以扫 AST 而不是 grep 文本。
    """
    tree = ast.parse(path.read_text(encoding="utf-8"), str(path))
    bad = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr == "Locator":
            owner = node.func.value
            name = getattr(owner, "id", None) or getattr(owner, "attr", "")
            if name == "AL":
                bad.append(node.lineno)
    assert not bad, (
        "%s 第 %s 行还在用 AL.Locator()（只认初拆载荷铺法，树模式下恒 None）。"
        "行→文件一律 UnifiedResolver / TreeResolver。" % (path.name, bad))
