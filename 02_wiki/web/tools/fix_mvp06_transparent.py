# -*- coding: utf-8 -*-
"""MVP 沙海月鸣：删男款结算截图；图标立绘去黑底转透明。"""
from __future__ import annotations
import sys

import json
import pathlib
from collections import deque

from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

ROOT = pathlib.Path(PROJ)
WEB = ROOT / "02_wiki/web"
BOARD = WEB / "data/boards/kill_broadcast.json"
ICON = WEB / "assets/kill_broadcast/mvp_bq_mvp_06_icon.png"
MALE_COVER = WEB / "assets/kill_broadcast/mvp_bq_mvp_06_cover_nan.png"


def transparent_bg(p: pathlib.Path, tol: int = 40) -> tuple[int, int]:
    im = Image.open(p).convert("RGBA")
    w, h = im.size
    px = im.load()
    seen = bytearray(w * h)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            q.append((x, y))
    cleared = 0
    while q:
        x, y = q.popleft()
        if x < 0 or y < 0 or x >= w or y >= h:
            continue
        i = y * w + x
        if seen[i]:
            continue
        seen[i] = 1
        r, g, b, a = px[x, y]
        if a == 0 or (r + g + b) <= tol * 3:
            px[x, y] = (r, g, b, 0)
            cleared += 1
            q.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])
    im.save(p)
    return w, h, cleared


def main() -> int:
    w, h, n = transparent_bg(ICON)
    print("图标 %dx%d，透明化像素 %d" % (w, h, n))

    d = json.loads(BOARD.read_text(encoding="utf-8"))
    it = next(x for x in d["items"] if x["id"] == "mvp_bq_mvp_06")
    imgs = [x for x in it["_media"]["images"] if x.get("label") != "主视觉（男）"]
    it["_media"]["images"] = imgs
    it["_media"]["total"] = len(imgs)
    it["male_cover_removed"] = "男款结算截图已按用户口径删除"
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    if MALE_COVER.is_file():
        MALE_COVER.unlink()
    print("剩余图像：", [x.get("label") for x in imgs])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
