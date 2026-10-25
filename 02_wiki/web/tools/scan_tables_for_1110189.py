# -*- coding: utf-8 -*-
"""在经典服 cdata 全表里找 key 或值等于 1110189 的行（含 oversea 关键词表）。

输出 01_索引与产物/30_分析/1110189_全表检索.json
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

ROOT = pathlib.Path("E:/la拆包项目")
TREES = [
    ROOT / "01_索引与产物/41_还原树/pe/配置/script.py314.lc.npk/com/cdata",
    ROOT / "01_索引与产物/41_还原树/pe/配置_增量快照/script.py314.lc.npk/com/cdata",
    ROOT / "01_索引与产物/41_还原树/pe/配置/com/cdata",
]
OVERSEA = ROOT / "01_索引与产物/41_还原树/pe/配置/com/cdata/oversea"
OUT = ROOT / "01_索引与产物/30_分析/1110189_全表检索.json"
TARGET = "1110189"
OV_KW = ("skin", "weapon", "lottery", "shop", "activity", "gift", "exchange", "collection")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core.bindict_table import decode_table_rows, parse_legacy_chs_pool  # noqa: E402


def body(p: pathlib.Path):
    raw = p.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        return None
    n = struct.unpack_from("<I", raw, at + 2)[0]
    if n <= 0 or at + 6 + n > len(raw):
        return None
    return raw[at + 6: at + 6 + n]


def val(v):
    return v[1] if isinstance(v, tuple) and len(v) == 2 else v


def scan(tree: pathlib.Path, files, tag: str, rep: list) -> int:
    cnt = 0
    for p in files:
        b = body(p)
        if not b:
            continue
        chs = tree / (p.stem + "_chs.py")
        pool = []
        if chs.exists():
            try:
                pool = parse_legacy_chs_pool(chs.read_bytes())
            except Exception:  # noqa: BLE001
                pool = []
        try:
            rows, _ = decode_table_rows(b, pool, resolve_jumps=False, lenient=True)
        except Exception:  # noqa: BLE001
            continue
        for r in rows:
            v = {k: val(x) for k, x in (r.get("values") or {}).items()}
            if str(r.get("key")) == TARGET or any(str(x) == TARGET for x in v.values()):
                rep.append({"tree": tag, "table": p.stem, "key": r.get("key"),
                            "values": {k: x for k, x in v.items() if isinstance(x, (str, int, float))}})
                cnt += 1
    return cnt


def main() -> int:
    rep = []
    for tree in TREES:
        if not tree.is_dir():
            continue
        files = [p for p in sorted(tree.glob("*.py")) if "_chs" not in p.name]
        n = scan(tree, files, tree.name, rep)
        print(tree.name, "表", len(files), "命中", n)
    if OVERSEA.is_dir():
        files = [p for p in sorted(OVERSEA.glob("*.py"))
                 if "_chs" not in p.name and any(k in p.name for k in OV_KW)]
        n = scan(OVERSEA, files, "oversea", rep)
        print("oversea 关键词表", len(files), "命中", n)
    OUT.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print("总命中", len(rep), "→", OUT)
    for x in rep[:10]:
        print("  ", x["tree"], x["table"], x["key"], str(x["values"])[:120])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
