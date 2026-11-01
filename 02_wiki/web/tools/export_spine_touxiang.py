# -*- coding: utf-8 -*-
"""导出 spine「头像」系列三件套（json + atlas + png，严格同名一一对应）。

源：02_wiki/web/assets/spine_live/ui/**/touxiang/*.json
出：01_索引与产物/交付/spine_三件套_头像/
"""
import json, glob, pathlib, shutil, collections, zipfile

WEB = pathlib.Path(r"E:/la拆包项目/02_wiki/web")
LIVE = WEB / "assets/spine_live/ui"
OUT = pathlib.Path(r"E:/la拆包项目/01_索引与产物/交付/spine_三件套_头像")
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

ok, bad = [], []
for jf in sorted(glob.glob(str(LIVE / "**/touxiang/*.json"), recursive=True)):
    p = pathlib.Path(jf)
    atlas = p.with_suffix(".atlas")
    if not atlas.is_file():
        bad.append((p, "缺同名 atlas")); continue
    pngs = []
    for ln in atlas.read_text(encoding="utf-8", errors="replace").splitlines():
        ln = ln.strip()
        if ln.lower().endswith(".png"):
            pngs.append(ln)
        if ln.startswith("size:"):
            break
    if not pngs:
        bad.append((p, "atlas 无 png 页名")); continue
    wrong = [x for x in pngs if pathlib.Path(x).stem != p.stem
             and not pathlib.Path(x).stem.startswith(p.stem + "_")]
    if wrong:
        bad.append((p, "页名不同名: " + ", ".join(wrong))); continue
    missing = [x for x in pngs if not (p.parent / x).is_file()]
    if missing:
        bad.append((p, "缺 png: " + ", ".join(missing))); continue
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        ver = str((d.get("skeleton") or {}).get("spine"))
        anims = list((d.get("animations") or {}).keys())
    except Exception as e:
        bad.append((p, "json 解析失败")); continue
    ok.append({"name": p.stem, "src": p.parent, "ver": ver, "pngs": pngs, "anims": anims})

print("三件齐全:", len(ok), "套")
print("缺件:", len(bad), "套")
for p, w in bad:
    print("   缺件", p.relative_to(LIVE).as_posix(), "|", w)

# 按版本分目录拷出（同名三件放同一目录，可直接拖进 Spine 编辑器）
rows = []
for it in ok:
    sub = OUT / it["ver"].replace(".", "_")
    sub.mkdir(exist_ok=True)
    for f in [it["src"] / (it["name"] + ".json"), it["src"] / (it["name"] + ".atlas")] + \
             [it["src"] / x for x in it["pngs"]]:
        shutil.copy2(f, sub / f.name)
    rows.append({"name": it["name"], "version": it["ver"], "files": [it["name"] + ".json",
                it["name"] + ".atlas"] + it["pngs"], "anims": it["anims"]})

(OUT / "清单.json").write_text(json.dumps({"count": len(rows), "items": rows,
                                           "缺件": [{"path": p.relative_to(LIVE).as_posix(), "why": w}
                                                  for p, w in bad]},
                                          ensure_ascii=False, indent=1), encoding="utf-8")

# 打 zip
zp = OUT.with_suffix(".zip")
if zp.exists():
    zp.unlink()
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for f in sorted(OUT.rglob("*")):
        if f.is_file():
            z.write(f, f.relative_to(OUT).as_posix())
print("输出目录:", OUT)
print("zip:", zp.name, "%.1f MB" % (zp.stat().st_size / 1e6))
ver_cnt = collections.Counter(r["version"] for r in rows)
print("版本分布:", dict(ver_cnt))
