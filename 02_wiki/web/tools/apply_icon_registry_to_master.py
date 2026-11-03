#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把全量图标注册表挂到「全量道具总表」板块（item_master_full）。

每条 item 新增（不覆盖既有字段）：
  icon_path     ui/... 原始路径（来自 icon_registry）
  icon_source   哪张表给的（common_item_data / fashion_data / gift_data / recipe …）
  icon_png      assets/lottery_icons/<id>.png 若本地已导出
  icon_state    已导出 / 源已定位未导出 / 无图标源
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
sys.path.insert(0, str(WEB / "tools"))
from board_io import write_board_pair  # noqa: E402

BOARD = WEB / "data/boards/item_master_full.json"
REG = Path(r"E:\la拆包项目\01_索引与产物\30_分析\icon_registry.json")
ICON_DIRS = [WEB / "assets/lottery_icons", WEB / "assets/item_icons_full"]


def main() -> int:
    reg = json.loads(REG.read_text(encoding="utf-8"))["icons"]
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    items = board["items"]

    have_png: dict[str, str] = {}
    for d in ICON_DIRS:
        if not d.exists():
            continue
        for p in d.glob("*.png"):
            have_png.setdefault(p.stem, f"assets/{d.name}/{p.name}")

    stat = Counter()
    lock = board["meta"]["provenance"]["source_locks"][0]
    sha = lock.get("sha256")
    for it in items:
        it.pop("_prov_shape", None)
        pv = it.get("provenance")
        if isinstance(pv, dict):
            pv.setdefault("table", it.get("icon_source") or "item_master_full")
            pv.setdefault("name_source", "item_master")
            up = pv.get("upstream")
            if not isinstance(up, dict):
                up = {}
            if not up.get("package_sha256"):
                up["package_sha256"] = sha
            pv["upstream"] = up
    for it in items:
        iid = str(it.get("item_id") or "")
        rec = reg.get(iid)
        if not rec:
            it["icon_state"] = "无图标源"
            stat["无图标源"] += 1
            continue
        it["icon_path"] = rec["path"]
        it["icon_source"] = rec["source"]
        png = have_png.get(iid)
        if png:
            it["icon"] = png
            it["_media"] = {"images": [{"png": png}], "total": 1}
            it["icon_state"] = "已导出"
            stat["已导出"] += 1
        else:
            it["icon_state"] = "源已定位未导出"
            stat["源已定位未导出"] += 1

    meta = board["meta"]
    # 中文标签 + 隐藏工程字段（可见区不出现英文键）
    labels = dict(meta.get("field_labels") or {})
    labels.update({
        "item_id": "道具ID", "name": "名称", "namespace": "所属表",
        "identity_state": "身份状态", "name_status": "命名状态",
        "icon_path": "图标路径", "icon_source": "图标来源",
        "icon_png": "图标文件", "icon_state": "图标状态",
    })
    meta["field_labels"] = labels
    hide = set(meta.get("hide_fields") or [])
    hide.update({"_prov_shape", "provenance", "evidence", "evidence_level",
                 "status_tags", "source", "id", "icon", "icon_png", "icon_path"})
    meta["hide_fields"] = sorted(hide)
    # 卡头摘要里那几项原本是 dict，页面会渲染成 [object Object]
    for k in ("namespace", "evidence", "status_tags"):
        if isinstance(meta.get(k), (dict, list)):
            meta[k] = "—"
    meta["card_mode"] = "roster"
    meta["hide_media"] = False
    meta["id_label"] = "道具ID"
    meta["card_summary"] = [
        ["item_id", "道具ID"], ["namespace", "所属表"],
        ["icon_state", "图标"], ["icon_source", "图标来源"],
    ]
    meta["icon_stats"] = {"总条目": len(items), **stat,
                          "icon 注册表": len(reg)}
    write_board_pair(BOARD, board)
    print(f"条目 {len(items)} | 已导出 {stat['已导出']} | 源已定位未导出 {stat['源已定位未导出']} "
          f"| 无源 {stat['无图标源']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
