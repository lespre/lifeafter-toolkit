# -*- coding: utf-8 -*-
"""从 PE npk 的那张 39,146 行道具表里取出 1110189 / 1110194 / 1110205 的完整行（含名字）。"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"))
from toolkit_core import hotfix_rows as HR                                       # noqa: E402
from toolkit_core.bindict_table import decode_table_rows, parse_legacy_chs_pool  # noqa: E402
from la_unpack_core import npk_decode_entry                                      # noqa: E402

NPK = ROOT / "01_索引与产物/源包/pe_hotfix/20261030_2225/script.py314.lc.npk"
POOLSRC = ROOT / "01_索引与产物/30_分析/hit_EF3A8474A5E5F7A4.bin"
FID = "B42760CCA41DBC25"
WANT = (1110189, 1110194, 1110205)


class _E:
    __slots__ = ("packed",)

    def __init__(self, p: int) -> None:
        self.packed = p


def main() -> int:
    pool = parse_legacy_chs_pool(POOLSRC.read_bytes())
    blob = NPK.read_bytes()
    ent = next(e for e in HR._entries(NPK) if str(e["fid"]).upper() == FID)
    data = npk_decode_entry(blob[ent["offset"]:ent["offset"] + ent["packed"]],
                            ent["decoded"], ent["flag"], entry=_E(ent["packed"]))
    at = data.find(b"x{")
    body = data[at + 6:at + 6 + int.from_bytes(data[at + 2:at + 6], "little")] if at >= 0 else data
    rows, _ = decode_table_rows(body, pool, resolve_jumps=False, lenient=True)
    print("行数", len(rows), "｜ decoded %.1f MB" % (len(data) / 1e6))

    out = {}
    for r in rows:
        if r.get("key") in WANT:
            v = {k: (x[1] if isinstance(x, tuple) else x) for k, x in (r.get("values") or {}).items()}
            out[str(r["key"])] = v
            print("\n== %s" % r["key"])
            for k in sorted(v):
                print("   %-22s %s" % (k, json.dumps(v[k], ensure_ascii=False)[:120]))
    dst = ROOT / "01_索引与产物/30_分析/item_rows_hotfix_3.json"
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n写出", dst, "｜ 命中", len(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
