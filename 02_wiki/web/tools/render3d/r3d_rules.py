# -*- coding: utf-8 -*-
"""r3d_rules.py — 索引 → 选型 的可复算规则 + golden_set 全量一致率验证

★ 这是流水线唯一「怎么从 fashion_index.json 选一套部件」的口径来源。
  改 rules/render3d.yml 的 selection_rules 必须同步改本文件，反之亦然。

规则（2026-11-07 实测，5/5 重现 11-02 既有产物）：
  R1 按 (series, gender) 分组；根优先级 players2025 > players2021，
     某组存在 2025 目录则只用 2025（重制款），players 老根一律排除。
  R2 players2025 容器：
     - container 里的系列号必须等于组 series，否则记 excluded（跨容器串号）
     - 同 prefix 优先 tail 以 _link 结尾（全件合体），再取 tail 字典序最小
     - primary_mesh 为空的目录跳过（如 _c_link 空壳）
  R3 players2021：
     - prefix → part_id：b=body / h=hair / bag=bag / suit=suit
     - b_ 目录内若存在 h_<gender>_<series>.mesh ⇒ 追加 hair（同目录多件）
     - b_ 目录内若存在 <stem>_1.mesh ⇒ 追加 outer（外层件）
     - 只对 b_ 目录做多 mesh 派生，避免把 bag 的 _1 误当成 outer
  R4 无法唯一判定 ⇒ status=unresolved，写报告，不猜不补（fail-closed）。

用法：
  python r3d_rules.py --check          # golden 一致率（只读）
  python r3d_rules.py --survey         # 全量索引可判定率统计（只读）
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys

from r3d_core import FASHION_INDEX, PE_CHARACTER, contract, golden, read_json

PREFIX_PART = {"b": "body", "h": "hair", "bag": "bag", "suit": "suit"}
PART_LABEL = {"body": "衣服", "hair": "头发", "bag": "背包",
              "suit": "整套", "outer": "外层件"}
PART_ORDER = {"body": 0, "outer": 1, "hair": 2, "bag": 3, "suit": 4}
_CONTAINER_SERIES = re.compile(r"_([0-9]{3,6})(?:_|$)")


def _rel(key: str) -> str:
    """索引 key（character/... 或 .../character/...）→ character 下相对路径。"""
    s = key.replace("\\", "/").lstrip("/")
    if s.startswith("character/"):
        return s[len("character/"):]
    i = s.find("/character/")
    return s[i + len("/character/"):] if i >= 0 else s


def _groups(idx: dict) -> dict:
    g = collections.defaultdict(list)
    for key, v in idx["dirs"].items():
        if v.get("root") not in ("players2025", "players2021"):
            continue
        if not v.get("series") or not v.get("gender"):
            continue
        g[(str(v["series"]), str(v["gender"]))].append((_rel(key), v))
    return g


def _container_ok(v: dict, series: str) -> bool:
    c = v.get("container")
    if not c:
        return True
    m = _CONTAINER_SERIES.search(c + "_")
    return (not m) or m.group(1) == series


def _pick_2025(rows: list, series: str) -> tuple[dict, list]:
    """返回 {prefix: (rel, v)} 与被排除记录。"""
    excluded = []
    by_prefix = collections.defaultdict(list)
    for rel, v in rows:
        if not _container_ok(v, series):
            excluded.append({"rel": rel, "reason": "跨容器串号（container 系列号 ≠ group series）"})
            continue
        if not v.get("primary_mesh"):
            continue
        by_prefix[v.get("prefix")].append((rel, v))
    picked = {}
    for pre, cand in by_prefix.items():
        if pre not in PREFIX_PART:
            continue
        links = [x for x in cand if str(x[1].get("tail") or "").endswith("_link")]
        pool = links or cand
        picked[pre] = sorted(pool, key=lambda x: str(x[1].get("tail") or ""))[0]
    return picked, excluded


def _pick_2021(rows: list, series: str, gender: str) -> tuple[list, list]:
    """返回 [(part_id, label, mesh_rel)] 与 unresolved 记录。"""
    parts, unresolved = [], []
    for rel, v in sorted(rows, key=lambda x: x[0]):
        pre = v.get("prefix")
        pm = v.get("primary_mesh")
        if not pm:
            continue
        if pre == "b":
            parts.append(("body", "衣服", rel + "/" + pm))
            names = set(v.get("meshes") or [])
            stem = pm[:-5] if pm.endswith(".mesh") else pm
            # 同目录的头发件（2021 款没有独立 h_ 目录）
            hair = "h_%s_%s.mesh" % (gender, series)
            if hair in names and hair != pm:
                parts.append(("hair", "头发", rel + "/" + hair))
            # 同目录的外层件（3223 有、3245 无）
            outer = stem + "_1.mesh"
            if outer in names:
                parts.append(("outer", "外层件", rel + "/" + outer))
        elif pre in ("h", "bag", "suit"):
            parts.append((PREFIX_PART[pre], PART_LABEL[PREFIX_PART[pre]], rel + "/" + pm))
        else:
            unresolved.append({"rel": rel, "reason": "未知 prefix=%s，不猜部件语义" % pre})
    parts.sort(key=lambda p: PART_ORDER.get(p[0], 99))
    return parts, unresolved


def build_specs_from_index(idx: dict, only: list | None = None) -> tuple[list, dict]:
    """全量按规则生成 spec。返回 (specs, audit)。不做任何写盘。"""
    groups = _groups(idx)
    specs, audit = [], {
        "groups_total": len(groups), "groups_selected": 0, "groups_unresolved": 0,
        "excluded": [], "unresolved": [],
    }
    for (series, gender), rows in sorted(groups.items()):
        oid = "%s_%s" % (series, gender)
        if only and oid not in only:
            continue
        roots = {v.get("root") for _, v in rows}
        use = "players2025" if "players2025" in roots else "players2021"
        sub = [(r, v) for r, v in rows if v.get("root") == use]
        unresolved = []
        if use == "players2025":
            picked, excluded = _pick_2025(sub, series)
            audit["excluded"].extend({"outfit_id": oid, **e} for e in excluded)
            parts = [(PREFIX_PART[pre], PART_LABEL[PREFIX_PART[pre]],
                      rel + "/" + v["primary_mesh"])
                     for pre, (rel, v) in sorted(picked.items())]
            parts.sort(key=lambda p: PART_ORDER.get(p[0], 99))
            note = "players2025 重制款，_link 目录为全件合体"
        else:
            parts, unresolved = _pick_2021(sub, series, gender)
            note = "players2021 分件组合"
        if not parts:
            unresolved.append({"rel": oid, "reason": "规则未选出任何部件"})
        if unresolved:
            audit["groups_unresolved"] += 1
            audit["unresolved"].extend({"outfit_id": oid, **u} for u in unresolved)
            continue
        audit["groups_selected"] += 1
        specs.append({
            "id": oid, "series": series, "gender": gender,
            "label": "%s · %s · %s" % (series, "女" if gender == "f" else "男", note),
            "note": note, "root": use,
            "parts": parts, "selection_basis": "r3d_rules R1-R4 (rules/render3d.yml)",
        })
    return specs, audit


def build_specs_from_golden(c: dict | None = None) -> list:
    """冻结基准直接成 spec（字面量，顺序照契约，不运行时反推）。"""
    out = []
    for g in golden(c):
        out.append({
            "id": g["id"], "series": str(g["series"]), "gender": g["gender"],
            "label": g["label"], "note": g.get("note", ""),
            "root": "players2025" if "players2025" in g["parts"][0]["source_mesh"] else "players2021",
            "parts": [(p["part_id"], p["label"], p["source_mesh"]) for p in g["parts"]],
            "selection_basis": "rules/render3d.yml golden_set（字面量）",
        })
    return out


def check_golden_agreement(idx: dict, c: dict | None = None) -> dict:
    """全量一致率验证：规则生成的 (part_id, source_mesh) 集合 vs 冻结基准。"""
    c = c or contract()
    need = int(c["selection_rules"]["require_golden_agreement"])
    ids = [g["id"] for g in golden(c)]
    specs, _ = build_specs_from_index(idx, only=ids)
    by_id = {s["id"]: s for s in specs}
    rows = []
    for g in golden(c):
        want = {(p["part_id"], p["source_mesh"]) for p in g["parts"]}
        got = {(p[0], p[2]) for p in by_id.get(g["id"], {}).get("parts", [])}
        rows.append({
            "id": g["id"], "ok": want == got,
            "want": sorted(want), "got": sorted(got),
            "only_in_golden": sorted(want - got), "only_in_rules": sorted(got - want),
        })
    ok = sum(1 for r in rows if r["ok"])
    return {"agreement": "%d/%d" % (ok, len(rows)), "required": "%d/%d" % (need, len(rows)),
            "pass": ok == len(rows) and ok >= need, "rows": rows}


def survey(idx: dict) -> dict:
    """全量索引可判定率（只读评估，不落盘、不出图）。"""
    specs, audit = build_specs_from_index(idx)
    root_cnt = collections.Counter(s["root"] for s in specs)
    part_cnt = collections.Counter(len(s["parts"]) for s in specs)
    return {
        "groups_total": audit["groups_total"],
        "groups_selected": audit["groups_selected"],
        "groups_unresolved": audit["groups_unresolved"],
        "excluded_cross_container": len(audit["excluded"]),
        "unresolved_records": len(audit["unresolved"]),
        "specs_by_root": dict(root_cnt),
        "parts_per_spec": dict(sorted(part_cnt.items())),
        "sample_excluded": audit["excluded"][:5],
        "sample_unresolved": audit["unresolved"][:5],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="3D 选型规则：golden 回归 / 全量普查")
    ap.add_argument("--check", action="store_true", help="golden_set 全量一致率")
    ap.add_argument("--survey", action="store_true", help="全量索引可判定率统计")
    args = ap.parse_args()
    if not (args.check or args.survey):
        ap.print_help()
        return 2
    idx = read_json(FASHION_INDEX)
    if args.check:
        r = check_golden_agreement(idx)
        for row in r["rows"]:
            print("  %-10s %s  want=%d got=%d" % (
                row["id"], "OK " if row["ok"] else "FAIL", len(row["want"]), len(row["got"])))
            if not row["ok"]:
                print("     仅基准有:", row["only_in_golden"])
                print("     仅规则有:", row["only_in_rules"])
        print("一致率 %s（要求 %s）⇒ %s" % (r["agreement"], r["required"], "PASS" if r["pass"] else "FAIL"))
        if not r["pass"]:
            return 1
    if args.survey:
        print(json.dumps(survey(idx), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
