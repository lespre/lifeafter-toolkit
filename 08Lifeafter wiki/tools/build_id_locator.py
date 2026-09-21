# -*- coding: utf-8 -*-
"""P1-9：标识 → 出现位置 定位索引构建器（基于 file_index_entries.jsonl）。

- NPK/script：标识 = file_id（16 hex）
- GPK：标识 = c1c2 指纹对（f"{c1:08x}{c2:08x}"）
- IDX：标识 = hash16（内容 MD5）
- FPK：帧无内容级标识（未存 payload hash），按 (client, package, frame_index/offset) 定位；
  identifier 列为 NULL 并单独可查。

SQLite 表 locations：kind/client_channel/package/identifier_type/identifier/
  entry_index/offset/packed_size/decoded_size/flag/storage/name_known。
输出：data/id_locator_index.db（只读查询库）+ data/id_locator_audit.json（覆盖率/重复/冲突统计）。
重复与冲突只记录关系（同标识多处出现 / 同标识不同 decoded_size），不做业务解释。
"""
from __future__ import annotations

import json
import sqlite3
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRIES = ROOT / "data" / "file_index_entries.jsonl"
DB = ROOT / "data" / "id_locator_index.db"
AUDIT = ROOT / "data" / "id_locator_audit.json"

SCHEMA = """
CREATE TABLE IF NOT EXISTS locations (
  kind TEXT NOT NULL,
  client_channel TEXT NOT NULL,
  package TEXT NOT NULL,
  identifier_type TEXT,
  identifier TEXT,
  entry_index INTEGER,
  offset INTEGER,
  packed_size INTEGER,
  decoded_size INTEGER,
  flag TEXT,
  storage TEXT,
  name_known INTEGER,
  pkg INTEGER
);
CREATE INDEX IF NOT EXISTS idx_identifier ON locations (identifier_type, identifier);
CREATE INDEX IF NOT EXISTS idx_package ON locations (client_channel, package);
CREATE INDEX IF NOT EXISTS idx_frame ON locations (kind, client_channel, package, entry_index);
"""


def main() -> int:
    started = time.time()
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    con.execute("PRAGMA journal_mode=OFF")
    con.execute("PRAGMA synchronous=OFF")
    con.executescript(SCHEMA)
    con.execute("BEGIN")

    counts = Counter()
    identifier_keys: Counter = Counter()  # (type, id) 出现次数
    size_by_ident: dict = {}  # (type, id) -> set(decoded_size)
    n = 0
    batch = []
    with ENTRIES.open(encoding="utf-8") as f:
        for ln in f:
            if not ln.strip():
                continue
            e = json.loads(ln)
            kind = e["kind"]
            idt = None
            ident = None
            if kind in ("容器(script)", "容器(npk)"):
                idt, ident = "fid", e["file_id"]
                dec = e.get("decoded_size")
                off = e.get("offset")
            elif kind == "gpk":
                idt, ident = "c1c2", f"{e['c1']:08x}{e['c2']:08x}"
                dec = e.get("decoded_size")
                off = e.get("offset")
            elif kind == "idx":
                idt, ident = "hash16", e["hash16"]
                dec = None
                off = e.get("offset")
                pkg_no = e.get("pkg")
            elif kind == "fpk":
                idt, ident = None, None
                dec = e.get("decoded_size")
                off = e.get("frame_offset")
            row = (
                kind, e["client_channel"], e["package"], idt, ident,
                e.get("entry_index"), off, e.get("packed_size"), dec,
                e.get("flag") if "flag" in e else None,
                e.get("storage"), 1 if e.get("name_known") else 0,
                pkg_no if idt == "hash16" else None,
            )
            batch.append(row)
            counts[kind] += 1
            if idt:
                key = (idt, ident)
                identifier_keys[key] += 1
                if dec is not None:
                    size_by_ident.setdefault(key, set()).add(dec)
            n += 1
            if n % 500_000 == 0:
                con.executemany("INSERT INTO locations VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                batch)
                batch = []
                con.commit()
                print(f"  ...{n:,} rows, {time.time()-started:.0f}s", flush=True)
    if batch:
        con.executemany("INSERT INTO locations VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        batch)
    con.commit()

    # 统计
    dup_keys = {k: c for k, c in identifier_keys.items() if c > 1}
    conflict_keys = {k: sizes for k, sizes in size_by_ident.items()
                     if len(sizes) > 1}
    audit = {
        "schema_version": 1,
        "total_rows": n,
        "rows_with_identifier": sum(identifier_keys.values()),
        "unique_identifiers": len(identifier_keys),
        "duplicate_identifier_keys": len(dup_keys),
        "duplicate_key_occurrences": sum(dup_keys.values()),
        "conflict_keys_same_ident_diff_size": len(conflict_keys),
        "conflict_samples": list(conflict_keys)[:10],
        "rows_by_kind": dict(counts),
        "note": "重复=同标识多位置（Documents/root 覆盖、内容去重等），冲突=同标识不同解码大小；"
                "只记录关系，不解释业务含义",
        "build_seconds": round(time.time() - started, 1),
    }
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=1),
                     encoding="utf-8")
    con.close()
    print(json.dumps(audit, ensure_ascii=False, indent=1))
    print("db ->", DB)
    return 0


if __name__ == "__main__":
    sys.exit(main())
