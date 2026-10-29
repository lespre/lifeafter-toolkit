# -*- coding: utf-8 -*-
"""全量核对：所有 board 的 provenance.table 是否指向真实存在的文件。"""
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


def exists(rel: str) -> bool:
    rel = rel.replace(BS, "/")
    if any((t / rel).is_file() for t in TREES):
        return True
    # 逻辑表名（无路径、无扩展名）也算合法：buff_data / skill_data / recipe
    stem = rel.split("/")[-1]
    if stem.endswith(".py"):
        stem = stem[:-3]
    for t in TREES:
        if (t / "com/cdata" / (stem + ".py")).is_file():
            return True
        if list(t.glob("**/%s.py" % stem)):
            return True
    return False


def main() -> int:
    bad = collections.Counter()
    total = 0
    for p in sorted((WEB / "data/boards").glob("*.json")):
        if p.name.startswith("_archive"):
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        for it in d.get("items", []):
            t = (it.get("provenance") or {}).get("table")
            if not t:
                continue
            total += 1
            if not exists(t):
                bad[(p.stem, t)] += 1
    print("带 table 声明的条目", total)
    print("指向不存在文件的条目", sum(bad.values()), "组数", len(bad))
    for (b, t), n in bad.most_common(15):
        print("  %-22s %-56s %d" % (b, t, n))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
