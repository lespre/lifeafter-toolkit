# -*- coding: utf-8 -*-
"""全量核对 provenance.table（v2：先建索引，避免 glob 风暴）。"""
from __future__ import annotations
import sys

import collections
import json
import pathlib

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
    print("索引：路径", len(paths), "表名", len(stems))

    def ok(rel: str) -> bool:
        r = rel.replace(BS, "/")
        if r in paths:
            return True
        stem = r.split("/")[-1]
        if stem.endswith(".py"):
            stem = stem[:-3]
        return stem in stems

    bad = collections.Counter()
    total = 0
    for fp in sorted((WEB / "data/boards").glob("*.json")):
        if fp.name.startswith("_archive"):
            continue
        d = json.loads(fp.read_text(encoding="utf-8"))
        for it in d.get("items", []):
            tb = (it.get("provenance") or {}).get("table")
            if not tb:
                continue
            total += 1
            if not ok(tb):
                bad[(fp.stem, tb)] += 1
    print("带 table 声明", total, "｜指向不存在", sum(bad.values()), "｜组数", len(bad))
    for (b, tb), n in bad.most_common(15):
        print("  %-24s %-56s %d" % (b, tb, n))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
