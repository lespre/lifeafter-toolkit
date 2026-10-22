# -*- coding: utf-8 -*-
"""副标题来源三要素：还原树源 + 数据源（表） + 服务器类型。

输出 meta.source_label，例如：
  PE 还原树 pe_20261020 · com/cdata/drone_data · 简单生存（kj1）
  Documents 快照 script.py314 · com/cdata/common_item_data · 经典服
"""
import json
import pathlib
import re

WEB = pathlib.Path("E:/la拆包项目/02_wiki/web")
B = WEB / "data" / "boards"


def tree_of(prov, item, meta):
    blob = " ".join([
        str(prov.get("source_id") or ""),
        str(prov.get("table") or ""),
        str(item.get("source") or ""),
        str(meta.get("source_server") or ""),
    ]).lower()
    if "pe_2026" in blob or "pe 还原树" in blob or "perestore" in blob:
        return "PE 还原树 pe_20261020"
    if "documents" in blob or "py314" in blob:
        return "Documents 快照 script.py314"
    if "热更" in blob:
        return "测试服热更树"
    return ""


def table_of(prov, item):
    t = str(prov.get("table") or "")
    if t:
        t = t.replace("\\", "/")
        return t.split("/")[-1]
    src = str(item.get("source") or "")
    m = re.search(r"([a-z0-9_]+)\.py", src)
    return m.group(1) if m else ""


def server_of(item, meta):
    s = str(item.get("server") or "").strip()
    if s:
        return s
    raw = str(meta.get("source_server") or "")
    if "经典" in raw and "简单" in raw:
        return "经典服 + 简单生存服"
    if "经典" in raw:
        return "经典服"
    if "简单生存" in raw:
        return "简单生存服"
    return ""


rows = []
for p in sorted(B.glob("*.json")):
    d = json.loads(p.read_text(encoding="utf-8"))
    m = d.get("meta") or {}
    items = d.get("items") or []
    if not items:
        continue
    it = items[0]
    prov = it.get("provenance") or {}

    tree = tree_of(prov, it, m)
    table = table_of(prov, it)
    server = server_of(it, m)

    parts = [x for x in (tree, table, server) if x]
    if not parts:
        continue
    label = " · ".join(parts)
    if m.get("source_label") == label:
        continue
    m["source_label_prev"] = m.get("source_label")
    m["source_label"] = label
    d["meta"] = m
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    rows.append((p.stem, label))

for bid, label in rows:
    print("%-30s %s" % (bid, label))
print("更新", len(rows))
