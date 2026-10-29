# -*- coding: utf-8 -*-
"""建立「半感染者花苞」板块：取人物时装里带 reborn_vis（是否隐藏半感染者花苞）的卡。

用户口径：花苞只有半感染者才有，reborn_vis 就是「是否隐藏半感染者花苞」。
"""
from __future__ import annotations
import sys

import hashlib
import json
import pathlib
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

ROOT = pathlib.Path(PROJ)
B = ROOT / "02_wiki/web/data/boards"
FW = B / "fashion_wardrobe.json"
OUT = B / "appearance_bud.json"
POLICY = ROOT / "02_wiki/web/data/publication_policy.json"
TAX = ROOT / "02_wiki/web/data/wiki_taxonomy.json"


def main() -> int:
    fw = json.loads(FW.read_text(encoding="utf-8"))
    # 过滤 name_visible=False 的「其他外观并入」卡（开发名、无独立图标），
    # 否则同一套外观会在本板出现两条（正式卡 + 开发名卡）。
    src = [i for i in fw["items"]
           if i.get("reborn_vis") is not None and i.get("name_visible") is not False]
    items = []
    for it in src:
        items.append({
            "id": "bud_" + hashlib.md5(str(it["id"]).encode()).hexdigest()[:10],
            "name": it.get("name"),
            "parent_card": it.get("id"),
            "part_bucket": it.get("part_bucket") or [],
            "hide_bud": "是" if it.get("reborn_vis") else "否",
            "reborn_vis": it.get("reborn_vis"),
            "hide_parts": it.get("hide_parts") or [],
            "_media": it.get("_media") or {"images": [], "total": 0},
            "icon_state": it.get("icon_state"),
            "evidence": "structure",
            "evidence_level": "structure-only",
            "source": "fashion_data#reborn_vis（是否隐藏半感染者花苞）",
            "status_tags": ["static config"],
            "provenance": it.get("provenance"),
        })
    board = {
        "meta": {
            "name": "半感染者花苞",
            "board": "appearance_bud",
            "category": "一、时装类 / （八）半感染者花苞",
            "generated": time.strftime("%Y-%m-%d"),
            "evidence": "structure",
            "package_sha": (fw["meta"].get("package_sha") or ""),
            "source_server": fw["meta"].get("source_server"),
            "provenance": fw["meta"].get("provenance"),
            "state_summary": {"verified": 0, "unresolved": len(items), "quarantined": 0,
                              "static config": len(items), "runtime final unknown": 0},
            "card_summary": [["name", "外观"], ["part_bucket", "部位"], ["hide_bud", "隐藏花苞"]],
            "note": "花苞仅半感染者拥有；本板收录带 reborn_vis 字段的时装，标明是否隐藏花苞。",
        },
        "items": items,
    }
    OUT.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")
    print("appearance_bud：%d 条" % len(items))

    pol = json.loads(POLICY.read_text(encoding="utf-8"))
    pol["boards"]["appearance_bud"] = {
        "publication_status": "published",
        "category": "一、时装类 / （八）半感染者花苞",
        "items": len(items),
        "reason": "花苞为半感染者专属；条目取时装表的 reborn_vis 字段（是否隐藏半感染者花苞）。",
    }
    POLICY.write_text(json.dumps(pol, ensure_ascii=False), encoding="utf-8")

    t = json.loads(TAX.read_text(encoding="utf-8"))
    for node in t["树"]:
        kids = node.get("children") or []
        if any("appearance_ring" in (k.get("boards") or []) for k in kids):
            if not any("appearance_bud" in (k.get("boards") or []) for k in kids):
                kids.append({"name": "（八）半感染者花苞", "boards": ["appearance_bud"]})
            node["children"] = kids
    TAX.write_text(json.dumps(t, ensure_ascii=False), encoding="utf-8")
    TAX.with_suffix(".js").write_text("window.WIKI_TAXONOMY=" + json.dumps(t, ensure_ascii=False) + ";\n",
                                      encoding="utf-8")
    print("taxonomy / policy 已加（八）半感染者花苞")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
