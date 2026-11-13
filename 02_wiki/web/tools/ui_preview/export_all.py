# -*- coding: utf-8 -*-
"""批量导出全部 CSB 面板 → HTML 页面 + 缩略图。

产物
  _ui_preview/<面板>/<面板>.html   每个面板一页
  _ui_preview/<面板>/<面板>.meta.json
  _ui_preview/assets/*.png        全局解码后的贴图（按目录+文件名去重）
  _ui_preview/thumbs/*.png        缩略图（420px 宽）

CLI
  export_all.py [--limit N] [--no-thumb] [--only a,b,c]
"""
from __future__ import annotations

import json
import math
import shutil
import subprocess
import sys
import time
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import la_paths  # noqa: E402
import csb2html  # noqa: E402
from csb2json import ui_dir  # noqa: E402

OUT_ROOT = csb2html.OUT_ROOT
THUMB_DIR = OUT_ROOT / "thumbs"
CHROME = pathlib.Path(
    r"C:\Program Files\Google\Chrome\Application\chrome.exe")
THUMB_W = 420


def shoot(page: pathlib.Path, dst: pathlib.Path, w: float, h: float) -> bool:
    """用无头 Chrome 截一张缩略图（只截舞台，不截页头页脚）。"""
    k = THUMB_W / w
    vw = THUMB_W
    vh = max(1, int(math.ceil(h * k)))
    cmd = [
        str(CHROME), "--headless=new", "--disable-gpu", "--hide-scrollbars",
        "--allow-file-access-from-files", "--force-device-scale-factor=1",
        "--virtual-time-budget=3500",
        f"--window-size={vw},{vh}",
        f"--screenshot={dst}",
        page.as_uri() + "?thumb=1",
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=90)
    except subprocess.TimeoutExpired:
        return False
    return dst.exists() and r.returncode == 0


def main(argv: list[str]) -> int:
    only = None
    limit = 0
    do_thumb = "--no-thumb" not in argv
    for a in argv:
        if a.startswith("--limit="):
            limit = int(a.split("=", 1)[1])
        if a.startswith("--only="):
            only = {x.strip() for x in a.split("=", 1)[1].split(",") if x.strip()}

    files = sorted(ui_dir().glob("*.csb"))
    if only:
        files = [f for f in files if f.stem in only]
    if limit:
        files = files[:limit]

    if not CHROME.exists():
        do_thumb = False
        print("[warn] 没找到 Chrome，跳过缩略图")

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    csb2html.ASSET_DIR.mkdir(parents=True, exist_ok=True)
    if do_thumb:
        THUMB_DIR.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    ok = fail = thumb_ok = 0
    no_thumb = []
    for i, csb in enumerate(files, 1):
        out_dir = OUT_ROOT / csb.stem
        try:
            page = csb2html.build(csb, out_dir)
            ok += 1
        except Exception as e:                                # noqa: BLE001
            fail += 1
            print(f"[fail] {csb.name}: {e}")
            continue
        if do_thumb:
            meta = json.loads((out_dir / (csb.stem + ".meta.json"))
                              .read_text(encoding="utf-8"))
            w, h = meta["stage"]
            dst = THUMB_DIR / (csb.stem + ".png")
            if shoot(page, dst, w, h):
                thumb_ok += 1
            else:
                no_thumb.append(csb.stem)
        if i % 20 == 0:
            print(f"  …{i}/{len(files)}  {time.time()-t0:.0f}s", flush=True)

    print(f"完成：页面 {ok} 失败 {fail}，缩略图 {thumb_ok}"
          f"，耗时 {time.time()-t0:.0f}s")
    if no_thumb:
        print("无缩略图:", ", ".join(no_thumb[:20]), "…" if len(no_thumb) > 20 else "")
    return 0 if not fail else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
