#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全站补图（回填阶段）：把已下发的 assets/lottery_icons/<item_id>.png 接回板块条目。

只动三个字段：icon（无 raw 文本合同的板）、icon_state、_media.images/total。
其它字段（provenance / text_provenance / stats / meta）一律不动，数据结构保持原形。

  - _media 为 null      → 新建 {"images":[1 张], "total": 1}
  - _media 已有 images  → 原地替换 images 与 total，保留其它键
  - 「客户端未下发」类 missing 列表在拿到图后清空（否则卡面同时显示有图与缺图）

写入走 tools/board_io.write_board_pair（紧凑格式，.json 与 .js 同源）。
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
BOARDS = ["lottery_periods", "chip_item_catalog", "common_item_text_sources"]
# 该板的 icon 字段是「common_item.icon 原样文本」（配 CHS 槽位溯源），不覆盖
RAW_ICON_BOARDS = {"common_item_text_sources"}
OUT = WEB / "assets/lottery_icons"

sys.path.insert(0, str(WEB / "tools"))
from board_io import write_board_pair  # noqa: E402


def usable_png(it: dict) -> bool:
    for im in ((it.get("_media") or {}).get("images") or []):
        p = (im.get("png") or "").split("?")[0]
        if p and (WEB / p).exists():
            return True
    return False


def main() -> int:
    summary = {}
    for bn in BOARDS:
        path = WEB / f"data/boards/{bn}.json"
        board = json.loads(path.read_text(encoding="utf-8-sig"))
        items = board.get("items") or []
        touched = 0
        for it in items:
            if not isinstance(it, dict) or not it.get("item_id"):
                continue
            iid = str(it["item_id"])
            tgt = OUT / f"{iid}.png"
            if not tgt.exists() or usable_png(it):
                continue
            rel = f"assets/lottery_icons/{iid}.png"
            media = it.get("_media")
            img = {"png": rel, "label": "图标", "source": "common_item.icon → PE 直出"}
            if isinstance(media, dict):
                media["images"] = [img]
                media["total"] = 1
                if isinstance(media.get("missing"), list) and media["missing"]:
                    media["missing"] = []
                if isinstance(media.get("note"), str) and "未下发" in media["note"]:
                    media.pop("note")
            else:
                it["_media"] = {"images": [img], "total": 1}
            if bn not in RAW_ICON_BOARDS:
                it["icon"] = rel
            it["icon_state"] = "已下发"
            touched += 1
        if touched:
            write_board_pair(path, board)
        summary[bn] = {"items": len(items), "touched": touched}
        print(f"{bn:28s} items={len(items):6d} backfilled={touched:6d}")
    (WEB.parent.parent / "01_索引与产物/30_分析/common_item_icon_backfill.json").write_text(
        json.dumps({"generated": time.strftime("%Y-%m-%d %H:%M:%S"), "boards": summary},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    print("total backfilled:", sum(v["touched"] for v in summary.values()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
