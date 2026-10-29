#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""fix_provenance_contract.py — 溯源契约修复器（规则驱动 / 幂等 / 不伪造）

按 rules/provenance_fixes.yml 修掉已发布板的契约不合格项：
  align_package_lock : 把板级假 lock 换成真实包级 lock，条目 source_id 对齐
  align_lock_by_sha  : 条目按自身 source_lock_sha256 回推 source_id，并补 upstream 表级定位
  stamp_partial      : 条目已有 table/row_key/field_refs 但源未登记 → 登记 lock + 补 locator_chain
  roster_channel     : 名册级条目（无行级溯源）→ 写 roster 块，走契约的「名册级通道」

铁律：
  * 只按规则文件里声明的事实修；推不出来的字段一律跳过并写报告，**不猜、不填占位**；
  * 默认 dry-run，加 --apply 才落盘；
  * 幂等：同规则重复执行结果一致；
  * 落盘前自动备份原板 json 到 02_wiki/state/backups/。

用法：
  python 02_wiki/web/tools/build/fix_provenance_contract.py --list
  python 02_wiki/web/tools/build/fix_provenance_contract.py --board talent_catalog [--apply]
  python 02_wiki/web/tools/build/fix_provenance_contract.py --all --apply
"""
from __future__ import annotations

import argparse
import copy
import datetime
import hashlib
import json
import pathlib
import shutil
import sys

PROJ = pathlib.Path(__file__).resolve().parents[4]
WEB = PROJ / "02_wiki" / "web"
BOARDS = WEB / "data" / "boards"
RULES = PROJ / "02_wiki" / "rules"
STATE = PROJ / "02_wiki" / "state"
sys.path.insert(0, str(WEB / "tools"))

import yaml  # noqa: E402
from publication_policy import publication_contract_errors  # noqa: E402

ALLOWED_TAGS = {"verified", "unresolved", "quarantined", "static config",
                 "runtime final unknown", "unverified"}


def sha256_of(path: pathlib.Path) -> tuple[str, int]:
    h = hashlib.sha256()
    n = 0
    with path.open("rb") as f:
        while True:
            b = f.read(1 << 20)
            if not b:
                break
            h.update(b)
            n += len(b)
    return h.hexdigest(), n


def load_rules() -> dict:
    return yaml.safe_load((RULES / "provenance_fixes.yml").read_text(encoding="utf-8"))


def remap_tags(tags, mapping):
    out = []
    for t in tags or []:
        out.append(mapping.get(t, t))
    return out


# ── 各模式实现 ────────────────────────────────────────────────────────
def fix_align_package_lock(board: dict, spec: dict, rules: dict) -> tuple[dict, list]:
    """恢复真实包级 lock，并把条目 source_id / steps[0].source_id 对齐。"""
    changed = 0
    pk = rules["package_locks"][spec["lock"]]
    prov = board.setdefault("meta", {}).setdefault("provenance", {})
    old_locks = prov.get("source_locks")
    new_locks = [{"source_id": spec["lock"], "role": pk.get("role", "primary"),
                  "sha256": pk["sha256"], "bytes": pk["bytes"], "mtime_ns": pk["mtime_ns"]}]
    if old_locks != new_locks:
        prov["source_locks"] = new_locks
        changed += 1
    for it in board.get("items", []):
        p = it.get("provenance") or {}
        if p.get("source_id") != spec["item_source_id"]:
            p["source_id"] = spec["item_source_id"]
            changed += 1
        chain = p.get("locator_chain") or {}
        for st in chain.get("steps") or []:
            if st.get("source_id") != spec["steps_source_id"]:
                st["source_id"] = spec["steps_source_id"]
                changed += 1
    return board, [f"locks→{spec['lock']}"] if changed else []


def fix_align_lock_by_sha(board: dict, spec: dict, rules: dict) -> tuple[dict, list]:
    """按条目自身 source_lock_sha256 回推 source_id；补 upstream 表级定位。"""
    notes = []
    changed = 0
    prov = board["meta"]["provenance"]
    locks = prov.get("source_locks") or []
    by_sha = {l.get("sha256"): l for l in locks}
    locs = rules.get("table_locators") or {}
    branch_loc = spec.get("upstream_locator_by_branch") or {}
    tag_map = spec.get("status_tag_map") or {}
    role_map = spec.get("lock_role_map") or {}

    for l in locks:
        if l.get("role") in role_map:
            l["role"] = role_map[l["role"]]
            changed += 1

    skipped = []
    for it in board.get("items", []):
        p = it.get("provenance") or {}
        sha = p.get("source_lock_sha256")
        lock = by_sha.get(sha)
        if not lock:
            skipped.append(it.get("id"))
            continue
        sid = lock.get("source_id")
        if p.get("source_id") != sid:
            p["source_id"] = sid
            changed += 1
        chain = p.get("locator_chain") or {}
        for st in chain.get("steps") or []:
            if st.get("source_id") != sid:
                st["source_id"] = sid
                changed += 1
        branch = it.get("server_branch")
        loc_key = branch_loc.get(branch)
        if loc_key:
            loc = locs.get(loc_key)
            if not loc:
                skipped.append(it.get("id"))
                continue
            up = p.setdefault("upstream", {})
            want = {"entry_index": loc["entry_index"], "file_id": loc["file_id"]}
            if up.get("entry_index") != want["entry_index"] or up.get("file_id") != want["file_id"]:
                up.update(want)
                changed += 1
        tags = remap_tags(it.get("status_tags"), tag_map)
        new_tags = [t for t in tags if t in ALLOWED_TAGS]
        if new_tags != it.get("status_tags"):
            it["status_tags"] = new_tags
            changed += 1
    if skipped:
        notes.append(f"跳过 {len(skipped)} 条（无法回推 lock）：{skipped[:5]}")
    return board, notes


def fix_stamp_partial(board: dict, spec: dict, rules: dict) -> tuple[dict, list]:
    """已有 table/row_key/field_refs 但源未登记的条目：登记 lock + 补 locator_chain。"""
    notes = []
    pl = spec["partial_lock"]
    prov = board["meta"]["provenance"]
    locks = prov.setdefault("source_locks", [])
    digest_path = PROJ / pl["file_digest_from"]
    if not digest_path.exists():
        return board, [f"❌ 源文件不存在，无法算 lock 摘要：{digest_path}"]
    sha, size = sha256_of(digest_path)
    mtime = digest_path.stat().st_mtime_ns
    new_lock = {"source_id": pl["source_id"], "role": pl.get("role", "primary"),
                "sha256": sha, "bytes": size, "mtime_ns": mtime,
                "path": pl["file_digest_from"]}
    changed = 0
    if not any(l.get("source_id") == pl["source_id"] for l in locks):
        locks.append(new_lock)
        changed += 1
    else:
        for l in locks:
            if l.get("source_id") == pl["source_id"]:
                l.update(new_lock)
    loc = (rules.get("table_locators") or {}).get(pl["table_locator"]) or {}

    skipped = []
    for it in board.get("items", []):
        p = it.get("provenance") or {}
        if p.get("locator_chain") and p.get("source_id") not in (None, pl["source_id"]):
            continue  # 已有完整链且属别的源 → 不动
        if not p.get("table") or p.get("row_key") is None or not p.get("field_refs"):
            skipped.append(it.get("id"))
            continue
        p["source_id"] = pl["source_id"]
        p["source_lock_sha256"] = sha
        if spec.get("name_source_from_table"):
            p.setdefault("name_source", p["table"])
        chain = p.setdefault("locator_chain", {})
        chain.setdefault("chain_status", "replayed-structural")
        chain.setdefault("scope", "record")
        chain.setdefault("no_cross_source_field_join", True)
        chain["steps"] = [{
            "kind": "decoded-table-row",
            "source_id": pl["source_id"],
            "table": p["table"],
            "row_key": p["row_key"],
            "field_refs": p["field_refs"],
        }]
        up = p.setdefault("upstream", {})
        up["package_sha256"] = pl["package_sha256"]
        if loc:
            up["entry_index"] = loc["entry_index"]
            up["file_id"] = loc["file_id"]
        changed += 1
    if skipped:
        notes.append(f"跳过 {len(skipped)} 条（缺 table/row_key/field_refs）：{skipped[:5]}")
    return board, notes


def fix_roster_channel(board: dict, spec: dict, rules: dict) -> tuple[dict, list]:
    """名册级条目：写 roster 块，status_tags 归一到允许集合，保留原标签于 roster。"""
    rs = spec["roster"]
    tag_map = spec.get("status_tag_map") or {}
    changed = 0
    skipped = []
    for it in board.get("items", []):
        p = it.get("provenance") or {}
        if p.get("locator_chain"):
            continue  # 有行级链 → 名册通道不适用
        desc = it.get(rs.get("source_desc_field", "source"))
        if not desc:
            skipped.append(it.get("id"))
            continue
        orig = list(it.get("status_tags") or [])
        roster = {
            "evidence": rs["evidence"],
            "source_id": rs["source_id"],
            "source_desc": str(desc)[:400],
            "original_status_tags": orig,
        }
        if p.get("roster") != roster:
            p["roster"] = roster
            changed += 1
        tags = remap_tags(orig, tag_map)
        new_tags = [t for t in tags if t in ALLOWED_TAGS] or ["unverified"]
        if "unverified" not in new_tags:
            new_tags.append("unverified")
        if new_tags != it.get("status_tags"):
            it["status_tags"] = new_tags
            changed += 1
        if p.get("source_id") != rs["source_id"]:
            p["source_id"] = rs["source_id"]
            changed += 1
    notes = []
    if skipped:
        notes.append(f"跳过 {len(skipped)} 条（无来源描述）：{skipped[:5]}")
    return board, notes


MODES = {
    "align_package_lock": fix_align_package_lock,
    "align_lock_by_sha": fix_align_lock_by_sha,
    "stamp_partial": fix_stamp_partial,
    "roster_channel": fix_roster_channel,
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--board", help="板 id")
    ap.add_argument("--all", action="store_true", help="所有规则板")
    ap.add_argument("--list", action="store_true", help="列出规则板")
    ap.add_argument("--apply", action="store_true", help="落盘（默认 dry-run）")
    args = ap.parse_args()

    rules = load_rules()
    spec_all = rules.get("boards") or {}
    if args.list or not (args.board or args.all):
        print("规则覆盖的板：")
        for b, s in spec_all.items():
            print(f"  {b:28s} mode={s.get('mode')}")
        return 0

    targets = list(spec_all) if args.all else [args.board]
    report = {"date": datetime.date.today().isoformat(), "applied": args.apply, "boards": {}}
    for bid in targets:
        spec = spec_all.get(bid)
        if not spec:
            print(f"⚠️ 无规则：{bid}")
            continue
        path = BOARDS / f"{bid}.json"
        if not path.exists():
            print(f"⚠️ 板文件不存在：{path}")
            continue
        board = json.loads(path.read_text(encoding="utf-8-sig"))
        before = publication_contract_errors(board, strict_v2=True)
        fn = MODES.get(spec.get("mode"))
        if not fn:
            print(f"⚠️ 未知 mode：{spec.get('mode')}")
            continue
        new_board, notes = fn(copy.deepcopy(board), spec, rules)
        after = publication_contract_errors(new_board, strict_v2=True)
        changed_fields = sum(1 for _ in ())  # 占位，实际差异由契约计数体现
        entry = {
            "mode": spec.get("mode"),
            "errors_before": len(before),
            "errors_after": len(after),
            "notes": notes,
            "remaining_kinds": sorted({e.split(".")[-1] for e in after})[:10],
        }
        if args.apply and len(after) < len(before):
            bak = STATE / "backups" / f"{bid}_{datetime.datetime.now():%Y%m%d_%H%M%S}.json"
            bak.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, bak)
            path.write_text(json.dumps(new_board, ensure_ascii=False, indent=1), encoding="utf-8")
            entry["backup"] = str(bak.relative_to(PROJ))
            entry["written"] = True
        else:
            entry["written"] = False
        report["boards"][bid] = entry
        flag = "✅" if entry["written"] else ("·" if not args.apply else "✋")
        print(f"{flag} {bid:28s} {spec.get('mode'):20s} 错误 {len(before)} → {len(after)}")
        for n in notes:
            print(f"    {n}")
        if after:
            print(f"    残留类型: {entry['remaining_kinds']}")

    out = STATE / "provenance_fix_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n报告：{out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
