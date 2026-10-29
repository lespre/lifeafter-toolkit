# -*- coding: utf-8 -*-
"""把 182 个 PE gpk 断点式推回模拟器（只推尺寸不符的）。"""
from __future__ import annotations

import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import SOURCE_PKG_ROOT  # noqa: E402

ADB = r"E:/leidian/LDPlayer14/adb.exe"
SRC = pathlib.Path(SOURCE_PKG_ROOT / "pe_gres_android")
DST = "/data/media/0/Android/data/com.netease.mrzh/files/netease/g66/Documents/gres"


def sh(cmd: str) -> str:
    r = subprocess.run([ADB, "shell", cmd], capture_output=True, text=True, errors="replace")
    return r.stdout


def main() -> int:
    sh("mkdir -p %s" % DST)
    remote = {}
    for line in sh("ls -l %s" % DST).splitlines():
        parts = line.split()
        if len(parts) >= 5 and parts[-1].endswith(".gpk"):
            try:
                remote[parts[-1]] = int(parts[4])
            except ValueError:
                pass
    todo = []
    for f in sorted(SRC.glob("*.gpk")):
        if remote.get(f.name) != f.stat().st_size:
            todo.append(f)
    print("远程已有 %d 个 ｜ 待推 %d 个 ｜ %.1f GB"
          % (len(remote), len(todo), sum(f.stat().st_size for f in todo) / 2 ** 30), flush=True)

    ok = fail = 0
    for i, f in enumerate(todo, 1):
        r = subprocess.run([ADB, "push", str(f), DST + "/"], capture_output=True)
        if r.returncode == 0:
            ok += 1
        else:
            fail += 1
            print("失败", f.name, r.stderr.decode(errors="replace")[:80], flush=True)
        if i % 10 == 0 or i == len(todo):
            print("[%d/%d] ok=%d fail=%d" % (i, len(todo), ok, fail), flush=True)
    print("完成 ok=%d fail=%d" % (ok, fail))
    print(sh("ls %s | wc -l" % DST))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
