# -*- coding: utf-8 -*-
"""解活动表：用热更 npk 里按内容命中的条目，试各个候选池，找出能解出活动名的那组。"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"))
from toolkit_core import hotfix_rows as HR                                       # noqa: E402
from toolkit_core.bindict_table import decode_table_rows, parse_legacy_chs_pool  # noqa: E402
from la_unpack_core import npk_decode_entry                                      # noqa: E402

NPK = ROOT / "01_索引与产物/源包/pe_hotfix/20261030_2225/script.py314.lc.npk"
TABLE_FID = "A703C08E329A6FE2"
POOL_FIDS = ["EF3A8474A5E5F7A4", "B8699B2984086DE5", "C9F3A471F90F79B1", "F1B54512F512F0FE"]
NEEDLE = "万圣绮夜"


class _E:
    __slots__ = ("packed",)

    def __init__(self, p: int) -> None:
        self.packed = p


def fetch(fid: str) -> bytes | None:
    blob = NPK.read_bytes()
    for e in HR._entries(NPK):
        if str(e["fid"]).upper() != fid:
            continue
        return npk_decode_entry(blob[e["offset"]:e["offset"] + e["packed"]],
                                e["decoded"], e["flag"], entry=_E(e["packed"]))
    return None


def rows_of(data: bytes, pool: list):
    at = data.find(b"x{")
    if at >= 0:
        body = data[at + 6:at + 6 + struct.unpack_from("<I", data, at + 2)[0]]
    else:
        body = data
    return decode_table_rows(body, pool, resolve_jumps=False, lenient=True)[0]


def main() -> int:
    tdata = fetch(TABLE_FID)
    print("活动表 %.2f MB" % (len(tdata) / 1e6))

    best = None
    for pf in POOL_FIDS:
        pdata = fetch(pf)
        try:
            pool = parse_legacy_chs_pool(pdata)
        except Exception as e:                       # noqa: BLE001
            print("池 %s 解析失败 %s" % (pf, type(e).__name__))
            continue
        try:
            rows = rows_of(tdata, pool)
        except Exception as e:                       # noqa: BLE001
            print("池 %s（%d 条）解表失败 %s" % (pf, len(pool), str(e)[:50]))
            continue
        names = 0
        for r in rows[:50]:
            v = {k: (x[1] if isinstance(x, tuple) else x) for k, x in (r.get("values") or {}).items()}
            if any(NEEDLE in str(x) for x in v.values()):
                names += 1
        print("池 %s（%d 条）→ 行 %d ｜ 前 50 行含活动名 %d" % (pf, len(pool), len(rows), names))
        if names and (best is None or names > best[1]):
            best = (pf, len(rows), rows, pool)

    if not best:
        print("没有一组能解出活动名")
        return 1
    pf, nrows, rows, pool = best
    print("\n采用池", pf, "｜ 行", nrows)
    out = []
    for r in rows:
        v = {k: (x[1] if isinstance(x, tuple) else x) for k, x in (r.get("values") or {}).items()}
        out.append({"key": r.get("key"), **v})
    dst = ROOT / "01_索引与产物/30_分析/huodong_conf_rows.json"
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("写出", dst)
    for x in out[:5]:
        print("  ", x.get("key"), str(x.get("name"))[:18])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
