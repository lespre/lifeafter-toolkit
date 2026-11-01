# -*- coding: utf-8 -*-
"""补齐配置里有、板上没有的时装卡（当前 2 张：蔚蓝奇遇 整套 3185 / 全村的阳光-头饰 3724）。"""
from __future__ import annotations

import json
import pathlib
import sys

PROJ = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
import add_fashion_style_fields as A  # noqa: E402
from board_io import write_board_pair  # noqa: E402

BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
MAP = {"cloth": "衣服", "hat": "头发", "bag": "背包", "light": "荧光棒", "suit": "整套"}


def sv(x):
    return x[1] if isinstance(x, tuple) else x


def main() -> int:
    rows, _, _ = A.load("fashion_data")
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]
    have = {(str(i.get("model_id")), i.get("part")) for i in items}

    groups = {}
    for r in rows:
        v = r["values"]
        pt = str(sv(v.get("part_type")) or "") or str(sv(v.get("new_fashion_id_str")) or "").split("_")[0]
        part = MAP.get(pt)
        model = sv(v.get("model_id"))
        if not part or model in (None, "", 0):
            continue
        key = (str(model), part)
        if key in have:
            continue
        g = groups.setdefault(key, {"rows": [], "name": None, "charm": None, "level": None,
                                    "desc": None, "icons": None})
        g["rows"].append(int(r["key"]))
        g["name"] = g["name"] or str(sv(v.get("name")) or "")
        ch = sv(v.get("charm_value"))
        if isinstance(ch, int):
            g["charm"] = ch if g["charm"] is None else max(g["charm"], ch)
        lv = sv(v.get("level"))
        if isinstance(lv, int) and g["level"] is None:
            g["level"] = lv
        ds = sv(v.get("desc"))
        if ds and not g["desc"]:
            g["desc"] = str(ds)
        ic = sv(v.get("icons"))
        if ic and not g["icons"]:
            g["icons"] = str(ic)

    print(f"待补 {len(groups)} 张")
    for key, g in groups.items():
        items.append({
            "id": f"fw_stat_{key[0]}_{'h' if key[1] == '头发' else 's' if key[1] == '整套' else 'c'}",
            "name": g["name"], "part": key[1], "part_label": key[1], "part_bucket": [key[1]],
            "model_id": int(key[0]), "model_ids": [int(key[0])],
            "grade_level": g["level"], "charm_value": g["charm"], "gender": None,
            "desc": g["desc"], "row_keys": sorted(g["rows"]),
            "icon_state": "有图标字段" if g["icons"] else "缺图",
            "icon_count": None, "_media": None, "status_tags": ["static config"],
            "source": "PE 活树 · fashion_data（骨架补齐）",
            "evidence": "structure", "evidence_level": "structure-only",
            "part_source": "fashion_data.part_type（部位码写死）",
            "provenance": {"source_id": "fashion-wardrobe-struct",
                           "table": "com\\cdata\\fashion_data.py",
                           "row_key": sorted(g["rows"])[0],
                           "row_keys": sorted(g["rows"]),
                           "field_refs": ["name", "part_type", "model_id", "charm_value", "level", "desc", "icons"]},
        })
        print("  +", g["name"], key, "行数", len(g["rows"]))
    if groups:
        write_board_pair(BOARD, d)
    print("板块", len(items))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
