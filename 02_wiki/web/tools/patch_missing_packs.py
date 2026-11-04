# -*- coding: utf-8 -*-
"""补索引：把盘上存在但索引里没有的 gpk 包补进 pe_index（按 fid 去重）。"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

PROJ = Path(r"E:\la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import android_gpk as AG  # noqa: E402

DB = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
PACKS = PROJ / "01_索引与产物/源包/pe_gres_android"


def main() -> int:
    con = sqlite3.connect(str(DB), timeout=300)
    cols = [r[1] for r in con.execute("pragma table_info(rows)")]
    print("rows 列:", cols)
    have = {r[0] for r in con.execute("select distinct pack from rows")}
    todo = [p for p in sorted(PACKS.glob("*.gpk")) if p.name not in have]
    print("待补包", [p.name for p in todo])
    total = 0
    for p in todo:
        rows = []
        try:
            for e in AG.iter_entries(str(p)):
                rows.append(("%016X" % e["fid"], p.name, e["row"], e.get("off", 0),
                             e.get("packed", 0), e.get("decoded", 0), e.get("flag", 0)))
        except Exception as exc:  # noqa: BLE001
            print("  跳过", p.name, type(exc).__name__, exc)
            continue
        con.executemany(
            "insert or ignore into rows(fid,pack,row,off,packed,decoded,flag,name) "
            "values(?,?,?,?,?,?,?,null)", rows)
        con.commit()
        total += len(rows)
        print(f"  {p.name} 写入候选 {len(rows)} 条")
    print("总候选", total, "| 现 rows", con.execute("select count(*) from rows").fetchone()[0],
          "| packs", con.execute("select count(distinct pack) from rows").fetchone()[0])
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
