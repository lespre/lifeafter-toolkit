# -*- coding: utf-8 -*-
"""反推 weapon_skin_effect_show_data 行布局：
在 CHS 池里取「辉光绽放/咏叹终章/光影游数…」的索引，然后在数据文件里找
这些索引连续出现的字节序列，用位置差反推字段宽度与行宽。
"""
from __future__ import annotations

import json
import sys

sys.path.insert(0, "E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
sys.path.insert(0, "E:/la拆包项目/02_wiki/web/tools")
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402
from _src import cdata_dir  # noqa: E402

CD = cdata_dir()
NAME = "weapon_skin_effect_show_data"
WANT = ["辉光绽放", "咏叹终章", "光影游数", "辉光流转", "咏叹之音", "影辉锁定", "决斗时刻", "光影咏叹"]


def main() -> int:
    pool = parse_legacy_chs_pool((CD / (NAME + "_chs.py")).read_bytes())
    print("池", len(pool), type(pool).__name__)
    idx = {}
    for i, v in enumerate(pool):
        if isinstance(v, str) and v in WANT:
            idx[v] = i
    print("目标索引", json.dumps(idx, ensure_ascii=False))

    raw = (CD / (NAME + ".py")).read_bytes()
    print("文件", len(raw))

    # 在文件里找 u16 LE 索引出现位置
    for w, i in idx.items():
        b = i.to_bytes(2, "little")
        pos = [p for p in range(len(raw) - 1) if raw[p:p + 2] == b]
        print("%-6s idx=%-4d u16出现 %2d 次 前5位置 %s" % (w, i, len(pos), pos[:5]))

    # 找 4 连号（连续 8 个索引是否成块出现）
    seq = [idx[w] for w in WANT if w in idx]
    print("目标序列", seq)
    best = None
    for start in range(len(raw) - 2 * len(seq)):
        window = [int.from_bytes(raw[start + 2 * k: start + 2 * k + 2], "little") for k in range(len(seq))]
        inter = len(set(window) & set(seq))
        if best is None or inter > best[0]:
            best = (inter, start, window)
    print("最佳窗口", best)

    # 打印该窗口附近的原始字节
    if best:
        s = max(0, best[1] - 24)
        print("上下文", best[1], raw[s:best[1] + 2 * len(seq) + 24].hex(" "))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
