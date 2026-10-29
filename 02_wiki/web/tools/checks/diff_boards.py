#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""diff_boards.py — 条目级 diff（不是条目数环比）

对比两次快照的 fingerprints.json，按条目 id 精确到「哪一条变了、变了什么字段」。

输出分两节（对应 rules/README.md 的口径变更 / 数据变更分列约定）：
  * 口径变更：rules/ 规则文件的哈希变化（改口径 ≠ 改数据，必须分开看）
  * 数据变更：条目级新增 / 删除 / 字段修改

用法:
  python 02_wiki/web/tools/checks/diff_boards.py --before 20261030_0900 --after 20261030_1800
  python 02_wiki/web/tools/checks/diff_boards.py --before xxx --after current   # after 直接读现产物
  python 02_wiki/web/tools/checks/diff_boards.py --before xxx --after current --board vehicle_full
  python 02_wiki/web/tools/checks/diff_boards.py --before xxx --after current --json-only

退出码: 0 无变更 / 1 有变更 / 2 参数或数据异常
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import sys

PROJ = pathlib.Path(__file__).resolve().parents[4]
WEB = PROJ / "02_wiki" / "web"
BOARDS = WEB / "data" / "boards"
RULES = PROJ / "02_wiki" / "rules"
STATE = PROJ / "02_wiki" / "state"
SNAP_DIR = STATE / "snapshots"
DIFF_DIR = STATE / "diff"

sys.path.insert(0, str(PROJ / "02_wiki" / "web" / "tools" / "build"))
from snapshot import board_fingerprint, rules_fingerprint  # noqa: E402

# 指纹不覆盖的字段（与 snapshot.IGNORE_KEYS 保持一致）
sys.path.insert(0, str(PROJ / "02_wiki" / "web" / "tools" / "build"))
from snapshot import IGNORE_KEYS  # noqa: E402

MAX_LISTED = 40


def load_before(label: str) -> tuple[dict, dict]:
    d = SNAP_DIR / label
    if not d.exists():
        raise SystemExit(f"❌ 找不到快照：{d}")
    fpf = d / "fingerprints.json"
    if not fpf.exists():
        raise SystemExit(f"❌ 快照缺 fingerprints.json：{fpf}")
    fp = json.loads(fpf.read_text(encoding="utf-8"))
    meta = {}
    mf = d / "meta.json"
    if mf.exists():
        meta = json.loads(mf.read_text(encoding="utf-8"))
    return fp, meta


def load_after(label: str) -> tuple[dict, dict]:
    """after=current 时直接对现产物算指纹；否则读另一张快照。"""
    if label == "current":
        fp: dict[str, dict] = {}
        counts: dict[str, int] = {}
        for p in sorted(BOARDS.glob("*.json")):
            try:
                f, n = board_fingerprint(p)
            except Exception as e:
                print(f"   ⚠️ {p.stem}: 指纹失败 {e}", file=sys.stderr)
                continue
            fp[p.stem] = f
            counts[p.stem] = n
        return fp, {"boards": sorted(fp), "items": counts,
                    "total_items": sum(counts.values()), "label": "current"}
    return load_before(label)


def changed_fields(old_item: dict, new_item: dict) -> list[str]:
    """定位条目里真正变化的字段名（忽略 IGNORE_KEYS）。"""
    keys = set(old_item) | set(new_item)
    out = []
    for k in sorted(keys):
        if k in IGNORE_KEYS:
            continue
        if old_item.get(k) != new_item.get(k):
            out.append(k)
    return out


def diff_one_board(before: dict, after: dict,
                   old_items: dict | None) -> dict:
    """old_items: {id: 原始条目dict}，用于字段级定位；没有就只报条目级。"""
    b_ids, a_ids = set(before), set(after)
    added = sorted(a_ids - b_ids)
    removed = sorted(b_ids - a_ids)
    common = a_ids & b_ids
    modified = sorted(i for i in common if before[i] != after[i])

    modified_detail = []
    for i in modified:
        fields = None
        if old_items is not None:
            oi = old_items.get(i)
            if oi is not None:
                ni = _read_current_item(i)
                if ni is not None:
                    fields = changed_fields(oi, ni)
        modified_detail.append({"id": i, "fields": fields})

    return {
        "added": added,
        "removed": removed,
        "modified": modified_detail,
        "added_count": len(added),
        "removed_count": len(removed),
        "modified_count": len(modified),
    }


_current_cache: dict[str, dict] = {}


def _read_current_item(item_id: str) -> dict | None:
    """从现产物里取条目原文（按 id 索引，带缓存）。"""
    if "map" not in _current_cache:
        m: dict[str, dict] = {}
        for p in sorted(BOARDS.glob("*.json")):
            try:
                d = json.loads(p.read_text(encoding="utf-8-sig"))
            except Exception:
                continue
            for it in d.get("items") or []:
                if isinstance(it, dict) and it.get("id") is not None:
                    m.setdefault(str(it["id"]), it)
        _current_cache["map"] = m
    return _current_cache["map"].get(item_id)


