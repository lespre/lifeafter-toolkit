# -*- coding: utf-8 -*-
"""名片框（无 spine 的静态图款）补图：business_card_scheme_data.image_path → assets/avatar_frames/<id>.png。
每 100 张落盘一次。用法：python fill_namecard_static.py [--budget 60] [--apply]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

PROJ = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
from toolkit_core import img_fetch

WEB = PROJ / "02_wiki/web"
CAT = WEB / "data/boards/avatar_catalog.json"
OUT = WEB / "assets/avatar_frames"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=float, default=60.0)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    cat = json.loads(CAT.read_text(encoding="utf-8"))
    items = cat["items"]
    pend = [i for i in items if i.get("kind") == "名片框"
            and not ((i.get("_media") or {}).get("images"))
            and (i.get("image_path") or "").strip()
            and not (i.get("spine_path") or "").strip()]
    print("静态款待补 %d" % len(pend))
    if not a.apply:
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    ok, bad, dirty = 0, [], 0
    for n, it in enumerate(pend, 1):
        if time.time() > t0 + a.budget:
            print("到预算，停在第 %d 条" % n)
            break
        rel = it["image_path"].replace("\\", "/").lstrip("/")
        dst = OUT / (it["id"] + ".png")
        src = ""
        if not (dst.is_file() and dst.stat().st_size > 512):
            try:
                src = img_fetch.export(rel, dst)
            except Exception as ex:                            # noqa: BLE001
                bad.append((it["id"], rel, "exc:" + str(ex)[:40]))
                continue
        if dst.is_file() and dst.stat().st_size > 512:
            it["_media"] = {"images": [{"png": "assets/avatar_frames/%s.png" % it["id"],
                                        "label": "名片框", "base": rel,
                                        "source": "business_card_scheme_data.image_path"}],
                            "total": 1}
            ok += 1
            dirty += 1
            if dirty >= 100:
                CAT.write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding="utf-8")
                dirty = 0
                print("  [落盘] %d ｜ %.1fs" % (ok, time.time() - t0))
        else:
            bad.append((it["id"], rel, "no_src"))
    if dirty:
        CAT.write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding="utf-8")
    have = sum(1 for i in items if (i.get("_media") or {}).get("images"))
    print("补 %d ｜ 失败 %d ｜ 名片框有图 %d ｜ %.1fs"
          % (ok, len(bad), sum(1 for i in items if i.get("kind") == "名片框"
                               and (i.get("_media") or {}).get("images")), time.time() - t0))
    print("失败样例", bad[:5])
    (PROJ / "01_索引与产物/10_索引/热更检测/_namecard_static_fail.json").write_text(
        json.dumps(bad, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
