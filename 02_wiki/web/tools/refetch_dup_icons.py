# -*- coding: utf-8 -*-
"""修「同卡多图标被同名文件互相覆盖」的问题。

═══════════════════════════════════════════════════════════════════════════
★ 现象（用户报：星途绮想典藏-头饰 / -衣服 重复了）

  星途绮想-头饰的 _media 里有两条「女」图：
      icon_366804_2 → assets/fashion_posters/fw_e6aed8eab3_f.png
      icon_366009_2 → assets/fashion_posters/fw_e6aed8eab3_f.png   ← 同一个文件！
  根因：导出时的目标文件名只用了「卡id_性别」，
        366009_2 后导出，把 366804_2 先写好的文件**覆盖**了。
  实测两图 md5 不同（366804_2=f180972d… / 366009_2=129d2bb7…）→ 真的丢了一张图。

  全板扫出 **88 张卡**有同样的「同 png 多 base」。

★ 修法

  1. 对这 88 张卡的每个 base 重新导出，文件名改为 `卡id_<去icon_前缀的base>.png`
     （唯一，不再撞车）
  2. 同卡同性别、md5 相同的多条 → 合并成一条（标 unisex_from）；
     不同 → 保留多条（不同期限款的图本来就该不一样）
  3. 旧 png 文件不删（可能仍被其它卡引用），只改数据指向

★ 用法
    python refetch_dup_icons.py --dry
    python refetch_dup_icons.py
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import pathlib
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


def md5(p: pathlib.Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def refetch(conn, base: str, dst: pathlib.Path) -> bool:
    r = None
    for suf in ("_b", "_s", ""):
        try:
            r = pe_fetch.resolve(ICON_DIR + "/" + base, suf, conn)
        except Exception:
            r = None
        if r:
            break
    if not r:
        return False
    try:
        if dst.exists():
            dst.unlink()
        ok = pe_fetch.export(r[0], dst)
    except Exception:
        ok = False
    return bool(ok and dst.is_file() and dst.stat().st_size > 512)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    conn = pe_fetch.con()
    OUT.mkdir(parents=True, exist_ok=True)

    fixed_cards = merged = kept = 0
    log = []
    for it in board["items"]:
        imgs = (it.get("_media") or {}).get("images") or []
        if not imgs:
            continue
        bypng = collections.defaultdict(set)
        for im in imgs:
            if im.get("png"):
                bypng[im["png"]].add(im.get("base"))
        if not any(len(bs) > 1 for bs in bypng.values()):
            continue

        fixed_cards += 1
        new_imgs = []
        seen_md5 = {}          # (label, md5) → 已有条目
        for im in imgs:
            base = im.get("base") or ""
            if not base:
                new_imgs.append(im)
                continue
            tail = base.split("_", 1)[-1] if base.startswith("icon_") else base
            dst = OUT / ("%s_%s.png" % (it["id"], tail))
            rel = "assets/fashion_posters/" + dst.name
            ok = False
            if not a.dry:
                ok = refetch(conn, base, dst)
                if ok:
                    im = dict(im, png=rel, refetched=True)
            if im.get("png") and (a.dry or (dst.is_file())):
                h = md5(OUT / pathlib.Path(im["png"]).name) if not a.dry else None
                key = (im.get("label"), h)
                if h and key in seen_md5:
                    merged += 1
                    prev = seen_md5[key]
                    prev.setdefault("unisex_from", []).append(base)
                    continue
                if h:
                    seen_md5[key] = im
                kept += 1
                new_imgs.append(im)
            else:
                kept += 1
                new_imgs.append(im)
        log.append((it["name"], len(imgs), len(new_imgs)))
        if not a.dry:
            it["_media"]["images"] = new_imgs
            it["_media"]["total"] = len(new_imgs)
            it["icon_count"] = len(new_imgs)

    print("=== 覆盖修复 ===")
    print("  涉及卡 %d ｜ 重导保留 %d ｜ 同图合并 %d" % (fixed_cards, kept, merged))
    for x in log[:10]:
        print("   %-14s %d → %d" % x)
    if a.dry:
        print("（--dry：未写盘）")
        return 0

    ts = time.strftime("%Y%m%d_%H%M%S")
    shutil.copy2(BOARD, BOARD.with_name(BOARD.name + ".bak_%s_dupfix" % ts))
    shutil.copy2(BOARD_JS, BOARD_JS.with_name(BOARD_JS.name + ".bak_%s_dupfix" % ts))
    BOARD.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    BOARD_JS.write_text("window.WIKI_BOARD_fashion_wardrobe = "
                        + json.dumps(board, ensure_ascii=False, indent=1) + ";\n",
                        encoding="utf-8")
    print("已写回 %s" % BOARD.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
