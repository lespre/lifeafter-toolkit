#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild anonymous all_equips -> schema6109 attribute relations from BA8.

The output is structural evidence only.  It retains the raw parent row key and
attrs-object offset, but intentionally does not infer an item/weapon name or a
combat-damage formula from this configuration relation.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from live_npk_reader import LiveNpkReader, NpkFormatError, _unpack_entry  # noqa: E402

SOURCE_REGISTRY = ROOT / "data" / "live_sources.json"
DEFAULT_OUTPUT = ROOT / "data" / "boards" / "weapon_attrs_schema_static.json"
SOURCE_PARSER = Path(r"E:\la拆包项目\01拆包器本体\工具库\05_BinDict解码器\weapon_attrs_table.py")
BASE_FID = "A130A31532FAF63C"
CHS_FID = "94AB0B3FD057EF01"
ATTRS_SCHEMA = 6109
PARENT_SCHEMA = 164051


def load_registered_source() -> dict[str, Any]:
    raw = json.loads(SOURCE_REGISTRY.read_text(encoding="utf-8"))
    source = next((item for item in raw.get("sources", []) if item.get("source_id") == "documents-py314-current"), None)
    if not isinstance(source, dict):
        raise ValueError("documents-py314-current source is not registered")
    return source


def load_parser_module():
    if not SOURCE_PARSER.is_file():
        raise FileNotFoundError(SOURCE_PARSER)
    spec = importlib.util.spec_from_file_location("weapon_attrs_codec", SOURCE_PARSER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load codec: {SOURCE_PARSER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def xbody(payload: bytes) -> bytes:
    offset = payload.find(b"x{")
    if offset < 0 or offset + 6 > len(payload):
        raise NpkFormatError("expected x{ BinDict container not found")
    size = int.from_bytes(payload[offset + 2:offset + 6], "little")
    end = offset + 6 + size
    if end > len(payload):
        raise NpkFormatError("BinDict body exceeds decoded payload")
    return payload[offset + 6:end]


# 人工映射：name 槽=长文本（desc 首句点名）的 10 行——desc-first 提取（2026-09-04 人工审 41 行长文清单后定案）
DESC_FIRST = {
    "10002": "生产台", "10211": "生产台",
    "10063": "AWP狙击步枪", "10301": "UZI冲锋枪",
    "10531": "光盾无人机", "10627": "蝶影双枪", "10647": "雷明顿霰弹枪",
    "10695": "KSG霰弹枪", "10730": "G3式自动步枪", "10938": "仿生菌焰喷火器",
    # 2026-09-04 匿名行二轮：desc 首句点名可安全提取（载具/联动外观/玩具）
    "10701": "极速之神", "10808": "极速之神", "11015": "极速之神",
    "10880": "奶龙", "10433": "红色气球",
}
# 含点号/标点但人工确认为名的短文本（型号名）
PUNCT_NAMES = {"10210": "Mark.06"}
# 短名但实为限用句（非名）：保持占位
NOT_NAME = {"10059", "10639", "10465"}


def type_hint_for(row_key: int, raw: str) -> str:
    """匿名行类型标注（非武器行/特殊行）——让读者理解为什么没名字。"""
    if raw.startswith("animator/"):
        return "飞行器（路径名行，非武器）"
    if row_key in (10580, 10581, 10589):
        return "护盾道具行"
    if row_key in (10221, 10282, 10546, 10611, 10836, 10882):
        return "营地工具/杂物行"
    if row_key in (10059, 10639, 10465):
        return "限用/补给句行"
    if row_key in (10440, 10441, 10743):
        return "武器本体（desc 未点名短名）"
    if row_key in (10027, 10079, 10088, 10434, 10435, 10436, 10579):
        return "时装/挂件/载具外观（诗体 desc 行）"
    return ""


def classify_name(row_key: int, raw: str):
    """回填三档：name-slot 直读 / desc-first 人工映射 / 占位。
    raw=name 槽原文（槽=短名时为名；槽=长文本时可能是 desc 首句点名）。"""
    import re
    rk = str(row_key)
    if rk in NOT_NAME:
        return None, "unresolved"
    if rk in DESC_FIRST:
        return DESC_FIRST[rk], "desc-first-map"
    if rk in PUNCT_NAMES:
        return PUNCT_NAMES[rk], "name-slot"
    has_punct = bool(re.search(r"[，。：、；（）().,/#]", raw))
    if raw and not has_punct and len(raw) <= 14 and not raw.startswith("animator"):
        return raw, "name-slot"
    return None, "unresolved"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    registered = load_registered_source()
    package = Path(registered["path"])
    reader = LiveNpkReader(package, str(registered.get("server_branch") or "Documents snapshot"))
    source = reader.source_metadata()
    if source["package_sha256"] != registered.get("expected_sha256"):
        raise RuntimeError("registered source SHA mismatch; refuse to rebuild from a changed package")
    if source["bytes"] != registered.get("expected_bytes"):
        raise RuntimeError("registered source byte-size mismatch; refuse to rebuild from a changed package")

    entries_by_fid = {f"{entry.file_id:016X}": entry for entry in reader._entries}

    def decode(fid: str, role: str) -> tuple[bytes, dict[str, Any]]:
        entry = entries_by_fid.get(fid)
        if entry is None:
            raise RuntimeError(f"required FID missing from locked source: {fid}")
        with package.open("rb") as handle:
            handle.seek(entry.offset)
            packed = handle.read(entry.packed_size)
        if len(packed) != entry.packed_size:
            raise RuntimeError(f"short packed read for FID {fid}")
        payload = _unpack_entry(packed, entry.declared_size, entry.flag)
        reader._assert_unchanged()
        return payload, {
            "entry_index": entry.entry_index,
            "file_id": fid,
            "decoded_sha256": hashlib.sha256(payload).hexdigest(),
            "role": role,
        }

    base_payload, base_entry = decode(BASE_FID, "all_equips_base")
    chs_payload, chs_entry = decode(CHS_FID, "all_equips_chs")
    codec = load_parser_module()
    slots = codec.strings(xbody(chs_payload))
    blob, _de, key_starts = codec.base_blob(xbody(base_payload))
    field_count, _bits, fields, _ = codec.schema_at(blob, slots, ATTRS_SCHEMA)
    if not (
        field_count == 55
        and fields[23].get("name") == "hurt"
        and fields[35].get("name") == "power"
    ):
        raise RuntimeError("schema6109 field layout changed; do not reuse position 23/35")

    records: list[dict[str, Any]] = []
    for row_key, start in sorted(key_starts.items()):
        if blob[start] != 0xD6:
            continue
        try:
            cursor = start + 1
            parent_schema, cursor = codec.uleb(blob, cursor, len(blob))
            bitmap_ref, cursor = codec.uleb(blob, cursor, len(blob))
            if parent_schema != PARENT_SCHEMA:
                continue
            _parent_count, parent_bits, parent_fields, _ = codec.schema_at(blob, slots, parent_schema)
            bitmap = blob[bitmap_ref:bitmap_ref + (parent_bits + 7) // 8]
            used_fields = [
                field for field in parent_fields
                if field["i"] >= parent_bits or bitmap[field["i"] // 8] & (1 << (field["i"] % 8))
            ]
            attrs_offsets: list[int] = []
            name_raw = ""
            for field in used_fields:
                value, cursor = codec.read_val(blob, field["t"], cursor, slots)
                if field["t"] == 11 and field.get("name") == "attrs":
                    attrs_offsets.append(value)
                elif field.get("name") == "name":
                    name_raw = value[1] if isinstance(value, tuple) and len(value) > 1 else (value if isinstance(value, str) else "")
            for attrs_offset in attrs_offsets:
                attrs = codec.attrs_obj(blob, slots, attrs_offset)
                if not attrs or "hurt" not in attrs:
                    continue
                records.append({
                    "row_key": row_key,
                    "attrs_offset": attrs_offset,
                    "name_raw": name_raw,
                    "schema6109_field23_hurt": attrs["hurt"],
                    "schema6109_field35_power": attrs.get("power"),
                })
        except (IndexError, KeyError, ValueError, NpkFormatError):
            continue

    row_keys = [record["row_key"] for record in records]
    if len(row_keys) != len(set(row_keys)):
        raise RuntimeError("a parent all_equips row resolved to multiple attrs objects; split relation before publication")
    if not records:
        raise RuntimeError("no schema6109 relations decoded from locked source")

    lock = {
        "sha256": source["package_sha256"],
        "bytes": source["bytes"],
        "mtime_ns": source["mtime_ns"],
        "path_hint": "Documents/script.py314.lc.npk",
    }
    source_entries = [base_entry, chs_entry]
    items = []
    for record in records:
        row_key = record["row_key"]
        clean_name, name_evidence = classify_name(row_key, record["name_raw"])
        if clean_name is None:
            item_name = f"未回填（all_equips key={row_key}）"
        else:
            item_name = clean_name
        items.append({
            "id": str(row_key),
            "row_key": row_key,
            "attrs_offset": record["attrs_offset"],
            "name": item_name,
            "name_raw": record["name_raw"][:200],
            "name_evidence": name_evidence,
            "type_hint": type_hint_for(row_key, record["name_raw"]),
            "evidence": "structure",
            "evidence_level": "structure-only",
            "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
            "schema6109_field23_hurt": record["schema6109_field23_hurt"],
            "schema6109_field35_power": record["schema6109_field35_power"],
            "provenance": {
                "source_lock_sha256": source["package_sha256"],
                "source_entries": source_entries,
                "table": "all_equips_data → attrs(schema6109)",
                "row_key": row_key,
                "field_refs": [
                    f"all_equips_data.key={row_key}",
                    f"all_equips_data.attrs → absolute_blob_offset={record['attrs_offset']}",
                    "schema6109.field[23]=hurt",
                    "schema6109.field[35]=power",
                ],
                "name_source": {
                    "name-slot": "parent row name slot raw short text (no punctuation, ≤14 chars, non-path)",
                    "desc-first-map": "parent row name slot held long desc text; name taken from its first sentence via human-reviewed map",
                    "unresolved": "name slot text is a description/path/poem or usage sentence; kept anonymous",
                }.get(name_evidence, name_evidence),
            },
        })

    board = {
        "meta": {
            "name": "all_equips → schema 6109 原始属性关系",
            "category": "三、战力类 / （一）武器",
            "source_server": "体验服 Documents BA8A239A 快照",
            "package_sha": source["package_sha256"],
            "generated": dt.date.today().isoformat(),
            "evidence": "structure",
            "notes": (
                "每项是当前同包 all_equips 的原始 row key 到 attrs 对象的关系，保留 attrs 绝对 offset 与 schema6109 的第 23/35 字段原值。"
                "schema 字符串标签为 hurt/power；此处不把它们扩展为业务公式、数值比较、装备归属或显示名称。"
                "名称回填（2026-09-04）：name 槽=无标点短文本的 154 行直读为名（name-slot）；name 槽=长描述且首句点名的 15 行经人工清单提取"
                "（desc-first-map：生产台/AWP狙击步枪/UZI冲锋枪/光盾无人机/蝶影双枪/雷明顿霰弹枪/KSG霰弹枪/G3式自动步枪/仿生菌焰喷火器，及极速之神/奶龙/红色气球）；"
                "其余 27 行 name 槽为诗句/路径/限用句或非点名描述，保持匿名占位（name_raw 原样可见）；"
                "all_equips 的 row_key/id 不与 common_item item_id 做跨表同号回填。"
            ),
            "provenance": {"audit_status": "passed", "source_locks": [lock]},
        },
        "items": items,
    }
    reader._assert_unchanged()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(board, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(args.output)
    print(f"wrote {args.output} items={len(items)} source_sha={source['package_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
