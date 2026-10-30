# -*- coding: utf-8 -*-
"""单条试渲：python test_render_one.py da_450002 [da_450129 ...] → 写到 scratch，不覆盖正式产物。"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_avatar_anim as B          # noqa: E402
import spine_render_fix as FX          # noqa: E402
from PIL import Image                  # noqa: E402
from avatar_resolve import Resolver    # noqa: E402

OUT = pathlib.Path("C:/Users/Administrator/AppData/Local/hermes/cache/scratch/render_one")
OUT.mkdir(parents=True, exist_ok=True)


def main(argv: list[str]) -> int:
    ids = argv or ["da_450002"]
    cat = json.loads(B.CAT.read_text(encoding="utf-8"))
    idx = {it["id"]: it for it in cat["items"]}
    res = Resolver()
    for iid in ids:
        it = idx.get(iid)
        if not it:
            print(iid, "不在板上")
            continue
        base = it["spine_path"].strip().replace("\\", "/").rstrip("/")
        at_f = B.SPINE_DIR / (base + ".atlas")
        js_f = B.SPINE_DIR / (base + ".json")
        atlas_text = at_f.read_text(encoding="utf-8", errors="ignore") if at_f.is_file() else res.fetch_text(base + ".atlas")
        if not at_f.is_file() and atlas_text:
            at_f.parent.mkdir(parents=True, exist_ok=True)
            at_f.write_text(atlas_text, encoding="utf-8")
        if not js_f.is_file():
            t = res.fetch_text(base + ".json")
            if t:
                js_f.parent.mkdir(parents=True, exist_ok=True)
                js_f.write_text(t, encoding="utf-8")
        pg_f = B.SPINE_DIR / (base + ".png")
        if not B.grab_page(res, base, atlas_text or "", pg_f):
            print(iid, "贴图页取不到")
            continue
        skel, pages, regions = FX.load_atlas(at_f)
        img_of = {}
        for pg in pages:
            src = pg_f if (pg_f.is_file() and "/" not in pg) else (B.SPINE_DIR / (base.rsplit("/", 1)[0] + "/" + pg if "/" in base else pg))
            if not src.is_file():
                src = pg_f
            if src.is_file():
                img_of[pg] = Image.open(src).convert("RGBA")
        aname = FX.anim_name(skel)
        dur = FX.anim_duration(skel, aname) or 1.0
        cnt = max(6, min(24, int(round(dur * B.FPS_FALLBACK))))
        frs, meta = FX.render_frames(at_f, img_of, box=168, cnt=cnt, aname=aname)
        dst = OUT / (iid + ".png")
        frs[0].save(dst, format="PNG", save_all=True, append_images=frs[1:],
                    duration=int(round(dur * 1000 / cnt)), loop=0, default_image=True)
        print(iid, it.get("name"), "→", dst, "帧", len(frs), "尺寸", frs[0].size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
