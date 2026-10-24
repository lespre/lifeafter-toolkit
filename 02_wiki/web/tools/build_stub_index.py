# -*- coding: utf-8 -*-
"""建「桩表 → 真表」索引：808/815B 的空壳表在还原树里另有同名/同族真身。

输出 01_索引与产物/10_索引/stub_tables.json：
  { "com/cdata/all_equips_data.py": {"stub_bytes": 808, "real": "..."}, ... }
用途：任何脚本读到桩表时，按这个索引改走真身，别再解出 0 行还以为是没数据。
"""
from __future__ import annotations

import json
import pathlib

PROJ = pathlib.Path("E:/la拆包项目")
TREE = PROJ / "01_索引与产物/41_还原树"
OUT = PROJ / "01_索引与产物/10_索引/stub_tables.json"
STUB_SIZES = {807, 808, 809, 815, 816}


def main() -> int:
    all_py = [p for p in TREE.rglob("*.py") if "cdata" in str(p)]
    by_stem: dict[str, list[pathlib.Path]] = {}
    for p in all_py:
        by_stem.setdefault(p.stem, []).append(p)

    mapping = {}
    for p in all_py:
        size = p.stat().st_size
        if size not in STUB_SIZES:
            continue
        stem = p.stem
        cands = [q for q in all_py
                 if q != p and q.stat().st_size > 2048 and not q.stem.endswith("_chs")
                 and (q.stem == stem or q.stem.startswith(stem + "_") or stem in q.stem)]
        # 优先：同目录族的 oversea 变体 → 其它目录同名 → 表缓存
        cands.sort(key=lambda q: (
            0 if q.stem == p.stem else 1,
            0 if "oversea" in str(q) else 1,
            1 if "_备份归档" in str(q) else 0,
            -q.stat().st_size,
        ))
        rel = str(p.relative_to(PROJ)).replace("\\", "/")
        mapping[rel] = {
            "stub_bytes": size,
            "real": (str(cands[0].relative_to(PROJ)).replace("\\", "/") if cands else None),
            "real_bytes": (cands[0].stat().st_size if cands else 0),
            "alternatives": [str(q.relative_to(PROJ)).replace("\\", "/") for q in cands[:3]],
        }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(mapping, ensure_ascii=False, indent=1), encoding="utf-8")
    with_real = sum(1 for v in mapping.values() if v["real"])
    print("桩表 %d 个 ｜ 找到真身 %d ｜ 无真身 %d" % (len(mapping), with_real, len(mapping) - with_real))
    for k, v in list(mapping.items())[:5]:
        print("  %-62s → %s" % (k.split("com/cdata/")[-1], (v["real"] or "无").split("com/cdata/")[-1]))
    print("写出", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
