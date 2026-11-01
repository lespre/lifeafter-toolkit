# -*- coding: utf-8 -*-
r"""只读探查：染色 colors / 主题海报字段 / 误挂卡来源。"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

PROJ = pathlib.Path(r"e:\la拆包项目")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))

from toolkit_core import bindict_table as BT  # noqa

CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"


def load(stem):
    raw = (CD / f"{stem}.py").read_bytes()
    at = raw.find(b"x{")
    ln = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + ln]
    pool = BT.parse_legacy_chs_pool((CD / f"{stem}_chs.py").read_bytes())
    rows = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)[0]
    cnt = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * cnt:]
    return rows, blob, pool


def sv(x):
    return x[1] if isinstance(x, tuple) else x


def jl(blob, row, field, pool):
    got = row["values"].get(field)
    if not got:
        return []
    tag, val = got
    if tag != "0x0b":
        return [val]
    try:
        off = int(str(val).split(":")[1])
    except (IndexError, ValueError):
        return []
    out = []

    def walk(g):
        kind, els = g
        for e in els:
            if kind == 0x0B:
                g2 = BT.read_27_group(blob, e)
                if g2:
                    walk(g2)
            elif kind == 0x05:
                out.append(pool[e] if 0 <= e < len(pool) else f"<oob:{e}>")
            else:
                out.append(e)

    g0 = BT.read_27_group(blob, off)
    if g0:
        walk(g0)
    return out


def show_fields(stem, key=None, limit=3):
    rows, blob, pool = load(stem)
    print(f"\n### {stem}: {len(rows)} rows, fields={list(rows[0]['values'].keys()) if rows else '?'}")
    picked = [r for r in rows if key is None or r['key'] == key][:limit]
    for r in picked:
        print(f"  row {r['key']}:")
        for k, v in r['values'].items():
            print(f"    {k:36s} {v}  jl={jl(blob, r, k, pool)[:4]}")
    return rows, blob, pool


def main():
    show_fields("appear_change_color_data", 361310)
    # 找一个 colors 有值的行
    rows, blob, pool = load("appear_change_color_data")
    hit = []
    for r in rows:
        vals = jl(blob, r, "colors", pool)
        if vals:
            hit.append((r["key"], vals[:8]))
    print("\ncolors 有值行:", len(hit), "样本:", hit[:3])
    print("字段名全集:", list(rows[0]["values"].keys()))

    show_fields("fashion_obtain_handbook_data", None, 2)
    show_fields("fashion_bg_data", None, 2)

    # 误挂卡：fw_facepreset_brand_1017
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    for it in board["items"]:
        if it["id"] in ("fw_facepreset_brand_1017", "fw_66eb2959a7", "fw_490892adfd", "fw_5eba8c89f4", "fw_d7284983fe"):
            print("\n=== card", it["id"], it.get("name"), "row_keys", it.get("row_keys"), "part", it.get("part"))
            for k in ("theme", "display_bg", "anim_graph", "hide_idle_anim", "model_change_color_id", "dye", "part_code"):
                if it.get(k):
                    print("   ", k, json.dumps(it[k], ensure_ascii=False)[:220])
            frows, fblob, fpool = load("fashion_data")
            for k in (it.get("row_keys") or []):
                try:
                    kk = int(k)
                except Exception:
                    continue
                if any(r["key"] == kk for r in frows):
                    r = next(r for r in frows if r["key"] == kk)
                    print("    fmap row", kk, "name=", sv(r["values"].get("name")), "part=", sv(r["values"].get("part")))
            # 同名的 fashion_data 行
            for r in frows:
                if sv(r["values"].get("name")) == it.get("name"):
                    print("    same-name fmap key", r["key"], "part=", sv(r["values"].get("part")).__class__)
                    break


if __name__ == "__main__":
    raise SystemExit(main())
