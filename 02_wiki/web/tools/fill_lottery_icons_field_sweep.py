#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扫描 41_还原树/pe/配置/com/cdata 全部表，为一批 item_id 找「带 ui/ 路径字段」的行。

用途：奖池板上不在 common_item 的 id，需要去各自家族表（礼包/配方/涂装/时装/家具…）
取 icon 字段。本脚本不预设家族，直接把每张表解码一遍，找出 key 命中的行里所有
取值形如 ui/... 的字段，输出 id → [(表, 字段, 值)]。

只读；不改还原树；输出 JSON 到 01_索引与产物/30_分析/lottery_icon_field_sweep.json
"""
from __future__ import annotations

import json
import struct
import sys
import time
from pathlib import Path

PROJ = Path(r"E:\la拆包项目")
CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
WEB = PROJ / "02_wiki/web"
OUT = PROJ / "01_索引与产物/30_分析/lottery_icon_field_sweep.json"

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "01_索引与产物/10_索引/热更检测/pe_icon_bind"))
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402


def xbody(p: Path) -> bytes | None:
    raw = p.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        return None
    n = struct.unpack_from("<I", raw, at + 2)[0]
    return raw[at + 6: at + 6 + n]


def main() -> int:
    board = json.loads((WEB / "data/boards/lottery_periods.json").read_text(encoding="utf-8"))
    ico = WEB / "assets/lottery_icons"
    ids = list(dict.fromkeys(str(i["item_id"]) for i in board["items"]
                             if isinstance(i, dict) and i.get("item_id")))
    want = {i for i in ids if not (ico / f"{i}.png").exists()}
    print("目标 id", len(want))

    hits: dict[str, list[dict]] = {}
    scanned = failed = 0
    t0 = time.time()
    for p in sorted(CD.glob("*.py")):
        if p.name.endswith("_chs.py"):
            continue
        try:
            body = xbody(p)
            if body is None:
                failed += 1
                continue
            cp = p.with_name(p.stem + "_chs.py")
            pool = parse_legacy_chs_pool(cp.read_bytes()) if cp.exists() else []
            rows, _ = decode_table_rows_with_chs_slots(body, pool)
            scanned += 1
        except Exception:  # noqa: BLE001
            failed += 1
            continue
        for r in rows:
            k = str(r["key"])
            if k not in want:
                continue
            for f, v in r["values"].items():
                vv = v[1] if isinstance(v, tuple) else v
                if isinstance(vv, str) and (vv.startswith("ui/") or vv.startswith("jump:")):
                    if not any(h["field"] == f and h["table"] == p.stem for h in hits.setdefault(k, [])):
                        hits[k].append({"table": p.stem, "field": f, "value": vv})
    print(f"扫表 {scanned} 失败 {failed} 用时 {time.time() - t0:.1f}s 命中 id {len(hits)}/{len(want)}")
    OUT.write_text(json.dumps({"generated": time.strftime("%Y-%m-%d %H:%M:%S"),
                               "want": len(want), "hits": hits},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    from collections import Counter
    tb = Counter(h["table"] for hs in hits.values() for h in hs)
    print(tb.most_common(15))
    print("未命中", len(want - set(hits)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
