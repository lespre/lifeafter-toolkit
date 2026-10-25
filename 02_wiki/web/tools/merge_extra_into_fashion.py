# -*- coding: utf-8 -*-
"""按用户口径重做：其他外观 796 条全部并入（一）人物时装，按 part_code 1~7 标注部位。

part_code → 部位（用户 2026-10-26 口径）
  1 头饰 · 2 捏脸 · 3 衣服 · 4 背包 · 5 挂饰 · 6 戒指 · 7 半感染者花苞
不再单开 捏脸 / 戒指 / 花苞 板块，全部合进人物时装。
"""
from __future__ import annotations

import hashlib
import json
import pathlib

ROOT = pathlib.Path("E:/la拆包项目")
B = ROOT / "02_wiki/web/data/boards"
FW = B / "fashion_wardrobe.json"
EX = B / "appearance_extra.retired.json"
BACKUP = pathlib.Path("C:/Users/Administrator/AppData/Local/hermes/cache/scratch/fw_before_merge.json")

PART = {1: "头饰", 2: "捏脸", 3: "衣服", 4: "背包", 5: "挂饰", 6: "戒指", 7: "半感染者花苞"}
TABLE = "com\\cdata\\player_appear_data.py"
SRC_ID = "fashion-parts-supplement-player_appear_data"
SRC_SHA = "61f7189bd6f94f58c07d350405a8820bc461183f03cee0b968df8dd2ff4cb199"
FIELDS = ["name", "part", "model_name"]


def prov(it: dict) -> dict:
    rk = it.get("row_keys") or []
    return {
        "source_id": SRC_ID,
        "source_lock_sha256": SRC_SHA,
        "table": TABLE,
        "row_key": rk[0] if rk else None,
        "row_keys": rk,
        "field_refs": FIELDS,
        "name_source": TABLE + "#name",
        "part_source": "part_code",
        "icon_source": None,
        "rebuild": "merge-20261026（其他外观并入人物时装）",
        "upstream": {"package_sha256": SRC_SHA, "entry_index": None, "file_id": None,
                     "decoded_sha256": None, "role": None},
        "locator_chain": {
            "chain_status": "replayed-structural",
            "scope": "record",
            "no_cross_source_field_join": True,
            "steps": [{"kind": "decoded-table-row", "source_id": SRC_ID, "table": TABLE,
                       "row_key": rk[0] if rk else None, "field_refs": FIELDS}],
        },
    }


def main() -> int:
    base = json.loads(BACKUP.read_text(encoding="utf-8"))   # 合并前的 2016 张
    items = base["items"]
    ex = json.loads(EX.read_text(encoding="utf-8"))["items"]

    have = {(i.get("name"), tuple(i.get("part_bucket") or [])) for i in items}
    added = 0
    for it in ex:
        code = it.get("part_code")
        label = PART.get(code, str(it.get("part") or "其他"))
        key = (it.get("name"), (label,))
        if key in have:
            continue
        hid = hashlib.md5(("%s|%s" % (it.get("name"), label)).encode()).hexdigest()[:10]
        card = {
            "id": "fw_" + hid,
            "name": it.get("name"),
            "part": label,
            "part_label": label,
            "part_bucket": [label],
            "part_code": code,
            "part_source": "player_appear_data.part_code",
            "gender": it.get("gender") or "",
            "model_ids": it.get("model_ids") or [],
            "row_keys": it.get("row_keys") or [],
            "evidence": "structure",
            "evidence_level": "structure-only",
            "source": "player_appear_data（其他外观并入，按 part_code 分部位）",
            "status_tags": ["static config"],
            "provenance": prov(it),
            "merged_from": "appearance_extra",
        }
        if (it.get("_media") or {}).get("images"):
            card["_media"] = it["_media"]
            card["icon_state"] = "有图"
        else:
            card["icon_state"] = "无独立图标"
        items.append(card)
        have.add(key)
        added += 1

    base["items"] = items
    meta = base.setdefault("meta", {})
    meta["part_rule"] = ("部位按 player_appear_data.part_code：1 头饰 / 2 捏脸 / 3 衣服 / 4 背包 / "
                         "5 挂饰 / 6 戒指 / 7 半感染者花苞。")
    meta["merged_from_extra"] = added
    FW.write_text(json.dumps(base, ensure_ascii=False), encoding="utf-8")
    print("并入 %d 张，时装总数 %d" % (added, len(items)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
