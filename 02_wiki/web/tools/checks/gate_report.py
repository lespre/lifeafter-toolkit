#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""gate_report.py — 发布闸门体检（G1 + G2）

一次跑出：
  G1 契约校验：每块已发布板是否满足 strict_v2 发布契约（与 build_wiki.py 同源校验函数）
  G2 条目数环比：当前板条目数 vs 上次发布（manifest.json）波动是否超过阈值

用法：
  python 02_wiki/web/tools/checks/gate_report.py                # 报告 + 写 state/gate_report.json
  python 02_wiki/web/tools/checks/gate_report.py --threshold 20  # 自定义环比阈值（默认 20%）
  python 02_wiki/web/tools/checks/gate_report.py --quiet         # 只输出结论行

退出码：0 全绿 / 1 有红板 / 2 配置或数据异常
本脚本只读，不修改任何产物。
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from collections import Counter

PROJ = pathlib.Path(__file__).resolve().parents[4]
WEB = PROJ / "02_wiki" / "web"
BOARDS = WEB / "data" / "boards"
STATE = PROJ / "02_wiki" / "state"
sys.path.insert(0, str(WEB / "tools"))

from publication_policy import (  # noqa: E402
    load_policy, public_board_ids, publication_contract_errors,
)


def kind_of(err: str) -> str:
    return re.sub(r"items\[\d+\]", "items[N]", err)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--threshold", type=float, default=20.0, help="条目数环比告警阈值 %%")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    policy_file = WEB / "data" / "publication_policy.json"
    if not policy_file.exists():
        print("❌ 缺少 publication_policy.json")
        return 2
    policy = load_policy(policy_file)
    public_ids = set(public_board_ids(policy_file, (p.stem for p in BOARDS.glob("*.json"))))

    # 上次发布的条目数（作为环比基线）
    baseline = {}
    mj = WEB / "data" / "manifest.json"
    if mj.exists():
        try:
            for b in json.loads(mj.read_text(encoding="utf-8")).get("boards", []):
                baseline[b["board"]] = b.get("items")
        except Exception:
            pass

    rows = []
    for p in sorted(BOARDS.glob("*.json")):
        if p.stem not in public_ids:
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8-sig"))
        except Exception as e:
            rows.append({"board": p.stem, "fatal": f"JSON 解析失败: {e}"})
            continue
        items = d.get("items") or []
        errs = publication_contract_errors(d, strict_v2=True)
        kinds = Counter(kind_of(e) for e in errs)
        base = baseline.get(p.stem)
        delta = None
        if base:
            delta = round((len(items) - base) * 100.0 / base, 1) if base else None
        rows.append({
            "board": p.stem,
            "name": (d.get("meta") or {}).get("name"),
            "items": len(items),
            "baseline": base,
            "delta_pct": delta,
            "error_count": len(errs),
            "error_kinds": dict(kinds.most_common(8)),
            "delta_alert": bool(delta is not None and abs(delta) > args.threshold),
        })

    red = [r for r in rows if r.get("error_count") or r.get("fatal") or r.get("delta_alert")]
    report = {
        "threshold_pct": args.threshold,
        "published_boards": len(rows),
        "green": len(rows) - len([r for r in red if r.get("error_count") or r.get("fatal")]),
        "red": len([r for r in red if r.get("error_count") or r.get("fatal")]),
        "delta_alerts": len([r for r in rows if r.get("delta_alert")]),
        "rows": rows,
    }
    STATE.mkdir(parents=True, exist_ok=True)
    (STATE / "gate_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    if not args.quiet:
        print(f"已发布板 {len(rows)} 块（基线 manifest.json）\n")
        print(f"{'板':34s} {'条目':>7s} {'环比':>8s} {'契约错':>7s}  状态")
        print("-" * 92)
        for r in rows:
            if r.get("fatal"):
                print(f"{r['board'][:34]:34s} {'-':>7s} {'-':>8s} {'-':>7s}  ❌ {r['fatal'][:30]}")
                continue
            d = r["delta_pct"]
            ds = f"{d:+.1f}%" if d is not None else "—"
            flag = "❌" if r["error_count"] else ("⚠️" if r["delta_alert"] else "✅")
            print(f"{r['board'][:34]:34s} {r['items']:>7d} {ds:>8s} {r['error_count']:>7d}  {flag}")
        bad = [r for r in rows if r["error_count"]]
        for r in bad:
            print(f"\n── {r['board']} 错误种类 Top：")
            for k, v in list(r["error_kinds"].items())[:5]:
                print(f"   {v:6d}  {k}")

    print(f"\n契约红板 {report['red']} 块 / 环比告警 {report['delta_alerts']} 块")
    print(f"报告已写入 {STATE / 'gate_report.json'}")
    return 1 if report["red"] else 0


if __name__ == "__main__":
    sys.exit(main())
