#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全量 icon 注册表：把各家族的 icon 字段合成一张 id → 图标路径 表。

来源（全部 PE 源）：
  common_item（90_表缓存 base 38,231 行）· gift_data · recipe · fashion_data(icons jump)
  · simple_fashion_data · equip_coating_data · player_module_appear_data · vehicle_ui_data
产物：01_索引与产物/30_分析/icon_registry.json
  { "meta": {...}, "icons": { "330001": {"path": "ui/...", "source": "chip_type_data", "kind": "..."} } }
"""
from __future__ import annotations

import json
import struct
import sys
from collections import Counter
from pathlib import Path

PROJ = Path(r"E:\la拆包项目")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))

import rebuild_lottery_periods as R  # noqa: E402
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402

OUT = PROJ / "01_索引与产物/30_分析/icon_registry.json"
CACHE = PROJ / "01_索引与产物/30_分析/90_表缓存"

# 表 → (icon 字段, 是否 jump 字符串组)
SIMPLE = {
    "gift_data": ["icon"],
    "recipe": ["icon"],
    "equip_coating_data": ["coating_icon"],
    "player_module_appear_data": ["icon"],
    "vehicle_ui_data": ["icon"],
    "body_sfx_data": ["icon"],
    "chip_type_data": ["chip_big_icon", "chip_icon"],
}
JUMPED = {
    "fashion_data": ["icons"],
    "simple_fashion_data": ["icons"],
    "gift_data": ["icons"],
}


def load_body(path: Path) -> bytes:
    raw = path.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        return b""
    size = struct.unpack_from("<I", raw, at + 2)[0]
    return raw[at + 6: at + 6 + size]


def main() -> int:
    registry: dict[str, dict] = {}

    def put(iid: int, path: str, source: str, kind: str) -> None:
        if not isinstance(path, str) or not path.startswith("ui/"):
            return
        key = str(iid)
        if key in registry:
            return
        registry[key] = {"path": path, "source": source, "kind": kind}

    # ① common_item（真表在表缓存里）
    base, chs = CACHE / "base_B42760CCA41DBC25.py", CACHE / "base_EF3A8474A5E5F7A4.py"
    if base.exists() and chs.exists():
        rows, _ = decode_table_rows_with_chs_slots(load_body(base), parse_legacy_chs_pool(chs.read_bytes()))
        for r in rows:
            v = {k: (x[1] if isinstance(x, tuple) else x) for k, x in r["values"].items()}
            put(r["key"], v.get("icon"), "common_item_data", "道具")
        print("common_item", len(rows))

    # ② 普通表
    for name, fields in SIMPLE.items():
        t = R._opt_table(R.TREE / f"{name}.py", R.TREE / f"{name}_chs.py")
        if not t.by_key:
            print("跳过(空)", name)
            continue
        n = 0
        for key, row in t.by_key.items():
            for f in fields:
                v = row["values"].get(f)
                if isinstance(v, str) and v.startswith("ui/"):
                    put(key, v, name, f)
                    n += 1
                    break
        print(name, "rows", len(t.by_key), "icon", n)

    # ③ jump 字符串组
    for name, fields in JUMPED.items():
        t = R._opt_table(R.TREE / f"{name}.py", R.TREE / f"{name}_chs.py")
        if not t.by_key:
            continue
        n = 0
        for key, row in t.by_key.items():
            for f in fields:
                vals = t.jump_values(row["values"].get(f))
                paths = [x for x in vals if isinstance(x, str) and x.startswith("ui/")]
                if paths:
                    put(key, paths[0], name, f)
                    n += 1
                    break
        print(name, "rows", len(t.by_key), "icon", n)

    kinds = Counter(v["source"] for v in registry.values())
    doc = {"meta": {"name": "全量图标注册表", "generated": "2026-11-03",
                    "sources": dict(kinds), "count": len(registry)},
           "icons": registry}
    OUT.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    print("总计", len(registry), dict(kinds.most_common(8)))
    print("写出", OUT.name, round(OUT.stat().st_size / 1e6, 2), "MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
