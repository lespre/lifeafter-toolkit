# -*- coding: utf-8 -*-
"""四个板块的活树表盘点：行数 + 字段名，判断能否从 PE 树重建。"""
from __future__ import annotations

import sys
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
sys.path.insert(0, str(WEB / "tools"))
import rebuild_lottery_periods as R  # noqa: E402

PATTERNS = {
    "talent": ["new_talent_data", "talent_data", "battle_prof_talent_ids"],
    "illustration": ["illustration_collect"],
    "avatar": ["dynamic_avatar_conf_data", "avatar_frame", "namecard"],
    "gene": ["gene_node", "gene_break_through_data_1"],
}


def probe(name: str) -> None:
    p = R.TREE / f"{name}.py"
    if not p.is_file():
        print(f"  {name}: 无表")
        return
    try:
        t = R._opt_table(p, R.TREE / f"{name}_chs.py")
        rows = t.by_key
        first = next(iter(rows.values()))["values"] if rows else {}
        print(f"  {name}: {len(rows)} 行 | 字段 {list(first)[:14]}")
    except Exception as exc:
        print(f"  {name}: 解析失败 {type(exc).__name__} {exc}"[:160])


def main() -> int:
    for grp, names in PATTERNS.items():
        print("==", grp)
        for n in names:
            probe(n)
    # 通配扫 illustration / gene
    allpy = sorted(p.stem for p in R.TREE.glob("*.py") if not p.stem.endswith("_chs"))
    print("\nillustration 相关:", [s for s in allpy if "illustration" in s][:12])
    print("gene_node 相关:", [s for s in allpy if s.startswith("gene_node")][:8])
    print("avatar 相关:", [s for s in allpy if "avatar" in s][:12])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
