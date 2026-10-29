# -*- coding: utf-8 -*-
"""修正 board provenance.table 指向：先探测哪张真实表含这些 row_key，再回写。

不做猜测：每张候选表解出来，抽 20 个 row_key 验证命中率，命中 >=80% 才采用。
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys
from collections import Counter


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import TOOLKIT_CORE, TREE_ROOT, WEB  # noqa: E402
sys.path.insert(0, str(TOOLKIT_CORE))
from toolkit_core import bindict_table as BT  # noqa: E402

TREES = [
    pathlib.Path(TREE_ROOT / "pe/配置_增量快照"),
    pathlib.Path(TREE_ROOT / "Documents/script.py314.lc.npk"),
    pathlib.Path(TREE_ROOT / "apk_mumu_5.0.679/assets/script.py314.lc.npk"),
]

CANDIDATES = {
    "com\\cdata\\common_item_data_base.py": [
        "com/cdata/common_item_data.py",
        "com/cdata/oversea/common_item_data_auto_oversea_data_kj1.py",
    ],
    "com\\cdata\\fashion_data_chs.py.py": ["com/cdata/fashion_data.py"],
    "com\\cdata\\unknown.py": ["com/cdata/fashion_data.py"],
    "oversea\\common_item_data_auto_oversea_data_kj1.py": [
        "com/cdata/oversea/common_item_data_auto_oversea_data_kj1.py",
        "com/cdata/common_item_data.py",
    ],
}


def load_keys(rel):
    for tree in TREES:
        p = tree / rel
        if not p.is_file():
            continue
        b = p.read_bytes()
        at = b.find(b"x{")
        if at < 0:
            continue
        L = struct.unpack_from("<I", b, at + 2)[0]
        pool = {}
        chs = p.with_name(p.stem + "_chs.py")
        if chs.is_file():
            try:
                pool = BT.parse_legacy_chs_pool(chs.read_bytes())
            except Exception:
                pool = {}
        try:
            rows, _ = BT.decode_table_rows(b[at + 6: at + 6 + L], pool, resolve_jumps=False, lenient=True)
        except Exception:
            continue
        keys = set()
        for r in rows:
            k = str(r["key"])
            keys.add(k)
            vals = r["values"]
            for cand in ("id", "item_id"):
                v = vals.get(cand)
                if v:
                    x = v[1] if isinstance(v, tuple) else v
                    if isinstance(x, (int, str)):
                        keys.add(str(x))
        return p, keys
    return None, set()


def main() -> int:
    report = []
    for board in ("item_master_full", "fashion_wardrobe", "mutation_core_full"):
        path = WEB / "data/boards" / (board + ".json")
        d = json.loads(path.read_text(encoding="utf-8"))
        by_table = {}
        for it in d["items"]:
            t = (it.get("provenance") or {}).get("table") or ""
            by_table.setdefault(t, []).append(it)
        print("==", board, {t: len(v) for t, v in by_table.items()})
        for t, items in by_table.items():
            cands = CANDIDATES.get(t)
            if not cands:
                continue
            sample = items[:20]
            best = None
            for rel in cands:
                p, keys = load_keys(rel)
                if not keys:
                    continue
                def _k(it):
                    pr = it.get("provenance") or {}
                    return str(pr.get("row_key") or it.get("item_id") or it.get("id"))
                hit = sum(1 for it in sample if _k(it) in keys)
                print("   %-58s 行键 %-7d 命中 %d/%d" % (rel, len(keys), hit, len(sample)))
                if best is None or hit > best[1]:
                    best = (rel, hit)
            if best and best[1] >= int(len(sample) * 0.8):
                report.append((board, t, best[0], len(items)))
    print("\n建议改写：")
    for r in report:
        print("  %-20s %-52s → %-52s (%d 条)" % r)
    (WEB / ".." / ".." / "01_索引与产物/30_分析/伤害系统逆向/provenance_fix_plan.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
