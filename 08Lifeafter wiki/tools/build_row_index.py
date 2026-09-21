# -*- coding: utf-8 -*-
"""P1-12：行级定位索引（test BA8 快照，全表数据体）。

只记录行定位（client/snapshot/table/fid/entry/row_index/row_key/offset/
schema_ref），不解字段值、不做字段语义/业务关联。

两种已验证行编码：
- 标准 D6/C6/96 行：0x76 索引尾 (key,start) + 行头 marker/schema_ref（uleb）
- KJ1 老格式：76 0b 0b 索引 + node off→ULEB 行偏移桶（行 key=node key，
  行型=首 ULEB，记录为 schema_ref=行首 uleb 值）
定位失败的表/行如实记 parse_failed（reason 分类）。

live：无独立解码证据，不靠 test 传播补行（仅 test 快照产行）。

输出：data/row_index.jsonl + data/row_index_summary.json
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
OUT_ROWS = ROOT / "data" / "row_index.jsonl"
OUT_SUM = ROOT / "data" / "row_index_summary.json"
SNAPSHOT = "test-328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f"
TOOLKIT = r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心"
TOOLS = str(Path(__file__).resolve().parent)


def xbody(data: bytes) -> tuple[int | None, int | None, str]:
    pos = 0
    while True:
        at = data.find(b"x{", pos)
        if at < 0:
            return None, None, "no_x_container"
        if at + 6 <= len(data):
            n = int.from_bytes(data[at + 2:at + 6], "little")
            if 0 < n <= len(data) - at - 6:
                cnt = int.from_bytes(data[at + 6:at + 10], "little")
                res = int.from_bytes(data[at + 10:at + 14], "little")
                if res == 0 and cnt <= 300000:
                    return at, n, "ok"
        pos = at + 3


def locate_rows(body: bytes):
    """返回 (rows, table_error)。rows=[{key,start,marker,schema_ref}]。"""
    if len(body) < 8:
        return [], "short_body"
    cnt = int.from_bytes(body[0:4], "little")
    res = int.from_bytes(body[4:8], "little")
    if res != 0:
        return [], "reserved_not_zero"
    te = 8 + 4 * cnt
    if te > len(body):
        return [], "bad_row_count"
    blob = body[te:]
    if len(blob) < 8:
        return [], "short_blob"
    sys.path[:0] = [TOOLS, TOOLKIT]
    from toolkit_core import bindict_table as bt
    # 标准 0x76 索引
    try:
        idx = bt.parse_index(blob)
        known = bt._collect_schemas(blob, idx)
        if known or any(0 <= s < len(blob) and blob[s] == 0x36
                        for _k, s in idx):
            rows = []
            for key, start in idx:
                if not (0 <= start < len(blob)):
                    continue
                marker = blob[start]
                if marker == 0x36:
                    rows.append({"key": key, "start": start, "marker": "0x36",
                                 "schema_ref": None})
                    continue
                if marker not in (0x96, 0xD6, 0xC6):
                    continue
                try:
                    sr, _ = bt.uleb(blob, start + 1, len(blob))
                except ValueError:
                    continue
                if sr in known:
                    rows.append({"key": key, "start": start,
                                 "marker": f"0x{marker:02x}",
                                 "schema_ref": sr})
            if rows:
                return rows, None
            return [], "no_valid_std_rows"
    except ValueError:
        pass
    # KJ1 老格式
    try:
        de = int.from_bytes(blob[0:4], "little")
        if 4 <= de < len(blob) and blob[de:de + 3] == b"\x76\x0b\x0b":
            tail = blob[de:]
            n, p = bt.uleb(tail, 3, len(tail))
            nodes = [struct.unpack_from("<II", tail, p + i * 8)
                     for i in range(n)]
            offs = sorted({o for _k, o in nodes if de <= o < len(blob)})
            bend = {o: (offs[i + 1] if i + 1 < len(offs) else len(blob))
                    for i, o in enumerate(offs)}
            rows = []
            for k, o in nodes:
                if not (de <= o < len(blob)):
                    continue
                q, end = o, bend.get(o, len(blob))
                targets = []
                while q < end:
                    try:
                        v, q = bt.uleb(blob, q, end)
                    except ValueError:
                        break
                    targets.append(v)
                for t in targets:
                    if not (4 <= t < de):
                        continue
                    try:
                        head_u = bt.uleb(blob, t, de)[0]
                    except ValueError:
                        head_u = None
                    rows.append({"key": k, "start": t, "marker": "kj1",
                                 "schema_ref": head_u})
            if rows:
                return rows, None
            return [], "kj1_nodes_fail"
    except (ValueError, struct.error):
        pass
    # 头特征分类（只记录，不硬解新格式）
    b0 = blob[0] if blob else -1
    if b0 == 0x73:
        return [], "legacy_0x73_shell"
    if b0 in (0x96, 0xD6, 0xC6, 0x92):
        return [], "row_stream_without_index"
    return [], f"unknown_head_0x{b0:02x}"


def _process_table(args: tuple) -> dict:
    entry, fn, table_name, fid = args
    data = (ENTRIES_DIR / fn).read_bytes()
    at, xl, xmode = xbody(data)
    if at is None:
        return {"entry": entry, "fid": fid, "table": table_name,
                "rows": [], "error": xmode, "body_len": len(data)}
    body = data[at + 6:at + 6 + xl]
    rows, err = locate_rows(body)
    if err:
        return {"entry": entry, "fid": fid, "table": table_name, "rows": [],
                "error": err, "body_len": len(body)}
    te = 8 + 4 * int.from_bytes(body[0:4], "little")  # 行区起点（blob 前）
    out = []
    for i, r in enumerate(rows, 1):
        out.append({
            "client_channel": "test",
            "snapshot": SNAPSHOT,
            "table": table_name,
            "fid": fid,
            "entry": entry,
            "row_index": i,
            "row_key": r["key"],
            "offset": at + 6 + te + r["start"],
            "schema_ref": r["schema_ref"],
            "marker": r["marker"],
        })
    return {"entry": entry, "fid": fid, "table": table_name, "rows": out,
            "error": None, "body_len": len(body)}


def main() -> int:
    t0 = time.time()
    # 表体清单（test BA8）+ fid
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
    print(f"table bodies: {len(tasks)}", flush=True)
    workers = min(12, (__import__("os").cpu_count() or 4))
    stats = Counter()
    row_count = 0
    schema_ref_tables = 0
    with ProcessPoolExecutor(max_workers=workers) as ex:
        with OUT_ROWS.open("w", encoding="utf-8", newline="\n") as f:
            for i, res in enumerate(ex.map(_process_table, tasks,
                                           chunksize=8), 1):
                if res["error"]:
                    stats["failed_tables:" + res["error"]] += 1
                else:
                    stats["ok_tables"] += 1
                    if any(r["schema_ref"] is not None
                           for r in res["rows"]):
                        schema_ref_tables += 1
                    for r in res["rows"]:
                        f.write(json.dumps(r, ensure_ascii=False) + "\n")
                        row_count += 1
                if i % 500 == 0:
                    print(f"  [{i}/{len(tasks)}] rows so far {row_count:,} "
                          f"{time.time()-t0:.0f}s", flush=True)
    summary = {
        "schema_version": 1,
        "snapshot": SNAPSHOT,
        "client": "test",
        "table_bodies_total": len(tasks),
        "tables_indexed": stats["ok_tables"],
        "tables_parse_failed": len(tasks) - stats["ok_tables"],
        "parse_failed_reasons": {k.replace("failed_tables:", ""): v
                                 for k, v in stats.items()
                                 if k.startswith("failed_tables:")},
        "total_rows": row_count,
        "rows_with_schema_ref": None,  # 由统计脚本填
        "tables_with_schema_ref": schema_ref_tables,
        "note": "行级定位（0x76 索引/KJ1 桶），row_key=索引 key，offset=表体文件内绝对偏移，"
                "schema_ref=行首 uleb（std 表=schema 引用号；KJ1=行首 uleb 行型值）；"
                "不解字段值；live 无独立解码证据不补行；server_branch=unresolved",
        "build_seconds": round(time.time() - t0, 1),
    }
    OUT_SUM.write_text(json.dumps(summary, ensure_ascii=False, indent=1),
                       encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
