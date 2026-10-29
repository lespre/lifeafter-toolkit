# -*- coding: utf-8 -*-
"""补齐 mvp_bq_mvp_06（沙海月鸣）的男款主视觉，并如实标注图标未进包。"""
from __future__ import annotations

import json
import pathlib
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

ROOT = pathlib.Path(PROJ)
WEB = ROOT / "02_wiki/web"
BOARD = WEB / "data/boards/kill_broadcast.json"
SRC = pathlib.Path("C:/Users/Administrator/AppData/Local/hermes/cache/scratch/mvp06/mvp06_nan.png")
DST = WEB / "assets/kill_broadcast/mvp_bq_mvp_06_cover_nan.png"


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    it = next(x for x in d["items"] if x["id"] == "mvp_bq_mvp_06")
    imgs = it.setdefault("_media", {}).setdefault("images", [])
    if not any(x.get("label") == "主视觉（男）" for x in imgs):
        if SRC.is_file():
            DST.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SRC, DST)
            imgs.append({"png": "assets/kill_broadcast/" + DST.name,
                         "base": "mvp06_nan", "label": "主视觉（男）",
                         "size": [572, 324], "source": "PE · ui/mvpvedio/vediocover/mvp06_nan"})
    it["_media"]["images"] = imgs
    it["_media"]["total"] = len(imgs)
    it["icon_state"] = "图标未进包"
    it["icon_note"] = ("ui/shangcheng_icon/jingshi/icon_mvp06.png 在 PE 173 包里 0 命中（其它 mvp 01~05/07/08 均有），"
                       "PC 索引同样 0 命中；不占位、不糊图。")
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("mvp_06 图像 %d 张：%s" % (len(imgs), [x.get("label") for x in imgs]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
