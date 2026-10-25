# -*- coding: utf-8 -*-
"""清理站点与仓库根目录的无用文件（备份 / 探针 / 旧页面 / 设计稿截图）。

只删确定没被线上页面引用的东西，删完打印清单。
"""
from __future__ import annotations

import pathlib
import shutil

ROOT = pathlib.Path("E:/la拆包项目")
WEB = ROOT / "02_wiki/web"

FILES = [
    ROOT / "la.py.bak_layer",
    WEB / "board.html.bak_media",
    WEB / "wiki.html.bak_arch",
    WEB / "wiki.html.bak_brand",
    WEB / "spine_view.html.bak_20261024",
    WEB / "wiki_旧_20261022.html",
    WEB / "_probe.html",
    WEB / "_audio_probe_test.html",
    WEB / "_perf_probe_test.html",
]

DIRS = [
    ROOT / "scratch_dl",
    ROOT / "__pycache__",
    WEB / ".pytest_cache",
]


def main() -> int:
    removed = []
    for f in FILES:
        if f.is_file():
            size = f.stat().st_size
            f.unlink()
            removed.append((f.name, size / 1024, "file"))
    for d in DIRS:
        if d.is_dir():
            total = sum(p.stat().st_size for p in d.rglob("*") if p.is_file())
            shutil.rmtree(d)
            removed.append((d.name + "/", total / 1024 / 1024, "dir"))

    # 设计稿里的大截图（mockup PNG，非线上资源）
    ddir = WEB / "design"
    png = 0
    png_mb = 0.0
    if ddir.is_dir():
        for p in ddir.rglob("*.png"):
            png_mb += p.stat().st_size / 1024 / 1024
            p.unlink()
            png += 1
        removed.append(("design/**/*.png", png_mb, "png×%d" % png))

    print("已删除 %d 项：" % len(removed))
    for name, size, kind in removed:
        unit = "MB" if kind in ("dir",) or kind.startswith("png") else "KB"
        print("  %-32s %8.1f %s  (%s)" % (name, size, unit, kind))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
