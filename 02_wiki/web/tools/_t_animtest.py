# -*- coding: utf-8 -*-
"""临时验证：用修正版 draw_region 渲染 touxiang_ani_02 的第 0 帧。"""
from __future__ import annotations

import json
import pathlib
import sys


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402
sys.path.insert(0, str(WEB / "tools"))
import spine_render as SR
import spine_render_fix as FX

SR.draw_region = FX.draw_region

from PIL import Image

AT = pathlib.Path(WEB / "assets/spine_live/ui/spine/touxiang_ani/touxiang_ani_02.atlas")
size = 256
skel = json.loads(AT.with_suffix(".json").read_text(encoding="utf-8"))
pages, regions = SR.parse_atlas(AT)
page_img = Image.open(AT.parent / pages[0]).convert("RGBA")
W, H = skel["skeleton"].get("width", 128), skel["skeleton"].get("height", 128)
scale = min(size / max(W, 1), size / max(H, 1))
off = (size / 2, size / 2)
anim = skel["animations"]["loop"]
t = 0.6
canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
world = SR.bone_world(skel, anim, t)
for slot in skel.get("slots", []):
    att = (skel.get("skins", {}).get("default", {}).get(slot["name"]) or {}).get(slot.get("attachment"))
    if not att:
        continue
    bm = world.get(slot["bone"], FX.IDENT)
    reg = regions.get(att.get("name") or slot["attachment"])
    if reg:
        FX.draw_region(canvas, page_img, reg, att, bm, scale, off)
bg = Image.new("RGBA", (size, size), (60, 60, 66, 255))
bg.alpha_composite(canvas)
bg.convert("RGB").save(str(WEB / "tools/_t_frame.png"))
print("ok")
