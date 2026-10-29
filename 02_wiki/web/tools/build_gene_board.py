# -*- coding: utf-8 -*-
r"""潜能板增强：解析 gene_node_data 的四条序列。

节点结构（实测 race=4 冷却强化）：
  subsequence_attr_value  = 27 22 04 + 4×float64   → 每序列加成（0.04 ×4 = 16%）
  subsequence_unlock_levels = 27 01 04 + 4×uleb    → 每序列解锁等级
  subsequence_unlock_cost  = 27 0b 04 + 4×uleb     → 每序列消耗
  subsequence_unlock_value = 27 22 04 + 4×float64  → 每序列解锁进度（0.1）
"""
from __future__ import annotations

import datetime
import json
import pathlib
import struct
import sys


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
WEB = PROJ / "02_wiki/web"
OV = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata/oversea"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

RACE = {1: "通用", 2: "人类", 3: "再生者", 4: "械骨人"}


def parse_group(blob: bytes, off: int):
    """解析 0x27 组：返回 (类型字节, 值列表)。"""
    if blob[off] != 0x27:
        return None, []
    typ = blob[off + 1]
    n = blob[off + 2]
    pos = off + 3
    out = []
    for _ in range(n):
        if typ == 0x22:
            out.append(struct.unpack_from("<d", blob, pos)[0]); pos += 8
        elif typ == 0x01:
            v, pos = BT.uleb(blob, pos, len(blob)); out.append(v)
        elif typ == 0x0B:
            v, pos = BT.uleb(blob, pos, len(blob)); out.append(v)
        else:
            return typ, []
    return typ, out


def main() -> int:
    p = OV / "gene_node_data_auto_oversea_data_kj1.py"
    c = OV / "gene_node_data_auto_oversea_data_kj1_chs.py"
    b = p.read_bytes()
    at = b.find(b"x{")
    L = struct.unpack_from("<I", b, at + 2)[0]
    body = b[at + 6: at + 6 + L]
    cnt = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * cnt:]
    rows, _ = BT.decode_table_rows(body, BT.parse_legacy_chs_pool(c.read_bytes()), resolve_jumps=False)

    def g(r, k):
        v = r["values"].get(k)
        return (v[1] if isinstance(v, tuple) else v) if v else None

    out = []
    for r in rows:
        def grp(k):
            v = g(r, k)
            if isinstance(v, str) and v.startswith("jump:"):
                return parse_group(blob, int(v.split(":")[1]))[1]
            return []

        vals = grp("subsequence_attr_value")
        lvls = grp("subsequence_unlock_levels")
        costs = grp("subsequence_unlock_cost")
        race = g(r, "race")
        try:
            race = int(race)
        except Exception:
            race = 0
        out.append({
            "id": "gene_%s" % r["key"],
            "item_id": r["key"],
            "name": str(g(r, "node_name") or ""),
            "kind": "潜能节点",
            "race": race,
            "race_name": RACE.get(race, "未知"),
            "level": g(r, "level"),
            "node_score": g(r, "node_score"),
            "attr_name": str(g(r, "subsequence_attr_name") or ""),
            "seq_values": [round(v * 100, 2) for v in vals],
            "seq_total": round(sum(vals) * 100, 2) if vals else None,
            "seq_levels": lvls,
            "seq_costs": costs,
            "effect_desc": str(g(r, "effect_desc") or ""),
            "icon_path": str(g(r, "icon_path") or ""),
            "evidence": "structure", "evidence_level": "static/candidate",
            "status_tags": ["static config"],
            "source": "gene_node_data(kj1)",
            "provenance": {
                "source_id": "documents-py314-current",
                "source_lock_source_id": "documents-py314-current",
                "source_lock_sha256": "",
                "table": "gene_node_data(kj1)", "row_key": r["key"],
                "field_refs": ["node_name", "race", "subsequence_attr_value"],
                "locator_chain": {"chain_status": "replayed-structural", "scope": "record",
                                  "no_cross_source_field_join": True,
                                  "steps": [{"kind": "decoded-table-row",
                                             "source_id": "documents-py314-current",
                                             "table": "gene_node_data(kj1)", "row_key": r["key"],
                                             "field_refs": ["node_name", "race"]}]},
            },
        })

    lock = json.loads((WEB / "data/boards/lottery_periods.json").read_text(encoding="utf-8"))["meta"]["provenance"]["source_locks"][0]
    for it in out:
        it["provenance"]["source_lock_sha256"] = lock["sha256"]

    board = {"meta": {
        "name": "潜能强化总表", "category": "二、战力类 / （八）种族潜能",
        "source_server": "简单生存服（pe_20261020 还原树）",
        "generated": datetime.date.today().isoformat(),
        "id_label": "节点ID", "hide_media": True, "evidence": "structure",
        "card_mode": "roster",
        "card_summary": [["name", "潜能"], ["race_name", "种族"], ["seq_total", "合计加成"],
                         ["attr_name", "属性"]],
        "field_labels": {"item_id": "节点ID", "race_name": "种族", "seq_total": "合计加成%",
                         "attr_name": "属性键", "seq_values": "序列加成", "seq_levels": "序列解锁等级",
                         "seq_costs": "序列消耗", "node_score": "养成度", "effect_desc": "说明"},
        "filters": [{"key": "race_name", "label": "种族"}],
        "state_summary": {"条目": len(out)},
        "package_sha": lock["sha256"],
        "provenance": {"source_locks": [dict(lock)]},
        "notes": ("gene_node_data：每节点 4 条序列，序列加成相加即面板效果。"
                  "race 1=通用 2=人类 3=再生者 4=械骨人；半感染者不走潜能表。"),
    }, "periods": [], "items": out}
    (WEB / "data/boards/gene_potential_catalog.json").write_text(
        json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/gene_potential_catalog.js").write_text(
        "window.WIKI_BOARD_gene_potential_catalog = " + json.dumps(board, ensure_ascii=False, indent=1) + ";",
        encoding="utf-8")
    print("潜能节点", len(out))
    for it in out:
        if it["attr_name"] == "coolant_recovery_rate":
            print("  样例", it["name"], it["seq_values"], "合计", it["seq_total"], "解锁", it["seq_levels"])
            break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
