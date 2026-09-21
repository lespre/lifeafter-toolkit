"""P4-A2 — ITEM_MASTER v0.2：把 common_item_data_base 七个 schema 的 27,753 候选批量升级/定档。

证据policy（v0.2 新增，v0.1 的 anchor-only 政策保持在原 RULES 不动）：
  item_id → Helpers.get_item_data(item_id) → DataHelpers.get_item_data
          → get_item_type(item_id) → com.cdata.common_item_data → .data.get(item_id) → item_info
          → 同行用于 bag/count/stack 业务（BagCompBase: max_stack_count/capacity、get_item_num、
            COMMON_ITEM_DATA.data.get(self.item_id) → is_blood_moon_*_item）
  该链为 runtime consumer evidence，独立于表自身内容，非循环证据。

负控（阶段 E，禁止升级）：
  - 只因为 row_key == id / integer collision / 表名像 item / 有 name/icon
  - foreign reference field（ITEM_MASTER v0.1 的拒绝规则继续有效）
  - 被 other dispatch namespace 遮蔽（id 同时存在于 belt_chip / nucleus / all_equips 表）
  - slot-6 desc 之类 chain_state=unsafe 的文本不得充当 name
所有排除项写入 audit，不写入 artifact。
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterable

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data"
AUDIT = REPO / "analysis" / "audit"

SOURCE_TABLE = "com\\cdata\\common_item_data_base.py"
EXPECTED_FID = "B42760CCA41DBC25"
EXPECTED_ENTRY = 18005
SCHEMAS = [92, 328, 689, 893, 49912, 118640, 245151]

CONSUMER_CHAIN = [
    "Helpers.get_item_data(item_id)",
    "DataHelpers.get_item_data(item_id)",
    "get_item_type(item_id)",
    "com.cdata.common_item_data",
    "data.get(item_id)",
    "item_info -> bag/count/stack business ops",
]
CONSUMER_EVIDENCE = {
    "type": "runtime_dispatch_consumer",
    "dispatch_symbol": "DataHelpers.get_item_data",
    "dispatch_body_artifact": "analysis/audit/helpers_def_hits/20487_datahelpers_get_item_data.bin",
    "consumer_symbols": [
        "BagItems.get_avail_space: Helpers.get_item_data(item_id) -> item_data -> max_stack_count",
        "BagItems.get_avail_space_for_common_item: Helpers.get_item_data(item_id) -> item_data",
        "BagCompBase.get_item_num(item_id)",
        "BagCompBase.is_blood_moon_inner_item: COMMON_ITEM_DATA.data.get(self.item_id) -> item_info",
        "BagCompBase.is_blood_moon_outer_item: COMMON_ITEM_DATA.data.get(self.item_id) -> item_info",
    ],
    "consumer_module": "com\\components\\avatar\\BagCompBase.py",
    "consumer_module_fid": "0D86C2AE10376C4E",
    "consumer_module_entry": 1410,
    "evidence_level": "runtime_consumer",
    "residuals": [
        "operand-level call binding = unresolved (opcode 级，P4-C 同类残差)",
        "get_item_type 的 numeric constant 表不可读 = unresolved",
    ],
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_jsonl(path: Path, needle: str | None = None) -> Iterable[dict[str, Any]]:
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            if needle is not None and needle not in line:
                continue
            line = line.strip()
            if line:
                yield json.loads(line)


def board_ids(path: Path) -> set[int]:
    if not path.exists():
        return set()
    doc = json.loads(path.read_text(encoding="utf-8"))
    items = doc.get("items") or doc.get("cards") or []
    out: set[int] = set()
    for item in items:
        for key in ("id", "item_id", "chip_id", "key", "skin_id"):
            value = item.get(key)
            if isinstance(value, bool):
                continue
            if isinstance(value, int):
                out.add(value)
            elif isinstance(value, str) and value.isdigit():
                out.add(int(value))
    return out


def collect_candidates() -> dict[int, set[int]]:
    cached = AUDIT / "p4a2_candidate_ids.json"
    doc = json.loads(cached.read_text(encoding="utf-8"))
    return {int(k): set(v) for k, v in doc.items()}


def collect_identity(allowed: dict[int, set[int]]) -> dict[tuple[int, int], dict[str, Any]]:
    out: dict[tuple[int, int], dict[str, Any]] = {}
    for row in load_jsonl(DATA / "ITEM_IDENTITY_CANDIDATES.jsonl", "common_item_data_base.py"):
        if row.get("table") != SOURCE_TABLE or row.get("candidate_field") != "id":
            continue
        schema = row.get("schema_ref")
        value = row.get("candidate_value")
        if schema not in allowed or not isinstance(value, int) or value not in allowed[schema]:
            continue
        out[(schema, value)] = row
    return out


def collect_names() -> dict[tuple[int, int], dict[str, Any]]:
    out: dict[tuple[int, int], dict[str, Any]] = {}
    for row in load_jsonl(DATA / "NAME_CHAIN_CANDIDATES.jsonl", "common_item_data_base.py"):
        if row.get("table") != SOURCE_TABLE:
            continue
        schema = row.get("schema_ref")
        if schema not in SCHEMAS or row.get("field_slot") != 4:
            continue
        if row.get("name_field") != "name" or row.get("name_role") != "primary":
            continue
        if row.get("chain_state") != "verified" or row.get("entity_name_allowed") is not True:
            continue
        out[(schema, row.get("row_key"))] = row
    return out


def publishable_name(row: dict[str, Any] | None, item_id: int) -> tuple[str | None, str]:
    if not row:
        return None, "unresolved_no_verified_name_row"
    if row.get("row_key") != item_id:
        return None, "unresolved_name_row_key_mismatch"
    if row.get("actual_value_present") is not True or row.get("replay_exact") is not True:
        return None, "unresolved_name_value_absent"
    text = row.get("raw_text")
    if not isinstance(text, str) or not text.strip():
        return None, "unresolved_empty_name"
    return text, "verified"


def build_new_rows(
    allowed: dict[int, set[int]],
    identity: dict[tuple[int, int], dict[str, Any]],
    names: dict[tuple[int, int], dict[str, Any]],
    shadow: dict[str, set[int]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    per_schema: dict[int, dict[str, int]] = collections.defaultdict(
        lambda: {"candidates": 0, "verified": 0, "shadowed": 0, "name_verified": 0, "name_unresolved": 0}
    )
    for schema in SCHEMAS:
        ids = sorted(allowed.get(schema, set()))
        per_schema[schema]["candidates"] = len(ids)
        for item_id in ids:
            shadow_hits = sorted(name for name, values in shadow.items() if item_id in values)
            if shadow_hits:
                per_schema[schema]["shadowed"] += 1
                excluded.append(
                    {
                        "schema_ref": schema,
                        "item_id": item_id,
                        "identity_state": "unresolved_dispatch_namespace_shadowed",
                        "reason": "id 同时存在于其它 dispatch namespace 表，运行时归属不可判",
                        "shadow_namespaces": shadow_hits,
                    }
                )
                continue
            src = identity.get((schema, item_id))
            if not src:
                excluded.append(
                    {
                        "schema_ref": schema,
                        "item_id": item_id,
                        "identity_state": "unresolved_missing_identity_row",
                        "reason": "候选清单存在但 identity 行缺失",
                    }
                )
                continue
            if src.get("repeat_decode_stable") is not True or src.get("source_state") != "verified":
                excluded.append(
                    {
                        "schema_ref": schema,
                        "item_id": item_id,
                        "identity_state": "unresolved_unstable_source",
                        "reason": f"repeat_decode_stable={src.get('repeat_decode_stable')} source_state={src.get('source_state')}",
                    }
                )
                continue
            name, name_status = publishable_name(names.get((schema, item_id)), item_id)
            per_schema[schema]["verified"] += 1
            per_schema[schema]["name_verified" if name_status == "verified" else "name_unresolved"] += 1
            rows.append(
                {
                    "item_id": item_id,
                    "name": name,
                    "name_status": name_status,
                    "max_stack_num": None,
                    "hide_in_bag": None,
                    "identity_state": "verified_runtime_business_key",
                    "identity_evidence": CONSUMER_EVIDENCE,
                    "provenance": {
                        "client": src.get("client"),
                        "snapshot": src.get("snapshot"),
                        "server_branch": src.get("server_branch", "unresolved"),
                        "package": src.get("package"),
                        "package_sha256": src.get("package_sha256"),
                        "FID": src.get("FID"),
                        "entry": src.get("entry"),
                        "table": src.get("table"),
                        "schema_ref": schema,
                        "row_key": src.get("row_key"),
                        "row_offset": src.get("row_offset"),
                        "marker": src.get("marker"),
                        "field_slot": src.get("field_slot"),
                        "scalar_type": src.get("scalar_type"),
                        "repeat_decode_stable": src.get("repeat_decode_stable"),
                        "upstream_artifact": "data/ITEM_IDENTITY_CANDIDATES.jsonl",
                        "upstream_business_id_allowed": src.get("business_id_allowed"),
                        "upstream_entity_kind": src.get("entity_kind"),
                    },
                    "name_evidence": {
                        "source_artifact": "data/NAME_CHAIN_CANDIDATES.jsonl",
                        "field_slot": 4,
                        "name_field": "name",
                        "name_role": "primary",
                        "chain_state": (names.get((schema, item_id)) or {}).get("chain_state"),
                        "entity_name_allowed": (names.get((schema, item_id)) or {}).get("entity_name_allowed"),
                        "value_chs_slot": (names.get((schema, item_id)) or {}).get("value_chs_slot"),
                        "status": name_status,
                    },
                    "structural": {"row_key_equals_id": src.get("row_key") == item_id},
                }
            )
    summary = {"per_schema": {str(k): v for k, v in sorted(per_schema.items())}}
    return rows, {"summary": summary, "excluded": excluded}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DATA / "ITEM_MASTER_v01.jsonl")
    parser.add_argument("--jsonl", type=Path, default=DATA / "ITEM_MASTER_v02.jsonl")
    parser.add_argument("--rules", type=Path, default=DATA / "ITEM_MASTER_v02_RULES.json")
    parser.add_argument("--audit", type=Path, default=AUDIT / "item_master_v02_audit.json")
    args = parser.parse_args()

    allowed = collect_candidates()
    identity = collect_identity(allowed)
    names = collect_names()
    shadow = {
        "belt_chip": board_ids(DATA / "boards" / "chip_item_catalog.json"),
        "nucleus": board_ids(DATA / "boards" / "nucleus_item_catalog.json"),
        "all_equips": board_ids(DATA / "boards" / "weapon_attrs_schema_static.json"),
    }
    base_rows = list(load_jsonl(args.base))
    new_rows, audit = build_new_rows(allowed, identity, names, shadow)

    merged: dict[int, dict[str, Any]] = {}
    for row in base_rows:
        merged[row["item_id"]] = row
    base_ids = set(merged)
    collisions = [row["item_id"] for row in new_rows if row["item_id"] in base_ids]
    for row in new_rows:
        merged.setdefault(row["item_id"], row)
    out_rows = [merged[k] for k in sorted(merged)]

    payload = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in out_rows)
    args.jsonl.write_text(payload, encoding="utf-8")
    jsonl_sha = sha256(args.jsonl)

    excluded = audit["excluded"]
    per = audit["summary"]["per_schema"]
    verified_new = len(new_rows)
    name_verified = sum(1 for r in new_rows if r["name_status"] == "verified")
    audit_doc = {
        "stage": "P4-A2",
        "artifact": args.jsonl.name,
        "jsonl_sha256": jsonl_sha,
        "base_rows": len(base_rows),
        "new_verified_rows": verified_new,
        "merged_rows": len(out_rows),
        "collisions_with_base": len(collisions),
        "name_verified": name_verified,
        "name_unresolved": verified_new - name_verified,
        "excluded_total": len(excluded),
        "excluded_by_state": dict(collections.Counter(e["identity_state"] for e in excluded)),
        "per_schema": per,
        "shadow_sets": {k: len(v) for k, v in shadow.items()},
        "shadow_hits": sum(len(v) for v in shadow.values()),
        "excluded": excluded,
        "negative_controls": {
            "row_key_equals_id_only": False,
            "integer_collision_only": False,
            "table_name_heuristic": False,
            "name_icon_presence": False,
            "foreign_reference_field": False,
            "foreign_entity_item_id": False,
            "sample_default_debug_id": False,
            "export_only_table": False,
            "unsafe_source": False,
            "circular_common_item_evidence": False,
            "dispatch_namespace_shadowed": True,
            "unsafe_name_slot": True,
        },
    }
    rules_doc = {
        "schema_version": 2,
        "artifact": args.jsonl.name,
        "jsonl_sha256": jsonl_sha,
        "base_artifact": {"path": args.base.name, "sha256": sha256(args.base), "rows": len(base_rows)},
        "evidence_policy": {
            "upgrade_block": "runtime consumer evidence",
            "required_chain": CONSUMER_CHAIN,
            "evidence": CONSUMER_EVIDENCE,
            "ancestor_policy_unchanged": "data/ITEM_MASTER_v01_RULES.json 的 anchor-only 政策不改动；v0.2 以 runtime consumer 证据升级，旧 artifact 的 business_id_allowed=false 保持不变，不追改。",
        },
        "scope": {
            "client": "test",
            "package": "Documents/script.py314.lc.npk",
            "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
            "FID": EXPECTED_FID,
            "entry": EXPECTED_ENTRY,
            "table": SOURCE_TABLE,
            "schemas": SCHEMAS,
            "candidate_rows": sum(v["candidates"] for v in per.values()),
            "server_branch": "unresolved",
        },
        "name_policy": {
            "source": "same-record NAME_CHAIN_CANDIDATES field_slot=4 name/primary/chain_state=verified/entity_name_allowed=True",
            "cross_table_name_join": False,
            "identity_independent_of_name": True,
            "unsafe_slot_example": "field_slot=6 (desc) 全 unsage，不充当 name",
        },
        "forbidden": [
            "同整数/row_key==id/唯一性单独证明 business identity",
            "foreign reference field 充当 identity",
            "被其它 dispatch namespace 遮蔽的 id 强行升级",
            "用 unsafe name slot 充当 name",
            "把 unresolved 行写进 artifact",
        ],
        "output_locks": {"jsonl": {"path": args.jsonl.name, "sha256": jsonl_sha}},
        "residuals": [
            "dispatch 顺序/numeric constant 未逐条证（opcode 级）",
            "get_item_type 实参绑定 = 形参级",
        ],
    }
    args.rules.write_text(json.dumps(rules_doc, ensure_ascii=False, indent=1), encoding="utf-8")
    args.audit.write_text(json.dumps(audit_doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: audit_doc[k] for k in ("base_rows", "new_verified_rows", "merged_rows", "collisions_with_base", "name_verified", "name_unresolved", "excluded_total", "excluded_by_state")}, ensure_ascii=False, indent=1))
    for schema in SCHEMAS:
        print(" ", schema, per[str(schema)])
    print("jsonl sha256", jsonl_sha)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
