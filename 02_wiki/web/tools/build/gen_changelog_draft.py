#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""gen_changelog_draft.py — 更新日志草稿生成器（**不直接改线上 updates.json**）

从条目级 diff 结果起草 updates.json 条目，写到 state/changelog_draft.json 供人工确认。

铁律：
  * **只写草稿**。绝不碰 web/data/updates.json —— 发布日志是人工口径，
    自动写进去就等于让机器替你决定「这次更新对用户意味着什么」。
  * 分组规则：新增条目按**板分类**归组（板 meta.category 的一级段，如「一、时装类」）。
  * 口径变更（rules/ 规则层）与数据变更分开起草 —— 改口径 ≠ 改数据。
  * 草稿里的每条都带**证据指针**（diff 报告路径 + 板 + 条目数），便于人工核对。

用法:
  python 02_wiki/web/tools/build/gen_changelog_draft.py --diff 02_wiki/state/diff/20261030_0900__current
  python 02_wiki/web/tools/build/gen_changelog_draft.py --diff <dir> --date 2026-10-31
  python 02_wiki/web/tools/build/gen_changelog_draft.py --diff <dir> --out state/changelog_draft.json

退出码: 0 成功 / 1 参数或数据异常
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from la_paths import PROJ, WEB, BOARDS_DIR, RULES_DIR, STATE_DIR  # noqa: E402

DRAFT_FILE = STATE_DIR / "changelog_draft.json"
UPDATES_FILE = WEB / "data" / "updates.json"

# diff 报告里每板列出的条目上限（超过只取前 N 个做样例）
SAMPLE_LIMIT = 6


def load_diff(diff_dir: pathlib.Path) -> dict:
    f = diff_dir / "diff.json"
    if not f.exists():
        raise SystemExit(f"❌ 找不到 diff 报告：{f}\n"
                         f"   先跑 build_pipeline.py 或 diff_boards.py 生成。")
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except Exception as e:
        raise SystemExit(f"❌ diff 报告解析失败：{e}")


def board_meta(board: str) -> dict:
    """读板 meta（取 category / name 用于归组）。"""
    p = BOARDS_DIR / f"{board}.json"
    if not p.exists():
        return {}
    try:
        d = json.loads(p.read_text(encoding="utf-8-sig"))
        return d.get("meta") or {}
    except Exception:
        return {}


def group_key(category: str) -> str:
    """从板 category 提取归组键（取「一、时装类」这一级）。

    例：「一、时装类 / （三）载具」→「一、时装类」
        「四、综合资料 / （三）称号」→「四、综合资料」
    """
    if not category:
        return "其他"
    head = str(category).split("/")[0].strip()
    return head or "其他"


def item_name(board: str, item_id: str) -> str:
    """取条目显示名（优先 name，其次 id）。"""
    p = BOARDS_DIR / f"{board}.json"
    if not p.exists():
        return str(item_id)
    try:
        d = json.loads(p.read_text(encoding="utf-8-sig"))
    except Exception:
        return str(item_id)
    for it in d.get("items") or []:
        if isinstance(it, dict) and str(it.get("id")) == str(item_id):
            nm = it.get("name") or it.get("title") or it.get("display_name")
            if nm:
                return str(nm)
    return str(item_id)


