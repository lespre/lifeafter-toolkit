# -*- coding: utf-8 -*-
"""等 PC 热更收尾后自动抓包 + 解表。

条件：script.py314.lc.npk 可读（没被客户端占用）且 90 秒内 size/mtime 不变。
然后依次跑 capture_pc_hotfix.py --copy 和 extract_pc_hotfix_tables.py。
"""
from __future__ import annotations

import subprocess
import sys
import time
import pathlib

NPK = pathlib.Path("E:/mrzh/Documents/script.py314.lc.npk")
PY = r"E:/la拆包项目/00_规范与工具/环境/venv/Scripts/python.exe"
TOOLS = pathlib.Path("E:/la拆包项目/02_wiki/web/tools")
MAX_WAIT = 3600


def readable(p: pathlib.Path) -> bool:
    try:
        with p.open("rb") as fh:
            fh.read(4096)
        return True
    except Exception:
        return False


def sig(p: pathlib.Path):
    st = p.stat()
    return st.st_size, st.st_mtime_ns


def main() -> int:
    t0 = time.time()
    last = None
    stable_since = None
    while time.time() - t0 < MAX_WAIT:
        if readable(NPK):
            cur = sig(NPK)
            if cur != last:
                last = cur
                stable_since = time.time()
                print("可读，size=%d，观察稳定性…" % cur[0], flush=True)
            elif time.time() - stable_since >= 90:
                print("文件稳定 90s，开始抓包", flush=True)
                rc = subprocess.run([PY, str(TOOLS / "capture_pc_hotfix.py"), "--copy"]).returncode
                print("capture rc=%d" % rc, flush=True)
                rc2 = subprocess.run([PY, str(TOOLS / "extract_pc_hotfix_tables.py")]).returncode
                print("extract rc=%d" % rc2, flush=True)
                return rc2
        else:
            print("文件被占用，等 30s", flush=True)
            last = None
        time.sleep(30)
    print("等待超时（1 小时），未抓到", flush=True)
    return 2


if __name__ == "__main__":
    sys.exit(main())
