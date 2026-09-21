#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""all_equips base/CHS 自定位解析器（FID 内容派生、随热更漂移时的兜底）。

为什么需要：FID 是内容派生的，热更后 base/CHS 的 FID 会变（2026-09-10 包中
A130A31532FAF63C / 94AB0B3FD057EF01 双双消失）。写死 FID 的工具会拒绝重建。

方法（结构优先，不猜内容）：
1. 扫包，对每个 payload（>200KB）做 `xbody()` →
   - **base-like**：`base_blob()` 成功且行数 > 500（大行表）
   - **chs-like**：`strings()` 成功且字符串数 > 2000（文本池）
2. 对每个 (base, chs) 组合跑 codec 的 schema6109 校验（field_count==55 且
   fields[23]=='hurt' / fields[35]=='power'），并统计解出的关系条数；
3. 命中的组合写入缓存 `data/audit/all_equips_pair_cache.json`（含源包 sha，
   换包即失效），供 rebuild_weapon_attrs_schema_static.py 复用。

只报候选+校验结果，不自动认领：命中必须同时满足 schema 布局与关系条数下界。
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(r"E:\la拆包项目\08Lifeafter wiki")
sys.path.insert(0, str(ROOT / "tools"))
from live_npk_reader import LiveNpkReader, NpkFormatError, _unpack_entry  # noqa: E402

CODEC = Path(r"E:\la拆包项目\01拆包器本体\工具库\05_BinDict解码器\weapon_attrs_table.py")
CACHE = ROOT / "data" / "audit" / "all_equips_pair_cache.json"
MIN_SIZE = 200_000
MIN_BASE_ROWS = 500
MIN_CHS_STRINGS = 2000
PARENT_SCHEMA = 164051
ATTRS_SCHEMA = 6109
MIN_RELATIONS = 50


def load_codec():
    spec = importlib.util.spec_from_file_location("weapon_attrs_codec", CODEC)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load codec: {CODEC}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def registered_source() -> dict[str, Any]:
    raw = json.loads((ROOT / "data" / "live_sources.json").read_text(encoding="utf-8"))
    src = next((s for s in raw.get("sources", []) if s.get("source_id") == "documents-py314-current"), None)
    if not isinstance(src, dict):
        raise ValueError("documents-py314-current is not registered")
    return src


def scan(codec) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    src = registered_source()
    package = Path(src["path"])
    reader = LiveNpkReader(package, str(src.get("server_branch") or "Documents snapshot"))
    bases: list[dict[str, Any]] = []
    chs: list[dict[str, Any]] = []
    with package.open("rb") as handle:
        for entry in reader._read_index_locked():
            if entry.declared_size < MIN_SIZE:
                continue
            handle.seek(entry.offset)
            packed = handle.read(entry.packed_size)
            try:
                payload = _unpack_entry(packed, entry.declared_size, entry.flag)
                body = codec_body(codec, payload)
            except Exception:
                continue
            fid = f"{entry.file_id:016X}"
            try:
                blob, _de, key_starts = codec.base_blob(body)
                if len(key_starts) >= MIN_BASE_ROWS:
                    bases.append({"fid": fid, "entry_index": entry.entry_index,
                                  "size": len(payload), "rows": len(key_starts),
                                  "blob_len": len(blob), "sha256": hashlib.sha256(payload).hexdigest()})
                    continue
            except Exception:
                pass
            try:
                slots = codec.strings(body)
                if len(slots) >= MIN_CHS_STRINGS:
                    cjk = sum(1 for s in slots if any("\u4e00" <= ch <= "\u9fff" for ch in s))
                    chs.append({"fid": fid, "entry_index": entry.entry_index, "size": len(payload),
                                "strings": len(slots), "cjk_strings": cjk,
                                "sha256": hashlib.sha256(payload).hexdigest()})
            except Exception:
                continue
    return bases, chs


def codec_body(codec, payload: bytes) -> bytes:
    """复用工具侧的 xbody 口径（找 x{ 容器）。"""
    offset = payload.find(b"x{")
    if offset < 0 or offset + 6 > len(payload):
        raise NpkFormatError("expected x{ BinDict container not found")
    size = int.from_bytes(payload[offset + 2:offset + 6], "little")
    end = offset + 6 + size
    if end > len(payload):
        raise NpkFormatError("BinDict body exceeds decoded payload")
    return payload[offset + 6:end]


