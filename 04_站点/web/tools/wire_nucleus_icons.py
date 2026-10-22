# -*- coding: utf-8 -*-
"""给 nucleus 板每条接图标：icon_path → PE 定位 → 导出 PNG → 写 _media。"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(r"E:/la拆包项目")
WEB = ROOT / "04_站点/web"
FETCH = ROOT / "01_工具/工具库/01_解码定位复原/图集与取图"
OUT = WEB / "assets/nucleus_icons"
sys.path.insert(0, str(FETCH))
sys.path.insert(0, str(ROOT / "01_工具/工具库/00_共享核心"))

import pe_fetch as PE          # noqa: E402
import pc_fetch as PC          # noqa: E402

board_path = WEB / "data/boards/nucleus.json"
d = json.loads(board_path.read_text(encoding="utf-8"))
OUT.mkdir(parents=True, exist_ok=True)

hit = miss = 0
misses = []
for it in d["items"]:
    icon = (it.get("icon") or "").strip()
    if not icon:
        misses.append(it["id"])
        continue
    base = icon.rsplit(".", 1)[0]
    dst = OUT / (it["id"] + ".png")
    ok = dst.is_file()
    if not ok:
        try:
            ok = PE.export(base, dst) or PC.export(base, dst)
        except Exception:
            ok = False
    if ok:
        it["image_path"] = icon
        it["_media"] = {"images": [{"png": "assets/nucleus_icons/%s.png" % it["id"], "label": "图标"}],
                        "total": 1}
        hit += 1
    else:
        miss += 1
        misses.append(it["id"])

board_path.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
(WEB / "data/boards/nucleus.js").write_text("window.WIKI_BOARD_nucleus = " + json.dumps(d, ensure_ascii=False) + ";\n",
                                            encoding="utf-8")
print("图标命中 %d ｜ 缺 %d ｜ 例 %s" % (hit, miss, misses[:5]))
