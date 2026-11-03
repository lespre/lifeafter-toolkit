# -*- coding: utf-8 -*-
"""读 PE 客户端热更状态（从雷电 adb 拉下来的 local_state）。

输出：版本信息 + 本次 overlay 覆盖包清单（名字/大小/族）。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJ = Path(r"E:\la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import patch_overlay as PO  # noqa: E402

ROOT = PROJ / "90_临时/pe_client"


def main() -> int:
    state = PO.read_client_state(ROOT)
    vi = state.get("version_info") or {}
    print("顶层键", sorted(state)[:12])
    for k in ("line", "server_kind", "version", "cdn_dir", "revision", "version_vs_cdn"):
        if k in vi:
            print(f"  {k}: {vi[k]}")
    ov = PO.overlay_list(state)
    pkgs = ov.get("packages") or []
    print("overlay 时间戳", ov.get("timestamp"), "| 包数", len(pkgs))
    total = sum(p.get("size") or 0 for p in pkgs)
    print(f"合计 {total/1024/1024:.1f} MB")
    from collections import Counter
    print("按族", Counter(p.get("family") for p in pkgs).most_common(8))
    for p in sorted(pkgs, key=lambda x: -(x.get("size") or 0))[:12]:
        print(f"  {p.get('name')}  {(p.get('size') or 0)/1024/1024:.1f} MB  {p.get('family')}")
    out = PROJ / "01_索引与产物/30_分析/pe_hotfix_overlay.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ov, ensure_ascii=False, indent=1), encoding="utf-8")
    print("写出", out.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
