# -*- coding: utf-8 -*-
r"""交付总账：**按盘上实际内容**重算 inventory（bundle 那份是中途生成的，会带「产物缺失」虚数）。

用法：交付总账.py <交付根>
产物：<交付根>/04_变更清单与报告总结/inventory.json（覆盖）+ 交付总账.json（含二级细分）
"""
from __future__ import annotations

import collections
import json
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
OUT = ROOT / "04_变更清单与报告总结"
OUT.mkdir(parents=True, exist_ok=True)

by_top = collections.Counter()
bytes_top = collections.Counter()
by_ext = collections.Counter()
bytes_ext = collections.Counter()
by_sub = collections.Counter()
bytes_sub = collections.Counter()
total = 0
total_bytes = 0

for p in ROOT.rglob("*"):
    if not p.is_file():
        continue
    if p.parts[-2:] == ("04_变更清单与报告总结", p.name) and p.suffix == ".json":
        continue
    rel = p.relative_to(ROOT)
    parts = rel.parts
    top = parts[0] if len(parts) > 1 else "(根文件)"
    sub = "/".join(parts[1:3]) if len(parts) > 2 else (parts[1] if len(parts) > 1 else "")
    sz = p.stat().st_size
    by_top[top] += 1
    bytes_top[top] += sz
    ext = p.suffix.lower().lstrip(".") or "(无扩展名)"
    by_ext[ext] += 1
    bytes_ext[ext] += sz
    key = "%s/%s" % (top, sub) if sub else top
    by_sub[key] += 1
    bytes_sub[key] += sz
    total += 1
    total_bytes += sz

def rows(counter, bcounter, n=None):
    items = sorted(counter.items(), key=lambda kv: -bcounter[kv[0]])
    return [{"键": k, "文件数": v, "字节": bcounter[k]} for k, v in (items[:n] if n else items)]

inv = {"说明": "按交付目录【盘上实际内容】统计（覆盖 bundle 中途生成的那份）",
       "root": str(ROOT), "total_files": total, "total_bytes": total_bytes,
       "by_top_dir": rows(by_top, bytes_top), "by_ext": rows(by_ext, bytes_ext, 25)}
(OUT / "inventory.json").write_text(json.dumps(inv, ensure_ascii=False, indent=1), encoding="utf-8")
(OUT / "交付总账.json").write_text(json.dumps(
    {**inv, "by_sub_dir": rows(by_sub, bytes_sub, 60)}, ensure_ascii=False, indent=1), encoding="utf-8")

print("交付根：%s" % ROOT)
print("合计 %d 文件 ｜ %.2f GB" % (total, total_bytes / 1024 ** 3))
print("\n顶层：")
for r in inv["by_top_dir"]:
    print("   %-22s %7d 文件  %8.2f GB" % (r["键"], r["文件数"], r["字节"] / 1024 ** 3))
print("\n二级（前 20）：")
for r in rows(by_sub, bytes_sub, 20):
    print("   %-46s %7d 文件  %8.2f GB" % (r["键"], r["文件数"], r["字节"] / 1024 ** 3))
print("\n扩展名（前 12）：")
for r in rows(by_ext, bytes_ext, 12):
    print("   %-18s %7d 文件" % (r["键"], r["文件数"]))
print("\n产物 → %s" % (OUT / "inventory.json"))
