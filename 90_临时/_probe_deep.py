# -*- coding: utf-8 -*-
"""1) 450204：页尺寸 vs atlas 声明、region 抽取、attachment 尺寸；2) 450002：骨骼旋转动画。"""
import json, math, pathlib, sys
from PIL import Image

PROJ = pathlib.Path(r"e:/la拆包项目")
WEB = PROJ / "02_wiki/web"
sys.path.insert(0, str(WEB / "tools"))
import spine_render_fix as FX
from build_avatar_anim import page_declared_sizes, page_cache_path
from avatar_resolve import Resolver

OUT = PROJ / "90_临时/_check"

def page_size_of(base):
    at = WEB / "assets/spine_live" / (base + ".atlas")
    txt = at.read_text(encoding="utf-8", errors="ignore")
    pg = page_cache_path(base, txt.splitlines()[0].strip())
    print("  page file:", pg, "exists", pg.is_file())
    if pg.is_file():
        print("  page real size:", Image.open(pg).size, "declared:", page_declared_sizes(txt))

# ---- 450204
base = "ui/spine_new/gexingwuliao/touxiang/icon_touxiang_204"
print("=== 450204", base)
page_size_of(base)
at = WEB / "assets/spine_live" / (base + ".atlas")
skel, pages, regions = FX.load_atlas(at)
keys = sorted(regions)
print("  regions:", len(keys), "first:", keys[:3], "last:", keys[-3:])
for k in (keys[0], keys[45], keys[-1]):
    print("   ", k, regions[k])
skin = skel["skins"]["default"]["touxiang"]
for k in (keys[0], keys[45], keys[-1]):
    a = skin.get(k)
    print("   att", k, {kk: a.get(kk) for kk in ("x", "y", "width", "height", "type", "rotation")})
# 抽取几个 region 存图
pg = page_cache_path(base, pages[0])
img = Image.open(pg).convert("RGBA")
sheet = Image.new("RGBA", (88 * 6 + 20, 88), (30, 32, 40, 255))
x = 0
for k in (keys[0], keys[15], keys[30], keys[45], keys[60], keys[-1]):
    r = regions[k]
    crop = FX._region_cache(img, r)
    print("   crop", k, crop.size)
    sheet.alpha_composite(crop, (x, 0)); x += 88 + 4
sheet.convert("RGB").save(OUT / "raw_204_regions.jpg", quality=90)

# ---- 450006
base = "ui/spine/touxiang_jiushiguang/icon_touxiang_06"
print("=== 450006", base)
page_size_of(base)
at = WEB / "assets/spine_live" / (base + ".atlas")
skel, pages, regions = FX.load_atlas(at)
skin = skel["skins"]["default"]
for sn in ("bg", "diejia", "fz", "gen"):
    a = skin.get(sn, {}).get(sn)
    print("   att", sn, {kk: a.get(kk) for kk in ("x", "y", "width", "height", "type")} if a else None)
    print("      region", regions.get(sn))
print("  bones:", [(b["name"], b.get("parent"), b.get("x"), b.get("y")) for b in skel["bones"]])
print("  y2 anim:", json.dumps((skel["animations"]["loop"].get("bones") or {}).get("y2"), ensure_ascii=False)[:600])

# ---- 450002 旋转
base = "ui/spine/touxiang_ani/touxiang_ani_03"
print("=== 450002", base)
page_size_of(base)
at = WEB / "assets/spine_live" / (base + ".atlas")
skel, pages, regions = FX.load_atlas(at)
anim = skel["animations"]["loop"]
rots = {k: v["rotate"] for k, v in (anim.get("bones") or {}).items() if "rotate" in v}
print("  有 rotate 的骨骼:", len(rots))
w0 = FX.bone_world(skel, anim, 0.0)
w1 = FX.bone_world(skel, anim, 1.0)
for bn in rots:
    r0 = math.degrees(math.atan2(w0[bn][1][0], w0[bn][0][0])) if bn in w0 else None
    r1 = math.degrees(math.atan2(w1[bn][1][0], w1[bn][0][0])) if bn in w1 else None
    print("   %-10s anim=%s  worldRot t0=%.2f t1=%.2f" % (
        bn, json.dumps(rots[bn][:3], ensure_ascii=False), r0, r1))
print("  setup bones:")
for b in skel["bones"]:
    if b.get("rotation") or b.get("scaleX") not in (None, 1) or b.get("scaleY") not in (None, 1):
        print("   ", b["name"], "parent", b.get("parent"), "rot", b.get("rotation"), "scale", b.get("scaleX"), b.get("scaleY"))
print("  slot 22/25/21/24/23 的 att bone:")
for s in skel["slots"][:6]:
    print("   ", s)
