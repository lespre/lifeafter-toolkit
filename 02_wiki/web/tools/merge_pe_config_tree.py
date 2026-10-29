# -*- coding: utf-8 -*-
"""合成全量 PE 配置树：基线包打底 + 热更增量覆盖。

为什么这样做而不是"搅在一起"：
  PE 本身的包结构就是「全量基线包 + 增量热更包」，覆盖关系是确定的（后包覆盖前包）。
  合出来的是一份**干净快照**，同时把每个文件来自哪个包写进清单，可追溯、可回滚。
  这与 PC 那种 res/gres 多根互相覆盖、谁生效说不清的情况不是一回事。

输出：
  41_还原树/pe/配置/            合成后的树
  41_还原树/pe/pe_config_full_合并清单.json  每个文件的来源 + 被覆盖清单
"""
from __future__ import annotations
import sys

import hashlib
import json
import pathlib
import shutil
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

BASE = PROJ / "01_索引与产物/41_还原树/pe/配置_基线包"
OVER = PROJ / "01_索引与产物/41_还原树/pe/配置_增量快照"
OUT = PROJ / "01_索引与产物/41_还原树/pe/配置"
MAN = PROJ / "01_索引与产物/41_还原树/pe/pe_config_full_合并清单.json"


def sha(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        while block := f.read(1 << 20):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    if not BASE.is_dir() or not OVER.is_dir():
        print("缺来源树")
        return 1
    if OUT.exists():
        print("目标已存在，先手动清理：", OUT)
        return 1
    t0 = time.time()

    base_files = {p.relative_to(BASE).as_posix(): p for p in BASE.rglob("*") if p.is_file()}
    over_files = {p.relative_to(OVER).as_posix(): p for p in OVER.rglob("*") if p.is_file()}
    print("基线 %d 文件 ｜ 增量 %d 文件" % (len(base_files), len(over_files)))

    overwritten, only_over = [], []
    n = 0
    for rel, src in base_files.items():
        dst = OUT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        n += 1
    for rel, src in over_files.items():
        dst = OUT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if rel in base_files:
            if sha(src) != sha(base_files[rel]):
                overwritten.append(rel)
        else:
            only_over.append(rel)
        shutil.copyfile(src, dst)
        n += 1

    merged = {p.relative_to(OUT).as_posix(): p for p in OUT.rglob("*") if p.is_file()}
    MAN.write_text(json.dumps({
        "base": str(BASE.relative_to(PROJ)),
        "overlay": str(OVER.relative_to(PROJ)),
        "base_files": len(base_files),
        "overlay_files": len(over_files),
        "overwritten_by_overlay": sorted(overwritten),
        "only_in_overlay_count": len(only_over),
        "only_in_overlay_sample": sorted(only_over)[:200],
        "merged_files": len(merged),
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    print("合成完成：%d 文件 ｜ 覆盖 %d ｜ 增量独有 %d ｜ %.0fs"
          % (len(merged), len(overwritten), len(only_over), time.time() - t0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
