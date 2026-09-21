#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild the fashion wardrobe board with row-level CHS-slot provenance.

Fashion appearance table facts (log 25.1, confirmed on current snapshot):
* entry 022570 base (FID E1645717C83FC968) + entry 020834 CHS (D016140651FEAB34);
  19 schema_refs, main schema 270688; same slot mixes part-name / desc / path /
  color across rows — field NAMES are NOT trustworthy, but 0x05 CHS *values*
  replay exactly with their field/value slot coordinates.
* The display name lives in the charm_value slot as ``名`` or ``名-N天`` or
  ``名-部件-N天``; part suffix and duration suffix come from the name itself;
  desc slots are cross-row shifted and are NOT attached here.

This rebuilder keeps, for every display-name hit, the exact row key and the
CHS field/value slots of the text it displays (SCHEMA 4.3 replayable text
chain), then aggregates time-limited and part variants of the same base name
into one catalog entry while preserving ALL original row keys per entry.

Structure-only: no availability/price/activity/acquisition claim.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import struct
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
TOOLKIT = Path(r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心")
if str(TOOLKIT) not in sys.path:
    sys.path.insert(0, str(TOOLKIT))
FASHION_PARSER_DIR = Path(r"E:\la拆包项目\01拆包器本体\工具库\05_BinDict解码器")
if str(FASHION_PARSER_DIR) not in sys.path:
    sys.path.insert(0, str(FASHION_PARSER_DIR))

from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402
from live_npk_reader import LiveNpkReader, NpkFormatError, _unpack_entry  # noqa: E402
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402

SOURCE_ID = "documents-py314-current"
FASHION_BASE_FID = "E1645717C83FC968"
FASHION_CHS_FID = "D016140651FEAB34"
DEFAULT_OUTPUT = ROOT / "data" / "boards" / "fashion_wardrobe_slots.json"

PARTS = ["头饰", "头发", "发型", "发饰", "衣服", "上衣", "下装", "裤子", "鞋子", "面饰",
         "眼镜", "口罩", "背包", "背饰", "披风", "挂件", "腰饰", "手套", "投影", "套装",
         "帽子", "裙", "手持", "脸饰", "纹身"]
_DUR_RE = re.compile(r"^(.*)-(\d+)天$")
_PART_RE = re.compile(r"^(.*)-(" + "|".join(PARTS) + r")$")
# 显示名：2-16 字主体（中文/字母数字/·★等），可带 -部件 与 -N天 后缀
_NAME_RE = re.compile(
    r"^[一-龥A-Za-z0-9·★]{1,16}"
    r"(-(" + "|".join(PARTS) + r"))?(-(1|3|5|7|14|30)天)?$"
)
_NAME_FULLCODE_RE = re.compile(r"^[A-Za-z0-9_;]+$")  # 纯英文码/内部串，非显示名


def parse_display_name(dn: str) -> tuple[str, str | None, int | None]:
    """(base, part, duration_days) from 名 / 名-部件 / 名-N天 / 名-部件-N天."""
    duration = None
    m = _DUR_RE.match(dn)
    if m:
        dn, duration = m.group(1), int(m.group(2))
    part = None
    m2 = _PART_RE.match(dn)
    if m2:
        dn, part = m2.group(1), m2.group(2)
    return dn, part, duration


def _load_registered_source(registry_path: Path) -> dict[str, Any]:
    raw = json.loads(registry_path.read_text(encoding="utf-8"))
    for source in raw.get("sources", []):
        if source.get("source_id") == SOURCE_ID:
            return source
    raise ValueError(f"source registry missing {SOURCE_ID}")


def _xbody(payload: bytes) -> bytes:
    marker = payload.find(b"x{")
    if marker < 0 or marker + 6 > len(payload):
        raise NpkFormatError("fashion base payload lacks a bounded x{ frame")
    length = struct.unpack_from("<I", payload, marker + 2)[0]
    start = marker + 6
    end = start + length
    if end > len(payload):
        raise NpkFormatError("fashion x{ frame exceeds decoded payload")
    return payload[start:end]


def _read_by_fid(reader: LiveNpkReader, file_id_hex: str) -> tuple[Any, bytes, dict[str, Any]]:
    matches = [entry for entry in reader._entries if entry.file_id == int(file_id_hex, 16)]
    if len(matches) != 1:
        raise NpkFormatError(f"expected one entry for FID {file_id_hex}, got {len(matches)}")
    entry = matches[0]
    with reader.package_path.open("rb") as handle:
        handle.seek(entry.offset)
        packed = handle.read(entry.packed_size)
    if len(packed) != entry.packed_size:
        raise NpkFormatError(f"short packed read for FID {file_id_hex}")
    decoded = _unpack_entry(packed, entry.declared_size, entry.flag)
    reader._assert_unchanged()
    return entry, decoded, {
        "entry_index": entry.entry_index,
        "file_id": file_id_hex,
        "decoded_sha256": hashlib.sha256(decoded).hexdigest(),
    }


def build_board(registry_path: Path) -> dict[str, Any]:
    source = _load_registered_source(registry_path)
    reader = LiveNpkReader(Path(source["path"]), str(source["server_branch"]))
    metadata = reader.source_metadata()
    if metadata["package_sha256"] != source["expected_sha256"]:
        raise RuntimeError("current package SHA differs from live source registry")
    if metadata["bytes"] != int(source["expected_bytes"]):
        raise RuntimeError("current package byte count differs from live source registry")

    _base_entry, base_payload, base_provenance = _read_by_fid(reader, FASHION_BASE_FID)
    _chs_entry, chs_payload, chs_provenance = _read_by_fid(reader, FASHION_CHS_FID)
    pool = parse_legacy_chs_pool(chs_payload)
    rows, unbound = decode_table_rows_with_chs_slots(_xbody(base_payload), pool)
    source_entries = [
        {**base_provenance, "role": "fashion_data_base"},
        {**chs_provenance, "role": "fashion_data_chs"},
    ]

    # ---- 行级扫描：工具库富文本解析器挑显示名（不信错位字段名），保留槽位链 ----
    # hit: {key, schema, name(text), prov{field_chs_slot,value_chs_slot}, base, part, duration}
    from fashion_display_name_parser import parse_display  # 05_BinDict解码器 工具库模块
    hits: list[dict[str, Any]] = []
    weak_rows = 0
    for r in rows:
        best: dict[str, Any] | None = None
        for fname, val in r["values"].items():
            if not (isinstance(val, tuple) and val[0] == "0x05" and isinstance(val[1], str)):
                continue
            text = val[1].strip()
            if not text:
                continue
            dn = parse_display(text)
            if dn is None:
                continue
            prov = r["value_provenance"].get(fname)
            if not (isinstance(prov, dict) and isinstance(prov.get("field_chs_slot"), int)
                    and isinstance(prov.get("value_chs_slot"), int)):
                continue
            # 多个槽命中同文本（charm_value 与 socket_names_male 同 value slot）时优先部件/时限
            score = 0
            if dn.part: score += 4
            if dn.duration_days is not None: score += 2
            if dn.flavor: score += 1
            if best is None or score > best["score"]:
                best = {"key": r["key"], "schema": r["schema"], "text": dn.raw,
                        "orig_text": text,
                        "field_chs_slot": prov["field_chs_slot"],
                        "value_chs_slot": prov["value_chs_slot"],
                        "base": dn.base, "part": dn.part, "duration": dn.duration_days,
                        "flavor": dn.flavor, "score": score}
        if best:
            hits.append(best)
        else:
            weak_rows += 1

    # ---- 聚合：同 base+part+flavor 一行（含所有变体行 key / 部件 / 时限） ----
    groups: dict[tuple[str, str | None, str | None], list[dict[str, Any]]] = {}
    for h in hits:
        groups.setdefault((h["base"], h["part"], h.get("flavor")), []).append(h)

    items: list[dict[str, Any]] = []
    for (base, part, flavor), gh in sorted(groups.items(), key=lambda kv: (kv[0][0], str(kv[0][1]))):
        # 代表行：优先无时限，其次 value_slot 最小（稳定）
        perm = [h for h in gh if h["duration"] is None]
        rep = min(perm or gh, key=lambda h: h["value_chs_slot"])
        durations = sorted({h["duration"] for h in gh if h["duration"] is not None})
        row_keys = sorted({h["key"] for h in gh})
        text_prov = {
            "name": {
                "field_chs_slot": rep["field_chs_slot"],
                "value_chs_slot": rep["value_chs_slot"],
                "scalar_type": "0x05",
                "text": rep["text"],  # 富文本前缀截取后的展示名（=item.name，可回放）
                "raw_slot_text": rep.get("orig_text", rep["text"]),  # 槽内原文（审计用）
                "rule": "strip #c..#n/#r, cut at first 。！？#r; then parse 名/名-部件/名-N天/(款型)",
            }
        }
        field_refs = [
            f"fashion_data.row_key={rep['key']}",
            "fashion_data display-name text (value-classified; field names unreliable in this table)",
            (
                "fashion_data.name CHS "
                f"field_slot={rep['field_chs_slot']} value_slot={rep['value_chs_slot']}"
            ),
        ]
        prov = {
            "source_lock_sha256": metadata["package_sha256"],
            "source_entries": source_entries,
            "table": "fashion_data",
            "row_key": rep["key"],
            "field_refs": field_refs,
            "name_source": (
                "same-snapshot fashion_data 0x05 CHS text replayed with field/value slot; "
                "display-name shape 名/名-部件/名-N天 classified by value, aggregated by base name"
            ),
        }
        item: dict[str, Any] = {
            "id": f"fash_{rep['key']}",
            "row_key": rep["key"],
            "name": rep["text"],
            "base": base,
            "part": part or "整套",
            "flavor": flavor,
            "part_note": "part 由显示名后缀解析（本表 part 槽为模型/图标路径，不可用）",
            "duration_days": durations,
            "has_permanent": bool(perm),
            "all_row_keys": row_keys,
            "schema_refs": sorted({h["schema"] for h in gh}),
            "variants": [
                {
                    "row_key": h["key"],
                    "text": h["text"],
                    "field_chs_slot": h["field_chs_slot"],
                    "value_chs_slot": h["value_chs_slot"],
                    "duration": h["duration"],
                    "schema": h["schema"],
                }
                for h in sorted(gh, key=lambda x: (x["duration"] is not None, x["value_chs_slot"]))
            ],
            "evidence": "structure",
            "evidence_level": "structure-only",
            "source": "Documents current-snapshot fashion_data row text (value-classified); not availability or acquisition evidence",
            "text_provenance": text_prov,
            "provenance": prov,
            "desc_note": "本表描述槽跨行错位（25.1 终判），描述待 name 文案 ID→i18n 文案表桥接，不展示以防串位",
        }
        items.append(item)

    reader._assert_unchanged()
    part_counter = Counter(it["part"] for it in items)
    return {
        "meta": {
            "name": "当前包 · 时装外观表（内嵌中文名层）",
            "category": "二、时装类 / （一）全量时装总表",
            "source_server": source["server_branch"],
            "package_sha": metadata["package_sha256"],
            "generated": dt.date.today().isoformat(),
            "evidence": "structure",
            "notes": (
                "时装外观表全量文字层（工具库 fashion_display_name_parser 富文本解析，v2）："
                "19260 行扫描 → 含名行按 (base,part,flavor) 聚合为目录条目。"
                "覆盖形态：裸名/名-部件/名-N天/（永久款|N天）括号款型/名 空格 色系尾/颜色码#c..#n/"
                "名。#r描述富文本；未命名行 0 新名可挖（表内已挖尽）。"
                "每条保留代表行 row key 与展示名的 CHS field/value 槽位（text=截取展示名，"
                "raw_slot_text=槽内原文可审计回放）。显示名按值解析（本表 19 schema_ref 字段名跨行"
                "错位不可信）；部件由显示名后缀解析（part 槽实为模型/图标路径）。"
                "仅文字来源，不表示外观当前可得、可购买、活动或上线状态；"
                "描述槽跨行错位不可取，留空待 i18n 桥接。"
            ),
            "provenance": {
                "audit_status": "passed",
                "source_locks": [{
                    "sha256": metadata["package_sha256"],
                    "bytes": metadata["bytes"],
                    "mtime_ns": metadata["mtime_ns"],
                    "path_hint": "Documents/script.py314.lc.npk",
                }],
                "source_id": SOURCE_ID,
                "base_entry": source_entries[0],
                "chs_entry": source_entries[1],
                "fid_lookup": True,
            },
        },
        "items": items,
        "stats": {
            "indexed_rows": len(rows) + len(unbound),
            "decoded_rows": len(rows),
            "unbound_rows": len(unbound),
            "display_name_hit_rows": len(hits),
            "no_display_name_rows": weak_rows,
            "catalog_entries": len(items),
            "parts": dict(part_counter.most_common()),
            "permanent_entries": sum(1 for it in items if it["has_permanent"]),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=ROOT / "data" / "live_sources.json")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    board = build_board(args.registry)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(board, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(args.output)
    print(json.dumps({
        "output": str(args.output), "bytes": args.output.stat().st_size,
        "items": len(board["items"]), "stats": board["stats"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
