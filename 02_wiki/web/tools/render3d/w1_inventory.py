# -*- coding: utf-8 -*-
"""w1_inventory.py — 武器皮肤 资产清单 / 溯源基线（只读扫描 → 幂等落盘）

★ 这是「可复用流水线」的第二条线（时装见 s1_roster.py）。
  复用同一套 r3d_core  machinery：glb_chunks / evidence / write_json_idempotent。
★ 只读 assets/3d/weapon_skin/ 与 30_分析/_fashion3d/weapon_c159_material_survey.json，
  绝不改写任何生产产物。
★ 溯源铁律：拿不到证据标 unresolved，绝不臆造 locator_chain。
  已知事实：武器目录名（如 1110013）与 c159 普查 skin_freq 键（skin_1007_007）
  是两套 ID 体系，无现成映射 ⇒ 默认 source_evidence=unresolved_no_mapping。

用法：
  python w1_inventory.py            # dry-run，写 state（不碰生产）
  python w1_inventory.py --apply    # 落盘 state（仍为运行态，非生产产物）
"""
from __future__ import annotations

import argparse
import collections
import json
import sys

from r3d_core import (
    C159_SURVEY, RULES_FILE, WEAPON_3D, WEAPON_INVENTORY,
    abs_path_present, contract, ensure_state, fidelity_levels,
    glb_chunks, read_json, sha256_file, write_json_idempotent,
)

SCHEMA = 1


def load_survey():
    """加载 c159 普查，建立 skin 令牌 → 涉及行 的索引（best-effort 溯源）。"""
    if not C159_SURVEY.exists():
        return None
    d = read_json(C159_SURVEY)
    skin_to_rows = collections.defaultdict(list)
    for i, row in enumerate(d.get("rows", [])):
        for tok in (row.get("skins") or []):
            skin_to_rows[tok].append(i)
    return {
        "survey": d,
        "skin_freq": d.get("skin_freq", {}),
        "skin_to_rows": skin_to_rows,
    }


def source_evidence(skin_id: str, sv) -> dict:
    """best-effort 把 viewer.skin_id 关联到 c159 普查。关联不上 ⇒ 如实 unresolved。"""
    if sv is None:
        return {"status": "unresolved", "reason": "c159 普查缺失"}
    if skin_id in sv["skin_freq"]:
        rows = [sv["survey"]["rows"][i] for i in sv["skin_to_rows"].get(skin_id, [])]
        shaders = sorted({s for r in rows for s in (r.get("shaders") or [])})
        cubes = [c for r in rows for c in (r.get("cubes") or [])]
        return {
            "status": "linked", "c159_docs": len(rows),
            "shaders": shaders[:8], "cube_present": bool(cubes),
            "transparent_mode": any("TransparentMode" in (r.get("materials") or []) for r in rows),
        }
    if skin_id in sv["skin_to_rows"]:
        rows = [sv["survey"]["rows"][i] for i in sv["skin_to_rows"][skin_id]]
        shaders = sorted({s for r in rows for s in (r.get("shaders") or [])})
        cubes = [c for r in rows for c in (r.get("cubes") or [])]
        return {
            "status": "linked", "c159_docs": len(rows),
            "shaders": shaders[:8], "cube_present": bool(cubes),
            "transparent_mode": any("TransparentMode" in (r.get("materials") or []) for r in rows),
        }
    return {"status": "unresolved", "reason": "no_c159_id_mapping（目录名与 skin_freq 键不同体系）"}


