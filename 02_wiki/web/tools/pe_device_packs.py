# -*- coding: utf-8 -*-
"""PE 设备包快照 / 差异（热更前后用）。

用法：
  python pe_device_packs.py --snapshot          # 记录设备当前 gpk 名单+大小
  python pe_device_packs.py --diff              # 与上次快照对比，列新增/变动/消失
  python pe_device_packs.py --diff --pull       # 并把新增/变动的包拉到 源包/pe_gres_android
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import re
import subprocess

ADB = "E:/leidian/LDPlayer14/adb.exe"
DEV = "/sdcard/Android/data/com.netease.mrzh/files/netease/g66/Documents/gres"
ROOT = pathlib.Path("E:/la拆包项目")
OUT = ROOT / "01_索引与产物/30_分析"
LOCAL = ROOT / "01_索引与产物/源包/pe_gres_android"


def ls_device() -> dict[str, int]:
    r = subprocess.run([ADB, "shell", f"ls -l {DEV}/*.gpk"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    out = {}
    for line in (r.stdout or "").splitlines():
        m = re.match(r"^[-\w]{10}\s+\d+\s+\S+\s+\S+\s+(\d+)\s+\S+\s+\S+\s+(\S+\.gpk)$", line.strip())
        if m:
            out[pathlib.Path(m.group(2)).name] = int(m.group(1))
    return out


def latest() -> pathlib.Path | None:
    c = sorted(OUT.glob("pe_device_packs_*.json"))
    return c[-1] if c else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", action="store_true")
    ap.add_argument("--diff", action="store_true")
    ap.add_argument("--pull", action="store_true")
    a = ap.parse_args()

    cur = ls_device()
    if not cur:
        print("设备上没读到 gpk，检查模拟器/路径")
        return 2
    total = sum(cur.values())
    print("设备 gpk %d 个 / %.1f GB" % (len(cur), total / 1e9))

    if a.snapshot:
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        p = OUT / f"pe_device_packs_{stamp}.json"
        p.write_text(json.dumps({"at": stamp, "count": len(cur), "total": total, "files": cur},
                                ensure_ascii=False, indent=1), encoding="utf-8")
        print("快照写出", p)
        return 0

    b = latest()
    if not b:
        print("没有历史快照，先 --snapshot")
        return 2
    old = json.loads(b.read_text(encoding="utf-8"))["files"]
    added = sorted(set(cur) - set(old))
    gone = sorted(set(old) - set(cur))
    changed = sorted(n for n in set(cur) & set(old) if cur[n] != old[n])
    print("对比 %s ｜ 新增 %d ｜ 变动 %d ｜ 消失 %d" % (b.name, len(added), len(changed), len(gone)))
    for label, names in (("新增", added), ("变动", changed), ("消失", gone)):
        if names:
            print("  %s %s%s" % (label, names[:10], " …" if len(names) > 10 else ""))

    if a.pull and (added or changed):
        LOCAL.mkdir(parents=True, exist_ok=True)
        for n in added + changed:
            subprocess.run([ADB, "pull", f"{DEV}/{n}", str(LOCAL / n)], capture_output=True)
        print("已拉取", len(added) + len(changed), "个包到", LOCAL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
