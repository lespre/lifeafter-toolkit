# -*- coding: utf-8 -*-
"""统一人物时装的部位标签：把英文 part（cloth/hat/bag/light/suit）归一成中文，
与并进来的 part_code 七类（头饰/捏脸/衣服/背包/挂饰/戒指/半感染者花苞）同一套。
"""
from __future__ import annotations
import sys

import json
import pathlib
from collections import Counter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

ROOT = pathlib.Path(PROJ)
FW = ROOT / "02_wiki/web/data/boards/fashion_wardrobe.json"

EN2CN = {"cloth": "衣服", "hat": "头饰", "bag": "背包", "light": "光源", "suit": "整套"}


def norm(p: str) -> str:
    if not p:
        return p
    if "/" in p:
        return "/".join(EN2CN.get(x, x) for x in p.split("/"))
    return EN2CN.get(p, p)


def main() -> int:
    d = json.loads(FW.read_text(encoding="utf-8"))
    for it in d["items"]:
        it["part"] = norm(it.get("part") or "")
        it["part_label"] = norm(it.get("part_label") or it.get("part") or "")
        pb = it.get("part_bucket")
        if isinstance(pb, list):
            out = []
            for p in pb:
                out.extend(norm(str(p)).split("/"))
            it["part_bucket"] = list(dict.fromkeys([x for x in out if x]))
        it["part_source"] = it.get("part_source") or "part"
    d["meta"]["part_rule"] = ("部位统一中文：头饰/捏脸/衣服/背包/挂饰/戒指/半感染者花苞（来自 part_code 1~7），"
                              "另有 光源 / 整套 两档来自 model id。")
    FW.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    c = Counter(p for it in d["items"] for p in (it.get("part_bucket") or []))
    print("归一完成，部位分布：", c.most_common(12))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