def main() -> int:
    ap = argparse.ArgumentParser(description="武器皮肤 · 资产清单 / 溯源基线")
    ap.add_argument("--apply", action="store_true", help="落盘 state（默认 dry-run）")
    args = ap.parse_args()

    ensure_state()
    c = contract()
    fid_levels = set(fidelity_levels(c))
    sv = load_survey()

    if not WEAPON_3D.exists():
        raise SystemExit("❌ 找不到武器资产目录：%s" % WEAPON_3D)

    records, no_viewer = [], []
    glb_total = glb_valid = glb_invalid = 0
    fid_dist = collections.Counter()
    src_dist = collections.Counter()

    for d in sorted(p for p in WEAPON_3D.iterdir() if p.is_dir() and not p.name.startswith("_")):
        sid = d.name
        vj_path = d / "viewer.json"
        has_viewer = vj_path.exists()
        vj = json.loads(vj_path.read_text(encoding="utf-8")) if has_viewer else None

        glbs = sorted(d.rglob("*.glb"))
        glb_info = []
        dir_invalid = False
        for g in glbs:
            rel = str(g.relative_to(d))
            info = glb_chunks(g)
            valid = info["valid"]
            glb_total += 1
            if valid:
                glb_valid += 1
            else:
                glb_invalid += 1
                dir_invalid = True
            glb_info.append({
                "file": rel, "valid": valid,
                "json_only": bool(info.get("json_only", False)),
                "bytes": g.stat().st_size,
                "sha256": sha256_file(g),
                "abs_path": abs_path_present(g) if valid else None,
            })

        models_ref = []
        fidelity = None
        ml_status = None
        if vj is not None:
            models_ref = [s.get("model") for s in vj.get("states", []) if s.get("model")]
            fidelity = (vj.get("fidelity") or {}).get("material")
            ml_status = (vj.get("material_layers") or {}).get("status")

        present_names = {g["file"] for g in glb_info}
        present_basenames = {str(p).split("/")[-1] for p in present_names}
        missing_models = [m for m in models_ref if m not in present_basenames]

        sev = source_evidence(sid, sv)
        src_dist[sev["status"]] += 1
        if fidelity:
            fid_dist[fidelity] += 1

        if not has_viewer:
            no_viewer.append(sid)

        # 状态判定（fail-closed）
        if dir_invalid:
            status = "invalid_glb"
        elif has_viewer and missing_models:
            status = "missing_model"
        elif has_viewer and not glb_info:
            status = "empty_dir"
        elif has_viewer:
            status = "ok"
        else:
            status = "white_model_no_viewer"

        records.append({
            "skin_id": sid,
            "has_viewer": has_viewer,
            "viewer": ({"skin_id": vj.get("skin_id"), "states": vj.get("states"),
                        "fidelity": vj.get("fidelity"), "material_layers_status": ml_status}
                       if vj is not None else None),
            "models_referenced": models_ref,
            "missing_models": missing_models,
            "glbs": glb_info,
            "fidelity": fidelity,
            "source_evidence": sev,
            "status": status,
        })

    summary = {
        "dirs": len(records),
        "dirs_with_viewer": sum(1 for r in records if r["has_viewer"]),
        "dirs_without_viewer": len(no_viewer),
        "glb_total": glb_total, "glb_valid": glb_valid, "glb_invalid": glb_invalid,
        "fidelity_dist": dict(fid_dist),
        "source_evidence_dist": dict(src_dist),
        "status_dist": dict(collections.Counter(r["status"] for r in records)),
    }

    # ── 共享 / 基础设施资产（_ 前缀目录 + 根级 glb）：骨骼 / 候选变体 / 模板
    #   单独扫描并纳入头校验，使全部 379 个 GLB 都对口，不遗漏。
    shared = {"skeletons": [], "candidate": [], "root": [], "other": []}
    shared_total = shared_valid = shared_invalid = 0
    for entry in WEAPON_3D.iterdir():
        if entry.is_dir() and entry.name.startswith("_"):
            cat = ("skeletons" if entry.name == "_skeletons" else
                   "candidate" if entry.name.startswith("_cand") else "other")
            for g in sorted(entry.rglob("*.glb")):
                info = glb_chunks(g)
                shared[cat].append({
                    "file": g.name, "rel": str(g.relative_to(WEAPON_3D)),
                    "valid": info["valid"], "bytes": g.stat().st_size,
                    "sha256": sha256_file(g),
                })
        elif entry.is_file() and entry.suffix.lower() == ".glb":
            info = glb_chunks(entry)
            shared["root"].append({
                "file": entry.name, "rel": entry.name,
                "valid": info["valid"], "bytes": entry.stat().st_size,
                "sha256": sha256_file(entry),
            })
    for cat, lst in shared.items():
        for rec in lst:
            shared_total += 1
            shared_valid += 1 if rec["valid"] else 0
            shared_invalid += 0 if rec["valid"] else 1
    summary["shared_glb_total"] = shared_total
    summary["shared_glb_invalid"] = shared_invalid
    summary["shared_by_dir"] = {k: len(v) for k, v in shared.items()}
    summary["grand_glb_total"] = glb_total + shared_total
    summary["grand_glb_invalid"] = glb_invalid + shared_invalid
    out = {
        "schema_version": SCHEMA, "scope": "research-prototype",
        "contract_sha256": sha256_file(RULES_FILE),
        "c159_survey_sha256": sha256_file(C159_SURVEY) if C159_SURVEY.exists() else None,
        "fidelity_levels_allowed": sorted(fid_levels),
        "summary": summary,
        "records": records,
        "shared_assets": shared,
        "coverage_gap": {"no_viewer_dirs": no_viewer},
    }

    print("== 武器皮肤 inventory ==")
    print("   目录 %d（有 viewer %d / 无 viewer %d）" % (
        summary["dirs"], summary["dirs_with_viewer"], summary["dirs_without_viewer"]))
    print("   GLB 逐皮肤 %d（合法 %d / 非法 %d） + 共享/基础设施 %d（非法 %d）"
          " ⇒ 总计 %d" % (
        summary["glb_total"], summary["glb_valid"], summary["glb_invalid"],
        summary["shared_glb_total"], summary["shared_glb_invalid"],
        summary["grand_glb_total"]))
    print("   共享资产分布 %s" % summary["shared_by_dir"])
    print("   保真分布 %s" % dict(fid_dist))
    print("   源证据分布 %s" % dict(src_dist))
    print("   状态分布 %s" % summary["status_dist"])
    if glb_invalid or shared_invalid:
        bad = [r["skin_id"] for r in records if r["status"] == "invalid_glb"]
        print("   ⚠ 非法 GLB 目录 %d：%s" % (len(bad), ", ".join(bad[:20])))
    if no_viewer:
        print("   ⚠ 无 viewer.json（白模无预览配置）%d 个，首条：%s" % (
            len(no_viewer), ", ".join(no_viewer[:20])))

    # weapon_inventory.json 属流水线运行态（非生产产物），dry-run 与 --apply 均写入，
    # 以便 weapon_verify 链式读取；生产 GLB 不被本脚本改写。
    write_json_idempotent(WEAPON_INVENTORY, out, True, "weapon_inventory.json")
    return 1 if glb_invalid else 0


if __name__ == "__main__":
    sys.exit(main())
