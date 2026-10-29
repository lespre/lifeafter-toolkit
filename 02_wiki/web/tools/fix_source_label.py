import sys
# -*- coding: utf-8 -*-
"""副标题来源归一：把 meta.source_server 的长句压成可核对的口径，写进 meta.source_label。

保留原值不动（source_server 原文仍在），只新增展示用 label：
  含 script        → 测试服 · script 表结构解析
  含 Document(s)   → 测试服 · Documents 快照
  含 pe_2026 / PE  → 测试服 · PE 还原树
  含 热更树        → 测试服 · 热更树
  含 toolkit_core  → 本项目工具生成
  其余             → 原值原样（不猜）
"""
import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

B = WEB / "data" / "boards"

RULES = [
    ("script", "测试服 · script 表结构解析"),
    ("document", "测试服 · Documents 快照"),
    ("pe_2026", "测试服 · PE 还原树"),
    ("pe 测试服", "测试服 · PE 还原树"),
    ("热更树", "测试服 · 热更树"),
    ("toolkit_core", "本项目工具生成"),
    ("快照", "测试服 · 客户端快照"),
]

changed = []
for p in sorted(B.glob("*.json")):
    d = json.loads(p.read_text(encoding="utf-8"))
    m = d.get("meta")
    if not isinstance(m, dict):
        continue
    src = str(m.get("source_server") or "").strip()
    if not src:
        m["source_label"] = "未记录"
    else:
        low = src.lower()
        label = next((lab for key, lab in RULES if key in low), src)
        m["source_label"] = label
    if m.get("source_label") != src:
        changed.append((p.stem, src[:34], m["source_label"]))
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")

for bid, old, new in changed:
    print("%-30s %-34s → %s" % (bid, old, new))
print("归一板块", len(changed))
