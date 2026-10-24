# -*- coding: utf-8 -*-
r"""核「这批贴图是不是本期新增」：两个独立判据。

① fid 是否在 `新增_fid.txt`（pkg_N.pi 两版 diff 的新增集合）
② 该内容的 md5 是否已存在于**别的容器**（= 之前就有的旧资源，随包重发）

输出：本期新增 / 随包重发 / 判不出 三类各多少张，并给样例。
"""
from __future__ import annotations

import collections
import json
import pathlib
import sqlite3

PROJ = pathlib.Path(r"E:/la拆包项目")
IDX = PROJ / "01_索引与产物/10_索引/indexes/lifeafter_files.sqlite3"
ROWMAP = PROJ / "01_索引与产物/10_索引/indexes/row_path_map.db"
DELIV = PROJ / "01_索引与产物/10_索引/热更检测/post_update_20261017_batch2/交付_playertest_20261017"
OUT = PROJ / "01_索引与产物/10_索引/热更检测/post_update_20261017_batch2/校验"
OUT.mkdir(parents=True, exist_ok=True)

CONT = ("Documents\\gres\\0006.gpk", "Documents\\gres\\0007.gpk")

added_file = DELIV / "04_变更清单与报告总结/变更清单/新增_fid.txt"
added = set()
if added_file.is_file():
    for ln in added_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = ln.strip()
        if s:
            added.add(s.upper())
print("新增 fid 清单：%d 条（%s）" % (len(added), added_file.name))

con = sqlite3.connect(str(IDX), timeout=60)
con.execute("ATTACH DATABASE ? AS rm", (str(ROWMAP),))
q = """
SELECT e.container, e.row_index, e.fid_hex, r.path, ch.md5, ch.size
FROM entries e
JOIN rm.rows r ON r.container = e.container AND r.row_index = e.row_index
LEFT JOIN content_hashes ch ON ch.container = e.container AND ch.row_index = e.row_index
WHERE e.container IN (?, ?) AND r.in_tree = 1
"""
rows = con.execute(q, CONT).fetchall()

dds = [r for r in rows if str(r[3]).lower().endswith(".dds")]
print("两个容器的 .dds 行：%d" % len(dds))

# ② 该 md5 在【别的容器】里也出现 → 之前就有
md5_other = collections.defaultdict(set)
q2 = "SELECT md5, container FROM content_hashes WHERE md5 IS NOT NULL"
for md5, c in con.execute(q2):
    if c not in CONT:
        md5_other[md5].add(c)
con.close()

new_fid = new_both = old = unknown = 0
samples = collections.defaultdict(list)
for c, ri, fid, path, md5, size in dds:
    in_added = (fid or "").upper() in added if added else None
    existed = bool(md5 and md5 in md5_other)
    if in_added is None:
        unknown += 1
        continue
    if in_added and not existed:
        new_both += 1
        tag = "本期新增（fid 在新增集 且 内容别处没有）"
    elif in_added and existed:
        new_fid += 1
        tag = "fid 新但内容旧（重发/复用）"
    else:
        old += 1
        tag = "fid 不在新增集（随包旧资源）"
    if len(samples[tag]) < 5:
        samples[tag].append("%s r%s %s %sB" % (c.split("\\")[-1], ri, (fid or "")[:16],
                                               size))

print("\n=== 判据结果（%d 张 .dds）===" % len(dds))
for k in ("本期新增（fid 在新增集 且 内容别处没有）", "fid 新但内容旧（重发/复用）",
          "fid 不在新增集（随包旧资源）"):
    n = {"本期新增（fid 在新增集 且 内容别处没有）": new_both,
         "fid 新但内容旧（重发/复用）": new_fid,
         "fid 不在新增集（随包旧资源）": old}[k]
    print("  %-36s %6d 张（%.1f%%）" % (k, n, 100 * n / max(1, len(dds))))
    for s in samples.get(k, []):
        print("        ", s)
print("  判不出（无新增清单）              %6d" % unknown)

(OUT / "贴图_是否本期.json").write_text(json.dumps({
    "dds_rows": len(dds), "新增fid清单": len(added),
    "本期新增": new_both, "fid新内容旧": new_fid, "随包旧资源": old,
    "判不出": unknown, "样例": {k: v for k, v in samples.items()},
}, ensure_ascii=False, indent=1), encoding="utf-8")
print("\n产物 →", OUT / "贴图_是否本期.json")
