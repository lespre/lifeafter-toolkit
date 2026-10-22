# -*- coding: utf-8 -*-
"""对比「经典服 / 简单生存服」的伤害加成上下限参数。"""
from __future__ import annotations

import pathlib
import struct
import sys

sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
from toolkit_core import bindict_table as BT  # noqa: E402

CD = pathlib.Path(r"E:/la拆包项目/01_索引与产物/41_还原树/pe_20261020/com/cdata")
CAND = [
    ("base（经典服）", CD / "special_hurt_params_data.py", CD / "special_hurt_params_data_chs.py"),
    ("kj1（简单生存）", CD / "oversea/special_hurt_params_data_auto_oversea_data_kj1.py",
     CD / "oversea/special_hurt_params_data_auto_oversea_data_kj1_chs.py"),
    ("kjxq", CD / "oversea/special_hurt_params_data_auto_oversea_data_kjxq.py",
     CD / "oversea/special_hurt_params_data_auto_oversea_data_kjxq_chs.py"),
]


def load(p, chs):
    b = pathlib.Path(p).read_bytes()
    at = b.find(b"x{")
    if at < 0:
        return None
    L = struct.unpack_from("<I", b, at + 2)[0]
    pool = {}
    if pathlib.Path(chs).is_file():
        try:
            pool = BT.parse_legacy_chs_pool(pathlib.Path(chs).read_bytes())
        except Exception:
            pool = {}
    try:
        rows, _ = BT.decode_table_rows(b[at + 6: at + 6 + L], pool, resolve_jumps=False)
    except Exception as e:
        return ("ERR", str(e)[:40])
    return rows


def slim(rows):
    out = {}
    for r in rows:
        def g(k):
            v = r["values"].get(k)
            return (v[1] if isinstance(v, tuple) else v) if v else None
        sid = g("scene_id")
        if sid is None:
            continue
        try:
            sid = int(sid)
        except Exception:
            continue
        out.setdefault(sid, set()).add((g("min_hurt_additional_rate"), g("max_hurt_additional_rate")))
    return out


def main() -> int:
    data = {}
    for label, p, chs in CAND:
        if not pathlib.Path(p).is_file():
            print(label, "缺文件")
            continue
        rows = load(p, chs)
        if isinstance(rows, tuple):
            print(label, rows)
            continue
        if rows is None:
            print(label, "无 x{")
            continue
        s = slim(rows)
        data[label] = s
        print("%-14s 行 %-5d 场景 %-4d" % (label, len(rows), len(s)))

    a = data.get("base（经典服）")
    b = data.get("kj1（简单生存）")
    if a and b:
        same = [k for k in a if k in b and a[k] == b[k]]
        diff = [k for k in a if k in b and a[k] != b[k]]
        only_a = sorted(set(a) - set(b))
        only_b = sorted(set(b) - set(a))
        print("\n共有场景", len(same) + len(diff), "｜完全相同", len(same), "｜不同", len(diff))
        print("只在经典服", len(only_a), only_a[:12])
        print("只在简单生存", len(only_b), only_b[:12])
        for k in diff[:10]:
            print("  差异 scene %s  经典 %s  简单 %s" % (k, sorted(a[k]), sorted(b[k])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
