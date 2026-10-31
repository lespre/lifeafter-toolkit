# -*- coding: utf-8 -*-
"""3662 学院企划 / 3656 浮光花序：jump 组 + 选项池成员。"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

ROOT = pathlib.Path("E:/la拆包项目")
CD = ROOT / "01_索引与产物/41_还原树/pe/配置/com/cdata"
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
import toolkit_core.bindict_table as BT  # noqa: E402


def bb(stem: str):
    raw = (CD / f"{stem}.py").read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6:at + 6 + L]
    count = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * count:]
    c = CD / f"{stem}_chs.py"
    pool = BT.parse_legacy_chs_pool(c.read_bytes()) if c.is_file() else []
    return body, blob, pool


def grp(blob, n):
    g = BT._read_27_uleb_group(blob, n)
    return g["values"] if g else None


def names_map():
    """尽量凑一张 id→名字表：common_item / gift / fashion / vehicle。"""
    out = {}
    files = pathlib.Path(ROOT / "01_索引与产物/10_索引/items")
    if files.is_dir():
        for p in files.glob("*.json"):
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
            except Exception:                          # noqa: BLE001
                continue
            if isinstance(d, dict):
                for k, v in list(d.items())[:200000]:
                    if isinstance(v, str) and k.isdigit():
                        out.setdefault(int(k), v)
                    elif isinstance(v, dict) and isinstance(v.get("name"), str) and str(k).isdigit():
                        out.setdefault(int(k), v["name"])
    return out


def main() -> int:
    nm = names_map()
    print("名字索引 %d 条" % len(nm))

    print("\n=== 3656 浮光花序（super_fashion conf key 236）===")
    body, blob, pool = bb("super_fashion_lottery_conf_data")
    panel = grp(blob, 9)
    bag = grp(blob, 35)
    print("panel_show_item_ids jump:9 →", panel)
    print("fortune_bag_dct   jump:35 →", bag)
    if panel:
        print("  展示件名字：")
        for i in panel:
            print("    %-10s %s" % (i, nm.get(i, "?")))

    print("\n=== 3662 学院企划（multi_optional conf key 11）===")
    body2, blob2, pool2 = bb("multi_optional_lottery_conf_data")
    show = grp(blob2, 4)
    print("show_item_ids jump:4 →", show)
    if show:
        for i in show:
            print("    %-10s %s" % (i, nm.get(i, "?")))

    b3, blob3, pool3 = bb("multi_optional_lottery_option_data")
    idx = BT.parse_index(blob3)
    offs = sorted(o for _, o in idx)
    print("option_data 索引 %d 项 ｜ key=11 偏移 %s" % (len(idx), [o for k, o in idx if k == 11]))
    tgt = [o for k, o in idx if k == 11]
    if tgt:
        off = tgt[0]
        nxt = next((o for o in offs if o > off), len(blob3))
        print("  行区间 [%d, %d)" % (off, nxt))
        groups = []
        i = off
        while i < nxt:
            g = BT._read_27_uleb_group(blob3, i)
            if g:
                groups.append(g["values"])
                i = g["end"]
            else:
                i += 1
        print("  组 %d 个：%s" % (len(groups), groups[:8]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
