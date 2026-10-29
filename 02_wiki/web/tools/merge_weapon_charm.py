import sys
# -*- coding: utf-8 -*-
"""把 weapon_skin_data 的 charm_value / weapon_type 合并进武器皮肤板（按 skin_id 整数对齐）。"""
import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import ANALYSIS_ROOT, WEB  # noqa: E402

ROWS = pathlib.Path(ANALYSIS_ROOT / "子代理产出_20261022/_weapon_skin_table_rows.json")
BOARD = WEB / "data" / "boards" / "weapon_skin_sfx_text_sources.json"

rows = {int(r["key"]): r for r in json.loads(ROWS.read_text(encoding="utf-8"))}
d = json.loads(BOARD.read_text(encoding="utf-8"))

hit = miss = 0
for it in d.get("items", []):
    sid = it.get("skin_id") or it.get("skin_item_id") or it.get("id")
    try:
        sid = int(str(sid).split("_")[-1])
    except (TypeError, ValueError):
        sid = None
    r = rows.get(sid) if sid else None
    if not r:
        miss += 1
        it["charm_value"] = None
        it["charm_source"] = "no_table_row"
        continue
    it["charm_value"] = r.get("charm_value")
    it["weapon_type_code"] = r.get("weapon_type")
    it["charm_source"] = "weapon_skin_data.charm_value"
    hit += 1
    for v in it.get("variant_items") or []:
        try:
            vid = int(str(v.get("id")).split("_")[-1])
        except (TypeError, ValueError):
            continue
        vr = rows.get(vid)
        if vr:
            v["charm_value"] = vr.get("charm_value")

BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
print("命中", hit, "缺行", miss, "｜表行", len(rows))
