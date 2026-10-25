# -*- coding: utf-8 -*-
"""给「表里登记了 icons_all 但没取到图」的时装卡补图：直接按登记路径试 _b/_s。"""
from __future__ import annotations

import json
import pathlib
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
SUF = ("_b", "_s", "")


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    todo = [i for i in d["items"]
            if not ((i.get("_media") or {}).get("images")) and (i.get("icons_all") or [])]
    print("有登记路径但无图 %d" % len(todo), flush=True)

    ok = fail = 0
    t0 = time.time()
    for n, it in enumerate(todo, 1):
        imgs = []
        for slot in it["icons_all"][:4]:
            base = str(slot.get("path") or "")
            if not base:
                continue
            gender = str(slot.get("gender") or "")
            lab = "男装" if gender == "男" else ("女装" if gender == "女" else "图示%d" % (len(imgs) + 1))
            hit = ""
            dst = OUT / ("%s_%d.png" % (it["id"], len(imgs) + 1))
            for s in SUF:
                try:
                    if pe_fetch.export(base + s, dst) and dst.is_file() and dst.stat().st_size > 512:
                        w, h = Image.open(dst).size
                        if w >= 64 and h >= 64:
                            hit = base + s
                            break
                except Exception:  # noqa: BLE001
                    continue
            if hit:
                imgs.append({"png": "assets/fashion_posters/%s_%d.png" % (it["id"], len(imgs) + 1),
                             "base": hit.split("/")[-1], "label": lab,
                             "source": "PE · %s（按 icons_all 登记路径）" % hit})
            elif dst.exists():
                dst.unlink()
        if imgs:
            it["_media"] = {"images": imgs, "total": len(imgs)}
            ok += 1
        else:
            fail += 1
        if n % 50 == 0:
            BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
            print("  [%d/%d] 命中 %d 失败 %d ｜ %.0fs" % (n, len(todo), ok, fail, time.time() - t0), flush=True)

    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("完成：命中 %d ｜ 失败 %d ｜ %.0fs" % (ok, fail, time.time() - t0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
