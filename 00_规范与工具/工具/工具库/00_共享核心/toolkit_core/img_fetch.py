# -*- coding: utf-8 -*-
"""统一的 2D 取图入口：PE(.ktx) 优先，未命中自动回落 PC(.bc7)。

用法：
    from img_fetch import export
    ok = export("ui/item_icon/icon_410001", out_png)

设计：
  · PE 与 PC 用同一套 murmur3 fid，逻辑路径一致，只是载荷格式不同（ktx / bc7+DDS）
  · 先 PE 再 PC，命中即返回；两边都未命中返回 False（调用方决定记不记缺失）
  · 结果 PNG 已转真 PNG（浏览器可直读），不是把 DDS 改名
"""
from __future__ import annotations

import sys
import pathlib

_HERE = pathlib.Path(__file__).resolve()
_PROJ = next((u for u in _HERE.parents if (u / "00_规范与工具").is_dir()), _HERE.parents[4])
_FETCH = _PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"
_CORE = _PROJ / "00_规范与工具/工具/工具库/00_共享核心"
for p in (str(_CORE), str(_FETCH)):
    if p not in sys.path:
        sys.path.insert(0, p)

_pe = None
_pc = None


def _mods():
    global _pe, _pc
    if _pe is None:
        import pe_fetch as PE
        import pc_fetch as PC
        _pe, _pc = PE, PC
    return _pe, _pc


def export(base: str, out: pathlib.Path) -> str:
    """导出到 out，返回命中的源（'pe' / 'pc' / ''）。"""
    PE, PC = _mods()
    out = pathlib.Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    for name, mod in (("pe", PE), ("pc", PC)):
        try:
            if mod.export(base, out):
                return name
        except Exception:
            continue
    return ""


def exists(base: str) -> bool:
    PE, PC = _mods()
    for mod in (PE, PC):
        try:
            if mod.resolve(base):
                return True
        except Exception:
            continue
    return False
