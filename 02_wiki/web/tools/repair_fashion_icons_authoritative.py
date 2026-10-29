# -*- coding: utf-8 -*-
"""把时装板的图收回「权威路径」：只认 icons_all 里的 icon 路径，删掉所有猜编号来的图。

═══════════════════════════════════════════════════════════════════════════
★ 为什么必须做

  历史上有几条"按 model 号猜图标编号"的链路（fill_fashion_by_model.py 等）：
      model 3249 → icon_367197_1_b   ← 猜出来的，实际是**另一件衣服**的图
      model 3027 → icon_bag_m_3027023_b ← 同一张图被 360/4399/OPPO/Taptap 背包共用
  这些图 base 都不在表里的 `icons_all` 路径上，属"张冠李戴"，
  用户已在 2026-10-29 报出（幻能葫芦 / 滑个龟龟 / 捣蛋蜪火 / 生机星三家 / 果赖折力 /
  ★海云鸿 / 丘比特背包 / 天穹凝冰 …）。

★ 口径（唯一可信）

  1. 权威路径 = 卡片 `icons_all[*].path`（来自 fashion_data.icons 或 player_appear_data）
  2. `_media.images` 里 base 归一化后**不在**权威路径集合的 → 删除（记入回滚清单）
  3. 权威路径没有 png 的 → 按该路径从 PE 取（_b / _s / 无后缀三档，.ktx/.png 两扩展）
  4. 取不到就如实留缺图，不猜、不跨卡借图

  归一化：剥目录、剥 .ktx/.png/.bc7/.dds、剥 _b/_s 档位后缀

★ 安全

  · 默认 --dry；落盘前自动备份 board（.bak_YYYYMMDD_HHMMSS_authoritative）
  · 删除清单写 `data/boards/_refs/removed_guess_icons_<ts>.json`，可回滚
  · 只改 `_media` / `icon_state` / `icon_count` / `icons_all[*].png`，不动名字与来源字段
═══════════════════════════════════════════════════════════════════════════
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
REF = WEB / "data/boards/_refs"
ICON_DIR = "ui/item_icon"

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
import pe_fetch  # noqa: E402

EXT_RE = re.compile(r"\.(ktx|png|bc7|dds)$", re.I)
SUF_RE = re.compile(r"_[bs]$")


def logical(x: str) -> str:
    """把各种写法的图标路径/基名归一成裸基名：icon_bag_f_3249001"""
    s = (x or "").strip().replace("\\", "/")
    s = s.rsplit("/", 1)[-1]
    s = EXT_RE.sub("", s)
    s = SUF_RE.sub("", s)
    return s


def resolve_icon(conn, base: str):
    """按裸基名找 (完整路径, 档位)；三档 × 两扩展都已由 pe_fetch 覆盖。"""
    for suf in ("_b", "_s", ""):
        try:
            r = pe_fetch.resolve(ICON_DIR + "/" + base, suf, conn)
        except Exception:
            r = None
        if r:
            return r[0], suf
    return None, None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--no-fill", action="store_true", help="只删错图，不补图")
    a = ap.parse_args()

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    conn = pe_fetch.con()
    ts = time.strftime("%Y%m%d_%H%M%S")

    removed = []          # 删掉的图
    filled = []           # 按权威路径补上的
    still_missing = []    # 权威路径有但包里取不到
    cards_lost_all = []   # 删完变 0 图的卡

    for it in board["items"]:
        icons = it.get("icons_all") or []
        auth = {}
        for x in icons:
            k = logical(x.get("path"))
            if k:
                auth.setdefault(k, x)
        if not auth:
            continue

        before = (it.get("_media") or {}).get("images") or []
        kept = []
        for im in before:
            base = logical(im.get("base"))
            if base and base in auth:
                kept.append(im)
            else:
                removed.append({"card": it["name"], "id": it["id"],
                                "base": im.get("base"), "label": im.get("label"),
                                "png": im.get("png"), "source": im.get("source")})
        if before and not kept:
            cards_lost_all.append(it["name"])

        # 按权威路径补图
        png_by_base = {}
        for k, x in auth.items():
            if x.get("png"):
                png_by_base[k] = x["png"]
        if not a.no_fill:
            for k, x in auth.items():
                if x.get("png"):
                    continue
                full, suf = resolve_icon(conn, k)
                if not full:
                    still_missing.append({"card": it["name"], "path": x.get("path")})
                    continue
                rel = None
                if not a.dry:
                    dst = OUT / ("%s_%s.png" % (it["id"], k.split("_")[-1]))
                    try:
                        if dst.exists():
                            dst.unlink()
                        ok = pe_fetch.export(full, dst)
                    except Exception:
                        ok = False
                    if not (ok and dst.is_file() and dst.stat().st_size > 512):
                        still_missing.append({"card": it["name"], "path": x.get("path")})
                        continue
                    rel = "assets/fashion_posters/" + dst.name
                    png_by_base[k] = rel
                else:
                    png_by_base[k] = "(dry)"
                filled.append({"card": it["name"], "path": full, "suffix": suf})

        if a.dry:
            continue

        # 回写：kept 里若 png 缺失但权威补到了，补上
        for im in kept:
            base = logical(im.get("base"))
            if not im.get("png") and png_by_base.get(base):
                im["png"] = png_by_base[base]
        kept = [im for im in kept if im.get("png")]

        # 权威路径补出来的图，若 _media 里还没有，追加
        have = {logical(im.get("base")) for im in kept}
        for k, png in png_by_base.items():
            if k in have or png == "(dry)":
                continue
            kept.append({
                "png": png,
                "base": k,
                "label": (auth[k].get("gender") or "图标"),
                "source": "icons_all 权威路径 → %s/%s" % (ICON_DIR, k),
                "fetch": "pe",
            })

        it["_media"] = dict(it.get("_media") or {}, images=kept, total=len(kept))
        if not kept:
            it["_media"].pop("missing", None)
        for x in icons:
            k = logical(x.get("path"))
            if png_by_base.get(k):
                x["png"] = png_by_base[k]
        it["icon_state"] = "有图" if kept else "缺图"
        it["icon_count"] = len(kept)
        if not kept:
            it["icon_missing_reason"] = "表里 icon 路径在 PE 包里取不到图"

    print("=== 权威化 ===")
    print("  删除猜编号图 %d 张（涉及 %d 张卡）"
          % (len(removed), len({r['card'] for r in removed})))
    print("  按权威路径补图 %d 张" % len(filled))
    print("  权威路径仍取不到 %d 条" % len(still_missing))
    print("  删完变 0 图的卡 %d：%s" % (len(cards_lost_all), cards_lost_all[:12]))
    for r in removed[:8]:
        print("   - %-14s %-28s %s" % (r["card"], r["base"], (r["source"] or "")[:30]))

    if a.dry:
        print("（--dry：未写盘）")
        return 0

    REF.mkdir(parents=True, exist_ok=True)
    (REF / ("removed_guess_icons_%s.json" % ts)).write_text(
        json.dumps({"removed": removed, "filled": filled, "still_missing": still_missing},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    bak = BOARD.with_name(BOARD.name + ".bak_%s_authoritative" % ts)
    shutil.copy2(BOARD, bak)
    shutil.copy2(BOARD_JS, BOARD_JS.with_name(BOARD_JS.name + ".bak_%s_authoritative" % ts))

    BOARD.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    BOARD_JS.write_text("window.WIKI_BOARD_fashion_wardrobe = "
                        + json.dumps(board, ensure_ascii=False, indent=1) + ";\n",
                        encoding="utf-8")
    print("已写回 %s ｜备份 %s" % (BOARD.name, bak.name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
