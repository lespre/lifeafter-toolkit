# -*- coding: utf-8 -*-
r"""救火：把树里【缺失】的文件按 (容器,行) 从客户端容器重新解出来补回去。

怎么判断哪些缺了：row_path_map 里 in_tree=1 的每一行 → 树里 `is_file()`。
怎么补：容器在 `E:/mrzh/<容器名>`；gpk 用 `_gpk_blockchain` 拿 (poff,packed,decoded,flag)，
        `la_unpack_core.npk_decode_entry` 解码，按 row_path_map 的路径写回。

用法：repair_tree.py [--real] [--limit N]
"""
from __future__ import annotations

import pathlib
import sqlite3
import sys
import time
from collections import defaultdict

PROJ = pathlib.Path(r"E:/la拆包项目")
ROWMAP = PROJ / "03_执行/10_索引/indexes/row_path_map.db"
TREE = PROJ / "03_执行/41_还原树"
CLIENT = pathlib.Path(r"E:/mrzh")
GPKI = PROJ / "01_工具/工具库/02_图文音频渲染/皮肤链与渲染"
UNPACK = PROJ / "01_工具/工具库/01_解码定位复原/解包与扫描"

REAL = "--real" in sys.argv
LIMIT = None
if "--limit" in sys.argv:
    LIMIT = int(sys.argv[sys.argv.index("--limit") + 1])

sys.path.insert(0, str(GPKI))
sys.path.insert(0, str(UNPACK))
import gpk_npk_index as gpki          # noqa: E402
import la_unpack_core as core          # noqa: E402

con = sqlite3.connect(str(ROWMAP), timeout=60)
rows = con.execute("SELECT container,row_index,path FROM rows WHERE in_tree=1").fetchall()
con.close()
print("row_path_map in_tree=1: %d 行" % len(rows))

missing: dict[str, list[tuple[int, str]]] = defaultdict(list)
for c, r, rel in rows:
    p = TREE / str(rel).replace("\\", "/")
    if not p.is_file():
        missing[c].append((int(r), str(rel)))
total = sum(len(v) for v in missing.values())
print("缺失 %d 个（%d 个容器）" % (total, len(missing)))
for c, v in sorted(missing.items(), key=lambda kv: -len(kv[1]))[:8]:
    print("   %-42s %6d" % (c, len(v)))
if not REAL:
    print("\n（dry-run；加 --real 才补写）")
    raise SystemExit(0)

done = fail = 0
t0 = time.time()
for c, items in missing.items():
    src = CLIENT / c.replace("\\", "/")
    if not src.is_file():
        print("✗ 容器不在客户端: %s（%d 条补不了）" % (c, len(items)))
        fail += len(items)
        continue
    try:
        _rec, rows_fn, _blocks = gpki._gpk_blockchain(str(src), with_crc=True)
        # (row, fid, poff, packed, decoded, flag, crc1, crc2) —— ★ flag 必须带上，
        # 写死 0 会去「明文直通」分支 ⇒ 解出 75 B 这种垃圾（2026-10-17 踩过）
        table = {int(r[0]): (int(r[2]), int(r[3]), int(r[4]), int(r[5])) for r in rows_fn()}
    except Exception as exc:                                      # noqa: BLE001
        print("✗ 解析容器失败 %s: %s" % (c, exc))
        fail += len(items)
        continue
    with src.open("rb") as fh:
        for r, rel in items:
            if LIMIT and done >= LIMIT:
                break
            t = table.get(r)
            if not t:
                fail += 1
                continue
            poff, packed, decoded, flag = t
            try:
                fh.seek(poff)
                seg = fh.read(packed)
                data = core.npk_decode_entry(seg, decoded, flag)
                if data is None or len(data) != decoded:
                    raise ValueError("解出 %s B ≠ 声明 %d" % (0 if data is None else len(data), decoded))
                dst = TREE / rel.replace("\\", "/")
                dst.parent.mkdir(parents=True, exist_ok=True)
                if dst.exists():
                    dst.unlink()
                dst.write_bytes(data)
                done += 1
            except Exception as exc:                              # noqa: BLE001
                fail += 1
                if fail <= 5:
                    print("  ✗ r%s %s: %s" % (r, rel[:60], exc))
print("补回 %d ｜ 失败 %d ｜ 用时 %.1fs" % (done, fail, time.time() - t0))
