# -*- coding: utf-8 -*-
"""用找到的中文池当 pool，在 npk 里找出「行键 1110189 = 浪漫过载」的那张数据表。"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"))
from toolkit_core import hotfix_rows as HR                       # noqa: E402
from toolkit_core.bindict_table import decode_table_rows, parse_legacy_chs_pool  # noqa: E402
from la_unpack_core import npk_decode_entry                      # noqa: E402

NPK = ROOT / "01_索引与产物/源包/pe_hotfix/20261030_2225/script.py314.lc.npk"
POOLSRC = ROOT / "01_索引与产物/30_分析/hit_EF3A8474A5E5F7A4.bin"
WANT = 1110189
MIN_DECODED = 200_000


class _E:
    __slots__ = ("packed",)

    def __init__(self, p: int) -> None:
        self.packed = p


def main() -> int:
    pool = parse_legacy_chs_pool(POOLSRC.read_bytes())
    ents = HR._entries(NPK)
    cand = [e for e in ents if int(e.get("decoded") or 0) >= MIN_DECODED]
    print("池 %d 条 ｜ 条目 %d ｜ 候选(decoded≥1MB) %d" % (len(pool), len(ents), len(cand)))
    blob = NPK.read_bytes()
    for e in cand:
        try:
            data = npk_decode_entry(blob[e["offset"]:e["offset"] + e["packed"]],
                                    e["decoded"], e["flag"], entry=_E(e["packed"]))
        except Exception:                            # noqa: BLE001
            continue
        at = data.find(b"x{")
        body = data[at + 6:at + 6 + int.from_bytes(data[at + 2:at + 6], "little")] if at >= 0 else data
        try:
            rows, _ = decode_table_rows(body, pool, resolve_jumps=False, lenient=True)
        except Exception:                            # noqa: BLE001
            continue
        hitrow = None
        for r in rows:
            v = {k: (x[1] if isinstance(x, tuple) else x) for k, x in (r.get("values") or {}).items()}
            if r.get("key") == WANT or "浪漫过载" in str(v.get("name")):
                hitrow = (r, v)
                break
        if hitrow:
            if True:
                    r, v = hitrow
                    print("命中 fid=%s ｜ 行 %d ｜ key=%s" % (e["fid"], len(rows), r.get("key")))
                    print({k: v[k] for k in list(v)[:12]})
                    out = ROOT / "01_索引与产物/30_分析/hit_item_rows.json"
                    out.write_text(__import__("json").dumps(v, ensure_ascii=False, indent=1), encoding="utf-8")
                    print("写出", out)
                    return 0
    print("没找到含该行键的表")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
