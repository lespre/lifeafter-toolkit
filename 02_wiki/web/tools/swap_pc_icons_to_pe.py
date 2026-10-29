# -*- coding: utf-8 -*-
"""把图里「来自 PC 包」的那批，尽量换成 PE 直导；PE 缺卷取不到的，明确降级标注。

═══════════════════════════════════════════════════════════════════════════
★ 背景

  `_media.images[*]` 里有 80 张 source 写着「性别补图（PC）」「fashion_data.icons → PC(ui_01)」。
  这些 base **全部落在卡片的 `icons_all[*].path` 里**（即路径是表里的权威路径，
  图内容没有张冠李戴），只是当年 PE 缺图时从 PC 备份导的。

  用户口径：图只认 PE。所以：
    · PE 能取到 → 重新按 PE 导一遍，source 改成 PE，去掉 pc 痕迹
    · PE 取不到（包缺卷）→ **保留这张图**（内容对，删了只会变空白），
      但 `fetch` 标 `pc_fallback`、`source` 写明「PE 缺卷，图取自 PC 备份」，
      并在卡上 `icon_note` 留一句说明，避免以后又被当成"PE 原生图"。

★ 用法
    python swap_pc_icons_to_pe.py --dry
    python swap_pc_icons_to_pe.py
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import sys
import time


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
WEB = PROJ / "02_wiki/web"
BOARD = WEB / "data/boards/fashion_wardrobe.json"
BOARD_JS = WEB / "data/boards/fashion_wardrobe.js"
OUT = WEB / "assets/fashion_posters"
ICON_DIR = "ui/item_icon"

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
import pe_fetch  # noqa: E402

EXT_RE = re.compile(r"\.(ktx|png|bc7|dds)$", re.I)
SUF_RE = re.compile(r"_[bs]$")


def logical(x: str) -> str:
    s = (x or "").strip().replace("\\", "/").rsplit("/", 1)[-1]
    s = EXT_RE.sub("", s)
    return SUF_RE.sub("", s)


def is_pc(im: dict) -> bool:
    s = im.get("source") or ""
    r = im.get("repair") or ""
    return ("PC" in s) or ("pc" in r.lower())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    conn = pe_fetch.con()
    swappable, kept_pc = 0, 0
    samples = []
    for it in board["items"]:
        imgs = (it.get("_media") or {}).get("images") or []
        touched = False
        only_pc_left = False
        for im in imgs:
            if not is_pc(im):
                continue
            k = logical(im.get("base"))
            if not k:
                continue
            got = None
            for suf in ("_b", "_s", ""):
                r = pe_fetch.resolve(ICON_DIR + "/" + k, suf, conn)
                if r:
                    got = (r[0], suf)
                    break
            if got:
                swappable += 1
                if len(samples) < 8:
                    samples.append(("PE", it["name"], k, got[0]))
                if not a.dry:
                    dst = OUT / ("%s_%s.png" % (it["id"], k.split("_")[-1]))
                    ok = False
                    try:
                        if dst.exists():
                            dst.unlink()
                        ok = pe_fetch.export(got[0], dst)
                    except Exception:
                        ok = False
                    if ok and dst.is_file() and dst.stat().st_size > 512:
                        im["png"] = "assets/fashion_posters/" + dst.name
                        im["base"] = k + (("_" + got[1][1:]) if got[1] else "")
                        im["source"] = "PE · %s（PC 备份已替换为 PE 直导）" % got[0]
                        im["fetch"] = "pe"
                        im.pop("repair", None)
                        touched = True
            else:
                kept_pc += 1
                only_pc_left = True
                if not a.dry:
                    im["fetch"] = "pc_fallback"
                    im["source"] = ((im.get("source") or "").split("·")[0].strip()
                                    + " · PE 缺卷，图取自 PC 备份")
                    im["pc_fallback"] = True
        if touched and not a.dry:
            prov = it.setdefault("provenance", {})
            df = prov.setdefault("derived_fields", [])
            if "pc_fallback" not in df:
                df.append("pc_fallback")

    print("PC 来源图：可换 PE %d ｜仍留 PC 备份 %d" % (swappable, kept_pc))
    for s in samples:
        print("   %s %-14s %-24s %s" % s)
    if a.dry:
        print("（--dry：未写盘）")
        return 0

    ts = time.strftime("%Y%m%d_%H%M%S")
    shutil.copy2(BOARD, BOARD.with_name(BOARD.name + ".bak_%s_pcswap" % ts))
    shutil.copy2(BOARD_JS, BOARD_JS.with_name(BOARD_JS.name + ".bak_%s_pcswap" % ts))
    BOARD.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    BOARD_JS.write_text("window.WIKI_BOARD_fashion_wardrobe = "
                        + json.dumps(board, ensure_ascii=False, indent=1) + ";\n",
                        encoding="utf-8")
    print("已写回 %s" % BOARD.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
