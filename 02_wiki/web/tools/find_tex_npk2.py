# -*- coding: utf-8 -*-
"""按「文件名精确匹配」解析特效贴图 fid，并在 pe_npk_full 里定位/导出。"""
from __future__ import annotations

import pathlib
import re
import sqlite3
import sys

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"))
from la_unpack_core import NpkArchive  # noqa: E402

D = ROOT / "01_索引与产物/30_分析/sfx_1110189_联动_20261031"
NJ = ROOT / "01_索引与产物/10_索引/热更检测/names_join.sqlite3"
PAT = re.compile(r"[A-Za-z0-9_\\/\.\-]+\.(?:tga|spr|dds|ktx)")


def targets() -> list[str]:
    s = set()
    for p in D.glob("*.sfx"):
        t = p.read_text(encoding="utf-8", errors="ignore")
        for m in PAT.finditer(t):
            s.add(pathlib.PureWindowsPath(m.group(0).replace("/", chr(92))).name.lower())
    return sorted(s)


def main(argv: list[str]) -> int:
    names = targets()
    con = sqlite3.connect(NJ)
    cur = con.cursor()
    fmap: dict[int, str] = {}
    unresolved = []
    for n in names:
        cur.execute("select fid, name from nm where lower(name) like ?", ("%" + n,))
        rows = [(int(f, 16), p) for f, p in cur.fetchall()
                if pathlib.PureWindowsPath(p).name.lower() == n]
        if rows:
            fmap[rows[0][0]] = rows[0][1]
        else:
            unresolved.append(n)
    print("目标 %d ｜ 精确 fid %d ｜ 未解析 %d" % (len(names), len(fmap), len(unresolved)))
    if unresolved:
        print("   未解析样例:", unresolved[:8])

    found: dict[int, tuple[pathlib.Path, int]] = {}
    for npk in sorted((ROOT / "01_索引与产物/源包/pe_npk_full").rglob("*.npk")):
        try:
            a = NpkArchive(str(npk))
        except Exception:                                   # noqa: BLE001
            continue
        n0 = len(found)
        for e in a._entries:
            if e.file_id in fmap and e.file_id not in found:
                found[e.file_id] = (npk, e.entry_index)
        if len(found) != n0:
            print("  %-44s +%d（累计 %d）" % (npk.name, len(found) - n0, len(found)))

    print("\n定位 %d / %d" % (len(found), len(fmap)))
    for fid, (npk, row) in found.items():
        print("  ✓ %-56s %s row=%d" % (pathlib.PureWindowsPath(fmap[fid]).name, npk.name, row))

    if "--export" in argv and found:
        out = D / "textures"
        out.mkdir(exist_ok=True)
        for fid, (npk, row) in found.items():
            try:
                data = NpkArchive(str(npk)).read_entry(entry_index=row)
            except Exception as exc:                        # noqa: BLE001
                print("  导出失败", fmap[fid], str(exc)[:40])
                continue
            p = out / pathlib.PureWindowsPath(fmap[fid]).name
            p.write_bytes(data)
            print("  → %-40s %7d B" % (p.name, len(data)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
