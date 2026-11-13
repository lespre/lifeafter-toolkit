# -*- coding: utf-8 -*-
"""s3_verify.py — Stage 3 质检与溯源报告（fail-closed）

红灯（exit 1）：GLB 头非法 / 空件 / missing[] 非空 / golden 回归不一致 /
                几何语义差异 semantic_diff / 保真标注与契约不符
黄灯（记录但不失败）：path_literal_only（既有 GLB 内嵌设备绝对路径）
绿灯：identical

★ 不改写任何既有产物，不伪造 locator_chain；拿不到的证据写 unresolved。
用法：
  python s3_verify.py            # 只体检，写 state/render3d/verify_report.json
  python s3_verify.py --strict   # 把 path_literal_only 也当红灯（发布前用）
"""
from __future__ import annotations

import argparse
import json
import sys

from r3d_core import (
    FASHION_3D, FASHION_INDEX, ROSTER, STATE, STAGING, VERIFY_REPORT,
    canonicalize_paths, contract, ensure_state, glb_chunks, glb_equivalence,
    golden, read_json, sha256_file, write_json_idempotent,
)
from r3d_rules import check_golden_agreement, survey


def fingerprint(units: list) -> dict:
    out = {}
    for uid in units:
        d = STAGING / uid
        if not d.exists():
            continue
        out[uid] = {f.name: sha256_file(f) for f in sorted(d.iterdir()) if f.is_file()}
    return out


def canonical_viewer(vj: dict) -> str:
    """viewer.json 语义比较：忽略 parts[].bytes（随 GLB 内嵌路径长度变化）。"""
    d = json.loads(json.dumps(vj, ensure_ascii=False))
    for p in d.get("parts", []):
        p.pop("bytes", None)
    return json.dumps(d, ensure_ascii=False, sort_keys=True)


def check_unit(uid: str, roster_unit: dict, gold_map: dict, fid_default: str, strict: bool) -> dict:
    sd, td = STAGING / uid, FASHION_3D / uid
    r = {"id": uid, "red": [], "yellow": [], "green": [],
         "glb": {}, "viewer_equivalence": None, "golden": None, "fidelity": None}
    if not sd.exists():
        r["red"].append("staging 目录不存在（Stage 2 未跑或导出失败）")
        return r
    sv = sd / "viewer.json"
    if not sv.exists():
        r["red"].append("staging 缺 viewer.json")
        return r
    vj = json.loads(sv.read_text(encoding="utf-8"))

    # ── 保真标注与契约一致性
    r["fidelity"] = vj.get("material")
    if vj.get("material") != fid_default:
        r["red"].append("保真标注 %r ≠ 契约 default %r" % (vj.get("material"), fid_default))

    # ── 逐部件：GLB 头 / 空件 / 缺贴图 / 与既有产物结构等价
    for p in vj.get("parts", []):
        pid, fn = p.get("id"), p.get("file")
        g = sd / (fn or "")
        info = glb_chunks(g)
        if not info["valid"]:
            r["red"].append("%s.glb 头非法：%s" % (pid, info.get("error")))
            r["glb"][pid] = {"valid": False}
            continue
        if not (p.get("vertices") or 0) or not (p.get("submeshes") or 0):
            r["red"].append("%s 空件（vertices=%s submeshes=%s）" % (
                pid, p.get("vertices"), p.get("submeshes")))
        if p.get("missing"):
            r["red"].append("%s 缺贴图 %d 项（不顶替）" % (pid, len(p["missing"])))
        if any("无同名 .mtg" in w for w in p.get("warnings", [])):
            r["red"].append("%s 无同名 .mtg，导出器已降级为纯白模" % pid)
        eq = glb_equivalence(g, td / (fn or ""))
        r["glb"][pid] = {"valid": True, "equivalence": eq,
                         "json_bytes": info["json_bytes"], "bin_bytes": info["bin_bytes"]}
        if eq == "identical":
            r["green"].append("%s 与既有产物字节一致" % pid)
        elif eq == "path_literal_only":
            msg = "%s 仅设备绝对路径字面量不同（几何/材质/BIN 完全一致）" % pid
            (r["red"] if strict else r["yellow"]).append(msg)
        elif eq == "semantic_diff":
            r["red"].append("%s 几何/材质语义差异，导出器或源发生漂移" % pid)
        elif eq == "missing":
            r["yellow"].append("%s 既有产物不存在（新增单元）" % pid)
        else:
            r["red"].append("%s 既有产物 GLB 非法" % pid)

    # ── viewer.json 与既有对照（忽略 bytes 字段）
    tv = td / "viewer.json"
    if tv.exists():
        other = json.loads(tv.read_text(encoding="utf-8"))
        r["viewer_equivalence"] = ("same" if canonical_viewer(vj) == canonical_viewer(other)
                                   else "semantic_diff")
        if r["viewer_equivalence"] == "semantic_diff":
            r["red"].append("viewer.json 与既有产物语义不一致（不只是 bytes 变化）")
    else:
        r["viewer_equivalence"] = "new"

    # ── golden 冻结基准回归
    g = gold_map.get(uid)
    if g:
        want = {(p["part_id"], p["source_mesh"]) for p in g["parts"]}
        got = {(p["id"], p["source_mesh"]) for p in vj.get("parts", [])}
        vmap = {p["id"]: p for p in vj.get("parts", [])}
        vert_bad = [p["part_id"] for p in g["parts"]
                    if (vmap.get(p["part_id"], {}).get("vertices") != p["vertices"]
                        or vmap.get(p["part_id"], {}).get("submeshes") != p["submeshes"])]
        ok = (want == got and not vert_bad)
        r["golden"] = {"ok": ok, "want": len(want), "got": len(got),
                       "only_in_golden": sorted(want - got), "only_in_staging": sorted(got - want),
                       "vertices_mismatch": vert_bad}
        if not ok:
            r["red"].append("golden 回归失败：来源/顶点数与 11-02 冻结基准不一致")
        else:
            r["green"].append("golden 回归 PASS（%d 部件）" % len(want))
    return r


