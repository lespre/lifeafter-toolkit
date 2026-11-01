# -*- coding: utf-8 -*-
"""逐 slot 单独绘制，定位异常绘制位置。"""
import pathlib, sys
import numpy as np
sys.path.insert(0, r"02_wiki/web/tools")
sys.path.insert(0, r"00_规范与工具/工具/工具库/00_共享核心")
sys.path.insert(0, r"00_规范与工具/工具/工具库/01_解码定位复原/图集与取图")
import spine_render_fix as FX
from toolkit_core import android_gpk as AG
from PIL import Image

base = sys.argv[1] if len(sys.argv) > 1 else "ui/spine_new/gexingwuliao/touxiang/icon_touxiang_146"
at = pathlib.Path("02_wiki/web/assets/spine_live") / (base + ".atlas")
skel, pages, regions = FX.load_atlas(at)
d = base.rsplit("/", 1)[0]
page = None
for pg in pages:
    cand = pathlib.Path("01_索引与产物/41_还原树/pe/资源") / (d + "/" + pg)
    if cand.with_suffix(".ktx").is_file():
        data = cand.with_suffix(".ktx").read_bytes()
        page = Image.fromarray(AG.decode_image({"data": data, "kind": "ktx", "info": AG.parse_ktx(data), "e": None}), "RGBA")
        break
anim = skel["animations"][FX.anim_name(skel)]
anim_slots = anim.get("slots") or {}
scale = 420 / max(skel["skeleton"]["width"], skel["skeleton"]["height"])
off = (700, 700)
canvas = 1400
world = FX.bone_world(skel, anim, 0.0)
FX.apply_ik(skel, world, anim, 0.0)
default = skel["skins"]["default"]
bones_mat = [world.get(b["name"], FX.IDENT) for b in skel["bones"]]
print("spine", skel["skeleton"].get("spine"), "scale", round(scale, 2), "page", page.size)
for s in skel["slots"]:
    nm = s.get("attachment")
    att = (default.get(s["name"]) or {}).get(nm)
    if not att:
        print(s["name"], "no att")
        continue
    atype = att.get("type") or ("mesh" if att.get("uvs") else "region")
    bm = world.get(s.get("bone"), FX.IDENT)
    reg = regions.get(att.get("name") or nm)
    if not reg:
        print(s["name"], atype, "no region", att.get("name") or nm)
        continue
    cv = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    if atype in ("mesh", "skinnedmesh"):
        ok = FX.draw_mesh(cv, FX._region_cache(page, reg), att, bones_mat, bm, scale, off)
    else:
        ok = FX.draw_region(cv, page, reg, att, bm, scale, off)
    a = np.asarray(cv)[:, :, 3]
    ys, xs = np.nonzero(a > 8)
    if xs.size:
        print(s["name"], atype, "ok", ok, "bbox", (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())), "cnt", int(xs.size))
    else:
        print(s["name"], atype, "EMPTY", ok)
