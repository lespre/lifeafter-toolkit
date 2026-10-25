# -*- coding: utf-8 -*-
"""经典服武器配置批量解码 + 定向检索（不把全量数据打进对话）。

输出：01_索引与产物/30_分析/经典服武器配置_检索.json
目标：1110189 / 10854 / 1013_10 / 喷火器 / 幻海 相关行
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

ROOT = pathlib.Path("E:/la拆包项目")
TREES = [ROOT / "01_索引与产物/41_还原树/pe/配置/script.py314.lc.npk/com/cdata",
         ROOT / "01_索引与产物/41_还原树/pe/配置_增量快照/script.py314.lc.npk/com/cdata",
         ROOT / "01_索引与产物/41_还原树/pe/配置/com/cdata"]
OUT = ROOT / "01_索引与产物/30_分析/经典服武器配置_检索.json"
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core.bindict_table import decode_table_rows, parse_legacy_chs_pool  # noqa: E402

KW = ("1110189", "10854", "1013_10", "喷火器", "幻海", "菌焰")
TNAME = ("weapon", "equip", "coating", "recipe", "item")


def body(p: pathlib.Path):
    raw = p.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        return None
    n = struct.unpack_from("<I", raw, at + 2)[0]
    if n <= 0 or at + 6 + n > len(raw):
        return None
    return raw[at + 6: at + 6 + n]


def val(v):
    return v[1] if isinstance(v, tuple) and len(v) == 2 else v


def main() -> int:
    seen, rep = set(), []
    for tree in TREES:
        if not tree.is_dir():
            continue
        for p in sorted(tree.glob("*.py")):
            if "_chs" in p.name or not any(k in p.name for k in TNAME):
                continue
            stem = p.stem
            if (tree, stem) in seen:
                continue
            b = body(p)
            if not b:
                continue
            chs = tree / (stem + "_chs.py")
            pool = []
            if chs.exists():
                try:
                    pool = parse_legacy_chs_pool(chs.read_bytes())
                except Exception:  # noqa: BLE001
                    pool = []
            try:
                rows, _ = decode_table_rows(b, pool, resolve_jumps=False, lenient=True)
            except Exception:  # noqa: BLE001
                continue
            seen.add((tree, stem))
            for r in rows:
                v = {k: val(x) for k, x in (r.get("values") or {}).items()}
                blob = " ".join(str(x) for x in v.values() if isinstance(x, (str, int)))
                if any(k in blob for k in KW):
                    rep.append({"tree": tree.name, "table": stem, "key": r.get("key"),
                                "values": {k: x for k, x in v.items() if isinstance(x, (str, int, float))}})
        print("扫完", tree.name, "累计命中", len(rep))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    from collections import Counter
    print("表数", len(seen), "命中行", len(rep))
    print(Counter((x["table"] for x in rep)).most_common(8))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
