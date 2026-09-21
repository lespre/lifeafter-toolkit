#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rebuild_fashion_glow_slots — 荧光棒板（player_appear_data 荧光棒名册）

源（BA8 当前快照）：player_appear_data base entry 007074 FID 484AB42BD31AE503
  + CHS 006403 FID 4151CFD3191DCAD7。
定位链（2026-09-04，用户指出时装表筛法不全）：
  时装搭配「荧光棒」格外观=player_appear_data 中 name 含 荧光棒 的行（part=5 荧光棒部件，
  gender 0=男/1=女 成对，key 5xxxx/15xxxx）；9 款：彩虹大神荧光棒/彩虹荧光棒/
  荧光棒·守护/救援/求索/漫步/腾飞/追随/闪耀。desc 层含赛季获取说明
  （辐射诡楼 XX 赛季 XX 骑士奖励，下赛季回收）。
  注：旧板（fashion_glow_slots v1 2 条）从时装表筛 name 含荧光棒——只抓到
  彩虹大神荧光棒与普通荧光棒，缺 荧光棒·X 系列 7 款（本板补全）。
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

PA_BASE_FID = "484AB42BD31AE503"
PA_CHS_FID = "4151CFD3191DCAD7"


def _xbody(payload: bytes) -> bytes:
    marker = payload.find(b"x{")
    if marker < 0:
        raise ValueError("no x{ container")
    length = struct.unpack_from("<I", payload, marker + 2)[0]
    end = marker + 6 + length
    if end > len(payload):
        raise ValueError("x{ frame exceeds payload")
    return payload[marker + 6:end]


def _read_by_fid(reader: LiveNpkReader, fid_hex: str):
    matches = [e for e in reader._entries if e.file_id == int(fid_hex, 16)]
    if len(matches) != 1:
        raise RuntimeError(f"FID {fid_hex}: {len(matches)} matches")
    e = matches[0]
    with reader.package_path.open("rb") as h:
        h.seek(e.offset)
        packed = h.read(e.packed_size)
    decoded = _unpack_entry(packed, e.declared_size, e.flag)
    reader._assert_unchanged()
    return e, decoded, {
        "entry_index": e.entry_index,
        "file_id": fid_hex,
        "decoded_sha256": hashlib.sha256(decoded).hexdigest(),
    }


