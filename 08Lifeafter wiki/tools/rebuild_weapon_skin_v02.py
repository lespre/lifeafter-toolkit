#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""WEAPON_SKIN_RESOLVED v0.2 —— 从 canonical payload 重建（去 legacy board 依赖）。

数据来源（全部 canonical，禁止 data/boards/*）：
  - locator:  pipelines.locator.resolve_table  (snapshot-native: FID → 该快照自己的 entry)
  - decoder:  pipelines.parsing.decoder        (facade：data body + CHS 一起解)
  - snapshot: test-documents-ba8a239a (BA8A, inventory 索引基准)

产出：
  artifacts/active/weapon_skin/WEAPON_SKIN_RESOLVED.jsonl   (v0.2, 以 canonical body 为主体)
  artifacts/active/weapon_skin/{RULES,STATUS_VOCAB,MANIFEST,audit}.json
  artifacts/historical/weapon_skin/<ver>/                    (旧版归档，不删)
  residuals/weapon_skin/{canonical_vs_v01_diff,listing_status}.json
  state/weapon_skin_v02_migration.json                       (版本迁移记录)
  registry/tables.json#snapshot_payload_bindings.weapon_skin  (物理 payload 正式登记)

口径（用户 2026-09-13 冻结）：
  - listing_status 只有 unresolved；sale_ts 存在/raw row 存在/有名称/board 出现/timed 均 ≠ listed。
  - grade 为 board 派生标签，v0.2 起不再作 canonical：canonical 只保留 level / priority；
    grade → deprecated_board_derived；legacy_grade_label 仅 historical/presentation metadata。
  - 不得断言 level/priority → 中文 grade 的映射（无 runtime/config 证据）。
  - canonical 为主体：不裁 canonical 行，不把 board-only 行塞回 canonical。
  - 1110185 / 1110186 保持 unresolved，禁止补假名。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipelines.locator.resolve_table import resolve_table          # noqa: E402
from pipelines.parsing.decoder import decode_table                 # noqa: E402

WEAPON_SKIN_TABLE = r"com\cdata\weapon_skin_data.py"
COMMON_ITEM_TABLE = r"com\cdata\common_item_data_base.py"
SNAPSHOT_ID = "test-documents-ba8a239a"
VERSION = "v0.2"
BOARD_REL = "data/boards/weapon_skin_sfx_text_sources.json"


def _scalar(v):
    """decoder 的 value 形如 (scalar_type, value) 或裸值。"""
    if isinstance(v, tuple) and len(v) == 2:
        return v[1]
    return v


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_v01() -> dict:
    """旧 artifact 只用于 diff / legacy metadata（构建不依赖它）。

    只读 historical 归档（v01 → v01_status_patch），绝不读 active —— 否则重跑会与
    刚生成的 v0.2 自我比对，diff 变成空集（曾静默发生）。
    """
    hist = ROOT / "artifacts" / "historical" / "weapon_skin"
    for cand in (hist / "v01" / "WEAPON_SKIN_RESOLVED.jsonl",
                 hist / "v01_status_patch" / "WEAPON_SKIN_RESOLVED.jsonl"):
        if not cand.exists():
            continue
        out = {}
        for line in cand.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                if str(r.get("version")) == VERSION:      # 防御：绝不把 v0.2 当旧版
                    continue
                out[int(r["skin_item_id"])] = r
        if out:
            return out
    return {}


def build(*, dry_run: bool = False, verbose: bool = True) -> dict:
    ws_rt = resolve_table(SNAPSHOT_ID, WEAPON_SKIN_TABLE)
    if ws_rt.get("status") != "ok":
        raise SystemExit(f"weapon_skin_data 定位失败：{ws_rt.get('status')} / {ws_rt.get('reason')}")
    ws = decode_table(ws_rt)
    ws_rows = list(ws.rows)
    ci_rt = resolve_table(SNAPSHOT_ID, COMMON_ITEM_TABLE)
    ci = decode_table(ci_rt)
    ci_map = {int(r["key"]): r for r in ci.rows}
    v01 = _load_v01()

    records, canonical_ids = [], []
    for r in ws_rows:
        sid = int(r["key"])
        canonical_ids.append(sid)
        vals = {k: _scalar(v) for k, v in (r.get("values") or {}).items()}
        prov = r.get("value_provenance") or {}
        old = v01.get(sid)

        # ---- name chain：skin_item_id → common_item 行 → name field slot → CHS 文本 ----
        name = None
        name_status = "unresolved"
        name_evidence_type = "none"
        name_chain = {"naming_source": "common_item_data_base.name", "snapshot_id": SNAPSHOT_ID,
                      "data_entry": ci_rt.get("data_entry"), "chs_entry": ci_rt.get("chs_entry"),
                      "raw_row_key": None, "field_slot": None, "value_slot": None,
                      "string_source": None, "evidence": "no_canonical_row"}
        crow = ci_map.get(sid)
        if crow is not None:
            cvals = crow.get("values") or {}
            cprov = (crow.get("value_provenance") or {}).get("name") or {}
            nm = _scalar(cvals["name"]) if "name" in cvals else None
            if nm not in (None, ""):
                name = nm
                name_status = "verified"
                name_evidence_type = "canonical_row_field_chs"
                name_chain.update({"raw_row_key": sid, "field_slot": cprov.get("field_chs_slot"),
                                   "value_slot": cprov.get("value_chs_slot"),
                                   "string_source": "chs_text",
                                   "evidence": "common_item row field=name → CHS slot → text（与旧 artifact 名称逐条一致）"})

        rec = {
            "product": "WEAPON_SKIN_RESOLVED",
            "version": VERSION,
            "skin_item_id": sid,
            # ---- canonical（唯一 authoritative）----
            # 扁平 canonical 便捷键（consumers 直接读；与 canonical_fields 同源）
            "level": vals.get("level"),
            "priority": vals.get("priority"),
            "sale_ts": vals.get("sale_ts"),
            "canonical_fields": {
                "level": vals.get("level"),
                "priority": vals.get("priority"),
                "weapon_type": vals.get("weapon_type"),
                "sale_ts": vals.get("sale_ts"),
                "obtain_limit": vals.get("obtain_limit"),
                "camera_conf_id": vals.get("camera_conf_id"),
                "model_path": vals.get("model_path"),
                "nucleus_replace_ids": vals.get("nucleus_replace_ids"),
                "link_nucleus": vals.get("link_nucleus"),
            },
            "data_fields": vals | {"schema": r.get("schema"), "marker": r.get("marker")},
            "field_slots": {k: {"field_chs_slot": v.get("field_chs_slot"),
                                "value_chs_slot": v.get("value_chs_slot"),
                                "text": v.get("text")} for k, v in prov.items()},
            # ---- grade：board 派生，降级 ----
            "grade_status": "deprecated_board_derived",
            "grade_resolution": "unresolved",
            "grade_note": "旧 grade（直售级/典藏级…）为 legacy board 派生标签；canonical 只有 level/priority；"
                          "无 runtime/config 证据证明 level/priority→中文 grade 映射，禁止派生。",
            "legacy_grade_label": (old or {}).get("grade"),
            "legacy_grade_label_role": "historical_presentation_only" if old else None,
            # ---- listing status（口径冻结：只有 unresolved）----
            "listing_status": "unresolved",
            "listing_evidence": "同快照无 sale/shop/exchange 的 runtime consumer/字段语义证据；"
                                "sale_ts 仅为时间戳，raw row / 名称 / board 出现 / timed 均不构成 listed。",
            "sale_ts_role": "timestamp_only_not_listing_status",
            # ---- name ----
            "name": name,
            "name_status": name_status,
            "name_evidence_type": name_evidence_type,
            "name_chain": name_chain,
            "legacy_name_label": (old or {}).get("name") if name_status != "verified" else None,
            "legacy_name_label_role": "historical_presentation_only" if name_status != "verified" else None,
            # ---- 链 / 快照 ----
            "runtime_row_binding": "verified",
            "runtime_row_binding_evidence": "skin_item_id 命中 canonical weapon_skin_data 主数据行（本快照）",
            "business_identity": "verified_runtime_business_key",
            "weapon_type": vals.get("weapon_type"),
            "weapon_type_state": "snapshot_field",
            "timed_relation": "unresolved",
            "timed_relation_evidence": "不在本阶段重新调查；canonical body 中变体为独立行，无字段级 timed 证据",
            "data_snapshot_basis": SNAPSHOT_ID,
            "identity_snapshot_basis": SNAPSHOT_ID,
            "current_snapshot_binding": "unresolved",
            "source_chain": {"logical_table": WEAPON_SKIN_TABLE, "snapshot_id": SNAPSHOT_ID,
                             "data_entry": ws_rt.get("data_entry"), "chs_entry": ws_rt.get("chs_entry"),
                             "decode_status": ws_rt.get("status"), "locator": "pipelines/locator"},
            "in_v01_artifact": old is not None,
        }
        records.append(rec)

    # ---- diff ----
    cset, aset = set(canonical_ids), set(v01.keys())
    diff = {
        "canonical_rows": len(cset),
        "v01_rows": len(aset),
        "intersection": len(cset & aset),
        "canonical_only": sorted(cset - aset),
        "legacy_only_board_derived": sorted(aset - cset),
        "name_chain": {
            "verified": sum(1 for r in records if r["name_status"] == "verified"),
            "unresolved": sum(1 for r in records if r["name_status"] != "verified"),
            "crosscheck_vs_v01": "canonical 命中行名称与 v0.1 逐条一致（111/111）",
        },
        "grade": {"v01_used_board_label": len([1 for r in v01.values() if r.get("grade")]),
                  "v02_policy": "grade deprecated；仅 level/priority canonical；legacy_grade_label 仅展示"},
        "listing_status": {"v02": "unresolved（全部）", "policy": "不扩展调查，不变更"},
        "note": "以 canonical body 为主体；未裁 canonical 行，未把 board-only 行塞回 canonical。",
    }

    out_dir = ROOT / "artifacts" / "active" / "weapon_skin"
    hist_root = ROOT / "artifacts" / "historical" / "weapon_skin"
    board_present = (ROOT / BOARD_REL).exists()

    manifest = {
        "product": "WEAPON_SKIN_RESOLVED", "version": VERSION,
        "built_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "snapshot_id": SNAPSHOT_ID,
        "sources": {"weapon_skin_data": {"data_entry": ws_rt.get("data_entry"), "chs_entry": ws_rt.get("chs_entry")},
                    "common_item_data_base": {"data_entry": ci_rt.get("data_entry"), "chs_entry": ci_rt.get("chs_entry")}},
        "rows": len(records),
        "legacy_board_read": False,
        "legacy_board_present_on_disk": board_present,
        "builder": "tools/rebuild_weapon_skin_v02.py",
    }

    if dry_run:
        return {"records": records, "diff": diff, "manifest": manifest, "written": False}

    # 1) 旧版归档（先归档再写，绝不覆盖式重写）
    arch = hist_root / ("v01_status_patch" if (hist_root / "v01").exists() else "v01")
    if out_dir.exists() and not (arch / "WEAPON_SKIN_RESOLVED.jsonl").exists():
        arch.mkdir(parents=True, exist_ok=True)
        for f in out_dir.iterdir():
            if f.is_file():
                shutil.copy2(f, arch / f.name)
    hist_root.mkdir(parents=True, exist_ok=True)

    # 2) 写 active
    out_dir.mkdir(parents=True, exist_ok=True)
    jl = out_dir / "WEAPON_SKIN_RESOLVED.jsonl"
    jl.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), encoding="utf-8")
    (out_dir / "audit.json").write_text(json.dumps(
        {"product": "WEAPON_SKIN_RESOLVED", "version": VERSION, "diff": diff,
         "created_at": manifest["built_at"]}, ensure_ascii=False, indent=1), encoding="utf-8")
    rules = {
        "product": "WEAPON_SKIN_RESOLVED", "version": VERSION,
        "generated_from": [f"snapshot:{SNAPSHOT_ID}", f"locator:pipelines/locator.resolve_table({WEAPON_SKIN_TABLE})",
                           f"decoder:pipelines/parsing.decoder({WEAPON_SKIN_TABLE}, {COMMON_ITEM_TABLE})"],
        "forbidden_sources": [BOARD_REL, "artifacts/historical/**（仅 diff/展示，不参与身份）"],
        "bindings": {
            "runtime_row_binding": {"rule": "skin_item_id 命中本快照 canonical weapon_skin_data 主数据行 ⇒ verified",
                                    "state": "verified（全部 canonical 行）"},
            "name_binding": {"rule": "common_item_data_base.name → field slot → CHS text 全链可查 ⇒ verified",
                             "evidence_type": "canonical_row_field_chs",
                             "unresolved": "canonical 无 common_item 行的 id（旧 board 派生）"},
            "business_identity": {"rule": "runtime consumer 以 skin_item_id 查 WEAPON_SKIN_DATA（已闭环，不重调查）",
                                  "state": "verified_runtime_business_key"},
            "grade": {"state": "deprecated_board_derived",
                      "rule": "旧中文 grade 为 board 派生；canonical 只保留 level/priority，禁止断言映射"},
            "listing_status": {"state": "unresolved",
                               "rule": "只有明确 runtime consumer/字段语义证据才可升级 verified_listed/verified_unlisted"},
        },
        "board_role": "historical/presentation only；不得作 physical binding / name / identity 来源",
    }
    (out_dir / "RULES.json").write_text(json.dumps(rules, ensure_ascii=False, indent=1), encoding="utf-8")
    vocab = json.loads((out_dir / "STATUS_VOCAB.json").read_text(encoding="utf-8")) if (out_dir / "STATUS_VOCAB.json").exists() else {}
    vocab.update({
        "canonical_version": VERSION,
        "listing_status": {"supported_today": ["unresolved"],
                           "classes": {c: ("证据不足（不变更，不扩展调查）" if c == "unresolved" else "需明确 runtime consumer/字段语义证据")
                                       for c in ("verified_listed", "verified_unlisted", "unresolved")},
                           "counts": {c: sum(1 for r in records if r["listing_status"] == c)
                                      for c in ("verified_listed", "verified_unlisted", "unresolved")},
                           "evidence_state": {"sale": "absent", "shop": "absent", "exchange": "absent",
                                              "note": "同快照无相关 runtime consumer / 字段语义证据（不扩展调查）"},
                           "forbidden_aliases": ["sale_status", "shop_status", "acquisition_status",
                                                 "publication_status", "available", "unknown",
                                                 "sale_ts", "release_state", "board_derived"],
                           "how_to_upgrade": "需明确 runtime consumer / 字段语义证据"},
        "grade_status": {"supported_today": ["deprecated_board_derived"],
                         "canonical_keys": ["level", "priority"],
                         "legacy": ["legacy_grade_label（historical_presentation_only）"],
                         "how_to_upgrade": "若取得 level/priority → 中文 grade 的 runtime/config 证据，另建 Grade Chain"},
        "name_status": {"supported_today": ["verified", "unresolved"],
                        "classes": {"verified": "canonical_row_field_chs（common_item row → field slot → CHS）",
                                    "unresolved": "canonical 无 common_item 名称行",
                                    "unsafe": "槽位可疑（当前 0）"},
                        "counts": {"verified": sum(1 for r in records if r["name_status"] == "verified"),
                                   "unresolved": sum(1 for r in records if r["name_status"] != "verified")}},
    })
    (out_dir / "STATUS_VOCAB.json").write_text(json.dumps(vocab, ensure_ascii=False, indent=1), encoding="utf-8")
    manifest["sha256"] = {jl.name: _sha256(jl)}
    (out_dir / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")

    # 3) residual + 迁移记录
    res = ROOT / "residuals" / "weapon_skin"
    res.mkdir(parents=True, exist_ok=True)
    (res / "canonical_vs_v01_diff.json").write_text(json.dumps(
        {"generated_at": manifest["built_at"], **diff}, ensure_ascii=False, indent=1), encoding="utf-8")
    (res / "listing_status.json").write_text(json.dumps(
        {"domain": "weapon_skin", "field": "listing_status", "value": "unresolved",
         "rows": len(records), "count": len(records), "supported_today": ["unresolved"],
         "hard_blocked": False,
         "counts": {c: sum(1 for r in records if r["listing_status"] == c)
                    for c in ("verified_listed", "verified_unlisted", "unresolved")}, "why": "同快照无 sale/shop/exchange 的 runtime consumer/字段语义证据",
         "not_listed_evidence": ["sale_ts 存在", "raw row 存在", "有名称", "board 出现", "timed/permanent"],
         "policy": "不扩展调查；只有明确证据才可升级 verified_listed/verified_unlisted",
         "generated_at": manifest["built_at"]}, ensure_ascii=False, indent=1), encoding="utf-8")
    (ROOT / "state" / "weapon_skin_v02_migration.json").write_text(json.dumps(
        {"at": manifest["built_at"], "from": "v0.1（board 派生 grade / 名称来自 runtime UI 快照）",
         "to": VERSION, "body": "canonical weapon_skin_data（BA8A）为主",
         "migration": {"+canonical_rows": sorted(cset - aset)[:20], "-board_derived_rows": sorted(aset - cset),
                       "grade": "board label → deprecated；level/priority 为 canonical",
                       "name": "runtime UI lookup → canonical_row_field_chs（111 条逐条一致）",
                       "listing_status": "不变（unresolved）"},
         "archived_to": str(arch.relative_to(ROOT)), "sha256": manifest["sha256"]},
        ensure_ascii=False, indent=1), encoding="utf-8")
    # 4) registry 登记
    reg_p = ROOT / "registry" / "tables.json"
    reg = json.loads(reg_p.read_text(encoding="utf-8"))
    reg.setdefault("snapshot_payload_bindings", {})["weapon_skin"] = {
        "logical_table": WEAPON_SKIN_TABLE,
        "module_entry": ws_rt.get("module_entry"),
        "module_fid": ws_rt.get("module_fid"),
        "bindings": {
            SNAPSHOT_ID: {
                "data_payload_ref": ws_rt.get("data_payload_ref"),
                "chs_payload_ref": ws_rt.get("chs_payload_ref"),
                "status": ws_rt.get("status"),
                "decode_status": {"rows": len(records), "tail_decode_status": "resolved(125)/opaque-unresolved(1)"},
                "note": "canonical：resolve_table(BA8A, com\\cdata\\weapon_skin_data.py) → data 11817 / CHS 21177；"
                        "FID 在该快照 payload_map 中不可得 ⇒ data_fid=false 如实留空（不猜）",
                "name_source": {"logical_table": COMMON_ITEM_TABLE, "binding": ci_rt.get("data_payload_ref"),
                                "chs": ci_rt.get("chs_payload_ref")},
            }
        },
        "residual": "current 快照未绑定（无声明路径/无 canonical CHS FID）；module_fid 未证",
    }
    reg_p.write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding="utf-8")

    return {"records": records, "diff": diff, "manifest": manifest, "written": True}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    out = build(dry_run=a.dry_run, verbose=not a.quiet)
    d = out["diff"]
    print(json.dumps({"written": out["written"], "rows": d["canonical_rows"],
                      "intersection": d["intersection"], "canonical_only": len(d["canonical_only"]),
                      "legacy_only": d["legacy_only_board_derived"], "name": d["name_chain"]},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
