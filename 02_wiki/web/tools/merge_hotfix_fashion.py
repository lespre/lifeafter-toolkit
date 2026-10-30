# -*- coding: utf-8 -*-
"""把 PC 热更新增的 19 套时装并进人物时装板（标 PC 热更来源），有图的挂图。"""
from __future__ import annotations

import hashlib
import json
import pathlib

ROOT = pathlib.Path("E:/la拆包项目")
WEB = ROOT / "02_wiki/web"
BOARD = WEB / "data/boards/fashion_wardrobe.json"
ROWS = ROOT / "01_索引与产物/30_分析/pc_hotfix_new_fashion.json"
IMGS = ROOT / "01_索引与产物/30_分析/pc_hotfix_new_fashion_imgs.json"

PART_CN = {"cloth": "衣服", "hat": "头饰", "bag": "背包", "light": "光源",
           "suit": "整套", "face": "捏脸"}


def main() -> int:
    rows = json.loads(ROWS.read_text(encoding="utf-8"))
    imgs = json.loads(IMGS.read_text(encoding="utf-8"))
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    have = {it.get("name") for it in board["items"]}

    # 按基名聚合成卡（同 model 的多部位拆成多张，与现有板一致）
    cards = {}
    for r in rows:
        name = str(r.get("name") or "")
        if not name:
            continue
        base = name.rsplit("-", 1)[0] if name.rsplit("-", 1)[-1].endswith("天") else name
        part = str(r.get("part_type") or "")
        key = (base, part)
        cur = cards.get(key)
        rec = {"name": base, "part": part, "model_id": r.get("model_id"),
               "level": r.get("level"), "row_keys": [r["row_key"]], "desc": r.get("desc")}
        if cur:
            cur["row_keys"].append(r["row_key"])
        else:
            cards[key] = rec

    added = 0
    for (base, part), rec in cards.items():
        label = PART_CN.get(part, part or "其他")
        # 头饰/衣服同模型时会各自成卡，名字带部位后缀，和现有板口径一致
        card_name = base if part in ("suit", "light") else f"{base}-{label}" if "-" not in base else base
        if card_name in have:
            continue
        cid = "fw_hf_" + hashlib.md5(f"{card_name}|{part}".encode()).hexdigest()[:8]
        paths = imgs.get(base) or []
        # 只挂与部位匹配的图
        pre = {"cloth": "icon_b_", "hat": "icon_h_", "bag": "icon_bag_", "light": "icon_light_",
               "suit": "icon_suit_"}.get(part, "icon_")
        paths = [p for p in paths if pathlib.Path(p).name.startswith(pre)] or paths
        item = {
            "id": cid,
            "name": card_name,
            "part": label,
            "part_label": label,
            "part_bucket": [label],
            "model_id": rec["model_id"],
            "model_ids": [rec["model_id"]] if rec["model_id"] else [],
            "grade_level": rec["level"],
            "charm_value": None,
            "gender": "女/男",
            "desc": rec.get("desc"),
            "row_keys": rec["row_keys"],
            "icon_state": "有图" if paths else "无图",
            "icon_count": len(paths),
            "_media": {"images": [{"png": p.replace("\\", "/"), "label": "图示1",
                                  "source": "PC 热更 20261030 · ui/item_icon"} for p in paths],
                       "total": len(paths)},
            "status_tags": ["static config"],
            "source": "PC 热更 20261030 · fashion_data（+133 行）",
            "hotfix_source": "pc_20261030_1954",
            "evidence": "structure",
        }
        board["items"].append(item)
        added += 1

    board["meta"]["hotfix_overlay"] = "PC 热更 20261030_1954：新增 19 套时装（图 9 套），PE 源未到位"
    BOARD.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    print("并入新卡", added, "｜ 板内总数", len(board["items"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
