# -*- coding: utf-8 -*-
"""检查三个骨架在 t=0 时各 slot 世界矩阵的 det 符号 / 负缩放，以及 slot 尺寸位置。"""
import json, math, pathlib, sys

PROJ = pathlib.Path(r"e:/la拆包项目")
WEB = PROJ / "02_wiki/web"
sys.path.insert(0, str(WEB / "tools"))

import spine_render_fix as FX

CASES = [
    ("450002", "ui/spine/touxiang_ani/touxiang_ani_03"),
    ("450006", "ui/spine/touxiang_jiushiguang/icon_touxiang_06"),
    ("450204", "ui/spine_new/gexingwuliao/touxiang/icon_touxiang_204"),
]

for tag, base in CASES:
    at = WEB / "assets/spine_live" / (base + ".atlas")
    skel, pages, regions = FX.load_atlas(at)
    aname = FX.anim_name(skel)
    anim = (skel.get("animations") or {}).get(aname) or {}
    dur = FX.anim_duration(skel, aname)
    print("=" * 70)
    print(tag, base, "anim", aname, "dur", dur)
    sk = skel.get("skeleton") or {}
    print("  W,H", sk.get("width"), sk.get("height"), "bones", len(skel["bones"]), "slots", len(skel["slots"]))
    # 负缩放骨骼
    neg = [(b["name"], b.get("scaleX"), b.get("scaleY")) for b in skel["bones"]
           if float(b.get("scaleX", 1)) < 0 or float(b.get("scaleY", 1)) < 0]
    print("  负缩放骨骼(setup):", neg[:20])
    for t in (0.0, dur / 2 if dur else 0.5, max(0.0, dur - 0.05)):
        w = FX.bone_world(skel, anim, t)
        dets = []
        for s in skel["slots"]:
            m = w.get(s.get("bone"))
            if not m:
                continue
            det = m[0][0] * m[1][1] - m[0][1] * m[1][0]
            if det < 0:
                dets.append((s["name"], s.get("bone"), round(det, 4)))
        print("  t=%.2f det<0 slots (%d):" % (t, len(dets)), dets[:12])
    # 主要 slot 位置尺寸
    print("  slots(前 24):")
    w0 = FX.bone_world(skel, anim, 0.0)
    for s in skel["slots"][:24]:
        att_name = s.get("attachment")
        reg = regions.get(att_name or "")
        m = w0.get(s.get("bone"))
        det = None
        if m:
            det = round(m[0][0] * m[1][1] - m[0][1] * m[1][0], 3)
        print("    %-16s bone=%-14s att=%-18s reg=%s m02=%.3f m12=%.3f det=%s" % (
            s["name"], s.get("bone"), att_name,
            (reg["w"], reg["h"]) if reg else None,
            m[0][2] if m else 0, m[1][2] if m else 0, det))
    # 动画里是否有负缩放
    aneg = []
    for bn, grp in (anim.get("bones") or {}).items():
        tl = grp.get("scale")
        if tl:
            for k in tl:
                if float(k.get("x", 1)) < 0 or float(k.get("y", 1)) < 0:
                    aneg.append((bn, k.get("time"), k.get("x"), k.get("y")))
    print("  负缩放骨骼(动画):", aneg[:10])
    # clipping 附件
    clip = 0
    for sn, atts in (skel.get("skins") or {}).get("default", {}).items() if isinstance(skel.get("skins"), dict) else []:
        for n, a in atts.items():
            if a.get("type") == "clipping" or a.get("vertices") and a.get("type") == "clipping":
                clip += 1
    print("  clipping 附件数:", clip)
