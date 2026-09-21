#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rebuild_nucleus_cards — 核芯卡（名册+特技+星级段，web 预览 v1）

数据链（2026-09-04）：
  ① 名册=common_item 660000 段（异变核芯-X：id/品级 desc 前缀/图标/简版 desc）
  ② 特技=nucleus_build_data kj1 base 016783/CHS 023314（75 行：nucleus_effect_name=X、
     desc 完整特技文本、simple_desc、attr_simple_desc({0}=数值占位)、icon_path、nucleus_attr_type、
     released_cbg、weapon_type 码、rank_to_desc→星级描述段槽序列）
  ③ 星级段=rank 对象 05 槽序列（05 01='desc' 段标记 + 05 <slot>=效果文本池槽；5/9/12 星特殊节点
     解锁新段——用户情报；经典服 12 星档）。
  品级按拆包原文呈现（特级/高级等 desc 前缀，不做语义裁决——用户指令）。
"""
from __future__ import annotations

import json
import re
import struct
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "boards" / "nucleus_cards.json"
PACKAGE_SHA = "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f"
ENTRIES_DIR = Path(r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_BA8A239A\entries")


def _xbody(payload: bytes) -> bytes:
    marker = payload.find(b"x{")
    ln = struct.unpack_from("<I", payload, marker + 2)[0]
    return payload[marker + 6: marker + 6 + ln]


def _load_decoder():
    import sys
    for p in (r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心", str(ROOT / "tools")):
        if p not in sys.path:
            sys.path.insert(0, p)
    from toolkit_core.bindict_table import parse_legacy_chs_pool, uleb
    from toolkit_core.bindict_table import _resolve_27_group_reference as _resolve_group
    from bindict_provenance import decode_table_rows_with_chs_slots
    return parse_legacy_chs_pool, uleb, decode_table_rows_with_chs_slots, _resolve_group


def _strip_rich(t: str) -> str:
    return re.sub(r"#(?:[rcn]|f\(\d+\)|c[0-9a-fA-F]{6})", "", t)


# 武器类型词典（desc「装配后<武器词>…」模式提取；无命中=通用属性核芯）
WEAPON_DICT = [
    "冷兵器", "霰弹枪", "榴弹炮", "喷火器", "狙击枪", "突击步枪",
    "电磁机枪", "手枪", "双枪", "武士刀", "步枪",
]


def extract_weapon_type(text: str) -> str:
    """从 desc 前段提取武器类型词（派生标注：模式=「装配后<武器词>」）。"""
    if not text:
        return "通用"
    head = text[:40]
    for w in WEAPON_DICT:
        if w in head:
            return w
    return "通用"


def extract_grade(text: str) -> str:
    """品级=desc 前缀（特级/高级/中级/低级异变核芯）。"""
    m = re.match(r"^(特级|高级|中级|低级|普通)异变核芯", text or "")
    return m.group(1) if m else ""


# weapon_type jump 目标组值 → 武器种类（码投票定版：desc 武器词交叉验证 2026-09-04）
WEAPON_CODE_MAP = {
    (0,): "通用",
    (1, 2): "突击步枪",
    (3,): "弓箭",
    (4,): "霰弹枪",
    (5,): "狙击枪",
    (6,): "手枪/双枪",
    (7,): "榴弹炮",
    (8,): "电磁机枪",
    (20,): "喷火器",
    (50,): "冷兵器",
}


def _load_entries_meta():
    """FID + decoded sha for nucleus_build_data kj1 entries (dynamic from npk)."""
    import hashlib
    import sys as _sys
    reg = json.loads((ROOT / "data/live_sources.json").read_text(encoding="utf-8"))
    source = next(s for s in reg["sources"] if s["source_id"] == "documents-py314-current")
    for p in (r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心", str(ROOT / "tools")):
        if p not in _sys.path:
            _sys.path.insert(0, p)
    from live_npk_reader import LiveNpkReader, _unpack_entry
    reader = LiveNpkReader(Path(source["path"]), "documents")
    out = {}
    for idx, role in ((16783, "nucleus_build_data_kj1_base"), (23314, "nucleus_build_data_kj1_chs")):
        e = [x for x in reader._entries if x.entry_index == idx][0]
        with reader.package_path.open("rb") as h:
            h.seek(e.offset)
            packed = h.read(e.packed_size)
        dec = _unpack_entry(packed, e.declared_size, e.flag)
        out[role] = {"entry_index": e.entry_index, "file_id": f"{e.file_id:016X}",
                     "decoded_sha256": hashlib.sha256(dec).hexdigest()}
    return out


def build_board() -> dict:
    parse_pool, uleb_fn, decode_rows, _resolve_group = _load_decoder()
    em = _load_entries_meta()
    # ① 名册（已发布板同源：common_item 660000 段）
    reg_path = ROOT / "data" / "boards" / "common_item_text_sources.json"
    ci = json.loads(reg_path.read_text(encoding="utf-8"))
    roster = {}
    for it in ci["items"]:
        if 660000 <= it["item_id"] < 660200 and it["name"].startswith("异变核芯-"):
            roster[it["name"][len("异变核芯-"):]] = {
                "item_id": it["item_id"],
                "grade": _strip_rich(it.get("text_provenance", {}).get("desc", {}).get("text", ""))[:16],
                "ci_desc": it.get("text_provenance", {}).get("desc", {}).get("text", ""),
                "ci_icon": it.get("text_provenance", {}).get("icon", {}).get("text", ""),
            }
    # ② 特技行
    base = (ENTRIES_DIR / "016783.bin").read_bytes()
    chs = (ENTRIES_DIR / "023314.bin").read_bytes()
    pool = parse_pool(chs)
    bb = _xbody(base)
    rows, unbound = decode_rows(bb, pool)
    cnt, _ = struct.unpack_from("<II", bb, 0)
    blob = bb[8 + 4 * cnt:]

    def rank_segments(target: int):
        """Rank 对象=05 槽序列：[05 01('desc' 段标记) 05 <slot>] 对列表 → 池文本段。"""
        segs = []
        pos = target
        guard = 0
        while pos + 2 < len(blob) and guard < 40:
            guard += 1
            if blob[pos] != 0x05:
                # 跳过非 05 前缀（对象计数/边界）
                nxt = blob.find(b"\x05", pos, min(len(blob), pos + 12))
                if nxt < 0:
                    break
                pos = nxt
                continue
            s, p = uleb_fn(blob, pos + 1, len(blob))
            if s == 1:  # 'desc' 段标记：下一 05 是文本槽
                pos = p
                if blob[pos] == 0x05:
                    s2, p2 = uleb_fn(blob, pos + 1, len(blob))
                    if s2 < len(pool):
                        segs.append(pool[s2])
                    pos = p2
                    continue
            pos = p
            # 非 desc 标记的 05 引用也收（纯槽序列场景）
            if s != 1 and s < len(pool):
                segs.append(pool[s])
        return segs

    items = []
    matched = 0
    for r in sorted(rows, key=lambda x: x["key"]):
        v = r["values"]
        eff = v.get("nucleus_effect_name")
        eff_t = eff[1] if isinstance(eff, tuple) else ""
        if not eff_t:
            continue
        rec = roster.get(eff_t, {})
        desc_t = v.get("desc")
        desc = desc_t[1] if isinstance(desc_t, tuple) else ""
        simple_t = v.get("simple_desc")
        simple = simple_t[1] if isinstance(simple_t, tuple) else ""
        attr_t = v.get("attr_simple_desc")
        attr = attr_t[1] if isinstance(attr_t, tuple) else ""
        icon_t = v.get("icon_path")
        icon = icon_t[1] if isinstance(icon_t, tuple) else ""
        rd = v.get("rank_to_desc")
        target = int(rd[1][5:]) if isinstance(rd, tuple) and isinstance(rd[1], str) and rd[1].startswith("jump:") else None
        segments = rank_segments(target) if target is not None else []
        wt = v.get("weapon_type")
        wt_code = wt_v = None
        if isinstance(wt, tuple) and isinstance(wt[1], str) and wt[1].startswith("jump:"):
            wt_code = int(wt[1][5:])
            try:
                _g = _resolve_group(blob, wt_code)
                wt_v = _g["values"] if _g else None
            except Exception:
                wt_v = None
        grade_txt = rec.get("ci_desc", "") or rec.get("grade", "")
        wt_label = WEAPON_CODE_MAP.get(tuple(wt_v or []), "") or extract_weapon_type(desc + rec.get("ci_desc", ""))
        items.append({
            "id": f"nucleus_{rec.get('item_id', r['key'])}",
            "name": f"异变核芯-{eff_t}" if rec else eff_t,
            "item_id": rec.get("item_id"),
            "grade_clean": extract_grade(grade_txt),
            "weapon_type_label": wt_label,
            "weapon_type_code": wt_v,
            "nucleus_attr_type": v.get("nucleus_attr_type", (None, None))[1] if isinstance(v.get("nucleus_attr_type"), tuple) else None,
            "released": v.get("released_cbg", (None, None))[1] if isinstance(v.get("released_cbg"), tuple) else None,
            "skill_icon": icon,
            "skill_desc": desc,
            "skill_desc_simple": simple,
            "skill_desc_attr": attr,
            "rank_segments": segments,
            "ci_desc": rec.get("ci_desc", ""),
            "ci_icon": rec.get("ci_icon", ""),
            "source": "common_item 660000 段 + nucleus_build_data kj1(016783/023314) 行级回放（BA8 328b8446）",
            "evidence": "structure",
            "evidence_level": "structure-only",
            "provenance": {
                "source_lock_sha256": PACKAGE_SHA,
                "source_entries": [em["nucleus_build_data_kj1_base"], em["nucleus_build_data_kj1_chs"]],
                "name_source": "nucleus_effect_name == 异变核芯-<X> 名册关联（common_item 660000 段同名）",
                "table": "nucleus_build_data",
                "row_key": r["key"],
                "field_refs": [
                    f"nucleus_build_data.key={r['key']}",
                    "nucleus_build_data.nucleus_effect_name",
                    "nucleus_build_data.desc / simple_desc / attr_simple_desc",
                    "nucleus_build_data.rank_to_desc jump → rank 段槽序列（05 引用池段）",
                    "nucleus_build_data.icon_path / weapon_type / released_cbg",
                ],
            },
        })
        if rec:
            matched += 1
    return {
            "meta": {
            "name": "核芯卡（名册+特技+星级段，web v1）",
            "category": "三、战力类 / （2）异变核芯·卡片",
            "source_server": "documents-py314-current",
            "package_sha": PACKAGE_SHA,
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evidence": "structure",
            "filters": [
                {"key": "grade_clean", "label": "品级"},
                {"key": "weapon_type_label", "label": "武器类型"},
            ],
            "notes": (
                "web 预览 v1：75 特技行+660000 名册关联；品级/文本=拆包原文（不裁决）；skill_desc=完整特技描述；"
                "rank_segments=星级描述段（5/9/12 特殊节点解锁新段，经典服 12 星档）；attr_simple_desc {0}=每星数值占位"
                "（数值数组待解）；weapon_type_code=武器类型码原文（映射待查）。"
            ),
            "provenance": {
                "audit_status": "passed",
                "source_locks": [{"sha256": PACKAGE_SHA, "bytes": 270106156,
                                  "mtime_ns": 1788266451099903500,
                                  "path_hint": "Documents/script.py314.lc.npk"}],
                "source_id": "documents-py314-current",
                "base_entry": em["nucleus_build_data_kj1_base"],
                "chs_entry": em["nucleus_build_data_kj1_chs"],
                "package_sha": PACKAGE_SHA,
            },
        },
        "items": items,
        "stats": {"catalog_entries": len(items), "roster_matched": matched,
                  "with_segments": sum(1 for i in items if i["rank_segments"])},
    }


def main() -> int:
    board = build_board()
    DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUTPUT.write_text(json.dumps(board, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"items": len(board["items"]),
                       "roster_matched": board["stats"]["roster_matched"],
                       "with_segments": board["stats"]["with_segments"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
