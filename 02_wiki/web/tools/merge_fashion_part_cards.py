# -*- coding: utf-8 -*-
"""时装板合并同套多部位卡片：同一 name + 同一 model_id 的 cloth/hat/light 合为一张卡。

- part_bucket 变成数组（衣服/头饰/光源…），筛选时任一命中即显示
- row_keys / 图片 合并去重
- 名称保持原样；不改任何单一部位卡的 part 原值
"""
from __future__ import annotations

import json
import pathlib

WEB = pathlib.Path(__file__).resolve().parents[1]
BOARD = WEB / "data/boards/fashion_wardrobe.json"

PART_CN = {"cloth": "衣服", "hat": "头饰", "bag": "背包", "suit": "整套",
           "light": "光源", "face": "面饰", "pendant": "挂饰", "proj": "投影"}


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]
    groups: dict[tuple, dict] = {}
    for it in items:
        mids = it.get("model_ids") or []
        key = (str(it.get("name") or ""), str(mids[0]) if mids else str(it.get("id")))
        g = groups.get(key)
        parts = [PART_CN.get(str(it.get("part")), str(it.get("part")))]
        if g is None:
            it["part_bucket"] = parts
            it["parts_raw"] = [str(it.get("part"))]
            groups[key] = it
            continue
        for p in parts:
            if p not in g["part_bucket"]:
                g["part_bucket"].append(p)
        if str(it.get("part")) not in g["parts_raw"]:
            g["parts_raw"].append(str(it.get("part")))
        g["row_keys"] = sorted(set((g.get("row_keys") or []) + (it.get("row_keys") or [])))
        gimgs = (g.setdefault("_media", {}) or {}).get("images") or []
        for im in (it.get("_media") or {}).get("images") or []:
            if im not in gimgs:
                gimgs.append(im)
        g["_media"] = {"images": gimgs, "total": len(gimgs)}
        for f in ("charm_value", "level", "desc"):
            if g.get(f) in (None, "", 0) and it.get(f) not in (None, "", 0):
                g[f] = it[f]

    merged = list(groups.values())
    for it in merged:
        it["part"] = "/".join(it.get("parts_raw") or [])
        it["part_label"] = "+".join(it["part_bucket"])
    d["items"] = merged
    d["meta"]["notes"] = (d["meta"].get("notes") or "") + " ｜ 同套多部位（衣服/头饰/光源）已合并为一张卡，部位为数组"
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("合并前 %d 卡 → 合并后 %d 卡" % (len(items), len(merged)))
    from collections import Counter
    print("部位分布", Counter(tuple(i["part_bucket"]) for i in merged).most_common(6))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
