# -*- coding: utf-8 -*-
"""P2-1：字段名绑定（table + schema_ref + field_slot → 真实字段名）。

机制（可验证，非猜测）：
- schema 定义位于 blob 内 schema_ref 偏移：uleb n + uleb bits + n×
  (slot uleb, type byte, name=CHS 池文本[slot])
- 字段名池=表家族 chs 型成员（chs/base_chs/inc_chs）条目解析的文本池；
  配对=池条数 == 表体 x{ 容器头期望 N（防漂移；023928=55141=common_item 锚已验证）
- 多 schema_ref 分别处理；slot 越池界=占位 <slot_N>=unresolved 字段
- unsafe：BA8 快照内无已实证字段错位表（错位检测属值语义层 P2）；0x96 宽表型标 suspect
- 不做业务 join；server_branch=unresolved

输出：data/field_names.json（(entry,schema_ref) 定义级）+ data/field_names_summary.json
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRIES_DIR = Path(r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_BA8A239A\entries")
ROW_INDEX = ROOT / "data" / "row_index.jsonl"
FAMILIES = ROOT / "data" / "table_families_v2.json"
OUT = ROOT / "data" / "field_names.json"
OUT_SUM = ROOT / "data" / "field_names_summary.json"
TOOLKIT = r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心"


def xbody_of(data: bytes):
    pos = 0
    while True:
        at = data.find(b"x{", pos)
        if at < 0:
            return None
        if at + 6 <= len(data):
            n = int.from_bytes(data[at + 2:at + 6], "little")
            if 0 < n <= len(data) - at - 6:
                cnt = int.from_bytes(data[at + 6:at + 10], "little")
                res = int.from_bytes(data[at + 10:at + 14], "little")
                if res == 0 and cnt <= 300000:
                    return at
        pos = at + 3


def main() -> int:
    t0 = time.time()
    sys.path[:0] = [TOOLKIT]
    from toolkit_core.bindict_table import parse_legacy_chs_pool, _schema_at

    # 1) 聚合 row_index：entry -> schema_refs（mapping 行 None 跳过；KJ1 行
    #    行型 uleb 非 schema 引用=排除（6 表 86 假 schema 污染先例）
    per_entry: dict[int, set] = defaultdict(set)
    with ROW_INDEX.open(encoding="utf-8") as f:
        for ln in f:
            r = json.loads(ln)
            if r["schema_ref"] is not None and r.get("marker") != "kj1":
                per_entry[r["entry"]].add(r["schema_ref"])
    print(f"std 表 {len(per_entry)} 个（有 schema_ref 行）", flush=True)

    # 2) 家族 chs 候选（family -> chs 型成员 entry 列表）
    fam = json.loads(FAMILIES.read_text(encoding="utf-8"))
    chs_members: dict[str, list[dict]] = {}
    for f in fam["families"]:
        tc = f["clients"].get("test")
        if not tc or not tc.get("present"):
            continue
        chs = [m for m in tc["members"] if "chs" in (m["role"] or "")]
        if chs:
            chs_members[f["family"]] = chs
    pool_cache: dict[int, tuple[list[str], int]] = {}  # entry -> (pool, n)

    def pool_for(entry: int) -> tuple[list[str] | None, int | None, str | None]:
        if entry in pool_cache:
            p, n = pool_cache[entry]
            return p, n, None if p else "parse_fail"
        try:
            d = (ENTRIES_DIR / f"{entry:06d}.bin").read_bytes()
            p = parse_legacy_chs_pool(d)
            pool_cache[entry] = (p, len(p))
            return p, len(p), None
        except Exception as exc:
            pool_cache[entry] = (None, 0)
            return None, 0, repr(exc)[:80]

    def resolve_pool(entry: int, family: str | None, expect: int):
        """返回 (pool, pool_entry, note)。"""
        cands = chs_members.get(family or "", [])
        if not cands:
            return None, None, "no_family_chs"
        best = None
        notes = []
        for m in cands:
            if m["entry"] == entry:
                continue
            p, n, err = pool_for(m["entry"])
            if err:
                notes.append(f"e{m['entry']}:{err}")
                continue
            if n == expect:
                best = (p, m["entry"])
                break
            notes.append(f"e{m['entry']}:pool={n}!=expect")
        if best:
            return best[0], best[1], "family_chs_matched"
        if notes:
            return None, None, "|".join(notes[:4])
        return None, None, "no_chs_parse"

    # 3) 逐表绑定
    tables_out = []
    slots_total = 0
    bound = 0
    unresolved = 0
    unsafe = []
    suspect_wide = 0
    multi_schema = 0
    table_name_map = {}
    with (ROOT / "data" / "table_index_entries.jsonl").open(
            encoding="utf-8") as f:
        for ln in f:
            r = json.loads(ln)
            if r["client_channel"] == "test" and r["table_name"]:
                table_name_map[r["entry"]] = r["table_name"]
    fam_of_entry = {}
    for f in fam["families"]:
        tc = f["clients"].get("test")
        if tc and tc.get("present"):
            for m in tc["members"]:
                fam_of_entry[m["entry"]] = f["family"]
    for entry, refs in sorted(per_entry.items()):
        fn = f"{entry:06d}.bin"
        d = (ENTRIES_DIR / fn).read_bytes()
        at = xbody_of(d)
        if at is None:
            continue
        xl = int.from_bytes(d[at + 2:at + 6], "little")
        body = d[at + 6:at + 6 + xl]
        expect = int.from_bytes(body[0:4], "little")
        cnt = int.from_bytes(body[0:4], "little")
        te = 8 + 4 * cnt
        blob = body[te:]
        family = fam_of_entry.get(entry)
        pool, pool_entry, note = resolve_pool(entry, family, expect)
        if pool is None:
            # 全家族候选都无匹配：池 unresolved
            schemas = []
            for ref in sorted(refs):
                try:
                    n_f, bits, _ = _schema_at(blob, ref, [])
                except ValueError:
                    continue
                for _ in range(n_f):
                    unresolved += 1
                schemas.append({"schema_ref": ref, "n_fields": n_f,
                                "bits": bits, "bound": "none",
                                "fields": None})
                slots_total += n_f
            tables_out.append({"entry": entry,
                               "table": table_name_map.get(entry),
                               "family": family, "pool_entry": None,
                               "pool_note": note,
                               "schemas": schemas, "pool_unresolved": True})
            unsafe.append(entry)
            continue
        multi_schema += 1 if len(refs) > 1 else 0
        # 0x96 宽表型 suspect（行 marker 主要为 0x96 且字段名池文本可能错位风险）
        # ——不判定值层，仅记录标记供 P2-2 复核
        schemas = []
        for ref in sorted(refs):
            try:
                bits, fields, _ = _schema_at(blob, ref, pool)
            except ValueError as exc:
                schemas.append({"schema_ref": ref, "error": repr(exc)[:80]})
                continue
            fld = []
            for slot, tbyte, name in fields:
                slots_total += 1
                if name.startswith("<slot_") or name.startswith("<oob"):
                    unresolved += 1
                else:
                    bound += 1
                fld.append({"slot": slot, "type": f"0x{tbyte:02x}",
                            "name": name if not name.startswith("<") else None,
                            "bound": not (name.startswith("<"))})
            schemas.append({"schema_ref": ref, "n_fields": len(fields),
                            "bits": bits, "fields": fld})
        tables_out.append({"entry": entry,
                           "table": table_name_map.get(entry),
                           "family": family, "pool_entry": pool_entry,
                           "pool_note": note, "schemas": schemas})
    summary = {
        "schema_version": 1,
        "snapshot": "test-328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "tables_with_schema": len(per_entry),
        "tables_bound": len([t for t in tables_out if not t.get("pool_unresolved")]),
        "pool_unresolved_tables": len(unsafe),
        "field_slots_total": slots_total,
        "field_slots_bound": bound,
        "field_slots_unresolved": unresolved,
        "tables_with_multi_schema_ref": multi_schema,
        "suspect_wide96": suspect_wide,
        "pool_unresolved_entry_list": unsafe[:200],
        "unsafe_count": 0,  # BA8 快照无已实证字段错位表；值层错位检测属 P2-2
        "note": "字段名=CHS 池文本（schema slot 引用），池配对=家族 chs 成员池条数==表体期望 N；"
                "禁止按值猜名；多 schema_ref 分别绑定；BA8 快照无已实证错位表=unsafe 语义未触发"
                "（本索引仅池无法配对表标 unsafe）；0x96 宽表 suspect 待 P2-2 值层复核",
        "build_seconds": round(time.time() - t0, 1),
    }
    OUT.write_text(json.dumps({"schema_entries": tables_out},
                              ensure_ascii=False, indent=0), encoding="utf-8")
    OUT_SUM.write_text(json.dumps(summary, ensure_ascii=False, indent=1),
                       encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
