# -*- coding: utf-8 -*-
r"""Stage 1-①：同内容（md5）硬链接去重。

口径：`content_hashes`（容器/行 → md5） JOIN `row_path_map`（容器/行 → 树路径）。
同一 md5 有多份时，保留一份、其余 `unlink + os.link(保留份)` —— 同卷硬链接，瞬时、不复制。

★ 安全前提：项目规矩是「往树里写字节必须先 unlink」（硬链接共享 inode）。所有写入口
  （restore_merge / gres_layer_merge）都已 unlink ✓，所以去重后仍安全。

用法：dedupe_tree.py            # dry-run（只报数）
      dedupe_tree.py --real     # 真做
"""
from __future__ import annotations

import os
import pathlib
import sqlite3
import sys
from collections import defaultdict

IDX = pathlib.Path(r"E:/la拆包项目/01_索引与产物/10_索引/indexes/lifeafter_files.sqlite3")
ROWMAP = pathlib.Path(r"E:/la拆包项目/01_索引与产物/10_索引/indexes/row_path_map.db")
TREE = pathlib.Path(r"E:/la拆包项目/01_索引与产物/41_还原树")
REAL = "--real" in sys.argv
MIN_SIZE = 0

con = sqlite3.connect(str(IDX), timeout=60)
con.execute("ATTACH DATABASE ? AS rm", (str(ROWMAP),))
q = """
SELECT ch.md5, ch.container, ch.row_index, ch.size, r.path
FROM content_hashes ch
JOIN rm.rows r ON r.container = ch.container AND r.row_index = ch.row_index
WHERE r.in_tree = 1
  AND ch.size > ?
  AND ch.md5 IN (SELECT md5 FROM content_hashes GROUP BY md5 HAVING COUNT(*) > 1)
ORDER BY ch.md5
"""
rows = con.execute(q, (MIN_SIZE,)).fetchall()
con.close()
print("候选行 %d（重复内容）" % len(rows))

groups: dict[str, list[tuple[pathlib.Path, int]]] = defaultdict(list)
for md5, _c, _r, size, rel in rows:
    p = TREE / str(rel).replace("\\", "/")
    if p.is_file():
        groups[md5].append((p, int(size)))

done = skipped_missing = already = 0
saved = 0
errors = []
for md5, items in groups.items():
    if len(items) < 2:
        continue
    keep_p, size = items[0]
    keep_ino = keep_p.stat().st_ino
    for p, _s in items[1:]:
        try:
            st = p.stat()
            if (st.st_dev, st.st_ino) == (keep_p.stat().st_dev, keep_ino):
                already += 1
                continue
            if REAL:
                # ★★ 顺序必须是「先建链接、再原子替换」——
                #   写成 `p.unlink(); os.link(...)` 时，link 失败（NTFS 单文件最多 1023 个硬链接）
                #   就等于把文件删了没建回来（2026-10-17 就这么丢了 60,955 个 scene DDS，靠
                #   repair_tree.py 从客户端容器重解才补回）。这里用临时名 + os.replace：
                #   link 失败 ⇒ 原文件毫发无损。
                tmp = p.with_name(p.name + ".dedupe_tmp")
                try:
                    if tmp.exists():
                        tmp.unlink()
                    os.link(keep_p, tmp)
                    os.replace(tmp, p)
                except OSError:
                    if tmp.exists():
                        tmp.unlink()
                    raise
            done += 1
            saved += st.st_size
        except FileNotFoundError:
            skipped_missing += 1
        except OSError as exc:
            errors.append("%s: %s" % (p, exc))

print("组 %d ｜ 已同 inode 跳过 %d ｜ %s %d ｜ 缺失 %d ｜ 错误 %d"
      % (len(groups), already, "已硬链接" if REAL else "可去重", done,
         skipped_missing, len(errors)))
print("预计/实际节省 ≈ %.2f GB" % (saved / 1024 ** 3))
for e in errors[:5]:
    print("  ✗", e[:140])
