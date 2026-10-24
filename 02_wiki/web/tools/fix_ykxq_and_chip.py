# -*- coding: utf-8 -*-
"""处理 ykxq 变体缺失的 658 条 + chip 注解 65 条：能对上行的才改，否则标 unresolved。"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
from toolkit_core import bindict_table as BT  # noqa: E402

WEB = pathlib.Path(r"E:/la拆包项目/02_wiki/web")
TREES = [
    pathlib.Path(r"E:/la拆包项目/01_索引与产物/41_还原树/pe/配置_增量快照"),
    pathlib.Path(r"E:/la拆包项目/01_索引与产物/41_还原树/apk_mumu_5.0.679/assets/script.py314.lc.npk"),
]
BS = chr(92)

CAND = {
    "fashion_data_for_export_auto_oversea_data_ykxq.py": [
        "com/cdata/oversea/fashion_data_for_export_auto_oversea_data_yk.py",
        "com/cdata/fashion_data_for_export.py",
    ],
    "fashion_data_auto_oversea_data_ykxq.py": [
        "com/cdata/oversea/fashion_data_auto_oversea_data_yk.py",
        "com/cdata/fashion_data.py",
    ],
    "simple_fashion_data_auto_oversea_data_ykxq.py": [
        "com/cdata/oversea/simple_fashion_data_auto_oversea_data_yk.py",
        "com/cdata/simple_fashion_data.py",
    ],
}


def keys_of(rel):
    for t in TREES:
        p = t / rel
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
        return {str(r["key"]) for r in rows}
    return set()


def main() -> int:
    name = "fashion_identity_unresolved_v01"
    p = WEB / "data/boards" / (name + ".json")
    d = json.loads(p.read_text(encoding="utf-8"))
    groups = {}
    for it in d["items"]:
        pr = it.get("provenance") or {}
        t = pr.get("table") or ""
        base = t.split(BS)[-1]
        if base in CAND:
            groups.setdefault(base, []).append(it)
    print("分组", {k: len(v) for k, v in groups.items()})

    for base, items in groups.items():
        sample = [str((it.get("provenance") or {}).get("row_key")) for it in items[:20]]
        best = None
        for rel in CAND[base]:
            ks = keys_of(rel)
            if not ks:
                print("  %-58s 缺" % rel)
                continue
            hit = sum(1 for k in sample if k in ks)
            print("  %-58s 行键 %-6d 命中 %d/20" % (rel, len(ks), hit))
            if best is None or hit > best[1]:
                best = (rel, hit)
        if best and best[1] >= 16:
            for it in items:
                pr = it["provenance"]
                pr["table_raw"] = pr["table"]
                pr["table"] = best[0].replace("/", BS)
                pr["table_variant_note"] = "源声明为 ykxq 变体，还原树无此表；按行键抽验改指向同类变体"
                pr.pop("table_status", None)
        else:
            for it in items:
                pr = it["provenance"]
                pr["table_status"] = "unresolved"
                pr["table_note"] = "ykxq 变体在还原树中不存在，且同类表行键对不上"
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards" / (name + ".js")).write_text(
        "window.WIKI_BOARD_%s = %s;" % (name, json.dumps(d, ensure_ascii=False, indent=1)), encoding="utf-8")

    # chip 注解
    cp = WEB / "data/boards/chip_item_catalog.json"
    if cp.is_file():
        cd = json.loads(cp.read_text(encoding="utf-8"))
        n = 0
        for it in cd["items"]:
            pr = it.get("provenance") or {}
            if "chip_type_data" in (pr.get("table") or "") and "(" in (pr.get("table") or ""):
                pr["table_raw"] = pr["table"]
                pr["table"] = "com" + BS + "cdata" + BS + "chip_type_data.py"
                n += 1
        if n:
            cp.write_text(json.dumps(cd, ensure_ascii=False, indent=1), encoding="utf-8")
            (WEB / "data/boards/chip_item_catalog.js").write_text(
                "window.WIKI_BOARD_chip_item_catalog = %s;" % json.dumps(cd, ensure_ascii=False, indent=1),
                encoding="utf-8")
        print("chip 注解修正", n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
