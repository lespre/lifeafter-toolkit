# -*- coding: utf-8 -*-
"""用「最长公共子串打分 + 互斥分配」把称号条目对到 PE csb，重合成动画。

规则（防串号）：
  分数 = 条目 anim_csb 词干 与 csb 内贴图路径 的最长公共子串长度
  要求 ≥ 10，按分数降序贪心分配；同一 csb 可以服务多个条目，但每条目只取最高分
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

PROJ = Path(r"E:\la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
from toolkit_core import android_gpk as AG  # noqa: E402
from toolkit_core.path_fid import fid_of  # noqa: E402
from board_io import write_board_pair  # noqa: E402
from title_anim_pace import frame_duration  # noqa: E402

WEB = PROJ / "02_wiki/web"
DB = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
PACKS = PROJ / "01_索引与产物/源包/pe_gres_android"
CSB_DIR = PROJ / "01_索引与产物/30_分析/title_csb_pe/gpk_all"
OUT = WEB / "assets/title_dyn/pe"
BOARD = WEB / "data/boards/title_catalog.json"
STR_RE = re.compile(rb"[ -~]{6,140}")
MAX_W, MAX_FRAMES, MIN_SCORE = 160, 40, 10


def lcs(a: str, b: str) -> int:
    best = 0
    prev = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best = cur[j]
        prev = cur
    return best


def frame_no(name: str) -> int:
    m = re.search(r"_(\d{2,4})\.png$", name)
    return int(m.group(1)) if m else 0


def main() -> int:
    # 清掉上一轮串号的产物
    for f in OUT.glob("csb_*.webp"):
        f.unlink()

    idx = json.loads((CSB_DIR / "index.json").read_text(encoding="utf-8"))
    csbs = []
    for it in idx:
        b = (CSB_DIR / it["file"]).read_bytes()
        tex = sorted({s.decode("ascii", "ignore") for s in STR_RE.findall(b)
                      if b"chenghao/" in s and s.endswith(b".png")}, key=frame_no)
        if tex:
            csbs.append({"file": it["file"], "textures": tex[:MAX_FRAMES],
                         "blob": " ".join(tex).lower()})
    board = json.loads(BOARD.read_text(encoding="utf-8"))

    pairs = []
    for it in board["items"]:
        csb = str(it.get("anim_csb") or "")
        if not csb:
            continue
        stem = csb.replace(chr(92), "/").rsplit("/", 1)[-1].removesuffix(".csb").lower()
        for c in csbs:
            sc = lcs(stem, c["blob"])
            if sc >= MIN_SCORE:
                pairs.append((sc, str(it.get("item_id")), stem, c))
    pairs.sort(key=lambda x: -x[0])
    chosen: dict[str, tuple] = {}
    for sc, iid, stem, c in pairs:
        if iid not in chosen:
            chosen[iid] = (sc, c)
    print("打分命中条目", len(chosen), "候选对", len(pairs), flush=True)

    # 解析贴图
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    def locate(n):
        base = n[:-4] if n.lower().endswith(".png") else n
        for cand in (f"ui/{base}", base, f"ui/{base}.ktx", base + ".ktx"):
            hx = "%016X" % (fid_of(cand) & 0xFFFFFFFFFFFFFFFF)
            r = con.execute("select pack,row from rows where fid=? limit 1", (hx,)).fetchone()
            if r:
                return r
        return None

    need = {}
    for iid, (sc, c) in chosen.items():
        for t in c["textures"]:
            if t not in need:
                need[t] = locate(t)
    by_pack = defaultdict(dict)
    for name, loc in need.items():
        if loc:
            by_pack[loc[0]][loc[1]] = name
    imgs = {}
    for pack, wants in by_pack.items():
        p = PACKS / pack
        if not p.is_file():
            continue
        for e in AG.iter_entries(str(p)):
            if e.get("row") in wants and e.get("payload"):
                try:
                    info = AG.parse_ktx(e["payload"])
                    arr = AG._ktx_rgba(e["payload"], info)
                    imgs[wants[e["row"]]] = Image.fromarray(np.ascontiguousarray(arr)).convert("RGBA")
                except Exception:
                    pass
    print("导出帧", len(imgs), flush=True)

    by_id = {str(i.get("item_id")): i for i in board["items"]}
    done = 0
    hashes = {}
    for iid, (sc, c) in chosen.items():
        frames = [imgs[t] for t in c["textures"] if t in imgs]
        if len(frames) < 2:
            continue
        w, h = frames[0].size
        if w > MAX_W:
            frames = [f.resize((MAX_W, max(1, int(h * MAX_W / w))), Image.LANCZOS) for f in frames]
        key = re.sub(r"[^0-9A-Za-z_]+", "_", iid)
        dst = OUT / f"csb_{key}.webp"
        frames[0].save(dst, save_all=True, append_images=frames[1:], duration=frame_duration(len(frames)), loop=0,
                       quality=60, method=4)
        h = hashlib.md5(dst.read_bytes()).hexdigest()
        hashes.setdefault(h, []).append(iid)
        it = by_id[iid]
        it["dyn_webp"] = f"assets/title_dyn/pe/csb_{key}.webp"
        it["dyn_webp_source"] = "PE csb 帧序列（%s，匹配分 %d）" % (c["file"], sc)
        done += 1
    write_board_pair(BOARD, board)
    dup = {h: v for h, v in hashes.items() if len(v) > 1}
    print("合成", done, "条 | 重复内容组", len(dup), "| 唯一", len(hashes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
