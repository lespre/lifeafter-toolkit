# -*- coding: utf-8 -*-
r"""只读探查 2：染色 colors 缺失行 / 主题海报字段全集。"""
from __future__ import annotations

import collections
import pathlib
import struct
import sys

PROJ = pathlib.Path(r"e:\la拆包项目")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))

from toolkit_core import bindict_table as BT  # noqa

CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"


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


def main():
    rows, blob, pool = load("appear_change_color_data")
    allkeys = collections.Counter()
    for r in rows:
        for k in r["values"]:
            allkeys[k] += 1
    print("appear_change_color_data 字段出现次数:", dict(allkeys), "总行", len(rows))
    no_colors = [r for r in rows if "colors" not in r["values"]]
    print("无 colors 字段行:", len(no_colors))
    for r in no_colors[:5]:
        print("  row", r["key"], r["values"])
        print("    __tail__:", r.get("__tail__"), r.get("lenient_recovered"))
    # 有 colors 但 color_values
    with_colors = [r for r in rows if "colors" in r["values"]]
    print("有 colors 行:", len(with_colors), "其中 color_values 有值:",
          sum(1 for r in with_colors if jl(blob, r, "color_values", pool)))
    for r in with_colors[:2]:
        print("  sample", r["key"], "colors=", jl(blob, r, "colors", pool)[:8],
              "color_values=", jl(blob, r, "color_values", pool)[:8])

    # 主题表字段全集与取值
    hb, hb_blob, hb_pool = load("fashion_obtain_handbook_data")
    hk = collections.Counter()
    for r in hb:
        for k in r["values"]:
            hk[k] += 1
    print("\nfashion_obtain_handbook_data 字段出现:", dict(hk), "总行", len(hb))
    for r in hb[:1]:
        print("  row", r["key"], {k: jl(hb_blob, r, k, hb_pool)[:3] for k in r["values"]})
    # 找 themes containing target ids
    targets = {166464, 467620, 3049}
    for r in hb:
        ids = set(x for x in jl(hb_blob, r, "fashion_ids", hb_pool) if isinstance(x, int))
        if ids & targets:
            print("  theme row", r["key"], {k: jl(hb_blob, r, k, hb_pool)[:4] for k in r["values"]})

    # 看看 oral: 有 open_time 的行
    ot = [r for r in hb if jl(hb_blob, r, "open_time", hb_pool)]
    print("含 open_time 行:", len(ot))
    if ot:
        print("  样本", ot[0]["key"], {k: jl(hb_blob, ot[0], k, hb_pool)[:3] for k in ot[0]["values"]})
    po = [r for r in hb if jl(hb_blob, r, "poster_img_path", hb_pool)]
    print("含 poster_img_path 行:", len(po))


if __name__ == "__main__":
    raise SystemExit(main())
