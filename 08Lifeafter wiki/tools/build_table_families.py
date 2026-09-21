# -*- coding: utf-8 -*-
"""P1-11：表族成员关系正式固化（family members 结构关系，无运行时推断）。

输入：data/table_index_entries.jsonl（P1-10）+ id_locator_index.db（fid join）
每个 family（表族主名=剥离族后缀后）：
- 按 client 分别记录成员：client/package/FID/entry/role/member_type/evidence
- role 槽规范化：后缀序列完整保留（_base_chs→base_chs）；
  主名无后缀 + merge_shell → merged（合并壳，1765 类先例）
  主名无后缀 + table_body  → main（主表数据体）
  主名无后缀 + 纯代码      → code（模块成员，不计入槽完整性）
  双端同一规则（live 行的 table_body/merge_shell 由 test 源 fid 继承）
- 完整性（6 槽）：{base, base_chs, inc, inc_chs, del, merged} 全有=complete；
  缺槽写入 missing（不补造）
- 族型：code_only（无表结构）/ main_only（主表或 chs 单件，无 6 槽族结构）/
        structural（含族结构槽，可能完整或缺失）
- 不推断运行时合并顺序、不解释字段、不生成 effective table。
输出：data/table_families_v2.json（族级结构 + 统计）
"""
from __future__ import annotations

import json
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRIES = ROOT / "data" / "table_index_entries.jsonl"
DB = ROOT / "data" / "id_locator_index.db"
OUT = ROOT / "data" / "table_families_v2.json"

SLOT_SUFFIXES = ("_base_chs", "_base", "_inc_chs", "_inc", "_del", "_merged",
                 "_chs")
COMPLETE_SLOTS = ("base", "base_chs", "inc", "inc_chs", "del", "merged")
STRUCT_ROLES = {"base", "base_chs", "inc", "inc_chs", "del", "merged"}


def split_suffix(basename: str) -> tuple[str, str | None]:
    """返回 (family, 后缀 role 或 None)。后缀完整保留。"""
    stem = basename[:-3] if basename.endswith(".py") else basename
    for suf in SLOT_SUFFIXES:
        if stem.endswith(suf):
            return stem[: -len(suf)], suf[1:]
    return stem, None


def slot_and_type(r: dict) -> tuple[str, str]:
    """统一归槽：后缀优先；无后缀按 body/merge 归位。"""
    name = r["table_name"]
    if not name:
        return "unknown", "unknown"
    basename = name.replace("/", "\\").split("\\")[-1]
    family, suf = split_suffix(basename)
    if suf is not None:
        if r["table_body"]:
            return family, suf
        # 壳型后缀成员（del/merged 壳、chs 壳、base 代码壳）仍属槽，类型区分
        return family, suf
    if r["merge_shell"]:
        return family, "merged"
    if r["table_body"]:
        return family, "main"
    return family, "code"


