# -*- coding: utf-8 -*-
"""w3_weapon_verify.py — 武器皮肤 质检与溯源报告（fail-closed）

红灯（exit 1）：GLB 头非法 / viewer 引用缺失或非法 GLB /
              保真标注不在契约允许集 / 有 viewer 却 0 合法 GLB
黄灯（记录）：无 viewer.json（白模无预览配置，覆盖率缺口）/
              source_evidence=unresolved（c159 映射缺失，溯源缺口）/
              GLB 内嵌设备绝对路径（可移植性缺口）

★ 不改写任何生产产物，不伪造 locator_chain。
用法：
  python w3_weapon_verify.py            # 写 state/render3d/weapon_verify_report.json
"""
from __future__ import annotations

import argparse
import json
import sys

from r3d_core import (
    WEAPON_INVENTORY, WEAPON_VERIFY_REPORT,
    contract, ensure_state, read_json, write_json_idempotent,
)


def main() -> int:
    ap = argparse.ArgumentParser(description="武器皮肤 · 质检与溯源报告")
    args = ap.parse_args()

    ensure_state()
    c = contract()
    fid_levels = set(c["fidelity"]["levels"])
    inv = read_json(WEAPON_INVENTORY)

    records = inv["records"]
    red, yellow = [], []
    per = []
    for r in records:
        entry = {"skin_id": r["skin_id"], "red": [], "yellow": []}
        # 红：GLB 头非法
        for g in r["glbs"]:
            if not g["valid"]:
                entry["red"].append("GLB %s 头非法（损坏/非 glTF2）" % g["file"])
        # 红：viewer 引用缺失/非法
        for m in r["missing_models"]:
            entry["red"].append("viewer 引用 %s 不在目录内" % m)
        # 红：保真标注非法
        if r["fidelity"] and r["fidelity"] not in fid_levels:
            entry["red"].append("保真标注 %r 不在契约允许集 %s" % (r["fidelity"], sorted(fid_levels)))
        # 红：有 viewer 却 0 合法 GLB
        if r["has_viewer"] and not any(g["valid"] for g in r["glbs"]):
            entry["red"].append("有 viewer.json 但目录内 0 合法 GLB")
        # 黄：无 viewer（覆盖率缺口）
        if not r["has_viewer"]:
            entry["yellow"].append("无 viewer.json（白模无预览配置）")
        # 黄：溯源缺失
        sev = r["source_evidence"]
        if sev.get("status") != "linked":
            entry["yellow"].append("源证据 %s（%s）" % (sev.get("status"), sev.get("reason", "")))
        # 黄：GLB 内嵌绝对路径（可移植性）
        for g in r["glbs"]:
            if g.get("abs_path"):
                entry["yellow"].append("GLB %s 内嵌设备绝对路径（可移植性缺口）" % g["file"])
                break
        if entry["red"]:
            red.append((r["skin_id"], entry["red"]))
        if entry["yellow"]:
            yellow.append((r["skin_id"], entry["yellow"]))
        per.append(entry)

    # 共享/基础设施 GLB（骨骼/候选/根级）头校验
    shared = inv.get("shared_assets", {})
    shared_invalid = []
    for cat, lst in shared.items():
        for g in lst:
            if not g["valid"]:
                shared_invalid.append((cat, g["rel"]))

    report = {
        "schema_version": 1, "scope": "research-prototype",
        "contract_version": c["version"],
        "summary": inv["summary"],
        "red_count": sum(len(x[1]) for x in red) + len(shared_invalid),
        "yellow_count": sum(len(x[1]) for x in yellow),
        "shared_invalid": [{"cat": cat, "rel": rel} for cat, rel in shared_invalid],
        "units": per,
        "known_gaps": c["fidelity"]["known_gaps"],
        "unresolved_note": (
            "武器目录名（如 1110013）与 c159 普查 skin_freq 键（skin_1007_007）"
            "是两套 ID 体系，无现成映射，故 source_evidence 默认 unresolved；"
            "不臆造关联。源证据要打通需建立 目录名↔c159 skin 的对照表。"),
    }
    write_json_idempotent(WEAPON_VERIFY_REPORT, report, True, "weapon_verify_report.json")

    print("== 武器皮肤 verify ==")
    print("   体检 %d 目录 + 共享资产  红灯 %d  黄灯 %d" % (
        len(records), report["red_count"], report["yellow_count"]))
    print("   GLB 合法 %d / 非法 %d；有 viewer %d / 无 viewer %d" % (
        inv["summary"]["glb_valid"], inv["summary"]["glb_invalid"],
        inv["summary"]["dirs_with_viewer"], inv["summary"]["dirs_without_viewer"]))
    for sid, msgs in red:
        for m in msgs:
            print("   [RED ] %s %s" % (sid, m))
    for cat, rel in shared_invalid:
        print("   [RED ] 共享/%s %s GLB 头非法" % (cat, rel))
    if yellow:
        print("   [YEL ] 共 %d 条（覆盖率/溯源/可移植性缺口，非产物错误）" % report["yellow_count"])
    return 1 if red else 0


if __name__ == "__main__":
    sys.exit(main())
