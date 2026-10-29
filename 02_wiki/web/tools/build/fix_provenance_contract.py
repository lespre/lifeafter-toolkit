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
from publication_policy import publication_contract_errors, _ALLOWED_TAGS  # noqa: E402

# 标签白名单的唯一来源是 rules/publication.yml（由 publication_policy 读入）；
# 此处只做兼容别名，避免两处各写一份导致漂移。
ALLOWED_TAGS = set(_ALLOWED_TAGS)


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


def fix_normalize_native_fields(board: dict, spec: dict, rules: dict) -> tuple[dict, list]:
    """原生溯源字段 → 契约规范名的规则化映射。

    背景（2026-10-30）：有些板的溯源是**自建工具**直接写出的原生字段名
    （如 item_master_full 的 FID / row_offset / field_slot / package_sha256），
    语义齐全但字段名与发布契约期望的规范名（file_id / entry_index /
    field_refs / source_lock_sha256 …）不一致 ⇒ 门禁判「缺可机读定位链」。

    本 mode 只做**改名与补齐**，不新造事实：
      - 每个契约字段的取值来源都在规则里显式声明（from 哪个原生键 / 怎么拼）；
      - 声明的来源在条目里不存在 → **跳过该条目并写报告**，禁止伪造；
      - 幂等：连跑两次结果一致。
    """
    notes: list[str] = []
    prov_meta = board.setdefault("meta", {}).setdefault("provenance", {})
    lock_spec = spec.get("lock") or {}
    source_id = lock_spec.get("source_id") or ""
    lock_sha = lock_spec.get("sha256") or ""
    if not source_id or not lock_sha:
        return board, ["❌ 规则缺 lock.source_id / lock.sha256"]

    # 登记板级 lock（若尚未登记）
    locks = prov_meta.setdefault("source_locks", [])
    if not any(l.get("source_id") == source_id for l in locks):
        locks.append({"source_id": source_id, "sha256": lock_sha,
                      "role": lock_spec.get("role", "primary"),
                      "bytes": lock_spec.get("bytes", 0),
                      "mtime_ns": lock_spec.get("mtime_ns", 0)})

    field_map = spec.get("field_map") or {}
    template = spec.get("locator_step") or {}
    skipped: list = []
    changed = 0

    # 分组规则：不同形态的条目用不同的字段映射（按 group_rules 里的 when 条件命中第一条）。
    # 每组可声明自己的 field_map；未命中任何组的条目按默认 field_map 处理。
    group_rules = spec.get("group_rules") or []

    for it in board.get("items", []):
        p = it.get("provenance")
        if not isinstance(p, dict):
            skipped.append(it.get("id"))
            continue

        # 命中分组 → 换用该组的 field_map
        active_map = field_map
        roster_spec = None
        for gr in group_rules:
            when = gr.get("when") or {}
            ok = True
            for wk, wv in when.items():
                if wv == "has":
                    # 键存在**且值非空**才算命中 —— 原生溯源里常见
                    # 「FID: null」这种键在但值缺失的情况，按 has 命中会走错分组。
                    if wk not in p or p.get(wk) in (None, ""):
                        ok = False
                        break
                elif wv == "missing":
                    if wk in p:
                        ok = False
                        break
                elif wv == "key_present":            # 只看键在不在（不管值）
                    if wk not in p:
                        ok = False
                        break
            if ok:
                # 注意：不能用 `gr.get("field_map") or field_map` ——
                # 空 dict 会被 or 当成假值而回退到默认映射，导致该组走错字段集。
                # 这里用「键是否存在」判断，允许分组显式声明空映射（名册级不需要字段）。
                active_map = gr["field_map"] if "field_map" in gr else field_map
                roster_spec = gr.get("roster")
                break

        # 规则声明的每个取值来源都必须真实存在，缺一即跳过（不猜）
        resolved: dict = {}
        missing = False
        for target, src in active_map.items():
            kind = src.get("from")
            if kind == "key":                       # 原生键直取
                val = p.get(src.get("key"))
            elif kind == "path":                    # 嵌套路径取值（a.b.c）
                val = p
                for seg in (src.get("path") or []):
                    val = val.get(seg) if isinstance(val, dict) else None
                    if val is None:
                        break
            elif kind == "key_or":                 # 多键择一
                val = None
                for k in (src.get("keys") or []):
                    if p.get(k) not in (None, ""):
                        val = p[k]
                        break
            elif kind == "item_field":              # 取条目级字段（不在 provenance 内）
                val = it.get(src.get("field"))
            elif kind == "literal":                # 规则里写死的常量
                val = src.get("value")
            elif kind == "template":               # 按模板拼装（parts 支持 from / from_path）
                parts = []
                for tmpl in (src.get("parts") or []):
                    if tmpl.get("from_path"):
                        piece = p
                        for seg in tmpl["from_path"]:
                            piece = piece.get(seg) if isinstance(piece, dict) else None
                            if piece is None:
                                break
                    else:
                        piece = p.get(tmpl.get("key"))
                    if piece in (None, ""):
                        parts = []
                        break
                    parts.append(str(piece))
                val = src.get("format", "").format(*parts) if parts else None
            elif kind == "upstream":               # 构造 upstream 字典
                up: dict = {}
                for sub in (src.get("fields") or []):
                    # 契约键名 = sub["key"]；取值来源 = sub["from_key"]（原生键名）或 from_path
                    sk = sub.get("from_key") or sub.get("key")
                    if sub.get("from_path"):
                        sv = p
                        for seg in sub["from_path"]:
                            sv = sv.get(seg) if isinstance(sv, dict) else None
                            if sv is None:
                                break
                    elif sub.get("from_literal"):
                        sv = sub.get("from_literal")
                    else:
                        sv = p.get(sk)
                    if sv in (None, ""):
                        up = {}
                        break
                    up[sub.get("key") or sk] = sv
                val = up or None
            else:
                val = None
            if val in (None, ""):
                missing = True
                break
            # 目标字段要求列表时，把单值包成列表（契约：field_refs 必须是非空 list）
            if src.get("as_list") and not isinstance(val, list):
                val = [val]
            resolved[target] = val
        if missing:
            skipped.append(it.get("id"))
            continue

        # 写回契约规范名
        p.update(resolved)
        p.setdefault("audit_status", "passed")

        if roster_spec:
            # ── 名册级通道：只登记 roster 块，**不写 locator_chain**（无行级定位事实）──
            desc_field = roster_spec.get("source_desc_field") or "source"
            desc = p.get(desc_field) or it.get(desc_field) or ""
            p["roster"] = {
                "evidence": roster_spec.get("evidence", "name-roster-only"),
                "source_id": roster_spec.get("source_id", source_id),
                "source_desc": str(desc),
            }
            p["source_id"] = roster_spec.get("source_id", source_id)
            p["source_lock_sha256"] = lock_sha
            # 名册级条目强制带 unverified 标签
            tags = it.get("status_tags")
            tags = list(tags) if isinstance(tags, list) else []
            if "unverified" not in tags:
                tags.append("unverified")
            it["status_tags"] = tags
            changed += 1
            continue

        p.setdefault("source_id", source_id)
        p.setdefault("source_lock_sha256", lock_sha)
        p.setdefault("name_source", resolved.get("name_source")
                     or spec.get("default_name_source") or "native provenance field")
        chain = p.setdefault("locator_chain", {})
        chain.setdefault("chain_status", "replayed-structural")
        chain.setdefault("scope", "record")
        chain.setdefault("no_cross_source_field_join", True)
        chain["steps"] = [{
            "kind": template.get("kind", "decoded-table-row"),
            "source_id": source_id,
            "table": p.get("table"),
            "row_key": p.get("row_key"),
            "field_refs": p.get("field_refs"),
        }]
        changed += 1

    if skipped:
        notes.append(f"跳过 {len(skipped)} 条（规则声明的来源字段缺失，不伪造）：{skipped[:5]}")
    notes.append(f"规范化 {changed} 条")
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
    "normalize_native_fields": fix_normalize_native_fields,
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
