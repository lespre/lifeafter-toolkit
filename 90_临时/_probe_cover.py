# -*- coding: utf-8 -*-
"""探针：common_item_data_base 覆盖率 + reward_pool_data_base 解 Nucleus 池。"""
import json
import pathlib
import struct
import sys

ROOT = pathlib.Path(r"e:\la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"))
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
from la_unpack_core import NpkArchive  # noqa: E402
from toolkit_core import bindict_table as BT  # noqa: E402

NPK = pathlib.Path(r"E:\mrzh\Documents\script.py314.lc.npk")

with NpkArchive(str(NPK)) as arc:
    raw = arc.read_entry(entry_index=25121)
    raw_chs = arc.read_entry(entry_index=33348)
ln = struct.unpack_from("<I", raw, 265)[0]
body = raw[269:269 + ln]
pool = BT.parse_legacy_chs_pool(raw_chs)
rows, _u = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)
names = {}
for r in rows:
    v = r["values"].get("name")
    if isinstance(v, tuple):
        v = v[1]
    if isinstance(v, str) and v:
        names[r["key"]] = v
print("item names", len(names))

d = json.loads((ROOT / "02_wiki/web/data/boards/lottery_periods.json").read_text(encoding="utf-8"))
bad = [i for i in d["items"] if i["name"].startswith("道具 ")]
hit = [i for i in bad if int(i["item_id"]) in names]
print("unresolved", len(bad), "covered", len(hit))
print("covered sample", [(i["item_id"], names[int(i["item_id"])], i["family"]) for i in hit[:10]])
miss = [i for i in bad if int(i["item_id"]) not in names]
print("still missing", len(miss), [(i["item_id"], i["family"]) for i in miss[:10]])

# reward pool
with NpkArchive(str(NPK)) as arc:
    raw_p = arc.read_entry(entry_index=29769)
    raw_pchs = arc.read_entry(entry_index=14650)
pln = struct.unpack_from("<I", raw_p, 265)[0]
pbody = raw_p[269:269 + pln]
ppool = BT.parse_legacy_chs_pool(raw_pchs)
pblob = pbody[8 + 4 * struct.unpack_from("<I", pbody, 0)[0]:]
prow, _u2 = BT.decode_table_rows(pbody, ppool, resolve_jumps=False, lenient=True)
by_key = {r["key"]: r for r in prow}
print("\npool rows", len(by_key), "391853 in:", 391853 in by_key)
row = by_key.get(391853)
if row:
    print("  row", str(row)[:500])
    ref = row["values"].get("reward")
    ref = ref[1] if isinstance(ref, tuple) else ref
    print("  ref", ref)
    if isinstance(ref, str) and ref.startswith("jump:"):
        tgt = BT.resolve_jump_target(pblob, int(ref.split(":")[1]), ppool)
        print("  jump ->", str(tgt)[:400])