def validate_pair(codec, base: dict[str, Any], chs: dict[str, Any]) -> dict[str, Any] | None:
    """用 codec 侧函数在内存里跑一遍工具主流程，返回统计或 None。"""
    src = registered_source()
    package = Path(src["path"])
    reader = LiveNpkReader(package, str(src.get("server_branch") or "Documents snapshot"))
    by_fid = {f"{e.file_id:016X}": e for e in reader._read_index_locked()}

    def payload_of(fid: str) -> bytes:
        entry = by_fid[fid]
        with package.open("rb") as handle:
            handle.seek(entry.offset)
            return _unpack_entry(handle.read(entry.packed_size), entry.declared_size, entry.flag)

    base_body = codec_body(codec, payload_of(base["fid"]))
    chs_body = codec_body(codec, payload_of(chs["fid"]))
    try:
        slots = codec.strings(chs_body)
        blob, _de, key_starts = codec.base_blob(base_body)
        count, _bits, fields, _ = codec.schema_at(blob, slots, ATTRS_SCHEMA)
    except Exception as exc:  # noqa: BLE001
        return None
    if count != 55 or fields[23].get("name") != "hurt" or fields[35].get("name") != "power":
        return None
    records = 0
    for row_key, start in sorted(key_starts.items()):
        if start >= len(blob) or blob[start] != 0xD6:
            continue
        try:
            cursor = start + 1
            parent_schema, cursor = codec.uleb(blob, cursor, len(blob))
            bitmap_ref, cursor = codec.uleb(blob, cursor, len(blob))
            if parent_schema != PARENT_SCHEMA:
                continue
            _pc, parent_bits, parent_fields, _ = codec.schema_at(blob, slots, parent_schema)
            bitmap = blob[bitmap_ref:bitmap_ref + (parent_bits + 7) // 8]
            used = [f for f in parent_fields
                    if f["i"] >= parent_bits or bitmap[f["i"] // 8] & (1 << (f["i"] % 8))]
            attrs_offsets = []
            for field in used:
                value, cursor = codec.read_val(blob, field["t"], cursor, slots)
                if field["t"] == 11 and field.get("name") == "attrs":
                    attrs_offsets.append(value)
            for offset in attrs_offsets:
                attrs = codec.attrs_obj(blob, slots, offset)
                if attrs and "hurt" in attrs:
                    records += 1
        except Exception:
            continue
    if records < MIN_RELATIONS:
        return None
    return {"records": records, "schema_fields": count, "base_rows": len(key_starts)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-cache", action="store_true")
    args = parser.parse_args(argv)
    codec = load_codec()
    src = registered_source()
    bases, chs = scan(codec)
    print(f"base-like 候选 {len(bases)} | chs-like 候选 {len(chs)}")
    for b in sorted(bases, key=lambda x: -x["rows"])[:8]:
        print(f"  base? fid={b['fid']} entry={b['entry_index']} rows={b['rows']} size={b['size']}")
    for c in sorted(chs, key=lambda x: -x["cjk_strings"])[:8]:
        print(f"  chs?  fid={c['fid']} entry={c['entry_index']} strings={c['strings']} cjk={c['cjk_strings']} size={c['size']}")
    hits: list[dict[str, Any]] = []
    for base in bases:
        for c in chs:
            result = validate_pair(codec, base, c)
            if result:
                hits.append({"base": base, "chs": c, **result})
                print(f"✅ base={base['fid']} chs={c['fid']} records={result['records']} rows={result['base_rows']}")
    if args.write_cache and hits:
        best = max(hits, key=lambda h: h["records"])
        cache = {
            "schema": "all_equips_pair_cache/v1",
            "package_sha256": src.get("expected_sha256"),
            "package_bytes": src.get("expected_bytes"),
            "base": best["base"],
            "chs": best["chs"],
            "records": best["records"],
            "candidates": len(hits),
            "note": "结构校验（xbody+base_blob+strings+schema6109 布局 + 关系条数下界）命中；换包即失效需重跑。",
        }
        CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
        print("缓存写入", CACHE, "→", best["base"]["fid"], best["chs"]["fid"])
    print("命中组合数:", len(hits))
    return 0


if __name__ == "__main__":
    sys.exit(main())
