# -*- coding: utf-8 -*-
"""从 ITEM_MASTER_v03.jsonl 还原道具总表板（item_id / name / provenance）。

用途：v0.3 板的构建脚本依赖 analysis/audit/*.json 中间产物（未入库），
新设备上只能用 jsonl 直接还原。条目数 30,252（v0.3 快照）。
"""
import json
import pathlib

WEB = pathlib.Path(__file__).resolve().parents[1]
SRC = pathlib.Path("E:/la拆包项目/01_索引与产物/10_索引/site_data/ITEM_MASTER_v03.jsonl")
OUT = WEB / "data/boards/item_master_full.json"

items = []
with SRC.open(encoding="utf-8") as fh:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        iid = r.get("item_id") or r.get("raw_row_key")
        name = r.get("name")
        if iid is None:
            continue
        prov = r.get("provenance") or {}
        items.append({
            "id": "item_%s" % iid,
            "item_id": iid,
            "name": name or "",
            "namespace": r.get("item_namespace"),
            "identity_state": r.get("identity_state"),
            "name_status": r.get("name_status"),
            "provenance": prov,
            "evidence": "structure",
            "evidence_level": "static/candidate",
            "source": "ITEM_MASTER_v03.jsonl（common_item_data 族聚合）",
            "status_tags": ["static config"],
        })

doc = {
    "meta": {
        "name": "全量道具总表",
        "category": "四、综合资料 / （二）全量道具总表",
        "source_server": "测试服 · ITEM_MASTER v0.3 快照",
        "source_label": "测试服 · Documents 快照 · ITEM_MASTER_v03",
        "generated": "2026-10-23",
        "evidence": "structure",
        "count": len(items),
        "notes": "由 ITEM_MASTER_v03.jsonl 还原（v0.3 构建脚本依赖的 audit 中间产物未入库）",
    },
    "items": items,
}
OUT.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
print("写出", OUT.name, len(items), "条")
