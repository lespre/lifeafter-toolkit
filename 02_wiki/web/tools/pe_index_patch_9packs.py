# -*- coding: utf-8 -*-
"""增量补索引：把 9 个从未入过 pe_index 的 gpk 追加进现有库（保留已有 name 列）。

不动其他包，不重建整库。
"""
from __future__ import annotations

import multiprocessing as mp
import pathlib
import sqlite3
import sys
import time

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import pe_index as PI  # noqa: E402

DB = ROOT / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
PACKDIR = ROOT / "01_索引与产物/源包/pe_gres_android"
PACKS = ["0234.gpk", "0239.gpk", "0279.gpk", "0280.gpk", "0284.gpk",
         "0288.gpk", "0293.gpk", "0303.gpk", "0309.gpk",
         "0342.gpk", "0343.gpk", "0344.gpk", "0345.gpk", "0346.gpk"]


def main() -> int:
    con = sqlite3.connect(str(DB))
    con.execute("PRAGMA synchronous=OFF")
    have = {r[0] for r in con.execute("select distinct pack from rows")}
    todo = [p for p in PACKS if p not in have]
    print("库里已有包", len(have), "｜ 本次补", len(todo), flush=True)
    if not todo:
        return 0
    t0 = time.time()
    total = 0
    paths = [str(PACKDIR / p) for p in todo]
    with mp.Pool(min(8, len(paths) or 1)) as pool:
        for pack, rows in pool.imap_unordered(PI.scan_one, paths):
            name = pathlib.Path(pack).name
            if rows and rows[0][0] == "__ERROR__":
                print("  ✗ 扫描失败", name, flush=True)
                continue
            con.executemany(
                "INSERT OR REPLACE INTO rows(fid,pack,row,off,packed,decoded,flag) VALUES(?,?,?,?,?,?,?)",
                [(f, name, r, o, pk, de, fl) for f, r, o, pk, de, fl in rows],
            )
            total += len(rows)
            print(f"  ✓ {name:<12} {len(rows):>6} 条 ｜ 累计 {total}｜{time.time()-t0:.0f}s", flush=True)
    con.commit()
    packs_now = con.execute("select count(distinct pack) from rows").fetchone()[0]
    rows_now = con.execute("select count(*) from rows").fetchone()[0]
    con.close()
    print(f"完成：新增 {total} 行 ｜ 现在 {packs_now} 包 / {rows_now} 行", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
