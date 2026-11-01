# -*- coding: utf-8 -*-
"""探查称号源表 title_conf_data 里与稀有度/颜色/动态相关的字段。只读。"""
import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, "02_wiki/web/tools")
import build_text_boards as B

rows = B.decode("title_conf_data")
print("rows", len(rows))
r = rows[0]
print("row keys:", sorted(r.keys()))
print("values keys:", sorted(r["values"].keys()))
# 找到目标称号
hits = [x for x in rows if "炽海天姿" in str(B.g(x, "name") or "")]
print("hit", len(hits))
for x in hits[:5]:
    print(json.dumps({k: (v[1] if isinstance(v, tuple) else v) for k, v in x["values"].items()}, ensure_ascii=False, indent=1))
