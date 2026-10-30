# -*- coding: utf-8 -*-
"""解析 NeoX .sfx（FxGroup XML）关键结构：生命周期、节点类型、贴图、粒子数。"""
from __future__ import annotations

import collections
import pathlib
import re
import xml.etree.ElementTree as ET


def analyze(path: pathlib.Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return {"file": path.name, "error": "XML 解析失败"}
    tags = collections.Counter(el.tag for el in root.iter())
    tex = sorted({m for m in re.findall(r"[A-Za-z0-9_/\.\-]+\.(?:tga|png|ktx|dds)", text)})
    g = root.attrib
    return {
        "file": path.name,
        "bytes": path.stat().st_size,
        "loop": g.get("Loop"),
        "life": g.get("FxLifeSpan"),
        "max_particles": g.get("MaxParticleCount"),
        "tags": {k: v for k, v in tags.most_common() if k not in ("Frame", "ColorFrame",
                                                                 "GravityFrame", "MaxSpriteVelocityFrame",
                                                                 "MinSpriteVelocityFrame", "RotDegreeSpeedFrame",
                                                                 "TrackFixPoint")},
        "textures": tex,
    }


if __name__ == "__main__":
    import sys
    for f in sys.argv[1:]:
        r = analyze(pathlib.Path(f))
        print("%-28s %6s B  loop=%-5s life=%-6s maxP=%-4s" %
              (r["file"], r.get("bytes"), r.get("loop"), r.get("life"), r.get("max_particles")))
        print("    节点:", ", ".join("%s×%d" % (k, v) for k, v in list(r.get("tags", {}).items())[:10]))
        print("    贴图:", ", ".join(r.get("textures", [])))
