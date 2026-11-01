# -*- coding: utf-8 -*-
"""盘点 spine_live 的三件套完整性：json / atlas / atlas 引用的 png 是否都在。

输出：完整三件套清单 + 缺件清单
"""
import json, glob, pathlib, collections

WEB = pathlib.Path(r"E:/la拆包项目/02_wiki/web")
LIVE = WEB / "assets/spine_live/ui"

ok, bad = [], []
for jf in sorted(glob.glob(str(LIVE / "**/*.json"), recursive=True)):
    p = pathlib.Path(jf)
    atlas = p.with_suffix(".atlas")
    # ① 同名的 atlas 必须在
    if not atlas.is_file():
        bad.append((p, "缺同名 atlas"))
        continue
    # ② atlas 里声明的贴图页
    pngs = []
    for ln in atlas.read_text(encoding="utf-8", errors="replace").splitlines():
        ln = ln.strip()
        if ln.lower().endswith(".png"):
            pngs.append(ln)
        if ln.startswith("size:"):
            break
    if not pngs:
        bad.append((p, "atlas 里没有 png 页名"))
        continue
    # ③ 严格一一对应：页名必须是 <同名>.png（多页则 <同名>_N.png 之类，但必须都在同目录）
    wrong = [x for x in pngs if pathlib.Path(x).stem != p.stem
             and not pathlib.Path(x).stem.startswith(p.stem + "_")]
    if wrong:
        bad.append((p, "页名与 json 不同名: " + ", ".join(wrong)))
        continue
    missing = [x for x in pngs if not (p.parent / x).is_file()]
    if missing:
        bad.append((p, "缺 png: " + ", ".join(missing)))
        continue
    ver = ""
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        ver = str((d.get("skeleton") or {}).get("spine"))
        anims = list((d.get("animations") or {}).keys())
    except Exception:
        ver, anims = "?", []
    ok.append({"dir": p.parent.relative_to(LIVE).as_posix(), "name": p.stem,
               "spine": ver, "pngs": pngs, "anims": anims})

print("=== 三件齐全 ===", len(ok), "套")
grp = collections.Counter(o["dir"] for o in ok)
for g, n in sorted(grp.items()):
    ver = collections.Counter(o["spine"] for o in ok if o["dir"] == g)
    print("  %-46s %3d 套  %s" % (g, n, dict(ver)))
print()
print("=== 缺件 ===", len(bad), "套")
for p, why in bad:
    print("  %-52s %s" % (p.relative_to(LIVE).as_posix(), why))

(WEB / "spine_play" / "triples.json").write_text(
    json.dumps({"ok_count": len(ok), "ok": ok,
                "bad_count": len(bad),
                "bad": [{"path": p.relative_to(LIVE).as_posix(), "why": w} for p, w in bad]},
               ensure_ascii=False, indent=1), encoding="utf-8")
print("\n清单写出: spine_play/triples.json")
