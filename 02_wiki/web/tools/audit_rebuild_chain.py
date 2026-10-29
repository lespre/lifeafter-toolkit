# -*- coding: utf-8 -*-
"""体检：board_builders 注册表 → 各板块能否在别的机器重建（脚本在不在、输入是什么、有无硬编码）。"""
from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path("E:/la拆包项目")
_reg_raw = json.loads((ROOT / "02_wiki/web/data/board_builders.json").read_text(encoding="utf-8"))
REG = _reg_raw.get("boards") if isinstance(_reg_raw, dict) else _reg_raw

ABS = re.compile(r"""["']([A-Za-z]:[/\\][^"'\n]{3,80})["']""")
SNAP = re.compile(r"(test-documents-[0-9a-f]{8}|snapshot_id\s*=\s*[\"'][^\"']+)")


def main() -> int:
    missing_script, no_builder, with_abs, with_snap = [], [], [], []
    for b in REG:
        bid = b.get("board_id")
        builder = b.get("builder")
        if not builder:
            no_builder.append(bid)
            continue
        p = ROOT / builder
        if not p.is_file():
            missing_script.append((bid, builder))
            continue
        txt = p.read_text(encoding="utf-8", errors="ignore")
        hits = [h for h in ABS.findall(txt) if "la拆包项目" not in h]
        if hits:
            with_abs.append((bid, sorted(set(hits))[:3]))
        if SNAP.search(txt):
            with_snap.append(bid)

    print("== 注册表", len(REG), "个板块")
    print("  无 builder（手工/产物冻结）:", len(no_builder), no_builder)
    print("  脚本缺失:", len(missing_script))
    for x in missing_script:
        print("     -", x[0], x[1])
    print("  含绝对路径的 builder:", len(with_abs))
    for bid, hits in with_abs:
        print("     -", bid, hits)
    print("  含快照 ID 的 builder:", len(with_snap), with_snap)

    # 未被注册表覆盖的板块
    man = json.loads((ROOT / "02_wiki/web/data/manifest.json").read_text(encoding="utf-8"))
    boards = {x["board"] for x in (man.get("boards") or man)}
    registered = {b.get("board_id") for b in REG}
    print("== manifest 有、注册表没有:", sorted(boards - registered))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
