#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""export_equip_icons_to_master.py — 把装备冻结快照的 icon 导成
`assets/item_icons_full/<item_id>.png`，让「全量道具总表」里 10000–70000 段
（武器/护甲）的 icon_state 从「源已定位未导出」变成「已导出」。

数据源（只读）：
  30_分析/all_equips_全量_node索引_20261029/all_equips_attrs_{classic,kj1,yk}.json
    → 每个 key 的 icon（`ui/item_icon/...`，无扩展名）；跨服同号取 classic > kj1 > yk

两条取图路线：
  1. 复用已导出的 equip_icons（2026-11-01 用户定版的大图 _b 产物）：
     assets/equip_icons/_index.json 里 icon 路径 → png，直接 copy（同路径同图，不重解码）
  2. 没有 png 的路径 → pe_index.sqlite3 查 fid → 源包/pe_gres_android/*.gpk 取载荷解码

解码硬口径（与 fill_master_icons_full_export 一致）：
  载荷以 `CompBlks` 开头 → `pe_icon_bind.decoders.decode_compblks`；
  否则 ktx → `toolkit_core.android_gpk.parse_ktx` + `_ktx_rgba`。
  **禁止 texture2ddecoder.decode_astc**（出彩色噪声）。

只读 PE 源与冻结快照；不改 41_还原树；不读 E:/mrzh；不碰 APK。
报告：01_索引与产物/30_分析/export_equip_icons_to_master_report.json

用法：python tools/export_equip_icons_to_master.py [--dry-run] [--limit N]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image

PROJ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "01_索引与产物/10_索引/热更检测/pe_icon_bind"))
from toolkit_core.path_fid import fid_of  # noqa: E402
from toolkit_core import android_gpk as AG  # noqa: E402
import decoders as DEC  # noqa: E402

FREEZE = PROJ / "01_索引与产物/30_分析/all_equips_全量_node索引_20261029"
IDX = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
PACKS = PROJ / "01_索引与产物/源包/pe_gres_android"
WEB = PROJ / "02_wiki/web"
OUT = WEB / "assets/item_icons_full"
EQUIP_ICONS = WEB / "assets/equip_icons"
REPORT = PROJ / "01_索引与产物/30_分析/export_equip_icons_to_master_report.json"

# 主名/主图优先级：经典服为基准
ICON_FILES = [("all_equips_classic", "all_equips_attrs_classic.json"),
              ("all_equips_kj1", "all_equips_attrs_kj1.json"),
              ("all_equips_yk", "all_equips_attrs_yk.json")]
SUFFIXES = ("_b", "_s")


def con():
    return sqlite3.connect("file:%s?mode=ro" % str(IDX).replace("\\", "/"),
                           uri=True, timeout=30)


def fid_hex(p: str) -> str:
    return "%016X" % (fid_of(p) & 0xFFFFFFFFFFFFFFFF)


def probe(c, base: str):
    """(命中路径, pack, row)；_b 大图优先，退化 _s。"""
    for suf in SUFFIXES:
        p = base + suf + ".ktx"
        r = c.execute("select pack,row from rows where fid=? limit 1", (fid_hex(p),)).fetchone()
        if r:
            return p, r[0], r[1]
    return None


class Packs:
    def __init__(self):
        self._cache: dict[str, dict] = {}

    def entry(self, pack: str, row: int):
        if pack not in self._cache:
            self._cache[pack] = {e["row"]: e for e in AG.iter_entries(str(PACKS / pack))}
        return self._cache[pack].get(row)


def magenta_ratio(arr: np.ndarray) -> float:
    op = arr[:, :, 3] > 8
    n = int(op.sum())
    if n == 0:
        return 1.0
    px = arr[op]
    mag = (px[:, 0] > 240) & (px[:, 1] < 16) & (px[:, 2] > 240)
    return float(mag.sum()) / n


def decode_payload(pl: bytes):
    """CompBlks → decode_compblks；其余 → parse_ktx + _ktx_rgba。"""
    if pl.startswith(b"CompBlks"):
        return DEC.decode_compblks(pl)
    info = AG.parse_ktx(pl)
    if not info:
        return None
    return AG._ktx_rgba(pl, info)


def save(arr, dst: Path) -> bool:
    if arr is None or getattr(arr, "ndim", 0) != 3 or arr.shape[2] != 4:
        return False
    if arr.shape[0] < 8 or arr.shape[1] < 8:
        return False
    if magenta_ratio(arr) > 0.30:
        return False
    tmp = dst.parent / ("." + dst.name + ".tmp")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.ascontiguousarray(arr), "RGBA").save(tmp, "PNG", optimize=True)
    os.replace(tmp, dst)
    return True


def collect() -> tuple[dict[int, str], Counter]:
    """key → icon 路径（classic > kj1 > yk 首个非空），及各服行数。"""
    key2icon: dict[int, str] = {}
    rows = Counter()
    for ns, fname in ICON_FILES:
        d = json.loads((FREEZE / fname).read_text(encoding="utf-8"))
        rows[ns] = len(d["rows"])
        for r in d["rows"]:
            k = r.get("key")
            if not isinstance(k, int):
                continue
            ic = r.get("icon")
            ic = ic.strip() if isinstance(ic, str) else ""
            if k not in key2icon and ic.startswith("ui/"):
                key2icon[k] = ic
            else:
                key2icon.setdefault(k, "")
    return {k: v for k, v in key2icon.items() if v}, rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    key2icon, rows = collect()
    by_path: dict[str, list[int]] = {}
    for k, p in key2icon.items():
        by_path.setdefault(p, []).append(k)
    print(f"快照行：{' / '.join(f'{k} {v:,}' for k, v in rows.items())}")
    print(f"有 icon 的 key {len(key2icon):,}｜唯一图标路径 {len(by_path):,}")

    idx = {}
    p = EQUIP_ICONS / "_index.json"
    if p.exists():
        idx = json.loads(p.read_text(encoding="utf-8")).get("icons") or {}
    print(f"equip_icons 已导出路径 {sum(1 for v in idx.values() if v.get('png')):,}")

    # 待做：只处理目标文件还不存在、且路径还没有 png 的
    todo_paths = [ip for ip in by_path
                  if any(not (OUT / f"{k}.png").exists() for k in by_path[ip])]
    if args.limit:
        todo_paths = todo_paths[: args.limit]
    print(f"待处理路径 {len(todo_paths):,}")

    if args.dry_run:
        have = sum(1 for ip in todo_paths if (idx.get(ip) or {}).get("png"))
        print(f"dry-run：其中 {have:,} 条路径可直接复用 equip_icons，"
              f"{len(todo_paths) - have:,} 条需从 gpk 解码")
        return 0

    st = Counter()
    detail = {}
    c, packs = con(), Packs()
    OUT.mkdir(parents=True, exist_ok=True)
    for i, ip in enumerate(todo_paths, 1):
        ids = by_path[ip]
        arr = None
        route = None
        rec = idx.get(ip) or {}
        if rec.get("png"):
            try:
                arr = np.array(Image.open(WEB / rec["png"]).convert("RGBA"))
                route = "equip_icons"
            except Exception:                                     # noqa: BLE001
                arr = None
        if arr is None:
            h = probe(c, ip)
            if not h:
                detail[ip] = {"state": "缺图（客户端无素材）", "ids": ids}
                st["miss_no_asset"] += len(ids)
                continue
            hp, pack, row = h
            e = packs.entry(pack, row)
            if not e:
                st["miss_pack_row"] += len(ids)
                detail[ip] = {"state": "缺图（索引行取不到）", "ids": ids, "path": hp}
                continue
            try:
                arr = decode_payload(e.get("payload") or b"")
                route = "gpk_decode"
            except Exception as exc:                              # noqa: BLE001
                st["fail_decode"] += len(ids)
                detail[ip] = {"state": f"解码失败 {exc.__class__.__name__}", "ids": ids,
                              "path": hp}
                continue
        ok = 0
        for k in ids:
            dst = OUT / f"{k}.png"
            if dst.exists():
                st["skipped"] += 1
                continue
            if save(arr, dst):
                ok += 1
            else:
                st["fail_write"] += 1
        if ok:
            st[f"ok_{route}"] += ok
            detail[ip] = {"state": "已导出", "route": route, "n": ok, "ids": ids[:5]}
        if i % 100 == 0:
            print(f"  进度 {i}/{len(todo_paths)}｜导出 {st['ok_equip_icons'] + st['ok_gpk_decode']:,}",
                  flush=True)

    total_new = st["ok_equip_icons"] + st["ok_gpk_decode"]
    report = {"generated": "auto", "source": "all_equips_attrs_{classic,kj1,yk}.json (2026-11-01 冻结)",
              "keys_with_icon": len(key2icon), "unique_paths": len(by_path),
              "exported": total_new, "stats": dict(st), "paths": detail}
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print("导出", total_new, "张 →", OUT)
    print("统计", dict(st))
    print("报告", REPORT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
