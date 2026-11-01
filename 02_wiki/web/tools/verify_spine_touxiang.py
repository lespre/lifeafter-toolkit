# -*- coding: utf-8 -*-
"""校验导出的 spine 三件套：每套是否严格同名一一对应，zip 是否完整。"""
import json, pathlib, zipfile, collections

OUT = pathlib.Path(r"E:/la拆包项目/01_索引与产物/交付/spine_三件套_头像")
zp = OUT.with_suffix(".zip")
man = json.loads((OUT / "清单.json").read_text(encoding="utf-8"))

bad = []
by = collections.defaultdict(list)
for f in OUT.rglob("*"):
    if f.is_file() and f.suffix in (".json", ".atlas", ".png") and f.name != "清单.json":
        by[(f.parent, f.stem)].append(f.suffix)

for (d, stem), sufs in sorted(by.items()):
    n_json = sufs.count(".json")
    n_atlas = sufs.count(".atlas")
    n_png = sufs.count(".png")
    if n_json != 1 or n_atlas != 1 or n_png < 1:
        bad.append((str(d.relative_to(OUT)), stem, sufs))

print("套数(按 目录+同名 计):", len(by))
print("不完整套:", len(bad))
for b in bad[:10]:
    print("  ", b)

z = zipfile.ZipFile(zp)
names = z.namelist()
print("zip 文件数:", len(names), "| 含 json:", sum(n.endswith('.json') for n in names),
      "| atlas:", sum(n.endswith('.atlas') for n in names),
      "| png:", sum(n.endswith('.png') for n in names))
print("zip 完整性:", z.testzip() or "OK")
print("清单声明:", man["count"], "套；缺件:", len(man["缺件"]))
for x in man["缺件"]:
    print("   缺件:", x["path"], "|", x["why"])

tot = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())
print("目录 %.1f MB / zip %.1f MB" % (tot / 1e6, zp.stat().st_size / 1e6))
