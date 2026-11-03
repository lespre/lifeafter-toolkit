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
import os
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
# 还原树（唯一认可的贴图来源）：配置里写的是旧版相对路径时，按同名文件回树里找。
TREE = PROJ / "01_索引与产物/41_还原树/pe/资源"
TEX_EXT = (".ktx", ".png", ".bc7", ".dds", ".jpg")
BADGE_MAX = 80   # 边长 ≤80px 的 style_icon 是「小徽标」而不是美术字


def tex_stem(name):
    low = name.lower()
    for e in TEX_EXT:
        if low.endswith(e):
            return name[: -len(e)]
    return name


def stem_key(p):
    """贴图名 → 按「文件名（去扩展名）」比对；配置里常是旧目录，路径不可信，只认同名文件。"""
    return tex_stem(p.replace("\\", "/").rsplit("/", 1)[-1]).lower()


def tree_by_stem(stems):
    """一次遍历还原树，按「文件名去扩展名」收集路径（只在精确路径导出失败时兜底）。"""
    want = {stem_key(s) for s in stems}
    got = {}
    for dp, _dn, fn in os.walk(TREE):
        for f in fn:
            s = stem_key(f)
            if s in want and s not in got:
                got[s] = os.path.relpath(os.path.join(dp, f), TREE).replace("\\", "/")
    return got


def export_skins():
    SKIN_DIR.mkdir(parents=True, exist_ok=True)
    got = []
    for name in SKINS:
        if IF.export("ui/chenghao_icon/img_chenghao_" + name, SKIN_DIR / (name + ".png")):
            got.append(name)
    print("色贴图 %d/%d: %s" % (len(got), len(SKINS), " ".join(got)))
    return got


def classify(it, out, rel):
    """小方图是 style_icon 徽标（贴在称号左侧），宽图才是称号名美术字。"""
    try:
        from PIL import Image
        w, h = Image.open(out).size
    except Exception:
        w = h = 999
    if w <= BADGE_MAX and h <= BADGE_MAX:
        it["badge_png"] = rel
        return "badge"
    it["art_png"] = rel
    return "art"


def export_art(items):
    ART_DIR.mkdir(parents=True, exist_ok=True)
    ok = badge = 0
    miss_list = []
    for it in items:
        it.pop("art_png", None)
        it.pop("badge_png", None)
    items_art = [it for it in items if it.get("art_icon")]
    for it in items_art:
        base = tex_stem(str(it["art_icon"]))
        rel = "assets/title_art/ta_%s.png" % it["item_id"]
        kind = classify(it, WEB / rel, rel) if IF.export(base, WEB / rel) else ""
        if kind == "art":
            ok += 1
        elif kind == "badge":
            badge += 1
        else:
            miss_list.append((it, base, rel))
    # 兜底：配置里的老路径取不到时，按同名文件回还原树再导一次（不猜目录、不改名）
    still = 0
    if miss_list:
        found = tree_by_stem([b for _it, b, _rel in miss_list])
        for it, base, rel in miss_list:
            hit = found.get(stem_key(base))
            kind = ""
            if hit:
                stem = tex_stem(hit)
                for cand in (stem, "ui/" + stem, "ui/" + tex_stem(base)):
                    if IF.export(cand, WEB / rel):
                        kind = classify(it, WEB / rel, rel)
                        break
            if kind == "art":
                ok += 1
                print("  树内回捞:", it["item_id"], it["name"], hit)
            elif kind == "badge":
                badge += 1
                print("  树内回捞(徽标):", it["item_id"], it["name"], hit)
            else:
                still += 1
                print("  未命中:", it["item_id"], it["name"], it["art_icon"])
        print("美术字 %d / 徽标 %d / 仍未命中 %d（带 art_icon 共 %d 条）"
              % (ok, badge, still, len(items_art)))
    return ok


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
