# -*- coding: utf-8 -*-
"""解析找到的那个条目：确认是不是道具表，并取出 1110189/1110194/1110205 的名字。"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core.bindict_table import decode_table_rows, parse_legacy_chs_pool  # noqa: E402

BIN = ROOT / "01_索引与产物/30_分析/hit_EF3A8474A5E5F7A4.bin"
WANT = (1110189, 1110194, 1110205)


def main() -> int:
    raw = BIN.read_bytes()
    print("大小 %.1f MB ｜ 头 16B %s" % (len(raw) / 1e6, raw[:16].hex(" ")))
    at = raw.find(b"x{")
    print("x{ 位置", at)
    body = raw[at + 6:at + 6 + struct.unpack_from("<I", raw, at + 2)[0]] if at >= 0 else raw

    # 没有独立 _chs 池时，先试内联文本（pool=[]）
    rows, _ = decode_table_rows(body, [], resolve_jumps=False, lenient=True)
    print("解出行", len(rows))
    if not rows:
        return 1

    keys = [r["key"] for r in rows if isinstance(r.get("key"), int)]
    print("键范围 %s .. %s ｜ 行数 %d" % (min(keys), max(keys), len(keys)))
    print("首行字段", list({k: 1 for k, _ in (rows[0].get("values") or {}).items()})[:10])

    found = []
    for r in rows:
        if r.get("key") in WANT:
            v = {k: (x[1] if isinstance(x, tuple) else x) for k, x in (r.get("values") or {}).items()}
            found.append((r["key"], v))
            print("\n== %s" % r["key"])
            for k in sorted(v):
                print("   %-24s %s" % (k, json.dumps(v[k], ensure_ascii=False)[:90]))
    print("\n命中 %d / 3" % len(found))
    out = ROOT / "01_索引与产物/30_分析/hit_table_names.json"
    out.write_text(json.dumps({str(k): v for k, v in found}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("写出", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
