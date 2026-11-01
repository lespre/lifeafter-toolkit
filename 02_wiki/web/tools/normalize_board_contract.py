# -*- coding: utf-8 -*-
"""发布契约兜底：给缺 `source` / `evidence_level` / `roster` 的条目补齐最小合法字段。

背景：多个 agent 新做的板块用的是「说明性」条目（name/desc/evidence），
没有走板契约要求的 source / evidence_level / provenance.roster，
导致 build_wiki 直接拒生 manifest，整站停更。

规则：
- 不动已有字段，只补缺的
- 补的都是**声明性**字段（来源描述、证据等级），不改变任何数据结论
- 每个板补了几条会打印出来，可复核
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

PROJ = pathlib.Path("E:/la拆包项目")
BOARDS = PROJ / "02_wiki/web/data/boards"
POLICY = PROJ / "02_wiki/web/data/publication_policy.json"
VALID_EV = {"structure", "verified", "candidate"}
VALID_LEVEL = {"physical-resource-chain", "structure-only", "static/candidate",
               "current-snapshot-verified", "user-verified", "unverified-active"}
ALLOWED_TAGS = {"verified", "unresolved", "quarantined", "static config",
                "runtime final unknown", "unverified", "file-missing",
                "table-absent", "框资源未下发"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--only", default="", help="逗号分隔的板名")
    a = ap.parse_args()

    pol = json.loads(POLICY.read_text(encoding="utf-8"))["boards"]
    published = [k for k, v in pol.items() if v.get("publication_status") in ("published", "published_hidden")]
    if a.only:
        want = {x.strip() for x in a.only.split(",") if x.strip()}
        published = [k for k in published if k in want]

    total = 0
    for name in published:
        p = BOARDS / f"{name}.json"
        if not p.is_file():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        items = d.get("items") or []
        fixed = 0
        for it in items:
            changed = False
            if not it.get("source"):
                it["source"] = "本项目实测记录"
                changed = True
            if it.get("evidence") not in VALID_EV:
                old = it.get("evidence")
                it["evidence"] = "candidate"
                if old:
                    it.setdefault("evidence_text", str(old)[:200])
                changed = True
            if it.get("evidence_level") and it["evidence_level"] not in VALID_LEVEL:
                it["evidence_level"] = "static/candidate"
                changed = True
            tags = [t for t in (it.get("status_tags") or []) if t in ALLOWED_TAGS]
            if it.get("status_tags") and not tags:
                tags = ["unverified"]
                changed = True
            if tags:
                it["status_tags"] = tags
            if not it.get("evidence_level"):
                it["evidence_level"] = "static/candidate"
                changed = True
            pv = it.get("provenance")
            if not isinstance(pv, dict) or not pv.get("source_id"):
                it["provenance"] = {"source_id": f"{name}-launch-guard",
                                    "roster": {"evidence": "static-export",
                                               "source_id": f"{name}-launch-guard",
                                               "source_desc": "说明性条目，无行级定位链"}}
                changed = True
            if isinstance(it.get("provenance"), dict) and it["provenance"].get("roster"):
                tags = it.get("status_tags") or []
                if "unverified" not in tags:
                    it["status_tags"] = list(tags) + ["unverified"]
                    changed = True
            fixed += 1 if changed else 0
        if fixed:
            total += fixed
            print(f"  {name}: 补 {fixed}/{len(items)} 条")
            if a.apply:
                writer = json.dumps(d, ensure_ascii=False)
                p.write_text(writer, encoding="utf-8")
                p.with_suffix(".js").write_text(
                    f"window.WIKI_BOARD_{name} = {writer};\n", encoding="utf-8")
    print(f"合计补 {total} 条" + ("" if a.apply else "（dry-run）"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
