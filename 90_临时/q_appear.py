# -*- coding: utf-8 -*-
"""按名字/关键词查 player_appear_data + fashion_data 的行，打印 model_name 等全部字段。"""
import sys, pathlib, json
PROJ = pathlib.Path(r"E:/la拆包项目")
CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT

v = lambda x: x[1] if isinstance(x, tuple) else x

def load(name):
    py = CD / (name + ".py")
    if not py.is_file():
        return []
    raw = py.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        return []
    L = int.from_bytes(raw[at+2:at+6], "little")
    chs = CD / (name + "_chs.py")
    pool = BT.parse_legacy_chs_pool(chs.read_bytes()) if chs.is_file() else None
    return BT.decode_table_rows(raw[at+6:at+6+L], pool, resolve_jumps=False, lenient=True)[0]

kw = sys.argv[1] if len(sys.argv) > 1 else "云糖绒翼"
for t in ("player_appear_data", "fashion_data"):
    rows = load(t)
    print("==", t, len(rows))
    for r in rows:
        val = r["values"]
        nm = str(v(val.get("name")) or "")
        if kw in nm:
            out = {k: v(val[k]) for k in val}
            print(json.dumps({"key": str(r["key"]), **out}, ensure_ascii=False)[:900])
            print()
