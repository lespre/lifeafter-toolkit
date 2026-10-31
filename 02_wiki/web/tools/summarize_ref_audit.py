# -*- coding: utf-8 -*-
"""把 site_reference_audit.json 汇总成「可删候选 / 仅被工具引用 / 正常在用」。"""
import json
import pathlib

d = json.loads(
    pathlib.Path("E:/la拆包项目/01_索引与产物/30_分析/site_reference_audit.json").read_text(encoding="utf-8")
)
refs = d["page_refs"]
LIVE = ["wiki.html", "index.html", "board.html", "updates.html", "skin3d.html"]

print("页面总数", len(refs))

zero = [k for k, v in refs.items() if not v]
print(f"\n== 完全无引用（{len(zero)}）")
for k in zero:
    print("   ", k)

print("\n== 仅被脚本/旧页引用（页面之间没有入口）")
for k, v in refs.items():
    if not v:
        continue
    live_refs = [r for r in v if r.split("\\")[-1] in LIVE and r.split("\\")[-1] != k]
    if not live_refs:
        print(f"    {k:<28} ← {', '.join(x.split(chr(92))[-1] for x in v[:4])}")

print("\n== 被在线页面引用（保留）")
for k, v in refs.items():
    live_refs = [r for r in v if r.split("\\")[-1] in LIVE and r.split("\\")[-1] != k]
    if live_refs:
        print(f"    {k:<28} ← {', '.join(sorted(set(r.split(chr(92))[-1] for r in live_refs)))}")
