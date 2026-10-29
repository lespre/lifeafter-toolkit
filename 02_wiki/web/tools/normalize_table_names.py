# -*- coding: utf-8 -*-
"""规范化 provenance.table：去掉注解后缀；仍解析不到的标 table_status=unresolved。"""
from __future__ import annotations
import sys

import collections
import json
import pathlib
import re

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import TREE_ROOT, WEB  # noqa: E402

TREES = [
    pathlib.Path(TREE_ROOT / "pe/配置_增量快照"),
    pathlib.Path(TREE_ROOT / "Documents/script.py314.lc.npk"),
    pathlib.Path(TREE_ROOT / "apk_mumu_5.0.679/assets/script.py314.lc.npk"),
]
BS = chr(92)


def main() -> int:
    paths, stems = set(), set()
    for t in TREES:
        for p in t.rglob("*.py"):
            paths.add(p.relative_to(t).as_posix())
            stems.add(p.stem)

    def ok(name: str) -> bool:
        r = name.replace(BS, "/")
        if r in paths:
            return True
        stem = r.split("/")[-1]
        if stem.endswith(".py"):
            stem = stem[:-3]
        return stem in stems

    stats = collections.Counter()
    for fp in sorted((WEB / "data/boards").glob("*.json")):
        if fp.name.startswith("_archive"):
            continue
        d = json.loads(fp.read_text(encoding="utf-8"))
        changed = 0
        for it in d.get("items", []):
            pr = it.get("provenance") or {}
            t = pr.get("table")
            if not t:
                continue
            if ok(t):
                continue
            # 1) 去注解：xxx(kj1) / xxx + yyy / "… pool (kjxq)"
            base = re.split(r"[(（]|\s+\+|;", t)[0].strip()
            base = base.replace(" ", "")
            if base and ok(base):
                pr["table_raw"] = t
                pr["table"] = base
                changed += 1
                stats["去注解"] += 1
                continue
            pr["table_status"] = "unresolved"
            pr["table_note"] = "该名字在还原树里找不到对应表，保留原声明"
            stats["仍不可解析"] += 1
            stats[("bad:" + t)[:70]] += 1
        if changed:
            fp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
            (WEB / "data/boards" / (fp.stem + ".js")).write_text(
                "window.WIKI_BOARD_%s = %s;" % (fp.stem, json.dumps(d, ensure_ascii=False, indent=1)),
                encoding="utf-8")
    print("规范化结果：", {k: v for k, v in stats.items() if not str(k).startswith("bad:")})
    print("仍不可解析的声明：")
    for k, v in stats.most_common(12):
        if str(k).startswith("bad:"):
            print("  %-70s %d" % (k[4:], v))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
