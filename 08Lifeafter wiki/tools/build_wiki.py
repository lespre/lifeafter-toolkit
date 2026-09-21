#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""08Lifeafter wiki builder v0.1（骨架版）

扫描 data/boards/*.json → 校验 provenance → 生成 data/manifest.js

用法: python tools/build_wiki.py
退出码: 0 成功 / 1 校验失败（不生成 manifest）
"""
import json
import re
import sys
import datetime
from collections import Counter
from pathlib import Path

from publication_policy import (load_policy, public_board_ids, publication_contract_errors,
                                PUBLISHED_HIDDEN)

ROOT = Path(__file__).resolve().parent.parent
BOARDS_DIR = ROOT / "data" / "boards"
POLICY_FILE = ROOT / "data" / "publication_policy.json"
POLICY_JS_FILE = ROOT / "data" / "publication_policy.js"
OUT_FILE = ROOT / "data" / "manifest.js"

REQUIRED_META = ["name", "category", "source_server", "package_sha", "generated", "evidence"]
VALID_EVIDENCE = ["structure", "verified", "candidate"]
ITEM_REQUIRED = ["id", "name", "evidence", "source"]


def check_board(path: Path, errors: list) -> dict | None:
    try:
        d = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as e:
        errors.append(f"{path.name}: JSON 解析失败: {e}")
        return None
    if not isinstance(d, dict):
        errors.append(f"{path.name}: 顶层必须是对象")
        return None

    meta = d.get("meta", {})
    bad = False
    miss = [k for k in REQUIRED_META if k not in meta]
    if miss:
        errors.append(f"{path.name}: meta 缺必填字段 {miss}")
        bad = True
    if meta.get("evidence") not in VALID_EVIDENCE:
        errors.append(f"{path.name}: meta.evidence 非法: {meta.get('evidence')!r}")
        bad = True
    if len(str(meta.get("package_sha", ""))) < 40:
        errors.append(f"{path.name}: meta.package_sha 长度不足（需完整 SHA-256）")
        bad = True

    items = d.get("items", [])
    if not isinstance(items, list) or not items:
        errors.append(f"{path.name}: items 为空或非列表")
        bad = True
    else:
        for i, it in enumerate(items):
            miss = [k for k in ITEM_REQUIRED if k not in it]
            if miss:
                errors.append(f"{path.name}: items[{i}] 缺字段 {miss}")
                bad = True
            if it.get("evidence") not in VALID_EVIDENCE:
                errors.append(f"{path.name}: items[{i}] evidence 非法: {it.get('evidence')!r}")
                bad = True
    if bad:
        return None

    evc = Counter(it["evidence"] for it in items)
    provenance = meta.get("provenance", {})
    chain_statuses = Counter(
        (it.get("provenance", {}).get("locator_chain", {}).get("chain_status", "missing"))
        for it in items if isinstance(it, dict)
    )
    dual_source = provenance.get("dual_source", {}) if isinstance(provenance, dict) else {}
    return {
        "name": meta["name"],
        "category": meta["category"],
        "board": path.stem,
        "items": len(items),
        "generated": meta["generated"],
        "source_server": meta["source_server"],
        "package_sha": meta["package_sha"],
        "evidence": dict(evc),
        "state_summary": meta.get("state_summary", {}),
        "name_status_summary": meta.get("name_status_summary", {}),
        "provenance_status": {
            "contract_version": provenance.get("contract_version"),
            "audit_status": provenance.get("audit_status"),
            "dual_source_mode": dual_source.get("mode"),
            "locator_chain_statuses": dict(sorted(chain_statuses.items())),
        },
    }


def main() -> int:
    errors: list = []
    boards: list = []

    try:
        policy = load_policy(POLICY_FILE)
        public_ids = set(public_board_ids(POLICY_FILE, (p.stem for p in BOARDS_DIR.glob("*.json"))))
    except Exception as e:
        print(f"❌ 发布策略无效，不生成 manifest：{e}")
        return 1

    if not BOARDS_DIR.exists():
        errors.append(f"板块目录不存在: {BOARDS_DIR}")
    else:
        for p in sorted(BOARDS_DIR.glob("*.json")):
            b = check_board(p, errors)
            if b is None or p.stem not in public_ids:
                continue
            raw_board = json.loads(p.read_text(encoding="utf-8-sig"))
            contract_errors = publication_contract_errors(raw_board, strict_v2=True)
            if contract_errors:
                errors.extend(
                    f"{p.name}: 已发布 board 缺可机读定位链 {issue}"
                    for issue in contract_errors
                )
                continue
            boards.append(b)

    if errors:
        print("❌ 校验失败，不生成 manifest：")
        for e in errors:
            print("  -", e)
        return 1

    payload = {
        "generated": datetime.date.today().isoformat(),
        "builder": "build_wiki.py v0.4-strict-dual-source-gated",
        "publication_policy": POLICY_FILE.name,
        "policy_generated": policy.get("generated"),
        "boards": boards,
    }
    OUT_FILE.write_text(
        "window.WIKI_MANIFEST = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )
    POLICY_JS_FILE.write_text(
        "window.WIKI_PUBLICATION_POLICY = " + json.dumps(policy, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )
    # 每个已发布板块输出同名 .js（file:// 下页面用 <script src> 拿数据，不能 fetch）
    for p in sorted(BOARDS_DIR.glob("*.json")):
        stem = p.stem
        if stem not in public_ids:
            continue
        if not re.fullmatch(r"[a-z0-9_]+", stem):
            print(f"⚠ 板块文件名含非法字符，跳过 js 输出: {p.name}")
            continue
        raw = p.read_text(encoding="utf-8-sig")
        (BOARDS_DIR / f"{stem}.js").write_text(
            f"window.WIKI_BOARD_{stem} = " + raw.rstrip() + ";\n", encoding="utf-8"
        )
    total = sum(b["items"] for b in boards)
    print(f"✅ manifest.js 已生成：{len(boards)} 个板块，共 {total} 条")
    for b in boards:
        print(f"  - [{b['category']}] {b['name']}: {b['items']} 条, 证据 {b['evidence']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
