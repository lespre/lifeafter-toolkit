# -*- coding: utf-8 -*-
"""统计本地 spine 缓存里哪些骨架带 mesh/skinnedmesh，并记录根链缩放。"""
from __future__ import annotations

import json
import math
import pathlib

SP = pathlib.Path("E:/la拆包项目/02_wiki/web/assets/spine_live")


def main() -> int:
    rows = []
    for p in SP.rglob("*.json"):
        try:
            d = json.loads(p.read_text(encoding="utf-8", errors="ignore"))
        except Exception:  # noqa: BLE001
            continue
        if "bones" not in d or "skins" not in d:
            continue
        meshes = 0
        skins = d.get("skins") or {}
        skins = skins.values() if isinstance(skins, dict) else [
            (x.get("attachments") if isinstance(x, dict) else {}) for x in skins]
        for skin in skins:
            if not isinstance(skin, dict):
                continue
            for atts in skin.values():
                if not isinstance(atts, dict):
                    continue
                for a in atts.values():
                    if isinstance(a, dict) and (a.get("type") in ("mesh", "skinnedmesh")):
                        meshes += 1
        if not meshes:
            continue
        by = {b["name"]: b for b in d["bones"]}
        chain = []
        n = d["bones"][0]["name"] if d["bones"] else None
        cur = d["bones"][0]
        seen = 0
        while cur and seen < 8:
            chain.append((cur["name"], cur.get("scaleX"), cur.get("scaleY")))
            nxt = by.get(cur.get("parent")) if cur.get("parent") else None
            cur = nxt
            seen += 1
        root_scale = 1.0
        for _, sx, sy in chain:
            if sx and sy:
                root_scale *= float(sx)
        rows.append((str(p.relative_to(SP)), meshes, round(root_scale, 3), chain[:3]))
    print("带 mesh 的骨架 %d 个" % len(rows))
    for r in rows[:12]:
        print("  %-52s mesh %2d ｜ 根链缩放 %.3f ｜ %s" % (r[0][:52], r[1], r[2], r[3]))
    from collections import Counter
    print("根链缩放分布", Counter(r[2] for r in rows).most_common(6))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
