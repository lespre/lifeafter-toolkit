# -*- coding: utf-8 -*-
"""HPGF 条目表：先看统计结构（列熵、周期性、可能的 XOR 常量）。"""
from __future__ import annotations

import collections
import math
import pathlib
import struct
import sys

sys.path.insert(0, r"E:/la拆包项目/01_工具/工具库/01_解码定位复原/解包与扫描")
from gpk_reader import Gpk  # noqa: E402

P = r"E:/mrzh/res/ui_01.gpk"
SIZE = pathlib.Path(P).stat().st_size


def entropy(vals) -> float:
    n = len(vals)
    c = collections.Counter(vals)
    return -sum((v / n) * math.log2(v / n) for v in c.values())


def main() -> int:
    g = Gpk(P)
    t = g.table
    print("表长", len(t), "记录", g.count, "SIZE", SIZE)

    # 1) 每字节位置的熵（若某列低熵，说明是明文结构列）
    per = []
    for i in range(32):
        col = t[i::32]
        per.append((entropy(col), i, len(set(col))))
    per.sort()
    print("低熵列（熵, 位置, 不同值数）：")
    for e, i, u in per[:8]:
        print("   pos%-2d  H=%.2f  uniq=%d" % (i, e, u))

    # 2) 记录首 4 字节（疑似 off）分布：是否单调、范围
    offs = [struct.unpack_from("<I", t, i * 32)[0] for i in range(min(2000, g.count))]
    print("off 前5:", [hex(x) for x in offs[:5]])
    inc = sum(1 for a, b in zip(offs, offs[1:]) if b > a)
    print("off 递增占比 %.0f%%" % (100 * inc / max(1, len(offs) - 1)))

    # 3) 周期性：同位置字节的自相关（找 XOR 密钥周期）
    for period in (16, 32, 64, 128, 256, 1024):
        same = sum(1 for i in range(0, min(len(t) - period, 65536)) if t[i] == t[i + period])
        print("周期 %-5d 相同字节占比 %.3f" % (period, same / min(len(t) - period, 65536)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
