# -*- coding: utf-8 -*-
"""用 player_appear_data 补齐时装板缺失的部位（如 不湮之花-头饰）。

背景：人物时装板只读 fashion_data；部分套装的头饰/衣服只登记在 player_appear_data，
导致同套装只剩「衣服」一张卡。这里按 model_id + 名字前缀对齐，把缺的部位补进 part_bucket。
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from collections import Counter


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
WEB = PROJ / "02_wiki/web"
CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

BOARD = WEB / "data/boards/fashion_wardrobe.json"
PART_RE = re.compile(r"^(.*?)[-·](衣服|头饰|背包|光源|整套|面饰|发饰)(?:[-·]|$)")
v = lambda x: x[1] if isinstance(x, tuple) else x


def load(name: str):
    raw = (CD / (name + ".py")).read_bytes()
    at = raw.find(b"x{")
    L = int.from_bytes(raw[at + 2:at + 6], "little")
    chs = CD / (name + "_chs.py")
    pool = BT.parse_legacy_chs_pool(chs.read_bytes()) if chs.is_file() else None
    return BT.decode_table_rows(raw[at + 6:at + 6 + L], pool, resolve_jumps=False, lenient=True)[0]


def main() -> int:
    rows = load("player_appear_data")
    by_model: dict[int, dict[str, dict]] = {}
    for r in rows:
        val = r["values"]
        nm = str(v(val.get("name")) or "").strip()
        m = PART_RE.match(nm)
        if not m:
            continue
        base, part = m.group(1).strip(), m.group(2)
        try:
            mid = int(v(val.get("model_id")))
        except (TypeError, ValueError):
            continue
        by_model.setdefault(mid, {})[part] = {
            "row": r["key"], "name": nm, "desc": str(v(val.get("desc")) or ""),
            "charm": v(val.get("charm_value")),
        }

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    added = Counter()
    touched = 0
    for it in board["items"]:
        try:
            mid = int(it.get("model_id"))
        except (TypeError, ValueError):
            continue
        parts = by_model.get(mid)
        if not parts:
            continue
        # 名字必须同族：卡名去掉「-部位」后与 appear 名字同前缀，避免把别的套装部位并进来
        _m0 = PART_RE.match(str(it.get("name") or ""))
        card_base = _m0.group(1).strip() if _m0 else str(it.get("name") or "").strip()
        def _base(nm: str) -> str:
            m2 = PART_RE.match(nm)
            return m2.group(1).strip() if m2 else ""
        parts = {p2: d2 for p2, d2 in parts.items()
                 if _base(d2["name"]) in (card_base, card_base + "幻典")}
        if not parts:
            continue
        have = set(it.get("part_bucket") or [])
        miss = {p: d for p, d in parts.items() if p not in have}
        if not miss:
            continue
        for p, d in miss.items():
            have.add(p)
            added[p] += 1
        it["part_bucket"] = sorted(have, key=lambda x: ["衣服", "头饰", "背包", "光源", "整套", "面饰", "发饰"].index(x)
                                   if x in ("衣服", "头饰", "背包", "光源", "整套", "面饰", "发饰") else 99)
        it.setdefault("appearance_rows", {})
        for p, d in miss.items():
            it["appearance_rows"][p] = d
        it["part_source_extra"] = "player_appear_data（补齐 fashion_data 未登记的部位）"
        touched += 1

    BOARD.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")
    print("补齐卡数 %d ｜ 新增部位统计 %s" % (touched, added.most_common()))
    x = [i for i in board["items"] if "不湮之花" in str(i.get("name"))]
    for i in x:
        print("  不湮之花 →", i.get("name"), i.get("part_bucket"), list((i.get("appearance_rows") or {}).keys()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
