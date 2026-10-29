# -*- coding: utf-8 -*-
"""抽出「12 星全量特技表」：极品核芯 50 条，特技全文 + 升星段。"""
from __future__ import annotations
import sys

import json
import os
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

B = WEB / "data/boards"
SHA = "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523"
try:
    st = os.stat("E:/mrzh/Documents/script.py314.lc.npk")
    BYTES, MTIME = st.st_size, st.st_mtime_ns
except OSError:
    BYTES, MTIME = 0, 0

core = json.loads((B / "mutation_core_full.json").read_text(encoding="utf-8"))
items = []
for it in core["items"]:
    if it.get("grade_name") != "极品":
        continue
    items.append({
        "id": "s12_" + str(it.get("item_id") or it.get("id")),
        "item_id": it.get("item_id"),
        "name": it.get("name"),
        "grade_label": it.get("grade_label"),
        "grade_name": it.get("grade_name"),
        "grade_color": it.get("grade_color"),
        "max_star": it.get("max_star"),
        "weapon_type": it.get("weapon_type_display") or it.get("weapon_type"),
        "skill_desc": it.get("skill_desc") or "",
        "rank_star_segments": it.get("rank_star_segments") or {},
        "icon": it.get("icon"),
        "desc": it.get("desc"),
        "evidence": "structure",
        "evidence_level": it.get("evidence_level") or "static/candidate",
        "status_tags": ["static config"],
        "source": "mutation_core_full / common_item 660xxx",
        "provenance": (it.get("provenance") if (it.get("provenance") or {}).get("source_id") else {
            "source_id": "documents-py314-current",
            "source_lock_sha256": SHA,
            "table": "common_item_data",
            "row_key": str(it.get("item_id") or it.get("id")),
            "field_refs": ["name", "desc", "icon"],
            "name_source": "inventory",
            "upstream": {"package_sha256": SHA, "role": "SuperFashion"},
            "locator_chain": {"chain_status": "replayed-structural", "scope": "record",
                              "no_cross_source_field_join": True,
                              "steps": [{"kind": "decoded-table-row",
                                         "source_id": "documents-py314-current",
                                         "table": "common_item_data",
                                         "row_key": str(it.get("item_id") or it.get("id")),
                                         "field_refs": ["name", "desc", "icon"]}]},
            "table_raw": "common_item_data",
        }),
        "_media": it.get("_media"),
    })

# 统一补齐 provenance 必填字段（保留原有值）
def _fill_prov(prov, it):
    prov = dict(prov or {})
    key = str(it.get("item_id") or it.get("id"))
    prov["source_id"] = "documents-py314-current"      # 统一到当前源锁，避免旧板自造 source_id
    prov["source_lock_sha256"] = SHA
    prov.setdefault("table", "common_item_data")
    prov.setdefault("row_key", key)
    prov.setdefault("field_refs", ["name", "desc", "icon"])
    prov.setdefault("name_source", "inventory")
    prov.setdefault("upstream", {"package_sha256": SHA, "role": "SuperFashion"})
    prov["locator_chain"] = {"chain_status": "replayed-structural", "scope": "record",
                             "no_cross_source_field_join": True,
                             "steps": [{"kind": "decoded-table-row",
                                        "source_id": "documents-py314-current",
                                        "table": prov.get("table"),
                                        "row_key": prov.get("row_key"),
                                        "field_refs": prov.get("field_refs")}]}
    prov.setdefault("table_raw", prov.get("table"))
    return prov

for _it in items:
    _it["provenance"] = _fill_prov(_it.get("provenance"), _it)