def main() -> int:
    ap = argparse.ArgumentParser(description="Stage 3 · 质检与溯源报告")
    ap.add_argument("--strict", action="store_true", help="把 path_literal_only 也判红灯")
    args = ap.parse_args()

    ensure_state()
    roster = read_json(ROSTER)
    c = contract()
    gold_map = {g["id"]: g for g in golden(c)}
    fid = c["fidelity"]["default"]
    idx = read_json(FASHION_INDEX)
    agree = check_golden_agreement(idx, c)

    units = [u["id"] for u in roster["units"] if (STAGING / u["id"]).exists()]
    if not units:
        print("❌ staging 无任何单元；先跑 s2_export.py")
        return 2
    rmap = {u["id"]: u for u in roster["units"]}
    results = [check_unit(uid, rmap.get(uid, {}), gold_map, fid, args.strict) for uid in units]

    fp = fingerprint(units)
    prev = read_json(VERIFY_REPORT, default={})
    prev_fp = prev.get("staging_fingerprint")
    reproducible = (prev_fp == fp) if prev_fp else None

    red = [(r["id"], m) for r in results for m in r["red"]]
    yellow = [(r["id"], m) for r in results for m in r["yellow"]]
    report = {
        "schema_version": 1, "scope": "research-prototype",
        "strict": args.strict,
        "contract_version": c["version"],
        "golden_agreement": agree["agreement"], "golden_pass": agree["pass"],
        "coverage_survey": survey(idx),
        "units_checked": len(results),
        "red_count": len(red), "yellow_count": len(yellow),
        "red": [{"id": i, "msg": m} for i, m in red],
        "yellow": [{"id": i, "msg": m} for i, m in yellow],
        "units": results,
        "staging_fingerprint": fp,
        "reproducible": reproducible,
        "known_gaps": c["fidelity"]["known_gaps"],
        "unresolved_note": (
            "既有 GLB 的 extras 内嵌本机绝对路径（e:/la拆包项目/...），换机即失效；"
            "本轮按方针不改写 45MB 既有产物，仅在质检中剥离比较。"
            "规范化需用户批准后单列一阶段处理。"),
    }
    write_json_idempotent(VERIFY_REPORT, report, True, "verify_report.json")

    print("== Stage 3 verify ==")
    print("   golden 一致率 %s  体检 %d 套  红灯 %d  黄灯 %d" % (
        agree["agreement"], len(results), len(red), len(yellow)))
    print("   staging 可复跑性：%s" % (
        "baseline（首次）" if reproducible is None else
        ("PASS（与上次逐字节一致）" if reproducible else "FAIL（本次与上次不同）")))
    for r in results:
        print("   %-10s glb=%s golden=%s fidelity=%s" % (
            r["id"],
            ",".join(sorted({v.get("equivalence", "?") for v in r["glb"].values()})) or "?",
            "PASS" if (r["golden"] or {}).get("ok") else "n/a",
            r["fidelity"]))
    for i, m in red:
        print("   [RED ] %s %s" % (i, m))
    if yellow:
        print("   [YEL ] 共 %d 条，首条：%s %s" % (len(yellow), yellow[0][0], yellow[0][1]))
    return 1 if red else 0


if __name__ == "__main__":
    sys.exit(main())
