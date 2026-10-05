#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""跑三线台账的【慢判据】，结果落盘供主页读缓存。

用法：
    python 04_站点/web/tools/run_checks.py            # 跑慢判据并落盘
    python 04_站点/web/tools/run_checks.py --print    # 只打印，不落盘

## 为什么要把慢判据单独拿出来

主页端点每 15 秒被轮询一次，`collect()` 只跑得动毫秒级判据。
而「查询链实跑可用」「纹理能取出来解码」这类必须真跑命令，一次几秒到几十秒。
所以：
    gen_home.collect()  →  跑快速判据 + 读 CACHE_PATH（秒级）
    run_checks.py       →  跑慢判据，落 CACHE_PATH（由 cron 或人手动触发）

页面读到的是缓存值，会在条目后标「（慢判据，读缓存）」——不假装是实时的。
"""
from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
CACHE = Path(r"E:/la拆包项目") / "03_执行" / "10_索引" / "checks_cache.json"


def load_checks():
    spec = importlib.util.spec_from_file_location("_checks_runner", TOOLS / "checks.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main() -> int:
    mod = load_checks()
    print("== 慢判据 ==")
    res = mod.run_slow()
    bad = 0
    for name, v in res.items():
        mark = "✓" if v["ok"] else "✗"
        if not v["ok"]:
            bad += 1
        print(f"  {mark} {name}")
        print(f"      {v['label']}")
        print(f"      {v['detail']}")

    if "--print" in sys.argv:
        print("\n（--print：未落盘）")
        return 0

    payload = {
        "schema": "home-checks-cache-v1",
        "written_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "note": "由 tools/run_checks.py 生成；主页读此缓存，条目会标「慢判据，读缓存」",
        "checks": res,
    }
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  ✓ 已落盘 {CACHE}")
    print(f"    写入时间 {payload['written_at']}")
    print(f"    不通过的慢判据：{bad} 个")
    return 0


if __name__ == "__main__":
    sys.exit(main())
