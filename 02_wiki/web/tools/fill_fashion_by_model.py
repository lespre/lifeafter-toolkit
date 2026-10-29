# -*- coding: utf-8 -*-
"""按 model_id 直造反图候选，给「完全无图」的时装卡补图。

关键规律（2026-10-25 实证）：
  icon_<部位>_<性别>_<model><序号>_b
  部位  b=衣服 h=头饰 bag=背包 light=光源 suit=整套
  性别  f=女 m=男
  序号  001 起（同套多件时递增）
例：不湮之花 model 5004 → icon_h_f_5004001_b（0172.gpk #3120）/ icon_h_m_5004001_b（0000.gpk #13940）
"""
from __future__ import annotations

import json
import pathlib
import sys
import time


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
WEB = PROJ / "02_wiki/web"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
import pe_fetch  # noqa: E402
from PIL import Image  # noqa: E402

BOARD = WEB / "data/boards/fashion_wardrobe.json"
OUT = WEB / "assets/fashion_posters"
OUT.mkdir(parents=True, exist_ok=True)

PREFIX = {"衣服": "b", "头饰": "h", "背包": "bag", "光源": "light", "整套": "suit"}
SEQ = ["001", "002", "003", "004", "005", "006"]


def candidates(model, part, gender):
    pre = PREFIX.get(part, "b")
    return ["ui/item_icon/icon_%s_%s_%s%s_b" % (pre, gender, model, s) for s in SEQ]


def main() -> int:
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    todo = [i for i in d["items"] if not ((i.get("_media") or {}).get("images"))]
    print("完全无图卡 %d（本次上限 %s）" % (len(todo), limit or "全量"), flush=True)
    if limit:
        todo = todo[:limit]

    ok = fail = 0
    t0 = time.time()
    for n, it in enumerate(todo, 1):
        model = str(it.get("model_id") or "")
        if not model or model == "None":
            fail += 1
            continue
        parts = it.get("part_bucket") or [it.get("part_label") or "衣服"]
        part = parts[0] if parts else "衣服"
        imgs = []
        for gender, lab in (("f", "女装"), ("m", "男装")):
            hit = ""
            dst = OUT / ("%s%s.png" % (it["id"], "" if gender == "f" else "_m"))
            for c in candidates(model, part, gender):
                try:
                    if pe_fetch.export(c, dst) and dst.is_file() and dst.stat().st_size > 512:
                        w, h = Image.open(dst).size
                        if w >= 64 and h >= 64:
                            hit = c
                            break
                except Exception:  # noqa: BLE001
                    continue
            if hit:
                imgs.append({"png": "assets/fashion_posters/%s.png" % dst.stem,
                             "base": hit.split("/")[-1], "label": lab,
                             "source": "PE · %s（按 model %s 部位命名反推）" % (hit, model)})
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
