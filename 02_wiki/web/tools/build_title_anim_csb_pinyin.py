# -*- coding: utf-8 -*-
"""用「称号名拼音 == csb 贴图 basename」对号，再合成 PE 动画。

例：称号「此剑别人间」→ cijianbierenjian
    csb 里 chenghao/zhanshen/icon_chenghao_cijianbierenjian_00.png → 命中
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image
from pypinyin import lazy_pinyin

PROJ = Path(r"E:\la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
from toolkit_core import android_gpk as AG  # noqa: E402
from toolkit_core.path_fid import fid_of  # noqa: E402
from board_io import write_board_pair  # noqa: E402

WEB = PROJ / "02_wiki/web"
DB = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
PACKS = PROJ / "01_索引与产物/源包/pe_gres_android"
CSB_DIR = PROJ / "01_索引与产物/30_分析/title_csb_pe/gpk_all"
OUT = WEB / "assets/title_dyn/pe"
BOARD = WEB / "data/boards/title_catalog.json"
STR_RE = re.compile(rb"[ -~]{6,140}")
MAX_W, MAX_FRAMES = 160, 40


def py(s: str) -> str:
    s = re.sub(r"[\[【(（].*?[\]】)）]", "", s)
    return "".join(lazy_pinyin(s)).lower().replace(" ", "")


def frame_no(n: str) -> int:
    m = re.search(r"_(\d{2,4})\.png$", n)
    return int(m.group(1)) if m else 0


def main() -> int:
    for f in OUT.glob("csb_*.webp"):
        f.unlink()
    idx = json.loads((CSB_DIR / "index.json").read_text(encoding="utf-8"))
    csbs = []
    for it in idx:
        b = (CSB_DIR / it["file"]).read_bytes()
        tex = sorted({s.decode("ascii", "ignore") for s in STR_RE.findall(b)
                      if b"chenghao/" in s and s.endswith(b".png")}, key=frame_no)
        if len(tex) >= 2:
            csbs.append({"file": it["file"], "textures": tex[:MAX_FRAMES]})

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    jobs = []
    for it in board["items"]:
        if not it.get("anim_csb"):
            continue
        p = py(str(it.get("name") or ""))
        if len(p) < 6:
            continue
        for c in csbs:
            if any(p in t.lower().replace("icon_chenghao_", "").replace("chenghao_", "") for t in c["textures"]):
                jobs.append((it, c, p))
                break
    print("拼音命中条目", len(jobs), flush=True)

    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)

    def locate(n: str):
        base = n[:-4] if n.lower().endswith(".png") else n
        for cand in (f"ui/{base}", base, f"ui/{base}.ktx", base + ".ktx"):
            hx = "%016X" % (fid_of(cand) & 0xFFFFFFFFFFFFFFFF)
            r = con.execute("select pack,row from rows where fid=? limit 1", (hx,)).fetchone()
            if r:
                return r
        return None

    need = {}
    for _it, c, _p in jobs:
        for t in c["textures"]:
            need.setdefault(t, locate(t))
    by_pack = defaultdict(dict)
    for name, loc in need.items():
        if loc:
            by_pack[loc[0]][loc[1]] = name
    imgs = {}
    for pack, wants in by_pack.items():
        pth = PACKS / pack
        if not pth.is_file():
            continue
        for e in AG.iter_entries(str(pth)):
            if e.get("row") in wants and e.get("payload"):
                try:
                    info = AG.parse_ktx(e["payload"])
                    arr = AG._ktx_rgba(e["payload"], info)
                    imgs[wants[e["row"]]] = Image.fromarray(np.ascontiguousarray(arr)).convert("RGBA")
                except Exception:
                    pass
    print("导出帧", len(imgs), flush=True)

    done = 0
    hashes = defaultdict(list)
    for it, c, _p in jobs:
        frames = [imgs[t] for t in c["textures"] if t in imgs]
        if len(frames) < 2:
            continue
        w, h = frames[0].size
        if w > MAX_W:
            frames = [f.resize((MAX_W, max(1, int(h * MAX_W / w))), Image.LANCZOS) for f in frames]
        key = re.sub(r"[^0-9A-Za-z_]+", "_", str(it.get("item_id")))
        dst = OUT / f"csb_{key}.webp"
        frames[0].save(dst, save_all=True, append_images=frames[1:], duration=40, loop=0,
                       quality=60, method=4)
        hashes[hashlib.md5(dst.read_bytes()).hexdigest()].append(it.get("item_id"))
        it["dyn_webp"] = f"assets/title_dyn/pe/csb_{key}.webp"
        it["dyn_webp_source"] = "PE csb 帧序列（%s，拼音对号）" % c["file"]
        done += 1
    write_board_pair(BOARD, board)
    print("合成", done, "| 唯一内容", len(hashes), "| 重复组", {k: v for k, v in hashes.items() if len(v) > 1})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
