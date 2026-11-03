#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""建全站 id → common_item 图标路径索引（只读配置，不写客户端）。

数据源（只读）：
  01_索引与产物/30_分析/90_表缓存/base_B42760CCA41DBC25.py   common_item 行表
  01_索引与产物/30_分析/90_表缓存/base_EF3A8474A5E5F7A4.py   common_item chs 池
  01_索引与产物/41_还原树/pe/资源/                            图标 ktx 落盘根

产物：01_索引与产物/30_分析/common_item_icon_index.json
  meta        来源/生成时间/统计
  icons       {item_id: "ui/item_icon/icon_7000"}
  local_ktx   {item_id: "ui/item_icon/icon_7000_b.ktx"}  仅本地真实存在的
"""
from __future__ import annotations

import json
import struct
import sys
import time
from pathlib import Path

PROJ = Path(r"E:\la拆包项目")
CACHE = PROJ / "01_索引与产物/30_分析/90_表缓存"
RES = PROJ / "01_索引与产物/41_还原树/pe/资源"
OUT = PROJ / "01_索引与产物/30_分析/common_item_icon_index.json"
BASE = CACHE / "base_B42760CCA41DBC25.py"
CHS = CACHE / "base_EF3A8474A5E5F7A4.py"

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402

SUFFIXES = ("_b", "_s", "", "_sq", "_l")


def load_body(path: Path) -> bytes:
    raw = path.read_bytes()
    at = raw.find(b"x{")
    size = struct.unpack_from("<I", raw, at + 2)[0]
    return raw[at + 6: at + 6 + size]


def pick(path_noext: str) -> str | None:
    """返回相对 RES 的落盘路径（优先 _b 大图，其次 _s，再裸名）。"""
    p = path_noext.lstrip("/")
    for suf in SUFFIXES:
        for ext in (".ktx", ".dds", ".png"):
            rel = f"{p}{suf}{ext}"
            if (RES / rel).exists():
                return rel
    return None


def main() -> int:
    body = load_body(BASE)
    pool = parse_legacy_chs_pool(CHS.read_bytes())
    rows, _ = decode_table_rows_with_chs_slots(body, pool)
    icons: dict[str, str] = {}
    for r in rows:
        v = {k: (x[1] if isinstance(x, tuple) else x) for k, x in r["values"].items()}
        ic = v.get("icon")
        if isinstance(ic, bytes):
            ic = ic.decode("utf-8", "replace")
        if isinstance(ic, str) and ic.startswith("ui/"):
            icons[str(r["key"])] = ic

    local: dict[str, str] = {}
    for iid, ic in icons.items():
        hit = pick(ic)
        if hit:
            local[iid] = hit

    payload = {
        "meta": {
            "name": "common_item 图标索引（id → 客户端图标路径）",
            "source": "PE 只读：common_item 真表 base_B42760CCA41DBC25 + chs 池 base_EF3A8474A5E5F7A4",
            "resource_root": "01_索引与产物/41_还原树/pe/资源",
            "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "rows": len(rows),
            "with_icon": len(icons),
            "local_ktx": len(local),
            "icon_prefix_note": "icon 原样保留表内路径（无扩展名）；local_ktx 为 _b > _s > 裸名 的落盘实选",
        },
        "icons": dict(sorted(icons.items(), key=lambda kv: kv[0])),
        "local_ktx": dict(sorted(local.items(), key=lambda kv: kv[0])),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"rows={len(rows)} with_icon={len(icons)} local_ktx={len(local)}")
    print(f"写出 {OUT} ({OUT.stat().st_size/1024/1024:.2f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
