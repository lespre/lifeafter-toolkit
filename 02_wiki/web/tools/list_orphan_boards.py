import sys
# -*- coding: utf-8 -*-
"""列出未被 taxonomy / policy 引用的孤儿板块文件。"""
import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

W = pathlib.Path(WEB)
tax = json.loads((W / "data/wiki_taxonomy.json").read_text(encoding="utf-8"))
pol = json.loads((W / "data/publication_policy.json").read_text(encoding="utf-8"))

ref = set()
def walk(ns):
    for n in ns:
        for b in (n.get("boards") or []):
            ref.add(b)
        walk(n.get("children") or [])
walk(tax["树"])
ref |= set(pol["boards"].keys())

files = {p.stem for p in (W / "data/boards").glob("*.json") if not p.name.startswith("_")}
orph = sorted(files - ref)
common = files.intersection(ref)
print("板块文件 %d ｜ 被引用 %d ｜ 孤儿 %d" % (len(files), len(common), len(orph)))
total = 0.0
for o in orph:
    p = W / "data" / "boards" / (o + ".json")
    mb = p.stat().st_size / 1048576
    total += mb
    print("  %-40s %.1f MB" % (o, mb))
print("孤儿合计 %.1f MB" % total)
