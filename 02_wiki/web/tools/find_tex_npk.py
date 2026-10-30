# -*- coding: utf-8 -*-
"""在 pe_npk_full 的所有 npk 里按 fid 找特效贴图（名字→fid→容器行），命中可导出。

用法：python find_tex_npk.py [--export] [--verbose]
"""
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
BS = chr(92)


def target_names() -> list[str]:
    names = set()
    for p in D.glob("*.sfx"):
        t = p.read_text(encoding="utf-8", errors="ignore")
        for m in PAT.finditer(t):
            names.add(pathlib.PureWindowsPath(m.group(0).replace("/", BS)).name.lower())
    return sorted(names)


def fids_of(names: list[str]) -> dict[int, str]:
    con = sqlite3.connect(NJ)
    cur = con.cursor()
    out: dict[int, str] = {}
    for n in names:
        cur.execute("select fid, name from nm where name like ? limit 1", ("%" + n,))
        r = cur.fetchone()
        if r:
            out[int(r[0], 16)] = r[1]
    return out


def main(argv: list[str]) -> int:
    names = target_names()
    fmap = fids_of(names)
    print("目标贴图 %d 个（按文件名），名字字典解析出 fid %d 个" % (len(names), len(fmap)))

    npks = sorted((ROOT / "01_索引与产物/源包/pe_npk_full").rglob("*.npk"))
    print("扫描 npk %d 个" % len(npks))
    found: dict[int, tuple[pathlib.Path, int]] = {}
    for npk in npks:
        try:
            a = NpkArchive(str(npk))
        except Exception:                                   # noqa: BLE001
            continue
        n0 = len(found)
        for e in a._entries:
            if e.file_id in fmap and e.file_id not in found:
                found[e.file_id] = (npk, e.entry_index)
        if len(found) != n0 or "--verbose" in argv:
            print("  %-46s entries %7d ｜ 新命中 %d（累计 %d）"
                  % (npk.name, len(a._entries), len(found) - n0, len(found)))

    print("\n命中 %d / %d" % (len(found), len(fmap)))
    for fid, (npk, row) in found.items():
        print("  ✓ %-52s %s row=%d" % (fmap[fid], npk.name, row))

    if "--export" in argv and found:
        outdir = D / "textures"
        outdir.mkdir(exist_ok=True)
        for fid, (npk, row) in found.items():
            try:
                data = NpkArchive(str(npk)).read_entry(entry_index=row)
            except Exception as exc:                        # noqa: BLE001
                print("  导出失败", fmap[fid], exc)
                continue
            name = pathlib.PureWindowsPath(fmap[fid]).name
            (outdir / name).write_bytes(data)
            print("  →", name, len(data), "B")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
