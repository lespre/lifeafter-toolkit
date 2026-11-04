# -*- coding: utf-8 -*-
"""摸 weapon_skin_effect_show_data 的真实结构：0x36 映射？行内组？名字在哪。"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

PROJ = Path(r"E:\la拆包项目")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
import rebuild_lottery_periods as R  # noqa: E402
from toolkit_core.bindict_table import parse_index, parse_legacy_chs_pool  # noqa: E402

CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
NAME = "weapon_skin_effect_show_data"


def main() -> int:
    raw = (CD / f"{NAME}.py").read_bytes()
    at = raw.find(b"x{")
    n = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + n]
    pool = parse_legacy_chs_pool((CD / f"{NAME}_chs.py").read_bytes())
    print("body", len(body), "| chs", len(pool))
    hits = [i for i, s in enumerate(pool) if "一击倾心" in s or "浪漫谢幕" in s or "辉光绽放" in s]
    print("池中命中索引", hits[:6], [pool[i] for i in hits[:3]])

    try:
        idx = parse_index(body)
        print("0x76 索引键", len(idx), list(idx)[:8])
    except Exception as exc:
        idx = {}
        print("parse_index 失败", exc)

    # 直接扫 0x27 组，看有没有含 pool 索引的组（kind 0x05 字符串组）
    groups = []
    i = 0
    while i < len(body) - 3:
        g = R.read_27(body, i)
        if g:
            groups.append((i, g["kind"], g["values"][:6]))
            i = g["end"]
        else:
            i += 1
    print("0x27 组数", len(groups))
    str_like = [g for g in groups if g[1] == 0x05]
    print("kind=0x05 字符串组", len(str_like), str_like[:3])
    print("组样例", groups[:5])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
