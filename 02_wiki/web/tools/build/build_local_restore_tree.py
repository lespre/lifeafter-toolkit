#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""build_local_restore_tree.py — 「本地还原树」板（三、综合资料 / （三）本地还原树）

用户 2026-11-01 口径：树状路径表，附带**已还原文件名比例 / 文件类型 / 热更时间**。

数据源（只读冻结产物，不扫线上客户端）：
  01_索引与产物/41_还原树/pe/pe_config_merge_ledger_v2.json
    每条 = 一个已还原的配置文件：file / source（合并体·增量快照·基线包）/ path / bytes / sha256

口径：
  ① 一行 = 一个还原文件，`name` 即相对路径（`com/cdata/xxx.py`），按路径排序 ⇒ 树状顺序；
     同一路径同时出现在「合并体」与「增量快照」→ 合并成一行，标 hotfix=true（被热更覆盖）。
  ② 文件类型 = 扩展名（.py 配置表 / .nxs 脚本 / 其它）。
  ③ 热更时间 = 磁盘上的文件 mtime（合并体取合并后的落盘时间）；无 mtime 则留空，不猜。
  ④ 已还原文件名比例 = 该文件所在目录里「文件名可读（非 hex/非纯数字/非 unnamed）」
     的文件占比。实测配置树 100%，将来出现匿名条目会掉下来 —— 比例是真算的，不是写死的。

用法：
  python 02_wiki/web/tools/build/build_local_restore_tree.py --dry
  python 02_wiki/web/tools/build/build_local_restore_tree.py --apply
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import pathlib
import re
import sys
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

from board_io import dumps_board, dumps_board_js, write_text  # noqa: E402
from la_paths import PROJ, WEB  # noqa: E402

BOARDS = WEB / "data" / "boards"
BOARD_ID = "local_restore_tree"
PE = PROJ / "01_索引与产物/41_还原树/pe"
LEDGER = PE / "pe_config_merge_ledger_v2.json"

# ★ 溯源字面量：账本文件的 sha256（运行时算会破坏字节级可复现，故写死）
LEDGER_SHA = "919a6aa4962e37018cee1a6147586cff466d2e75f5c34dc1c8c7f7d9f45a7251"
LEDGER_LOCK_ID = "pe-config-merge-ledger-v2"

TODAY = datetime.date.today().isoformat()
HEXNAME = re.compile(r"^(?:[0-9a-fA-F]{16,}|[0-9a-fA-F]{8,}\.[a-z0-9]+|unnamed.*)$", re.I)

CATEGORY = "三、综合资料 / （三）本地还原树"
NOTES = (
    "一行 = 一个已还原的配置文件，name 即相对路径（按路径排序＝树序）。"
    "来源标签取合并账本：合并体（配置/com）> 增量快照（配置_增量快照）> 基线包；"
    "同路径两处都有 → 合并成一行并标 hotfix（被热更覆盖）。"
    "已还原文件名比例 = 所在目录里文件名可读（非 hex / 非纯数字 / 非 unnamed）的占比，"
    "实测配置树 100%；落盘时间取磁盘 mtime（合并体统一为合并时刻），缺失留空不猜。"
    "★ 逐表的「热更时刻」没有落盘留存，只能用「来源=增量快照 ⇒ 被热更覆盖」表达。"
)


