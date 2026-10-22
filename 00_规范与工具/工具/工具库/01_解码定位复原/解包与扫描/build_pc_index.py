# -*- coding: utf-8 -*-
"""建 PC 侧索引：扫客户端里的 .gpk，把 (fid, 包, 行, 偏移, 压缩/解压长度, flag) 落库。

与 pe 索引同一套块链读取器（toolkit_core.android_gpk.open_blocks），只读头、不解压载荷，
所以 60 个包 / 227 万行可以在几分钟内扫完。

用法：
    python build_pc_index.py                       # 默认扫 E:/mrzh 下 res / Documents/gres
    python build_pc_index.py --root E:/mrzh/res --out pc_index.sqlite3
    python build_pc_index.py --probe 3             # 只扫前 3 个包，验证用
"""
from __future__ import annotations

import argparse
import datetime
import pathlib
import sqlite3
import sys
import time

_here = pathlib.Path(__file__).resolve()
PROJ = next((u for u in _here.parents if (u / "00_规范与工具/治理").is_dir()), _here.parents[3])
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))

from toolkit_core import android_gpk as AG  # noqa: E402

DEFAULT_ROOTS = [
    pathlib.Path("E:/mrzh/res"),
    pathlib.Path("E:/mrzh/Documents/gres"),
    pathlib.Path("E:/mrzh"),
]
DEFAULT_OUT = PROJ / "01_索引与产物/30_分析/热更检测/pc_index.sqlite3"

SCHEMA = """
CREATE TABLE IF NOT EXISTS rows(
    fid TEXT NOT NULL,
    pack TEXT NOT NULL,
    row INTEGER NOT NULL,
    off INTEGER,
    packed INTEGER,
    decoded INTEGER,
    flag INTEGER,
    name TEXT
);
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT);
CREATE INDEX IF NOT EXISTS idx_rows_fid ON rows(fid);
CREATE INDEX IF NOT EXISTS idx_rows_pack ON rows(pack);
"""


def find_packs(roots: list[pathlib.Path]) -> list[pathlib.Path]:
    packs: list[pathlib.Path] = []
    seen: set[str] = set()
    for root in roots:
        if not root.is_dir():
            continue
        for p in sorted(root.glob("*.gpk")):
            if p.name in seen:          # res 与 gres 同名包只取先出现的
                continue
            seen.add(p.name)
            packs.append(p)
    return packs


def build(out: pathlib.Path, roots: list[pathlib.Path], probe: int | None, quiet: bool) -> int:
    packs = find_packs(roots)
    if probe:
        packs = packs[:probe]
    if not packs:
        print("没找到 .gpk，检查 --root", file=sys.stderr)
        return 2

    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    con = sqlite3.connect(str(out))
    con.executescript(SCHEMA)
    con.execute("INSERT OR REPLACE INTO meta VALUES(?,?)",
                ("generated", datetime.datetime.now().isoformat(timespec="seconds")))
    con.execute("INSERT OR REPLACE INTO meta VALUES(?,?)", ("roots", ";".join(map(str, roots))))

    total = 0
    for idx, pack in enumerate(packs, 1):
        t0 = time.time()
        try:
            _rec, _spans, factory = AG.open_blocks(pack)
            batch = []
            n = 0
            for row, fid, off, packed, decoded, flag in factory():
                batch.append(("%016X" % (int(fid) % (1 << 64)), pack.name, int(row),
                              int(off), int(packed), int(decoded), int(flag), None))
                n += 1
                if len(batch) >= 5000:
                    con.executemany("INSERT INTO rows VALUES(?,?,?,?,?,?,?,?)", batch)
                    batch.clear()
            if batch:
                con.executemany("INSERT INTO rows VALUES(?,?,?,?,?,?,?,?)", batch)
            con.commit()
            total += n
            if not quiet:
                print("[%d/%d] %-24s %7d 行  %.1fs" % (idx, len(packs), pack.name, n, time.time() - t0),
                      flush=True)
        except Exception as exc:  # noqa: BLE001
            print("[%d/%d] %-24s 失败：%r" % (idx, len(packs), pack.name, exc), flush=True)

    con.execute("INSERT OR REPLACE INTO meta VALUES(?,?)", ("rows", str(total)))
    con.execute("INSERT OR REPLACE INTO meta VALUES(?,?)", ("packs", str(len(packs))))
    con.commit()
    con.close()
    print("写出 %s ｜ %d 包 ｜ %d 行 ｜ %.1f MB"
          % (out, len(packs), total, out.stat().st_size / 1048576))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--root", action="append", help="客户端根目录，可多次传")
    ap.add_argument("--probe", type=int, help="只扫前 N 个包")
    ap.add_argument("-q", "--quiet", action="store_true")
    a = ap.parse_args()
    roots = [pathlib.Path(r) for r in a.root] if a.root else DEFAULT_ROOTS
    return build(pathlib.Path(a.out), roots, a.probe, a.quiet)


if __name__ == "__main__":
    raise SystemExit(main())
