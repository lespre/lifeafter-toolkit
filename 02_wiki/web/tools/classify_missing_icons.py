# -*- coding: utf-8 -*-
"""把「补不到图」的 936 张分成：内部/占位、疑似不可得、玩家可用（真缺图），并重写清单。"""
from __future__ import annotations

import csv
import json
import pathlib
import re
from collections import Counter

PROJ = pathlib.Path("E:/la拆包项目")
BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
OUT_MD = PROJ / "01_索引与产物/30_分析/时装补不到图清单_20261101.md"
OUT_CSV = PROJ / "01_索引与产物/30_分析/时装补不到图清单_20261101.csv"

ENG = re.compile(r"占位|测试|NPC[-_ ]|级头盔|套（|high套|^00\d|debug|test", re.I)


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    miss = [i for i in d["items"] if not ((i.get("_media") or {}).get("images"))]

    rows, cat = [], Counter()
    for it in miss:
        name = it.get("name") or ""
        visible = it.get("name_visible")
        show_no_have = it.get("show_no_have")
        has_obtain = bool(it.get("obtain_res") or it.get("theme") or it.get("gift_package"))

        if visible is False or ENG.search(name):
            label = "内部/占位"
        elif has_obtain or show_no_have is True:
            label = "玩家可用·真缺图"
        elif show_no_have is False:
            label = "疑似不可得"
        else:
            label = "未判定"
        cat[label] += 1
        rows.append({
            "名称": name, "部件": it.get("part"), "性别": it.get("gender") or "",
            "model": it.get("model_id") or "",
            "分类": label,
            "有获取途径": "是" if has_obtain else "否",
            "未拥有时显示": show_no_have if show_no_have is not None else "",
            "名字可见": visible if visible is not None else "",
            "row_keys": ",".join(str(x) for x in (it.get("row_keys") or [])[:3]),
        })

    print("分类统计", dict(cat))
    order = {"玩家可用·真缺图": 0, "疑似不可得": 1, "未判定": 2, "内部/占位": 3}
    rows.sort(key=lambda r: (order[r["分类"]], str(r["部件"]), r["名称"]))
    with OUT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    lines = ["# 补不到图的时装清单（2026-11-01 分类版）", "",
             f"- 无图卡 {len(miss)}",
             "- 分类口径：",
             "  - **内部/占位**：`name_visible=False` 或名字含工程样式（NPC-/套（/级头盔/占位/测试）",
             "  - **玩家可用·真缺图**：有获取途径（obtain_res/theme/gift_package）或 `show_no_have=True`",
             "  - **疑似不可得**：无获取途径且 `show_no_have=False`（未拥有时列表里不显示）",
             "  - **未判定**：其余", ""]
    for k in ("玩家可用·真缺图", "疑似不可得", "未判定", "内部/占位"):
        lines.append(f"- {k}: {cat.get(k, 0)}")
    lines.append("")
    cur = None
    for r in rows:
        if r["分类"] != cur:
            cur = r["分类"]
            lines += ["", f"## {cur}", ""]
        extra = f"（model {r['model']}）" if r["model"] else ""
        lines.append(f"- {r['名称']}{extra}")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("→", OUT_MD, "\n→", OUT_CSV)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
