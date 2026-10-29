# -*- coding: utf-8 -*-
"""在 182 个 PE 包里按名字直扫（绕过索引），确认某个 icon 到底在不在包里。"""
import sys
import pathlib


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
import pe_fetch as PE  # noqa: E402
AG = PE.AG

PACKS = PROJ / "01_索引与产物/源包/pe_gres_android"
needles = sys.argv[1:] or ["icon_366420_1", "icon_366050_1"]
hits = []
for pk in sorted(PACKS.glob("*.gpk")):
    try:
        for e in AG.iter_entries(str(pk)):
            nm = getattr(e, "name", None) or (e[0] if isinstance(e, tuple) else "")
            if any(n in str(nm) for n in needles):
                hits.append((pk.name, nm))
    except Exception as ex:  # noqa: BLE001
        print("跳过", pk.name, repr(ex)[:60])
print("命中", len(hits))
for h in hits[:20]:
    print(" ", h)
