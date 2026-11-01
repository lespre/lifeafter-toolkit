# -*- coding: utf-8 -*-
"""对比还原树里的名片框资源与 catalog 引用：是否有新资源未被收录。"""
import json, pathlib, re, collections, time

PROJ = pathlib.Path(r"e:\la拆包项目")
TREE = PROJ / "01_索引与产物/41_还原树/pe/资源"
WEB = PROJ / "02_wiki/web"
cat = json.loads((WEB / "data/boards/avatar_catalog.json").read_text(encoding="utf-8"))
cards = [it for it in cat["items"] if it.get("kind") == "名片框"]

ref_frame = set()
ref_bg = set()
for it in cards:
    ip = (it.get("image_path") or "").replace("\\", "/")
    rp = (it.get("resource_path") or "").replace("\\", "/")
    if ip:
        ref_frame.add(ip.rsplit(".", 1)[0])
    if rp:
        ref_bg.add(rp.rsplit(".", 1)[0])

root = TREE / "ui/mingpiankuang_icon"
print("还原树目录存在:", root.is_dir())
allf = []
if root.is_dir():
    for p in root.rglob("*"):
        if p.is_file():
            allf.append(p)

def logical(p):
    return p.relative_to(TREE).as_posix().rsplit(".", 1)[0]

by_stem = collections.Counter()
for p in allf:
    by_stem[logical(p)] += 1

fr = [s for s in by_stem if re.search(r"img_biankuang_(?!b_)[^/]*$", s)]
bg = [s for s in by_stem if re.search(r"img_biankuang_b_", s)]
other = [s for s in by_stem if s not in fr and s not in bg]
print("树里 img_biankuang_*（非b）: %d ｜ img_biankuang_b_*: %d ｜ 其它: %d ｜ 文件总数 %d" %
      (len(fr), len(bg), len(other), len(allf)))

new_fr = sorted(set(fr) - ref_frame)
new_bg = sorted(set(bg) - ref_bg)
print("\n[catalog 未引用] 边框候选 %d:" % len(new_fr))
for s in new_fr[:25]:
    print("   ", s)
print("[catalog 未引用] 背景候选 %d:" % len(new_bg))
for s in new_bg[:25]:
    print("   ", s)

print("\n树里其它文件（前 20）:")
for s in sorted(other)[:20]:
    print("   ", s)

print("\n最近修改的 8 个文件:")
for p in sorted(allf, key=lambda x: x.stat().st_mtime)[-8:]:
    print("   ", time.strftime("%Y-%m-%d %H:%M", time.localtime(p.stat().st_mtime)),
          p.relative_to(TREE).as_posix())
