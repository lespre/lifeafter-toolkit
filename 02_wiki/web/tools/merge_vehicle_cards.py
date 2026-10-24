# -*- coding: utf-8 -*-
"""载具板：同名（含时限变体）合并成一张卡，保留全部 vehicle_id。"""
from __future__ import annotations

import json
import pathlib

WEB = pathlib.Path(__file__).resolve().parents[1]
BOARD = WEB / "data/boards/vehicle_full.json"


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]
    groups: dict[str, dict] = {}
    import re as _re
    for it in items:
        raw_name = str(it.get("name") or it.get("id"))
        trial = bool(_re.search(r"[（(]体验版[)）]", raw_name))
        name = _re.sub(r"[（(]体验版[)）]", "", raw_name)
        name = _re.sub(r"[（(]\s*\d+\s*天\s*[)）]", "", name)
        name = _re.sub(r"[-－]\d+\s*天$", "", name).strip() or raw_name
        it["has_trial"] = trial
        it["name_raw"] = raw_name
        g = groups.get(name)
        if g is None:
            it["vehicle_ids"] = [it.get("vehicle_id")] if it.get("vehicle_id") is not None else []
            it["name"] = name
            groups[name] = it
            continue
        if trial:
            g["has_trial"] = True
        vid = it.get("vehicle_id")
        if vid is not None and vid not in g["vehicle_ids"]:
            g["vehicle_ids"].append(vid)
        gimgs = (g.setdefault("_media", {}) or {}).get("images") or []
        seen = {x.get("png") for x in gimgs}
        for im in (it.get("_media") or {}).get("images") or []:
            if im.get("png") not in seen:
                gimgs.append(im)
                seen.add(im.get("png"))
        g["_media"] = {"images": gimgs, "total": len(gimgs)}
        for f in ("desc", "brand_name", "special_function", "jump_text", "charm_value"):
            if g.get(f) in (None, "") and it.get(f) not in (None, ""):
                g[f] = it[f]
        g.setdefault("variant_rows", []).append({k: it.get(k) for k in
                                                ("vehicle_id", "available_ts", "desc", "jump_text")})

    merged = list(groups.values())
    for it in merged:
        it["vehicle_ids"] = sorted(x for x in it["vehicle_ids"] if x is not None)
        it["variant_count"] = len(it["vehicle_ids"])
        if it["variant_count"] > 1:
            it["name_display_group"] = it["name"]
    d["items"] = merged
    d["meta"]["notes"] = (d["meta"].get("notes") or "") + " ｜ 同名（含时限变体）合并为一张卡，编号见详情"
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    multi = sum(1 for i in merged if i["variant_count"] > 1)
    print("合并前 %d 张 → 合并后 %d 张（其中多编号 %d 张）" % (len(items), len(merged), multi))
    for i in merged:
        if i["variant_count"] > 1:
            print("  %-12s %d 个编号 %s" % (i["name"], i["variant_count"], i["vehicle_ids"][:6]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
