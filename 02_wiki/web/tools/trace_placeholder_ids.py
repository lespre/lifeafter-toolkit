# -*- coding: utf-8 -*-
r"""查奖池里「道具 <id>」占位名到底来自哪张表、为什么没回填。

输出：每个 id 命中的表名 + 该表的字段名列表（找 name 类字段）。
"""
from __future__ import annotations

import json
import pathlib
import re
import struct
import sys
import time


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
WEB = PROJ / "02_wiki/web"
CDATA = PROJ / "01_索引与产物/41_还原树/pe_test_script/com/cdata"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402


def main() -> int:
    d = json.loads((WEB / "data/boards/lottery_periods.json").read_text(encoding="utf-8"))
    ph = [i for i in d["items"] if re.match(r"^(道具|奖励|展示奖励) \d+$", str(i.get("name", "")))]
    ids = {str(i["item_id"]) for i in ph}
    print("占位 id 数", len(ids))

    pairs = []
    for p in sorted(CDATA.rglob("*.py")):
        if p.stem.endswith("_chs"):
            continue
        c = p.with_name(p.stem + "_chs.py")
        if c.is_file() and p.stat().st_size < 3_000_000:
            pairs.append((p, c))
    t0 = time.time()
    hits = {}
    for p, c in pairs:
        if time.time() - t0 > 420:
            print("超时")
            break
        try:
            raw = p.read_bytes()
            at = raw.find(b"x{")
            if at < 0:
                continue
            L = struct.unpack_from("<I", raw, at + 2)[0]
            body = raw[at + 6: at + 6 + L]
            rows, _ = BT.decode_table_rows(body, BT.parse_legacy_chs_pool(c.read_bytes()), resolve_jumps=False)
        except Exception:
            continue
        for r in rows:
            k = str(r["key"])
            if k in ids and k not in hits:
                fields = list(r["values"].keys())
                hits[k] = (p.name, fields[:12])
    print("命中", len(hits))
    for k, (tbl, fields) in list(hits.items())[:15]:
        print("  ", k, "|", tbl, "|", fields)
    (WEB / "data/boards/_placeholder_sources.json").write_text(
        json.dumps(hits, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
