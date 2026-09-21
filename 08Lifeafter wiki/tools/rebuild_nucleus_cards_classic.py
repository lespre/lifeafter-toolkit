#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rebuild_nucleus_cards_classic — 核芯卡合并版（双服：经典服 12 星主体 + 简单生存服独有）

v2 (2026-09-04 用户定版)：
  - 经典服 76 颗（nucleus_build_data 主表 40949/34899，5/9/12 星级段完整）
  - + 简单生存服独有核芯（BA8 kj1 行，星级段以简单生存服体验服快照为准）
  - 品级=经典服 kj1 common_item 覆盖 + BA8 common_item 660000 名册兜底
  - 武器类型显示=种类（码）同行；simple/attr 文案不进卡（数据层保留于源码回放）
"""
from __future__ import annotations

import json
import re
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "boards" / "nucleus_cards_classic.json"
PACKAGE_SHA_CLASSIC = "79c0d06f53db02ca4f8ebad97da2cfef22916f963e8cae3461b914d4a39bb85d"
NPK_CLASSIC = Path(r"E:\LifeAfter\Documents\script.py314.lc.npk")
ENTRIES_CLASSIC = [
    ("common_item_kj1_base", 9503),
    ("common_item_kj1_chs", 28181),
    ("nucleus_build_data_base", 40949),
    ("nucleus_build_data_chs", 34899),
]
# 简单生存服·体验服（BA8）：淬焰燃锋等独有核芯 + 名册品级兜底
BA8_ENTRIES = r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_BA8A239A\entries"
BA8_BUILD_BASE = 16783
BA8_BUILD_CHS = 23314
BA8_CI_BASE = 18005
BA8_CI_CHS = 18006
PACKAGE_SHA_BA8 = "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f"

WEAPON_CODE_MAP = {
    (0,): "通用", (1, 2): "突击步枪", (3,): "弓箭", (4,): "霰弹枪", (5,): "狙击枪",
    (6,): "手枪/双枪", (7,): "榴弹炮", (8,): "电磁机枪", (20,): "喷火器", (50,): "冷兵器",
}
BA8_CORE_FILE_IDS = {"016783": "PLACEHOLDER", "023314": "PLACEHOLDER",
                     "018005": "PLACEHOLDER", "018006": "PLACEHOLDER"}


def _strip_rich(t: str) -> str:
    return re.sub(r"#(?:[rcn]|f\(\d+\)|c[0-9a-fA-F]{6})", "", t)


def _grade_of(text: str) -> str:
    m = re.match(r"^(特级|高级|中级|低级|普通)异变核芯", text or "")
    return m.group(1) if m else ""


def _load():
    import sys as _s
    for p in (r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心", str(ROOT / "tools")):
        if p not in _s.path:
            _s.path.insert(0, p)
    from toolkit_core.bindict_table import parse_legacy_chs_pool, uleb
    from toolkit_core.bindict_table import _resolve_27_group_reference
    from live_npk_reader import LiveNpkReader, _unpack_entry
    from bindict_provenance import decode_table_rows_with_chs_slots
    return (parse_legacy_chs_pool, uleb, _resolve_27_group_reference,
            LiveNpkReader, _unpack_entry, decode_table_rows_with_chs_slots)


def _xbody(payload: bytes) -> bytes:
    m = payload.find(b"x{")
    ln = struct.unpack_from("<I", payload, m + 2)[0]
    return payload[m + 6:m + 6 + ln]


class NpkSource:
    def __init__(self, path: str, sha: str, entries: list, parse_pool, unpack, reader_cls):
        self.path = path
        self.sha = sha
        self.entries = entries
        self.reader = reader_cls(path, "documents")
        self.by_idx = {e.entry_index: e for e in self.reader._entries}
        self.by_fid = {e.file_id: e for e in self.reader._entries}
        self.parse_pool = parse_pool
        self.unpack = unpack

    def entry_bytes(self, idx):
        e = self.by_fid.get(idx) or self.by_idx.get(idx)
        if e is None:
            raise KeyError(idx)
        with open(self.path, "rb") as h:
            h.seek(e.offset)
            packed = h.read(e.packed_size)
        return self.unpack(packed, e.declared_size, e.flag)

    def entry_meta(self):
        import hashlib
        out = []
        for role, ei in self.entries:
            e = self.by_idx[ei]
            out.append({"entry_index": ei, "role": role,
                        "file_id": f"{e.file_id:016X}",
                        "decoded_sha256": hashlib.sha256(self.entry_bytes(ei)).hexdigest()})
        return out


def build_board() -> dict:
    parse_pool, uleb_fn, resolve, LiveNpkReader, unpack, decode_rows = _load()
    # ========== ① 经典服（主源 12 星） ==========
    cls = NpkSource(str(NPK_CLASSIC), PACKAGE_SHA_CLASSIC, ENTRIES_CLASSIC,
                    parse_pool, unpack, LiveNpkReader)
    # 名册（kj1 增量：淬焰燃锋/碎冰飞溅等）
    ci_pool = cls.parse_pool(cls.entry_bytes(28181))
    ci_rows, _ = decode_rows(_xbody(cls.entry_bytes(9503)), ci_pool)
    roster_classic = {}
    # 品级正源：正式服 common_item 主表 660000 段（同 FID 两服同表）desc 前缀
    grade_pool = cls.parse_pool(cls.entry_bytes(0xEF3A8474A5E5F7A4))
    g_rows, _ = decode_rows(_xbody(cls.entry_bytes(0xB42760CCA41DBC25)), grade_pool)
    grade_660 = {}
    for g_r in g_rows:
        k = int(g_r["key"])
        if not (660000 <= k <= 660149):
            continue
        gv = g_r["values"]
        g_nm = gv.get("name")
        g_nm_t = g_nm[1] if isinstance(g_nm, tuple) else ""
        if not (isinstance(g_nm_t, str) and g_nm_t.startswith("异变核芯-")):
            continue
        g_d = gv.get("desc")
        g_d_t = g_d[1] if isinstance(g_d, tuple) else ""
        gm = re.match(r"^(特级|高级|中级|低级|普通)异变核芯", g_d_t)
        if gm:
            nm_k = g_nm_t[len("异变核芯-"):]
            prev = grade_660.get(nm_k)
            grade_660[nm_k] = {"grade": gm.group(1),
                               "ci_id": min(prev["ci_id"], k) if prev else k}
    for r in ci_rows:
        v = r["values"]
        nm = v.get("name")
        if not (isinstance(nm, tuple) and isinstance(nm[1], str) and nm[1].startswith("异变核芯-")):
            continue
        desc_t = v.get("desc")
        roster_classic[nm[1][len("异变核芯-"):]] = {
            "item_id": int(r["key"]),
            "grade": _grade_of(desc_t[1] if isinstance(desc_t, tuple) else ""),
            "ci_desc": desc_t[1] if isinstance(desc_t, tuple) else "",
        }
    # 主表 76 行
    bd_pool = cls.parse_pool(cls.entry_bytes(34899))
    bd_rows, _ = decode_rows(_xbody(cls.entry_bytes(40949)), bd_pool)
    cnt, _ = struct.unpack_from("<II", _xbody(cls.entry_bytes(40949)), 0)
    blob = _xbody(cls.entry_bytes(40949))[8 + 4 * cnt:]

    def rank_map(blob_, target):
        if target is None or target >= len(blob_) or blob_[target] != 0x36:
            return {}
        c, pos = uleb_fn(blob_, target + 3, len(blob_))
        out = {}
        for _ in range(c):
            k, pos = uleb_fn(blob_, pos, len(blob_))
            v, pos = uleb_fn(blob_, pos, len(blob_))
            if v < len(bd_pool):
                out[str(k)] = bd_pool[v]
        return out

    def wt_label_of(wt_raw):
        codes = None
        if isinstance(wt_raw, tuple) and isinstance(wt_raw[1], str) and wt_raw[1].startswith("jump:"):
            g = resolve(blob, int(wt_raw[1][5:]))
            codes = g["values"] if g else None
        label = WEAPON_CODE_MAP.get(tuple(codes or []), "")
        code_txt = "、".join(str(c) for c in codes) if codes else ""
        return label, code_txt

    items = []
    src_by_id = {}
    for r in sorted(bd_rows, key=lambda x: x["key"]):
        v = r["values"]
        eff = v.get("nucleus_effect_name")
        eff_t = eff[1] if isinstance(eff, tuple) else ""
        if not eff_t:
            continue
        rec = roster_classic.get(eff_t, {})
        desc_t = v.get("desc")
        icon_t = v.get("icon_path")
        rd = v.get("rank_to_desc")
        target = int(rd[1][5:]) if isinstance(rd, tuple) and isinstance(rd[1], str) and rd[1].startswith("jump:") else None
        stars = rank_map(blob, target)
        label, code_txt = wt_label_of(v.get("weapon_type"))
        item_id = rec.get("item_id") or f"nuc_{r['key']}"
        items.append({
            "id": f"nuc_{item_id}",
            "name": f"异变核芯-{eff_t}",
            "item_id": item_id,
            "grade_clean": (rec.get("grade", "") or (grade_660.get(eff_t) or {}).get("grade", "")),
            "sort_660": (grade_660.get(eff_t) or {}).get("ci_id", 0),
            "weapon_type_label": label,
            "weapon_type_display": f"{label}（{code_txt}）" if label and code_txt else label or code_txt or "",
            "weapon_type_code": code_txt,
            "skill_icon": icon_t[1] if isinstance(icon_t, tuple) else "",
            "skill_desc": desc_t[1] if isinstance(desc_t, tuple) else "",
            "rank_star_segments": stars,
            "server_branch": "经典服",
            "source": "经典服 nucleus_build_data 主表(40949/34899)+kj1(9503/28181) 行级回放（79c0d06f）",
        })
        src_by_id[str(item_id)] = "经典服"

    # ========== ② 简单生存服·体验服（BA8）独有核芯 ==========
    E = BA8_ENTRIES
    ba8_pool = parse_pool(open(Path(E) / "023314.bin", "rb").read())
    ba8_rows, _ = decode_rows(_xbody(open(Path(E) / "016783.bin", "rb").read()), ba8_pool)
    ba8_ci_pool = parse_pool(open(Path(E) / "018006.bin", "rb").read())
    ba8_ci_rows, _ = decode_rows(_xbody(open(Path(E) / "018005.bin", "rb").read()), ba8_ci_pool)
    ba8_roster = {}
    for r in ba8_ci_rows:
        v = r["values"]
        nm = v.get("name")
        if not (isinstance(nm, tuple) and isinstance(nm[1], str) and nm[1].startswith("异变核芯-")):
            continue
        desc_t = v.get("desc")
        ba8_roster[nm[1][len("异变核芯-"):]] = {
            "item_id": int(r["key"]),
            "grade": _grade_of(desc_t[1] if isinstance(desc_t, tuple) else ""),
            "ci_desc": desc_t[1] if isinstance(desc_t, tuple) else "",
        }
    cnt_b, _ = struct.unpack_from("<II", _xbody(open(Path(E) / "016783.bin", "rb").read()), 0)
    blob_b = _xbody(open(Path(E) / "016783.bin", "rb").read())[8 + 4 * cnt_b:]
    for r in sorted(ba8_rows, key=lambda x: x["key"]):
        v = r["values"]
        eff = v.get("nucleus_effect_name")
        eff_t = eff[1] if isinstance(eff, tuple) else ""
        if not eff_t:
            continue
        if any(i["name"] == f"异变核芯-{eff_t}" for i in items):
            continue  # 经典服主表已有（12 星版为准）；kj1 名册在册但主表没有=简单生存服独有
        rec = ba8_roster.get(eff_t, {})
        desc_t = v.get("desc")
        icon_t = v.get("icon_path")
        rd = v.get("rank_to_desc")
        target = int(rd[1][5:]) if isinstance(rd, tuple) and isinstance(rd[1], str) and rd[1].startswith("jump:") else None
        stars = {}
        if target is not None and target < len(blob_b) and blob_b[target] == 0x36:
            c, pos = uleb_fn(blob_b, target + 3, len(blob_b))
            for _ in range(c):
                k, pos = uleb_fn(blob_b, pos, len(blob_b))
                vv, pos = uleb_fn(blob_b, pos, len(blob_b))
                if vv < len(ba8_pool):
                    stars[str(k)] = ba8_pool[vv]
        # 简单生存服 BA8 只有 5 星段（体验服快照）——星级段如实标注，来源注明
        label, code_txt = "", ""
        wt_raw = v.get("weapon_type")
        codes = None
        if isinstance(wt_raw, tuple) and isinstance(wt_raw[1], str) and wt_raw[1].startswith("jump:"):
            g = resolve(blob_b, int(wt_raw[1][5:]))
            codes = g["values"] if g else None
        label = WEAPON_CODE_MAP.get(tuple(codes or []), "")
        code_txt = "、".join(str(c) for c in codes) if codes else ""
        items.append({
            "id": f"nuc_{rec.get('item_id', r['key'])}",
            "name": f"异变核芯-{eff_t}",
            "item_id": rec.get("item_id"),
            "grade_clean": (rec.get("grade", "") or (grade_660.get(eff_t) or {}).get("grade", "")),
            "sort_660": (grade_660.get(eff_t) or {}).get("ci_id", 0),
            "weapon_type_label": label,
            "weapon_type_display": f"{label}（{code_txt}）" if label and code_txt else label or code_txt or "",
            "weapon_type_code": code_txt,
            "skill_icon": icon_t[1] if isinstance(icon_t, tuple) else "",
            "skill_desc": desc_t[1] if isinstance(desc_t, tuple) else "",
            "rank_star_segments": stars,
            "server_branch": "简单生存服",
            "source": "简单生存服·体验服 nucleus_build_data kj1(016783/023314)+common_item(018005/018006) 行级回放（328b8446）；星级段以 5 星快照为准（正式 12 星待简单生存服正式包）",
        })

    import hashlib as _hl
    cls_meta = cls.entry_meta()
    ba8_npk = NpkSource(r"E:\mrzh\Documents\script.py314.lc.npk", PACKAGE_SHA_BA8,
                        [("nucleus_build_data_kj1_base", 16783),
                         ("nucleus_build_data_kj1_chs", 23314),
                         ("common_item_base", 18005),
                         ("common_item_chs", 18006)],
                        parse_pool, unpack, LiveNpkReader)
    ba8_meta = ba8_npk.entry_meta()
    for it in items:
        it["evidence"] = "structure"
        it["evidence_level"] = "structure-only"
        it["provenance"] = {
            "source_lock_sha256": PACKAGE_SHA_CLASSIC if it["server_branch"] == "经典服" else PACKAGE_SHA_BA8,
            "source_entries": cls_meta if it["server_branch"] == "经典服" else ba8_meta,
            "name_source": "nucleus_build_data.nucleus_effect_name（经典服主表 / BA8 kj1）",
            "table": "nucleus_build_data",
            "row_key": it["id"],
            "field_refs": [
                "nucleus_build_data.desc(核芯特技) / rank_to_desc→0x36 MAPPING(星→段)",
                "nucleus_build_data.icon_path / weapon_type(组码→种类映射) / released_cbg",
            ],
        }
    items.sort(key=lambda x: (x["server_branch"] != "经典服", x["name"]))
    return {
        "meta": {
            "name": "核芯卡（双服合并：经典服 12 星 + 简单生存服独有）",
            "category": "三、战力类 / （二）核芯",
            "source_server": "lifeafter-classic-current + documents-py314-current",
            "package_sha": PACKAGE_SHA_CLASSIC,
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evidence": "structure",
            "filters": [
                {"key": "grade_clean", "label": "品级"},
                {"key": "weapon_type_label", "label": "武器类型"},
            ],
            "notes": (
                "双服合并：经典服 76 颗为 12 星完整版（星级段 5/9/12 特殊节点描述）；"
                "简单生存服独有核芯（淬焰燃锋等）星级段以简单生存服·体验服快照为准；"
                "同名核芯两服取经典服 12 星版；品级=desc 前缀原文（不裁决）。"
            ),
            "provenance": {
                "audit_status": "passed",
                "source_locks": [
                    {"sha256": PACKAGE_SHA_CLASSIC, "bytes": 366060232,
                     "mtime_ns": 0, "path_hint": "LifeAfter/Documents/script.py314.lc.npk（经典服）"},
                    {"sha256": PACKAGE_SHA_BA8, "bytes": 270106156,
                     "mtime_ns": 0, "path_hint": "mrzh/Documents/script.py314.lc.npk（简单生存服·体验服）"},
                ],
                "source_id": "lifeafter-classic-current,documents-py314-current",
                "package_sha": PACKAGE_SHA_CLASSIC,
            },
        },
        "items": items,
        "stats": {"catalog_entries": len(items),
                  "classic_12star": sum(1 for i in items if i["server_branch"] == "经典服"),
                  "simple_only": sum(1 for i in items if i["server_branch"] == "简单生存服"),
                  "with_star_segments": sum(1 for i in items if i["rank_star_segments"])},
    }


def main() -> int:
    board = build_board()
    DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUTPUT.write_text(json.dumps(board, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"items": len(board["items"]),
                       "classic": board["stats"]["classic_12star"],
                       "simple_only": board["stats"]["simple_only"],
                       "with_star_segments": board["stats"]["with_star_segments"]},
                      ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