def main() -> int:
    rows = []
    with ENTRIES.open(encoding="utf-8") as f:
        for ln in f:
            rows.append(json.loads(ln))
    con = sqlite3.connect(DB)
    fid_map = {}
    for (client, pkg, entry, ident) in con.execute(
            "SELECT client_channel, package, entry_index, identifier FROM "
            "locations WHERE identifier_type='fid'"):
        fid_map[(client, pkg, entry)] = ident

    fams: dict[str, dict] = defaultdict(lambda: defaultdict(list))
    role_count = Counter()
    for r in rows:
        if not r["table_name"]:
            continue
        family, slot = slot_and_type(r)
        member_type = ("body" if r["table_body"] else
                       "merge_shell" if r["merge_shell"] else "code_shell")
        rec = {
            "client_channel": r["client_channel"],
            "package": r["package"],
            "fid": fid_map.get((r["client_channel"], r["package"], r["entry"])),
            "entry": r["entry"],
            "role": slot,
            "member_type": member_type,
            "size": r.get("size"),
            "evidence": r["evidence"],
        }
        fams[family][r["client_channel"]].append(rec)
        role_count[(r["client_channel"], slot)] += 1

    fam_out = []
    n_code_only = n_main_only = n_structural = 0
    complete_by_client = {"test": 0, "live": 0}
    unresolved_issues = []
    for family in sorted(fams):
        per_client = {}
        for client in ("test", "live"):
            members = fams[family].get(client, [])
            if not members:
                per_client[client] = {"present": False}
                continue
            slots: dict[str, list] = defaultdict(list)
            for m in members:
                slots[m["role"]].append(m)
            present = set(slots)
            missing = [s for s in COMPLETE_SLOTS if s not in present]
            complete = not missing
            if complete:
                complete_by_client[client] += 1
            per_client[client] = {
                "present": True,
                "members": [{"fid": m["fid"], "entry": m["entry"],
                             "package": m["package"], "role": m["role"],
                             "member_type": m["member_type"],
                             "evidence": m["evidence"]} for m in members],
                "slots": {k: [{"fid": m["fid"], "entry": m["entry"],
                               "package": m["package"],
                               "member_type": m["member_type"]}
                              for m in v] for k, v in slots.items()},
                "missing": missing,
                "complete": complete,
            }
        t = per_client["test"]
        t_roles = {m["role"] for m in t["members"]} if t["present"] else set()
        if not t["present"]:
            fam_type = "live_only"
        elif not (t_roles & (STRUCT_ROLES | {"main"})) and not any(
                m["member_type"] == "body" for m in t["members"]):
            fam_type = "code_only"
            n_code_only += 1
        elif not (t_roles & STRUCT_ROLES):
            fam_type = "main_only"
            n_main_only += 1
        else:
            fam_type = "structural"
            n_structural += 1
        fam_out.append({"family": family, "type": fam_type,
                        "clients": per_client})

    # 异常检查
    dup = []
    nofid = 0
    live_missing_but_test_present = 0
    for f in fam_out:
        for client, info in f["clients"].items():
            if not info.get("present"):
                continue
            seen = set()
            for m in info["members"]:
                if m["fid"] is None:
                    nofid += 1
                k = (m["entry"], m["package"])
                if k in seen:
                    dup.append((f["family"], client, k[0], k[1]))
                seen.add(k)
        tc = f["clients"]["test"]
        lc = f["clients"].get("live")
        if tc["present"] and (not lc or not lc["present"]):
            pass
    if dup:
        unresolved_issues.append({"issue": "duplicate-entry-same-position",
                                  "cases": dup[:20]})
    if nofid:
        unresolved_issues.append({"issue": "members-without-fid", "count": nofid})

    stats = {
        "family_total": len(fam_out),
        "family_types": {"code_only": n_code_only, "main_only": n_main_only,
                         "structural": n_structural},
        "complete_families": complete_by_client,
        "incomplete_structural": {
            "test": sum(1 for f in fam_out
                        if f["type"] == "structural"
                        and not f["clients"]["test"]["complete"]),
            "live": sum(1 for f in fam_out
                        if f["type"] == "structural"
                        and f["clients"]["live"].get("present")
                        and not f["clients"]["live"]["complete"]),
        },
        "role_counts": {f"{c}:{role}": role_count[(c, role)]
                        for c, role in sorted(role_count)},
        "family_shared": len({f["family"] for f in fam_out
                              if f["clients"]["live"].get("present")}),
        "family_test_only": sum(1 for f in fam_out
                                if f["clients"]["test"]["present"]
                                and not f["clients"]["live"].get("present")),
        "unresolved": unresolved_issues,
        "note": "family=剥离族后缀主名；role=完整后缀序列或 main/merged/code 归位；"
                "complete=6 槽{base,base_chs,inc,inc_chs,del,merged}全有；"
                "missing 不补造；不推断合并顺序；无字段语义；server_branch=unresolved",
    }
    doc = {"schema": "lifeafter-table-family-relations-v1", "stats": stats,
           "families": fam_out}
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=1))
    print("->", OUT.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
