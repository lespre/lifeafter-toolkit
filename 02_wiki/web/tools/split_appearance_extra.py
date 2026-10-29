# -*- coding: utf-8 -*-
"""「其他外观」按用户口径重分七类，并把头饰/衣服/背包/挂饰合并进人物时装。

- 头饰 / 衣服 / 背包 / 挂饰 → 合并进（一）人物时装
- 捏脸 / 戒指 / 半感染者花苞 → 各单开一个板块
- appearance_extra 原板下线（改名 .retired.json）
"""
from __future__ import annotations
import sys

import hashlib
import json
import pathlib
import re

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

ROOT = pathlib.Path(PROJ)
B = ROOT / "02_wiki/web/data/boards"
FW = B / "fashion_wardrobe.json"
EX = B / "appearance_extra.json"

MAP = {"发型/头部": "头饰", "脸型": "捏脸", "衣服": "衣服", "背包": "背包",
       "挂饰/宠物": "挂饰", "手持/道具": "挂饰", "光环/特效": "挂饰"}
MERGE = {"头饰", "衣服", "背包", "挂饰"}
OWN = {"捏脸": "appearance_face", "戒指": "appearance_ring", "半感染者花苞": "appearance_bud"}
TABLE = "com\\cdata\\player_appear_data.py"
SRC_ID = "fashion-parts-supplement-player_appear_data"
FIELDS = ["name", "part", "model_name"]
SRC_SHA = "61f7189bd6f94f58c07d350405a8820bc461183f03cee0b968df8dd2ff4cb199"


def classify(it: dict) -> str:
    nm = str(it.get("name") or "")
    if "花苞" in nm:
        return "半感染者花苞"
    if re.search(r"戒指|之戒|戒$", nm):
        return "戒指"
    return MAP.get(str(it.get("part")), "挂饰")


def prov(it: dict) -> dict:
    rk = it.get("row_keys") or []
    src = it.get("provenance") or {}
    return {
        "source_id": SRC_ID,
        "source_lock_sha256": SRC_SHA,
        "table": TABLE,
        "row_key": rk[0] if rk else None,
        "row_keys": rk,
        "field_refs": FIELDS,
        "name_source": TABLE + "#name",
        "part_source": "part",
        "icon_source": None,
        "rebuild": "split-20261026（来自 appearance_extra）",
        "upstream": {
            "package_sha256": src.get("source_lock_sha256"),
            "entry_index": None,
            "file_id": None,
            "decoded_sha256": None,
            "role": None,
        },
        "locator_chain": {
            "chain_status": "replayed-structural",
            "scope": "record",
            "no_cross_source_field_join": True,
            "steps": [{
                "kind": "decoded-table-row",
                "source_id": SRC_ID,
                "table": TABLE,
                "row_key": rk[0] if rk else None,
                "field_refs": FIELDS,
            }],
        },
    }


def main() -> int:
    ex = json.loads(EX.read_text(encoding="utf-8"))["items"]
    fw = json.loads(FW.read_text(encoding="utf-8"))
    items = fw["items"]
    have = {(i.get("name"), tuple(i.get("part_bucket") or [])) for i in items}

    buckets: dict[str, list[dict]] = {k: [] for k in
                                     ("头饰", "捏脸", "衣服", "背包", "挂饰", "戒指", "半感染者花苞")}
    for it in ex:
        buckets[classify(it)].append(it)

    added = 0
    for cat in MERGE:
        for it in buckets[cat]:
            key = (it.get("name"), (cat,))
            if key in have:
                continue
            hid = hashlib.md5(("%s|%s" % (it.get("name"), cat)).encode()).hexdigest()[:10]
            card = {
                "id": "fw_" + hid,
                "name": it.get("name"),
                "part": cat,
                "part_label": cat,
                "part_bucket": [cat],
                "part_source": "其他外观合并",
                "model_ids": it.get("model_ids") or [],
                "row_keys": it.get("row_keys") or [],
                "evidence": "structure",
                "evidence_level": "structure-only",
                "source": "player_appear_data（其他外观按部位合并）",
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
    FW.write_text(json.dumps(fw, ensure_ascii=False), encoding="utf-8")
    print("合并进人物时装 %d 张，时装总数 %d" % (added, len(items)))

    for cat, bid in OWN.items():
        rows = buckets[cat]
        out = {
            "meta": {"name": cat, "board": bid,
                     "category": "一、时装类 / （%s）%s" % (
                         {"捏脸": "六", "戒指": "七", "半感染者花苞": "八"}[cat], cat),
                     "generated": "2026-10-26", "evidence": "structure",
                     "package_sha": SRC_SHA,
                     "source_server": "PE 测试服 · 表 41_还原树/pe/配置/com/cdata（player_appear_data）",
                     "note": "由「其他外观」按部位拆出，只收该部位条目。"},
            "items": rows,
        }
        (B / (bid + ".json")).write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
        print("%-10s %3d 条 → %s.json" % (cat, len(rows), bid))

    arc = B / "appearance_extra.retired.json"
    if EX.is_file():
        EX.replace(arc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
