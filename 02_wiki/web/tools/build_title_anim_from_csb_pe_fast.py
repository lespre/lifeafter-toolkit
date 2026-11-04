# -*- coding: utf-8 -*-
"""批量（按包一次扫）用 PE csb 帧贴图合成称号动画。

慢版逐张 img_fetch.export 每张 ~6s；这里改成：
  csb 里的贴图路径 → 候选名（ui/ 前缀、.ktx/.png）→ pe_index 一条 SQL 拿 (pack,row)
  → 按包分桶 → 每包 AG.iter_entries 一次 → 解 KTX → 合成 WebP
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


def frame_no(name: str) -> int:
    m = re.search(r"_(\d{2,4})\.png$", name)
    return int(m.group(1)) if m else 0


def resolve(names: list[str], con) -> dict[str, tuple[str, int]]:
    out = {}
    for n in names:
        base = n[:-4] if n.lower().endswith(".png") else n
        for cand in (f"ui/{base}", base, f"ui/{base}.ktx", f"ui/{base}.png", base + ".ktx"):
            hx = "%016X" % (fid_of(cand) & 0xFFFFFFFFFFFFFFFF)
            r = con.execute("select pack,row from rows where fid=? limit 1", (hx,)).fetchone()
            if r:
                out[n] = (r[0], r[1])
                break
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    idx = json.loads((CSB_DIR / "index.json").read_text(encoding="utf-8"))
    csbs = []
    for it in idx:
        b = (CSB_DIR / it["file"]).read_bytes()
        tex = sorted({s.decode("ascii", "ignore") for s in STR_RE.findall(b)
                      if b"chenghao/" in s and s.endswith(b".png")}, key=frame_no)
        if tex:
            csbs.append({"file": it["file"], "textures": tex[:MAX_FRAMES]})
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)

    # 1) 条目 ↔ csb
    jobs = []
    for it in board["items"]:
        csb = str(it.get("anim_csb") or "")
        if not csb:
            continue
        stem = csb.replace("\\", "/").rsplit("/", 1)[-1].removesuffix(".csb")
        tokens = [t for t in stem.split("_") if len(t) >= 5 and t not in ("main", "chenghao", "xuancai")]
        m = next((c for c in csbs if any(tok in " ".join(c["textures"]) for tok in tokens)), None)
        if m:
            jobs.append((it, stem, m))

    # 2) 全部路径解析 (pack,row)
    alltex = sorted({t for _i, _s, m in jobs for t in m["textures"]})
    loc = resolve(alltex, con)
    print("待导出贴图", len(alltex), "可定位", len(loc), flush=True)

    by_pack: dict[str, dict[int, str]] = defaultdict(dict)
    for name, (pack, row) in loc.items():
        by_pack[pack][row] = name
    imgs: dict[str, Image.Image] = {}
    for pack, need in by_pack.items():
        p = PACKS / pack
        if not p.is_file():
            continue
        for e in AG.iter_entries(str(p)):
            r = e.get("row")
            if r in need and e.get("payload"):
                try:
                    info = AG.parse_ktx(e["payload"])
                    arr = AG._ktx_rgba(e["payload"], info)
                    imgs[need[r]] = Image.fromarray(np.ascontiguousarray(arr)).convert("RGBA")
                except Exception:
                    pass
        print(" 包", pack, "解码累计", len(imgs), flush=True)

    done = 0
    for it, stem, m in jobs:
        frames = [imgs[t] for t in m["textures"] if t in imgs]
        if len(frames) < 2:
            continue
        w, h = frames[0].size
        if w > MAX_W:
            frames = [f.resize((MAX_W, max(1, int(h * MAX_W / w))), Image.LANCZOS) for f in frames]
        key = re.sub(r"[^0-9A-Za-z_]+", "_", stem)
        dst = OUT / f"csb_{key}.webp"
        frames[0].save(dst, save_all=True, append_images=frames[1:], duration=40, loop=0,
                       quality=60, method=4)
        it["dyn_webp"] = f"assets/title_dyn/pe/csb_{key}.webp"
        it["dyn_webp_source"] = "PE csb 帧序列（%s）" % m["file"]
        done += 1
        print(f"  {it.get('item_id')} {it.get('name')} ← {len(frames)} 帧", flush=True)

    write_board_pair(BOARD, board)
    print("合成", done, "条 / 任务", len(jobs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
