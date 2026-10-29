# -*- coding: utf-8 -*-
"""cdata 归一（A 档）：把 配置 / 配置_基线包 / 配置_增量快照 合成唯一一份。

规则：热更优先 —— 增量快照 > 配置 > 基线包（同名表取优先级最高的那份）。
实现：硬链接进 配置_v2（不复制内容、不占空间），校验通过后再换名上线。
"""
from __future__ import annotations
import sys

import hashlib
import json
import os
import pathlib
import shutil

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import TREE_ROOT  # noqa: E402

PE = pathlib.Path(TREE_ROOT / "pe")
SRC = [("增量快照", PE / "配置_增量快照/com/cdata"),
       ("合并体", PE / "配置/com/cdata"),
       ("基线包", PE / "配置_基线包/com/cdata")]
DST = PE / "配置_v2/com/cdata"
LEDGER = PE / "pe_config_merge_ledger_v2.json"


def sha256(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main() -> int:
    if DST.exists():
        shutil.rmtree(DST)
    DST.mkdir(parents=True)

    chosen: dict[str, tuple[str, pathlib.Path]] = {}
    for tag, d in SRC:
        if not d.is_dir():
            print("跳过缺失目录", d)
            continue
        for p in d.iterdir():
            if not p.is_file():
                continue
            # 先遍历到的是高优先级；已存在则不覆盖
            chosen.setdefault(p.name, (tag, p))

    rows = []
    for name, (tag, p) in sorted(chosen.items()):
        dst = DST / name
        try:
            os.link(p, dst)
        except OSError:
            shutil.copyfile(p, dst)
        rows.append({"file": name, "source": tag,
                     "path": str(p).replace("\\", "/"),
                     "bytes": p.stat().st_size, "sha256": sha256(p)})

    LEDGER.write_text(json.dumps({
        "schema": "pe-config-merge-ledger-v2",
        "generated": "2026-10-26",
        "rule": "增量快照 > 配置(合并体) > 基线包，同名表取高优先级；硬链接复用不复制",
        "sources": [{"tag": t, "dir": str(d).replace("\\", "/")} for t, d in SRC],
        "count": len(rows),
        "files": rows,
    }, ensure_ascii=False), encoding="utf-8")

    from collections import Counter
    c = Counter(r["source"] for r in rows)
    print("归一完成：%d 个文件 → %s" % (len(rows), DST))
    print("来源分布：", dict(c))
    print("ledger：", LEDGER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
