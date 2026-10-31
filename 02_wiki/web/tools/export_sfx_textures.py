# -*- coding: utf-8 -*-
"""按 .sfx 引用的贴图名，从 CDN 索引定位 .ktx 并导出 PNG（这才是原始贴图）。

关键发现：.sfx 写 .tga，客户端实际存的是同名 .ktx —— 换扩展名后 33/33 全命中。
"""
from __future__ import annotations

import json
import pathlib
import re
import sqlite3
import sys

import numpy as np
from PIL import Image

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"))
from toolkit_core.path_fid import fid_of  # noqa: E402
from toolkit_core import android_gpk as AG  # noqa: E402
from la_unpack_core import NpkArchive  # noqa: E402

SFX = ROOT / "01_索引与产物/30_分析/sfx_1110189_联动_20261031"
IDX = ROOT / "01_索引与产物/10_索引/cdn_index.sqlite3"
NJ = ROOT / "01_索引与产物/10_索引/热更检测/names_join.sqlite3"
PACKS = ROOT / "01_索引与产物/源包/pe_npk_20261029"
OUT = ROOT / "_截图/sfx_textures_real"
PAT = re.compile(r"[A-Za-z0-9_\\/\.\-]+\.(?:tga|spr)")


def main() -> int:
    names = set()
    for p in SFX.glob("*.sfx"):
        t = p.read_text(encoding="utf-8", errors="ignore")
        for m in PAT.finditer(t):
            names.add(pathlib.PureWindowsPath(m.group(0)).name.lower())

    nj = sqlite3.connect(NJ)
    idx = sqlite3.connect(IDX)
    pack_cache: dict[str, NpkArchive] = {}

    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.png"):
        old.unlink()

    meta = []
    for n in sorted(names):
        cur = nj.execute("select name from nm where lower(name) like ?", ("%" + n,))
        full = next((r[0] for r in cur.fetchall()
                     if pathlib.PureWindowsPath(r[0]).name.lower() == n), None)
        if not full:
            print("✗ 无全路径", n)
            continue
        cand = re.sub(r"\.tga$", ".ktx", full, flags=re.I)
        fid = fid_of(cand)
        row = idx.execute("select pack,row from entries where fid_hi=? and fid_lo=? limit 1",
                          ((fid >> 32) & 0xFFFFFFFF, fid & 0xFFFFFFFF)).fetchone()
        if not row:
            print("✗ 索引未命中", n)
            continue
        pack, r = row
        a = pack_cache.get(pack) or NpkArchive(str(PACKS / pack.split("/")[-1]))
        pack_cache[pack] = a
        try:
            d = a.read_entry(entry_index=r)
            info = AG.parse_ktx(d)
            rgba = AG._ktx_rgba(d, info)
            if rgba is None:
                print("✗ 解码返回空", n)
                continue
            img = Image.fromarray(np.asarray(rgba, dtype=np.uint8), "RGBA")
            out = OUT / (pathlib.PureWindowsPath(n).stem + ".png")
            img.save(out)
            meta.append({"name": n, "pack": pack, "row": r, "w": info["width"],
                         "h": info["height"], "fmt": info["fmt_name"], "png": out.name})
            print("✓ %-30s %-24s %4d×%-4d %s" % (n, pack, info["width"], info["height"], info["fmt_name"]))
        except Exception as exc:                                # noqa: BLE001
            print("✗ %-30s %s" % (n, str(exc)[:60]))

    (OUT / "manifest.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print("导出", len(meta), "→", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
