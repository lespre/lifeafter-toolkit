# -*- coding: utf-8 -*-
"""P3：可靠数据源筛选 v2 —— 源状态=类别关键槽聚合。

类别关键槽：
  名称正源 → name
  物品/时装/武器/载具/商店/奖池/活动/其他 → name + icon（desc 仅参考）
槽跨 schema 状态聚合：含 unsafe（有样本）→unsafe；否则含 unresolved→unresolved；
  否则含 likely→likely；全 verified→verified。
can_prove/cannot_prove 按关键槽状态陈述（事实性，不升华语义）。
KJ1 格式表（无 schema 字段语义）=kj1-format 单列 unresolved（本层不适用）。
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TE = ROOT / "data" / "table_index_entries.jsonl"
RULES = ROOT / "data" / "FIELD_RULES.json"
OUT = ROOT / "data" / "RELIABLE_SOURCES.json"
OUT_RULES = ROOT / "data" / "SOURCE_RULES.json"
OUT_MD = ROOT / "docs" / "SOURCE_RULES.md"

CATEGORY_PATTERNS = [
    ("名称正源", [r"common_item", r"gift", r"item_name", r"_name_data",
                  r"name_display"]),
    ("物品/装备", [r"item", r"equip", r"bobj", r"material", r"backpack",
                   r"prop_", r"consum", r"resource_", r"armor", r"hat",
                   r"accessory"]),
    ("武器", [r"weapon", r"gun", r"arms"]),
    ("时装", [r"fashion", r"cloth", r"costume", r"avatar", r"dress",
              r"skin"]),
    ("载具", [r"vehicle", r"_car", r"motorcycle", r"aircraft"]),
    ("活动", [r"activity", r"act_", r"huodong", r"event", r"mission",
              r"campaign", r"season", r"anniversary", r"battle_pass"]),
    ("奖池", [r"lottery", r"reward", r"_pool", r"prize", r"draw",
              r"kaijia"]),
    ("商店/兑换", [r"shop", r"store", r"exchange", r"transfer", r"mall",
                   r"trade", r"market"]),
    ("其他业务配置", []),
]
STATE_RANK = {"unsafe": 4, "unresolved": 3, "likely": 2, "verified": 1}


def categorize(fam: str) -> str:
    low = fam.lower().replace(".py", "")
    for cat, pats in CATEGORY_PATTERNS:
        for p in pats:
            if re.search(p, low):
                return cat
    return "其他业务配置"


def canonical_family(fam: str) -> str:
    m = re.search(r"_auto_oversea_data_[a-z0-9]+$", fam)
    if m:
        return fam[:m.start()]
    return fam


def main() -> int:
    tables = json.loads(RULES.read_text(encoding="utf-8"))["tables"]
    # 槽跨 schema 聚合：name -> worst state（unsafe 有样本优先）
    sources = []
    for te in tables:
        entry = te["entry"]
        tname = te.get("table")
        if not tname:
            continue
        basename = tname.replace("/", "\\").split("\\")[-1]
        stem = basename[:-3]
        if re.search(r"_(chs|base_chs|inc_chs|inc|del|merged)$", stem):
            continue
        fam_raw = re.sub(r"_(chs|base_chs|inc_chs|inc|del|merged)$", "",
                         stem)
        fam = canonical_family(fam_raw)
        slot_worst: dict[str, tuple[int, str]] = {}
        for sch in te.get("schemas", []):
            for f in sch.get("fields", []):
                nm = f.get("name")
                st = f.get("state", "unresolved")
                if not nm:
                    continue
                if st == "unresolved" and "no-samples" in (f.get("evidence")
                                                           or ""):
                    continue  # 无样本=无反证，不压实证状态
                old = slot_worst.get(nm)
                if old is None or STATE_RANK[st] > old[0]:
                    slot_worst[nm] = (STATE_RANK[st], st)
        def worst_of(names):
            sts = [slot_worst[n][1] for n in names if n in slot_worst]
            if not sts:
                return None
            return max(sts, key=lambda s: STATE_RANK[s])
        cat = categorize(fam_raw)
        if cat == "名称正源":
            keys = ["name"]
            keys2 = ["desc", "short_name"]
        else:
            keys = ["name", "icon"]
            keys2 = ["desc", "title", "short_name"]
        state = worst_of(keys)
        if state is None:
            state = worst_of(keys2)
        if state is None:
            # 无标准语义槽名：结构槽全 verified → numeric-only verified
            numeric_ok = all(
                slot_worst[n][1] in ("verified", "likely")
                for n in slot_worst)
            state = "verified" if numeric_ok and slot_worst else "unresolved"
            mode = "numeric_only" if state == "verified" else "no_semantic"
        else:
            mode = "semantic"
        can = []
        cannot = []
        for n in keys + keys2:
            v = slot_worst.get(n)
            if not v:
                continue
            if v[1] == "verified":
                can.append(n + " 槽")
            elif v[1] == "unsafe":
                cannot.append(n + " 槽（unsafe，禁业务真值）")
            elif v[1] == "unresolved":
                cannot.append(n + " 槽（unresolved）")
        sources.append({
            "table": tname, "entry": entry,
            "family_canonical": fam,
            "variant": fam_raw if fam_raw != fam else None,
            "category": cat,
            "state": state,
            "key_slots": {n: (slot_worst[n][1] if n in slot_worst else None)
                          for n in ["name", "icon", "desc", "title"]},
            "can_prove": can, "cannot_prove": cannot,
            "evidence_mode": mode,
        })
    by_state = Counter(s["state"] for s in sources)
    by_cat = Counter(s["category"] for s in sources)
    by_state_cat = Counter((s["category"], s["state"]) for s in sources)
    out = {
        "schema_version": 2,
        "snapshot": "test-328b8446…（BA8 工作副本）",
        "sources": sources,
        "stats": {
            "sources_total": len(sources),
            "by_state": dict(by_state),
            "by_category": dict(by_cat),
            "by_category_state": {f"{c}:{s}": v for (c, s), v in
                                  sorted(by_state_cat.items())},
            "numeric_only": sum(1 for s in sources
                                if s["evidence_mode"] == "numeric_only"),
        },
        "note": "源状态=类别关键槽跨 schema 聚合（名称正源→name；业务源→name+icon）；"
                "unsafe 禁业务真值；KJ1 格式表不在 FIELD_RULES（无 schema 语义）；"
                "can/cannot=槽状态事实陈述；server_branch=unresolved",
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    rules = {
        "schema_version": 2,
        "rules": [
            "verified：关键槽（名称正源=name；业务源=name+icon）全 verified，"
            "槽值可用于该字段语义。",
            "usable_with_limits：关键槽 likely（样本不足）——行级复核后可用。",
            "unsafe：关键槽 unsafe（历史错位/名型矛盾/模式冲突）——该槽值禁止作为业务真值；"
            "结构字段仍可参考。",
            "unresolved：关键槽池缺/无样本/无标准语义槽名——不得作为业务依据。",
            "类别仅表名模式归类，不构成业务关系证明；不做业务 join。",
            "oversea 变体（*_auto_oversea_data_*）为分支版本，使用时须标注维度；"
            "server_branch 一律 unresolved。",
        ],
        "category_patterns": [
            {"category": c, "patterns": [p for p in pats if p]}
            for c, pats in CATEGORY_PATTERNS if pats
        ],
    }
    OUT_RULES.write_text(json.dumps(rules, ensure_ascii=False, indent=1),
                         encoding="utf-8")
    OUT_MD.write_text(
        "# SOURCE_RULES（P3 可靠数据源规则 v2）\n\n"
        "1. **verified**：关键槽（名称正源=name；业务源=name+icon）全 verified。\n"
        "2. **usable_with_limits**：关键槽 likely（样本不足），行级复核后可用。\n"
        "3. **unsafe**：关键槽 unsafe——该槽值禁止作为业务真值。\n"
        "4. **unresolved**：池缺/无样本/无标准语义槽名。\n"
        "5. 类别仅表名模式归类；不做业务 join。\n"
        "6. oversea 变体为分支版本；server_branch 一律 unresolved。\n",
        encoding="utf-8")
    print(json.dumps(out["stats"], ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    main()
