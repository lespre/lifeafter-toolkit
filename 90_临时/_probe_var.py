# -*- coding: utf-8 -*-
"""变体矩阵：sprite 旋转符号 × atlas 旋转解包方向，在多个骨架上与静态图比数值/出图。"""
import json, pathlib, sys, types
from PIL import Image
import numpy as np

PROJ = pathlib.Path(r"e:/la拆包项目")
WEB = PROJ / "02_wiki/web"
TOOLS = WEB / "tools"
sys.path.insert(0, str(TOOLS))
SRC = (TOOLS / "spine_render_fix.py").read_text(encoding="utf-8")
from build_avatar_anim import load_pages, page_declared_sizes
from avatar_resolve import Resolver

OUT = PROJ / "90_临时/_check"
RES = Resolver()


def variant(rot_sign, atlas_rot):
    src = SRC.replace("sprite.rotate(ang, expand=True", "sprite.rotate(%sang, expand=True" % rot_sign)
    src = src.replace("transpose(Image.ROTATE_90)", "transpose(Image.ROTATE_%s)" % atlas_rot)
    src = src.replace("transpose(Image.ROTATE_270)", "transpose(Image.ROTATE_%s)" % atlas_rot)
    mod = types.ModuleType("fxv_%s_%s" % (rot_sign.replace("-", "neg"), atlas_rot))
    mod.__file__ = str(TOOLS / "spine_render_fix.py")
    exec(compile(src, mod.__file__, "exec"), mod.__dict__)
    return mod


cases = [("450002", "ui/spine/touxiang_ani/touxiang_ani_03")]
d = json.load(open(WEB / "data/boards/avatar_catalog.json", encoding="utf-8"))
for it in d["items"]:
    sp = (it.get("spine_path") or "")
    if "touxiang_ani_02" in sp:
        cases.append((it["id"].replace("da_", ""), sp))
print("cases:", cases)

variants = [("+", "270"), ("+", "90"), ("-", "270"), ("-", "90")]
sheets = []
for tag, base in cases:
    st_path = WEB / "assets/img_cache/avatar_catalog" / ("da_" + tag + ".png")
    static = Image.open(st_path).convert("RGBA")
    print("=" * 60)
    print(tag, base, "static", static.size)
    cells = [("static", static)]
    for rs, ar in variants:
        mod = variant(rs, ar)
        at = WEB / "assets/spine_live" / (base + ".atlas")
        skel, pages, regions = mod.load_atlas(at)
        img_of, missing = load_pages(RES, base, pages,
                                     page_declared_sizes(at.read_text(encoding="utf-8", errors="ignore")))
        if missing:
            print("  ", rs, ar, "missing pages", missing)
            continue
        frs, meta = mod.render_frames(at, img_of, box=420, cnt=6,
                                      aname=mod.anim_name(skel), crop="coverage")
        f0 = frs[0]
        st = static.resize(f0.size, Image.LANCZOS)
        a = np.asarray(f0, dtype=np.int16); b = np.asarray(st, dtype=np.int16)
        print("  sign%s atlas%s  canvas=%s  rgb=%.2f alpha=%.2f" % (
            rs, ar, meta["canvas"],
            np.abs(a[..., :3] - b[..., :3]).mean(), np.abs(a[..., 3] - b[..., 3]).mean()))
        cells.append(("%s%s" % (rs, ar), f0))
    S = 300
    sheet = Image.new("RGB", (S * len(cells), S), (24, 26, 32))
    x = 0
    for nm, im in cells:
        r = min((S - 6) / im.width, (S - 6) / im.height)
        big = im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)
        bg = Image.new("RGBA", big.size, (24, 26, 32, 255))
        bg.alpha_composite(big)
        sheet.paste(bg.convert("RGB"), (x + 3, 3)); x += S
    sheet.save(OUT / ("var_%s.jpg" % tag), quality=90)
    print("  saved var_%s.jpg" % tag)
