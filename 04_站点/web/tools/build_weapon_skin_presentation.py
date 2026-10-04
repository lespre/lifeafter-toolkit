#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""生成 WEAPON_SKIN 展示层边车（PRESENTATION_LEGACY.jsonl）。

用途：卡片需要的 官方描述 / 特效名 / 历史参考 等**展示字段**在 canonical 侧尚无来源
（canonical 特效字段只有 jump id，特效名解析未建立）。这些字段一次性从 legacy board 抽取，
逐条标注 presentation_only=true + source，**不得进入 business identity / 名称 / 绑定结论**。

产物：artifacts/active/weapon_skin/PRESENTATION_LEGACY.jsonl
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / "data" / "boards" / "weapon_skin_sfx_text_sources.json"
OUT = ROOT / "artifacts" / "active" / "weapon_skin" / "PRESENTATION_LEGACY.jsonl"
SRC = "data/boards/weapon_skin_sfx_text_sources.json（legacy 板，仅展示层）"


def main() -> int:
    b = json.loads(BOARD.read_text(encoding="utf-8"))
    out = []
    for i in b["items"]:
        sfx = []
        for s in (i.get("sfx_items") or []):
            nm = s.get("display_name") or s.get("item_name")
            if nm:
                sfx.append({"name": nm, "type_label": s.get("sfx_type_label"), "item_id": s.get("id")})
        out.append({
            "skin_item_id": int(i.get("skin_id") or i.get("id")),
            "presentation_only": True,
            "source": SRC,
            "official_desc": i.get("official_desc"),
            "sale_date": i.get("sale_date"),
            "weapon_type_label": i.get("weapon_type_label"),
            "sfx_names": sfx,
            "sfx_named_count": i.get("named_sfx_item_count"),
            "variant_item_count": i.get("variant_item_count"),
            "historical_ref": {
                "legacy_grade_label": i.get("grade"),
                "reference_source": ((i.get("reference_fields") or {}).get("source_kind")),
                "reference_sha256": ((i.get("reference_fields") or {}).get("source_sha256")),
                "legacy_status_tags": i.get("status_tags"),
            },
            "ip_now": i.get("ip_now"),
        })
    OUT.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out), encoding="utf-8")
    print(json.dumps({"rows": len(out), "with_desc": sum(1 for r in out if r["official_desc"]),
                      "with_sfx_names": sum(1 for r in out if r["sfx_names"]), "out": str(OUT.relative_to(ROOT))},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
