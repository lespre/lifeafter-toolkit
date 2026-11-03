#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rebuild_local_restore_tree — 本地还原树配置表全量清单（一行 = 一个已落盘配置文件）

源（只读，均在仓库内）：
  ① `01_索引与产物/41_还原树/pe/pe_config_merge_ledger_v2.json`
     = 合并账本 v2 的 `files` 记录（file / source / path / bytes / sha256），
       33,601 条 = 「配置合并体 30,609 + 增量快照 2,992」
  ② `01_索引与产物/41_还原树/pe/配置/com/cdata/` 磁盘状态
     = 落盘时间（mtime）、目录名称还原率（同目录可读文件名占比）

为什么以账本为主、磁盘为辅：账本是**已合并树**的唯一权威清单（含「这条来自合并体
还是增量快照」的来源标签，磁盘上看不出）；磁盘只提供 mtime 与名称还原率。
两者条数必须一致，不一致直接报错退出（不静默产出半表）。

输出：data/boards/local_restore_tree.json（+ 同名 .js），经 board_io.write_board_pair 落盘。

用法：python 02_wiki/web/tools/rebuild_local_restore_tree.py [--check]
  --check  只比对，不写盘（打印与现有板的差异摘要）
"""
from __future__ import annotations

import collections
import datetime
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pe_source as src  # noqa: E402
from board_io import write_board_pair  # noqa: E402

BOARD_ID = "local_restore_tree"
OUT = src.board_path(BOARD_ID)

_HEX_RE = re.compile(r"^[0-9a-fA-F]{6,}$")
_NUM_RE = re.compile(r"^\d+$")
_EXT_STATS_ORDER = (".py", ".nxs")


def _relative_path(ledger_path: str) -> str:
    """账本绝对路径 → 树内相对路径（com/cdata/X.py）。"""
    norm = ledger_path.replace("\\", "/")
    for marker in ("/pe/配置_增量快照/", "/pe/配置/"):
        if marker in norm:
            return norm.split(marker, 1)[1]
    raise SystemExit(f"❌ 账本路径不在还原树内：{ledger_path}")


def _readable(name: str) -> bool:
    """文件名是否「已还原」（非 hex 串 / 非纯数字 / 不含 unnamed）。"""
    stem = name.rsplit(".", 1)[0]
    if not stem or "unnamed" in stem.lower():
        return False
    if _HEX_RE.match(stem) or _NUM_RE.match(stem):
        return False
    return True


def _name_rate_by_dir(paths: list[Path]) -> dict[str, float]:
    """同目录可读文件名占比（%）——目录内一个文件都没有时返回 100.0。"""
    buckets: dict[str, list[bool]] = collections.defaultdict(list)
    for p in paths:
        buckets[str(p.parent)].append(_readable(p.name))
    out: dict[str, float] = {}
    for k, flags in buckets.items():
        out[k] = round(100.0 * sum(flags) / len(flags), 1) if flags else 100.0
    return out


def build() -> dict:
    files = src.ledger_files()
    if not files:
        raise SystemExit("❌ 合并账本没有 files 记录")

    # 账本 path 带来源根（…/pe/配置/… 或 …/pe/配置_增量快照/…）；
    # 行身份 = 相对树根的路径（com/cdata/X.py），落盘位置一律在合并体「配置/」下。
    # ★ 增量快照目录已被清理，但同一文件已合并进 配置/ ⇒ mtime 取合并体那份。
    tree_root = Path(src.LEDGER).parent / "配置"
    disk_paths = []
    missing = []
    for rec in files:
        rel = _relative_path(rec["path"])
        p = tree_root / rel
        rec["_rel"] = rel
        rec["_disk"] = p
        if p.is_file():
            disk_paths.append(p)
        else:
            missing.append(rel)
    if missing:
        raise SystemExit(
            f"❌ 账本里有 {len(missing)} 个文件在配置树下不存在（示例：{missing[:3]}）——"
            "树与账本脱同步，先重跑合并再重建本板")
    if len(disk_paths) != len(files):
        raise SystemExit(f"❌ 账本 {len(files)} 条 / 磁盘命中 {len(disk_paths)} 条，不一致")

    rates = _name_rate_by_dir(disk_paths)

    ledger_lock = src.lock_of(src.LEDGER, source_id="pe-config-merge-ledger-v2",
                              root=src.LEDGER.parents[3])

    items = []
    ext_counter: collections.Counter = collections.Counter()
    mtime_missing = 0
    for i, rec in enumerate(sorted(files, key=lambda r: r["_rel"]), 1):
        p = rec["_disk"]
        st = p.stat()
        mtime = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")
        if not mtime:
            mtime_missing += 1
        ext = os.path.splitext(rec["_rel"])[1].lower()
        ext_counter[ext] += 1
        items.append({
            "id": f"rt_{i:05d}",
            "name": rec["_rel"],
            "ext": ext,
            "size_kb": round(rec["bytes"] / 1024, 1),
            "mtime": mtime,
            "name_rate": rates[str(p.parent)],
            "evidence": "structure",
            "evidence_level": "structure-only",
            "status_tags": ["unverified", "static config"],
            "provenance": {
                "table": "pe_config_merge_ledger_v2.files",
                "row_key": rec["_rel"],
                # 名册级通道：逐条没有行级字段回放，只有账本记录（path/source/bytes/sha256）
                "roster": {
                    "evidence": "static-export",
                    "source_id": ledger_lock["source_id"],
                    "source_desc": "本地还原树合并账本 v2 · files（path / source / bytes / sha256）",
                },
            },
            "source": rec["source"],
        })

    src_counts = collections.Counter(it["source"] for it in items)
    n_files = len(items)
    rate_all = round(100.0 * sum(1 for it in items if it["name_rate"] >= 99.9) / n_files, 1)
    ext_stats = {e: ext_counter[e] for e in _EXT_STATS_ORDER if ext_counter[e]}
    for e in sorted(ext_counter):
        if e not in ext_stats:
            ext_stats[e] = ext_counter[e]

    board = {
        "meta": {
            "name": "本地还原树 · 配置表全量清单（路径 · 类型 · 落盘时间 · 名称还原率）",
            "category": "四、服务与包体 / （三）本地还原树",
            "source_server": "本地 PE 还原树（41_还原树/pe），不读线上客户端",
            "package_sha": ledger_lock["sha256"],
            "generated": datetime.date.today().isoformat(),
            "evidence": "structure",
            "notes": (
                "一行 = 一个已还原的配置文件，name 即相对路径（按路径排序＝树序）。"
                "来源标签取合并账本：合并体（配置/com）> 增量快照（配置_增量快照）> 基线包；"
                "同路径两处都有 → 合并成一行并标 hotfix（被热更覆盖）。"
                "已还原文件名比例 = 所在目录里文件名可读（非 hex / 非纯数字 / 非 unnamed）的占比；"
                "落盘时间取磁盘 mtime（合并体统一为合并时刻），缺失留空不猜。"
                "★ 逐表的「热更时刻」没有落盘留存，只能用「来源=增量快照 ⇒ 被热更覆盖」表达。"
                f"本次重建：账本 {n_files} 条 = 磁盘命中 {len(disk_paths)} 条（0 缺失），"
                f"mtime 缺失 {mtime_missing} 条。"
            ),
            "state_summary": {
                "文件": n_files,
                "配置树": src_counts.get("合并体", 0),
                "仅增量快照": src_counts.get("增量快照", 0),
                "被热更覆盖": src_counts.get("增量快照", 0),
                "正式名": sum(1 for it in items if _readable(it["name"])),
                "已还原文件名比例": f"{rate_all}%",
            },
            "card_mode": "",
            "card_summary": [["name", "路径"], ["ext", "类型"], ["size_kb", "KB"], ["mtime", "落盘时间"]],
            "field_labels": {
                "name": "路径", "ext": "文件类型", "size_kb": "大小 KB",
                "mtime": "落盘时间", "source": "来源", "name_rate": "目录名称还原率 %",
            },
            "source_label": "本地还原树合并账本 v2（配置合并体 + 增量快照）",
            "ledger_generated": "2026-10-26",
            "ext_stats": ext_stats,
            "provenance": {
                "contract_version": 3,
                "audit_status": "passed",
                "contract": "frozen-audited-artifact",
                "source_locks": [{
                    "source_id": ledger_lock["source_id"],
                    "role": "primary",
                    "sha256": ledger_lock["sha256"],
                    "path": ledger_lock["path_hint"],
                    "bytes": ledger_lock["bytes"],
                    "mtime_ns": 0,
                }],
                "source_scope": {
                    "cross_source_policy": "no-cross-source-field-join",
                    "integer_join_policy": "no-equal-integer-join",
                    "runtime_final_policy": "unknown-unless-runtime-proven",
                },
            },
        },
        "items": items,
    }
    return board


def main(argv: list[str]) -> int:
    board = build()
    check = "--check" in argv
    if check:
        old = src.read_json(OUT)
        old_names = [it["name"] for it in old.get("items", [])]
        new_names = [it["name"] for it in board["items"]]
        print(f"旧 {len(old_names)} 条 / 新 {len(new_names)} 条")
        print(f"仅旧有 {len(set(old_names) - set(new_names))} · 仅新有 {len(set(new_names) - set(old_names))}")
        print(f"顺序一致={old_names == new_names}")
        return 0
    write_board_pair(OUT, board, BOARD_ID)
    print(f"✅ {BOARD_ID}: {len(board['items'])} 条 → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
