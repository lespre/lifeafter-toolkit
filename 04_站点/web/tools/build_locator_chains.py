"""生成 canonical Locator Chain 层（v1.4 Phase 1）。

产物：
    locator_chains/registry.json                 唯一正式入口（链清单 + completeness 汇总）
    locator_chains/<domain>/chain.json           链定义（hops / evidence_refs / residuals / rejected_routes）
    locator_chains/<domain>/instances.jsonl      实例（每跳 from/to/status/evidence/… + 11 维 completeness）

只整理既有结构化证据，不做新调查；不改 Wiki / UI / Domain / API 业务功能。
"""
from __future__ import annotations

import datetime
import json
import sys
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from locator_chains.build import build_all  # noqa: E402

OUT = REPO / "locator_chains"
DIMS = ("runtime_semantic", "namespace", "logical_table", "snapshot_binding", "payload_binding",
        "row_binding", "field_binding", "business_identity", "name_binding",
        "current_snapshot_binding", "runtime_final")



def _debt_entry(doc: dict, marker: str) -> dict:
    """定位债状态：active artifact 的 RULES.generated_from 若已不含该 legacy 源 ⇒ repaid。

    判据只看 generated_from（真实来源），不看 RULES 里的 forbidden_sources（那里会写明禁用它）。
    """
    domain = doc.get("domain")
    rules_p = REPO / "artifacts" / "active" / str(domain) / "RULES.json"
    gen: list = []
    if rules_p.exists():
        try:
            gen = json.loads(rules_p.read_text(encoding="utf-8")).get("generated_from") or []
        except Exception:
            gen = []
    txt = json.dumps(gen, ensure_ascii=False)
    repaid = bool(gen) and (marker not in txt)
    return {"dependency": marker, "status": "repaid" if repaid else "unpaid",
            "note": ("active 结论已不依赖该源：RULES.generated_from 只含 canonical 来源，"
                     "并有删除该源仍可重建的测试守护" if repaid else
                     "active 结论若只能靠 board/日志支撑即为定位债；需用结构化证据偿还（本轮不替换）"),
            "evidence": ("artifacts/active/%s/RULES.json#generated_from" % domain) if repaid else None}


def main() -> int:
    now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    docs = build_all()
    registry = {"schema": "locator-chain/v1", "generated": now,
                "entry_point": "locator_chains/registry.json",
                "auditor": "python -m tools.audit_locator_chains",
                "explain": "python -m api.cli explain <kind> <key>",
                "chains": []}
    total_inst = 0
    for chain_id, doc in docs.items():
        d = OUT / doc["domain"]
        d.mkdir(parents=True, exist_ok=True)
        definition = {k: v for k, v in doc.items() if k != "instances"}
        (d / "chain.json").write_text(json.dumps(definition, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        insts = doc["instances"]
        with (d / "instances.jsonl").open("w", encoding="utf-8") as fh:
            for it in insts:
                fh.write(json.dumps(it, ensure_ascii=False) + "\n")
        total_inst += len(insts)
        summary: dict[str, dict[str, int]] = {}
        for dim in DIMS:
            c: dict[str, int] = {}
            for it in insts:
                v = str((it.get("completeness") or {}).get(dim))
                c[v] = c.get(v, 0) + 1
            summary[dim] = c
        legacy: list[str] = sorted({m for it in insts for m in (it.get("legacy_dependencies") or [])})
        broken = sum(1 for it in insts if it.get("break_at"))
        registry["chains"].append({
            "chain_id": chain_id, "domain": doc["domain"], "title": doc["title"],
            "kind": "semantic+physical+name（同一实例内三维独立）",
            "definition": f"locator_chains/{doc['domain']}/chain.json",
            "instances_file": doc["instances_file"],
            "instance_count": len(insts), "broken_instances": broken,
            "completeness": summary,
            "residuals": doc["residuals"],
            "rejected_routes": doc["rejected_routes"],
            "rejected_route_count": len(doc["rejected_routes"]),
            "legacy_dependencies": legacy,
            "legacy_debt": ([_debt_entry(doc, m) for m in legacy] if legacy else []),
            "evidence_refs": doc["evidence_refs"],
        })
    registry["totals"] = {"chains": len(docs), "instances": total_inst,
                          "broken_instances": sum(c["broken_instances"] for c in registry["chains"])}
    (OUT / "registry.json").write_text(json.dumps(registry, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"chains": [(c["chain_id"], c["instance_count"], c["broken_instances"]) for c in registry["chains"]],
                      "totals": registry["totals"]}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
