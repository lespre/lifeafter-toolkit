# -*- coding: utf-8 -*-
r"""生成「工具 × 段位」映射表（.md + .json）。

★ 这个文件是**薄壳**：段位定义与判据唯一处是
    `00_共享核心/toolkit_core/tool_seg_map.py`
  现场打印同一张表请用：`run_all.py map`（支持 --seg / --files / --json）。

判据（可核，不靠名字猜）——详见 tool_seg_map.CRITERION：
  产物下一站：下游解析器 → ① ｜ 人眼耳朵 → ② ｜ 浏览器 → ③
  上游导航 → 带H ｜ 接口口径 → 带D ｜ 闸门结论 → 带Q ｜ 不产业务产物 → 横切

用法：python 01_工具/工具库/docs/gen_tool_seg_map.py [--quiet]
"""
from __future__ import annotations

import sys
from pathlib import Path

for _stream in ("stdout", "stderr"):
    try:
        getattr(sys, _stream).reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

HERE = Path(__file__).resolve()                 # <工具库>/docs/gen_tool_seg_map.py
TK = HERE.parent.parent                         # <工具库>
CORE = TK / "00_共享核心"


def _bootstrap() -> None:
    for p in (CORE / "命令行", CORE):
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))


def main() -> int:
    _bootstrap()
    from toolkit_core import tool_seg_map as M
    try:
        from toolkit_cli import build_parser, commands_by_seg
        build_parser()                          # 从命令定义现场登记段位（不另抄一份）
        by_seg = commands_by_seg()
    except Exception as exc:                    # 命令层坏掉也要能出表
        print("⚠ 取 CLI 段位登记失败（表里 CLI 列会空）：%r" % (exc,), file=sys.stderr)
        by_seg = {}

    rows = M.collect(TK, include_archive=True)
    paths = M.write_artifacts(rows, TK / "docs", by_seg=by_seg)
    t = M.totals(rows)
    print("扫描 %d 个 .py（工具库 %d · 站点工具 %d）｜ 归档 %d ｜ 目录与段位不一致 %d ｜ 未分类 %d"
          % (t["total"], t["toolkit"], t["site"], t["archive"], t["dir_mismatch"],
             t["low_confidence"]))
    for k, v in paths.items():
        print("  → %s" % v)
    unknown = [r for r in rows if r["seg"] == "未分类"]
    if unknown:
        print("★ 有 %d 个文件没有命中任何判据（需人工定段）：" % len(unknown), file=sys.stderr)
        for r in unknown:
            print("    %s" % r["path"], file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
