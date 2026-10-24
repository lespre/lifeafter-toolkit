# -*- coding: utf-8 -*-
"""按几何跨度给背包打「隐藏半感染者花苞」标记。

口径（用户 2026-10-24 确认）：横向跨度 span_x ≥ 13.0 的背包会遮住花苞；
名字里带「翼/翅膀」的也一律算（已被跨度覆盖）。
依据：`子代理产出_20261022/_work_bbox_final.json`（.mesh 文件头真值包围盒）。
"""
from __future__ import annotations

import json
import pathlib

PROJ = pathlib.Path("E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
BB = PROJ / "01_索引与产物/30_分析/子代理产出_20261022/_work_bbox_final.json"
BOARD = WEB / "data/boards/fashion_wardrobe.json"
THRESHOLD = 13.0


def main() -> int:
    bb = json.loads(BB.read_text(encoding="utf-8"))
    spans = {}
    for r in bb:
        spans[str(r.get("name") or "")] = max(spans.get(str(r.get("name") or ""), 0), r["span"][0])
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    n = 0
    for it in board["items"]:
        if it.get("part_bucket") != ["背包"]:
            continue
        name = str(it.get("name") or "").split("-")[0]
        s = spans.get(name)
        if s is not None and s >= THRESHOLD:
            it["reborn_vis"] = True
            it["reborn_src"] = "bbox_span>=13"
            n += 1
    BOARD.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")
    print("标记背包卡", n, "张｜阈值 span_x ≥", THRESHOLD)
    print("样例", [i["name"] for i in board["items"] if i.get("reborn_src") == "bbox_span>=13"][:10])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
