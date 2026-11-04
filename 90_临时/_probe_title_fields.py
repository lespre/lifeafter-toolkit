# -*- coding: utf-8 -*-
"""看 title_conf_data 的所有字段（找颜色/描边字段）。"""
import pathlib
import sys

PROJ = pathlib.Path(r"E:\la拆包项目")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
import build_text_boards as B  # noqa: E402

rows = B.decode("title_conf_data")
print("行数", len(rows))
keys = sorted({k for r in rows for k in r["values"]})
print("字段:", keys)
for r in rows[:2]:
    print("---")
    for k in keys:
        v = r["values"].get(k)
        print("  ", k, "=", (v[1] if isinstance(v, tuple) else v))
