# -*- coding: utf-8 -*-
"""直接解 weapon_skin_effect_show_data，看真名到底怎么挂在皮肤上。

输出：行数、key 分布、是否含 1110189、以及一条行的完整字段/组。
"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

PROJ = Path(r"E:\la拆包项目")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
import rebuild_lottery_periods as R  # noqa: E402
from toolkit_core.bindict_table import decode_table_rows, parse_legacy_chs_pool  # noqa: E402

CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
NAME = "weapon_skin_effect_show_data"


def main() -> int:
    raw = (CD / f"{NAME}.py").read_bytes()
    at = raw.find(b"x{")
    n = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + n]
    chs = CD / f"{NAME}_chs.py"
    pool = parse_legacy_chs_pool(chs.read_bytes()) if chs.exists() else []
    rows, unbound = decode_table_rows(body, pool, resolve_jumps=True, lenient=True)
    print("表大小", len(raw), "| chs 池", len(pool), "| 行", len(rows))
    keys = [r["key"] for r in rows]
    print("key 样例", keys[:8], "... 共", len(keys))
    print("含 1110189?", 1110189 in keys)

    def flat(r):
        v = {k: (x[1] if isinstance(x, tuple) else x) for k, x in (r.get("values") or {}).items()}
        res = r.get("resolved") or {}
        return v, res

    tgt = next((r for r in rows if str(r["key"]) == "1110189"), None)
    for r in ([tgt] if tgt else rows[:1]):
        v, res = flat(r)
        print("\n== key", r["key"])
        print(" 字段:", json.dumps(v, ensure_ascii=False)[:600])
        for k, val in list(res.items())[:6]:
            print("  resolved", k, json.dumps(val, ensure_ascii=False)[:300])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
