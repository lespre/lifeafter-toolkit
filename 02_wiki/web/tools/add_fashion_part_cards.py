# -*- coding: utf-8 -*-
"""给「板上只有同套其他部位、缺本部位独立卡」的登记行补卡（如 不湮之花-头饰）。"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re

WEB = pathlib.Path("E:/la拆包项目/02_wiki/web")
REG = WEB / "data/fashion_registry.json"
BOARD = WEB / "data/boards/fashion_wardrobe.json"
PART_END = re.compile(r"[-·](衣服|头饰|背包|光源|整套|面饰|发饰)$")


def main() -> int:
    reg = json.loads(REG.read_text(encoding="utf-8"))
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    names = {str(i.get("name")) for i in board["items"]}
    bases = {}
    for i in board["items"]:
        nm = str(i.get("name") or "")
        m = PART_END.search(nm)
        base = nm[: m.start()] if m else nm
        bases.setdefault(base, set()).add(str(i.get("model_id")))

    # 同一名字多行（时限变体）取永久款一条
    picked = {}
    for r in reg["rows"]:
        nm = r["name"]
        if not PART_END.search(nm) or nm in names:
            continue
        base = nm[: PART_END.search(nm).start()]
        if base not in bases:
            continue                      # 板上没有这套 → 不属于「补部位」
        if str(r["model_id"]) not in bases[base]:
            continue
        cur = picked.get(nm)
        if cur is None or (r.get("level") is not None and cur.get("level") is None):
            picked[nm] = r

    added = 0
    for nm, r in picked.items():
        m = PART_END.search(nm)
        part = m.group(1)
        item = {
            "id": "fw_" + hashlib.md5(nm.encode()).hexdigest()[:10],
            "name": nm,
            "evidence": "structure",
            "evidence_level": "structure-only",
            "source": "%s 行 %s" % (r["table"], r["key"]),
            "tables": [r["table"] + ".py"],
            "row_keys": [r["key"]],
            "name_variants": [nm],
            "part": part,
            "part_source": r["table"],
            "part_label": part,
            "part_bucket": [part],
            "model_id": r["model_id"],
            "model_ids": [r["model_id"]],
            "grade_level": r.get("level"),
            "grade_levels": [r.get("level")] if r.get("level") else [],
            "charm_value": r.get("charm"),
            "desc": r.get("desc") or "",
            "desc_note": "部位卡：该部位只在 %s 登记，fashion_data 无对应行" % r["table"],
            "icon_state": "无独立图标",
            "status_tags": ["static config"],
            "gender": "",
            "provenance": {"source_id": "fashion-parts-supplement",
                           "table": "com\\cdata\\%s.py" % r["table"],
                           "row_key": r["key"]},
        }
        board["items"].append(item)
        added += 1

    board["meta"]["notes"] = (str(board["meta"].get("notes") or "")
                              + " ｜ 部位补卡：从 player_appear_data / simple_fashion_data 补入 "
                              + str(added) + " 张独立部位卡")
    BOARD.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")
    print("补入部位卡 %d 张" % added)
    for nm in picked:
        if "不湮之花" in nm:
            print("   +", nm, picked[nm]["table"], picked[nm]["key"])
    print("现在总卡数", len(board["items"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