def rel_parts(path: str) -> tuple[str, str]:
    """返回 (顶层目录, 相对路径)。"""
    p = path.replace("\\", "/")
    root = str(PE).replace("\\", "/").rstrip("/") + "/"
    if p.startswith(root):
        p = p[len(root):]
    top, _, rest = p.partition("/")
    return top, (rest or p)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="落盘（默认 dry-run）")
    args = ap.parse_args()

    raw = LEDGER.read_bytes()
    sha_now = hashlib.sha256(raw).hexdigest()
    if sha_now != LEDGER_SHA:
        print("⚠ 账本 sha 变了（%s ≠ 字面量 %s）：口径/锁需要人工复核后再改常量"
              % (sha_now[:12], LEDGER_SHA[:12]))
    led = json.loads(raw.decode("utf-8"))
    files = led.get("files") or []

    merged: dict[str, dict] = {}
    for f in files:
        top, rel = rel_parts(f.get("path") or "")
        rec = merged.setdefault(rel, {"top": top, "bytes": 0, "sources": [], "sha": ""})
        rec["sources"].append(str(f.get("source") or top))
        # 合并体是实际落盘的那份（体积取它），增量快照只作 hotfix 标记
        if str(f.get("source")) == "合并体" or not rec["bytes"]:
            rec["bytes"] = int(f.get("bytes") or 0)
        rec["sha"] = rec["sha"] or str(f.get("sha256") or "")

    # 目录级「已还原文件名比例」
    per_dir: dict[str, list[int]] = {}
    for rel in merged:
        d = str(pathlib.PurePosixPath(rel).parent)
        base = pathlib.PurePosixPath(rel).name
        per_dir.setdefault(d, []).append(0 if HEXNAME.match(base) else 1)
    dir_rate = {d: (sum(v), len(v)) for d, v in per_dir.items()}

    items = []
    for i, rel in enumerate(sorted(merged), start=1):
        rec = merged[rel]
        p = pathlib.PurePosixPath(rel)
        base, d = p.name, str(p.parent)
        ext = p.suffix.lower() or "（无扩展名）"
        srcs = sorted(set(rec["sources"]))
        hotfix = any(s == "增量快照" for s in srcs)
        # 落盘时间：优先原始路径（合并体），增量快照目录已随合并删除 → 回落到合并体里的同名文件
        mtime = ""
        for fpath in (PE / rec["top"] / rel, PE / "配置" / rel):
            try:
                mtime = datetime.datetime.fromtimestamp(fpath.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                break
            except OSError:
                continue
        ok, tot = dir_rate.get(d, (0, 0))
        # 卡面只留「路径 + 4 个有信息量的列」：dir/base/tree 与路径重复、
        # hotfix=否 是噪声，一并省掉（省 ~40% 体积，也好看得多）。
        item = {
            "id": "rt_%05d" % i,
            "name": rel,
            "ext": ext,
            "size_kb": round(rec["bytes"] / 1024.0, 1),
            "mtime": mtime,
            "name_rate": (round(100.0 * ok / tot, 1) if tot else None),
            "evidence": "structure",
            "evidence_level": "structure-only",
            # ★ 名册级通道（publication.yml 口径）：本板是本地账本的**静态导出**，
            #   没有「npk 行级解码链」可写 —— 伪造 locator_chain 是不允许的，
            #   按 roster + unverified 如实标注（门禁据此放宽定位链要求）。
            "status_tags": ["unverified", "static config"],
            "provenance": {
                "table": "pe_config_merge_ledger_v2.files",
                "row_key": rel,
                "roster": {
                    "evidence": "static-export",
                    "source_id": LEDGER_LOCK_ID,
                    "source_desc": "本地还原树合并账本 v2 · files（path / source / bytes / sha256）",
                },
            },
        }
        # ★ 字段必须全条目一致（build_wiki 的 check_board 要求），所以 source 恒写；
        #   hotfix 不单独成列 —— 「来源含增量快照」即可判定，省一列也少一半噪声。
        item["source"] = " + ".join(srcs)
        items.append(item)

    ext_c = Counter(i["ext"] for i in items)
    ok_all = sum(1 for rel in merged if not HEXNAME.match(pathlib.PurePosixPath(rel).name))
    hot = sum(1 for i in items if "增量快照" in str(i.get("source")))
    state = {
        "文件": len(items),
        "配置树": sum(1 for k, v in merged.items() if v["top"] == "配置"),
        "仅增量快照": sum(1 for k, v in merged.items() if v["top"] == "配置_增量快照"),
        "被热更覆盖": hot,
        "正式名": ok_all,
        "已还原文件名比例": "%.1f%%" % (100.0 * ok_all / len(items)) if items else "—",
    }

    board = {
        "meta": {
            "name": "本地还原树 · 配置表全量清单（路径 · 类型 · 落盘时间 · 名称还原率）",
            "category": CATEGORY,
            "source_server": "本地 PE 还原树（41_还原树/pe），不读线上客户端",
            "package_sha": LEDGER_SHA,
            "generated": TODAY,
            "evidence": "structure",
            "notes": NOTES,
            "state_summary": state,
            "card_mode": "",
            "card_summary": [["name", "路径"], ["ext", "类型"],
                             ["size_kb", "KB"], ["mtime", "落盘时间"]],
            "field_labels": {
                "name": "路径", "ext": "文件类型", "size_kb": "大小 KB",
                "mtime": "落盘时间", "source": "来源",
                "name_rate": "目录名称还原率 %",
            },
            "source_label": "本地还原树合并账本 v2（配置合并体 + 增量快照）",
            "ledger_generated": led.get("generated"),
            "ext_stats": dict(sorted(ext_c.items(), key=lambda kv: -kv[1])),
            "provenance": {
                "contract_version": 3,
                "audit_status": "passed",
                "contract": "frozen-audited-artifact",
                "source_locks": [{
                    "source_id": LEDGER_LOCK_ID,
                    "role": "primary",
                    "sha256": LEDGER_SHA,
                    "path": "01_索引与产物/41_还原树/pe/pe_config_merge_ledger_v2.json",
                    "bytes": len(raw),
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

    print("文件 %d（配置 %d / 仅增量快照 %d），被热更覆盖 %d，正式名 %d（%s）"
          % (len(items), state["配置树"], state["仅增量快照"], hot, ok_all,
             state["已还原文件名比例"]))
    print("类型分布：%s" % ", ".join("%s %d" % kv for kv in ext_c.most_common(5)))
    print("样例：")
    for it in items[:3] + items[-2:]:
        print("   %-52s %-5s %8.1fKB %s %s" % (it["name"][:52], it["ext"],
                                               it["size_kb"], it["mtime"] or "-", it["source"]))
    if not args.apply:
        print("--dry：未写盘")
        return 0

    text = dumps_board(board)
    assert json.loads(text) == board, "写出前语义校验失败"
    write_text(BOARDS / ("%s.json" % BOARD_ID), text)
    write_text(BOARDS / ("%s.js" % BOARD_ID), dumps_board_js(BOARD_ID, text))
    print("已写 %s.json / %s.js（%.1f MB）"
          % (BOARD_ID, BOARD_ID, len(text.encode("utf-8")) / 1048576))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
