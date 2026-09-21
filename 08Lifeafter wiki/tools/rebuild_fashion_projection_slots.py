#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rebuild_fashion_projection_slots — 伴身投影（投影格）定位链板导出器

定位链（2026-09-04，用户三张实机锚点图）：
  游戏「时装搭配→投影」格的外观=buff_data 表（base entry 006675 FID 445751514818606E
  + CHS 002918 FID 1E23D0CBDFC4BEA7）中 sfx_path 指向 effect/.../benshentouying/
  （伴身投影资源目录）的 SfxBuff/IdleChangeFollowBuff/AddSocketModelBuff 行。
  name 形态：伴身投影·X / 伴身投影-X / 投影·X / 有龙则灵-X（sfx 同目录，无投影字样）。
  实机锚点核对：用户三图 27 名 → 24 精确命中本表（回旋音阶/烈焰燃蝶/浮光花丛/九尾蓝狐/
  浑天穹焰/赤红月噬/星海寄情/临渊流火/有龙则灵系/五行之力/破阵相思/燕字回时/时空裂隙/
  澜起掠影/浮灵幽幽/樱吹雪/悠游天地/梵影华光/海洋之歌/雪映流光/蔷薇来信/西湖燕尔/
  青焰流光/好运时间）；星河流淌/无尽之紫/星礼星愿 待续（buff 池 0 命中）。
