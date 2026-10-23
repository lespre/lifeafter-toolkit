# -*- coding: utf-8 -*-
"""把时装四类附加图层并进 fashion_wardrobe：面饰 / 光源 / 挂饰（投影另一步）。

来源（全部可由还原树重建）：
  面饰  fashion_face_slots.json（player_appear_data 面饰行）
  光源  fashion_glow_slots.json（player_appear_data 荧光棒行）
  挂饰  all_equips_data 270xxx（本体行，带 name / charm_value / desc）

用法：
    python tools/merge_fashion_layers.py
"""
from __future__ import annotations

import json
import pathlib
import sys

WEB = pathlib.Path(__file__).resolve().parents[1]
PROJ = WEB.parents[1]
sys.path.insert(0, str(WEB / "tools"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))

from _src import table_path  # noqa: E402

BOARD = WEB / "data/boards/fashion_wardrobe.json"
LAYERS = [("fashion_face_slots.json", "face_"), ("fashion_glow_slots.json", "glow_")]


def _v(v):
    return v[1] if isinstance(v, tuple) else v


def pendants() -> list[dict]:
    from toolkit_core import bindict_table as BT
    base = table_path("all_equips_data_auto_oversea_data_kj1", "oversea")
    if not base or not base.exists():
        return []
    chs = base.with_name(base.stem + "_chs.py")
    raw = base.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        return []
    L = int.from_bytes(raw[at + 2:at + 6], "little")
    pool = BT.parse_legacy_chs_pool(chs.read_bytes()) if chs.exists() else None
    rows = BT.decode_table_rows(raw[at + 6:at + 6 + L], pool, resolve_jumps=False, lenient=True)[0]
    out = []
    for r in rows:
        key = str(r.get("key") or "")
        if not key.startswith("270"):
            continue
        vals = r.get("values") or {}
        name = _v(vals.get("name"))
        if not name:
            continue
        out.append({
            "id": "pendant_%s" % key,
            "name": str(name),
            "part": "挂饰",
            "charm_value": _v(vals.get("charm_value")),
            "desc": _v(vals.get("desc")),
            "evidence": "structure",
            "evidence_level": "static/candidate",
            "source": "all_equips_data %s（挂饰本体）" % key,
            "status_tags": ["static config"],
        })
    return out


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d.get("items", [])
    have = {str(i.get("id")) for i in items}

    added = {"face": 0, "glow": 0, "pendant": 0}
    for fname, prefix in LAYERS:
        p = WEB / "data/boards" / fname
        if not p.exists():
            continue
        for it in json.loads(p.read_text(encoding="utf-8")).get("items", []):
            iid = str(it.get("id") or "")
            if not iid.startswith(prefix) or iid in have:
                continue
            item = {
                "id": iid,
                "name": it.get("name") or it.get("display_name") or "",
                "part": "面饰" if prefix == "face_" else "光源",
                "charm_value": it.get("charm_value"),
                "desc": it.get("desc"),
                "evidence": it.get("evidence", "structure"),
                "evidence_level": it.get("evidence_level", "static/candidate"),
                "source": it.get("source") or "player_appear_data（%s）" % fname,
                "status_tags": it.get("status_tags") or ["static config"],
            }
            items.append(item)
            have.add(iid)
            added[prefix.strip("_")] += 1

    for item in pendants():
        if item["id"] in have:
            continue
        items.append(item)
        have.add(item["id"])
        added["pendant"] += 1

    d["items"] = items
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("并入 face %d / glow %d / pendant %d ｜ 总 %d"
          % (added["face"], added["glow"], added["pendant"], len(items)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
