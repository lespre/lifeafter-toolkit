# -*- coding: utf-8 -*-
"""解 weapon_skin_effect_show_data：皮肤 → 战斗表现的正式特效名。

表很小（6.7 KB），先把原始结构打出来，确认字段后再接到板子。
"""
from __future__ import annotations

import json
import struct
import sys

sys.path.insert(0, "E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
sys.path.insert(0, "E:/la拆包项目/02_wiki/web/tools")
from toolkit_core.bindict_table import decode_table_rows, parse_legacy_chs_pool  # noqa: E402
from _src import cdata_dir  # noqa: E402

CD = cdata_dir()


def main() -> int:
    name = "weapon_skin_effect_show_data"
    raw = (CD / (name + ".py")).read_bytes()
    at = raw.find(b"x{")
    n = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + n]
    chs = CD / (name + "_chs.py")
    pool = parse_legacy_chs_pool(chs.read_bytes()) if chs.exists() else []
    print("chs 池条数", len(pool))
    rows, _ = decode_table_rows(body, pool, resolve_jumps=True, lenient=True)
    print("行数", len(rows))
    for r in rows[:3]:
        v = {k: (x[1] if isinstance(x, tuple) else x) for k, x in (r.get("values") or {}).items()}
        print("key", r["key"], json.dumps(v, ensure_ascii=False)[:500])
        res = r.get("resolved") or {}
        for k, val in list(res.items())[:4]:
            print("   resolved", k, json.dumps(val, ensure_ascii=False)[:200])
    # 找含'辉光绽放'的行
    for r in rows:
        s = json.dumps({k: (x[1] if isinstance(x, tuple) else x) for k, x in (r.get("values") or {}).items()}, ensure_ascii=False)
        if "辉光绽放" in s:
            print("== 命中行", r["key"])
            print(s[:800])
            break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
