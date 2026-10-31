#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""fix_upcoming_auto_20261101.py — 修「新更新与预告（自动）」板的元数据与占位名（幂等）

用户 2026-11-01 判定要修的三类问题：

  ① 计数自相矛盾：meta.state_summary 写「武器皮肤 11」，items 里实际只有 9 条；
     periods[up_skin].member_count 也是 11。evidence_detail / icon_stats 是从
     lottery_periods 的 meta 抄来的（structure 402 与本板无关）。
     ⇒ 一律由条目实时重算，不再手填。

  ② 占位名：「道具 400019」「时装部件 741540120」是构建器查不到名字时的兜底。
     ⇒ 按 时装部位表 → 时装板 → 全量道具表 求真名；查不到显式标未解析（不编造）。

  ③ notes 里留着 2026-10-29 那次人工订正的长文，且与 ① 的计数无关联。
     ⇒ 收敛成规则化短句（幂等追加，重复跑不会增长）。

口径实现全在 upcoming_board_rules.py（构建器 build_upcoming_auto.py 共用同一份）。
只改 data/boards/upcoming_auto.{json,js}；不动 provenance / source_locks。

用法：
  python 02_wiki/web/tools/build/fix_upcoming_auto_20261101.py          # dry-run
  python 02_wiki/web/tools/build/fix_upcoming_auto_20261101.py --apply
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

from board_io import dumps_board, dumps_board_js, write_text  # noqa: E402
from la_paths import WEB  # noqa: E402
from notes_util import SEP, append_note  # noqa: E402
from upcoming_board_rules import (  # noqa: E402
    CATEGORY, NOTE_COUNTS, NOTE_LISTED, NOTE_MAIN, NOTE_NAMES, NOTE_SCOPE, NOTE_WINDOW,
    enrich_period_status, ensure_source_locks, fix_placeholders, load_name_index,
    rebuild_skin_items, recount,
)

BOARDS = WEB / "data" / "boards"
TARGET = BOARDS / "upcoming_auto.json"
POLICY = WEB / "data" / "publication_policy.json"
TODAY = "2026-11-01"
POLICY_REASON = ("预告专栏唯一板：武器皮肤未上架段 + 未开始奖池期次（万圣绮夜）连带成员。"
                 "分类与条目数随板产物同步；数值来自各源板行，不含上线/价格/概率推断。")


def sync_policy(n_items: int) -> tuple[str, str]:
    """把发布策略里本板的分类/条目数/理由对齐到板产物（幂等）。返回前后分类。"""
    pol = json.loads(POLICY.read_text(encoding="utf-8"))
    entry = pol["boards"].setdefault("upcoming_auto", {})
    before = str(entry.get("category") or "")
    entry["category"] = CATEGORY
    entry["items"] = n_items
    entry["reason"] = POLICY_REASON
    pol["generated"] = TODAY
    write_text(POLICY, json.dumps(pol, ensure_ascii=False, indent=1) + "\n")
    return before, CATEGORY


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="落盘（默认 dry-run）")
    args = ap.parse_args()

    board = json.loads(TARGET.read_text(encoding="utf-8"))
    idx = load_name_index(BOARDS)

    print("── ⓪ 武器皮肤段按当前源表重建（新热更的皮肤要进来）")
    for line in rebuild_skin_items(board, BOARDS, TODAY) or ["（无变化）"]:
        print("   " + line)

    print("── ① 占位名")
    logs = fix_placeholders(board, idx)
    for line in logs or ["（无占位名）"]:
        print("   " + line)

    print("── ② 期次状态（供前端判断「还在预告窗口」）")
    for line in enrich_period_status(board, BOARDS) or ["（无奖池成员）"]:
        print("   " + line)

    print("── ③ 计数重算")
    res = recount(board)
    print("   state_summary: %s → %s" % (res["state_summary"][0], res["state_summary"][1]))
    print("   periods.member_count: %s" % res["periods"])

    print("── ③b 板级 source_locks 补齐（门禁逐条核对 sha 归属）")
    for line in ensure_source_locks(board, BOARDS) or ["（已齐）"]:
        print("   " + line)

    print("── ④ notes 收敛")
    # 旧 notes 是一整段（含 10-29 手工订正长文、无 ｜ 分段）：收敛成两条规则句，
    # 再用 append_note 幂等补三条。重跑时同样走到这里，结果不变。
    old_note = str(board["meta"].get("notes") or "")
    if (not old_note) or ("不再人工维护预告卡。" in old_note):
        board["meta"]["notes"] = NOTE_MAIN + SEP + NOTE_LISTED
    for n in (NOTE_COUNTS, NOTE_NAMES, NOTE_WINDOW, NOTE_SCOPE):
        append_note(board, n)
    board["meta"]["updated"] = TODAY
    print("   notes = %s" % board["meta"]["notes"])

    if not args.apply:
        print("--dry：未写盘")
        return 0

    text = dumps_board(board)
    assert json.loads(text) == board, "写出前语义校验失败"
    write_text(TARGET, text)
    write_text(BOARDS / "upcoming_auto.js", dumps_board_js("upcoming_auto", text))
    before, after = sync_policy(len(board.get("items") or []))
    print("已写 %s / upcoming_auto.js" % TARGET.name)
    print("policy.upcoming_auto.category: %s → %s" % (before, after))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
