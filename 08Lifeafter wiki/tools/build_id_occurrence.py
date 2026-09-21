# -*- coding: utf-8 -*-
"""P1-13：数字 ID 出现位置索引（复用 P1-12 row_index 定位与解码器行语义）。

每行值流按 schema 顺序解码（pool=[] 安全占位：字段名不解=只记 field_slot），
抽整数型槽（ULEB 0x01/0x04、ZIGZAG 0x11）为 ID 出现；BOOL/JUMP/文本 CHS/
浮点槽不抽（JUMP=内部引用、F32/F64=数值属性、CHS=文本——非数字 ID 语义）。
0x27 内联组元素同为 ID 候选（field_slot=宿主槽，group_index/element_index 定位）。
0x36 mapping 行键值抽整数型（field_slot=None + marker 区分）。

只记录出现位置，不解释业务含义；同 ID 跨表出现不建业务关系；
server_branch=unresolved。

输出：data/id_occurrence_index.db（SQLite）+ data/id_occurrence_summary.json
"""
from __future__ import annotations

import json
import sqlite3
import struct
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRIES_DIR = Path(r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_BA8A239A\entries")
DB = ROOT / "data" / "id_locator_index.db"
TABLE_ENTRIES = ROOT / "data" / "table_index_entries.jsonl"
OUT_DB = ROOT / "data" / "id_occurrence_index.db"
OUT_SUM = ROOT / "data" / "id_occurrence_summary.json"
SNAPSHOT = "test-328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f"
TOOLKIT = r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心"
TOOLS = str(Path(__file__).resolve().parent)

INT_TYPES = {0x01, 0x04, 0x11}  # ULEB / ULEB_ALT / ZIGZAG
CHS_TYPE = 0x05


def xbody(data: bytes):
    pos = 0
    while True:
        at = data.find(b"x{", pos)
        if at < 0:
            return None, None
        if at + 6 <= len(data):
            n = int.from_bytes(data[at + 2:at + 6], "little")
            if 0 < n <= len(data) - at - 6:
                cnt = int.from_bytes(data[at + 6:at + 10], "little")
                res = int.from_bytes(data[at + 10:at + 14], "little")
                if res == 0 and cnt <= 300000:
                    return at, n
        pos = at + 3


def _scan_table(args: tuple) -> dict:
    entry, fn, table_name, fid = args
    data = (ENTRIES_DIR / fn).read_bytes()
    at, xl = xbody(data)
    if at is None:
        return {"entry": entry, "error": "no_x", "hits": []}
    body = data[at + 6:at + 6 + xl]
    if len(body) < 12:
        return {"entry": entry, "error": "short_body", "hits": []}
    cnt = int.from_bytes(body[0:4], "little")
    res = int.from_bytes(body[4:8], "little")
    te = 8 + 4 * cnt
    if res != 0 or te > len(body):
        return {"entry": entry, "error": "bad_header", "hits": []}
    blob = body[te:]
    sys.path[:0] = [TOOLS, TOOLKIT]
    from toolkit_core import bindict_table as bt
    try:
        idx = bt.parse_index(blob)
        known = bt._collect_schemas(blob, idx)
    except ValueError:
        return {"entry": entry, "error": "no_index", "hits": []}
    if not known and not any(0 <= s < len(blob) and blob[s] == 0x36
                             for _k, s in idx):
        return {"entry": entry, "error": "no_schemas", "hits": []}
    # 行起点与边界（对齐 decode_table_rows 已验证逻辑）
    starts = sorted({s for _k, s in idx if 0 <= s < len(blob)})
    base = at + 6 + te
    hits = []
    stats = Counter()
    # 行起点有效性按 marker/schema 检查
    for r_i, (key, s0) in enumerate(idx):
        if not (0 <= s0 < len(blob)):
            stats["unbound"] += 1
            continue
        marker = blob[s0]
        if marker == 0x36:
            # mapping 行：36 kt vt uleb(count) pairs
            if s0 + 3 > len(blob):
                continue
            kt, vt = blob[s0 + 1], blob[s0 + 2]
            try:
                pc, q = bt.uleb(blob, s0 + 3, len(blob))
            except ValueError:
                continue
            for _ in range(pc):
                try:
                    kv, q = bt._decode_value(blob, q, kt, [])
                    vv, q = bt._decode_value(blob, q, vt, [])
                except ValueError:
                    break
                for val, side in ((kv, "k"), (vv, "v")):
                    if isinstance(val, int) and val != 0:
                        hits.append((val, key, r_i, base + s0, None, None,
                                     None, side, "0x36"))
            continue
        if marker not in (0x96, 0xD6, 0xC6):
            stats["bad_marker"] += 1
            continue
        try:
            sr, q0 = bt.uleb(blob, s0 + 1, len(blob))
        except ValueError:
            stats["bad_schema_uleb"] += 1
            continue
        if sr not in known:
            stats["unknown_schema"] += 1
            continue
        try:
            bits, fields, _ = bt._schema_at(blob, sr, [])
        except ValueError:
            stats["bad_schema"] += 1
            continue
        nxt = len(blob)
        for s2 in starts:
            if s2 > s0:
                nxt = s2
                break
        q = q0
        bm_size = (bits + 7) // 8
        if marker == 0x96:
            if q + bm_size > len(blob):
                continue
            bm = blob[q:q + bm_size]
            q += bm_size
        else:
            try:
                bref, q = bt.uleb(blob, q, len(blob))
            except ValueError:
                continue
            if bref + bm_size > len(blob):
                continue
            bm = blob[bref:bref + bm_size]
        if q > nxt:
            continue
        # 启用槽（对齐 decode_table_rows 已验证逻辑）：i<bits 看位图；i>=bits 默认启用
        enabled = [i for i, (_s, _t, _n) in enumerate(fields)
                   if i >= bits or (bm[i // 8] >> (i % 8)) & 1]
        ok = True
        for ix in enabled:
            _slot, tbyte, _name = fields[ix]
            try:
                val, q = bt._decode_value(blob, q, tbyte, [])
            except ValueError:
                ok = False
                break
            if q > nxt:
                ok = False
                break
            if tbyte in INT_TYPES and isinstance(val, int) and val != 0:
                hits.append((val, key, r_i, base + s0, sr, ix, None, None,
                             "std"))
        if not ok:
            stats["value_overrun"] += 1
            continue
        stats["rows_decoded"] += 1
        # 行尾 0x27 内联组（27 kind uleb cnt + 元素——元素全 uleb，同解码器）
        while q < nxt and blob[q] == 0x27:
            try:
                ec, q = bt.uleb(blob, q + 2, nxt)
            except (IndexError, ValueError):
                break
            try:
                for gi in range(ec):
                    ev, q = bt.uleb(blob, q, nxt)
                    if ev != 0:
                        hits.append((ev, key, r_i, base + s0, sr, None, gi,
                                     None, "grp"))
            except ValueError:
                break
    return {"entry": entry, "error": None, "hits": hits, "stats": stats}


def main() -> int:
    t0 = time.time()
    bodies = []
    with TABLE_ENTRIES.open(encoding="utf-8") as f:
        for ln in f:
            r = json.loads(ln)
            if r["client_channel"] == "test" and r["table_body"] \
                    and r["table_name"]:
                bodies.append(r)
    con = sqlite3.connect(DB)
    fid_map = {}
    for (entry, ident) in con.execute(
            "SELECT entry_index, identifier FROM locations WHERE "
            "client_channel='test' AND identifier_type='fid' AND "
            "package='Documents/script.py314.lc.npk'"):
        fid_map[entry] = ident
    tasks = [(r["entry"], f"{r['entry']:06d}.bin", r["table_name"],
              fid_map.get(r["entry"])) for r in bodies]
    print(f"bodies: {len(tasks)}", flush=True)
    workers = min(12, (__import__("os").cpu_count() or 4))
    if OUT_DB.exists():
        OUT_DB.unlink()
    db = sqlite3.connect(OUT_DB)
    db.execute("PRAGMA journal_mode=OFF")
    db.execute("PRAGMA synchronous=OFF")
    db.executescript(
        "CREATE TABLE occurrences (id INTEGER NOT NULL, kind TEXT, "
        "table_name TEXT, fid TEXT, entry INTEGER, row_key INTEGER, "
        "row_index INTEGER, offset INTEGER, schema_ref INTEGER, "
        "field_slot INTEGER, group_index INTEGER, element_index TEXT, "
        "marker TEXT);"
        "CREATE INDEX idx_id ON occurrences (id);"
        "CREATE INDEX idx_table ON occurrences (entry);")
    total = 0
    overflow_ids = 0
    fail_stats = Counter()
    n_scan = 0
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for i, res in enumerate(ex.map(_scan_table, tasks, chunksize=8), 1):
            if res["error"]:
                fail_stats[res["error"]] += 1
                continue
            n_scan += 1
            if res["hits"]:
                # SQLite INTEGER=有符号 64 位：越界值非 ID 语义，跳过并计数
                rows_in = []
                for h in res["hits"]:
                    if not (-(2 ** 63) <= h[0] < 2 ** 63):
                        overflow_ids += 1
                        continue
                    if not (-(2 ** 63) <= (h[1] or 0) < 2 ** 63):
                        overflow_ids += 1
                        continue
                    rows_in.append(
                        (h[0], "int", tasks[i - 1][2], tasks[i - 1][3],
                         res["entry"], h[1], h[2], h[3], h[4], h[5], h[6],
                         h[7], h[8]))
                if rows_in:
                    db.executemany(
                        "INSERT INTO occurrences VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        rows_in)
                    total += len(rows_in)
            if i % 500 == 0:
                db.commit()
                print(f"  [{i}/{len(tasks)}] hits {total:,} "
                      f"{time.time()-t0:.0f}s", flush=True)
    db.commit()
    n_unique = db.execute("SELECT count(DISTINCT id) FROM occurrences").fetchone()[0]
    n_multi_table = db.execute(
        "SELECT count(*) FROM (SELECT id FROM occurrences GROUP BY id "
        "HAVING count(DISTINCT entry) > 1)").fetchone()[0]
    db.close()
    summary = {
        "schema_version": 1,
        "snapshot": SNAPSHOT,
        "tables_scanned": n_scan,
        "tables_skipped": {k: v for k, v in fail_stats.items()},
        "overflow_ids_dropped": overflow_ids,
        "occurrences_total": total,
        "unique_ids": n_unique,
        "ids_in_multiple_tables": n_multi_table,
        "field_names": "none-by-design（本层不解字段名，只记 field_slot；P2 再命名）",
        "note": "整数槽 ULEB/ULEB_ALT/ZIGZAG + 0x27 组元素 + 0x36 mapping 键值；"
                "值=0 槽不记（缺省/空值）；只记录出现位置不解释业务含义；"
                "同 ID 跨表出现不建业务关系；server_branch=unresolved",
        "build_seconds": round(time.time() - t0, 1),
    }
    OUT_SUM.write_text(json.dumps(summary, ensure_ascii=False, indent=1),
                       encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    print("->", OUT_DB)
    return 0


if __name__ == "__main__":
    sys.exit(main())
