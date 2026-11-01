# -*- coding: utf-8 -*-
"""探查三条「比例异常」头像骨架的构成：画板尺寸、骨骼、slot、附件类型。"""
import json
import pathlib
import sys

WEB = pathlib.Path(r"e:\la拆包项目\02_wiki\web")
sys.path.insert(0, str(WEB / "tools"))

for base in ("ui/spine_new/gexingwuliao/touxiang/icon_touxiang_55",
             "ui/spine_new/gexingwuliao/touxiang/icon_touxiang_63",
             "ui/spine_new/gexingwuliao/touxiang/icon_touxiang_113"):
    j = WEB / "assets/spine_live" / (base + ".json")
    if not j.is_file():
        print(base, "缺 json")
        continue
    s = json.loads(j.read_text(encoding="utf-8"))
    sk = s["skeleton"]
    print("\n###", base)
    print("  spine", sk.get("spine"), "W,H=", sk.get("width"), sk.get("height"))
    print("  bones=%d slots=%d" % (len(s.get("bones", [])), len(s.get("slots", []))))
    neg = [b["name"] for b in s.get("bones", [])
           if b.get("scaleX", 1) < 0 or b.get("scaleY", 1) < 0]
    print("  负缩放骨骼:", neg[:8])
    types = {}
    for sk2 in s.get("skins", {}).values():
        for slot, atts in sk2.items():
            for nm, att in atts.items():
                types[att.get("type", "region")] = types.get(att.get("type", "region"), 0) + 1
    print("  附件类型:", types)
    anims = s.get("animations") or {}
    for an, a in anims.items():
        dur = 0
        for grp in a.values():
            if isinstance(grp, dict):
                for k, keys in grp.items():
                    if isinstance(keys, list) and keys:
                        dur = max(dur, keys[-1].get("time", 0))
        print("  anim %s dur=%.2fs" % (an, dur))
    print("  slots:", [sl["name"] for sl in s.get("slots", [])][:12])
