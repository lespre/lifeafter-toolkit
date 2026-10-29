# -*- coding: utf-8 -*-
"""把 assets/avatar_icons/<item_id>.png 挂到名片框板卡面（有图才挂）。"""
from __future__ import annotations
import sys

import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

ICONS = WEB / "assets/avatar_icons"


def main() -> int:
    if not ICONS.is_dir():
        print("图标目录不存在：", ICONS)
        return 1
    p = WEB / "data/boards/avatar_catalog.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    hit = 0
    for it in d["items"]:
        f = ICONS / ("%s.png" % it.get("item_id"))
        if not f.is_file():
            continue
        rel = "assets/avatar_icons/%s.png" % it.get("item_id")
        it["_media"] = {"images": [{"png": rel, "label": "图标"}], "total": 1}
        hit += 1
    d["meta"]["hide_media"] = hit == 0
    d["meta"]["notes"] = (d["meta"].get("notes", "") +
                          " ｜ 已挂图标 %d 条（UI 图集按路径提取）。" % hit).strip()
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/avatar_catalog.js").write_text(
        "window.WIKI_BOARD_avatar_catalog = %s;" % json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print("挂图", hit, "/", len(d["items"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
