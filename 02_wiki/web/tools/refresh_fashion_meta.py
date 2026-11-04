# -*- coding: utf-8 -*-
"""刷新时装衣柜板的 meta：生成时间、活树行数、覆盖、图标状态、热更版本。

只改 meta，不动 items。
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
sys.path.insert(0, str(WEB / "tools"))
import rebuild_lottery_periods as R  # noqa: E402
from board_io import write_board_pair  # noqa: E402

BOARD = WEB / "data/boards/fashion_wardrobe.json"
OVERLAY = Path(r"E:\la拆包项目\01_索引与产物\30_分析\pe_hotfix_overlay.json")


def main() -> int:
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    items = board["items"]
    meta = board["meta"]

    fd = R._opt_table(R.TREE / "fashion_data.py", R.TREE / "fashion_data_chs.py")
    rows = len(fd.by_key)
    covered = set()
    for it in items:
        for k in (it.get("row_keys") or []):
            try:
                covered.add(int(k))
            except Exception:
                pass

    with_img = sum(1 for it in items if ((it.get("_media") or {}).get("images") or []))
    no_img = len(items) - with_img

    ts = None
    if OVERLAY.is_file():
        ts = json.loads(OVERLAY.read_text(encoding="utf-8")).get("timestamp")
    hv = ""
    if ts:
        when = dt.datetime.fromtimestamp(int(ts) / 1000).strftime("%Y-%m-%d %H:%M")
        hv = f"PE 热更 overlay {ts}（{when}，573 个包）已并入还原树"

    now = dt.datetime.now().astimezone()
    meta["generated"] = now.strftime("%Y-%m-%d")
    meta["rebuild"] = {
        "at": now.isoformat(timespec="seconds"),
        "decoded_rows": rows,
        "cards": len(items),
        "rows_covered": len(covered & set(fd.by_key)),
        "uncovered_rows": rows - len(covered & set(fd.by_key)),
        "prev_items": meta.get("rebuild", {}).get("prev_items"),
        "fetched_new": 0,
    }
    meta["hotfix_overlay"] = hv or "PE 还原树当前快照"
    meta["icon_filled_at"] = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    meta["state_summary"] = {
        "有图": with_img,
        "无图": no_img,
        "活树行数": rows,
        "已覆盖行数": len(covered & set(fd.by_key)),
    }
    meta["source_label"] = "PE 还原树 · fashion_data（测试服，活树）"
    notes = meta.get("notes") or ""
    # 只替换首行统计，保留后面的图标命名说明
    notes = re.sub(r"^全量重建：[\d,]+ 行 → [\d,]+ 张卡[^\n]*",
                   f"活树重建：{rows:,} 行 → {len(items):,} 张卡（覆盖 {len(covered & set(fd.by_key)):,}/{rows:,} 行）；"
                   f"有图 {with_img:,} / 无图 {no_img:,}。", notes, count=1)
    meta["notes"] = notes
    write_board_pair(BOARD, board)
    print("generated", meta["generated"], "| 行", rows, "| 卡", len(items),
          "| 覆盖", len(covered & set(fd.by_key)), "| 有图", with_img, "| 热更", hv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
