# -*- coding: utf-8 -*-
r"""还原树「对标客户端路径」重排 —— 映射表 + dry-run（Stage 1，不写盘）。

## 目标形态（用户 2026-09-30 定）

```
41_还原树/
  <容器相对路径 = 客户端 E:\mrzh 下的真实路径>/
      <包内逻辑路径>            ← 有名字
      _未命名/<8位行号>.<ext>    ← 没名字（保持原样，但收进包目录里）
  例：
    script.py314.lc.npk/com/cdata/weapon_skin_data.py
    Documents/script.py314.lc.npk/com/cdata/weapon_skin_data.py
    Documents/gres/0000.gpk/...
    res/ui_01.gpk/...
```

## 为什么（实测规模）

```
索引 60 个容器名 → E:\mrzh 下 60/60 全部存在（容器名 = 相对路径）
有名字的路径 1,014,624 ｜ ★跨容器重名 4,225（全是「补丁层 × 底座层」）
  Documents\script.py314.lc.npk × script.py314.lc.npk        3,234
  Documents\gres\0000.gpk      × res\*.gpk                    352+189+96+71+63…
⇒ 旧的「按名字压成一棵路径树」把这 4,225 处的层信息压丢了。
   收进容器目录后，撞名从根上消失，每条内容都能溯源到具体包。
"""
from __future__ import annotations

import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional

NAME = "tree_align"


def _paths():
    from toolkit_core import paths as P
    return P


def _dir_name_of(container: str) -> str:
    """容器名 → 现有 `_未命名` 目录名（复用 container_probe 的唯一实现）。"""
    try:
        from toolkit_core.container_probe import container_dir_name
        return container_dir_name(container)
    except Exception:                                               # noqa: BLE001
        s = str(container).replace("\\", "/")
        return s.split("/")[-1].rsplit(".", 1)[0]


def _row_map(src_dir: Path) -> Dict[int, str]:
    """目录里 `00012345.ext` → {行号: 文件名}（只列一次，不逐行 glob）。"""
    out: Dict[int, str] = {}
    if not src_dir.is_dir():
        return out
    try:
        with __import__("os").scandir(src_dir) as it:
            for e in it:
                if not e.is_file() or "." not in e.name:
                    continue
                stem = e.name.rsplit(".", 1)[0]
                if stem.isdigit():
                    out[int(stem)] = e.name
    except OSError:
        pass
    return out


def _ext_of(name: Optional[str], fallback: str = ".bin") -> str:
    if not name or "." not in name:
        return fallback
    return "." + name.rsplit(".", 1)[1]


def build_plan(containers: Optional[List[str]] = None) -> dict:
    """生成「现在在哪 → 迁到哪」的完整映射（只读）。

    返回 {rows, moves, missing, collisions, by_container, samples}
    """
    P = _paths()
    tree = Path(P.TREE_ROOT)
    rmap_db = Path(P.INDEX_ROOT) / "indexes" / "row_path_map.db"
    idx_db = Path(P.INDEX_ROOT) / "indexes" / "lifeafter_files.sqlite3"
    con = sqlite3.connect("file:%s?mode=ro" % idx_db.as_posix(), uri=True)
    conts = containers or [c for (c,) in
                           con.execute("SELECT DISTINCT container FROM entries ORDER BY container")]
    named_by_container: Dict[str, Dict[int, str]] = defaultdict(dict)
    all_rows: Dict[str, List[int]] = {}
    for c in conts:
        rows = [r for (r,) in con.execute(
            "SELECT row_index FROM entries WHERE container=? ORDER BY row_index", (c,))]
        all_rows[c] = rows
    con.close()
    if rmap_db.is_file():
        rc = sqlite3.connect("file:%s?mode=ro" % rmap_db.as_posix(), uri=True)
        undirs: Dict[str, str] = {}
        for cont, row, path in rc.execute(
                "SELECT container,row_index,path FROM rows WHERE in_tree=1"):
            if cont not in all_rows or not path:
                continue
            if path.startswith("_未命名"):
                # ★ 目录名【从数据里取】：老 path = `_未命名\<目录>\<文件>`
                if cont not in undirs:
                    parts = path.split("\\")
                    if len(parts) >= 3:
                        undirs[cont] = parts[1]
            else:
                named_by_container[cont][row] = path
        rc.close()
    else:
        undirs = {}

    moves: List[dict] = []
    missing = 0
    new_path_seen: Dict[str, int] = {}          # 新路径 → 出现次数（查撞名）
    per_cont = Counter()
    samples: List[dict] = []
    for c in conts:
        # ★ 绝不能用 `_dir_name_of()`（它在**产物根**里找目录，S5 后必然退回 stem，
        #   会让 `Documents\script.py314.lc.npk` 的无名行错指到底座容器 —— 2026-09-30 实测踩过）
        d = undirs.get(c) or _dir_name_of(c)
        undir = tree / "_未命名" / d
        have = _row_map(undir)
        for row in all_rows[c]:
            named = named_by_container[c].get(row)
            if named:
                cur = str(named)
                newrel = str(Path(c.replace("\\", "/")) / Path(named))
            else:
                fn = have.get(row)
                if fn is None:
                    missing += 1
                    continue
                cur = str(Path("_未命名") / d / fn)
                newrel = str(Path(c.replace("\\", "/")) / "_未命名" / fn)
            if not (tree / cur).is_file():
                missing += 1
                continue
            new_path_seen[newrel] = new_path_seen.get(newrel, 0) + 1
            per_cont[c] += 1
            moves.append({"container": c, "row": row, "cur": cur, "new": newrel})
            if len(samples) < 8:
                samples.append({"cur": cur, "new": newrel})
    coll = {k: v for k, v in new_path_seen.items() if v > 1}
    return {"rows": sum(len(v) for v in all_rows.values()), "moves": moves,
            "missing": missing, "collisions": coll,
            "by_container": {k: n for k, n in per_cont.most_common()},
            "new_paths": len(new_path_seen), "samples": samples}


def render_report(rep: dict, limit_cont: int = 12) -> str:
    L = []
    L.append("# 还原树对标客户端路径 —— 迁移映射 dry-run（%s）" % NAME)
    L.append("")
    L.append("| 项 | 数 |")
    L.append("|---|---|")
    L.append("| 索引条目（行） | %d |" % rep["rows"])
    L.append("| 可迁移（现有文件能找到） | %d |" % len(rep["moves"]))
    L.append("| 缺文件（树里没有） | %d |" % rep["missing"])
    L.append("| 新落点唯一路径数 | %d |" % rep["new_paths"])
    L.append("| ★ 新落点仍撞名 | %d |" % len(rep["collisions"]))
    L.append("")
    L.append("## 每个容器迁多少（前 %d）" % limit_cont)
    L.append("")
    for k, n in list(rep["by_container"].items())[:limit_cont]:
        L.append("- `%s` → %d" % (k, n))
    if rep["collisions"]:
        L.append("")
        L.append("## ⚠ 仍撞名的前 10 条")
        for k, v in list(rep["collisions"].items())[:10]:
            L.append("- %s ×%d" % (k, v))
    L.append("")
    L.append("## 映射样例")
    L.append("")
    for s in rep["samples"]:
        L.append("- `%s`\n  → `%s`" % (s["cur"], s["new"]))
    return "\n".join(L)
