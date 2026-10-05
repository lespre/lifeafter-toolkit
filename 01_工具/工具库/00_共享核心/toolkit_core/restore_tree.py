# -*- coding: utf-8 -*-
r"""按【源路径】把拆包产物物化成目录树（还原文件夹与文件名）。

背景
----
容器里【不存文件名】，只存路径的 murmur3 哈希（fid）。因此「还原文件名」只有
一条路：把已知的 fid → 路径 映射（:mod:`names` / 字典）反查回去。能命名的就
按真实路径落盘，命不中的留在 `_未命名/` 下保留行号名。

用硬链接（``os.link``）而不是复制：同盘瞬时、不占额外空间、**原件一个字节都不动**。

产物目录名规则（实证）
----------------------
``取容器名的 basename 去扩展名``；同名冲突时前缀上一级目录并加 ``__``。
例：``res\ui_02.gpk`` → ``ui_02``；``Documents\script.py314.lc.npk`` → ``Documents__script.py314.lc``。

用法
----
::

    from toolkit_core import restore_tree
    stats = restore_tree.materialize(
        out_root=r"E:\la拆包项目\03_执行\41_还原树",
        containers=["res\\ui_02.gpk"],          # None = 全部 60 个
        link=True,                               # False 则复制
        include_unnamed=True,
    )
    print(stats)

CLI 对应：``toolkit_cli.py materialize``
"""

from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

from . import paths

__all__ = ["materialize", "MaterializeStats", "container_dir_name"]


@dataclass
class MaterializeStats:
    containers: int = 0
    rows: int = 0
    named: int = 0
    unnamed: int = 0
    missing: int = 0
    linked: int = 0
    errors: int = 0
    per_container: dict[str, int] = field(default_factory=dict)

    def __str__(self) -> str:
        return (
            "容器 %d · 索引行 %d → 已命名 %d · 未命名 %d · 缺产物 %d\n"
            "  建立链接 %d · 失败 %d"
            % (self.containers, self.rows, self.named, self.unnamed,
               self.missing, self.linked, self.errors)
        )


def container_dir_name(container: str) -> str:
    r"""容器名 → 产物目录名。

    规则：取 basename 去扩展名；同名冲突时前缀上级目录 + ``__``。
    ``res\ui_02.gpk`` → ``ui_02`` · ``Documents\script.py314.lc.npk`` → ``Documents__script.py314.lc``
    """
    c = container.replace("/", "\\")
    parts = [p for p in c.split("\\") if p]
    base = parts[-1]
    stem = base.rsplit(".", 1)[0] if "." in base else base
    # 冲突处理：script.py314.lc.npk 在两个目录下各有一个 ⇒ 按约定加前缀
    if stem == "script.py314.lc" and len(parts) >= 2:
        return "%s__%s" % (parts[-2], stem)
    return stem


def _row_map(src_dir: Path) -> dict[int, str]:
    """扫一个产物目录，建【行号 → 文件绝对路径】映射（文件名形如 00008484.dds）。"""
    out: dict[int, str] = {}
    if not src_dir.is_dir():
        return out
    with os.scandir(src_dir) as it:
        for e in it:
            if not e.is_file():
                continue
            nm = e.name
            if "." not in nm:
                continue
            stem = nm.rsplit(".", 1)[0]
            if stem.isdigit():
                out[int(stem)] = e.path
    return out


def materialize(
    out_root: str | os.PathLike,
    db_path: Optional[str | os.PathLike] = None,
    names_dict: Optional[str | os.PathLike] = None,
    src_root: Optional[str | os.PathLike] = None,
    containers: Optional[Iterable[str]] = None,
    link: bool = True,
    include_unnamed: bool = True,
) -> MaterializeStats:
    """把产物按源路径物化成目录树。

    :param out_root:   输出根目录（还原树落这里）
    :param db_path:    索引库；默认用 :mod:`paths` 的约定位置
    :param names_dict: 名字字典 json；默认用 :mod:`paths` 的约定位置
    :param src_root:   产物根（含各容器目录）；默认 ``files/``
    :param containers: 只处理这些容器；None = 全部
    :param link:       True 用硬链接（省空间），False 复制
    :param include_unnamed: 是否把未命名条目也放到 ``_未命名/``
    """
    import json

    out_root = Path(out_root)
    db_path = Path(db_path) if db_path else (Path(paths.INDEX_ROOT) / "indexes"
                                             / "lifeafter_files.sqlite3")
    src_root = Path(src_root) if src_root else (Path(paths.DEFAULT_OUTPUT_ROOT)
                                                 / "全量实测_20260926" / "files")
    if names_dict:
        nd = Path(names_dict)
    else:
        # 字典按版本回退：v6 → v5 → v3 → 默认名
        cands = [Path(paths.NAMES_ROOT) / n for n in
                 ("names_dict_v6.json", "names_dict_v5.json",
                  "names_dict_v3.json", "names_dict.json")]
        nd = next((c for c in cands if c.is_file()), cands[-1])

    names = json.loads(Path(nd).read_text(encoding="utf-8"))
    db = sqlite3.connect(str(db_path))
    st = MaterializeStats()

    conts = list(containers) if containers else [
        c for (c,) in db.execute("SELECT DISTINCT container FROM entries ORDER BY container")
    ]
    for cont in conts:
        st.containers += 1
        src_dir = src_root / container_dir_name(cont)
        row2file = _row_map(src_dir)
        rows = db.execute(
            "SELECT row_index,fid_hex FROM entries WHERE container=? ORDER BY row_index",
            (cont,)).fetchall()
        st.rows += len(rows)
        c_named = c_unnamed = c_missing = 0
        made: set[str] = set()          # 已建过的目录，避免每行都 mkdir+exists
        for row, fid in rows:
            hit = row2file.get(row)
            if hit is None:
                st.missing += 1
                c_missing += 1
                continue
            p = names.get(fid)
            # ★ 2026-09-30 用户定：对标 E:\mrzh 层级 —— 每一条都落进【它所在容器】的目录下，
            #   这样同名表的多层副本（底座 / Documents overlay）各占各的路径，不再互相覆盖。
            cont_dir = cont.replace("/", os.sep).replace("\\", os.sep)
            if p:
                dst = out_root / cont_dir / p.replace("/", os.sep).replace("\\", os.sep)
                st.named += 1
                c_named += 1
            elif include_unnamed:
                dst = out_root / cont_dir / "_未命名" / Path(hit).name
                st.unnamed += 1
                c_unnamed += 1
            else:
                continue
            d = str(dst.parent)
            try:
                if d not in made:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    made.add(d)
                if not dst.exists():
                    if link:
                        os.link(hit, dst)
                    else:
                        import shutil
                        shutil.copy2(hit, dst)
                    st.linked += 1
            except OSError:
                st.errors += 1
        st.per_container[cont] = c_named
    return st
