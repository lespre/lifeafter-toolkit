# -*- coding: utf-8 -*-
"""更新后：对比设备上的 gpk 与更新前基线，列出新增/变动/消失，供决定拉哪些包。

用法：
  python 02_wiki/web/tools/diff_device_packs.py            # 只对比（需模拟器在线）
  python 02_wiki/web/tools/diff_device_packs.py --pull     # 顺带把新增/变动的包拉到 源包/pe_gres_android
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path("E:/la拆包项目")
ADB = "E:/leidian/LDPlayer14/adb.exe"
DEV_DIR = "/sdcard/Android/data/com.netease.mrzh/files/netease/g66/Documents/gres"  # 设备侧 gpk 目录（可用 --dev-dir 覆盖）
LOCAL = ROOT / "01_索引与产物/源包/pe_gres_android"
BASE_DIR = ROOT / "01_索引与产物/30_分析"


def adb(*args: str) -> str:
    r = subprocess.run([ADB, *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout or ""


def latest_baseline() -> pathlib.Path | None:
    cands = sorted(BASE_DIR.glob("baseline_pe_before_update_*.json"))
    return cands[-1] if cands else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pull", action="store_true", help="拉取新增/变动的包")
    ap.add_argument("--dev-dir", default=DEV_DIR)
    a = ap.parse_args()

    b = latest_baseline()
    if not b:
        print("没有基线文件，先跑 snapshot_before_update.py")
        return 2
    base = {x["name"]: x for x in json.loads(b.read_text(encoding="utf-8"))["packages"]["files"]}
    print("基线：", b.name, "｜", len(base), "个包")

    out = adb("shell", f"ls -l {a.dev_dir}/*.gpk")
    if not out.strip():
        print("设备上没读到 gpk（模拟器没开 / 路径变了）：", a.dev_dir)
        return 2

    dev = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) < 8 or not parts[-1].endswith(".gpk"):
            continue
        try:
            size = int(parts[4])
        except ValueError:
            continue
        name = parts[-1].rsplit("/", 1)[-1]
        dev[name] = size
    print("设备：", len(dev), "个包")

    added = sorted(set(dev) - set(base))
    gone = sorted(set(base) - set(dev))
    changed = sorted(n for n in set(dev) & set(base) if dev[n] != base[n]["size"])
    print("新增 %d ｜ 变动 %d ｜ 消失 %d" % (len(added), len(changed), len(gone)))
    for label, names in (("新增", added), ("变动", changed), ("消失", gone)):
        if names:
            print(" ", label, names[:12], "…" if len(names) > 12 else "")

    if a.pull and (added or changed):
        LOCAL.mkdir(parents=True, exist_ok=True)
        for n in added + changed:
            dst = LOCAL / n
            print("  拉", n, "→", dst)
            subprocess.run([ADB, "pull", f"{a.dev_dir}/{n}", str(dst)], capture_output=True)
        print("完成，共拉", len(added) + len(changed), "个")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
