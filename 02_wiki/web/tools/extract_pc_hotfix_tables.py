# -*- coding: utf-8 -*-
"""从 PC 热更 npk 里只解 com\\cdata 表，与现有 PE 表逐字节比对，列出变更。

产出：
  01_索引与产物/30_分析/pc_hotfix_tables/<stamp>/...   有变化的表（保留相对路径）
  01_索引与产物/30_分析/pc_hotfix_diff_<stamp>.json     差异清单
"""
from __future__ import annotations

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

TREE = ROOT / "01_索引与产物/41_还原树/pe/配置/com/cdata"
OUT = ROOT / "01_索引与产物/30_分析"


def latest_pc_npk() -> pathlib.Path:
    cands = sorted((ROOT / "01_索引与产物/源包/pc_hotfix").glob("*/script.py314.lc.npk"))
    if not cands:
        raise SystemExit("没有抓到 PC 热更包，先跑 capture_pc_hotfix.py --copy")
    return cands[-1]


def load_names() -> dict[str, str]:
    con = sqlite3.connect(str(ROOT / "01_索引与产物/10_索引/热更检测/names_join.sqlite3"))
    out = {}
    for fid, name in con.execute(
            "select fid,name from nm where name like 'com\\cdata\\%' and name not like '%oversea%'"):
        n = str(name).replace("\\", "/")
        if n.count("/") == 2 and n.endswith(".py"):      # com/cdata/xxx.py
            out[str(fid).upper()] = n.rsplit("/", 1)[-1]
    con.close()
    return out


class _E:
    __slots__ = ("packed",)

    def __init__(self, p: int) -> None:
        self.packed = p


def main() -> int:
    npk = latest_pc_npk()
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    dst_dir = OUT / "pc_hotfix_tables" / stamp
    print("热更包", npk, "%.0f MB" % (npk.stat().st_size / 1e6))

    names = load_names()
    print("名字表里 com/cdata 表名", len(names))

    blob = npk.read_bytes()
    entries = HR._entries(npk)
    print("npk 条目", len(entries))

    stats = {"identical": 0, "changed": 0, "new": 0, "decode_fail": 0, "not_in_names": 0}
    changed, new, fails = [], [], []
    for e in entries:
        fid = str(e.get("fid", "")).upper()
        fn = names.get(fid)
        if not fn:
            stats["not_in_names"] += 1
            continue
        raw = blob[e["offset"]:e["offset"] + e["packed"]]
        try:
            data = npk_decode_entry(raw, e["decoded"], e["flag"], entry=_E(e["packed"]))
        except Exception as ex:                          # noqa: BLE001
            stats["decode_fail"] += 1
            if len(fails) < 10:
                fails.append((fn, str(ex)[:60]))
            continue
        cur = TREE / fn
        if not cur.is_file():
            stats["new"] += 1
            new.append(fn)
            (dst_dir).mkdir(parents=True, exist_ok=True)
            (dst_dir / fn).write_bytes(data)
            continue
        if data == cur.read_bytes():
            stats["identical"] += 1
        else:
            stats["changed"] += 1
            changed.append(fn)
            (dst_dir).mkdir(parents=True, exist_ok=True)
            (dst_dir / fn).write_bytes(data)

    report = {"at": stamp, "npk": str(npk), "stats": stats,
              "changed": changed[:500], "new": new[:500], "decode_fail_samples": fails}
    (OUT / f"pc_hotfix_diff_{stamp}.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    print("相同 %d ｜ 变更 %d ｜ 新增 %d ｜ 解码失败 %d ｜ 无名字 %d"
          % (stats["identical"], stats["changed"], stats["new"], stats["decode_fail"], stats["not_in_names"]))
    if changed:
        print("变更示例", changed[:10])
    if new:
        print("新增示例", new[:10])
    print("变更表落盘", dst_dir if (changed or new) else "（无）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
