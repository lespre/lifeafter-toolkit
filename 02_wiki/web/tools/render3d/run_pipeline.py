# -*- coding: utf-8 -*-
"""run_pipeline.py — 3D 资产流水线编排器（CLI 约定对齐 build_pipeline.py）

  python run_pipeline.py --check                    # 查看方针/阶段/路径/待定口径
  python run_pipeline.py                           # dry-run 时装全流程（不触碰正式产物）
  python run_pipeline.py --apply                   # 时装真正落盘
  python run_pipeline.py --stage roster,verify     # 只跑指定阶段
  python run_pipeline.py --mode index --survey     # 扩量评估（仍 dry-run）
  python run_pipeline.py --only 3715_f --apply     # 指定套
  python run_pipeline.py --line weapon             # 武器线 质检+溯源基线（只读生产）
  python run_pipeline.py --line all                # 两条线都跑

退出码：0 全绿 / 1 阶段失败 / 2 规则或参数错误。
★ 默认 dry-run；--apply 才写正式产物。dry-run 会写 state/staging 中间区。
★ 不并入 rules/pipeline_graph.yml（那是板级重建顺序，语义不同）。
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys

from r3d_core import (
    ENV_DIR, PIPELINE_REPORT, ROSTER, RULES_FILE, STATE, VERIFY_REPORT,
    WEAPON_VERIFY_REPORT,
    contract, ensure_state, paths, read_json, write_json_idempotent,
)

HERE = pathlib.Path(__file__).resolve().parent
PY = ENV_DIR / "venv" / "Scripts" / "python.exe"
STAGE_ORDER = ["roster", "export", "verify"]
STAGE_TOOL = {"roster": "s1_roster.py", "export": "s2_export.py", "verify": "s3_verify.py"}
WEAPON_STAGES = ["weapon_inventory", "weapon_verify"]
WEAPON_TOOL = {"weapon_inventory": "w1_inventory.py", "weapon_verify": "w3_weapon_verify.py"}


def check(c: dict) -> int:
    print("== render3d 流水线 · 方针视图（只读）==")
    p = c["policy"]
    print("\n目标：%s" % " ".join(p["goal"].split()))
    print("边界：%s" % " ".join(p["boundary"].split()))
    print("\n纪律：")
    for x in p["principles"]:
        print("  · %s" % " ".join(x.split()))
    print("\n数据源 allow：")
    for x in c["data_sources"]["allow"]:
        print("  · %s" % x)
    print("  forbid：%s" % " / ".join(c["data_sources"]["forbid"][:2]))
    print("\n保真口径：default=%s，levels=%s" % (
        c["fidelity"]["default"], ",".join(c["fidelity"]["levels"])))
    print("已知硬缺口 %d 项：" % len(c["fidelity"]["known_gaps"]))
    for x in c["fidelity"]["known_gaps"]:
        print("  · %s" % " ".join(x.split()))
    print("\n阶段图（书写顺序 = 执行顺序）：")
    for s in c["stages"]:
        print("  %-8s %-16s → %s" % (s["id"], s["tool"], s["output"]))
    ws = c.get("weapon_stages") or []
    if ws:
        print("  武器线（复用 r3d_core machinery）：")
        for s in ws:
            print("  %-8s %-16s → %s" % (s["id"], s["tool"], s["output"]))
    print("\n路径（全部经 la_paths 派生）：")
    for k, v in paths().items():
        print("  %-15s %s" % (k, v))
    print("\n待用户判定口径（本轮未擅自定）：")
    for x in c["owner_decision_pending"]:
        print("  · %s" % " ".join(x.split()))
    print("\n建议推进顺序：① 把 c159 材质级参数接进生产 → ② 补 IBL cube → "
          "③ 时装第二 UV 定证 → ④ 普查扩量 → ⑤ TransparentMode 逐值统计 → "
          "⑥ GLB extras 路径归一化（需批准，会改既有产物）")
    return 0


def run_stage(name: str, args: argparse.Namespace) -> dict:
    tool = STAGE_TOOL.get(name) or WEAPON_TOOL[name]
    cmd = [str(PY), str(HERE / tool)]
    if args.apply:
        cmd.append("--apply")
    if args.only:
        cmd += ["--only"] + list(args.only)
    if name == "roster":
        cmd += ["--mode", args.mode]
        if args.survey:
            cmd.append("--survey")
    if name == "export" and args.reuse_cache:
        cmd.append("--reuse-cache")
    if name == "verify" and args.strict:
        cmd.append("--strict")
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    print("\n── %s ── %s" % (name, " ".join(cmd[1:])))
    r = subprocess.run(cmd, env=env, capture_output=False)
    return {"stage": name, "cmd": cmd[1:], "rc": r.returncode}


def main() -> int:
    ap = argparse.ArgumentParser(description="3D 资产流水线编排器")
    ap.add_argument("--check", action="store_true", help="只读方针/阶段/路径视图")
    ap.add_argument("--apply", action="store_true", help="真正落盘（默认 dry-run）")
    ap.add_argument("--line", choices=["fashion", "weapon", "all"], default="fashion",
                    help="跑哪条线：fashion(默认) / weapon / all")
    ap.add_argument("--stage", default=None, help="逗号分隔阶段（覆盖 --line 默认）")
    ap.add_argument("--mode", choices=["golden", "index"], default="golden")
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--survey", action="store_true", help="Stage 1 打印全量普查")
    ap.add_argument("--reuse-cache", action="store_true")
    ap.add_argument("--strict", action="store_true", help="Stage 3 把路径字面量差异也判红灯")
    args = ap.parse_args()

    c = contract()
    ensure_state()
    if args.check:
        return check(c)
    if not PY.exists():
        print("❌ 找不到项目 venv Python：%s" % PY)
        return 2

    ALL = STAGE_ORDER + WEAPON_STAGES
    if args.stage:
        stages = [s.strip() for s in args.stage.split(",") if s.strip()]
    elif args.line == "weapon":
        stages = list(WEAPON_STAGES)
    elif args.line == "all":
        stages = list(ALL)
    else:
        stages = list(STAGE_ORDER)
    bad = [s for s in stages if s not in ALL]
    if bad:
        print("❌ 未知阶段 %s；可用：%s" % (bad, ALL))
        return 2

    results = []
    for s in stages:
        res = run_stage(s, args)
        results.append(res)
        if res["rc"] != 0:
            print("❌ 阶段 %s 失败（rc=%d），后续阶段不再执行（fail-closed）" % (s, res["rc"]))
            break

    # 只有本次真的跑了 verify，才引用质检结论；否则留空，不拿旧结果冒充本次结果
    ran = [r["stage"] for r in results]
    fv = read_json(VERIFY_REPORT, default={}) if ("verify" in ran and VERIFY_REPORT.exists()) else {}
    wv = read_json(WEAPON_VERIFY_REPORT, default={}) if ("weapon_verify" in ran and WEAPON_VERIFY_REPORT.exists()) else {}
    verify = fv or wv
    report = {
        "schema_version": 1, "apply": args.apply, "mode": args.mode,
        "line": args.line,
        "stages": results,
        "all_pass": bool(results) and len(results) == len(stages) and all(r["rc"] == 0 for r in results),
        "red_count": verify.get("red_count"), "yellow_count": verify.get("yellow_count"),
        "golden_agreement": verify.get("golden_agreement"),
        "reproducible": verify.get("reproducible"),
        "weapon_red_count": wv.get("red_count"), "weapon_yellow_count": wv.get("yellow_count"),
        "scope": "research-prototype",
    }
    write_json_idempotent(PIPELINE_REPORT, report, True, "pipeline_report.json")
    rc = 0 if report["all_pass"] else 1
    print("\n== 流水线 %s · line=%s ==  red=%s yellow=%s golden=%s" % (
        "PASS" if rc == 0 else "FAIL", args.line, report["red_count"],
        report["yellow_count"], report["golden_agreement"]))
    if wv:
        print("   武器侧：red=%s yellow=%s" % (wv.get("red_count"), wv.get("yellow_count")))
    if not args.apply:
        print("（dry-run：正式产物未改动；加 --apply 才落盘）")
    return rc


if __name__ == "__main__":
    sys.exit(main())
