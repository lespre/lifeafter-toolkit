# -*- coding: utf-8 -*-
"""对比热更表与现有 PE 表：行数 / 行键差异（先看 fashion_data 与武器皮肤表）。"""
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


def decode(p: pathlib.Path):
    raw = p.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        return None
    n = struct.unpack_from("<I", raw, at + 2)[0]
    rows, _ = decode_table_rows(raw[at + 6:at + 6 + n], [], resolve_jumps=False, lenient=True)
    return rows


def main() -> int:
    for name in ("fashion_data.py", "weapon_skin_effect_show_data.py",
                 "nucleus_data.py", "space_data_yk.py"):
        np_, op = NEW_DIR / name, OLD_DIR / name
        if not np_.is_file() or not op.is_file():
            print("%-36s 缺文件（新:%s 旧:%s）" % (name, np_.is_file(), op.is_file()))
            continue
        rn, ro = decode(np_), decode(op)
        if rn is None or ro is None:
            print("%-36s 解不出（x{ 缺失）" % name)
            continue
        kn = {r["key"] for r in rn if isinstance(r.get("key"), int)}
        ko = {r["key"] for r in ro if isinstance(r.get("key"), int)}
        print("%-36s 行 %d→%d ｜ 新增键 %d ｜ 消失 %d ｜ 同为 %d"
              % (name, len(ro), len(rn), len(kn - ko), len(ko - kn), len(kn & ko)))
        if kn - ko:
            print("    新增键示例", sorted(kn - ko)[:8])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
