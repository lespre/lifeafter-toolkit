# -*- coding: utf-8 -*-
"""按逻辑路径从 PE gpk 原样导出任意资源（mesh/gim/mtg/sfx/png…）。

用途：渲染/解析模型时绕开只服务图片的图片管线。
"""
from __future__ import annotations

import pathlib
import sqlite3
import sys

PROJ = pathlib.Path("E:/la拆包项目")
IDX = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
PACKS = PROJ / "01_索引与产物/源包/pe_gres_android"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
from toolkit_core.path_fid import fid_of  # noqa: E402
import pe_fetch as PE  # noqa: E402

AG = PE.AG


def find(path: str):
    con = sqlite3.connect(IDX)
    for cand in (path, path.rsplit(".", 1)[0] if "." in path else path):
        try:
            f = "%016X" % (fid_of(cand) & 0xFFFFFFFFFFFFFFFF)
        except Exception:  # noqa: BLE001
            continue
        r = con.execute("select pack,row,decoded,off from rows where fid=?", (f,)).fetchone()
        if r:
            return r
    return None


def extract(path: str, dst: pathlib.Path) -> bool:
    r = find(path) or find(path + ".ktx")
    if not r:
        return False
    pack, row, decoded, off = r
    for e in AG.iter_entries(str(PACKS / pack)):
        if e.get("row") != row:
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(bytes(e.get("payload") or b""))
        return True
    return False


def main() -> int:
    out = pathlib.Path(sys.argv[1])
    ok = 0
    for p in sys.argv[2:]:
        dst = out / pathlib.Path(p).name
        if extract(p, dst):
            print("ok  %-46s %d B" % (pathlib.Path(p).name, dst.stat().st_size))
            ok += 1
        else:
            print("miss %s" % p)
    print("导出 %d / %d" % (ok, len(sys.argv) - 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
