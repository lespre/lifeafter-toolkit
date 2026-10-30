# -*- coding: utf-8 -*-
"""等 PC 热更收尾后自动抓包 + 解表（v2：占用重试、以复制结果为准）。"""
from __future__ import annotations

import pathlib
import shutil
import subprocess
import time

NPK = pathlib.Path("E:/mrzh/Documents/script.py314.lc.npk")
PY = r"E:/la拆包项目/00_规范与工具/环境/venv/Scripts/python.exe"
TOOLS = pathlib.Path("E:/la拆包项目/02_wiki/web/tools")
TMP = pathlib.Path("C:/Users/Administrator/AppData/Local/hermes/cache/scratch/pc_npk_probe.bin")
MAX_WAIT = 5400


def snapshot_ok() -> tuple[bool, int, float]:
    """能完整复制一份出来 = 未被独占。返回 (ok, size, mtime)。"""
    try:
        shutil.copy2(NPK, TMP)
        st = NPK.stat()
        return True, st.st_size, st.st_mtime
    except Exception:
        return False, 0, 0.0


def main() -> int:
    t0 = time.time()
    last = None
    stable_since = None
    while time.time() - t0 < MAX_WAIT:
        ok, size, mt = snapshot_ok()
        if ok:
            if (size, mt) != last:
                last = (size, mt)
                stable_since = time.time()
                print("可复制，size=%d，观察稳定性…" % size, flush=True)
            elif time.time() - stable_since >= 120:
                print("稳定 120s，开始抓包", flush=True)
                rc = subprocess.run([PY, str(TOOLS / "capture_pc_hotfix.py"), "--copy"]).returncode
                print("capture rc=%d" % rc, flush=True)
                dst_ok, dst_size, _ = True, size, 0
                newest = sorted((pathlib.Path("E:/la拆包项目/01_索引与产物/源包/pc_hotfix")).glob("*/script.py314.lc.npk"))
                if newest and newest[-1].stat().st_size == size:
                    print("抓到的包大小一致：%d" % size, flush=True)
                    rc2 = subprocess.run([PY, str(TOOLS / "extract_pc_hotfix_tables.py")]).returncode
                    print("extract rc=%d" % rc2, flush=True)
                    return rc2
                print("抓到的包大小不一致，继续等", flush=True)
                stable_since = time.time()
        else:
            print("文件被占用（客户端在跑），等 30s", flush=True)
            last = None
        time.sleep(30)
    print("等待超时", flush=True)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
