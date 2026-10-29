# -*- coding: utf-8 -*-
r"""修正时装板的部位归类：
 - 名字含 挂饰/挂件 的 → 挂件
 - 名字是包（背包/挎包/单肩包/双肩包）的 → 背包
其余保持原 part_bucket 不动。
"""
from __future__ import annotations
import sys

import json
import pathlib
import re
import shutil

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

BOARD = WEB / "data/boards/fashion_wardrobe.json"
JS = WEB / "data/boards/fashion_wardrobe.js"

PEND = re.compile(r"挂饰|挂件|吊坠|腰饰|背饰")
BAG = re.compile(r"背包|挎包|单肩包|双肩包|包$")


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    shutil.copy2(BOARD, BOARD.with_suffix(".json.bak_bucketfix"))
    moved = {"挂件": 0, "背包": 0}
    for it in d["items"]:
        name = it.get("name") or ""
        pb = it.get("part_bucket")
        cur = "/".join(pb) if isinstance(pb, list) else str(pb or "")
        if PEND.search(name):
            if cur != "挂件":
                it["part_bucket"] = "挂件"
                moved["挂件"] += 1
        elif BAG.search(name) and cur != "背包":
            it["part_bucket"] = "背包"
            moved["背包"] += 1
    d["meta"]["bucket_fix_20261018"] = moved
    BOARD.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    JS.write_text("window.WIKI_BOARD_fashion_wardrobe = "
                  + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print("改归", moved)
    from collections import Counter
    c = Counter()
    for it in d["items"]:
        pb = it.get("part_bucket")
        c["/".join(pb) if isinstance(pb, list) else str(pb or "")] += 1
    print("新分布", c.most_common(12))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
