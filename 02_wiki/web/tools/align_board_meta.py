import sys
# -*- coding: utf-8 -*-
"""把每个板块的 meta.category 对齐到 taxonomy（序号/名称唯一口径）。"""
import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

DATA = WEB / "data"

tax = json.loads((DATA / "wiki_taxonomy.json").read_text(encoding="utf-8"))
path_of = {}
for top in tax["树"]:
    for b in top.get("boards", []):
        path_of[b] = top["name"]
    for leaf in top.get("children", []):
        for b in leaf.get("boards", []):
            path_of[b] = "%s / %s" % (top["name"], leaf["name"])

fixed, skipped = 0, []
for bid, cat in path_of.items():
    p = DATA / "boards" / ("%s.json" % bid)
    if not p.exists():
        skipped.append(bid)
        continue
    d = json.loads(p.read_text(encoding="utf-8"))
    meta = d.setdefault("meta", {})
    if meta.get("category") != cat:
        meta["category"] = cat
        p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        fixed += 1

print("对齐", fixed, "个板块的 meta.category")
print("缺文件", skipped or "无")
