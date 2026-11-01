# -*- coding: utf-8 -*-
"""快速看表：打印指定表的前几行字段名与值（判断哪个字段是池号/成员）。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, r"E:\la拆包项目\02_wiki\web\tools")
import rebuild_lottery_periods as R  # noqa: E402


def show(name: str, n: int = 3) -> None:
    p = R.TREE / f"{name}.py"
    if not p.exists():
        print(f"## {name}: 不存在")
        return
    chs = p.with_name(p.stem + "_chs.py")
    t = R.Table(p, chs if chs.exists() else None)
    print(f"## {name}  rows={len(t.rows)} map_keys={len(t.map_start)} size={p.stat().st_size}")
    for row in list(t.by_key.values())[:n]:
        vals = row["values"]
        brief = {}
        for k, v in vals.items():
            if isinstance(v, str) and v.startswith("jump:"):
                g = t.jump_values(v)
                brief[k] = f"{v} → {g[:6]}"
            else:
                brief[k] = v
        print(f"  key={row['key']}: {brief}")
    if t.map_start:
        ks = sorted(t.map_start.items())[:2]
        for k, off in ks:
            try:
                slots = R.parse_map_row(t, off)
            except Exception as exc:
                print(f"  map key={k}: 解不出 ({exc})")
                continue
            print(f"  map key={k}: slots={slots[:6]}")
    print()


if __name__ == "__main__":
    for nm in sys.argv[1:]:
        show(nm)
