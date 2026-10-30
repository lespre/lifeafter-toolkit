# -*- coding: utf-8 -*-
"""把 PC 热更里新增的时装行解成结构化 JSON（含 icons 字段），供补图与建卡。"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core.bindict_table import decode_table_rows, parse_legacy_chs_pool  # noqa: E402

NEW = sorted((ROOT / "01_索引与产物/30_分析/pc_hotfix_tables").glob("*"))[-1]
OLD = ROOT / "01_索引与产物/41_还原树/pe/配置/com/cdata"
OUT = ROOT / "01_索引与产物/30_分析/pc_hotfix_new_fashion.json"


def dec(d: pathlib.Path, name: str, resolve: bool = True):
    p = d / name
    raw = p.read_bytes()
    at = raw.find(b"x{")
    n = struct.unpack_from("<I", raw, at + 2)[0]
    chs = d / (name[:-3] + "_chs.py")
    pool = parse_legacy_chs_pool(chs.read_bytes()) if chs.is_file() else []
    rows, _ = decode_table_rows(raw[at + 6:at + 6 + n], pool, resolve_jumps=resolve, lenient=True)
    return rows


def val(v):
    return v[1] if isinstance(v, tuple) and len(v) == 2 else v


def main() -> int:
    new_rows = dec(NEW, "fashion_data.py")
    old_rows = dec(OLD, "fashion_data.py")
    ko = {r["key"] for r in old_rows if isinstance(r.get("key"), int)}
    out = []
    for r in new_rows:
        if not isinstance(r.get("key"), int) or r["key"] in ko:
            continue
        v = {k: val(x) for k, x in (r.get("values") or {}).items()}
        out.append({"row_key": r["key"], **v})
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("新增行", len(out), "→", OUT)
    print("字段样例", list(out[0])[:12] if out else [])
    print("首行", json.dumps(out[0], ensure_ascii=False)[:400] if out else "")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
