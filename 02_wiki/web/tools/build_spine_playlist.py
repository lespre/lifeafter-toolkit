# -*- coding: utf-8 -*-
"""扫 spine_live 下所有 3.8.99 骨架，生成网页播放器清单。

输出: 02_wiki/web/spine_play/list.json
"""
import json, glob, pathlib, collections, shutil

WEB = pathlib.Path(r"E:/la拆包项目/02_wiki/web")
LIVE = WEB / "assets/spine_live/ui"
OUT = WEB / "spine_play"
RT = pathlib.Path(r"E:/la拆包项目/00_规范与工具/环境/spine-player/3.8")

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "runtime").mkdir(exist_ok=True)
for f in ("spine-core-3.8.js", "spine-webgl-3.8.js"):
    shutil.copy2(RT / f, OUT / "runtime" / f)

items = []
stats = collections.Counter()
for jf in sorted(glob.glob(str(LIVE / "**/*.json"), recursive=True)):
    p = pathlib.Path(jf)
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        stats["bad_json"] += 1
        continue
    sk = d.get("skeleton") or {}
    ver = str(sk.get("spine"))
    stats[ver] += 1
    if ver != "3.8.99":
        continue
    atlas = p.with_suffix(".atlas")
    if not atlas.is_file():
        stats["no_atlas"] += 1
        continue
    anims = list((d.get("animations") or {}).keys())
    if not anims:
        stats["no_anim"] += 1
        continue
    # 贴图页名（atlas 里第一段的 png 名），用于缩略图
    pngs = []
    for ln in atlas.read_text(encoding="utf-8", errors="replace").splitlines():
        ln = ln.strip()
        if ln.lower().endswith(".png"):
            pngs.append(ln)
        if ln.startswith("size:"):
            break
    # ★ atlas 引用的贴图页必须都在，否则运行时 atlas 加载失败（实测 img_biankuang_76.png 就是 404）
    missing = [x for x in pngs if not (p.parent / x).is_file()]
    if not pngs or missing:
        stats["missing_png"] += 1
        continue
    rel = p.relative_to(WEB).as_posix()
    items.append({
        "name": p.stem,
        "group": p.parent.name,
        "json": "../" + rel,
        "atlas": "../" + p.with_suffix(".atlas").relative_to(WEB).as_posix(),
        "png": ("../" + (p.parent / pngs[0]).relative_to(WEB).as_posix()) if pngs else None,
        "anims": anims[:6],
        "wh": [sk.get("width"), sk.get("height")],
    })

(OUT / "list.json").write_text(json.dumps({"count": len(items), "items": items},
                                          ensure_ascii=False, indent=1), encoding="utf-8")
print("3.8.99 可播:", len(items))
print("版本统计:", dict(stats))
grp = collections.Counter(i["group"] for i in items)
print("分组:", dict(grp))
