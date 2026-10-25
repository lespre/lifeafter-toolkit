# -*- coding: utf-8 -*-
"""用骨骼名集合的 Jaccard 相似度，给喷火器皮肤找最接近的本体。"""
from __future__ import annotations

import glob
import json
import pathlib
import sys

D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else
                 "C:/Users/Administrator/AppData/Local/hermes/cache/scratch/skel1013")


def load():
    sk, wp = {}, {}
    for f in sorted(glob.glob(str(D / "*_skeleton.json"))):
        d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        bones = d.get("bones") or []
        stem = pathlib.Path(f).stem.replace("_skeleton", "")
        (sk if stem.startswith("skin_") else wp)[stem] = set(bones)
    return sk, wp


def jac(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def main() -> int:
    sk, wp = load()
    print("皮肤 %d ｜ 本体 %d" % (len(sk), len(wp)))
    for s, sb in sk.items():
        ranked = sorted(((jac(sb, wb), w) for w, wb in wp.items()), reverse=True)
        top = ", ".join("%s %.2f" % (w.replace("weapon_", ""), v) for v, w in ranked[:3])
        print("  %-18s 骨 %3d → %s" % (s.replace("skin_", ""), len(sb), top or "无候选"))
    print("\n本体骨数:", {w.replace("weapon_", ""): len(b) for w, b in wp.items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
