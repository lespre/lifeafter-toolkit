# -*- coding: utf-8 -*-
"""用 PE 里的 csb 帧贴图合成称号动画（纯 PE 源）。

链路：PE csb 里写的 chenghao/**/*.png → img_fetch 从 PE 包导出 → 按文件名序号排帧
      → 合成循环 WebP → assets/title_dyn/pe/csb_<key>.webp → 回填 item.dyn_webp
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image

PROJ = Path(r"E:\la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
from toolkit_core import img_fetch as IF  # noqa: E402
from board_io import write_board_pair  # noqa: E402
from title_anim_pace import frame_duration  # noqa: E402

WEB = PROJ / "02_wiki/web"
CSB_DIR = PROJ / "01_索引与产物/30_分析/title_csb_pe/gpk_all"
OUT = WEB / "assets/title_dyn/pe"
BOARD = WEB / "data/boards/title_catalog.json"
STR_RE = re.compile(rb"[ -~]{6,140}")
MAX_W, MAX_FRAMES = 160, 40


def frame_no(name: str) -> int:
    m = re.search(r"_(\d{2,4})\.png$", name)
    return int(m.group(1)) if m else 0


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    idx = json.loads((CSB_DIR / "index.json").read_text(encoding="utf-8"))
    csbs = []
    for it in idx:
        b = (CSB_DIR / it["file"]).read_bytes()
        tex = sorted({s.decode("ascii", "ignore") for s in STR_RE.findall(b)
                      if b"chenghao/" in s and s.endswith(b".png")}, key=frame_no)
        if tex:
            csbs.append({"file": it["file"], "textures": tex})
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    tmp = Path(tempfile.mkdtemp(prefix="titlepe_"))
    done = 0

    for it in board["items"]:
        csb = str(it.get("anim_csb") or "")
        if not csb:
            continue
        stem = csb.replace("\\", "/").rsplit("/", 1)[-1].removesuffix(".csb")
        tokens = [t for t in stem.split("_") if len(t) >= 5 and t not in ("main", "chenghao", "xuancai")]
        match = next((c for c in csbs if any(tok in " ".join(c["textures"]) for tok in tokens)), None)
        if not match:
            continue
        tex = match["textures"][:MAX_FRAMES]

        def grab(t: str) -> Path | None:
            base = t[:-4]  # 去 .png，img_fetch 自己补 .ktx/.png
            out = tmp / (base.replace("/", "_") + ".png")
            try:
                src = IF.export(base, out)
            except Exception:
                return None
            return out if out.is_file() and src == "pe" else None

        with ThreadPoolExecutor(max_workers=8) as ex:
            files = [p for p in ex.map(grab, tex) if p]
        if len(files) < 2:
            continue
        imgs = [Image.open(f).convert("RGBA") for f in files]
        w, h = imgs[0].size
        if w > MAX_W:
            imgs = [im.resize((MAX_W, max(1, int(h * MAX_W / w))), Image.LANCZOS) for im in imgs]
        key = re.sub(r"[^0-9A-Za-z_]+", "_", stem)
        dst = OUT / f"csb_{key}.webp"
        imgs[0].save(dst, save_all=True, append_images=imgs[1:], duration=frame_duration(len(imgs)), loop=0, quality=60, method=4)
        it["dyn_webp"] = f"assets/title_dyn/pe/csb_{key}.webp"
        it["dyn_webp_source"] = "PE csb 帧序列（%s）" % match["file"]
        done += 1
        print(f"{it.get('item_id')} {it.get('name')} ← {len(imgs)} 帧 {key}", flush=True)

    write_board_pair(BOARD, board)
    print("合成", done, "条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
