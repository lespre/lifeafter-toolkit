# -*- coding: utf-8 -*-
"""MVP 8 条回写图片：优先用 assets/kill_broadcast 里已导出的 mvp_bq_mvp_0X[_cover].png。

卡片展示取 _cover（572×324 主视觉）优先，没有则用 300×150 本体。
"""
from __future__ import annotations

import json
import pathlib
import sys

from PIL import Image  # noqa: E402

WEB = pathlib.Path("E:/la拆包项目/02_wiki/web")
BOARD = WEB / "data/boards/kill_broadcast.json"
ASSETS = WEB / "assets/kill_broadcast"


def pick(stem: str) -> list[pathlib.Path]:
    cov = ASSETS / (stem + "_cover.png")
    base = ASSETS / (stem + ".png")
    out = []
    if cov.is_file():
        out.append(cov)
    if base.is_file():
        out.append(base)
    return out


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    ok = 0
    for it in d["items"]:
        if it.get("kind") != "MVP 结算动画":
            continue
        stem = str(it.get("id") or "").replace("kb_", "") or str(it.get("item_id"))
        cands = []
        for s in (stem, "mvp_" + stem, "mvp_bq_mvp_" + str(it.get("mvp_id") or "")[-2:]):
            cands += pick(s)
        cands = [p for p in dict.fromkeys(cands) if p.is_file()]
        if not cands:
            print("无图", it["name"], stem)
            continue
        imgs = []
        for p in cands[:2]:
            try:
                w, h = Image.open(p).size
            except Exception:  # noqa: BLE001
                w = h = 0
            imgs.append({"png": "assets/kill_broadcast/%s" % p.name,
                         "base": p.stem,
                         "label": "主视觉" if p.name.endswith("_cover.png") else "图标",
                         "size": [w, h],
                         "source": "PE"})
        it["_media"] = {"images": imgs, "total": len(imgs)}
        ok += 1
        print("回写", it["name"], [i["png"].split("/")[-1] for i in imgs])
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("MVP 回写 %d 条" % ok)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
