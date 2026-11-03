# -*- coding: utf-8 -*-
"""检查已发布板块对未上架板块的依赖（代码 + 数据）。

代码依赖：已发布板块的 builder 脚本里出现未上架板块的 id / 读它的 json
数据依赖：已发布板块条目字段里出现未上架板块 id（如 related_board）
"""
from __future__ import annotations

import json
import re
from pathlib import Path

PROJ = Path(r"E:\la拆包项目")
WEB = PROJ / "02_wiki/web"
BOARDS = WEB / "data/boards"
TOOLS = WEB / "tools"

CANDIDATES = [
    "weapon_skin_static_candidates_v01", "nucleus_cards_classic", "chip_item_catalog",
    "vehicle_garage_names", "skin_behavior_preview", "weapon_skin_structure_v01",
    "weapon_skin_active", "shop_static_candidates", "fashion_face", "vehicle_catalog",
    "fashion_kaijia", "nucleus_item_catalog", "nucleus_entry_slots",
    "common_item_text_sources", "fashion_wardrobe_slots", "fashion_face_slots",
    "fashion_glow_slots", "fashion_projection_slots",
]


def main() -> int:
    pol = json.loads((WEB / "data/publication_policy.json").read_text(encoding="utf-8"))["boards"]
    reg = {}
    rp = WEB / "data/board_builders.json"
    if rp.exists():
        for b in json.loads(rp.read_text(encoding="utf-8")).get("boards") or []:
            reg[b.get("board_id")] = str(b.get("builder") or "")

    pub = [bid for bid, m in pol.items() if (m.get("publication_status") == "published")]

    code_hits: dict[str, set[str]] = {}
    for bid in pub:
        script = reg.get(bid) or ""
        names = {script.split("/")[-1]} if script else set()
        # 该板可能的其他 builder
        for p in TOOLS.glob(f"*{bid}*.py"):
            names.add(p.name)
        for nm in [n for n in names if n.endswith(".py")]:
            sp = TOOLS / nm
            if not sp.is_file():
                continue
            txt = sp.read_text(encoding="utf-8", errors="ignore")
            for cand in CANDIDATES:
                if cand in txt:
                    code_hits.setdefault(cand, set()).add(f"{bid} ({nm})")

    data_hits: dict[str, set[str]] = {}
    for bid in pub:
        p = BOARDS / f"{bid}.json"
        if not p.exists():
            continue
        txt = p.read_text(encoding="utf-8", errors="ignore")
        for cand in CANDIDATES:
            if f'"{cand}"' in txt:
                data_hits.setdefault(cand, set()).add(bid)

    print("== 代码依赖")
    if not code_hits:
        print("  无")
    for cand, users in sorted(code_hits.items()):
        print(f"  {cand:36s} ← {', '.join(sorted(users))[:120]}")
    print("== 数据依赖")
    if not data_hits:
        print("  无")
    for cand, users in sorted(data_hits.items()):
        print(f"  {cand:36s} ← {', '.join(sorted(users))[:120]}")
    print("== 无依赖（可安全删）")
    safety = [c for c in CANDIDATES if c not in code_hits and c not in data_hits]
    print("  " + "、".join(safety))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
