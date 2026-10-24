# -*- coding: utf-8 -*-
"""载具分类改为真表口径：
  类型  = vehicle_brand_data.type_name（6 类）
  子类  = 同表 brands 跳转组里的品牌名
  归属  = vehicle_brand_type_conf.brand_type（按载具 id）

来源树：script.py314.lc.npk/com/cdata（含 _chs 池）
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys
from collections import Counter

PROJ = pathlib.Path("E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

CD = PROJ / "01_索引与产物/41_还原树/pe/配置_基线包/com/cdata"
BOARD = WEB / "data/boards/vehicle_full.json"
v = lambda x: x[1] if isinstance(x, tuple) else x


def load(name):
    p = CD / (name + ".py")
    raw = p.read_bytes()
    at = raw.find(b"x{")
    L = int.from_bytes(raw[at + 2:at + 6], "little")
    body = raw[at + 6:at + 6 + L]
    cnt = struct.unpack_from("<I", body, 0)[0]
    chs = CD / (name + "_chs.py")
    pool = BT.parse_legacy_chs_pool(chs.read_bytes()) if chs.exists() else None
    rows = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)[0]
    return rows, pool, body[8 + 4 * cnt:]


def main() -> int:
    rows, pool, blob = load("vehicle_brand_data")
    types, brand2type = {}, {}
    for r in rows:
        val = r["values"]
        tid = int(r["key"])
        types[tid] = v(val.get("type_name"))
        b = val.get("brands")
        if isinstance(b, tuple):
            g = BT.read_27_group(blob, int(str(b[1]).split(":")[1]))
            if g:
                for i in g[1]:
                    if i < len(pool):
                        brand2type[str(pool[i])] = types[tid]

    conf, _, _ = load("vehicle_brand_type_conf")
    id2type = {}
    for r in conf:
        bt = v(r["values"].get("brand_type"))
        if bt is not None:
            id2type[str(r["key"])] = types.get(int(bt), "未分类")

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    for it in board["items"]:
        t = None
        for vid in (it.get("vehicle_ids") or [it.get("vehicle_id")]):
            t = id2type.get(str(vid))
            if t:
                break
        brand = str(it.get("brand_name") or "").strip()
        sub = None
        if brand:
            for bname in brand2type:
                if brand == bname or brand.startswith(bname) or bname.startswith(brand):
                    sub = bname
                    break
        if sub is None:
            nm = str(it.get("name") or "")
            for bname in brand2type:
                if nm.startswith(bname):
                    sub = bname
                    break
        if not t:
            nm2 = str(it.get("name") or "")
            for bname, tname in brand2type.items():
                if nm2.startswith(bname) or (sub and sub == bname):
                    t = tname
                    break
        if not t and str(it.get("brand_name") or ""):
            t = brand2type.get(str(it.get("brand_name")).strip())
        it["vehicle_class"] = t or "未分类"
        it["vehicle_subclass"] = sub
        it["class_source"] = "vehicle_brand_type_conf.brand_type + vehicle_brand_data.brands"

    board["meta"]["filters"] = [{"key": "vehicle_class", "label": "类型"},
                                {"key": "vehicle_subclass", "label": "子类"}]
    board["meta"]["notes"] = ((board["meta"].get("notes") or "")
                              + " ｜ 类型=vehicle_brand_data.type_name（6 类），子类=brands 池")
    BOARD.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")

    print("类型分布", Counter(i["vehicle_class"] for i in board["items"]).most_common())
    print("子类分布", Counter(i["vehicle_subclass"] or "未匹配" for i in board["items"]).most_common(12))
    print("未分类", sum(1 for i in board["items"] if i["vehicle_class"] == "未分类"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
