# -*- coding: utf-8 -*-
"""副标题来源三要素（v2）：还原树源 · 数据源表 · 服务器类型。

优先级：meta.source_server 原文里的树名/服型 > item.provenance > item.source
"""
import json
import pathlib
import re

WEB = pathlib.Path("E:/la拆包项目/02_wiki/web")
B = WEB / "data" / "boards"


def tree_of(meta, prov, item):
    raw = " ".join([str(meta.get("source_server") or ""), str(item.get("source") or "")])
    m = re.search(r"pe_[a-z0-9_]+", raw, re.I)
    if m:
        return "PE 还原树 %s" % m.group(0)
    if "documents" in raw.lower() or "py314" in raw.lower():
        return "Documents 快照 script.py314"
    if "热更树" in raw:
        return "测试服热更树"
    sid = str(prov.get("source_id") or "").lower()
    if "documents" in sid:
        return "Documents 快照 script.py314"
    return ""


def table_of(prov, item):
    t = str(prov.get("table") or "")
    if t:
        return t.replace("\\", "/").split("/")[-1].removesuffix(".py")
    m = re.search(r"([a-z0-9_]+)\.py", str(item.get("source") or ""))
    return m.group(1) if m else ""


def server_of(meta, item):
    raw = " ".join([str(meta.get("source_server") or ""), str(item.get("server") or "")])
    s = str(item.get("server") or "").strip()
    parts = []
    if "经典" in raw or "经典" in s:
        parts.append("经典服")
    if "简单生存" in raw or "简单生存" in s or "kj1" in raw:
        parts.append("简单生存服")
    if not parts:
        if "正式服" in raw:
            parts.append("正式服")
        elif "体验" in raw or "测试" in raw:
            parts.append("测试服")
    return " + ".join(dict.fromkeys(parts))


OVERRIDE = {
    "drone_catalog": "PE 还原树 pe_20261020 · all_equips_data（kj1） · 简单生存服",
    "mutation_core_full": "PE 还原树 pe_20261020 · common_item_data · 经典服",
    "item_master_full": "PE 还原树 pe_20261020（pe_test_script） · all_equips_data（kj1） · 简单生存服",
    "fashion_wardrobe": "PE 还原树 pe_20261020 · fashion_data · 测试服",
}

rows = []
for p in sorted(B.glob("*.json")):
    d = json.loads(p.read_text(encoding="utf-8"))
    m = d.get("meta") or {}
    items = d.get("items") or []
    if not items:
        continue
    it = items[0]
    prov = it.get("provenance") or {}

    if p.stem in OVERRIDE:
        m["source_label"] = OVERRIDE[p.stem]
        d["meta"] = m
        p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        rows.append((p.stem, OVERRIDE[p.stem]))
        continue
    tree = tree_of(m, prov, it)
    table = table_of(prov, it)
    server = server_of(m, it)
    parts = [x for x in (tree, table, server) if x]
    if len(parts) < 2:
        continue
    label = " · ".join(parts)
    if m.get("source_label") == label:
        continue
    m.setdefault("source_label_prev", m.get("source_label"))
    m["source_label"] = label
    d["meta"] = m
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    rows.append((p.stem, label))

for bid, label in rows:
    print("%-30s %s" % (bid, label))
print("更新", len(rows))
