#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rebuild_fashion_bestplay_slots — 本场最佳动画 & 击败播报（衣柜-社交类目）

定位链（2026-09-04，用户指示时装类新增此类目）：
  ① 本场最佳动画道具=common_item 1340003-1340009（7 主题：斩破天光/炽日耀斑/炽海天姿/
     金乌负日/沙海月鸣/水晶玫瑰/不湮之花；desc=传世武器皮肤升阶三阶或殿堂时装外观造境奖励）
     + gift_data 礼盒 135386「本场最佳:街头赢家（30天）」（特训战场赛季 1000 分限时奖励，
     用户锚点；desc=街头涂鸦风暴龙卷动画）。
  ② 击败播报=common_item 154150 赤月荆棘/154775 炽海天澜/155147 神鸟凌天/155740 沙海月鸣/
     155955 水晶玫瑰（desc=衣柜-社交-击败播报处更换；传世皮肤升格二阶获得）。
  同主题链：传世皮肤二阶→击败播报、三阶/造境→本场最佳动画。
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "boards" / "fashion_bestplay_slots.json"

# (item_id, 类型, 主题, 获取链)
BESTPLAY_ITEMS = [
    (1340003, "本场最佳动画", "斩破天光", "传世武器皮肤·赤月晶魄 升阶三阶"),
    (1340004, "本场最佳动画", "炽日耀斑", "传世武器皮肤·炽日耀斑 升阶三阶"),
    (1340005, "本场最佳动画", "炽海天姿", "殿堂时装外观·炽海天姿 造境"),
    (1340006, "本场最佳动画", "金乌负日", "传世武器皮肤·金乌负日 升阶三阶"),
    (1340007, "本场最佳动画", "沙海月鸣", "传世武器皮肤·沙海月鸣 升阶三阶"),
    (1340008, "本场最佳动画", "水晶玫瑰", "传世武器皮肤·水晶玫瑰 升阶三阶"),
    (1340009, "本场最佳动画", "不湮之花", "殿堂时装外观·不湮之花 造境"),
    (135386, "本场最佳动画", "街头赢家（30天）", "特训战场每赛季 1000 分限时奖励（礼盒，用户锚点）"),
    (154150, "击败播报", "赤月荆棘", "传世武器皮肤·赤月晶魄 升格二阶"),
    (154775, "击败播报", "炽海天澜", "传世武器皮肤·炽日耀斑 升格二阶"),
    (155147, "击败播报", "神鸟凌天", "传世武器皮肤·金乌负日 升格二阶"),
    (155740, "击败播报", "沙海月鸣", "传世武器皮肤·沙海月鸣 升格二阶"),
    (155955, "击败播报", "水晶玫瑰", "传世武器皮肤·水晶玫瑰 升格二阶"),
]


def build_board() -> dict:
    ci = json.loads((ROOT / "data/boards/common_item_text_sources.json")
                    .read_text(encoding="utf-8"))
    ci_by = {it["item_id"]: it for it in ci["items"]}
    gift = json.loads((ROOT / "data/boards/gift_data_text_sources.json")
                      .read_text(encoding="utf-8"))
    gift_by = {it.get("item_id") or it.get("row_key"): it for it in gift["items"]}

    items = []
    for item_id, kind, theme, obtain in BESTPLAY_ITEMS:
        src = gift_by if item_id == 135386 else ci_by
        it = src.get(item_id)
        if it is None:
            raise KeyError(f"source row missing: {item_id}")
        display = it.get("name", it.get("display_name", ""))
        prov = it.get("text_provenance", {})
        cloned = json.loads(json.dumps(it))
        cloned["id"] = f"bestplay_{item_id}"
        cloned["name"] = display
        cloned["display_name"] = display
        cloned["kind"] = kind
        cloned["theme"] = theme
        cloned["obtain_chain"] = obtain
        cloned["source_board"] = "gift_data_text_sources" if item_id == 135386 \
            else "common_item_text_sources"
        cloned["text_provenance"] = prov
        items.append(cloned)

    items.sort(key=lambda x: (x["kind"], x["item_id"]))
    return {
        "meta": {
            "name": "\u5f53\u524d\u5305 \u00b7 \u672c\u573a\u6700\u4f73\u52a8\u753b & \u51fb\u8d25\u64ad\u62a5",
            "category": "二、时装类 / （六）最佳动画/击败播报",
            "source_server": ci["meta"].get("source_server", ""),
            "package_sha": ci["meta"].get("package_sha", ""),
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evidence": "structure",
            "notes": (
                "\u4e0b\u8863\u67dc-\u793e\u4ea4 \u7c7b\u76ee\uff1a\u672c\u573a\u6700\u4f73\u52a8\u753b 8"
                "\uff08common_item 1340003-1340009 \u4f20\u4e16\u76ae\u80a4\u4e09\u9636/\u6bbf\u5802\u9020\u5883 + "
                "gift \u793c\u76d2 135386 \u8857\u5934\u8d62\u5bb6 30\u5929\u7279\u8bad\u6218\u573a\u8d5b\u5b63\u5956\uff09"
                "+ \u51fb\u8d25\u64ad\u62a5 5\uff08common_item 154xxx\uff0c\u4f20\u4e16\u76ae\u80a4\u4e8c\u9636\uff09\uff1b"
                "\u540c\u4e3b\u9898\u94fe\uff1a\u76ae\u80a4\u4e8c\u9636\u2192\u64ad\u62a5\u3001\u4e09\u9636/\u9020\u5883\u2192\u52a8\u753b\u3002"
                "\u4ec5\u6587\u5b57/\u914d\u7f6e\u6765\u6e90\u3002"
            ),
            "provenance": ci["meta"].get("provenance", {}),
        },
        "items": items,
        "stats": {
            "catalog_entries": len(items),
            "by_kind": {"\u672c\u573a\u6700\u4f73\u52a8\u753b": sum(1 for i in items if i["kind"] == "\u672c\u573a\u6700\u4f73\u52a8\u753b"),
                        "\u51fb\u8d25\u64ad\u62a5": sum(1 for i in items if i["kind"] == "\u51fb\u8d25\u64ad\u62a5")},
        },
    }


def main() -> int:
    board = build_board()
    DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUTPUT.write_text(json.dumps(board, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"items": len(board["items"]), "stats": board["stats"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
