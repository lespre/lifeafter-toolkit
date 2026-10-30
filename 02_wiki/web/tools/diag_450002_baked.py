# -*- coding: utf-8 -*-
"""判定 skinnedmesh.vertices 是「骨骼局部坐标」还是「已烘焙世界坐标」。

判据：算每个顶点引用的骨骼的 (x,y) 加权和；
  · 若顶点坐标 ≈ 该和 → 顶点已烘焙世界（不该再乘骨骼矩阵）
  · 若顶点坐标集中在 0 附近、与骨位置无关 → 局部坐标（现行做法正确）
"""
from __future__ import annotations

import json
import pathlib
import statistics

P = pathlib.Path("E:/la拆包项目/02_wiki/web/assets/spine_live/ui/spine/touxiang_ani/touxiang_ani_03.json")


def main() -> int:
    d = json.loads(P.read_text(encoding="utf-8"))
    bones = d["bones"]
    skin = d["skins"]["default"]
    for slot, atts in list(skin.items()):
        for name, a in atts.items():
            if (a.get("type") or "") != "skinnedmesh":
                continue
            verts = a["vertices"]
            i = 0
            near_bone = 0
            far = 0
            dists = []
            n = 0
            while i < len(verts):
                cnt = int(verts[i]); i += 1
                bx = by = 0.0
                vx = vy = 0.0
                for _ in range(cnt):
                    bidx = int(verts[i]); x = float(verts[i + 1]); y = float(verts[i + 2]); w = float(verts[i + 3])
                    i += 4
                    b = bones[bidx]
                    bx += float(b.get("x", 0.0)) * w
                    by += float(b.get("y", 0.0)) * w
                    vx += x * w
                    vy += y * w
                dd = ((vx - bx) ** 2 + (vy - by) ** 2) ** 0.5
                dists.append(dd)
                if dd < 5:
                    near_bone += 1
                else:
                    far += 1
                n += 1
            print("mesh %-6s 顶点 %3d ｜ 顶点≈骨位置 %3d ｜ 远离骨 %3d ｜ 中位距 %.1f"
                  % (name, n, near_bone, far, statistics.median(dists) if dists else -1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
