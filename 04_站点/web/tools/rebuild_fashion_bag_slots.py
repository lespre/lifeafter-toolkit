#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rebuild_fashion_bag_slots — 时装外观附件（背包）独立板导出器

源=时装板 fashion_wardrobe_slots 同快照条目（BA8 current-snapshot fashion_data 22570，
v3 desc 防护已过）。按展示名含词（背包/挂件/挂饰/腰饰/披风/背饰/挎包/伞）筛附件类，
剔除 v3 仍漏网的纯 desc 句（可爱的X/使用…打造/有纪念意义/科技会…产品——raw 为完整
句子且无部件标记）。条目保留时装板原行级链（text_provenance/provenance/row_key/variants），
仅改 category 与补 accessory 分类字段。不改时装板本体。
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "boards" / "fashion_bag_slots.json"
ACC_WORDS = ("背包", "挂件", "挂饰", "腰饰", "披风", "背饰", "挎包", "伞", "翅膀", "翼", "包", "袋")
# 翅膀外观（帝皇战翼 等战翼=背饰槽）在衣柜中归背包分类，保留 accessory 细分
WING_WORDS = ("翅膀", "翼")
# "XX之翼"=翅膀主题时装（希望之翼 有 -衣服/-头饰 件行铁证），非背包——排除
FASHION_WING_TAILS = ("之翼",)
# 单字 包/袋 命中归背包（仿皮旅行包/大袋化肥 等名字无"背包"字样的背包），
# 但部件行（恭喜发财红包-头饰 等名字带部件后缀的）不是背包
PART_BUCKETS = ("头饰", "衣服", "套装")
DESC_STRAY = {
    # 完整句子残头（无部件标记、raw 为 desc 句），v3 词表未覆盖
    "使用全新科技打造的喷气背包",
    "有纪念意义的背包",
    "科技会全新背包产品",
    "可爱的水母啵啵背包",
    "可爱的草莓甜心背包",
}


def build_board(registry_path: Path) -> dict:
    src_path = ROOT / "data" / "boards" / "fashion_wardrobe_slots.json"
    if not src_path.is_file():
        raise FileNotFoundError(f"need published fashion_wardrobe_slots: {src_path}")
    src = json.loads(src_path.read_text(encoding="utf-8"))

    items = []
    for it in src["items"]:
        nm = it["name"]
        if nm in DESC_STRAY:
            continue
        acc = next((w for w in ACC_WORDS if w in nm), None)
        if acc is None:
            continue
        # 部件行排除（红包-头饰/纸箱头系=头饰，非背包）
        if it.get("part") in PART_BUCKETS:
            continue
        # "XX之翼"翅膀主题时装排除（希望之翼 - 衣服/头饰 件行铁证）
        if any(nm.endswith(t) for t in FASHION_WING_TAILS):
            continue
        wing = next((w for w in WING_WORDS if w in nm), None)
        cloned = json.loads(json.dumps(it))  # 深拷贝保 provenance
        if wing:
            cloned["accessory_type"] = "翅膀"
            cloned["accessory_bucket"] = "背包"
        elif acc == "挎包":
            cloned["accessory_type"] = "挎包"
            cloned["accessory_bucket"] = "挎包"
        else:
            cloned["accessory_type"] = "背包"
            cloned["accessory_bucket"] = "背包"
        cloned["source_board"] = "fashion_wardrobe_slots"
        items.append(cloned)

    items.sort(key=lambda x: (x["accessory_type"], x["name"]))
    return {
        "meta": {
            "name": "当前包 · 时装外观附件（背包·挂饰）",
            "category": "二、时装类 / （三）背包/挂件",
            "source_server": src["meta"]["source_server"],
            "package_sha": src["meta"]["package_sha"],
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evidence": "structure",
            "notes": (
                "从时装板（fashion_wardrobe_slots，BA8 fashion_data 22570 同快照）筛附件类条目："
                "展示名含 背包/挎包/挂件/挂饰/腰饰/披风/背饰/伞/翅膀(翼)/单字包·袋（部件行排除），"
                "剔除 v3 漏网纯 desc 句 5 条（可爱的X/使用…打造/有纪念意义/科技会…产品）。"
                "行级链（name/desc 槽位回放、variants 全行 key）原样继承时装板，未跨表裁决；"
                "名字无\"背包\"字样的背包（仿皮旅行包/大袋化肥/可乐玩偶包/纪念包系 15 条）按用户口径收录，"
                "accessory_type=背包；翅膀（希望之翼/帝皇战翼等 5 条）归背包分类（背饰槽）细分=翅膀；"
                "挎包・EVA 细分=挎包。时装表内挂件/腰饰/披风/伞=0 行。"
            ),
            "provenance": src["meta"].get("provenance", {}),
        },
        "items": items,
        "stats": {
            "catalog_entries": len(items),
            "by_accessory": {w: sum(1 for x in items if x["accessory_type"] == w)
                             for w in ("背包", "挎包", "翅膀")},
        },
    }


def main() -> int:
    board = build_board(ROOT / "data" / "live_sources.json")
    DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUTPUT.write_text(json.dumps(board, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(DEFAULT_OUTPUT), "items": len(board["items"]),
                      "by_accessory": board["stats"]["by_accessory"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
