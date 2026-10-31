# -*- coding: utf-8 -*-
"""在 pe_npk_full 的所有 npk 里按 fid 找特效贴图，命中即导出。"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"))
from la_unpack_core import NpkArchive  # noqa: E402

D = ROOT / "01_索引与产物/30_分析/sfx_1110189_联动_20261031"
PAT = re.compile(r"[A-Za-z0-9_\\/\.\-]+\.(?:tga|spr|dds|ktx)")
BS = chr(92)


def targets() -> dict[int, str]:
    out = {}
    for p in D.glob("*.sfx"):
        t = p.read_text(encoding="utf-8", errors="ignore")
        for m in PAT.finditer(t):
            name = m.group(0).replace("/", BS)
            short = pathlib.PureWindowsPath(name).name
            out.setdefault(short.lower(), name)
    return out


def main() -> int:
    tgt = targets()
    print("目标贴图（按文件名）", len(tgt))
    npks = sorted((ROOT / "01_索引与产物/源包/pe_npk_full").rglob("*.npk"))
    print("待扫 npk", len(npks))
    found: dict[str, tuple[str, int]] = {}
    for npk in npks:
        try:
            a = NpkArchive(str(npk))
        except Exception:                                  # noqa: BLE001
            continue
        ents = a._entries
        if not ents:
            continue
        for e in ents:
            pass
        # 直接用名字字典里的 fid 对照：这里没有名字，只能按 fid 比对
        for short, path in list(tgt.items()):
            if short in found:
                continue
        print("  %-52s entries %7d" % (npk.name, len(ents)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
