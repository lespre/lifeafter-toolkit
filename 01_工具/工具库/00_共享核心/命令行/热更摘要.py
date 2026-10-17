# -*- coding: utf-8 -*-
r"""热更摘要：给**下一次会话开局**读的 15 行，替代「重新推导一遍」。

为什么要它（2026-10-17 复盘）：
  一波热更会消耗几小时，中间要读一堆 du/日志/manifest —— 这些原始输出全进上下文，
  下一波再干一遍就爆窗口。把**结论**外置成一个 JSON（几 KB），开局读它，
  就不必把历史输出留在对话里。

用法：
  热更摘要.py                     # 取 30_分析/热更检测 下最新的 RUN
  热更摘要.py <RUN目录>            # 指定
  热更摘要.py --json              # 机器读
优先级：RUN/STATE.json > 从 manifest.json + inventory.json 现算。
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

HOT = pathlib.Path(r"E:/la拆包项目/03_执行/30_分析/热更检测")


def latest_run() -> pathlib.Path | None:
    dirs = [d for d in HOT.iterdir() if d.is_dir() and not d.name.startswith("_")]
    if not dirs:
        return None
    return max(dirs, key=lambda d: d.stat().st_mtime)


def human(n: int | float | None) -> str:
    if n is None:
        return "-"
    return "%.2f GB" % (n / 1024 ** 3) if n > 1024 ** 2 else "%d B" % n


def build(run: pathlib.Path) -> dict:
    out: dict = {"run": str(run), "name": run.name}
    st = run / "STATE.json"
    if st.is_file():
        try:
            out.update(json.loads(st.read_text(encoding="utf-8")))
            out["_from"] = "STATE.json"
        except Exception as exc:                                # noqa: BLE001
            out["_state_error"] = str(exc)
    # 交付目录里若有 manifest/inventory，补关键数
    for cand in sorted(run.glob("交付_*")):
        mf = cand / "manifest.json"
        inv = cand / "04_变更清单与报告总结" / "inventory.json"
        if mf.is_file():
            try:
                d = json.loads(mf.read_text(encoding="utf-8"))
                out.setdefault("交付", {})
                out["交付"]["目录"] = str(cand)
                out["交付"]["条目"] = d.get("counts", {}).get("total") or len(d.get("entries") or [])
                out["交付"]["有名"] = d.get("counts", {}).get("named")
            except Exception:                                   # noqa: BLE001
                pass
        if inv.is_file():
            try:
                d = json.loads(inv.read_text(encoding="utf-8"))
                out.setdefault("交付", {})
                out["交付"]["盘上文件"] = d.get("total_files")
                out["交付"]["盘上体积"] = d.get("total_bytes")
            except Exception:                                   # noqa: BLE001
                pass
    out.setdefault("_from", "现算（无 STATE.json）")
    return out


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    run = pathlib.Path(args[0]) if args else latest_run()
    if not run or not run.is_dir():
        print("找不到 RUN 目录")
        return 2
    d = build(run)
    if "--json" in sys.argv:
        print(json.dumps(d, ensure_ascii=False, indent=1))
        return 0

    print("RUN        %s（摘要来源：%s）" % (d["name"], d.get("_from")))
    for k in ("批次", "时间", "来源", "基线", "一句话"):
        if d.get(k):
            print("%-10s %s" % (k, d[k]))
    jf = d.get("交付") or {}
    if jf:
        print("交付       %s" % jf.get("目录", "-"))
        print("           条目 %s ｜ 有名 %s ｜ 盘上 %s 文件 / %s"
              % (jf.get("条目"), jf.get("有名"), jf.get("盘上文件"), human(jf.get("盘上体积"))))
    if d.get("关键数"):
        for k, v in (d["关键数"] or {}).items():
            print("· %-22s %s" % (k, v))
    if d.get("待办"):
        print("待办：")
        for x in d["待办"]:
            print("   - %s" % x)
    if d.get("下一步"):
        print("下一步：")
        for i, x in enumerate(d["下一步"], 1):
            print("   %d. %s" % (i, x))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
