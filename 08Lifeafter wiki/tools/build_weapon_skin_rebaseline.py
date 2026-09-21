# -*- coding: utf-8 -*-
"""A3：武器皮肤链 —— 新基准(328b8446) vs 旧基准(BA8A) 双基解码与差异审计。

为什么需要它
------------
canonical 链（Phase 2→Final）读的是 `test-documents-ba8a239a` 工作副本（pre-09-10 包），
而 09-10 体验服 Documents 包已换代成 `328b8446`（entry 空间不同 ⇒ v1.2 facade 拒绝跨基准）。
本工具：在新基准里按**自己的** entry 表定位同一批表，双基各自解码，逐表逐字段比对。

用法
----
  python tools/build_weapon_skin_rebaseline.py            # 全表比对 + 写审计
  python tools/build_weapon_skin_rebaseline.py --table weapon_skin_data

产物
----
  analysis/audit/weapon_skin_rebaseline_diff.json   逐表：行数/键集/字段差异/新键明细
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipelines.locator.resolve_table import resolve_table          # noqa: E402
from pipelines.parsing.decoder import decode_table                 # noqa: E402

OLD_SNAP = "test-documents-ba8a239a"
NEW_SNAP = "test-documents-328b8446"
NEW_INV = ROOT / "data" / "table_index_entries_328b8446.jsonl"
OUT = ROOT / "analysis" / "audit" / "weapon_skin_rebaseline_diff.json"

# 链上的表（family 名以 com\cdata\<name>.py 为准）
TABLES = [
    "weapon_skin_data",
    "weapon_skin_sfx_function_data",
    "weapon_skin_behavior_res_data",
    "weapon_skin_pendant_data",
    "skin_2_sfx_function_map",
    "skin_2_sfx_function_map_detail",
    "skin_function_item_id_to_anim_name",
    "common_item_data_base",
    "store_v2_data",
]


def load_new_inventory() -> list[dict[str, Any]]:
    rows = []
    with NEW_INV.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def find_in_new(rows: list[dict[str, Any]], table: str) -> dict[str, Any]:
    """在新基准清单里定位 data + chs（同目录同 stem，`<stem>_chs.py`）。"""
    want = f"\\{table}.py"
    data = [r for r in rows if r.get("table_name", "").endswith(want)]
    chs = [r for r in rows if r.get("table_name", "").endswith(f"\\{table}_chs.py")]
    # 非 oversea 优先；其次带 table_body
    def key(r):
        return ("oversea" in (r.get("table_name") or ""), not r.get("table_body"))
    data.sort(key=key)
    chs.sort(key=lambda r: ("oversea" in (r.get("table_name") or ""),))
    return {
        "data": data[0] if data else None,
        "chs": chs[0] if chs else None,
        "data_candidates": [r["entry"] for r in data[:6]],
        "chs_candidates": [r["entry"] for r in chs[:6]],
    }


def resolved_for(snapshot: str, entry: int | None, chs_entry: int | None,
                 fid: str | None = None, chs_fid: str | None = None) -> dict[str, Any]:
    return {
        "snapshot_id": snapshot,
        "data_entry": entry,
        "chs_entry": chs_entry,
        "data_fid": fid,
        "chs_fid": chs_fid,
        "status": "ok" if entry else "data_body_not_found",
        "data_payload_ref": {"snapshot_id": snapshot, "entry_index": entry},
        "chs_payload_ref": {"snapshot_id": snapshot, "entry_index": chs_entry},
    }


def norm_fields(row: dict[str, Any]) -> dict[str, Any]:
    """行 → {字段: 标量}；`["0x01", v]` 与裸值都归一。"""
    out: dict[str, Any] = {}
    for k, v in (row.get("values") or {}).items():
        if isinstance(v, list) and len(v) == 2 and isinstance(v[0], str) and v[0].startswith("0x"):
            out[k] = v[1]
        else:
            out[k] = v
    if isinstance(row.get("key"), int):
        out["__key"] = row["key"]
    return out


def decode_side(snapshot: str, table: str, *, entry: int | None, chs: int | None,
                fid: str | None, chs_fid: str | None) -> dict[str, Any]:
    if not entry:
        return {"status": "not_located", "rows": [], "row_count": 0}
    res = decode_table(resolved_for(snapshot, entry, chs, fid, chs_fid))
    return {
        "status": res.status,
        "row_count": res.row_count,
        "unique_keys": res.unique_keys,
        "chs_strings": res.chs_strings,
        "schemas": res.schemas,
        "keys": res.keys,
        "rows": res.rows,
        "provenance": res.provenance,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", action="append")
    a = ap.parse_args()
    tables = a.table or TABLES

    inv = load_new_inventory()
    report: dict[str, Any] = {
        "schema": "weapon-skin-rebaseline-diff-v1",
        "generated": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "old_basis": OLD_SNAP, "new_basis": NEW_SNAP,
        "note": "同一张表在两个基准内各按自己的 entry 表定位；entry 序号不可跨基准使用",
        "tables": {},
    }
    print(f"新基准清单 {len(inv)} 条；比对 {len(tables)} 张表\n")
    for t in tables:
        loc = find_in_new(inv, t)
        old_r = resolve_table(OLD_SNAP, t)
        new_side = decode_side(NEW_SNAP, t,
                               entry=(loc["data"] or {}).get("entry"),
                               chs=(loc["chs"] or {}).get("entry"),
                               fid=(loc["data"] or {}).get("file_id"),
                               chs_fid=(loc["chs"] or {}).get("file_id"))
        old_side = decode_side(OLD_SNAP, t,
                               entry=old_r.get("data_entry"),
                               chs=old_r.get("chs_entry"),
                               fid=old_r.get("data_fid"),
                               chs_fid=old_r.get("chs_fid"))
        old_keys = {str(k) for k in old_side.get("keys", [])}
        new_keys = {str(k) for k in new_side.get("keys", [])}
        entry: dict[str, Any] = {
            "old": {"entry": old_r.get("data_entry"), "chs": old_r.get("chs_entry"),
                    "fid": old_r.get("data_fid"), "chs_fid": old_r.get("chs_fid"),
                    "locator_status": old_r.get("status"),
                    "decode_status": old_side.get("status"), "rows": old_side.get("row_count"),
                    "chs_strings": old_side.get("chs_strings")},
            "new": {"entry": (loc["data"] or {}).get("entry"), "chs": (loc["chs"] or {}).get("entry"),
                    "fid": (loc["data"] or {}).get("file_id"), "chs_fid": (loc["chs"] or {}).get("file_id"),
                    "table_name": (loc["data"] or {}).get("table_name"),
                    "decode_status": new_side.get("status"), "rows": new_side.get("row_count"),
                    "chs_strings": new_side.get("chs_strings"),
                    "candidates": {"data": loc["data_candidates"], "chs": loc["chs_candidates"]}},
            "keys": {"intersection": len(old_keys & new_keys),
                     "only_old": sorted(old_keys - new_keys),
                     "only_new": sorted(new_keys - old_keys)},
        }
        # 逐字段比对（共同键）
        old_by = {str(r["key"]): norm_fields(r) for r in old_side.get("rows", []) if isinstance(r.get("key"), int)}
        new_by = {str(r["key"]): norm_fields(r) for r in new_side.get("rows", []) if isinstance(r.get("key"), int)}
        fdiff: dict[str, list[Any]] = {}
        for k in sorted(old_keys & new_keys):
            o, n = old_by.get(k, {}), new_by.get(k, {})
            for f in set(o) | set(n):
                if f == "__key":
                    continue
                ov, nv = o.get(f), n.get(f)
                if isinstance(ov, (int, float)) and isinstance(nv, (int, float)):
                    same = abs(ov - nv) < 1e-6
                else:
                    same = (ov == nv)
                if not same:
                    fdiff.setdefault(f, []).append({"key": k, "old": ov, "new": nv})
        entry["field_diff"] = {f: {"count": len(v), "sample": v[:5]} for f, v in sorted(fdiff.items())}
        entry["field_diff_total"] = sum(len(v) for v in fdiff.values())
        # 新键明细（不假设语义，只落字段）
        entry["only_new_detail"] = [
            {"key": k, "fields": {kk: vv for kk, vv in new_by[k].items() if kk != "__key"}}
            for k in sorted(new_keys - old_keys) if k in new_by
        ][:40]
        report["tables"][t] = entry
        print(f"{t:38s} old={entry['old']['rows']} new={entry['new']['rows']} "
              f"∩={entry['keys']['intersection']} +new={len(entry['keys']['only_new'])} "
              f"-old={len(entry['keys']['only_old'])} 字段差={entry['field_diff_total']} "
              f"[新定位 entry={entry['new']['entry']} fid={entry['new']['fid']} st={entry['new']['decode_status']}]")
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n→ {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
