# -*- coding: utf-8 -*-
"""【已停用】用 PE 原生帧贴图按「家族」重建称号动画（不依赖 csb、不碰 PC）。

⚠️ 2026-11-07 复核判定此口径**错误**：按 ui/chenghao/<家族> 取帧会把同一家族下
不同变体的不同底图当成一个序列（ugc 三张完全不同的牌、miwuhaiyu 三个不同图标、
tianxie/kumufengchun 多款混帧），播放时底图乱跳；且用 `key in anim_csb` 子串
把同一份动画挂给十几张卡。⇒ 默认拒绝执行，产物 assets/title_dyn/pe/ 不再被引用。
**现行口径 = build_title_dyn_sequences.py**（按 item.dyn_tex 精确帧序列）。
确需复现旧产物做回归比对时，显式加 `--legacy`。
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

PROJ = Path(r"E:\la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
from toolkit_core import android_gpk as AG  # noqa: E402
from board_io import write_board_pair  # noqa: E402
from title_anim_pace import frame_duration  # noqa: E402

DB = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
PACKS = PROJ / "01_索引与产物/源包/pe_gres_android"
WEB = PROJ / "02_wiki/web"
OUT = WEB / "assets/title_dyn/pe"
BOARD = WEB / "data/boards/title_catalog.json"
MAX_W = 160
MAX_FRAMES = 40


def frames_by_family() -> dict[str, list[tuple[str, str, int]]]:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    rows = con.execute(
        "select name,pack,row from rows where name like 'ui/chenghao/%' "
        "and (name like '%loop%' or name like '%_00%') order by name").fetchall()
    fam: dict[str, list] = defaultdict(list)
    for name, pack, row in rows:
        m = re.match(r"ui/chenghao/([^/]+)/", name)
        if m:
            fam[m.group(1)].append((name, pack, row))
    return fam


def decode_frames(entries: list[tuple[str, str, int]], limit: int = MAX_FRAMES) -> list[Image.Image]:
    by_pack: dict[str, dict[int, str]] = defaultdict(dict)
    for name, pack, row in entries:
        by_pack[pack][row] = name
    if len(entries) > limit:
        step = len(entries) / limit
        entries = [entries[int(i * step)] for i in range(limit)]
        by_pack = defaultdict(dict)
        for name, pack, row in entries:
            by_pack[pack][row] = name
    out: dict[str, Image.Image] = {}
    for pack, need in by_pack.items():
        p = PACKS / pack
        if not p.is_file():
            continue
        try:
            for e in AG.iter_entries(str(p)):
                row = e.get("row")
                data = e.get("payload")
                if row in need and data:
                    info = AG.parse_ktx(data)
                    arr = AG._ktx_rgba(data, info)
                    out[need[row]] = Image.fromarray(np.ascontiguousarray(arr)).convert("RGBA")
        except Exception as exc:  # noqa: BLE001
            print("  包读取失败", pack, type(exc).__name__, exc)
    return [out[n] for n, _p, _r in entries if n in out]


def main() -> int:
    if "--legacy" not in sys.argv[1:]:
        print("已停用：按家族拼帧会把不同变体的底图轮流播放（2026-11-07 复核）。\n"
              "现行口径请跑 build_title_dyn_sequences.py；需复现旧产物请显式加 --legacy。")
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    fam = frames_by_family()
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    done = 0
    for key, entries in sorted(fam.items()):
        if len(entries) < 3:
            continue
        print(f"家族 {key}: {len(entries)} 帧")
        imgs = decode_frames(entries)
        if len(imgs) < 3:
            print("  解码不足，跳过", len(imgs))
            continue
        w, h = imgs[0].size
        if w > MAX_W:
            imgs = [im.resize((MAX_W, int(h * MAX_W / w)), Image.LANCZOS) for im in imgs]
        dst = OUT / f"{key}.webp"
        imgs[0].save(dst, save_all=True, append_images=imgs[1:], duration=frame_duration(len(imgs)), loop=0,
                     quality=60, method=4)
        for it in board["items"]:
            csb = str(it.get("anim_csb") or "")
            if key in csb:
                it["dyn_webp"] = f"assets/title_dyn/pe/{key}.webp"
                it["dyn_webp_source"] = "PE 原生帧贴图（ui/chenghao/%s，无需 csb）" % key
                done += 1
        print("  →", dst.name, f"{len(imgs)} 帧")
    write_board_pair(BOARD, board)
    print("回填", done, "条；家族", len(fam))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
