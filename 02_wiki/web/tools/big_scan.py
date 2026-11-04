# -*- coding: utf-8 -*-
"""大文件/大目录扫描器：按目录聚合大小 + 记录 >300MB 的单文件，输出 JSON。

用法：python big_scan.py E:/ [C:/Users] --out xxx.json
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

SKIP = {"Windows", "WinSxS", "$Recycle.Bin", "System Volume Information", "node_modules",
        ".git", "AppData/Local/Packages"}
BIG = 300 * 1024 * 1024


def main() -> int:
    roots = [Path(a) for a in sys.argv[1:] if not a.startswith("--")]
    out = Path([a.split("=", 1)[1] for a in sys.argv if a.startswith("--out=")][0])
    big: list[dict] = []
    sizes: dict[str, int] = {}
    t0 = time.time()

    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root, onerror=lambda e: None):
            dirnames[:] = [d for d in dirnames if d not in SKIP]
            try:
                for fn in filenames:
                    p = os.path.join(dirpath, fn)
                    try:
                        st = os.stat(p, follow_symlinks=False)
                    except OSError:
                        continue
                    sz = st.st_size
                    if sz >= BIG:
                        big.append({"path": p, "mb": round(sz / 2**20), "mtime": int(st.st_mtime)})
                    rel = os.path.relpath(p, root)
                    top = rel.split(os.sep)[0] if os.sep in rel else "(root files)"
                    sizes[f"{root}|{top}"] = sizes.get(f"{root}|{top}", 0) + sz
            except Exception:
                continue
            if time.time() - t0 > 1500:
                print("超时，已扫部分", flush=True)
                break

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"big": sorted(big, key=lambda x: -x["mb"]),
                               "tops": dict(sorted(sizes.items(), key=lambda kv: -kv[1])[:60])},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    print("大文件", len(big), "| 顶层目录", len(sizes), "| 用时", int(time.time() - t0), "s")
    for k, v in sorted(sizes.items(), key=lambda kv: -kv[1])[:12]:
        print(f"  {v/2**30:8.1f}G  {k}")
    for b in sorted(big, key=lambda x: -x["mb"])[:12]:
        print(f"  {b['mb']:7d}MB  {b['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
