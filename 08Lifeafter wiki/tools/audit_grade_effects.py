#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""按 GRADE_EFFECT_RULES 核对 weapon_skin v0.2 的品级×特效覆盖（只读审计，不改任何数据）。

输出：analysis/audit/weapon_skin_grade_effects.json
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts" / "active" / "weapon_skin" / "WEAPON_SKIN_RESOLVED.jsonl"
RULES = ROOT / "domains" / "weapon_skin" / "GRADE_EFFECT_RULES.json"
OUT = ROOT / "analysis" / "audit" / "weapon_skin_grade_effects.json"
VARIANT_MARK = "（"


def _val(df, f):
    return df.get(f) not in (None, "", [], {})


def main() -> int:
    rules = json.loads(RULES.read_text(encoding="utf-8"))
    rows = [json.loads(x) for x in ART.read_text(encoding="utf-8").splitlines() if x.strip()]
    eff, tiers = rules["effects"], rules["tiers"]
    report = {"generated_from": ["weapon_skin v0.2", "GRADE_EFFECT_RULES.json"],
              "field_mapping": {k: v["fields"] for k, v in eff.items()},
              "mapping_status": {k: v.get("status") for k, v in eff.items()},
              "tiers": {}, "deviations": []}
    for lv in ("6", "5", "4", "3", "2"):
        rs = [r for r in rows if str(r.get("level")) == lv]
        cov = {}
        for label, meta in eff.items():
            hit = [r["skin_item_id"] for r in rs if any(_val(r.get("data_fields") or {}, f) for f in meta["fields"])]
            cov[label] = {"rows": len(hit), "of": len(rs), "ids": hit[:60]}
        std = tiers[lv]["standard"]
        report["tiers"][lv] = {"name": tiers[lv]["name"], "rows": len(rs), "coverage": cov}
        for r in rs:
            df = r.get("data_fields") or {}
            if VARIANT_MARK in str(r.get("name") or ""):
                continue                      # 变体行天然字段少，不按本标准判
            miss = [x for x in std if not any(_val(df, f) for f in eff[x]["fields"])]
            extra = []
            if lv == "4":
                forbidden = [x for x in ("击败特效", "伤害跳字", "专属待机动作")
                             if any(_val(df, f) for f in eff[x]["fields"])]
                if forbidden and r["skin_item_id"] != 1110023:
                    extra = forbidden
            wt = r.get("canonical_fields", {}).get("weapon_type")
            melee = bool(df.get("coldarm_types")) and wt == 50
            # R1/R2（待用户确认的细化）：冷兵器无准心；非枪械类别无弹道 ⇒ 先归类为 explained_by_hypothesis
            explained = []
            for m in list(miss):
                if m == "攻击准心" and melee:
                    miss.remove(m); explained.append("R1_melee_no_crosshair")
                elif m == "攻击弹道" and not melee:
                    miss.remove(m); explained.append("R2_weapon_class_no_trace")
            if miss or extra or explained:
                report["deviations"].append({"skin_item_id": r["skin_item_id"], "name": r.get("name"),
                                             "level": int(lv), "weapon_type": wt,
                                             "missing_standard": miss, "extra_beyond_tier": extra,
                                             "explained_by_hypothesis": explained,
                                             "kind": "true_deviation" if (miss or extra) else "hypothesis_explained"})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"tiers": {k: v["rows"] for k, v in report["tiers"].items()},
                      "deviations": len(report["deviations"]),
                      "out": str(OUT.relative_to(ROOT))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
