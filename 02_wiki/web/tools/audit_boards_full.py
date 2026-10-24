# -*- coding: utf-8 -*-
"""全板体检：条数 / 字段完整度 / 图覆盖 / 筛选轴，一次列出所有可量化的缺陷。

用法：
    python tools/audit_boards_full.py            # 打印表格 + 写报告
    python tools/audit_boards_full.py --json     # 只打印 JSON
"""
from __future__ import annotations

import json
import pathlib
import sys

WEB = pathlib.Path(__file__).resolve().parents[1]
BOARDS = WEB / "data/boards"
TAXONOMY = WEB / "data/wiki_taxonomy.json"

# 每类板块必须有的字段（缺了页面上对应的列/筛选就是空的）
REQUIRED = {
    "fashion": ["name", "part_bucket", "charm_value", "model_ids"],
    "weapon": ["name", "grade", "charm_value"],
    "avatar": ["name", "kind"],
    "core": ["name", "grade_name"],
    "default": ["name"],
}
FASHION_KEYS = {"fashion_wardrobe", "fashion_face_slots", "fashion_projection_slots",
                "fashion_kaijia_slots", "fashion_pendant_slots"}
WEAPON_KEYS = {"weapon_skin_sfx_text_sources", "weapon_skin_catalog", "weapon_skin"}


def published_boards() -> list[str]:
    if not TAXONOMY.exists():
        return sorted(p.stem for p in BOARDS.glob("*.json"))
    t = json.loads(TAXONOMY.read_text(encoding="utf-8"))
    out = []

    def walk(node):
        if isinstance(node, dict):
            for k in ("boards", "board_id", "id"):
                v = node.get(k)
                if isinstance(v, str) and (BOARDS / (v + ".json")).exists():
                    out.append(v)
                elif isinstance(v, list):
                    for x in v:
                        if isinstance(x, str) and (BOARDS / (x + ".json")).exists():
                            out.append(x)
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for x in node:
                walk(x)

    walk(t)
    return sorted(set(out)) or sorted(p.stem for p in BOARDS.glob("*.json"))


def req_for(bid: str) -> list[str]:
    if bid in FASHION_KEYS:
        return REQUIRED["fashion"]
    if bid in WEAPON_KEYS:
        return REQUIRED["weapon"]
    if bid == "avatar_catalog":
        return REQUIRED["avatar"]
    if bid == "mutation_core_full":
        return REQUIRED["core"]
    return REQUIRED["default"]


def audit(bid: str) -> dict:
    p = BOARDS / (bid + ".json")
    d = json.loads(p.read_text(encoding="utf-8"))
    items = d.get("items") or []
    n = len(items)
    req = req_for(bid)
    field_cov = {}
    for f in req:
        field_cov[f] = sum(1 for i in items if i.get(f) not in (None, "", [], {}))
    imgs = 0
    for i in items:
        if (i.get("_media") or {}).get("images"):
            imgs += 1
    filters = (d.get("meta") or {}).get("filters")
    return {
        "board": bid,
        "items": n,
        "fields": field_cov,
        "img": imgs,
        "img_rate": round(imgs / n, 3) if n else 0,
        "filters": len(filters) if isinstance(filters, list) else 0,
        "has_meta_name": bool((d.get("meta") or {}).get("name")),
    }


def main() -> int:
    rows = [audit(b) for b in published_boards()]
    problems = []
    for r in rows:
        bad = []
        for f, c in r["fields"].items():
            if r["items"] and c / r["items"] < 0.5:
                bad.append("%s %d/%d" % (f, c, r["items"]))
        if r["img_rate"] < 0.5 and r["board"] not in ("scene_balance", "activity_master",
                                                      "server_types", "desc_catalog",
                                                      "text_notice_catalog"):
            bad.append("图 %.0f%%" % (r["img_rate"] * 100))
        if bad:
            problems.append((r["board"], r["items"], bad))

    if "--json" in sys.argv:
        print(json.dumps(rows, ensure_ascii=False))
        return 0

    print("%-34s %7s %6s %6s %s" % ("板块", "条数", "有图", "筛选", "缺什么"))
    for r in rows:
        missing = []
        for f, c in r["fields"].items():
            if r["items"] and c / r["items"] < 0.5:
                missing.append("%s %d/%d" % (f, c, r["items"]))
        print("%-34s %7d %5.0f%% %6d %s" % (r["board"], r["items"], r["img_rate"] * 100,
                                            r["filters"], "；".join(missing) or "-"))
    print("\n问题板 %d / %d" % (len(problems), len(rows)))
    out = WEB.parents[1] / "01_索引与产物/30_分析/全板体检_20261024.json"
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print("明细", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
