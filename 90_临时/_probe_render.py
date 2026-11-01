# -*- coding: utf-8 -*-
"""单条渲染试验：用还原树的页贴图 + 本地 atlas/json 渲染，输出多帧与静态图对比。"""
import json, pathlib, sys
import numpy as np

PROJ = pathlib.Path(r"e:/la拆包项目")
WEB = PROJ / "02_wiki/web"
sys.path.insert(0, str(WEB / "tools"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与抓图"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))

from PIL import Image
import spine_render_fix as FX
from toolkit_core import android_gpk as AG

TREE = PROJ / "01_索引与产物/41_还原树/pe/资源"
SPINE = WEB / "assets/spine_live"
OUT = PROJ / "90_临时/_probe_render"
OUT.mkdir(parents=True, exist_ok=True)


def tree_lookup(logical):
    p = TREE / logical
    if p.is_file():
        return p
    for e in (".ktx", ".bc7", ".png", ".dds", ".jpg"):
        q = p.with_suffix(e)
        if q.is_file():
            return q
    return None


def load_page_img(path):
    if path.suffix.lower() == ".ktx":
        data = path.read_bytes()
        rec = {"data": data, "kind": "ktx", "info": AG.parse_ktx(data), "e": None}
        rgba = AG.decode_image(rec)
        im = Image.fromarray(rgba, "RGBA")
        info = AG.parse_ktx(data)
        if (im.width, im.height) != (info["width"], info["height"]):
            im = im.transpose(Image.ROTATE_90) if False else im
        return im, info
    return Image.open(path).convert("RGBA"), None


def run(base, tag):
    at = SPINE / (base + ".atlas")
    skel, pages, regions = FX.load_atlas(at)
    d = base.rsplit("/", 1)[0]
    img_of = {}
    for pg in pages:
        hit = tree_lookup(d + "/" + pg)
        if hit is None:
            print("  page missing", pg); continue
        im, info = load_page_img(hit)
        print("  page", pg, "file", hit.name, "size", im.size, "info", info and (info["width"], info["height"]))
        img_of[pg] = im
    aname = FX.anim_name(skel)
    frs, meta = FX.render_frames(at, img_of, box=300, cnt=12, aname=aname)
    print(" ", tag, base, "frames", len(frs), meta)
    if not frs:
        return
    for i, f in enumerate(frs[:4]):
        a = np.asarray(f)[: , :, 3]
        print("   frame", i, f.size, "coverage", round(float((a > 8).mean()), 4))
    w = sum(f.width for f in frs[:4])
    h = max(f.height for f in frs[:4])
    sh = Image.new("RGBA", (w, h), (40, 42, 50, 255))
    x = 0
    for f in frs[:4]:
        sh.alpha_composite(f, (x, 0)); x += f.width
    sh.convert("RGB").save(OUT / (tag + ".png"))


if __name__ == "__main__":
    for spec in sys.argv[1:]:
        tag, base = spec.split("=", 1)
        run(base, tag)
