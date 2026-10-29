# -*- coding: utf-8 -*-
"""补齐 mvp_06 图标：ui/shangcheng_icon/jingshi/icon_mvp06.ktx（0000.gpk row 12735）已导出。"""
from __future__ import annotations
import sys

import json
import pathlib
import shutil

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

ROOT = pathlib.Path(PROJ)
WEB = ROOT / "02_wiki/web"
SRC = pathlib.Path("C:/Users/Administrator/AppData/Local/hermes/cache/scratch/mvp06b/icon_mvp06.png")
DST = WEB / "assets/kill_broadcast/mvp_bq_mvp_06_icon.png"
BOARD = WEB / "data/boards/kill_broadcast.json"


def main() -> int:
    if not SRC.is_file():
        raise SystemExit("缺源图")
    shutil.copyfile(SRC, DST)
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    it = next(x for x in d["items"] if x["id"] == "mvp_bq_mvp_06")
    imgs = it.setdefault("_media", {}).setdefault("images", [])
    imgs = [x for x in imgs if x.get("label") != "图标"]
    imgs.append({"png": "assets/kill_broadcast/" + DST.name,
                 "base": "icon_mvp06", "label": "图标", "size": [300, 150],
                 "source": "PE 0000.gpk row 12735 · ui/shangcheng_icon/jingshi/icon_mvp06.ktx"})
    it["_media"]["images"] = imgs
    it["_media"]["total"] = len(imgs)
    it.pop("icon_state", None)
    it["icon_note"] = "图标已补齐：0000.gpk row 12735（.ktx 300×150）。"
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("mvp_06 图像", [x.get("label") for x in imgs])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
