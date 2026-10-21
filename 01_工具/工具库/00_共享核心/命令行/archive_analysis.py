# -*- coding: utf-8 -*-
r"""Stage 1-②：把「0 引用 + 已冷」的专题分析目录打包成 zip，校验后删源。

规则（照项目清理判据）：
  · 只动 30_分析 下**代码/站点 0 引用**的目录
  · 先 zip（ZIP_LZMA，7-Zip/Python 都能读）→ `testzip()` 全过 + 文件数一致 → 才删源
  · 产物落 `30_分析/_归档/<名>_<日期>.zip`，并追加一行到 `_归档/清单.md`

用法：archive_analysis.py [--real]
"""
from __future__ import annotations

import datetime
import pathlib
import shutil
import sys
import zipfile

BASE = pathlib.Path(r"E:/la拆包项目/03_执行/30_分析")
ARCH = BASE / "_归档"
REAL = "--real" in sys.argv

#: 0 引用（2026-10-17 扫过 01_工具 + 04_站点 的 .py/.js/.html/.json/.md）
CANDIDATES = [
    "c159挖掘_20260928",
    "热更_9月28日_流水线",
    "热更_9月28日_直解",
    "字典猛攻_20260927",
    "空白攻坚_20260927",
    "内容认领_20261001",
    "正式服UI缓存_20260928",
]


def dir_files(d: pathlib.Path) -> list[pathlib.Path]:
    return [p for p in d.rglob("*") if p.is_file()]


ARCH.mkdir(parents=True, exist_ok=True)
log = ARCH / "清单.md"
if not log.exists():
    log.write_text("# 30_分析 归档清单（zip 后可解回）\n\n", encoding="utf-8")

tot_before = tot_after = 0
for name in CANDIDATES:
    d = BASE / name
    if not d.is_dir():
        print("跳过（不存在）: %s" % name)
        continue
    files = dir_files(d)
    before = sum(p.stat().st_size for p in files)
    z = ARCH / ("%s_%s.zip" % (name, datetime.date.today().strftime("%Y%m%d")))
    print("%-28s %6d 文件 / %6.2f GB → %s" % (name, len(files), before / 1024 ** 3,
                                              "打包" if REAL else "（dry-run）"))
    if not REAL:
        tot_before += before
        continue
    with zipfile.ZipFile(z, "w", compression=zipfile.ZIP_LZMA, compresslevel=9) as zf:
        for p in files:
            zf.write(p, p.relative_to(d).as_posix())
    # 校验
    with zipfile.ZipFile(z) as zf:
        bad = zf.testzip()
        n = len([x for x in zf.namelist() if not x.endswith("/")])
    if bad or n != len(files):
        print("   ✗ 校验失败（bad=%s, %d≠%d），保留源目录" % (bad, n, len(files)))
        continue
    after = z.stat().st_size
    shutil.rmtree(d)
    tot_before += before
    tot_after += after
    with log.open("a", encoding="utf-8") as fh:
        fh.write("- `%s` ← `%s`（%d 文件 / %.2f GB → %.2f GB）\n"
                 % (z.name, name, len(files), before / 1024 ** 3, after / 1024 ** 3))
    print("   ✓ %d 文件一致 ｜ %.2f GB → %.2f GB（省 %.2f GB）"
          % (n, before / 1024 ** 3, after / 1024 ** 3, (before - after) / 1024 ** 3))

print("\n合计：%.2f GB → %.2f GB ｜ 省 %.2f GB" %
      (tot_before / 1024 ** 3, tot_after / 1024 ** 3, (tot_before - tot_after) / 1024 ** 3))
if not REAL:
    print("（dry-run：加 --real 才真打包+删源）")
