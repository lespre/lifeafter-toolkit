# -*- coding: utf-8 -*-
"""manifest 的分类路径按 taxonomy 重算（taxonomy 是唯一口径）。"""
import json
import pathlib

DATA = pathlib.Path(r"E:/la拆包项目/02_wiki/web/data")
tax = json.loads((DATA / "wiki_taxonomy.json").read_text(encoding="utf-8"))

path_of = {}
for top in tax["树"]:
    for leaf in top.get("children", []):
        for b in leaf.get("boards", []):
            path_of[b] = "%s / %s" % (top["name"], leaf["name"])

man = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
changed = 0
for b in man.get("boards", []):
    new = path_of.get(b["board"])
    if new and b.get("category") != new:
        b["category"] = new
        changed += 1

(DATA / "manifest.json").write_text(
    json.dumps(man, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
(DATA / "manifest.js").write_text(
    "window.WIKI_MANIFEST = " + json.dumps(man, ensure_ascii=False) + ";\n", encoding="utf-8")

missing = sorted(set(b["board"] for b in man["boards"]) - set(path_of))
print("manifest 分类已按 taxonomy 重算：改动 %d 条" % changed)
print("未进 taxonomy 的板块：", missing or "无")