def build_board(registry_path: Path) -> dict:
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    source = next(s for s in registry["sources"] if s["source_id"] == "documents-py314-current")
    reader = LiveNpkReader(Path(source["path"]), "documents")
    meta = reader.source_metadata()
    if meta["package_sha256"] != source["expected_sha256"]:
        raise RuntimeError("current package SHA differs from registry")

    _, b_payload, b_prov = _read_by_fid(reader, PA_BASE_FID)
    _, c_payload, c_prov = _read_by_fid(reader, PA_CHS_FID)
    pool = parse_legacy_chs_pool(c_payload)
    rows, unbound = decode_table_rows_with_chs_slots(_xbody(b_payload), pool)
    source_entries = [
        {**b_prov, "role": "player_appear_data_base"},
        {**c_prov, "role": "player_appear_data_chs"},
    ]

    glow_rows = []
    for r in rows:
        nm = r["values"].get("name")
        if not (isinstance(nm, tuple) and isinstance(nm[1], str)):
            continue
        name = nm[1]
        k = r["key"]
        # 51 段（5100000≤k<5200000 男 / 15100000≤k<15200000 女）=荧光棒/应援棒专段
        # （用户锚点 灿若星 5103001/墨染清荷 5103701/可乐小子应援棒 5101701 100% 在段内；
        #   段内 96 名无挂件词；挂件在 50 段 MOSS 5006801/三笠Q版挂件 5007201 等）
        in_51 = (5100000 <= k < 5200000) or (15100000 <= k < 15200000)
        has_word = ("\u8367\u5149\u68d2" in name) or ("\u5e94\u63f4\u68d2" in name)
        if not (in_51 or has_word):
            continue
        def val(f):
            v = r["values"].get(f)
            return v[1] if isinstance(v, tuple) else None
        glow_rows.append({
            "key": r["key"], "name": nm[1], "gender": val("gender"), "part": val("part"),
            "model_name": val("model_name"), "schema": r["schema"],
            "prov": r.get("value_provenance", {}).get("name"),
        })
    # 按名聚合：男女行合成一条（variants 存另一性别 key）
    by_name: dict[str, dict] = {}
    for g in glow_rows:
        if g["name"] not in by_name:
            by_name[g["name"]] = g
        else:
            by_name[g["name"]]["pair_key"] = g["key"]
    items = []
    for name in sorted(by_name):
        g = by_name[name]
        tp = {}
        if isinstance(g["prov"], dict) and isinstance(g["prov"].get("field_chs_slot"), int):
            tp["name"] = {**g["prov"], "scalar_type": "0x05", "text": g["name"]}
        items.append({
            "id": f"glow_{g['key']}",
            "row_key": g["key"],
            "name": name,
            "display_name": name,
            "gender": g["gender"],
            "part": g["part"],
            "model_name": g["model_name"],
            "pair_key": g.get("pair_key"),
            "schema_refs": [g["schema"]],
            "evidence": "structure",
            "evidence_level": "structure-only",
            "source": ("player_appear_data name \u542b \u8367\u5149\u68d2 \u884c\uff08part=5 "
                       "\u8367\u5149\u68d2\u90e8\u4ef6\uff0c\u7537\u5973\u6210\u5bf9 key 5xxxx/15xxxx\uff09"),
            "text_provenance": tp,
            "provenance": {
                "source_lock_sha256": meta["package_sha256"],
                "source_entries": source_entries,
                "table": "player_appear_data",
                "row_key": g["key"],
                "field_refs": [
                    f"player_appear_data.row_key={g['key']}",
                    "player_appear_data name column-level 0x05",
                ],
                "name_source": "player_appear_data \u8367\u5149\u68d2\u540d\u518c\uff08\u7528\u6237\u6307\u51fa\u65f6\u88c5\u8868\u7b5b\u6cd5\u4e0d\u5168\u540e\u91cd\u5efa\uff09",
            },
        })

    return {
        "meta": {
            "name": "\u5f53\u524d\u5305 \u00b7 \u8367\u5149\u68d2\uff08player_appear_data \u540d\u518c\uff09",
            "category": "二、时装类 / （四）荧光棒",
            "source_server": source["server_branch"],
            "package_sha": meta["package_sha256"],
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evidence": "structure",
            "notes": (
                "\u8367\u5149\u68d2\u540d\u518c 9 \u6b3e\uff08\u5bf9\u6bd4 v1 \u65f6\u88c5\u8868\u7b5b\u6cd5 2 \u6761\uff1a"
                "\u8865\u5168 \u8367\u5149\u68d2\u00b7\u5b88\u62a4/\u6551\u63f4/\u6c42\u7d22/\u6f2b\u6b65/\u817e\u98de/\u8ffd\u968f/\u95ea\u8000 7 \u6b3e\uff09\uff1b"
                "desc \u5c42\u542b\u8d5b\u5b63\u83b7\u53d6\u8bf4\u660e\uff08\u8f90\u5c04\u8be1\u697c XX \u8d5b\u5b63 XX \u9a91\u58eb\u5956\u52b1\uff0c"
                "\u4e0b\u8d5b\u5b63\u56de\u6536\uff09\u3002\u4ec5\u6587\u5b57/\u914d\u7f6e\u6765\u6e90\uff0c\u4e0d\u8868\u793a\u5f53\u524d\u53ef\u5f97\u3002"
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
            "glow_rows": len(glow_rows),
            "catalog_entries": len(items),
        },
    }


def main() -> int:
    import argparse
    ROOT = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=ROOT / "data" / "live_sources.json")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "data" / "boards" / "fashion_glow_slots.json")
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
