# -*- coding: utf-8 -*-
"""把单条头像动图重新渲进正式产物，并恢复目录条目里的 anim 字段。"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_avatar_anim as B      # noqa: E402
import spine_render_fix as FX      # noqa: E402
from PIL import Image              # noqa: E402
from avatar_resolve import Resolver  # noqa: E402

IID = "da_450002"


def main() -> int:
    cat = json.loads(B.CAT.read_text(encoding="utf-8"))
    it = next(x for x in cat["items"] if x["id"] == IID)
    base = it["spine_path"].strip().replace("\\", "/").rstrip("/")
    at_f = B.SPINE_DIR / (base + ".atlas")
    res = Resolver()
    atlas_text = at_f.read_text(encoding="utf-8", errors="ignore") if at_f.is_file() else res.fetch_text(base + ".atlas")
    pg_f = B.SPINE_DIR / (base + ".png")
    B.grab_page(res, base, atlas_text or "", pg_f)
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
    out = B.ANIM_DIR / (IID + ".png")
    out.parent.mkdir(parents=True, exist_ok=True)
    frs[0].save(out, format="PNG", save_all=True, append_images=frs[1:],
                duration=int(round(dur * 1000 / cnt)), loop=0, default_image=True)

    m = it.setdefault("_media", {})
    m["anim"] = "assets/avatar_anim/%s.png" % IID
    m["anim_meta"] = {"spine": (skel.get("skeleton") or {}).get("spine"), "anim": aname,
                      "frames": len(frs), "duration": round(dur, 3),
                      "source": base + ".atlas"}
    for k in ("anim_status", "anim_note"):
        it.pop(k, None)
    B.CAT.write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding="utf-8")
    print("已重渲", IID, "→", out, out.stat().st_size, "B，帧", len(frs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
