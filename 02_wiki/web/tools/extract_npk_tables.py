# -*- coding: utf-8 -*-
"""通用：从任一 script npk 解 com\\cdata 表并与指定树逐字节比对。

  python extract_npk_tables.py --npk <npk> [--label pe_20261030] [--tree <cdata 目录>]
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"))
from toolkit_core import hotfix_rows as HR          # noqa: E402
from la_unpack_core import npk_decode_entry         # noqa: E402

DEFAULT_TREE = ROOT / "01_索引与产物/41_还原树/pe/配置/com/cdata"
OUT = ROOT / "01_索引与产物/30_分析"


class _E:
    __slots__ = ("packed",)

    def __init__(self, p: int) -> None:
        self.packed = p


def load_names() -> dict[str, str]:
    con = sqlite3.connect(str(ROOT / "01_索引与产物/10_索引/热更检测/names_join.sqlite3"))
    out = {}
    for fid, name in con.execute(
            "select fid,name from nm where name like 'com\\cdata\\%' and name not like '%oversea%'"):
        n = str(name).replace("\\", "/")
        if n.count("/") == 2 and n.endswith(".py"):
            out[str(fid).upper()] = n.rsplit("/", 1)[-1]
    con.close()
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--npk", required=True)
    ap.add_argument("--label", default="")
    ap.add_argument("--tree", default=str(DEFAULT_TREE))
    a = ap.parse_args()

    npk = pathlib.Path(a.npk)
    tree = pathlib.Path(a.tree)
    label = a.label or datetime.datetime.now().strftime("%Y%m%d_%H%M")
    dst_dir = OUT / f"hotfix_tables_{label}"
    names = load_names()
    blob = npk.read_bytes()
    entries = HR._entries(npk)
    print("npk %s ｜ %.0f MB ｜ 条目 %d ｜ 表名 %d" % (npk.name, npk.stat().st_size / 1e6, len(entries), len(names)))

    stats = {"identical": 0, "changed": 0, "new": 0, "fail": 0, "unnamed": 0}
    changed, new = [], []
    for e in entries:
        fn = names.get(str(e.get("fid", "")).upper())
        if not fn:
            stats["unnamed"] += 1
            continue
        raw = blob[e["offset"]:e["offset"] + e["packed"]]
        try:
            data = npk_decode_entry(raw, e["decoded"], e["flag"], entry=_E(e["packed"]))
        except Exception:                                # noqa: BLE001
            stats["fail"] += 1
            continue
        cur = tree / fn
        if not cur.is_file():
            stats["new"] += 1
            new.append(fn)
            dst_dir.mkdir(parents=True, exist_ok=True)
            (dst_dir / fn).write_bytes(data)
        elif data == cur.read_bytes():
            stats["identical"] += 1
        else:
            stats["changed"] += 1
            changed.append(fn)
            dst_dir.mkdir(parents=True, exist_ok=True)
            (dst_dir / fn).write_bytes(data)

    rep = {"at": label, "npk": str(npk), "npk_size": npk.stat().st_size, "stats": stats,
           "changed": changed, "new": new}
    (OUT / f"hotfix_diff_{label}.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print("相同 %d ｜ 变更 %d ｜ 新增 %d ｜ 解码失败 %d ｜ 无名字 %d"
          % (stats["identical"], stats["changed"], stats["new"], stats["fail"], stats["unnamed"]))
    if changed:
        print("变更示例", changed[:8])
    if new:
        print("新增示例", new[:8])
    print("落盘", dst_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
