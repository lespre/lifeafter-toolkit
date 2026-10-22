# -*- coding: utf-8 -*-
"""全量核对：所有板块的 meta / items / 配图 / manifest 一致性。

产出：01_索引与产物/30_分析/wiki_full_audit_20261022.json + 控制台摘要
"""
from __future__ import annotations

import json
import pathlib
import re
from collections import Counter, defaultdict

ROOT = pathlib.Path(r"E:/la拆包项目")
WEB = ROOT / "02_wiki/web"
BOARDS = WEB / "data/boards"
OUT = ROOT / "01_索引与产物/30_分析/wiki_full_audit_20261022.json"

HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")
REQ_META = ("name", "category", "package_sha", "evidence")
REQ_PROV = ("source_id", "source_lock_sha256", "table", "row_key", "field_refs",
            "name_source", "upstream", "locator_chain")

report = {}
summary = defaultdict(int)
missing_media = []

board_files = sorted(p for p in BOARDS.glob("*.json") if not p.name.startswith("_"))
for p in board_files:
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        report[p.stem] = {"error": "JSON 解析失败: %s" % e}
        summary["板块解析失败"] += 1
        continue
    meta = d.get("meta") or {}
    items = d.get("items") or []
    issues = []

    for k in REQ_META:
        if not meta.get(k):
            issues.append("meta 缺 %s" % k)
    sha = str(meta.get("package_sha") or "")
    if sha and not HEX64.match(sha):
        issues.append("meta.package_sha 不是 64 位 hex")

    ids = [str(i.get("id")) for i in items]
    dup_ids = [k for k, v in Counter(ids).items() if v > 1]
    if dup_ids:
        issues.append("重复 id %d 个（例 %s）" % (len(dup_ids), dup_ids[:3]))

    no_prov, bad_prov = [], []
    for it in items:
        if "table-absent" in (it.get("status_tags") or []):
            continue          # 已标注「当前表无同名行」的例外，不算缺口
        prov = it.get("provenance")
        if not prov:
            no_prov.append(str(it.get("id")))
            continue
        miss = [k for k in REQ_PROV if not prov.get(k)]
        if miss:
            bad_prov.append((str(it.get("id")), miss))

    if no_prov:
        issues.append("缺 provenance %d 条" % len(no_prov))
    if bad_prov:
        issues.append("provenance 字段不全 %d 条（例 %s 缺 %s）"
                      % (len(bad_prov), bad_prov[0][0], ",".join(bad_prov[0][1])))

    no_ev = sum(1 for it in items if not it.get("evidence_level"))
    if no_ev:
        issues.append("缺 evidence_level %d 条" % no_ev)
    no_tags = sum(1 for it in items if not it.get("status_tags"))
    if no_tags:
        issues.append("缺 status_tags %d 条" % no_tags)

    # 配图存在性
    m = 0
    for it in items:
        cand = []
        if it.get("image_path"):
            cand.append(it["image_path"])
        for im in ((it.get("_media") or {}).get("images") or []):
            if im.get("png"):
                cand.append(im["png"])
        for c in cand:
            s = str(c).replace("\\", "/")
            if s.startswith("assets/"):
                fp = WEB / s
            elif s.startswith("ui/") or s.startswith("character/"):
                continue          # 逻辑路径，不要求本地文件
            else:
                fp = WEB / s
            if not fp.is_file():
                m += 1
                missing_media.append((p.stem, str(it.get("id")), s))
    if m:
        issues.append("媒体文件缺失 %d 处" % m)

    report[p.stem] = {
        "items": len(items),
        "meta_ok": not any(i.startswith("meta") for i in issues),
        "issues": issues,
        "state_summary": meta.get("state_summary"),
    }
    summary["板块"] += 1
    summary["条目"] += len(items)
    if issues:
        summary["有问题板块"] += 1

# manifest 一致性
man = WEB / "data/manifest.js"
man_counts = {}
if man.is_file():
    txt = man.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r'"boards"\s*:\s*(\{.*\})\s*,\s*"', txt, re.S)
    for bid, cnt in re.findall(r'"([a-z0-9_]+)"\s*:\s*\{\s*"items"\s*:\s*(\d+)', txt):
        man_counts[bid] = int(cnt)
mismatch = []
for b in report:
    if b in man_counts and man_counts[b] != report[b].get("items"):
        mismatch.append((b, man_counts[b], report[b].get("items")))

report["__summary__"] = {
    "boards": summary["板块"],
    "items": summary["条目"],
    "boards_with_issues": summary["有问题板块"],
    "manifest_mismatch": mismatch,
    "missing_media_total": len(missing_media),
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({"report": report, "missing_media": missing_media[:500]},
                          ensure_ascii=False, indent=1), encoding="utf-8")

print("板块 %d ｜ 条目 %d ｜ 有问题 %d" % (summary["板块"], summary["条目"], summary["有问题板块"]))
print("manifest 计数不符:", mismatch or "无")
print("媒体缺失:", len(missing_media))
for b, r in report.items():
    if b.startswith("__"):
        continue
    if r.get("issues"):
        print(" - %-34s %s" % (b, "; ".join(r["issues"])[:150]))
print("报告:", OUT)