"""
from __future__ import annotations

import hashlib
import json
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心")
from live_npk_reader import LiveNpkReader, _unpack_entry  # noqa: E402
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402

BUFF_BASE_FID = "445751514818606E"
BUFF_CHS_FID = "1E23D0CBDFC4BEA7"
SKIP_NAMES = {"\u4f34\u8eab\u6295\u5f71\u00b71219\u6d4b\u8bd5\u8d44\u6e90"}  # 伴身投影·1219测试资源


def _xbody(payload: bytes) -> bytes:
    marker = payload.find(b"x{")
    if marker < 0:
        raise ValueError("buff base: no x{ container")
    length = struct.unpack_from("<I", payload, marker + 2)[0]
    start = marker + 6
    end = start + length
    if end > len(payload):
        raise ValueError("buff base: x{ frame exceeds payload")
    return payload[start:end]


def _read_by_fid(reader: LiveNpkReader, file_id_hex: str) -> tuple[Any, bytes, dict]:
    matches = [e for e in reader._entries if e.file_id == int(file_id_hex, 16)]
    if len(matches) != 1:
        raise RuntimeError(f"expected one entry for FID {file_id_hex}, got {len(matches)}")
    entry = matches[0]
    with reader.package_path.open("rb") as h:
        h.seek(entry.offset)
        packed = h.read(entry.packed_size)
    decoded = _unpack_entry(packed, entry.declared_size, entry.flag)
    reader._assert_unchanged()
    return entry, decoded, {
        "entry_index": entry.entry_index,
        "file_id": file_id_hex,
        "decoded_sha256": hashlib.sha256(decoded).hexdigest(),
    }


def build_board(registry_path: Path) -> dict:
    ROOT = Path(__file__).resolve().parents[1]
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    source = next(s for s in registry["sources"] if s["source_id"] == "documents-py314-current")
    reader = LiveNpkReader(Path(source["path"]), "documents")
    meta = reader.source_metadata()
    if meta["package_sha256"] != source["expected_sha256"]:
        raise RuntimeError("current package SHA differs from live source registry")

    b_entry, b_payload, b_prov = _read_by_fid(reader, BUFF_BASE_FID)
    c_entry, c_payload, c_prov = _read_by_fid(reader, BUFF_CHS_FID)
    pool = parse_legacy_chs_pool(c_payload)
    rows, unbound = decode_table_rows_with_chs_slots(_xbody(b_payload), pool)
    source_entries = [
        {**b_prov, "role": "buff_data_base"},
        {**c_prov, "role": "buff_data_chs"},
    ]

    items = []
    for r in rows:
        nm = r["values"].get("name")
        sp = r["values"].get("sfx_path")
        if not (isinstance(nm, tuple) and isinstance(nm[1], str)):
            continue
        name = nm[1]
        sfx = sp[1] if isinstance(sp, tuple) and isinstance(sp[1], str) else None
        is_proj = ("\u6295\u5f71" in name) or (sfx and "benshentouying" in sfx)
        if not is_proj or name in SKIP_NAMES:
            continue
        prov = r.get("value_provenance", {}).get("name")
        text_prov = {}
        if isinstance(prov, dict) and isinstance(prov.get("field_chs_slot"), int) \
                and isinstance(prov.get("value_chs_slot"), int):
            text_prov["name"] = {**prov, "scalar_type": "0x05", "text": name}
        def val(f):
            v = r["values"].get(f)
            if isinstance(v, tuple) and v[1] is not None:
                return v[1]
            return None
        items.append({
            "id": f"proj_{r['key']}",
            "row_key": r["key"],
            "name": name,
            "display_name": name,
            "buff_class": val("buff_class"),
            "sfx_path": sfx,
            "sfx_socket": val("sfx_socket"),
            "type": val("type"),
            "effect_duration": val("effect_duration"),
            "schema_refs": [r["schema"]],
            "evidence": "structure",
            "evidence_level": "structure-only",
            "source": (
                "buff_data (FID 445751514818606E+1E23D0CBDFC4BEA7) row whose sfx_path "
                "points into effect/.../benshentouying/ or name contains 投影"
            ),
            "text_provenance": text_prov,
            "provenance": {
                "source_lock_sha256": meta["package_sha256"],
                "source_entries": source_entries,
                "table": "buff_data",
                "row_key": r["key"],
                "field_refs": [
                    f"buff_data.row_key={r['key']}",
                    "buff_data.name column-level 0x05 (buff name)",
                    f"buff_data.name CHS field_slot={prov.get('field_chs_slot') if isinstance(prov, dict) else '-'} "
                    f"value_slot={prov.get('value_chs_slot') if isinstance(prov, dict) else '-'}",
                ],
                "name_source": "buff_data name/sfx_path 定位链：伴身投影资源目录 benshentouying",
            },
        })

    # common_item 640000 系投影道具层名册：buff 名册缺的 3 个（星河流淌/无尽之紫/星礼星愿）
    # 以已发布 common_item 板为源（行级槽位已回放）
    ci_path = ROOT / "data" / "boards" / "common_item_text_sources.json"
    ci_items = {it["item_id"]: it for it in json.loads(ci_path.read_text(encoding="utf-8"))["items"]}
    for ci_id in (640001, 640020, 640032):
        it = ci_items.get(ci_id)
        if it is None:
            continue
        items.append({
            "id": f"proj_item_{ci_id}",
            "row_key": it["item_id"],
            "name": it["name"],
            "display_name": it["name"],
            "buff_class": None,
            "sfx_path": None,
            "sfx_socket": None,
            "type": None,
            "effect_duration": None,
            "schema_refs": it.get("schema_refs", []),
            "evidence": "structure",
            "evidence_level": "structure-only",
            "source": ("common_item 640000 \u7cfb\u6295\u5f71\u9053\u5177\u540d\u518c"
                       "\uff08icon_fx_640xxx\uff0c\u7528\u6237\u5b9e\u673a\u951a\u70b9\u540d\u4e0e\u4e4b\u4e00\u81f4\uff09"),
            "text_provenance": it.get("text_provenance", {}),
            "provenance": {
                "source_lock_sha256": meta["package_sha256"],
                "source_entries": source_entries,
                "table": "common_item",
                "row_key": it["item_id"],
                "field_refs": [
                    f"common_item.item_id={it['item_id']}",
                    "common_item name/desc/icon column-level 0x05",
                ],
                "name_source": "common_item 640000 \u7cfb\u6295\u5f71\u9053\u5177\uff08buff \u540d\u518c\u7f3a\u8fd9 3 \u540d\uff09",
            },
        })

    items.sort(key=lambda x: x["name"])
    return {
        "meta": {
            "name": "\u5f53\u524d\u5305 \u00b7 \u4f34\u8eab\u6295\u5f71\uff08\u6295\u5f71\u683c\uff09",
            "category": "二、时装类 / （五）投影",
            "source_server": source["server_branch"],
            "package_sha": meta["package_sha256"],
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evidence": "structure",
            "notes": (
                "\u6295\u5f71\u5b9a\u4f4d\u94fe\uff1abuff_data \u4f34\u8eab\u6295\u5f71\u7cfb\uff08sfx \u76ee\u5f55 "
                "effect/.../benshentouying\uff09\u3002\u7528\u6237\u5b9e\u673a\u951a\u70b9 3 \u56fe 27 \u540d 24 \u547d\u4e2d"
                "\uff1b\u661f\u6cb3\u6d41\u6d8c/\u65e0\u5c3d\u4e4b\u7d2b/\u661f\u793c\u661f\u613f \u5f85\u7eed\uff08buff \u6c60 0 \u547d\u4e2d\uff09\u3002"
                "\u6709\u9f99\u5219\u7075\u7cfb 4 \u53d8\u4f53 sfx \u540c\u76ee\u5f55\u6536\u5f55\u3002"
                "\u4ec5\u6587\u5b57/\u914d\u7f6e\u6765\u6e90\uff0c\u4e0d\u8868\u793a\u5f53\u524d\u53ef\u83b7\u5f97\u3002"
            ),
            "provenance": {
                "audit_status": "passed",
                "source_locks": [{
                    "sha256": meta["package_sha256"],
                    "bytes": meta["bytes"],
                    "mtime_ns": meta["mtime_ns"],
                    "path_hint": "Documents/script.py314.lc.npk",
                }],
                "source_id": source["source_id"],
                "base_entry": source_entries[0],
                "chs_entry": source_entries[1],
                "fid_lookup": True,
            },
        },
        "items": items,
        "stats": {
            "source_rows": len(rows),
            "unbound_rows": len(unbound),
            "catalog_entries": len(items),
        },
    }


def main() -> int:
    import argparse
    ROOT = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=ROOT / "data" / "live_sources.json")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "data" / "boards" / "fashion_projection_slots.json")
    args = parser.parse_args()
    board = build_board(args.registry)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    tmp = args.output.with_suffix(args.output.suffix + ".tmp")
    tmp.write_text(json.dumps(board, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(args.output)
    print(json.dumps({"items": len(board["items"]), "stats": board["stats"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
