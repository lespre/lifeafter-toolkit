#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""portability_audit.py — 路径可移植性体检

开源目标：别人 clone 仓库后，用**自己设备**的拆包产物能构建出一样的 wiki。
⇒ 脚本里不能写死「我这台机器的绝对路径」。

体检两类硬编码：
  A. 指向项目自身的绝对路径（E:/la拆包项目/...）
     → 换机/换目录即失效。可机械改写为「从仓库根推导」。
  B. 指向本机设备的绝对路径（E:/mrzh、E:/LifeAfter、C:/Users/...）
     → 属于「运行期输入」，必须走环境变量/参数（如 LA_CLIENT_ROOT），
     写死则换设备必崩。

同时识别「已用可移植写法」的文件（__file__ 推导 / 环境变量）作为正面样本。

用法:
  python 02_wiki/web/tools/checks/portability_audit.py            # 全量体检 + 写 state/portability.json
  python 02_wiki/web/tools/checks/portability_audit.py --top 30   # 列出问题最多的文件
  python 02_wiki/web/tools/checks/portability_audit.py --scope tools   # 只查 02_wiki/web/tools
  python 02_wiki/web/tools/checks/portability_audit.py --check     # 门禁模式：有硬编码则 exit 1

退出码: 0 干净 / 1 存在硬编码 / 2 配置异常
"""
from __future__ import annotations

import argparse
import ast
import json
import pathlib
import re
import sys
from collections import Counter

PROJ = pathlib.Path(__file__).resolve().parents[4]
WEB = PROJ / "02_wiki" / "web"
TOOLS = WEB / "tools"
RULES = PROJ / "02_wiki" / "rules"
STATE = PROJ / "02_wiki" / "state"

# 本机项目根与设备路径（按当前机器实际情况登记；换机器时改这里即可）
PROJECT_ROOT_PAT = re.compile(r"[A-Za-z]:[\\/]la拆包项目")
DEVICE_PAT = re.compile(r"[A-Za-z]:[\\/](?:mrzh|LifeAfter|Users)[\\/]?")
# 可移植写法标志
PORTABLE_PAT = re.compile(r"__file__|LA_ROOT|LA_CLIENT_ROOT|parents\[\d+\]|"
                          r"toolkit_core\.paths|from\s+la_paths|import\s+la_paths")
# 明显不是路径的误报排除（URL、协议前缀）
NOT_PATH = re.compile(r"^[a-z]+://|^[a-z]:[\\/]{2}|gph\.netease|w3\.org")

SCOPES = {
    "tools": [TOOLS],
    "toolkit": [PROJ / "00_规范与工具" / "工具" / "工具库"],
    "root": [PROJ],
}


def iter_py(dirs):
    seen = set()
    for d in dirs:
        if not d.exists():
            continue
        for p in d.rglob("*.py"):
            if any(x in p.parts for x in ("__pycache__", "_archive", "venv", ".git")):
                continue
            rp = p.resolve()
            if rp in seen:
                continue
            seen.add(rp)
            yield p


def scan_file(p: pathlib.Path) -> dict:
    src = p.read_text(encoding="utf-8", errors="ignore")
    lines = src.splitlines()
    proj_hits: list[int] = []
    dev_hits: list[int] = []
    for i, ln in enumerate(lines, 1):
        # 注释行不算（注释里的路径只是说明）
        stripped = ln.strip()
        if stripped.startswith("#"):
            continue
        for m in PROJECT_ROOT_PAT.finditer(ln):
            if NOT_PATH.match(m.group(0)):
                continue
            proj_hits.append(i)
            break
        else:
            for m in DEVICE_PAT.finditer(ln):
                if NOT_PATH.match(m.group(0)):
                    continue
                dev_hits.append(i)
                break
    portable = bool(PORTABLE_PAT.search(src))
    try:
        ast.parse(src)
    except SyntaxError:
        pass
    return {
        "path": str(p.relative_to(PROJ)).replace("\\", "/"),
        "project_abs": len(proj_hits),
        "device_abs": len(dev_hits),
        "portable_marker": portable,
        "lines": proj_hits[:20] + dev_hits[:20],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="路径可移植性体检")
    ap.add_argument("--scope", default="tools", choices=sorted(SCOPES) + ["all"])
    ap.add_argument("--top", type=int, default=20, help="列出问题最多的前 N 个文件")
    ap.add_argument("--check", action="store_true", help="门禁模式：存在硬编码则 exit 1")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    dirs = []
    if args.scope == "all":
        for v in SCOPES.values():
            dirs.extend(v)
    else:
        dirs = SCOPES[args.scope]

    rows = []
    for p in iter_py(dirs):
        rows.append(scan_file(p))

    bad = [r for r in rows if r["project_abs"] or r["device_abs"]]
    bad.sort(key=lambda r: -(r["project_abs"] + r["device_abs"]))
    clean = [r for r in rows if not (r["project_abs"] or r["device_abs"])]

    total_proj = sum(r["project_abs"] for r in rows)
    total_dev = sum(r["device_abs"] for r in rows)
    report = {
        "scope": args.scope,
        "files_scanned": len(rows),
        "files_clean": len(clean),
        "files_with_hardcoded": len(bad),
        "project_abs_sites": total_proj,
        "device_abs_sites": total_dev,
        "portable_ratio": round(len(clean) * 100.0 / len(rows), 1) if rows else 100.0,
        "files": sorted(bad, key=lambda r: r["path"]),
    }
    STATE.mkdir(parents=True, exist_ok=True)
    (STATE / "portability.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    if not args.quiet:
        print(f"扫描 {report['files_scanned']} 个 py（scope={args.scope}）")
        print(f"  含硬编码：{report['files_with_hardcoded']} 个文件"
              f"（项目自身 {total_proj} 处 / 本机设备 {total_dev} 处）")
        print(f"  可移植：{report['files_clean']} 个文件（{report['portable_ratio']}%）")
        if bad:
            print(f"\n问题最多的文件（前 {args.top}）：")
            print(f"{'文件':66s} {'项目':>4s} {'设备':>4s}")
            print("-" * 78)
            for r in bad[:args.top]:
                print(f"{r['path'][:66]:66s} {r['project_abs']:>4d} {r['device_abs']:>4d}")
        print(f"\n报告已写入 {STATE / 'portability.json'}")

    if args.check and bad:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
