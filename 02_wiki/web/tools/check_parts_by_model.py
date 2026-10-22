# -*- coding: utf-8 -*-
r"""按 model_id 反查部位：只在「源表该 model 只有一种部位」时比对，避免整套误判。"""
from __future__ import annotations

import json
import pathlib
import struct
import sys
from collections import defaultdict

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
BASE = PROJ / "01_索引与产物/41_还原树/Documents/script.py314.lc.npk/com/cdata"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
import toolkit_core.bindict_table as BT  # noqa: E402

PART_CN = {"hat": "头饰", "cloth": "衣服", "bag": "背包", "pendant": "挂饰", "suit": "整套",
           "light": "光源", "face": "面饰", "hair": "发饰", "projection": "投影"}


def main() -> int:
    p = BASE / "fashion_data.py"
    c = BASE / "fashion_data_chs.py"
    raw = p.read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + L]
    pool = BT.parse_legacy_chs_pool(c.read_bytes())
    rows, _ = BT.decode_table_rows(body, pool, resolve_jumps=True)
    parts: dict[int, set] = defaultdict(set)
    names: dict[int, list] = defaultdict(list)
    for r in rows:
        f = {k: (v[1] if isinstance(v, tuple) and len(v) == 2 else v) for k, v in r["values"].items()}
        mid, pt = f.get("model_id"), str(f.get("part_type") or "")
        if mid is None or not pt:
            continue
        parts[int(mid)].add(PART_CN.get(pt, pt))
        names[int(mid)].append(str(f.get("name") or ""))

    d = json.loads((WEB / "data/boards/fashion_wardrobe.json").read_text(encoding="utf-8"))
    conf = []
    for it in d["items"]:
        cur = set(it.get("part_bucket") or [])
        if cur == {"整套"}:
            continue
        mid = it.get("model_id")
        if mid is None:
            continue
        want = parts.get(int(mid))
        if not want or len(want) != 1:
            continue
        w = next(iter(want))
        if w not in cur:
            conf.append((it.get("id"), it.get("name"), sorted(cur), [w], names[int(mid)][:2]))
    print("按 model 判定冲突 %d 件" % len(conf))
    for c2 in conf[:15]:
        print("   %-14s %-20s 板上=%-8s 源=%-6s %s" % c2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
