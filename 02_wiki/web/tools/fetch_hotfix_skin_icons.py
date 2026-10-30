# -*- coding: utf-8 -*-
"""给热更新增的 3 款武器皮肤取 2D 图（PE icon_<id>_b）并挂到板上。"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
import pe_fetch  # noqa: E402

WEB = ROOT / "02_wiki/web"
OUT = WEB / "assets/skin_posters"
BOARD = WEB / "data/boards/weapon_skin_sfx_text_sources.json"
IDS = ["1110189", "1110194", "1110205"]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    got = {}
    for sid in IDS:
        dst = OUT / f"{sid}.png"
        if dst.is_file() and dst.stat().st_size > 1024:
            got[sid] = dst
            continue
        for cand in (f"ui/item_icon/icon_{sid}_b", f"ui/item_icon/icon_{sid}"):
            if pe_fetch.export(cand, dst):
                got[sid] = dst
                break
    print("取到图", len(got), sorted(got))

    d = json.loads(BOARD.read_text(encoding="utf-8"))
    n = 0
    for it in d["items"]:
        sid = str(it.get("id"))
        if sid in got:
            it["_media"] = {"images": [{"png": f"assets/skin_posters/{sid}.png",
                                        "label": "图示", "source": "PE · ui/item_icon"}], "total": 1}
            n += 1
    BOARD.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print("挂图卡", n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
