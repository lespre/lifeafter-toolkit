# -*- coding: utf-8 -*-
"""从 Spine atlas 切出最大区域做缩略图（展示真实元素，而不是整张贴图页）。"""
from __future__ import annotations

import json
import pathlib
import re

from PIL import Image

ROOT = pathlib.Path(r"E:/la拆包项目/02_wiki/web/assets/spine")
TH = ROOT / "thumbs"
TH.mkdir(exist_ok=True)

xy_rx = re.compile(r"^\s*xy:\s*(\d+)\s*,\s*(\d+)")
sz_rx = re.compile(r"^\s*size:\s*(\d+)\s*,\s*(\d+)")
rot_rx = re.compile(r"^\s*rotate:\s*(\w+)")


def regions(atlas: pathlib.Path):
    out, cur = [], {}
    for line in atlas.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = xy_rx.match(line)
        if m:
            cur["x"], cur["y"] = int(m.group(1)), int(m.group(2))
            continue
        m = sz_rx.match(line)
        if m:
            cur["w"], cur["h"] = int(m.group(1)), int(m.group(2))
            continue
        m = rot_rx.match(line)
        if m:
            cur["rot"] = m.group(1).lower() == "true"
            if "x" in cur:
                out.append(dict(cur))
            cur = {}
    if "x" in cur:
        out.append(dict(cur))
    return out


def main() -> int:
    man = json.loads((ROOT / "MANIFEST.json").read_text(encoding="utf-8"))
    done = 0
    for s in man["sets"]:
        at = ROOT / s["atlas"]
        pages = s.get("pages") or []
        if not pages or not at.is_file():
            continue
        img_path = at.parent / pages[0]
        regs = regions(at)
        if not regs:
            continue
        top = sorted(regs, key=lambda d: d["w"] * d["h"], reverse=True)[:6]
        try:
            with Image.open(img_path) as im:
                best, best_score = None, -1
                for r in top:
                    x, y, w, h = r["x"], r["y"], r["w"], r["h"]
                    if r.get("rot"):
                        w, h = h, w
                    crop = im.crop((x, y, x + w, y + h)).convert("RGBA")
                    small = crop.copy()
                    small.thumbnail((64, 64))
                    px = list(small.getdata())
                    cover = sum(1 for a in px if a[3] > 24) / max(1, len(px))
                    score = cover * min(1.0, (w * h) / 40000.0)
                    if score > best_score:
                        best, best_score = crop, score
                if best is None:
                    continue
                best.thumbnail((360, 360), Image.LANCZOS)
                out = TH / (at.stem + ".png")
                best.save(out)
                done += 1
        except Exception:
            continue
    print("缩略图", done)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
