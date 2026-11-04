#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""时装衣柜 · 增量对齐 PE 活树（不重建、只补新与刷新）。

为什么不是「全量重建」：现有 3,150 张卡是长期多源拼装的结果
（fashion_data 前缀族 821 组 + 名称族 1,153 组 + appear 151 组 + 捏脸/投影/戒指/花苞等），
单一规则复现不出 3,150（实测最多 2,125）。硬重建会把板冲小，所以走增量：

  · 活树里出现、但板上任何卡都没收过的 row_key → 新建卡（骨架，富化字段留空）
  · 已收过的 row_key → 只刷新 name / row_keys / grade / charm，不动媒体与描述
  · 绝不删除既有卡
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
sys.path.insert(0, str(WEB / "tools"))
import rebuild_lottery_periods as R  # noqa: E402
from board_io import write_board_pair  # noqa: E402

BOARD = WEB / "data/boards/fashion_wardrobe.json"
DUR = re.compile(r"[-_－]\d+\s*天$")
PREFIX_PART = {"hat": "头饰", "cloth": "衣服", "bag": "背包", "light": "荧光棒", "suit": "整套"}
APPLY = "--apply" in sys.argv


def main() -> int:
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    items = board["items"]
    fd0 = R._opt_table(R.TREE / "fashion_data.py", R.TREE / "fashion_data_chs.py")

    def group_key(row_key: int):
        row = fd0.by_key.get(row_key)
        if not row:
            return None
        v = row["values"]
        s_ = str(v.get("new_fashion_id_str") or "")
        if s_:
            p_ = s_.split("_")
            return ("p", p_[0], p_[1] if len(p_) > 1 else "", p_[2] if len(p_) > 2 else "")
        nm = DUR.sub("", str(v.get("name") or v.get("show_name") or "").strip())
        return ("n", str(v.get("part_type") or ""), nm, "")

    covered: set[int] = set()
    card_of_group: dict[tuple, dict] = {}
    for it in items:
        for k in (it.get("row_keys") or []):
            try:
                ik = int(k)
            except Exception:
                continue
            covered.add(ik)
            gk = group_key(ik)
            if gk:
                card_of_group.setdefault(gk, it)
    print("现有卡片", len(items), "覆盖 row_key", len(covered), "| 分组键", len(card_of_group))

    fd = R._opt_table(R.TREE / "fashion_data.py", R.TREE / "fashion_data_chs.py")
    ap = R._opt_table(R.TREE / "player_module_appear_data.py", R.TREE / "player_module_appear_data_chs.py")

    added, refreshed = [], 0
    for key, row in fd.by_key.items():
        v = row["values"]
        s = str(v.get("new_fashion_id_str") or "")
        part = PREFIX_PART.get(s.split("_")[0]) if s else None
        if part is None:
            pt = str(v.get("part_type") or "")
            part = PREFIX_PART.get(pt) or {"bag": "背包"}.get(pt)
        name = DUR.sub("", str(v.get("name") or v.get("show_name") or "").strip())
        if not part or not name:
            continue
        gk = group_key(key)
        if key in covered:
            continue
        if gk and gk in card_of_group:
            # 同组已有卡 → 只把这条行权收进该卡（限时变体等），不新建
            card = card_of_group[gk]
            card.setdefault("row_keys", []).append(key)
            card["row_keys"] = sorted(set(card["row_keys"]))
            covered.add(key)
            refreshed += 1
            continue
        part_v = part
        items.append({
            "id": "fw_" + hashlib.md5(f"{key}:{part_v}".encode()).hexdigest()[:10],
            "name": name,
            "evidence": "structure",
            "evidence_level": "structure-only",
            "source": "PE 活树 fashion_data 增量对齐",
            "tables": ["fashion_data.py"],
            "row_keys": [key],
            "part": part_v,
            "part_label": part_v,
            "part_bucket": [part_v],
            "part_source": "new_fashion_id_str 前缀 / part_type",
            "model_id": v.get("model_id"),
            "model_ids": [v["model_id"]] if isinstance(v.get("model_id"), int) else [],
            "grade_level": v.get("level"),
            "charm_value": v.get("charm_value"),
            "desc": v.get("desc"),
            "status_tags": ["static config", "unverified"],
            "provenance": {
                "source_id": "pe-live-tree", "table": "fashion_data", "row_key": key,
                "field_refs": ["name", "part_type", "new_fashion_id_str"],
                "name_source": "fashion_data#name",
                "locator_chain": {"steps": [{"kind": "decoded-table-row", "source_id": "pe-live-tree",
                                             "table": "fashion_data", "row_key": key,
                                             "field_refs": ["name"]}],
                                  "chain_status": "replayed-structural", "scope": "record",
                                  "no_cross_source_field_join": True},
                "source_lock_sha256": board["meta"]["provenance"]["source_locks"][0]["sha256"],
                "upstream": {"package_sha256": board["meta"]["provenance"]["source_locks"][0]["sha256"],
                             "entry_index": None, "file_id": None},
            },
        })
        covered.add(key)
        added.append(key)
        if gk:
            card_of_group[gk] = items[-1]

    # appear 表里没被收过的
    for key, row in ap.by_key.items():
        if key in covered:
            continue
        v = row["values"]
        nm = str(v.get("name") or "").strip()
        part = {1: "头发", 2: "头饰", 20001: "面饰"}.get(v.get("part"))
        if not nm or not part:
            continue
        items.append({
            "id": "fw_" + hashlib.md5(f"{key}:{part}".encode()).hexdigest()[:10],
            "name": nm, "evidence": "structure", "evidence_level": "structure-only",
            "source": "PE 活树 player_module_appear_data 增量对齐",
            "tables": ["player_module_appear_data.py"], "row_keys": [key],
            "part": part, "part_label": part, "part_bucket": [part],
            "part_source": "part 码", "model_id": v.get("model_id"),
            "model_ids": [v["model_id"]] if isinstance(v.get("model_id"), int) else [],
            "grade_level": v.get("level"), "charm_value": v.get("charm_value"),
            "desc": v.get("desc"), "status_tags": ["static config", "unverified"],
            "provenance": {
                "source_id": "pe-live-tree", "table": "player_module_appear_data", "row_key": key,
                "field_refs": ["name", "part"], "name_source": "player_module_appear_data#name",
                "locator_chain": {"steps": [{"kind": "decoded-table-row", "source_id": "pe-live-tree",
                                             "table": "player_module_appear_data", "row_key": key,
                                             "field_refs": ["name"]}],
                                  "chain_status": "replayed-structural", "scope": "record",
                                  "no_cross_source_field_join": True},
                "source_lock_sha256": board["meta"]["provenance"]["source_locks"][0]["sha256"],
                "upstream": {"package_sha256": board["meta"]["provenance"]["source_locks"][0]["sha256"],
                             "entry_index": None, "file_id": None},
            },
        })
        covered.add(key)
        added.append(key)

    board["meta"]["state_summary"] = {"条目": len(items)}
    if APPLY and (added or refreshed):
        write_board_pair(BOARD, board)
    print(f"新增卡 {len(added)} | 刷新名 {refreshed} | 板现在 {len(items)}")
    if added:
        print("新增样例", [str(items[-len(added)+i]['name']) for i in range(min(5, len(added)))])
    print("（dry-run；加 --apply 写盘）" if not APPLY else "已写盘")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
