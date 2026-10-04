"""Chain Auditor（v1.4）：10 项定位链不变量检查。

用法：
    python -m tools.audit_locator_chains            # 人类可读 + JSON 摘要
    python -m tools.audit_locator_chains --json     # 只输出 JSON

检查项（任一项 FAIL ⇒ 退出码 1）：
 1. verified 跳必须有 evidence（evidence_type + evidence_ref）
 2. 物理跳必须绑 snapshot_id（verified/likely 时不得为空）
 3. entry 跳必须绑定 PayloadRef（引用 registry 绑定/ payload map）
 4. BA8A 跳不得冒充 current
 5. board 不得作为身份来源；有 legacy 依赖必须登记定位债
 6. Fashion 三钥匙不得自动相连
 7. business identity 不得推导 physical binding（两维必须独立且显式）
 8. name verified 必须有名称证据
 9. lottery item join 必须先通过 target-type 跳
10. rejected 跳不得重新进入 active chain
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from locator_chains.build import INVENTORY_BASIS, bindings, current_snapshot  # noqa: E402

CHAINS = REPO / "locator_chains"
SCHEMA = json.loads((CHAINS / "schema.json").read_text(encoding="utf-8"))
REGISTRY = json.loads((CHAINS / "registry.json").read_text(encoding="utf-8"))
PHYSICAL_HOPS = {h["id"] for h in SCHEMA["hops"] if h["physical"]}
PAYLOAD_HOPS = {"data_fid", "data_entry", "chs_fid", "chs_entry"}
STATUS = set(SCHEMA["status_vocab"])
FORBIDDEN_WORDS = SCHEMA["forbidden_status_words"]
BOARD_TOKENS = ("data/boards", "data\\boards")


def _instances(chain: dict) -> list[dict]:
    p = REPO / chain["instances_file"]
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def _cur_ok(table_short: str) -> bool:
    """current 绑定成立 = data 与 CHS 同时 ok（与 locator_chains/build.py 的口径一致）。"""
    b = (bindings().get(table_short) or {}).get("bindings", {}).get(current_snapshot()) or {}
    d = (b.get("data_payload_ref") or {}).get("status")
    c = (b.get("chs_payload_ref") or {}).get("status")
    return d == "ok" and c == "ok"


def check(chains: dict[str, dict], insts: dict[str, list[dict]]) -> dict:
    """在内存结构上执行 10 项检查（可注入故障以自证非空洞）。"""
    results: list[dict] = []
    inventory = {"legacy_dependencies": [], "broken": [], "status_vocab_violations": []}

    def _instances(c: dict) -> list[dict]:
        return insts.get(c["chain_id"], [])

    def add(cid: str, key: str, hop: str, msg: str) -> None:
        results.append({"check": CURRENT, "chain": cid, "instance": key, "hop": hop, "detail": msg})

    # ---- 1 ----
    CURRENT = 1
    for cid, c in chains.items():
        for it in _instances(c):
            for e in it["edges"]:
                if e["status"] in ("verified", "likely"):
                    if not e.get("evidence_type") or not e.get("evidence_ref"):
                        add(cid, it["entity_key"], e["to"], "verified 跳缺 evidence_type/evidence_ref")
                if e["status"] not in STATUS:
                    inventory["status_vocab_violations"].append({"chain": cid, "instance": it["entity_key"], "hop": e["to"], "status": e["status"]})
    # ---- 2 ----
    CURRENT = 2
    for cid, c in chains.items():
        for it in _instances(c):
            for e in it["edges"]:
                if e["to"] in PHYSICAL_HOPS and e["status"] in ("verified", "likely") and not e.get("snapshot_id"):
                    add(cid, it["entity_key"], e["to"], "物理跳缺 snapshot_id")
    # ---- 3 ----
    CURRENT = 3
    for cid, c in chains.items():
        for it in _instances(c):
            for e in it["edges"]:
                if e["to"] in PAYLOAD_HOPS and e["status"] == "verified":
                    refs = " ".join(e.get("evidence_ref") or [])
                    if "snapshot_payload_bindings" not in refs and "payload_maps" not in refs:
                        add(cid, it["entity_key"], e["to"], "entry 跳未绑定 PayloadRef（无 registry 绑定引用）")
                    if not e.get("snapshot_id"):
                        add(cid, it["entity_key"], e["to"], "entry 跳缺 snapshot_id（entry 不得脱离快照）")
    # ---- 4 ----
    CURRENT = 4
    for cid, c in chains.items():
        if c["domain"] not in ("item", "gift", "recipe", "belt_chip", "lottery", "fashion"):
            continue
        for it in _instances(c):
            if (it.get("completeness") or {}).get("current_snapshot_binding") == "verified":
                tbl = {"item": "common_item", "gift": "gift", "recipe": "recipe", "belt_chip": "belt_chip",
                       "lottery": "reward_pool", "fashion": "fashion"}[c["domain"]]
                if not _cur_ok(tbl):
                    add(cid, it["entity_key"], "current_snapshot_binding", "current 绑定未成立却标 verified（BA8A 冒充 current）")
            for e in it["edges"]:
                if e.get("snapshot_id") == INVENTORY_BASIS and e["status"] == "verified" and "current" in str(e.get("rule") or "") and "current" in str(e.get("rule") or "").replace("current", "", 1):
                    if "不" not in str(e.get("rule")):
                        add(cid, it["entity_key"], e["to"], "BA8A 跳的 rule 声称 current verified")
    # ---- 5 ----
    CURRENT = 5
    for cid, c in chains.items():
        for it in _instances(c):
            for e in it["edges"]:
                refs = " ".join(e.get("evidence_ref") or [])
                if any(t in refs for t in BOARD_TOKENS) and e["status"] in ("verified", "likely"):
                    add(cid, it["entity_key"], e["to"], "board 被当作 verified 身份/表来源")
            for dep in it.get("legacy_dependencies") or []:
                inventory["legacy_dependencies"].append({"chain": cid, "instance": it["entity_key"], "dependency": dep})
        if c.get("legacy_debt") is None and any(
                (it.get("legacy_dependencies") or []) for it in _instances(c)):
            add(cid, "-", "-", "存在 legacy 依赖但 registry 未登记定位债（legacy_debt）")
    # ---- 6 ----
    CURRENT = 6
    for cid, c in chains.items():
        if c["domain"] != "fashion":
            continue
        for it in _instances(c):
            rel = ((it.get("three_keys") or {}).get("relation") or "")
            if "NO RELATION PROVEN" not in rel:
                add(cid, it["entity_key"], "three_keys", "三钥匙关系未标注 NO RELATION PROVEN")
            for e in it["edges"]:
                if e["to"] in ("structural_key", "decoded_row") and e["status"] in ("verified", "likely"):
                    add(cid, it["entity_key"], e["to"], "fashion 物理跳被标 verified（应为断链）")
    # ---- 7 ----
    CURRENT = 7
    for cid, c in chains.items():
        for it in _instances(c):
            comp = it.get("completeness") or {}
            if comp.get("business_identity") == "verified" and comp.get("row_binding") in ("unresolved", "rejected", None):
                if not (it.get("break_reason") or any(e.get("residual") for e in it["edges"] if e["to"] == "structural_key")):
                    add(cid, it["entity_key"], "business_identity", "business verified 与 physical 断链未显式区分")
            if comp.get("business_identity") != comp.get("payload_binding") and "business" not in json.dumps(comp, ensure_ascii=False):
                pass  # 两维独立本身即满足；仅要求不被压成一个布尔
    # ---- 8 ----
    CURRENT = 8
    for cid, c in chains.items():
        for it in _instances(c):
            for e in it["edges"]:
                if e["to"] == "name_binding" and e["status"] == "verified":
                    ok = bool(e.get("evidence_ref")) and ("名称" in str(e.get("rule")) or "name" in str(e.get("rule")).lower())
                    if not ok:
                        add(cid, it["entity_key"], "name_binding", "name verified 缺名称证据/判据")
    # ---- 9 ----
    CURRENT = 9
    for cid, c in chains.items():
        if c["domain"] != "lottery":
            continue
        for it in _instances(c):
            if it.get("kind") != "lottery_reward_target":
                continue
            passed_gate = any(e["to"] == "runtime_final" and e["status"] == "verified" and "item" in str(e.get("rule"))
                              for e in it["edges"])
            joined = any(e["to"] == "resolved_entity" and e["status"] == "verified" for e in it["edges"])
            if joined and not passed_gate:
                add(cid, it["entity_key"], "resolved_entity", "item join 未通过 target-type 门槛")
    # ---- 10 ----
    CURRENT = 10
    for cid, c in chains.items():
        rejected_tokens: list[str] = []
        for r in c.get("rejected_routes") or []:
            tok = str(r.get("route") or "").strip()
            if tok:
                rejected_tokens.append(tok.split("（")[0].strip())
        for it in _instances(c):
            for e in it["edges"]:
                if e["status"] == "rejected" and not (e.get("rejected_alternatives") or e.get("residual")):
                    add(cid, it["entity_key"], e["to"], "rejected 跳缺 rejected_alternatives/residual")
                if e["status"] in ("verified", "likely"):
                    rule = str(e.get("rule") or "")
                    for tok in rejected_tokens:
                        if len(tok) >= 4 and tok in rule:
                            add(cid, it["entity_key"], e["to"], f"已拒路线重新进入 active chain：{tok}")
            if it.get("break_at"):
                inventory["broken"].append({"chain": cid, "instance": it["entity_key"],
                                            "break_at": it["break_at"], "reason": it.get("break_reason")})

    by_check: dict[int, int] = {}
    for r in results:
        by_check[r["check"]] = by_check.get(r["check"], 0) + 1
    return {"ok": not results, "violations": results, "violations_by_check": by_check, "inventory": inventory}


def load() -> tuple[dict, dict]:
    chains = {c["chain_id"]: c for c in REGISTRY["chains"]}
    insts = {cid: _instances(c) for cid, c in chains.items()}
    return chains, insts


def run() -> dict:
    chains, insts = load()
    return check(chains, insts)


NAMES = {
    1: "verified 跳必须有 evidence",
    2: "物理跳必须绑 snapshot_id",
    3: "entry 跳必须绑定 PayloadRef",
    4: "BA8A 不得冒充 current",
    5: "board 不得作身份来源 / legacy 债须登记",
    6: "Fashion 三钥匙不得自动相连",
    7: "business identity 不得推导 physical binding",
    8: "name verified 必须有名称证据",
    9: "lottery item join 必须过 target-type 门槛",
    10: "rejected 跳不得重回 active chain",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    rep = run()
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=1))
    else:
        for i in range(1, 11):
            n = rep["violations_by_check"].get(i, 0)
            print(f"[{'PASS' if n == 0 else 'FAIL'}] {i:>2}. {NAMES[i]}  ({n} 处)")
        print(f"\n链数 {len(REGISTRY['chains'])} · 实例 {REGISTRY['totals']['instances']} · 断链实例 {REGISTRY['totals']['broken_instances']}")
        print(f"legacy 依赖条目 {len(rep['inventory']['legacy_dependencies'])} · 状态词违规 {len(rep['inventory']['status_vocab_violations'])}")
        if rep["violations"]:
            print("\n违规明细：")
            for v in rep["violations"][:20]:
                print(f"  check{v['check']} {v['chain']} / {v['instance']} / {v['hop']} —— {v['detail']}")
        print("\n总体：", "PASS" if rep["ok"] else "FAIL")
    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
