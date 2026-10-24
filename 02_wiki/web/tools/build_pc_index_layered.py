# -*- coding: utf-8 -*-
"""建分层 PC 索引：同一 fid 多份时按「包版本顺序」取最新，并记录候选数。

层序（低→高）：
  res/   基线包                  rank 0
  gres/  热更落地包，按包号升序  rank 1..n（0000 < 0006 < 0007）
本源内同名 fid 取 rank 最大者；同时写 candidates 数量，便于审计「当年有几个版本」。
"""
from __future__ import annotations

import pathlib
import re
import sqlite3

DET = pathlib.Path("E:/la拆包项目/01_索引与产物/30_分析/热更检测")
SRC = DET / "pc_index.sqlite3"
OUT = DET / "pc_index_layered.sqlite3"

NUM = re.compile(r"^(\d+)\.gpk$")


def rank_of(pack: str) -> tuple[int, int]:
    if NUM.match(pack):
        return (1, int(NUM.match(pack).group(1)))
    return (0, 0)


def main() -> int:
    src = sqlite3.connect(SRC)
    rows = src.execute("select fid,pack,row,off,packed,decoded,flag,name from rows").fetchall()
    print("源行", len(rows))

    best: dict[str, tuple] = {}
    cand: dict[str, int] = {}
    for r in rows:
        fid, pack = r[0], r[1]
        rk = rank_of(pack)
        cand[fid] = cand.get(fid, 0) + 1
        cur = best.get(fid)
        if cur is None or rk > cur[1]:
            best[fid] = (r, rk)

    if OUT.exists():
        OUT.unlink()
    out = sqlite3.connect(OUT)
    out.execute("""create table rows(
        fid text primary key, pack text, row int, off int, packed int, decoded int,
        flag int, name text, layer int, pack_no int, candidates int)""")
    out.executemany("insert into rows values(?,?,?,?,?,?,?,?,?,?,?)",
                    [(*v[0], v[1][0], v[1][1], cand[v[0][0]]) for v in best.values()])
    out.execute("create table meta(key text primary key, value text)")
    out.executemany("insert into meta values(?,?)", [
        ("generated", "2026-10-24"),
        ("source", str(SRC)),
        ("source_rows", str(len(rows))),
        ("unique_fid", str(len(best))),
        ("dup_fid", str(sum(1 for c in cand.values() if c > 1))),
        ("policy", "layer_rank: res=0, gres按包号升序(1..n)；同 fid 取 rank 最大"),
    ])
    out.commit()

    dup = sum(1 for c in cand.values() if c > 1)
    print("唯一 fid", len(best), "｜ 多版本 fid", dup)
    for fid, c in list(sorted(((k, v) for k, v in cand.items() if v > 1), key=lambda x: -x[1]))[:3]:
        print("  样本", fid, "候选", c, "选中包", best[fid][0][1], "rank", best[fid][1])
    print("写出", OUT, OUT.stat().st_size // 1024, "KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
