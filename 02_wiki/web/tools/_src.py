# -*- coding: utf-8 -*-
r"""还原树取值优先级：新 PE 树 → 旧 PE 树 → PC 树。

用法：
    from _src import cdata_dir, table_path, open_table_bytes
    CD = cdata_dir()                 # 默认（无子目录）
    OV = cdata_dir("oversea")        # 服型变体目录
    p  = table_path("fashion_data")  # 按表名找 .py（优先 PE）
"""
from __future__ import annotations

import pathlib

PROJ = pathlib.Path(r"E:/la拆包项目")
import os

# 表根优先级：
#   1) LA_CDATA_ROOT 环境变量（显式指定，测试/临时用）
#   2) profiles.yml 的 source: pe|pc|documents
#   3) 默认 PE → Documents 依次回落
_ENV_ROOT = os.environ.get("LA_CDATA_ROOT")


def _source_root() -> pathlib.Path | None:
    name = os.environ.get("LA_SOURCE")
    if not name:
        try:
            import yaml
            cfg = yaml.safe_load((PROJ / "profiles.yml").read_text(encoding="utf-8")) or {}
            name = cfg.get("source")
        except Exception:
            name = None
    if not name:
        return None
    try:
        import yaml
        cfg = yaml.safe_load((PROJ / "profiles.yml").read_text(encoding="utf-8")) or {}
        rel = ((cfg.get("sources") or {}).get(name) or {}).get("cdata")
        if rel:
            return PROJ / rel
    except Exception:
        return None
    return None


_SRC_ROOT = _source_root()
ROOTS = ([pathlib.Path(_ENV_ROOT)] if _ENV_ROOT else []) + ([_SRC_ROOT] if _SRC_ROOT else []) + [
    PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata",   # 基线+增量合成树（优先）
    PROJ / "01_索引与产物/41_还原树/pe/配置_增量快照/com/cdata",
    PROJ / "01_索引与产物/41_还原树/Documents/script.py314.lc.npk/com/cdata",
]


def cdata_dir(*parts: str) -> pathlib.Path:
    for root in ROOTS:
        p = root.joinpath(*parts)
        if p.is_dir():
            return p
    return ROOTS[-1].joinpath(*parts)


def table_path(stem: str, *parts: str) -> pathlib.Path:
    for root in ROOTS:
        p = root.joinpath(*parts, stem + ".py")
        if p.is_file():
            return p
    return ROOTS[-1].joinpath(*parts, stem + ".py")
