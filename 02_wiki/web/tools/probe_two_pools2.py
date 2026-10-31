# -*- coding: utf-8 -*-
"""解 3662 学院企划 / 3656 浮光花序 的 jump 组与选项池。"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

ROOT = pathlib.Path("E:/la拆包项目")
CD = ROOT / "01_索引与产物/41_还原树/pe/配置/com/cdata"
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
import toolkit_core.bindict_table as BT  # noqa: E402


def body_blob(stem: str):
    raw = (CD / f"{stem}.py").read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6:at + 6 + L]
    count = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * count:]
    c = CD / f"{stem}_chs.py"
    pool = BT.parse_legacy_chs_pool(c.read_bytes()) if c.is_file() else []
    return body, blob, pool


def jump(blob, n, pool, table):
    for base in (0, BT.jump_base(table)):
        try:
            r = BT.resolve_jump_target(blob, n + base, pool)
        except Exception:                              # noqa: BLE001
            r = None
        if r and r.get("values"):
            return base, r
    return None, None


def main() -> int:
    print("=== 3662 学院企划 ===")
    body, blob, pool = body_blob("multi_optional_lottery_conf_data")
    base, r = jump(blob, 4, pool, "multi_optional_lottery_conf_data")
    print("show_item_ids jump:4 → base %s │ %s" % (base, r))

    body2, blob2, pool2 = body_blob("multi_optional_lottery_option_data")
    idx = BT.parse_index(blob2)
    print("option_data 索引 %d 项，前 6：%s" % (len(idx), idx[:6]))
    hit = [(k, off) for k, off in idx if k == 11]
    print("key=11 →", hit)
    if hit:
        off = hit[0][1]
        nxt = next((k for k, o in idx if o > off), None)
        end = nxt if isinstance(nxt, int) else len(blob2)
        print("  映射行 @%d，区间到 %s" % (off, end))
        groups = []
        i = off
        while i < min(end, len(blob2)):
            g = BT._read_27_uleb_group(blob2, i)
            if g:
                groups.append(g["values"])
                i = g["end"]
            else:
                i += 1
        print("  区间内 0x27 组 %d 个：%s" % (len(groups), groups[:6]))

    print("\n=== 3656 浮光花序 ===")
    body3, blob3, pool3 = body_blob("super_fashion_lottery_conf_data")
    for n, lab in ((9, "panel_show_item_ids"), (35, "fortune_bag_dct")):
        base, r = jump(blob3, n, pool3, "super_fashion_lottery_conf_data")
        print("%s jump:%d → base %s │ %s" % (lab, n, base, r))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
