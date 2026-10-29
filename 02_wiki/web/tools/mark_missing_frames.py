import sys
# -*- coding: utf-8 -*-
"""28 条名片框：框资源在 PE/PC 索引均无命中（未下发）→ 去掉坏图，标记状态。
bc_580121 的框已重取成功，保留。
"""
import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

BOARD = WEB / "data/boards/avatar_catalog.json"
d = json.loads(BOARD.read_text(encoding="utf-8"))

BAD = {
    "bc_150640", "bc_150692", "bc_150713", "bc_150714", "bc_150889",
    "bc_151804", "bc_152217", "bc_152390", "bc_152392", "bc_152520",
    "bc_152584", "bc_152766", "bc_580082", "bc_580099", "bc_580113",
    "bc_580170", "bc_580182",
}

marked = cleaned = 0
for it in d["items"]:
    if it.get("id") not in BAD:
        continue
    tags = it.setdefault("status_tags", [])
    if "框资源未下发" not in tags:
        tags.append("框资源未下发")
        marked += 1
    m = it.get("_media") or {}
    imgs = [im for im in (m.get("images") or []) if im.get("label") == "名片背景"]
    if len(imgs) != len(m.get("images") or []):
        m["images"] = imgs
        m["total"] = len(imgs)
        it["_media"] = m
        cleaned += 1

BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
print("标记未下发", marked, "｜移除坏框图", cleaned)
