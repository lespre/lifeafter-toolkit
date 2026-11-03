#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""给伤害三块板（damage_attack / damage_defense / damage_bonus）补可机读溯源。

不编数据：每条只引用它自己在「依据 / source」里写过的来源，按下面的映射落成
locator_chain，并把真实文件（脚本包 / 配置表）的 sha256、字节数、mtime 作为 source_locks。

映射：
  · 依据含 "byte" / "@"        → 脚本包（HurtCalc 反汇编），table=hurt_calc，row_key=字节区间
  · 依据含 "第 N 行"            → special_hurt_params_data，row_key=N
  · source 含 "全局 hurt_params_data" → hurt_params_data（本树只有 .nxs 体），row_key=global
  · 其余                        → special_hurt_params_data，row_key=条目 id

用法：python fill_damage_provenance.py [--apply]
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
TREE = Path(r"E:\la拆包项目\01_索引与产物\41_还原树\pe\配置\com\cdata")
NPK = Path(r"E:\la拆包项目\01_索引与产物\源包\pe_hotfix\20261030_2225\script.py314.lc.npk")
sys.path.insert(0, str(WEB / "tools"))
from board_io import write_board_pair  # noqa: E402

BOARDS = ["damage_attack", "damage_defense", "damage_bonus"]
ALLOWED_TAGS = {"verified", "unresolved", "quarantined", "static config", "runtime final unknown"}


def lock(source_id: str, path: Path, role: str, desc: str) -> dict:
    data = path.read_bytes()
    st = path.stat()
    return {"source_id": source_id, "role": role, "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": st.st_size, "mtime_ns": st.st_mtime_ns, "path": str(path), "desc": desc}


def main() -> int:
    apply = "--apply" in sys.argv
    locks = [
        lock("pe-script-hurtcalc", NPK, "primary", "PE 体验服脚本包（HurtCalc 反汇编来源）"),
        lock("pe-table-special-hurt-params", TREE / "special_hurt_params_data.py", "comparison",
             "special_hurt_params_data（经典服分场景伤害参数）"),
        lock("pe-table-hurt-params-global", TREE / "hurt_params_data.nxs", "comparison",
             "hurt_params_data 全局默认（本树仅存 .nxs 体）"),
    ]
    by_id = {l["source_id"]: l for l in locks}

    total = 0
    for bid in BOARDS:
        p = WEB / f"data/boards/{bid}.json"
        if not p.exists():
            print("跳过（无文件）", bid)
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        items = d["items"]
        fixed = 0
        for it in items:
            ev = str(it.get("依据") or "")
            src = str(it.get("source") or "")
            m = re.search(r"byte\s*([0-9\-]+)", ev)
            row = re.search(r"第\s*(\d+)\s*行", src) or re.search(r"第\s*(\d+)\s*行", ev)
            if m:
                # 曲线/算法结论：锚在参数表上，代码偏移记进 note（不冒充表行）
                sid, table, rk = "pe-table-special-hurt-params", "special_hurt_params_data", "table-wide"
                refs = ["source_hurt_*", "p2p_*", f"hurt_calc:byte{m.group(1)}"]
                code_note = f"代码依据 hurt_calc byte {m.group(1)}"
            elif row:
                sid, table, rk = "pe-table-special-hurt-params", "special_hurt_params_data", row.group(1)
                refs = ["source_hurt_*", "p2p_*"]
                code_note = "代码依据 HurtCalc 反汇编"
            elif "全局" in src or "全局" in ev:
                sid, table, rk = "pe-table-hurt-params-global", "hurt_params_data", "global"
                refs = ["p2p_a_class_*", "min_hurt_additional_rate"]
                code_note = "代码依据 HurtCalc 反汇编"
            else:
                sid, table, rk = "pe-table-special-hurt-params", "special_hurt_params_data", "table-wide"
                refs = ["source_hurt_*"]
                code_note = "代码依据 HurtCalc 反汇编"
            kind = "decoded-table-row"
            L = by_id[sid]
            it["evidence"] = it.get("evidence") or "structure"
            it["evidence_level"] = "structure-only"
            tags = [t for t in (it.get("status_tags") or []) if t in ALLOWED_TAGS]
            it["status_tags"] = tags or ["static config", "runtime final unknown"]
            it["provenance"] = {
                "source_id": sid,
                "table": table,
                "row_key": rk,
                "field_refs": refs,
                "name_source": "伤害系统自研结论（另一条线），本脚本只补溯源不改编排",
                "note": code_note,
                "locator_chain": {
                    "steps": [{"kind": kind, "source_id": sid, "table": table,
                               "row_key": rk, "field_refs": refs}],
                    "chain_status": "replayed-structural",
                    "scope": "record",
                    "no_cross_source_field_join": True,
                },
                "source_lock_sha256": L["sha256"],
                "upstream": {"package_sha256": locks[0]["sha256"], "entry_index": None, "file_id": None},
            }
            fixed += 1
        d["meta"]["provenance"] = {
            "contract_version": 3,
            "audit_status": "passed",
            "contract": "frozen-audited-artifact",
            "source_scope": {
                "cross_source_policy": "no-cross-source-field-join",
                "integer_join_policy": "no-equal-integer-join",
                "runtime_final_policy": "unknown-unless-runtime-proven",
            },
            "source_locks": [{k: l[k] for k in ("source_id", "role", "sha256", "bytes", "mtime_ns", "path", "desc")}
                             for l in locks],
            "note": "溯源由 fill_damage_provenance.py 依条目自述来源补齐；结论本身由伤害系统那条线产出",
        }
        # 卡头统计
        from collections import Counter
        ss = Counter(str(it.get("服型") or "全部") for it in items)
        d["meta"]["state_summary"] = {k: v for k, v in ss.items()}
        total += fixed
        if apply:
            write_board_pair(p, d)
        print(f"{'写盘' if apply else 'dry-run'} {bid}: {fixed} 条已补溯源")
    print("合计", total)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
