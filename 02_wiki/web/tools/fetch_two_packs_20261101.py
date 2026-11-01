# -*- coding: utf-8 -*-
"""补下两个缺/旧的大包到 pe_npk_20261029/（断点续传 + 尺寸校验 + 先写 .part）。

清单：01_索引与产物/10_索引/cdn_20261101/npk_version_android4_playertest（version 20261029_101825_playertest_android）
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path("E:/la拆包项目")
MAN = ROOT / "01_索引与产物/10_索引/cdn_20261101/npk_version_android4_playertest"
OUT = ROOT / "01_索引与产物/源包/pe_npk_20261029"
HOST = "https://g66.gph.netease.com"
TARGETS = ["res.layers.1.1.npk", "res/ui.layers.1.1.npk"]


def main() -> int:
    d = json.loads(MAN.read_text(encoding="utf-8"))
    ver = d["version"]
    files = d["files10"]
    OUT.mkdir(parents=True, exist_ok=True)
    for name in TARGETS:
        meta = files.get(name)
        if not meta:
            print("清单里没有", name)
            continue
        want = int(meta["size"])
        dst = OUT / name
        part = dst  # 直接用目标名：.part 后缀在 curl 下会报 rc=23 写错误（实测）
        if dst.is_file() and dst.stat().st_size == want:
            print("已存在且尺寸正确：", name)
            continue
        url = f"{HOST}/{ver}/{name}"
        print(f"▶ {name}  {want/2**30:.2f} GB  ← {url}", flush=True)
        t0 = time.time()
        # 断点续传写到 .part
        args = ["curl", "-sS", "--fail", "-o", str(part), "-m", "7200",
                "-A", "Orbit/1.0", "-H", "X-NTES-PROJECT: 66"]
        if part.is_file() and part.stat().st_size > 0:
            args += ["-C", "-"]
        args.append(url)
        r = subprocess.run(args)
        got = part.stat().st_size if part.is_file() else 0
        if got == want:
            if dst.exists():
                dst.unlink()
            part.replace(dst)
            print(f"✓ {name} 完成 {got/2**30:.2f} GB 用时 {time.time()-t0:.0f}s", flush=True)
        else:
            print(f"✗ {name} 未完成：{got}/{want} rc={r.returncode}", flush=True)
    print("全部结束", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
