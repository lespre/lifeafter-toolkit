# -*- coding: utf-8 -*-
"""经典服 special_hurt_params_data：按数值特征推定 min/max 两列，导出 CSV。

推定依据（逐条）：
  slot_2 与 slot_4 在 693 行里有 682 行满足 slot2 > slot4，且分布符合「上限/下限」形态：
    slot2 ∈ {3.0(359), 1.7(184), 1.5(55), 2.0(30), 1.1(27)}
    slot4 ∈ {0.4(359), 0.5(216), 1.0(57), 0.9(27), 0.8(19)}
  slot6 取值 -0.80 ~ -0.35，与简单生存服 p2m_a_class_min_hurt_additional_rate = -0.75 同量纲。
其余槽位语义未定，不改名。
"""
from __future__ import annotations

import csv
import pathlib
import struct
import sys
from collections import Counter

sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
from toolkit_core import bindict_table as BT  # noqa: E402

CD = pathlib.Path(r"E:/la拆包项目/01_索引与产物/41_还原树/pe_20261020/com/cdata")
OUT = pathlib.Path(r"E:/la拆包项目/01_索引与产物/30_分析/伤害系统逆向")


def num(r, i):
    x = r["values"].get("<slot_%d>" % i)
    x = x[1] if isinstance(x, tuple) else x
    try:
        return float(x)
    except Exception:
        return None


def main() -> int:
    b = (CD / "special_hurt_params_data.py").read_bytes()
    at = b.find(b"x{")
    L = struct.unpack_from("<I", b, at + 2)[0]
    rows, _ = BT.decode_table_rows(b[at + 6: at + 6 + L], {}, resolve_jumps=False)

    recs = []
    for r in rows:
        mn, mx = num(r, 4), num(r, 2)
        recs.append({
            "key": r["key"],
            "min_推定": mn,
            "max_推定": mx,
            "跨度": round(mx - mn, 3) if None not in (mn, mx) else None,
            "slot6_负值": num(r, 6),
            "slot0": num(r, 0),
        })
    recs.sort(key=lambda x: (x["max_推定"] is None, x["max_推定"] or 0, x["min_推定"] or 0))

    dest = OUT / "classic_hurt_params_推定.csv"
    with dest.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(recs[0].keys()))
        w.writeheader()
        w.writerows(recs)

    pairs = Counter((x["min_推定"], x["max_推定"]) for x in recs)
    print("行", len(recs), "→", dest)
    print("最常见 (min,max) 组合：")
    for (mn, mx), n in pairs.most_common(8):
        print("  %.2f ~ %.2f  %d 行" % (mn, mx, n))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
