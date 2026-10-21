# -*- coding: utf-8 -*-
r"""给「展示奖励 <id>」补名：跨表扫描 common_item / fashion / gift / vehicle / body_sfx / recipe。"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "04_站点/web"
CD = PROJ / "03_执行/41_还原树/pe_test_script/com/cdata"
sys.path.insert(0, str(PROJ / "01_工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

TABLES = [
    "oversea/common_item_data_auto_oversea_data_kj1",
    "fashion_data",
    "gift_data",
    "vehicle_ui_data",
    "body_sfx_data",
    "recipe",
    "drone_conf_data",
]


def load(nm: str):
    p = CD / (nm + ".py")
    c = CD / (nm + "_chs.py")
    if not p.is_file():
        return None
    raw = p.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        return None
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + L]
    pool = BT.parse_legacy_chs_pool(c.read_bytes()) if c.is_file() else {}
    try:
        rows, _ = BT.decode_table_rows(body, pool, resolve_jumps=False)
    except Exception:
        return None
    return rows


def main() -> int:
    board_p = WEB / "data/boards/lottery_periods.json"
    d = json.loads(board_p.read_text(encoding="utf-8"))
    un = [i for i in d["items"] if str(i.get("name", "")).startswith("展示奖励")]
    ids = {str(i["item_id"]) for i in un if i.get("item_id")}
    print("待补名", len(ids))

    found = {}
    for nm in TABLES:
        rows = load(nm)
        if not rows:
            print("  跳过", nm)
            continue
        hit = 0
        for r in rows:
            if str(r["key"]) not in ids:
                continue
            f = {k: (v[1] if isinstance(v, tuple) and len(v) == 2 else v) for k, v in r["values"].items()}
            name = None
            for k in ("name", "item_name", "buff_item_name", "chip_name", "furniture_name"):
                if f.get(k):
                    name = str(f[k]).strip()
                    break
            if name:
                found[str(r["key"])] = (name, nm)
                hit += 1
        print("  %-46s 命中 %d" % (nm, hit))

    print("总命中", len(found))
    for k, (n, src) in list(found.items())[:12]:
        print("   ", k, "→", n, "|", src)

    n = 0
    for it in d["items"]:
        if not str(it.get("name", "")).startswith("展示奖励"):
            continue
        hit = found.get(str(it.get("item_id")))
        if hit:
            it["name"] = hit[0]
            it["name_source"] = hit[1]
            n += 1
    board_p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/lottery_periods.js").write_text(
        "window.WIKI_BOARD_lottery_periods = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    print("回填", n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
