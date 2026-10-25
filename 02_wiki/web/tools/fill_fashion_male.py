# -*- coding: utf-8 -*-
"""补齐时装卡的男角色图（只用 PE 源）。

用法：
  python fill_fashion_male.py 100      # 只跑前 100 张（试样）
  python fill_fashion_male.py 0        # 全量
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import time

PROJ = pathlib.Path("E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
import pe_fetch  # noqa: E402
from PIL import Image  # noqa: E402

BOARD = WEB / "data/boards/fashion_wardrobe.json"
OUT = WEB / "assets/fashion_posters"
OUT.mkdir(parents=True, exist_ok=True)

NUM2 = re.compile(r"icon_(\d+)_2(?:_[a-z0-9]+)?$")
BF = re.compile(r"icon_b_f_(\d+)(?:_[a-z0-9]+)?$")
ANY = re.compile(r"icon_(\d+)")
SUFFIXES = ("_b", "_s", "")


def male_candidates(base: str) -> list[str]:
    base = str(base or "").strip()
    out = []
    m = NUM2.match(base)
    if m:
        n = m.group(1)
        out += [f"ui/item_icon/icon_{n}_1{s}" for s in SUFFIXES]
    m = BF.match(base)
    if m:
        n = m.group(1)
        out += [f"ui/item_icon/icon_b_m_{n}_b", f"ui/item_icon/icon_b_m_{n}",
                f"ui/item_icon/icon_b_m_{n}_s"]
    if not out:
        m = ANY.search(base)
        if m:
            n = m.group(1)
            out += [f"ui/item_icon/icon_{n}_1_b", f"ui/item_icon/icon_b_m_{n}_b"]
    return list(dict.fromkeys(out))


def main() -> int:
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    items = board["items"]

    todo = []
    for it in items:
        imgs = [x for x in ((it.get("_media") or {}).get("images") or []) if isinstance(x, dict)]
        if not imgs:
            continue
        if any("男" in str(x.get("label", "")) for x in imgs):
            continue
        todo.append(it)
    print("待补男图卡 %d（本次上限 %s）" % (len(todo), limit or "全量"), flush=True)
    if limit:
        todo = todo[:limit]

    ok = fail = 0
    reasons = {"索引无": 0, "解码失败": 0, "无候选": 0}
    t0 = time.time()
    for i, it in enumerate(todo, 1):
        imgs = [x for x in ((it.get("_media") or {}).get("images") or []) if isinstance(x, dict)]
        base = imgs[0].get("base") if imgs else ""
        cands = male_candidates(base)
        if not cands:
            reasons["无候选"] += 1
            fail += 1
            continue
        dst = OUT / ("%s_m.png" % it["id"])
        hit = ""
        for c in cands:
            try:
                if pe_fetch.export(c, dst):
                    if dst.is_file() and dst.stat().st_size > 512:
                        w, h = Image.open(dst).size
                        if w >= 64 and h >= 64 and w * h < 4096 * 4096:
                            hit = c
                            break
            except Exception:  # noqa: BLE001
                continue
        if not hit:
            reasons["索引无"] += 1
            fail += 1
            if dst.exists():
                dst.unlink()
            continue
        imgs.append({"png": "assets/fashion_posters/%s_m.png" % it["id"],
                     "base": hit.split("/")[-1], "label": "男装",
                     "source": "PE · %s" % hit})
        it["_media"] = {"images": imgs, "total": len(imgs)}
        ok += 1
        if i % 100 == 0:
            BOARD.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")
            print("  [%d/%d] 命中 %d 失败 %d ｜ %.0fs" % (i, len(todo), ok, fail, time.time() - t0), flush=True)

    BOARD.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")
    print("完成：命中 %d ｜ 失败 %d ｜ 失败原因 %s ｜ %.0fs"
          % (ok, fail, reasons, time.time() - t0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
