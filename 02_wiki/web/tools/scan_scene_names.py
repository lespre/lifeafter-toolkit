# -*- coding: utf-8 -*-
"""暴力扫全部 cdata 表：找行键命中 scene/类型 id 且带中文名字的表。"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
from toolkit_core import bindict_table as BT  # noqa: E402

CD = pathlib.Path(r"E:/la拆包项目/01_索引与产物/41_还原树/pe_20261020/com/cdata")
OUT = pathlib.Path(r"E:/la拆包项目/01_索引与产物/30_分析/伤害系统逆向/scene_name_scan_hits.json")
WANT = {580, 750, 799, 754, 724, 2005, 200}


def has_cjk(s: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in s)


def main() -> int:
    files = [p for p in CD.rglob("*.py") if "_chs" not in p.name]
    print("待扫表", len(files))
    hits = []
    for i, p in enumerate(files):
        try:
            b = p.read_bytes()
        except OSError:
            continue
        at = b.find(b"x{")
        if at < 0:
            continue
        try:
            L = struct.unpack_from("<I", b, at + 2)[0]
            payload = b[at + 6:at + 6 + L]
        except Exception:
            continue
        chs = p.with_name(p.stem + "_chs.py")
        pool = {}
        if chs.is_file():
            try:
                pool = BT.parse_legacy_chs_pool(chs.read_bytes())
            except Exception:
                pool = {}
        try:
            rows, _ = BT.decode_table_rows(payload, pool, resolve_jumps=False)
        except Exception:
            continue
        for r in rows:
            try:
                key = int(r["key"])
            except Exception:
                continue
            if key not in WANT:
                continue
            names = []
            for k, v in r["values"].items():
                x = v[1] if isinstance(v, tuple) else v
                if isinstance(x, str) and has_cjk(x):
                    names.append(x)
            if names:
                hits.append({"table": str(p.relative_to(CD)), "key": key, "strings": names[:5]})
                break
        if i % 500 == 0:
            print("  ...%d/%d 命中%d" % (i, len(files), len(hits)))
    OUT.write_text(json.dumps(hits, ensure_ascii=False, indent=1), encoding="utf-8")
    print("命中表", len(hits), "→", OUT)
    for h in hits[:20]:
        print("  %-46s %-5s %s" % (h["table"], h["key"], h["strings"][:2]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
