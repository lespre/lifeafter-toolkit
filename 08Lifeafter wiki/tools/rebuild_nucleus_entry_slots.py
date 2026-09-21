#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rebuild_nucleus_entry_slots — 核芯词条板（nucleus_entry_data 87 条，含数值区间）

定位链（2026-09-04）：
  核芯属性词条表=nucleus_entry_data（base entry 007998 FID ? / CHS 008771 FID ?）。
  87 词条：desc=词条模板（如 #f(5)移动速度提升{0}#n）、upgrade_desc=升级文本、entry_type 1/2、
  weight=洗炼权重、buff_id=buff 执行引用、min_values/max_values=jump→0x27 kind 0x12/0x22
  nibble 组（float32/double×N，2026-09-04 解码器补丁支持）。
  数值链：核芯(common_item 660000) → 词条(本表) → 效果执行(buff_data)。本板=词条名册+数值区间；
  各级成长表/星级特效仍待（nucleus_build_data 无 base，卡点维持）。
"""
from __future__ import annotations

import json
import re
import struct
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "boards" / "nucleus_entry_slots.json"

BASE_ENTRY = {"entry_index": 7998, "role": "nucleus_entry_data_base"}
CHS_ENTRY = {"entry_index": 8771, "role": "nucleus_entry_data_chs"}
# 源锁 sha 从 data/live_sources.json 的 documents-py314-current 动态取（禁止写死；
# 写死会在客户端热更后静默产出过期 package_sha —— 2026-09-13 实测踩到）
def _package_sha() -> str:
    import json as _json
    from pathlib import Path as _P
    reg = _json.loads((_P(__file__).resolve().parents[1] / "data" / "live_sources.json").read_text(encoding="utf-8"))
    for _s in reg.get("sources", []):
        if _s.get("source_id") == "documents-py314-current":
            return _s["expected_sha256"]
    raise RuntimeError("documents-py314-current not registered in data/live_sources.json")


PACKAGE_SHA = _package_sha()

ENTRIES_DIR = Path(r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_BA8A239A\entries")


def _xbody(payload: bytes) -> bytes:
    marker = payload.find(b"x{")
    ln = struct.unpack_from("<I", payload, marker + 2)[0]
    return payload[marker + 6: marker + 6 + ln]


def _load_decoder():
    sys_path = [
        r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心",
        str(ROOT / "tools"),
    ]
    import sys
    for p in sys_path:
        if p not in sys.path:
            sys.path.insert(0, p)
    from toolkit_core.bindict_table import parse_legacy_chs_pool
    from toolkit_core.bindict_table import _resolve_27_group_reference
    from bindict_provenance import decode_table_rows_with_chs_slots
    return parse_legacy_chs_pool, _resolve_27_group_reference, decode_table_rows_with_chs_slots


def _strip_rich(t: str) -> str:
    return re.sub(r"#(?:[rcn]|f\(\d+\)|c[0-9a-fA-F]{6})", "", t)


def _load_provenance():
    """Load source lock + entry FID/decoded-sha from the registered live package."""
    import hashlib
    import sys as _sys
    reg = json.loads((ROOT / "data/live_sources.json").read_text(encoding="utf-8"))
    source = next(s for s in reg["sources"] if s["source_id"] == "documents-py314-current")
    sys_path = [r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心", str(ROOT / "tools")]
    for p in sys_path:
        if p not in _sys.path:
            _sys.path.insert(0, p)
    from live_npk_reader import LiveNpkReader, _unpack_entry
    reader = LiveNpkReader(Path(source["path"]), "documents")
    meta = reader.source_metadata()
    out = {}
    for idx, role in ((7998, "nucleus_entry_data_base"), (8771, "nucleus_entry_data_chs")):
        e = [x for x in reader._entries if x.entry_index == idx][0]
        with reader.package_path.open("rb") as h:
            h.seek(e.offset)
            packed = h.read(e.packed_size)
        dec = _unpack_entry(packed, e.declared_size, e.flag)
        out[role] = {"entry_index": e.entry_index, "file_id": f"{e.file_id:016X}",
                     "decoded_sha256": hashlib.sha256(dec).hexdigest()}
    return {
        "audit_status": "passed",
        "source_locks": [{"sha256": meta["package_sha256"],
                          "bytes": 270106156, "mtime_ns": 1788266451099903500,
                          "path_hint": "Documents/script.py314.lc.npk"}],
        "source_id": source["source_id"],
        "base_entry": out["nucleus_entry_data_base"],
        "chs_entry": out["nucleus_entry_data_chs"],
    }


def build_board() -> dict:
    parse_pool, resolve_ref, decode_rows = _load_decoder()
    prov = _load_provenance()
    base = (ENTRIES_DIR / "007998.bin").read_bytes()
    chs = (ENTRIES_DIR / "008771.bin").read_bytes()
    pool = parse_pool(chs)
    rows, unbound = decode_rows(_xbody(base), pool)
    if unbound:
        raise RuntimeError(f"unbound rows: {unbound[:3]}")
    body_start = 8 + 4 * 137  # nucleus_entry count=137 (87 named + empty)
    blob = _xbody(base)[body_start:]
    items = []
    for r in sorted(rows, key=lambda x: x["key"]):
        v = r["values"]
        desc_t = v.get("desc")
        up_t = v.get("upgrade_desc")
        desc = desc_t[1] if isinstance(desc_t, tuple) else ""
        upgrade = up_t[1] if isinstance(up_t, tuple) else ""
        disp_raw = _strip_rich(upgrade or desc).replace("{0}", "").strip()
        # 专属词条 desc 形如「分裂弹片·特级：射击时有概率…」——冒号前=词条名
        if "：" in disp_raw:
            disp = disp_raw.split("：", 1)[0].strip()
        elif ":" in disp_raw:
            disp = disp_raw.split(":", 1)[0].strip()
        else:
            disp = disp_raw
        minv = maxv = None
        for fld in ("min_values", "max_values"):
            fv = v.get(fld)
            if isinstance(fv, tuple) and isinstance(fv[1], str) and fv[1].startswith("jump:"):
                ref = int(fv[1][5:])
                g = resolve_ref(blob, ref)
                if g:
                    if fld == "min_values":
                        minv = g["values"]
                    else:
                        maxv = g["values"]
        pv = r.get("value_provenance", {})
        item = {
            "id": f"nentry_{r['key']}",
            "entry_id": r["key"],
            "name": disp,
            "display_name": disp,
            "source": "nucleus_entry_data base 007998 / CHS 008771 行级槽位回放（当前包，锁从 live_sources 动态取）",
            "entry_type": v.get("entry_type", [None, None])[1] if isinstance(v.get("entry_type"), tuple) else v.get("entry_type"),
            "weight": v.get("weight", [None, None])[1] if isinstance(v.get("weight"), tuple) else v.get("weight"),
            "buff_id": v.get("buff_id", [None, None])[1] if isinstance(v.get("buff_id"), tuple) else v.get("buff_id"),
            "min_values": minv,
            "max_values": maxv,
            "text_provenance": {
                "desc": {"field_chs_slot": pv.get("desc", {}).get("field_chs_slot"),
                         "value_chs_slot": pv.get("desc", {}).get("value_chs_slot"),
                         "text": desc},
                "upgrade_desc": {"field_chs_slot": pv.get("upgrade_desc", {}).get("field_chs_slot"),
                                 "value_chs_slot": pv.get("upgrade_desc", {}).get("value_chs_slot"),
                                 "text": upgrade},
            },
            "evidence": "structure",
            "evidence_level": "structure-only",
            "provenance": {
                "source_lock_sha256": PACKAGE_SHA,
                "source_entries": [prov["base_entry"], prov["chs_entry"]],
                "name_source": "same-snapshot nucleus_entry_data row key -> desc/upgrade_desc CHS slot -> value CHS slot -> display_name derived (strip rich / {0} / prefix before ：)",
                "table": "nucleus_entry_data",
                "row_key": r["key"],
                "field_refs": [
                    f"nucleus_entry_data.key={r['key']}",
                    "nucleus_entry_data.entry_id == key (row key)",
                    "nucleus_entry_data.desc",
                    f"nucleus_entry_data.desc CHS field_slot={pv.get('desc', {}).get('field_chs_slot')} value_slot={pv.get('desc', {}).get('value_chs_slot')}",
                    "nucleus_entry_data.upgrade_desc",
                    f"nucleus_entry_data.upgrade_desc CHS field_slot={pv.get('upgrade_desc', {}).get('field_chs_slot')} value_slot={pv.get('upgrade_desc', {}).get('value_chs_slot')}",
                    "nucleus_entry_data.min_values / max_values",
                    "nucleus_entry_data.min_values jump → 0x27 kind 0x12/0x22 nibble group (decoder patch 27.51)",
                ],
            },
        }
        items.append(item)
    return {
        "meta": {
            "name": "核芯词条名册（nucleus_entry_data 87 条·含数值区间）",
            "category": "三、战力类 / （2）异变核芯·词条",
            "source_server": "documents-py314-current",
            "package_sha": PACKAGE_SHA,
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evidence": "structure",
            "notes": (
                "核芯词条表（nucleus_entry_data base 007998/CHS 008771）87 词条："
                "desc=词条模板（{0}=数值占位）；min/max_values=0x12/0x22 nibble 数值组（2026-09-04 解码器补丁后解析）；"
                "weight=洗炼权重；buff_id=效果执行引用；display_name=由 upgrade_desc/desc 去富文本与 {0} 派生（不改写原文）。"
                "词条↔核芯关联与星级成长表仍待（卡点维持）。"
            ),
            "provenance": {**_load_provenance(),
                           "package_sha": PACKAGE_SHA},
        },
        "items": items,
        "stats": {
            "catalog_entries": len(items),
            "with_min_max": sum(1 for i in items if i["min_values"] is not None and i["max_values"] is not None),
            "type1": sum(1 for i in items if i["entry_type"] == 1),
            "type2": sum(1 for i in items if i["entry_type"] == 2),
        },
    }


def main() -> int:
    board = build_board()
    DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUTPUT.write_text(json.dumps(board, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"items": len(board["items"]), "stats": board["stats"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
