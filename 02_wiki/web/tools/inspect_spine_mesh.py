# -*- coding: utf-8 -*-
"""看 touxiang_ani_03 的骨架：mesh/skinnedmesh 的 uvs 值域、slot 数、动画通道。"""
from __future__ import annotations

import json
import pathlib

P = pathlib.Path("E:/la拆包项目/02_wiki/web/assets/spine_live/ui/spine/touxiang_ani/touxiang_ani_03.json")


def main() -> int:
    d = json.loads(P.read_text(encoding="utf-8"))
    sk = d.get("skeleton") or {}
    print("spine 版本", sk.get("spine"), "｜ slots", len(d.get("slots") or []),
          "｜ bones", len(d.get("bones") or []), "｜ skins", len(d.get("skins") or {}))
    kinds = {"region": 0, "mesh": 0, "skinnedmesh": 0, "other": 0}
    uv_ranges = []
    for skin_name, skin in (d.get("skins") or {}).items():
        if not isinstance(skin, dict):
            continue
        for slot_name, atts in skin.items():
            if not isinstance(atts, dict):
                continue
            for att_name, a in atts.items():
                if not isinstance(a, dict):
                    continue
                t = a.get("type") or "region"
                kinds[t if t in kinds else "other"] = kinds.get(t if t in kinds else "other", 0) + 1
                uvs = a.get("uvs")
                if uvs:
                    xs = uvs[0::2]
                    ys = uvs[1::2]
                    uv_ranges.append((slot_name, att_name, t, min(xs), max(xs), min(ys), max(ys), len(uvs) // 2))
    print("附件类型", kinds)
    print("带 uvs 的附件 %d 个，前 6 个值域：" % len(uv_ranges))
    for r in uv_ranges[:6]:
        print("   %-18s %-14s %-12s x[%.3f,%.3f] y[%.3f,%.3f] 顶点 %d" % r)
    over = [r for r in uv_ranges if r[4] > 1.5 or r[6] > 1.5]
    print("uvs 超过 1.5 的附件（页像素坐标）：", len(over))
    for r in over[:6]:
        print("   ", r[0], r[1], r[2], "x[%.1f,%.1f] y[%.1f,%.1f]" % (r[3], r[4], r[5], r[6]))
    anims = d.get("animations") or {}
    print("动画", list(anims)[:5])
    for name, a in list(anims.items())[:2]:
        print("  ", name, {k: len(v) for k, v in a.items() if isinstance(v, list)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
