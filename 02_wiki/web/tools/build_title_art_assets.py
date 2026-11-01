# -*- coding: utf-8 -*-
"""称号板视觉资源：档位色贴图 + 称号美术字 → 02_wiki/web/assets。

做什么：
  1) 从 PE 资源包导出档位色贴图（ui/chenghao_icon/img_chenghao_line_N、bg_N）到 assets/title_skin/；
  2) 对 title_catalog 里带 art_icon（style_icon / normal_name_icon）的条目，导出美术字 PNG 到
     assets/title_art/ta_<称号ID>.png，并把真实存在的相对路径回填成 item.art_png；
  3) 同步重写 title_catalog.json / title_catalog.js（两者内容必须一致）。

口径：
  · 只导出「表里写明路径」的美术字，不做拼音目录猜测；
  · 导出失败的不写 art_png，前端回落纯文字，不会产生 404；
  · 动态（shining_style → cocos_csb）是 Cocos Studio 场景，本项目无 csb 运行时，不在此渲染。
"""
from __future__ import annotations

import json
import pathlib
import sys

PROJ = pathlib.Path(__file__).resolve().parents[3]
WEB = PROJ / "02_wiki/web"
BOARD = WEB / "data/boards/title_catalog.json"
ART_DIR = WEB / "assets/title_art"
SKIN_DIR = WEB / "assets/title_skin"

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import img_fetch as IF  # noqa: E402

# 档位色 → 源贴图（实测：line_1 蓝 / line_2 紫 / line_3 金 / line_8 绿；bg_2 紫 / bg_3 金 / bg_4 红）
SKINS = ["line_1", "line_2", "line_3", "line_8", "bg_2", "bg_3", "bg_4", "love_3", "star_3", "cake_3"]


def export_skins():
    SKIN_DIR.mkdir(parents=True, exist_ok=True)
    got = []
    for name in SKINS:
        if IF.export("ui/chenghao_icon/img_chenghao_" + name, SKIN_DIR / (name + ".png")):
            got.append(name)
    print("色贴图 %d/%d: %s" % (len(got), len(SKINS), " ".join(got)))
    return got


def export_art(items):
    ART_DIR.mkdir(parents=True, exist_ok=True)
    ok = miss = 0
    for it in items:
        src = str(it.get("art_icon") or "")
        it.pop("art_png", None)
        if not src:
            continue
        base = src
        for ext in (".png", ".ktx", ".dds"):
            if base.lower().endswith(ext):
                base = base[: -len(ext)]
                break
        rel = "assets/title_art/ta_%s.png" % it["item_id"]
        if IF.export(base, WEB / rel):
            it["art_png"] = rel
            ok += 1
        else:
            miss += 1
            print("  未命中:", it["item_id"], it["name"], src)
    print("美术字 导出 %d / 未命中 %d（总 %d 条带 art_icon）" % (ok, miss, ok + miss))
    return ok, miss


def main() -> int:
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    items = board["items"]
    export_skins()
    export_art(items)
    txt = json.dumps(board, ensure_ascii=False, indent=1)
    BOARD.write_text(txt, encoding="utf-8")
    (WEB / "data/boards/title_catalog.js").write_text(
        "window.WIKI_BOARD_title_catalog = " + txt + ";", encoding="utf-8")
    print("已回填 art_png，重写 title_catalog.json/.js")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