def _old_item_map(snapshot_label: str) -> dict:
    """从快照的 boards/ 副本里读旧条目原文。"""
    d = SNAP_DIR / snapshot_label / "boards"
    m: dict[str, dict] = {}
    if not d.exists():
        return m
    for p in sorted(d.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        for it in data.get("items") or []:
            if isinstance(it, dict) and it.get("id") is not None:
                m.setdefault(str(it["id"]), it)
    return m


def rules_delta(before_meta: dict, after_meta: dict) -> dict:
    """规则层变更（口径变更）。"""
    b = before_meta.get("rules_fingerprint") or {}
    a = after_meta.get("rules_fingerprint") or {}
    changed = sorted(k for k in set(a) if k in b and a[k] != b[k])
    added = sorted(k for k in a if k not in b)
    removed = sorted(k for k in b if k not in a)
    return {"changed": changed, "added": added, "removed": removed}


def render_md(report: dict) -> str:
    L = []
    A = L.append
    A(f"# 变更报告 · {report['before_label']} → {report['after_label']}")
    A("")
    A(f"- 生成时间：{report['created']}")
    A(f"- 对比板数：{report['board_count']}")
    A(f"- 数据变更条目：新增 {report['total_added']} / 删除 {report['total_removed']} / 修改 {report['total_modified']}")
    A("")
    A("## 一、口径变更（rules/ 规则层）")
    A("")
    rd = report["rules_delta"]
    if not any(rd.values()):
        A("规则层无变化。")
    else:
        for k, label in (("changed", "修改"), ("added", "新增"), ("removed", "删除")):
            for f in rd[k]:
                A(f"- **{label}** `rules/{f}`")
    A("")
    A("## 二、数据变更（条目级）")
    A("")
    if not report["boards"]:
        A("无条目级变化。")
    for bd in report["boards_detail"]:
        if not (bd["added_count"] or bd["removed_count"] or bd["modified_count"]):
            continue
        A(f"### {bd['board']}")
        A("")
        if bd["added_count"]:
            A(f"**新增 {bd['added_count']} 条**")
            for i in bd["added"][:MAX_LISTED]:
                A(f"- `+` {i}")
            if bd["added_count"] > MAX_LISTED:
                A(f"- … 另有 {bd['added_count'] - MAX_LISTED} 条")
            A("")
        if bd["removed_count"]:
            A(f"**删除 {bd['removed_count']} 条**")
            for i in bd["removed"][:MAX_LISTED]:
                A(f"- `-` {i}")
            if bd["removed_count"] > MAX_LISTED:
                A(f"- … 另有 {bd['removed_count'] - MAX_LISTED} 条")
            A("")
        if bd["modified_count"]:
            A(f"**修改 {bd['modified_count']} 条**")
            for m in bd["modified"][:MAX_LISTED]:
                fs = "、".join(m["fields"]) if m.get("fields") else "（内容有变，字段级不可定位）"
                A(f"- `~` `{m['id']}` — {fs}")
            if bd["modified_count"] > MAX_LISTED:
                A(f"- … 另有 {bd['modified_count'] - MAX_LISTED} 条")
            A("")
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(description="条目级 diff")
    ap.add_argument("--before", required=True, help="基线快照标签")
    ap.add_argument("--after", default="current", help="对比快照标签，或 current")
    ap.add_argument("--board", help="只对比某板")
    ap.add_argument("--json-only", action="store_true", help="不打印 Markdown")
    ap.add_argument("--out", help="报告输出目录（默认 state/diff/）")
    args = ap.parse_args()

    before_fp, before_meta = load_before(args.before)
    after_fp, after_meta = load_after(args.after)

    boards = sorted(set(before_fp) | set(after_fp))
    if args.board:
        if args.board not in boards:
            raise SystemExit(f"❌ 板 {args.board} 不在对比范围内")
        boards = [args.board]

    old_items = _old_item_map(args.before) if args.after == "current" else {}

    details = []
    ta = tr = tm = 0
    for b in boards:
        bd = diff_one_board(before_fp.get(b, {}), after_fp.get(b, {}), old_items or None)
        bd["board"] = b
        ta += bd["added_count"]; tr += bd["removed_count"]; tm += bd["modified_count"]
        details.append(bd)

    report = {
        "created": datetime.datetime.now().isoformat(timespec="seconds"),
        "before_label": args.before,
        "after_label": args.after,
        "board_count": len(boards),
        "total_added": ta, "total_removed": tr, "total_modified": tm,
        "rules_delta": rules_delta(before_meta, after_meta),
        "boards_detail": details,
    }
    outdir = pathlib.Path(args.out) if args.out else DIFF_DIR / f"{args.before}__{args.after}"
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "diff.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    (outdir / "diff.md").write_text(render_md(report), encoding="utf-8")

    if not args.json_only:
        print(render_md(report))
        print(f"\n报告已写入 {outdir}")

    changed = bool(ta or tr or tm or any(report["rules_delta"].values()))
    return 1 if changed else 0


if __name__ == "__main__":
    sys.exit(main())
