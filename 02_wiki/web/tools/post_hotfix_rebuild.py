#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""热更后自动重建：把「热更进树 → 板块全量重建 → manifest」串成一条命令。

用法：
  python post_hotfix_rebuild.py            # 全量重建（默认）
  python post_hotfix_rebuild.py --only lottery_periods,fashion_wardrobe
  python post_hotfix_rebuild.py --dry     # 只列出将执行哪些 builder

设计：
  · builder 清单唯一来源 = data/board_builders.json（board_id → builder）
  · 每个 builder 单独超时（默认 300s），失败不中断，最后汇总
  · 奖池流水线（多脚本串联）单独作为一步跑
  · 结尾统一跑 build_wiki.py，产出 manifest
  · 结果写 01_索引与产物/30_分析/热更后重建_<时间>.md
"""
from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
import time
from pathlib import Path

PROJ = Path(r"E:\la拆包项目")
WEB = PROJ / "02_wiki/web"
TOOLS = WEB / "tools"
PY = str(PROJ / "00_规范与工具/环境/venv/Scripts/python.exe")
OUT_DIR = PROJ / "01_索引与产物/30_分析"


def run(cmd: list[str], timeout: int) -> tuple[int, str]:
    t0 = time.time()
    try:
        r = subprocess.run(cmd, cwd=str(PROJ), capture_output=True, text=True,
                           encoding="utf-8", errors="ignore", timeout=timeout)
        tail = "\n".join([ln for ln in (r.stdout or "").splitlines() if ln.strip()][-3:])
        return r.returncode, f"{time.time()-t0:.0f}s | {tail[-300:]}"
    except subprocess.TimeoutExpired:
        return 124, f"超时 >{timeout}s"


def main() -> int:
    only = None
    for a in sys.argv[1:]:
        if a.startswith("--only=") or a == "--only":
            pass
    if "--only" in sys.argv:
        only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
    dry = "--dry" in sys.argv

    reg = json.loads((WEB / "data/board_builders.json").read_text(encoding="utf-8"))
    boards = reg.get("boards") or []

    steps: list[tuple[str, list[str], int]] = []
    for b in boards:
        bid = b.get("board_id")
        builder = (b.get("builder") or "").strip()
        if not builder or bid in ("damage_bonus_piecewise",):
            continue
        if only and bid not in only:
            continue
        p = PROJ / builder if "/" in builder else TOOLS / builder
        if not p.is_file():
            p = TOOLS / Path(builder).name
        if not p.is_file():
            continue
        if p.name == "lottery_pipeline.py":   # 已作为第 0 步跑过，避免重复
            continue
        steps.append((bid, [PY, "-u", str(p)], 300))

    # 前置链：merge_core_boards 依赖 nucleus.json（由 build_nucleus_board 生成）
    pre = TOOLS / "build_nucleus_board.py"
    if pre.is_file():
        steps.append(("前置:nucleus", [PY, "-u", str(pre)], 300))

    if not only or "lottery" in (only or set()):
        steps.insert(0, ("lottery_pipeline", [PY, "-u", str(TOOLS / "lottery_pipeline.py")], 900))

    if dry:
        print(f"将执行 {len(steps)} 步：")
        for bid, cmd, to in steps:
            print(f"  {bid:34s} {Path(cmd[-1]).name}  (timeout {to}s)")
        return 0

    results = []
    for bid, cmd, to in steps:
        print(f"▶ {bid} …", flush=True)
        rc, note = run(cmd, to)
        ok = "✓" if rc == 0 else "✗"
        print(f"  {ok} rc={rc} {note[:160]}", flush=True)
        results.append({"board": bid, "rc": rc, "note": note})

    # ★ 武器皮肤后处理链：重建只出数据，真名/官方描述/媒体要再叠一层
    POST = ["rebuild_weapon_skin_media.py", "attach_skin_posters.py", "fill_weapon_skin_media.py",
            "merge_skin_effect_show.py", "backfill_skin_official_desc.py"]
    for name in POST:
        p2 = TOOLS / name
        if not p2.is_file():
            continue
        print(f"▶ 后处理 {name} …", flush=True)
        rc, note = run([PY, "-u", str(p2)], 300)
        print(f"  {'✓' if rc == 0 else '✗'} rc={rc} {note[:120]}", flush=True)
        results.append({"board": f"post:{name}", "rc": rc, "note": note})

    print("▶ build_wiki …", flush=True)
    rc, note = run([PY, "-u", str(TOOLS / "build_wiki.py")], 900)
    results.append({"board": "build_wiki", "rc": rc, "note": note})
    print(f"  {'✓' if rc == 0 else '✗'} rc={rc} {note[:160]}", flush=True)

    ts = dt.datetime.now().strftime("%Y%m%d_%H%M")
    md = OUT_DIR / f"热更后重建_{ts}.md"
    lines = [f"# 热更后重建 {ts}", "", "| 步骤 | 结果 | 摘要 |", "|---|---|---|"]
    for r in results:
        lines.append(f"| `{r['board']}` | {'通过' if r['rc']==0 else '失败 rc=%d' % r['rc']} | {r['note'][:120].replace('|','/')} |")
    md.parent.mkdir(parents=True, exist_ok=True)
    md.write_text("\n".join(lines), encoding="utf-8")

    bad = [r["board"] for r in results if r["rc"] != 0]
    print(f"\n完成：{len(results)-len(bad)}/{len(results)} 通过；报告 {md.name}")
    if bad:
        print("失败：", ", ".join(bad))
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
