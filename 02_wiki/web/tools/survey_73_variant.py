# -*- coding: utf-8 -*-
"""普查：还原树里有多少表属于「0x73 变体」解不开，多少能解。

输出 01_索引与产物/30_分析/table_73_survey.json
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path("E:/la拆包项目")
CD = ROOT / "01_索引与产物/41_还原树/pe/配置/com/cdata"
OUT = ROOT / "01_索引与产物/30_分析/table_73_survey.json"
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_73 as B73  # noqa: E402


def main() -> int:
    ok, bad, not73 = [], [], 0
    files = sorted(CD.glob("*.py"))
    for p in files:
        try:
            head = p.open("rb").read(1)
        except OSError:
            continue
        if head != b"s":            # 不是 0x73 头
            not73 += 1
            continue
        try:
            body, meta = B73.extract_body(p.read_bytes())
            ok.append((p.name, len(body), meta.get("kind")))
        except Exception:          # noqa: BLE001
            bad.append((p.name, p.stat().st_size))
    print("总表 %d ｜ 非 0x73 头 %d ｜ 0x73 可解 %d ｜ 0x73 变体(解不开) %d"
          % (len(files), not73, len(ok), len(bad)))
    print("解不开的表（按大小前 12）：")
    for n, sz in sorted(bad, key=lambda x: -x[1])[:12]:
        print("   %-52s %6.1f KB" % (n, sz / 1024))
    OUT.write_text(json.dumps({"ok": ok, "variant_unresolved": bad},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    print("写出", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
