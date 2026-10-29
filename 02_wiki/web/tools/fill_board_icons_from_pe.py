# -*- coding: utf-8 -*-
"""给 0% 的板块灌图标：board icon 字段 → fid → pe_index(pack,row) → gpk 行 → PNG。

链路（全部可复算）：
    icon 路径（去扩展名）→ 变体 '' / '_b' / '_s' / '_max' + '.ktx'
        （另试补 'ui/' 前缀）→ toolkit_core.path_fid.fid_of → pe_index rows(fid)
        → open_blocks 表取该行 (off,packed,decoded,flag) → 只解这一行
        → parse_ktx + decode_image → assets/img_cache/<board>/<id>.png
只写真命中的图；未命中/解不出的逐条记原因，不用别名图兜底。

用法：
    python fill_board_icons_from_pe.py --board chip_item_catalog [--max 8000]
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sqlite3
import struct
import sys
import time
import pathlib
from collections import Counter, defaultdict

import numpy as np
from PIL import Image


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core.path_fid import fid_of          # noqa: E402
from toolkit_core import android_gpk as AG         # noqa: E402

DET = PROJ / "01_索引与产物/10_索引/热更检测"
IDX_MAIN = DET / "pe_index.sqlite3"
IDX_FALLBACK = DET / "pe_index_v2.sqlite3"
PKGDIR = PROJ / "01_索引与产物/源包/pe_gres_android"
BOARDS = PROJ / "02_wiki/web/data/boards"
CACHE = PROJ / "02_wiki/web/assets/img_cache"
SUFFIXES = ("", "_b", "_s", "_max")


def open_index() -> tuple[sqlite3.Connection, str]:
    """优先新索引；被占用（另一进程在改名）时退到 v2（同 173 包同表结构）。"""
    for path, opts in ((IDX_MAIN, "mode=ro"), (IDX_FALLBACK, "mode=ro&immutable=1")):
        if not path.is_file():
            continue
        try:
            con = sqlite3.connect("file:%s?%s" % (str(path).replace("\\", "/"), opts),
                                  uri=True, timeout=3)
            con.execute("select 1 from rows limit 1").fetchone()
            return con, path.name
        except sqlite3.Error:
            continue
    raise SystemExit("没有可读的索引")


def variants(icon: str):
    """icon 字段 → (相对路径, 变体后缀) 生成器，按质量优先：原尺寸 → _b(大) → _s(小) → _max。"""
    base = icon.strip().replace("\\", "/")
    stem = re.sub(r"\.[A-Za-z0-9]{2,5}$", "", base)
    stems = [stem]
    if not stem.lower().startswith("ui/"):
        stems.append("ui/" + stem)
    for s in stems:
        for suf in SUFFIXES:
            yield s + suf + ".ktx", s, suf


def resolve(con: sqlite3.Connection, icon: str):
    for rel, stem, suf in variants(icon):
        r = con.execute("select pack,row from rows where fid=? limit 1",
                        ("%016X" % fid_of(rel),)).fetchone()
        if r:
            return {"rel": rel, "suffix": suf, "pack": r[0], "row": int(r[1])}
    return None


def export_pack(pack: str, wanted: dict[int, list[str]], outdir: pathlib.Path, stats: Counter):
    """wanted: {row: [id,...]} → 逐行解 PNG。返回 {id: (rel_path, pack, row)}。"""
    pkg = PKGDIR / pack
    if not pkg.is_file():
        stats["pack_missing"] += len(wanted)
        return {}
    _rec, spans, factory = AG.open_blocks(str(pkg))
    need = set(wanted)
    meta = {}
    for row, fid, off, packed, decoded, flag in factory():
        if row in need:
            meta[row] = (off, packed, decoded, flag)
    blob = pkg.read_bytes()
    done = {}
    for row, ids in wanted.items():
        m = meta.get(row)
        if not m:
            stats["row_missing"] += len(ids)
            continue
        off, packed, decoded, flag = m
        h = AG._base_of(spans, row) + off
        if h + 20 > len(blob):
            stats["oob"] += len(ids)
            continue
        hp, hd, _c1, _c2, hf = struct.unpack_from("<5I", blob, h)
        if (hp, hd, hf) != (packed, decoded, flag):
            stats["header_mismatch"] += len(ids)
            continue
        data = AG.decompress(blob[h + 20: h + 20 + packed], flag, decoded)
        if not data:
            stats["decompress_failed"] += len(ids)
            continue
        if data.startswith(b"\xabKTX"):
            info = AG.parse_ktx(data)
            if not info:
                stats["ktx_bad_header"] += len(ids)
                continue
            rec = {"kind": "ktx", "data": data, "info": info}
        elif data.startswith(b"DDS "):
            rec = {"kind": "dds", "data": data}
        elif data.startswith(b"\x89PNG"):
            rec = {"kind": "png", "data": data}
        elif data.startswith(b"CompBlks"):
            # 二级容器（CompBlks：8B magic + 20B 头 + 块数据），当前无已验证解码器 —— 不猜、落空
            stats["compblks_undecoded"] += len(ids)
            continue
        else:
            stats["not_image"] += len(ids)
            continue
        try:
            rgba = AG.decode_image(rec)
        except Exception:                                    # noqa: BLE001
            stats["decode_failed"] += len(ids)
            continue
        arr = np.asarray(rgba, dtype=np.uint8)
        if arr.ndim != 3 or arr.shape[2] != 4:
            stats["bad_array"] += len(ids)
            continue
        for iid in ids:
            dst = outdir / (iid + ".png")
            Image.fromarray(arr, "RGBA").save(dst)
            done[iid] = (pack, row)
            stats["png_written"] += 1
    return done


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--board", required=True)
    ap.add_argument("--max", type=int, default=8000)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    t0 = time.time()
    bpath = BOARDS / (a.board + ".json")
    board = json.loads(bpath.read_text(encoding="utf-8"))
    items = board["items"]
    con, idxname = open_index()
    print("板块 %s ｜ %d 条 ｜ 索引 %s" % (a.board, len(items), idxname))

    stats = Counter()
    by_pack: dict[str, dict[int, list[str]]] = defaultdict(lambda: defaultdict(list))
    resolved: dict[str, dict] = {}
    used = 0
    skipped_cap = 0
    for it in items:
        icon = it.get("icon") or ""
        if not icon:
            stats["no_icon_field"] += 1
            continue
        if used >= a.max:
            stats["cap_skipped"] += 1
            skipped_cap += 1
            continue
        used += 1
        r = resolve(con, icon)
        if not r:
            stats["fid_not_in_index"] += 1
            continue
        resolved[str(it["id"])] = r
        by_pack[r["pack"]][r["row"]].append(str(it["id"]))

    print("  待解 %d 条 ｜ 索引无 %d ｜ 超上限跳过 %d ｜ 包 %d 个"
          % (sum(len(v) for d in by_pack.values() for v in d.values()),
             stats["fid_not_in_index"], skipped_cap, len(by_pack)))
    if a.dry:
        print("  [dry] 各包条数", {k: sum(len(v) for v in d.values()) for k, d in by_pack.items()})
        return 0

    outdir = CACHE / a.board
    outdir.mkdir(parents=True, exist_ok=True)
    got: dict[str, tuple[str, int]] = {}
    for pack, wanted in sorted(by_pack.items(), key=lambda kv: -sum(len(v) for v in kv[1].values())):
        t1 = time.time()
        d = export_pack(pack, wanted, outdir, stats)
        got.update(d)
        print("  %-12s 目标 %5d 出图 %5d ｜ %.1fs（累计 %d）"
              % (pack, sum(len(v) for v in wanted.values()), len(d), time.time() - t1, len(got)))

    # ── 回写 _media ───────────────────────────────────────────
    n_before = sum(1 for it in items if (it.get("_media") or {}).get("images"))
    for it in items:
        iid = str(it["id"])
        if iid in got:
            pack, row = got[iid]
            it["_media"] = {"images": [{"png": "assets/img_cache/%s/%s.png" % (a.board, iid),
                                        "label": "图标", "pack": pack, "row": row}],
                            "total": 1}
    n_after = sum(1 for it in items if (it.get("_media") or {}).get("images"))

    bak = bpath.with_suffix(".json.bak_20261024_icons")
    if not bak.exists():
        shutil.copy2(bpath, bak)
    bpath.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")

    report = {
        "board": a.board, "items": len(items), "has_icon_field": len(items) - stats["no_icon_field"],
        "attempted": used, "cap": a.max, "cap_skipped": skipped_cap,
        "media_before": n_before, "media_after": n_after,
        "stats": dict(stats), "index": idxname, "seconds": round(time.time() - t0, 1),
        "backup": str(bak),
    }
    (DET / ("fill_icons_report_%s.json" % a.board)).write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print("完成：有图 %d/%d（前 %d）｜ 失败原因 %s ｜ %.1fs"
          % (n_after, len(items), n_before, dict(stats), time.time() - t0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
