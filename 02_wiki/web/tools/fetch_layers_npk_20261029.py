# -*- coding: utf-8 -*-
"""按 CDN 清单单文件续传下载 res.layers.1.1*.npk（20261029 测试服版本）。

- curl -C - 断点续传；失败重试 5 次；每次比对本文件 size 与清单一致才算完成。
- 落到 01_索引与产物/源包/pe_npk_20261029/，不覆盖旧的 20261020 副本。
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import time

ROOT = pathlib.Path("E:/la拆包项目")
MAN = ROOT / "01_索引与产物/10_索引/cdn_20261031/npk_version_android4_playertest"
OUT = ROOT / "01_索引与产物/源包/pe_npk_20261029"
HOST = "https://g66.gph.netease.com"
LOG = ROOT / "01_索引与产物/源包/pe_npk_20261029/下载日志.txt"

TARGETS = [
    "res.layers.1.1.npk",
    "res.layers.1.1.1.npk",
    "res.layers.1.1.2.npk",
]


def log(msg: str) -> None:
    line = "%s  %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def main() -> int:
    man = json.loads(MAN.read_text(encoding="utf-8"))
    ver = man["version"]
    files = man["files10"]
    OUT.mkdir(parents=True, exist_ok=True)
    log("版本 %s ｜ 目标 %d 个文件" % (ver, len(TARGETS)))

    for rel in TARGETS:
        meta = files.get(rel) or {}
        want = int(meta.get("size") or 0)
        dst = OUT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        for attempt in range(1, 6):
            have = dst.stat().st_size if dst.is_file() else 0
            if want and have == want:
                log("✓ 已完成 %-28s %d B" % (rel, have))
                break
            log("→ %-28s 第%d次 已有 %.1f / %.1f MB" % (rel, attempt, have / 1e6, want / 1e6))
            cmd = [
                "curl", "-s", "--fail", "-C", "-", "-o", str(dst), "-m", "7200",
                "-A", "Orbit/1.0", "-H", "X-NTES-PROJECT: 66",
                "%s/%s/%s" % (HOST, ver, rel),
            ]
            r = subprocess.run(cmd)
            have = dst.stat().st_size if dst.is_file() else 0
            if want and have == want:
                log("✓ 完成 %-28s %d B" % (rel, have))
                break
            log("  rc=%d 现有 %.1f MB（期望 %.1f MB）" % (r.returncode, have / 1e6, want / 1e6))
            time.sleep(5)
        else:
            log("✗ 放弃 %s" % rel)

    log("全部任务结束")
    for rel in TARGETS:
        dst = OUT / rel
        log("  %-28s %s" % (rel, ("%.1f MB" % (dst.stat().st_size / 1e6)) if dst.is_file() else "缺失"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