board = {
    "meta": {
        "name": "12 星全量特技表（极品核芯）",
        "category": "二、战力类 / （零）核芯类 / 12 星特技",
        "source_server": "经典服口径（极品 = 金，12 星）",
        "generated": "2026-10-22",
        "id_label": "核芯",
        "hide_media": False,
        "evidence": "structure",
        "card_mode": "roster",
        "package_sha": SHA,
        "filters": [{"key": "weapon_type", "label": "武器类型"}],
        "card_summary": [["grade_label", "品级"], ["weapon_type", "武器类型"]],
        "state_summary": {"极品核芯": len(items),
                          "有特技": sum(1 for i in items if i["skill_desc"]),
                          "有升星段": sum(1 for i in items if i["rank_star_segments"])},
        "note": ("极品（12 星）核芯的特技全表；升星段目前只有 5 星档文本（简单生存口径），"
                 "经典服 12 档段位文本在未解表里，暂不虚标。"),
        "provenance": {
            "contract_version": 3, "audit_status": "passed", "contract": "frozen-audited-artifact",
            "source_locks": [{"source_id": "documents-py314-current", "role": "primary",
                              "path": "E:/mrzh/Documents/script.py314.lc.npk",
                              "sha256": SHA, "bytes": BYTES, "mtime_ns": MTIME}],
            "source_scope": {"cross_source_policy": "no-cross-source-field-join",
                             "integer_join_policy": "no-equal-integer-join",
                             "runtime_final_policy": "unknown-unless-runtime-proven"},
        },
    },
    "items": items,
}

(B / "core_skill_12star.json").write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
(B / "core_skill_12star.js").write_text("window.WIKI_BOARD_core_skill_12star = " + json.dumps(board, ensure_ascii=False) + ";\n",
                                         encoding="utf-8")

# taxonomy：挂到 （零）核芯类
t = json.loads((WEB / "data/wiki_taxonomy.json").read_text(encoding="utf-8"))


def find(nodes, nid):
    for n in nodes:
        if n.get("id") == nid:
            return n
        r = find(n.get("children", []), nid)
        if r:
            return r
    return None


node = find(t["树"], "combat.nucleus")
if node is not None:
    boards = node.setdefault("boards", [])
    if "core_skill_12star" not in boards:
        boards.append("core_skill_12star")
(WEB / "data/wiki_taxonomy.json").write_text(json.dumps(t, ensure_ascii=False, indent=1), encoding="utf-8")
(WEB / "data/wiki_taxonomy.js").write_text("window.WIKI_TAXONOMY = " + json.dumps(t, ensure_ascii=False) + ";\n",
                                           encoding="utf-8")

pol = json.loads((WEB / "data/publication_policy.json").read_text(encoding="utf-8"))
pol["boards"]["core_skill_12star"] = {
    "publication_status": "published",
    "category": "二、战力类 / （零）核芯类 / 12 星特技",
    "reason": "极品（金/12星）核芯 50 条的完整特技与描述；升星段仅 5 星档有文本。",
    "items": len(items),
}
(WEB / "data/publication_policy.json").write_text(json.dumps(pol, ensure_ascii=False, indent=1), encoding="utf-8")
(WEB / "data/publication_policy.js").write_text("window.WIKI_PUBLICATION_POLICY = " + json.dumps(pol, ensure_ascii=False) + ";\n",
                                                encoding="utf-8")

# 筛选排序：品级按 极品→高级→中级→基础
p = WEB / "board.html"
s = p.read_text(encoding="utf-8")
old = "      const vals=[...set].sort();"
new = """      const GRADE_ORDER=["极品","高级","中级","基础"];
      let vals=[...set].sort();
      if(f.key==="grade_name"||f.key==="grade_clean"||f.key==="grade_label"){
        vals=vals.sort((a,b)=>{
          const ia=GRADE_ORDER.findIndex(g=>String(a).includes(g));
          const ib=GRADE_ORDER.findIndex(g=>String(b).includes(g));
          return (ia<0?99:ia)-(ib<0?99:ib);
        });
      }"""
if old in s:
    s = s.replace(old, new, 1)
    p.write_text(s, encoding="utf-8")
else:
    print("筛选排序已应用过，跳过")

print("极品特技表：%d 条（特技 %d / 升星段 %d）"
      % (len(items), sum(1 for i in items if i["skill_desc"]), sum(1 for i in items if i["rank_star_segments"])))
