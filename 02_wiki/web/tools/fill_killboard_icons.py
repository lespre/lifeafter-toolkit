# -*- coding: utf-8 -*-
"""击败播报 5 条配 2D 图标（PE only）。icon_jisha01..05 → _b/_s 后缀命中。"""
from __future__ import annotations

import json
import pathlib
import sys


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
import pe_fetch as PE  # noqa: E402

BOARD = PROJ / "02_wiki/web/data/boards/kill_broadcast.json"
OUT = PROJ / "02_wiki/web/assets/kill_broadcast"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    ok = fail = 0
    for it in d["items"]:
        if it.get("kind") != "击败播报":
            continue
        base = str(it.get("icon") or "").strip()
        if not base:
            print("无 icon 字段", it["id"])
            continue
        dst = OUT / ("%s.png" % it["id"])
        hit = ""
        for suf in ("_b", "_s", ""):
            try:
                if PE.export(base + suf, dst) and dst.is_file():
                    hit = base + suf
                    break
            except Exception:  # noqa: BLE001
                continue
        if not hit:
            fail += 1
            print("未命中", it["id"], base)
            continue
        imgs = (it.get("_media") or {}).get("images") or []
        imgs = [x for x in imgs if isinstance(x, dict)]
        imgs.insert(0, {"png": "assets/kill_broadcast/%s.png" % it["id"],
                        "base": hit.split("/")[-1],
                        "label": "图标",
                        "source": "PE %s" % hit})
        it["_media"] = {"images": imgs, "total": len(imgs)}
        ok += 1
        print("命中", it["name"], hit, dst.stat().st_size)
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("完成：命中 %d ｜ 失败 %d" % (ok, fail))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
