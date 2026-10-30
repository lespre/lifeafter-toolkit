# -*- coding: utf-8 -*-
"""列出 1110189 联动 sfx 引用的模型/贴图，并在 pe 索引里查可达性。"""
from __future__ import annotations

import pathlib
import re
import sqlite3
import sys

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core.path_fid import fid_of  # noqa: E402

BS = chr(92)
D = ROOT / "01_索引与产物/30_分析/sfx_1110189_联动_20261031"
PAT = re.compile(r"[A-Za-z0-9_\\/\.\-]+\.(?:gim|mesh|mtg|tga|spr|dds|ktx)")


def main() -> int:
    models, tex = set(), set()
    for p in D.glob("*.sfx"):
        t = p.read_text(encoding="utf-8", errors="ignore")
        for m in PAT.finditer(t):
            s = m.group(0).replace("/", BS)
            (tex if s.lower().endswith((".tga", ".spr", ".dds", ".ktx")) else models).add(s)
    con = sqlite3.connect(ROOT / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3")
    cur = con.cursor()

    for label, group in (("模型", models), ("贴图", tex)):
        print("== %s %d 个" % (label, len(group)))
        hit = miss = 0
        for s in sorted(group):
            f = "%016X" % fid_of(s)
            cur.execute("select pack,row,decoded from rows where fid=?", (f,))
            r = cur.fetchone()
            if r:
                hit += 1
                print("   ✓ %-58s %s row=%s %sB" % (pathlib.PureWindowsPath(s).name, r[0], r[1], r[2]))
            else:
                miss += 1
        print("   命中 %d ｜ 本地不可达 %d" % (hit, miss))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