def build_draft(diff: dict, date: str, diff_dir: pathlib.Path) -> dict:
    """把 diff 报告转成更新日志草稿条目。"""
    groups: dict[str, dict] = {}   # group_key -> {boards: [...], added: n, ...}
    entries: list[dict] = []

    for bd in diff.get("boards_detail") or []:
        board = bd.get("board") or "?"
        meta = board_meta(board)
        cat = meta.get("category") or ""
        gk = group_key(cat)
        g = groups.setdefault(gk, {"group": gk, "boards": {}, "added": 0,
                                   "removed": 0, "modified": 0})
        g["boards"][board] = {
            "name": meta.get("name") or board,
            "added": bd.get("added_count", 0),
            "removed": bd.get("removed_count", 0),
            "modified": bd.get("modified_count", 0),
        }
        g["added"] += bd.get("added_count", 0)
        g["removed"] += bd.get("removed_count", 0)
        g["modified"] += bd.get("modified_count", 0)

    # ── 数据变更：按归组起草 ────────────────────────────────────────
    for gk in sorted(groups, key=lambda k: -groups[k]["added"]):
        g = groups[gk]
        if not (g["added"] or g["removed"] or g["modified"]):
            continue
        items: list[str] = []
        for board, info in sorted(g["boards"].items()):
            if info["added"]:
                items.append(f"{info['name']}：新增 {info['added']} 条")
            if info["modified"]:
                items.append(f"{info['name']}：更新 {info['modified']} 条")
            if info["removed"]:
                items.append(f"{info['name']}：移除 {info['removed']} 条")
        if not items:
            continue
        title = f"{gk}：{sum(i['added'] for i in g['boards'].values())} 条新增" \
            if g["added"] else f"{gk}：内容更新"
        entries.append({
            "date": date,
            "title": title,
            "tag": gk,
            "items": items,
            "_evidence": {
                "kind": "data-change",
                "group": gk,
                "boards": {b: info for b, info in sorted(g["boards"].items())},
            },
        })

    # ── 口径变更：单独一条（改口径 ≠ 改数据）────────────────────────
    rd = diff.get("rules_delta") or {}
    changed = list(rd.get("changed") or [])
    added = list(rd.get("added") or [])
    removed = list(rd.get("removed") or [])
    if changed or added or removed:
        items = []
        if changed:
            items.append("口径规则调整：" + "、".join(f"`{c}`" for c in changed[:8]))
        if added:
            items.append("新增口径文件：" + "、".join(f"`{c}`" for c in added[:8]))
        if removed:
            items.append("移除口径文件：" + "、".join(f"`{c}`" for c in removed[:8]))
        entries.append({
            "date": date,
            "title": "口径调整（规则层变更）",
            "tag": "口径",
            "items": items,
            "_evidence": {"kind": "rules-change",
                          "changed": changed, "added": added, "removed": removed},
        })

    return {
        "generated": datetime.datetime.now().isoformat(timespec="seconds"),
        "date": date,
        "source_diff": str(diff_dir.relative_to(PROJ)).replace("\\", "/") if diff_dir.is_relative_to(PROJ) else str(diff_dir),
        "before_label": diff.get("before_label"),
        "after_label": diff.get("after_label"),
        "total_added": diff.get("total_added", 0),
        "total_removed": diff.get("total_removed", 0),
        "total_modified": diff.get("total_modified", 0),
        "note": ("草稿 —— 供人工确认。确认后手工并入 web/data/updates.json；"
                 "本工具不会写线上文件。"),
        "entries": entries,
    }


def render_md(draft: dict) -> str:
    L: list[str] = []
    A = L.append
    A(f"# 更新日志草稿 · {draft['date']}")
    A("")
    A(f"- 生成时间：{draft['generated']}")
    A(f"- 来源 diff：`{draft['source_diff']}`"
      f"（{draft.get('before_label')} → {draft.get('after_label')}）")
    A(f"- 变更合计：新增 {draft['total_added']} / 删除 {draft['total_removed']} / 修改 {draft['total_modified']}")
    A(f"- ⚠️ {draft['note']}")
    A("")
    if not draft["entries"]:
        A("无变更，无需起草。")
        return "\n".join(L)
    for e in draft["entries"]:
        A(f"## {e['title']}")
        A("")
        A(f"**tag**：{e['tag']}　**date**：{e['date']}")
        A("")
        for it in e["items"]:
            A(f"- {it}")
        A("")
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(description="更新日志草稿生成器")
    ap.add_argument("--diff", required=True, help="diff 报告目录（含 diff.json）")
    ap.add_argument("--date", help="日志日期（默认今天）")
    ap.add_argument("--out", help="草稿输出路径（默认 state/changelog_draft.json）")
    ap.add_argument("--md", help="额外写一份 Markdown 到此路径")
    args = ap.parse_args()

    diff_dir = pathlib.Path(args.diff)
    if not diff_dir.is_absolute():
        diff_dir = PROJ / diff_dir
    if not diff_dir.exists():
        raise SystemExit(f"❌ diff 目录不存在：{diff_dir}")

    diff = load_diff(diff_dir)
    date = args.date or datetime.date.today().isoformat()
    draft = build_draft(diff, date, diff_dir)

    out = pathlib.Path(args.out) if args.out else DRAFT_FILE
    if not out.is_absolute():
        out = PROJ / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(draft, ensure_ascii=False, indent=1), encoding="utf-8")

    if args.md:
        mp = pathlib.Path(args.md)
        if not mp.is_absolute():
            mp = PROJ / mp
        mp.parent.mkdir(parents=True, exist_ok=True)
        mp.write_text(render_md(draft), encoding="utf-8")

    print(render_md(draft))
    print(f"\n草稿已写入 {out}")
    print(f"⚠️ 未改动 {UPDATES_FILE.relative_to(PROJ)}（发布日志须人工确认）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
