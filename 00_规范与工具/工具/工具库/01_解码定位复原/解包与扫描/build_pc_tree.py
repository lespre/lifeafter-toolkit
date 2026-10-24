# -*- coding: utf-8 -*-
"""PC 还原树构建：pc_index 行 → 按 PE 名字表还原路径落盘。

用法：
  python build_pc_tree.py --probe 1          # 只跑第 1 个包，验证
  python build_pc_tree.py --workers 4        # 全量
  python build_pc_tree.py --pack ui_01.gpk   # 单包
"""
from __future__ import annotations

import argparse
import multiprocessing as mp
import os
import sqlite3
import sys
import time
from pathlib import Path

_here = Path(__file__).resolve()
PROJ = next((u for u in _here.parents if (u / "00_规范与工具/治理").is_dir() and (u / "00_规范与工具/工具").is_dir()), _here.parents[3])
DET = PROJ / "01_索引与产物/10_索引/热更检测"
PC_IDX = DET / "pc_index.sqlite3"
PE_IDX = DET / "pe_index.sqlite3"
TREE = PROJ / "01_索引与产物/41_还原树/pc"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))

from toolkit_core import android_gpk as AG  # noqa: E402
import pc_fetch as PF  # noqa: E402

PACK_ROOTS = [Path("E:/mrzh"), Path("E:/mrzh/res"),
              Path("E:/mrzh/Documents"), Path("E:/mrzh/Documents/gres")]


def find_pack(pack: str) -> Path | None:
    for root in PACK_ROOTS:
        p = root / pack
        if p.is_file():
            return p
    for root in PACK_ROOTS:
        if root.is_dir():
            for hit in root.rglob(pack):
                if hit.is_file():
                    return hit
    return None


def names_for_pack(pack: str) -> dict[int, str]:
    con = sqlite3.connect("file:%s?mode=ro" % PC_IDX.as_posix(), uri=True)
    fids = [r[0] for r in con.execute("select fid from rows where pack=?", (pack,))]
    con.close()
    out: dict[int, str] = {}
    if not fids:
        return out
    pe = sqlite3.connect("file:%s?mode=ro" % PE_IDX.as_posix(), uri=True)
    for i in range(0, len(fids), 900):
        chunk = fids[i:i + 900]
        q = "select fid,name from rows where name<>'' and fid in (%s)" % ",".join("?" * len(chunk))
        for fid, name in pe.execute(q, chunk):
            try:
                out[int(fid, 16)] = name          # 索引里 fid 是 HEX 文本，条目里是 int
            except (TypeError, ValueError):
                continue
    pe.close()
    return out


def run_pack(pack: str) -> tuple[str, int, int, int, float]:
    src = find_pack(pack)
    if not src:
        return pack, 0, 0, 0, 0.0
    nm = names_for_pack(pack)
    written = skipped = failed = 0
    t0 = time.time()
    for e in AG.iter_entries(str(src)):
        fid = e["fid"]
        name = nm.get(fid if isinstance(fid, int) else int(str(fid), 16))
        if not name:
            continue
        if "_未命名" in name:          # PE 里的占位名，不是真路径
            skipped += 1
            continue
        rel = name.replace("\\", "/").lstrip("/")
        out = TREE / rel
        if out.exists():
            skipped += 1
            continue
        data = e.get("payload")
        if data is None:
            failed += 1
            continue
        try:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(data)
            written += 1
        except OSError:
            failed += 1
    return pack, written, skipped, failed, time.time() - t0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack")
    ap.add_argument("--out", help="输出根目录（默认 41_还原树/pc）")
    ap.add_argument("--root", action="append", help="客户端根目录，可多次传（默认 E:/mrzh 系列）")
    ap.add_argument("--probe", type=int)
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()

    global TREE, PACK_ROOTS
    if a.out:
        TREE = Path(a.out)
    if a.root:
        PACK_ROOTS = [Path(x) for x in a.root]

    con = sqlite3.connect("file:%s?mode=ro" % PC_IDX.as_posix(), uri=True)
    packs = [r[0] for r in con.execute("select distinct pack from rows order by pack")]
    con.close()
    if a.pack:
        packs = [a.pack]
    elif a.probe:
        packs = packs[:a.probe]

    TREE.mkdir(parents=True, exist_ok=True)
    print("PC 树 → %s ｜ 包 %d ｜ 进程 %d" % (TREE, len(packs), a.workers))
    tw = ts = tf = 0
    if a.workers <= 1:
        it = map(run_pack, packs)
    else:
        it = mp.Pool(a.workers).imap_unordered(run_pack, packs)
    for i, (pack, w, s, f, dt) in enumerate(it, 1):
        tw += w
        ts += s
        tf += f
        print("[%d/%d] %-28s 写 %6d 跳 %6d 失败 %4d  %5.1fs"
              % (i, len(packs), pack, w, s, f, dt), flush=True)
    print("合计：写 %d ｜ 跳过 %d ｜ 失败 %d" % (tw, ts, tf))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
