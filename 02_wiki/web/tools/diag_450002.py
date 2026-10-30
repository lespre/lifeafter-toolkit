# -*- coding: utf-8 -*-
"""诊断 da_450002：atlas regions / 页尺寸 / mesh 顶点与 uv 范围。"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import spine_render_fix as FX  # noqa: E402

SP = pathlib.Path("E:/la拆包项目/02_wiki/web/assets/spine_live/ui/spine/touxiang_ani")


def main() -> int:
    at = SP / "touxiang_ani_03.atlas"
    skel, pages, regions = FX.load_atlas(at)
    print("页", pages)
    print("regions", len(regions))
    for name, r in list(regions.items())[:10]:
        print("  %-12s page=%-24s x=%s y=%s w=%s h=%s rot=%s" %
              (name, r.get("page"), r.get("x"), r.get("y"), r.get("w"), r.get("h"), r.get("rotate")))
    d = json.loads((SP / "touxiang_ani_03.json").read_text(encoding="utf-8"))
    skin = (d.get("skins") or {}).get("default") or {}
    for slot, atts in skin.items():
        for name, a in atts.items():
            if (a.get("type") or "") in ("mesh", "skinnedmesh"):
                uvs = a.get("uvs") or []
                verts = a.get("vertices") or []
                tris = a.get("triangles") or []
                xs = uvs[0::2]; ys = uvs[1::2]
                vx = verts[0::2]; vy = verts[1::2]
                print("mesh slot=%-10s name=%-6s verts=%d tris=%d uv x[%.3f,%.3f] y[%.3f,%.3f] 顶点 x[%.1f,%.1f] y[%.1f,%.1f]"
                      % (slot, name, len(verts) // 2, len(tris) // 3, min(xs), max(xs), min(ys), max(ys),
                         min(vx), max(vx), min(vy), max(vy)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
