import sys
# -*- coding: utf-8 -*-
"""抽样审计：每个已发布板块能否在新设备全量拆包后重建。

判据：
  A 有构建脚本（文件名或内容里出现该 board，且写了 boards/<id>.json）
  B 脚本输入来自还原树（含 41_还原树 / pe_20261020 / com/cdata）
  C 脚本不依赖本地临时目录（cache/scratch、Documents 绝对路径）
"""
import json
import pathlib
import re

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

DATA = WEB / "data"
TOOLS = WEB / "tools"

boards = [b["board"] for b in json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))["boards"]]
scripts = {p.name: p.read_text(encoding="utf-8", errors="ignore") for p in TOOLS.glob("*.py")}

rows = []
for b in boards:
    cands = []
    for name, txt in scripts.items():
        if b not in txt and ("%s.json" % b) not in txt:
            continue
        if not re.search(r"build|rebuild|export|aggregate|backfill", name):
            continue
        cands.append(name)
    if not cands:
        rows.append((b, "", "-", "-", "无脚本"))
        continue
    name = cands[0]
    txt = scripts[name]
    tree = bool(re.search(r"41_还原树|pe_20261020|com/cdata|com\\\\cdata", txt))
    local = bool(re.search(r"cache/scratch|AppData|Documents/", txt))
    ok = tree and not local
    rows.append((b, name, "是" if tree else "否", "是" if local else "否",
                 "可重建" if ok else ("需人工" if tree or not local else "依赖本地")))

print("%-32s %-34s %-6s %-6s %s" % ("board", "脚本", "读树", "本地依赖", "结论"))
for r in rows:
    print("%-32s %-34s %-6s %-6s %s" % r)
bad = [r[0] for r in rows if r[4] != "可重建"]
print("\n不可直接重建:", bad or "无")
