# -*- coding: utf-8 -*-
"""尝试解 weapon_skin_effect_show_data（皮肤战斗表现正式名表）。"""
from __future__ import annotations

import json
import sys

sys.path.insert(0, "E:/la拆包项目/02_wiki/web")
sys.path.insert(0, "E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
sys.path.insert(0, "E:/la拆包项目/02_wiki/web/tools")

from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402
from _src import cdata_dir  # noqa: E402

CD = cdata_dir()
NAME = "weapon_skin_effect_show_data"


def try_all() -> None:
    raw = (CD / (NAME + ".py")).read_bytes()
    chs_raw = (CD / (NAME + "_chs.py")).read_bytes()
    pool = parse_legacy_chs_pool(chs_raw)
    print("chs 池", len(pool))

    from bindict_provenance import decode_table_rows_with_chs_slots

    candidates = {"整文件": raw}
    at = raw.find(b"x{")
    if at >= 0:
        import struct

        n = struct.unpack_from("<I", raw, at + 2)[0]
        candidates["x{ 段"] = raw[at + 6: at + 6 + n]

    for label, blob in candidates.items():
        try:
            rows, unbound = decode_table_rows_with_chs_slots(blob, pool)
        except Exception as e:  # noqa: BLE001
            print(label, "解失败", type(e).__name__, str(e)[:80])
            continue
        print(label, "行", len(rows), "未绑定", len(unbound) if unbound else 0)
        for r in rows[:2]:
            v = {k: (x[1] if isinstance(x, tuple) else x) for k, x in (r.get("values") or {}).items()}
            print("   key", r.get("key"), json.dumps(v, ensure_ascii=False)[:300])
        if rows:
            hits = [r for r in rows if "辉光绽放" in json.dumps(
                {k: (x[1] if isinstance(x, tuple) else x) for k, x in (r.get("values") or {}).items()},
                ensure_ascii=False)]
            print("   含辉光绽放的行", len(hits))
            if hits:
                v = {k: (x[1] if isinstance(x, tuple) else x) for k, x in (hits[0].get("values") or {}).items()}
                print("   ", json.dumps(v, ensure_ascii=False)[:500])


if __name__ == "__main__":
    try_all()
