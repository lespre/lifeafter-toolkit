# -*- coding: utf-8 -*-
"""补时装缺失的另一个性别图。

现象：双性别时装（gender=女/男）里 587 张只有一张图，缺另一性别。
规律：同一编号两张图是 icon_<num>_1_*（男）与 icon_<num>_2_*（女）。
做法：从已有图的 base 推出兄弟编号，用 img_fetch（PE→PC 回落）导出，挂到 _media.images。
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import time


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
from toolkit_core import img_fetch  # noqa: E402

BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
OUT = PROJ / "02_wiki/web/assets/fashion_posters"
PAT = re.compile(r"icon_(\d+)_(\d+)(_[a-z0-9]+)?$", re.I)
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 10 ** 9


def variants(num: str, idx: str) -> list[str]:
    other = "2" if idx == "1" else "1"
    return [f"ui/item_icon/icon_{num}_{other}_b", f"ui/item_icon/icon_{num}_{other}_s",
            f"ui/item_icon/icon_{num}_{other}"]


def main() -> int:
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    items = board["items"]
    todo = []
    for it in items:
        if "男" not in str(it.get("gender")) or "女" not in str(it.get("gender")):
            continue
        ims = [x for x in ((it.get("_media") or {}).get("images") or []) if isinstance(x, dict)]
        if len(ims) != 1:
            continue
        m = PAT.search(str(ims[0].get("base") or ""))
        if m:
            todo.append((it, m.group(1), m.group(2)))
    print("待补 %d 张（本次上限 %d）" % (len(todo), LIMIT))

    done = 0
    fail = 0
    t0 = time.time()
    for it, num, idx in todo[:LIMIT]:
        dst = OUT / ("%s_g2.png" % it["id"])
        src = ""
        for v in variants(num, idx):
            try:
                src = img_fetch.export(v, dst)
            except Exception:  # noqa: BLE001
                src = ""
            if dst.exists() and src != "pe":
                pass
            if src == "pe" and dst.is_file() and dst.stat().st_size > 512:
                break
            src = ""
            if dst.exists() and src != "pe":
                pass
        if src != "pe":
            if dst.exists():
                dst.unlink()
            fail += 1
            it["gender_icon_state"] = "另一性别缺图"
            continue
        ims = it["_media"]["images"]
        ims.append({"png": "assets/fashion_posters/%s_g2.png" % it["id"],
                    "base": v.replace("ui/item_icon/", ""),
                    "label": "图示%d" % (len(ims) + 1),
                    "source": "fashion_data.icons → 兄弟编号补图 20261024"})
        it["_media"]["total"] = len(ims)
        it["gender_icon_state"] = "双图齐"
        done += 1
        if done % 100 == 0:
            BOARD.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")
            print("  已补 %d ｜ 失败 %d ｜ %.0fs" % (done, fail, time.time() - t0), flush=True)
    BOARD.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")
    print("完成：补 %d ｜ 失败 %d ｜ %.0fs" % (done, fail, time.time() - t0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
