# -*- coding: utf-8 -*-
"""核对：CDN 清单（最新）vs 本地包；再把本地包与还原树抽查对齐。

只读。输出：本地哪些包已是最新、哪些缺失、树里的抽检命中率。
"""
from __future__ import annotations

import json
import pathlib
import sqlite3

ROOT = pathlib.Path("E:/la拆包项目")
MANIFEST = ROOT / "01_索引与产物/10_索引/cdn_20261101/npk_version_android4_playertest"
PACK_DIRS = [
    ROOT / "01_索引与产物/源包/pe_npk_full",
    ROOT / "01_索引与产物/源包/pe_npk_20261029",
    ROOT / "01_索引与产物/源包/pe_hotfix/20261030_2225",
]
TREE = ROOT / "01_索引与产物/41_还原树/pe"
NAMES_DB = ROOT / "01_索引与产物/10_索引/热更检测/names_join.sqlite3"


def main() -> int:
    raw = MANIFEST.read_text(encoding="utf-8", errors="ignore")
    m = json.loads(raw)
    files = m.get("files") or m.get("npk_files") or {}
    print("清单 version:", m.get("version"), "｜ 文件数:", len(files))

    local = {}
    for d in PACK_DIRS:
        if not d.is_dir():
            continue
        for p in d.rglob("*.npk"):
            local[p.name] = p

    have, stale, missing = 0, [], []
    for name, meta in files.items():
        size = meta.get("size") if isinstance(meta, dict) else meta
        p = local.get(name)
        if p is None:
            missing.append(name)
        elif size and p.stat().st_size != size:
            stale.append((name, p.stat().st_size, size))
        else:
            have += 1
    print(f"本地已是最新 {have} ｜ 大小不符 {len(stale)} ｜ 没有 {len(missing)}")
    for s in stale[:5]:
        print("   不符", s)
    big_missing = [n for n in missing if isinstance(files[n], dict) and (files[n].get("size") or 0) > 50_000_000]
    print("   缺失中 >50MB 的:", big_missing[:5], "共", len(big_missing))

    # 树抽查：按名字库把 fid 映射回路径，比对大小
    npk = local.get("res.layers.1.1.2.npk")
    if npk and NAMES_DB.is_file():
        con = sqlite3.connect(f"file:{NAMES_DB}?mode=ro", uri=True)
        cur = con.cursor()
        from importlib import util as _u
        spec = _u.spec_from_file_location(
            "gpk", ROOT / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描/gpk_reader.py"
        )
        mod = _u.module_from_spec(spec)
        spec.loader.exec_module(mod)
        try:
            g = mod.Gpk(npk)
        except Exception as _e:
            print('  （该包不是 HPGF 容器，跳过抽查：%s）' % str(_e)[:40])
            g = None
        if g is None:
            return 0
        ents = list(g.entries())
        step = max(1, len(ents) // 200)
        hit = miss = 0
        for e in ents[::step][:200]:
            row = cur.execute("select name from nm where fid=?", (e["fid"],)).fetchone()
            if not row:
                continue
            rel = row[0].replace("\\", "/")
            cand = TREE / "资源" / rel
            if cand.is_file() and cand.stat().st_size == e["decomp"]:
                hit += 1
            else:
                miss += 1
        print(f"树抽查（res.layers.1.1.2 采样）：命中 {hit} ｜ 缺/不符 {miss}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
