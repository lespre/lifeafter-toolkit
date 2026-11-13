# -*- coding: utf-8 -*-
"""s1_roster.py — Stage 1 资源清单（只读扫描 → 幂等落盘）

输入：rules/render3d.yml + 30_分析/_fashion3d/fashion_index.json + PE 还原树资源
输出：02_wiki/state/render3d/roster.json

★ 缺源标 missing，绝不补占位；无法判定标 unresolved 并写报告。
★ --mode index 扩量前强制跑 golden_set 全量一致率，不过就拒绝（exit 2）。
用法：
  python s1_roster.py                            # dry-run，golden 5 套
  python s1_roster.py --apply                   # 落盘
  python s1_roster.py --mode index --survey     # 全量索引评估（dry-run）
  python s1_roster.py --only 3715_f 3640_m      # 指定套
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys

from r3d_core import (
    FASHION_INDEX, PE_RES, PE_CHARACTER, ROSTER, RULES_FILE, STATE,
    contract, evidence, ensure_state, read_json, resolve_mesh, sha256_file,
    write_json_idempotent,
)
from r3d_rules import (
    build_specs_from_golden, build_specs_from_index, check_golden_agreement, survey,
)

SCHEMA = 1


def build_roster(mode: str, only: list | None, c: dict) -> tuple[dict, dict]:
    idx = read_json(FASHION_INDEX)
    if mode == "index":
        agree = check_golden_agreement(idx, c)
        if not agree["pass"]:
            raise SystemExit(
                "❌ 选型规则 golden 一致率 %s 未达 %s，拒绝扩量。\n"
                "   先修 r3d_rules.py 与 rules/render3d.yml 的 selection_rules。"
                % (agree["agreement"], agree["required"]))
        specs, audit = build_specs_from_index(idx, only)
    else:
        specs = build_specs_from_golden(c)
        if only:
            specs = [s for s in specs if s["id"] in only]
        audit = {}

    fid = c["fidelity"]["default"]
    wm = (c.get("white_model") or {})
    wm_enabled = bool(wm.get("enabled"))
    wm_exclude = set(wm.get("exclude_units") or [])
    units = []
    for s in specs:
        uid = s["id"]
        allow_white = wm_enabled and (uid not in wm_exclude)
        parts = []
        for pid, label, mesh_rel in s["parts"]:
            # ★ 选型候选再校验：桩/_shadow mesh 魔数不对，同级重解析；
            #   若几何体是 .gim（当前导出器不支持）则如实降级 gim_only，不顶替。
            final_rel, ev_mesh, mstatus, mreason = resolve_mesh(mesh_rel)
            mtg = (PE_CHARACTER / final_rel).with_suffix(".mtg")
            ev_mtg = evidence(mtg, PE_RES)
            mtg_missing = (mstatus == "ready" and ev_mtg["status"] != "ready")
            # ★ 白模政策（用户 2026-11-07 决策）：几何在 + 基础材质缺 ⇒ 仍标 ready，
            #   交由 s2_export 出白模；几何缺 / gim_only / 被 exclude ⇒ 维持 missing/unresolved。
            if mstatus == "ready" and (ev_mtg["status"] == "ready" or allow_white):
                pstatus = "ready"
            elif mstatus == "gim_only":
                pstatus = "unresolved"
            else:
                pstatus = "missing"
            parts.append({
                "part_id": pid, "label": label, "source_mesh": final_rel,
                "file": pid + ".glb", "status": pstatus,
                "mtg_missing": bool(mtg_missing),
                "mesh": ev_mesh, "mtg": ev_mtg, "mesh_note": mreason,
            })
        n_ready = sum(1 for p in parts if p["status"] == "ready")
        n_unres = sum(1 for p in parts if p["status"] == "unresolved")
        if n_ready == len(parts):
            ustatus = "ready"
        elif n_unres:
            ustatus = "unresolved"
        else:
            ustatus = "missing"
        units.append({
            "id": s["id"], "series": s["series"], "gender": s["gender"],
            "label": s["label"], "note": s["note"], "root": s["root"],
            "selection_basis": s["selection_basis"],
            "fidelity": fid, "status": ustatus,
            "parts": parts,
        })

    roster = {
        "schema_version": SCHEMA, "mode": mode, "scope": "research-prototype",
        "contract_sha256": sha256_file(RULES_FILE),
        "index_sha256": sha256_file(FASHION_INDEX),
        "fidelity_note": c["fidelity"]["rule"],
        "units": units,
        "summary": {
            "units": len(units),
            "units_ready": sum(1 for u in units if u["status"] == "ready"),
            "units_missing": sum(1 for u in units if u["status"] == "missing"),
            "units_unresolved": sum(1 for u in units if u["status"] == "unresolved"),
            "parts": sum(len(u["parts"]) for u in units),
            "parts_ready": sum(1 for u in units for p in u["parts"] if p["status"] == "ready"),
            "parts_missing": sum(1 for u in units for p in u["parts"] if p["status"] == "missing"),
            "parts_unresolved": sum(1 for u in units for p in u["parts"] if p["status"] == "unresolved"),
            "fidelity": fid,
        },
        "audit": audit,
    }
    return roster, agree_info(mode, idx, c, audit)


def agree_info(mode, idx, c, audit):
    return {
        "golden_agreement": check_golden_agreement(idx, c)["agreement"],
        "survey": survey(idx) if mode == "index" else None,
        "rule_audit": audit if mode == "index" else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Stage 1 · 3D 资源清单")
    ap.add_argument("--apply", action="store_true", help="真正落盘（默认 dry-run）")
    ap.add_argument("--mode", choices=["golden", "index"], default="golden")
    ap.add_argument("--only", nargs="*", default=None, help="只处理指定套 id")
    ap.add_argument("--survey", action="store_true", help="打印全量索引普查")
    args = ap.parse_args()

    c = contract()
    ensure_state()
    try:
        roster, info = build_roster(args.mode, args.only, c)
    except SystemExit as e:
        print(e)
        return 2

    s = roster["summary"]
    print("== Stage 1 roster  mode=%s ==" % args.mode)
    print("   套 %d（ready %d / missing %d / unresolved %d）  部件 %d（ready %d / missing %d / unresolved %d）" % (
        s["units"], s["units_ready"], s["units_missing"], s["units_unresolved"],
        s["parts"], s["parts_ready"], s["parts_missing"], s["parts_unresolved"]))
    print("   golden 一致率 %s" % info["golden_agreement"])
    # 扩量时上千套，只打前 5 条 + 全部缺源套，避免刷屏；缺源必须逐条如实列出
    units = roster["units"]
    show = units if len(units) <= 10 else units[:5]
    for u in show:
        miss = [p["part_id"] for p in u["parts"] if p["status"] != "ready"]
        print("   %-10s parts=%d %-8s %s" % (
            u["id"], len(u["parts"]), u["status"],
            ("缺源: " + ",".join(miss)) if miss else ""))
    if len(units) > 10:
        bad = [u for u in units if u["status"] != "ready"]
        n_miss = sum(1 for u in bad if u["status"] == "missing")
        n_unr = sum(1 for u in bad if u["status"] == "unresolved")
        print("   … 其余 %d 套省略；非 ready %d 套（缺源 %d / 几何体为 .gim 未支持 %d）："
              % (len(units) - 5, len(bad), n_miss, n_unr))
        for u in bad[:30]:
            miss = [p["part_id"] for p in u["parts"] if p["status"] == "missing"]
            unr = [p["part_id"] for p in u["parts"] if p["status"] == "unresolved"]
            tag = ("缺源:" + ",".join(miss)) if miss else ""
            if unr:
                tag += (("；" if tag else "") + "gim未支持:" + ",".join(unr))
            print("      %-10s %s" % (u["id"], tag))
        if len(bad) > 30:
            print("      … 另有 %d 套，完整清单见 roster.json" % (len(bad) - 30))
    if info["survey"]:
        sv = info["survey"]
        print("   全量组 %d → 可判定 %d / unresolved %d / 跨容器串号排除 %d" % (
            sv["groups_total"], sv["groups_selected"],
            sv["groups_unresolved"], sv["excluded_cross_container"]))
    if args.survey and not info["survey"]:
        print(json.dumps(survey(read_json(FASHION_INDEX)), ensure_ascii=False, indent=1))

    # roster.json 属流水线运行态（非生产产物），dry-run 与 --apply 均写入，
    # 以便下游阶段（export/verify）链式读取；只有 FASHION_3D 的 GLB 才由 --apply 门控。
    write_json_idempotent(ROSTER, roster, True, "roster.json")
    print("   roster.json 已写入 state（运行态；生产 GLB 仍由 --apply 门控）")
    if s["units_missing"] or s["units_unresolved"]:
        print("⚠ 非 ready 套：%d 缺源(missing) / %d 几何体为 .gim 未支持(unresolved)；"
              "如实保留标记，Stage 2 将跳过，不顶替。"
              % (s["units_missing"], s["units_unresolved"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
