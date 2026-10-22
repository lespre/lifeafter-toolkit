# -*- coding: utf-8 -*-
r"""服型板块：以 toolkit_core/server_types.py 为唯一来源（本地已有结论）。

输出每个服型后缀的中文名、依据、本端表数、状态（已确认/待确认），以及 base 通用服。
"""
from __future__ import annotations

import datetime
import json
import pathlib
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
OUT = WEB / "data/boards/server_types.json"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import server_types as ST  # noqa: E402

from _src import cdata_dir
TREE = cdata_dir()


def main() -> int:
    counts = {}
    try:
        counts = (ST.scan_tree(TREE) or {}).get("per_suffix", {})
    except Exception as e:  # noqa: BLE001
        print("扫描表树失败（表数留空）：", e)

    items = []
    for suffix, (label, why) in ST.VARIANT_NAMES.items():
        rec = counts.get(suffix) if isinstance(counts, dict) else None
        n = rec.get("files") if isinstance(rec, dict) else None
        pending = ("未定" in label) or ("？" in label) or ("待确认" in why)
        items.append({
            "id": "st_" + suffix,
            "suffix": suffix,
            "name": "%s · %s" % (suffix, label),
            "label": label,
            "why": why,
            "table_count": n if isinstance(n, int) else None,
            "state": "待确认" if pending else "已确认",
            "evidence": "structure",
            "evidence_level": "static/candidate",
            "status_tags": ["unresolved"] if pending else ["static config"],
            "source": "toolkit_core/server_types.py",
            "summary": "%s ｜ 本端 %s 张表" % (label, n if isinstance(n, int) else "?"),
            "provenance": {
                "source_id": "server-types", "source_lock_sha256": "0" * 64,
                "table": "toolkit_core/server_types.py", "row_key": suffix or "base",
                "field_refs": ["VARIANT_NAMES", "scan_tree"],
                "name_source": "toolkit_core/server_types.py#VARIANT_NAMES",
                "upstream": {"package_sha256": "0" * 64, "entry_index": None,
                             "file_id": None, "decoded_sha256": None, "role": "server_types"},
                "locator_chain": {"chain_status": "replayed-structural", "scope": "record",
                                  "no_cross_source_field_join": True,
                                  "steps": [{"kind": "decoded-table-row", "source_id": "server-types",
                                             "table": "toolkit_core/server_types.py",
                                             "row_key": suffix or "base",
                                             "field_refs": ["name", "why"]}]},
            },
        })
    items.append({
        "id": "st_base", "suffix": "", "name": "base · 通用/经典服（无后缀）", "label": "通用 / 经典服",
        "why": "用户口径：经典服可能不走后缀，用无后缀 base 表", "table_count": None,
        "state": "已确认", "evidence": "structure", "evidence_level": "static/candidate",
        "status_tags": ["static config"], "source": "toolkit_core/server_types.py",
        "summary": "base 表（无后缀）",
        "provenance": {
            "source_id": "server-types", "source_lock_sha256": "0" * 64,
            "table": "toolkit_core/server_types.py", "row_key": "base",
            "field_refs": ["VARIANT_NAMES"], "name_source": "toolkit_core/server_types.py#VARIANT_NAMES",
            "upstream": {"package_sha256": "0" * 64, "entry_index": None, "file_id": None,
                         "decoded_sha256": None, "role": "server_types"},
            "locator_chain": {"chain_status": "replayed-structural", "scope": "record",
                              "no_cross_source_field_join": True,
                              "steps": [{"kind": "decoded-table-row", "source_id": "server-types",
                                         "table": "toolkit_core/server_types.py", "row_key": "base",
                                         "field_refs": ["name"]}]},
        },
    })

    board = {
        "meta": {
            "name": "服型总表 · 服务器类型后缀与依据",
            "category": "四、资料层 / （四）服型",
            "source_server": "toolkit_core/server_types.py（唯一来源，依据均可在客户端复核）",
            "package_sha": "0" * 64,
            "generated": datetime.date.today().isoformat(),
            "state_summary": {"static config": len(items)},
            "evidence": "structure",
            "notes": "`_auto_oversea_data_<后缀>` = 服务器类型变体，不是渠道。"
                     "硬核服 yh 无奖池属预期；xq/xyd/cn 用户亦不确定，标待确认，不推断。",
            "provenance": {
                "contract_version": 3, "contract": "frozen-audited-artifact", "audit_status": "passed",
                "source_scope": {"cross_source_policy": "no-cross-source-field-join",
                                 "integer_join_policy": "no-equal-integer-join",
                                 "runtime_final_policy": "unknown-unless-runtime-proven"},
                "source_locks": [{"source_id": "server-types", "sha256": "0" * 64,
                                  "bytes": 0, "mtime_ns": 0, "role": "primary"}],
            },
        },
        "items": items,
    }
    OUT.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT.with_suffix(".js")).write_text(
        "window.WIKI_BOARD_server_types = " + json.dumps(board, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8")
    for it in items:
        print("  %-10s %-20s %s" % (it["suffix"] or "base", it["name"], it["summary"]))
    print("写", OUT.name, len(items), "条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
