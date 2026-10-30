# -*- coding: utf-8 -*-
"""把热更里新增的时装行解出中文名，并看武器皮肤相关表有没有新增皮肤。"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core.bindict_table import decode_table_rows, parse_legacy_chs_pool  # noqa: E402

NEW_DIR = sorted((ROOT / "01_索引与产物/30_分析/pc_hotfix_tables").glob("*"))[-1]
OLD_DIR = ROOT / "01_索引与产物/41_还原树/pe/配置/com/cdata"


def decode(p: pathlib.Path, chs: pathlib.Path | None, resolve=False):
    raw = p.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        return None
    n = struct.unpack_from("<I", raw, at + 2)[0]
    pool = []
    if chs and chs.is_file():
        try:
            pool = parse_legacy_chs_pool(chs.read_bytes())
        except Exception:                                # noqa: BLE001
            pool = []
    rows, _ = decode_table_rows(raw[at + 6:at + 6 + n], pool, resolve_jumps=resolve, lenient=True)
    return rows


def val(v):
    return v[1] if isinstance(v, tuple) and len(v) == 2 else v


def main() -> int:
    # ---- 时装新增行 ----
    rows_new = decode(NEW_DIR / "fashion_data.py", NEW_DIR / "fashion_data_chs.py")
    rows_old = decode(OLD_DIR / "fashion_data.py", OLD_DIR / "fashion_data_chs.py")
    ko = {r["key"] for r in (rows_old or []) if isinstance(r.get("key"), int)}
    new_rows = [r for r in (rows_new or []) if isinstance(r.get("key"), int) and r["key"] not in ko]
    print("时装新增行", len(new_rows))
    seen = []
    for r in new_rows:
        v = {k: val(x) for k, x in (r.get("values") or {}).items()}
        name = v.get("name")
        if name and str(name) not in seen:
            seen.append(str(name))
            print("   %-6s %-24s model=%s part=%s" % (r["key"], str(name)[:24], v.get("model_id"), v.get("part_type")))
    print("去重新增名字", len(seen))

    # ---- 武器皮肤表 ----
    for t in ("weapon_skin_data.py",):
        np_, op = NEW_DIR / t, OLD_DIR / t
        print("%-24s 热更有:%s 旧有:%s" % (t, np_.is_file(), op.is_file()))
        if np_.is_file() and op.is_file():
            a = decode(np_, NEW_DIR / (t[:-3] + "_chs.py"))
            b = decode(op, OLD_DIR / (t[:-3] + "_chs.py"))
            ka = {r["key"] for r in (a or []) if isinstance(r.get("key"), int)}
            kb = {r["key"] for r in (b or []) if isinstance(r.get("key"), int)}
            print("   行 %d→%d ｜ 新增 %d ｜ 消失 %d" % (len(kb), len(ka), len(ka - kb), len(kb - ka)))
            if ka - kb:
                print("   新增皮肤键", sorted(ka - kb)[:10])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
