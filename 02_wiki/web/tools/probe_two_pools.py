# -*- coding: utf-8 -*-
"""解两个活动的奖池配置：3662 学院企划（多时装抽奖）/ 3656 浮光花序（幻彩典藏 2）。"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

ROOT = pathlib.Path("E:/la拆包项目")
CD = ROOT / "01_索引与产物/41_还原树/pe/配置/com/cdata"
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
import toolkit_core.bindict_table as BT  # noqa: E402


def load(stem: str):
    p = CD / f"{stem}.py"
    c = CD / f"{stem}_chs.py"
    raw = p.read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6:at + 6 + L]
    count = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * count:]
    pool = BT.parse_legacy_chs_pool(c.read_bytes()) if c.is_file() else []
    rows, unbound = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)
    return rows, unbound, body, blob, pool


def flat(v):
    return v[1] if isinstance(v, tuple) else v


def show(label, key, stem):
    rows, unbound, body, blob, pool = load(stem)
    print(f"\n== {label} ｜ {stem} ｜ 行 {len(rows)} ｜ 未绑定 {len(unbound)}")
    hit = [r for r in rows if str(r.get("key")) == str(key)]
    if not hit:
        print("   未找到 key", key)
        return None, blob, body, pool
    d = {k: flat(v) for k, v in (hit[0].get("values") or {}).items()}
    for k in ("lottery_id", "lottery_group_id", "option_pool_id", "ensure_cnt",
              "ui_group_id", "rule_id", "show_item_ids", "panel_show_item_ids",
              "left_item_desc", "left_item_id", "right_item_id", "right_bag_item_id",
              "task_id", "share_reward_id", "fortune_bag_dct"):
        if k in d:
            print("   %-20s %r" % (k, d[k]))
    return d, blob, body, pool


if __name__ == "__main__":
    show("3662 学院企划 · MultiOptional", 11, "multi_optional_lottery_conf_data")
    show("3656 浮光花序 · SuperFashion", 236, "super_fashion_lottery_conf_data")
