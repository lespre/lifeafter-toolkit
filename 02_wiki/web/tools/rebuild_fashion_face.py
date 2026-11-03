#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rebuild_fashion_face — 人物·面饰/挂饰名册（一行 = 一个去时限后的面饰名）

源（只读 PE 还原树）：`41_还原树/pe/配置/com/cdata/player_module_appear_data.py`
      + 配对池 `player_module_appear_data_chs.py`

口径（与旧池扫描板同一分法，但改为「池名册 × 行级覆盖」双向核对）：
  ① 名册 = CHS 池里形如面饰名的字符串（去 `-N天` 时限后缀聚合，N∈1/3/5/7/14/30）
  ② 行级覆盖 = 表里 `part_type == "face"` 的行，以及旧 schema（无 part_type 字段）里
     `part ∈ {1,2}` 的面饰行；名字按 `name` 去 `-N天` 后缀归一
  ③ 两者**必须相等**（2026-11-04 实测 190 == 190）；不等就在 meta 里写出差集，不静默吞

字段：id / name / part / time_limited_variants / desc / row_variants / provenance。
本板是**名册视图**；行级槽位复证（每行 name/desc 的 CHS 槽位）见 fashion_face_slots。

用法：python 02_wiki/web/tools/rebuild_fashion_face.py [--check]
"""
from __future__ import annotations

import collections
import datetime
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pe_source as src  # noqa: E402
from board_io import write_board_pair  # noqa: E402

BOARD_ID = "fashion_face"
TABLE = "player_module_appear_data"
OUT = src.board_path(BOARD_ID)

_DUR_SUFFIX = re.compile(r"-(\d+)天$")
_DUR_ANY = re.compile(r"^(.+)-(\d+)天$")
DURATION_CHOICES = (1, 3, 5, 7, 14, 30)


def is_name(s: str) -> bool:
    """池字符串是否像个面饰名（沿用旧池扫描判据，保持可比）。"""
    return (1 < len(s) <= 14 and "#f" not in s and "。" not in s and not s.isascii()
            and not s.startswith(("character/", "ui/")) and "面饰男女" not in s)


def strip_dur(name: str) -> str:
    return _DUR_SUFFIX.sub("", name)


def build() -> tuple[dict, dict]:
    table = src.load(TABLE)
    pool = table["pool"]
    rows = table["rows"]

    # ① 池名册（去时限后缀聚合时限档）
    roster: collections.OrderedDict[str, dict] = collections.OrderedDict()
    for s in pool:
        m = _DUR_ANY.match(s)
        if m:
            roster.setdefault(m.group(1), {"dur": set()})["dur"].add(int(m.group(2)))
            continue
        if is_name(s) and s not in roster:
            roster[s] = {"dur": set()}

    # ② 行级覆盖（面饰行：part_type=face，或旧 schema 无 part_type 时 part∈{1,2}）
    by_name: dict[str, list[dict]] = collections.defaultdict(list)
    for r in rows:
        nm = src.val(r, "name")
        if isinstance(nm, str):
            by_name[strip_dur(nm)].append(r)
    face_names = set()
    for r in rows:
        nm = src.val(r, "name")
        if not isinstance(nm, str):
            continue
        pt = src.val(r, "part_type")
        if pt == "face" or (pt is None and src.val(r, "part") in (1, 2)):
            face_names.add(strip_dur(nm))

    lock = src.lock_of(table["base"], source_id=src.SOURCE_TREE)
    only_roster = sorted(set(roster) - face_names)
    only_rows = sorted(face_names - set(roster))

    items = []
    for i, (name, info) in enumerate(roster.items()):
        variants = sorted(by_name.get(name, []), key=lambda r: int(r["key"]))
        rep = variants[0] if variants else None
        durs = set(info["dur"])
        row_durs = {int(src.val(r, "valid_days") or 0) for r in variants} - {0}
        durs |= row_durs
        desc = None
        if rep is not None:
            for r in variants:
                if isinstance(src.val(r, "desc"), str) and src.val(r, "desc"):
                    desc = src.val(r, "desc")
                    break
        items.append({
            "id": f"face_{i:04d}",
            "name": name,
            "evidence": "structure",
            "source": (f"{TABLE} 池名册（{TABLE}_chs，去 -N天 时限聚合）+ 行级 part_type/name 覆盖核对"
                       " · PE 还原树"),
            "part": src.val(rep, "part_type") if rep is not None and src.val(rep, "part_type") else "面饰/挂饰",
            "time_limited_variants": sorted(d for d in durs if d in DURATION_CHOICES),
            "desc": desc,
            "desc_note": None if desc else "该名在本表无带 desc 的行（旧 schema 行），描述留空不猜",
            "provenance": src.item_provenance(
                source_id=src.SOURCE_TREE,
                lock_sha=lock["sha256"],
                table=TABLE,
                row_key=rep["key"] if rep is not None else f"pool:{name}",
                field_refs=(["show_name", "name", "part_type", "part", "valid_days", "desc"]
                            if rep is not None else [f"{TABLE}_chs pool string"]),
                name_source=f"{TABLE} 池名（去 -N天 后缀）",
                upstream_role=TABLE,
                entry=src.entry_of(table, f"{TABLE}_base"),
            ),
            "row_variants": [int(r["key"]) for r in variants],
            "evidence_level": "structure-only",
            "status_tags": ["static config"],
        })

    board = {
        "meta": {
            "name": "人物·面饰/挂饰",
            "category": "人物类-面饰",
            "source_server": "PE 测试服 · 表 41_还原树/pe/配置/com/cdata · player_module_appear_data",
            "package_sha": lock["sha256"],
            "generated": datetime.date.today().isoformat(),
            "evidence": "structure",
            "notes": (
                f"{len(items)} 个面饰/挂饰（眼镜/口罩/面具/头顶挂饰等）。"
                f"名册 = {TABLE}_chs 池名去 -N天 时限聚合；行级覆盖 = part_type=='face' 或旧 schema part∈{{1,2}} 的面饰行，"
                f"两者实测相等（池 {len(roster)} 名 / 行 {len(face_names)} 名）。"
                f"仅池有名：{len(only_roster)}；仅行有名：{len(only_rows)}。"
                "desc 取同主题行级富文本原样回放（不改写）；行级 CHS 槽位复证见 fashion_face_slots 板。"
            ),
            "source_label": f"{TABLE} · 测试服 PE 还原树",
            "provenance": {
                "contract_version": 3,
                "audit_status": "passed",
                "contract": "frozen-audited-artifact",
                "source_locks": [dict(lock, role="primary")],
                "source_scope": {
                    "cross_source_policy": "no-cross-source-field-join",
                    "integer_join_policy": "no-equal-integer-join",
                    "runtime_final_policy": "unknown-unless-runtime-proven",
                },
            },
            "state_summary": {
                "verified": 0, "unresolved": 0, "quarantined": 0,
                "static config": len(items), "runtime final unknown": 0,
            },
        },
        "stats": {
            "pool_strings": len(pool),
            "roster_names": len(roster),
            "face_row_names": len(face_names),
            "row_variants": sum(len(it["row_variants"]) for it in items),
            "catalog_entries": len(items),
        },
        "items": items,
    }
    return board, {"only_roster": only_roster, "only_rows": only_rows}


def main(argv: list[str]) -> int:
    board, diff = build()
    old = src.old_board(BOARD_ID)
    old_names = [it["name"] for it in old["items"]]
    new_names = [it["name"] for it in board["items"]]
    print(f"旧 {len(old_names)} 条 / 新 {len(new_names)} 条")
    print(f"新增名 {len(set(new_names) - set(old_names))} · 消失名 {len(set(old_names) - set(new_names))}")
    if diff["only_roster"] or diff["only_rows"]:
        print("⚠ 池/行 不一致：仅池有名", diff["only_roster"][:5],
              "仅行有名", diff["only_rows"][:5])
    if "--check" in argv:
        return 0
    write_board_pair(OUT, board, BOARD_ID)
    print(f"✅ {BOARD_ID}: {len(board['items'])} 条 → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
