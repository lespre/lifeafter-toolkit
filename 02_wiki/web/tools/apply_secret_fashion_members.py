#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""神秘商店（SecretFashionHD）：用 secret_fashion_goods_data 的结构成员填期次。

表结构：0x36 映射行 key=活动号，槽位指向 0x86 明细行；
明细行的 jump 字段里带真的商品 id（实测字段 12 = 时装/礼包，字段 15 = 材料/家具）。
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
sys.path.insert(0, str(WEB / "tools"))

import rebuild_lottery_periods as R  # noqa: E402
from board_io import write_board_pair  # noqa: E402

BOARD = WEB / "data/boards/lottery_periods.json"


def main() -> int:
    t = R._opt_table(R.TREE / "secret_fashion_goods_data.py",
                     R.TREE / "secret_fashion_goods_data_chs.py")
    names = R.Names()
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    meta = board["meta"]
    lock = meta["provenance"]["source_locks"][0]
    src_id, src_sha = lock["source_id"], lock["sha256"]
    periods = {p["period_id"]: p for p in board["periods"]}

    board["items"] = [i for i in board["items"] if not i.get("secret_mapped")]

    added = touched = 0
    for key in sorted(t.map_start):
        pid = f"lp_{key}"
        per = periods.get(pid)
        if per is None or "SecretFashion" not in str(per.get("family_key")):
            continue
        try:
            slots = R.parse_map_row(t, t.map_start[key])
        except Exception:
            continue
        seen: set[int] = set()
        n_per = 0
        for slot, off in slots:
            row = R.row86(t, off)
            for fld, v in row.items():
                if not (isinstance(v, str) and v.startswith("jump:")):
                    continue
                try:
                    grp = t.jump_values(v)
                except Exception:
                    continue
                for iid in grp:
                    if not (10000 <= iid < 3_000_000_000) or iid in seen:
                        continue
                    seen.add(iid)
                    name = names.resolve(int(iid))[0]
                    board["items"].append({
                        "id": f"{pid}:sf{iid}",
                        "period_id": pid,
                        "period_label": per.get("label"),
                        "period_start": per.get("start"),
                        "period_end": per.get("end"),
                        "family": per.get("family"),
                        "family_key": per.get("family_key"),
                        "name": name or f"未识别道具 {iid}",
                        "item_id": str(iid),
                        "kind": "神秘商店商品",
                        "evidence": "structure",
                        "evidence_level": "structure-only",
                        "status_tags": (["unresolved", "static config"] if not name
                                        else ["verified", "static config", "runtime final unknown"]),
                        "_media": {"images": [], "total": 0},
                        "icon_state": "未下发",
                        "icon": None,
                        "slot": slot,
                        "source": f"secret_fashion_goods_data key={key} 槽位 {slot} 字段 {fld}",
                        "secret_mapped": True,
                        "provenance": {
                            "source_id": src_id,
                            "table": "secret_fashion_goods_data",
                            "row_key": key,
                            "field_refs": [f"field_{fld}"],
                            "name_source": "item_names",
                            "locator_chain": {
                                "steps": [{"kind": "decoded-table-row", "source_id": src_id,
                                           "table": "secret_fashion_goods_data",
                                           "row_key": key, "field_refs": [f"field_{fld}"]}],
                                "chain_status": "replayed-structural", "scope": "record",
                                "no_cross_source_field_join": True,
                            },
                            "source_lock_sha256": src_sha,
                            "upstream": {"package_sha256": src_sha, "entry_index": None, "file_id": None},
                        },
                    })
                    n_per += 1
        if n_per:
            added += n_per
            touched += 1
            per["member_source"] = "structure:secret-shop"

    cnt = Counter(i["period_id"] for i in board["items"])
    for p in board["periods"]:
        p["member_count"] = cnt.get(p["period_id"], 0)
    write_board_pair(BOARD, board)
    print(f"神秘商店期次 {touched} 个，新增成员 {added} 条")
    return 0


if __name__ == "__main__":
    sys.exit(main())
