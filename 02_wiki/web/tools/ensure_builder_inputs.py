#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ensure_builder_inputs.py — 审计并补齐 builder 的隐式输入（非 board 依赖）。

背景
----
`tools/*.py` 里有一批 builder 在读「中间产物」而不是 board：
``analysis/audit/p4a3_classify.json``、``analysis/audit/p4a3_sets.json``、
``data/boards/common_item_text_sources.json``、``config_work/<snapshot>/entries/*.bin`` …
这些文件不在 board 目录里，也不在 MANIFEST 里，所以清库/搬迁/换机后先挂的是 builder，
而且报错信息只说「文件不存在」，不说它该由谁产出。

两个子命令
----------
``scan``
    静态扫描 ``tools/*.py``，抽出「读取（read-side）路径字面量」，按四档标注：

    ======  ============================================================
    A       期望路径存在
    B       期望路径缺失，但仓库别处有同尾文件 → 可「恢复」（复制/硬链）
    X       同名但快照 id 不同 → 禁止恢复（会把别的快照灌进来）
    P       期望路径在 web 部署树之外 / web 前缀重复 → 脚本拼接缺陷，改脚本
    C       全仓库都没有 → 只能「重生」，需跑产出脚本
    U       路径由变量/参数拼出，静态推不出（人工看）
    ======  ============================================================

``ensure``
    只处理 B 档：把别处的同尾文件恢复（copy 默认，``--link`` 走硬链）到期望路径。
    默认 dry-run，``--apply`` 才落盘。**永不覆盖已存在的文件**，不碰任何 board，
    也不执行任何写 board 的产出脚本（C 档只打印建议命令）。

用法
----
    py -3 ensure_builder_inputs.py scan
    py -3 ensure_builder_inputs.py scan --json ../analysis/builder_inputs.json
    py -3 ensure_builder_inputs.py ensure                  # 只报告计划
    py -3 ensure_builder_inputs.py ensure --apply           # 真恢复
    py -3 ensure_builder_inputs.py ensure --apply --link    # 硬链（省磁盘）
    py -3 ensure_builder_inputs.py ensure --root <沙盒/web> --apply   # 沙盒演练

纪律
----
* 不写 board；不 import 任何 builder；不跑产出脚本。
* ``--root`` 指向沙盒时只影响期望路径的落点，扫描对象仍是真实 tools。
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import shutil
import sys
import warnings
from collections import Counter, defaultdict
from pathlib import Path

DEFAULT_WEB = Path(__file__).resolve().parents[1]
PROJECT = DEFAULT_WEB.parents[1] if len(DEFAULT_WEB.parents) > 1 else DEFAULT_WEB

PATHISH = re.compile(
    r"\.(json|jsonl|csv|md|txt|tsv|yaml|yml|db|sqlite|bin|dat|wav|ogg|mp3|png|jpg|zip|xlsx|docx)$",
    re.I,
)
# 写入/搬运上下文：这些行里的路径是产物，不是输入
WRITE_HINT = re.compile(
    r"write_text|write_bytes|json\.dump\(|['\"]w['\"]|['\"]a['\"]|\.mkdir|unlink"
    r"|shutil\.(copy|move)|savefig|imwrite|\.save\(|to_csv|to_excel|writerow"
)
OUT_HINT = re.compile(r"--out|DEFAULT_OUTPUT|^OUT =|\bOUT\b|_OUTPUT|--dst|--target")
TEMPLATE = re.compile(r"%s|%d|%\(|\{\w+\}")

# 允许「换根」的镜像目录：期望路径在这些地方找同尾文件
MIRROR_ROOTS = [
    PROJECT / "01_索引与产物" / "30_分析" / "site_analysis",
    PROJECT / "01_索引与产物" / "10_索引" / "site_data",
    PROJECT / "01_索引与产物" / "30_分析",
    PROJECT / "01_索引与产物",
]

# C 档（仓库内不存在）的产出脚本建议
PRODUCERS = {
    "common_item_text_sources.json": (
        "rebuild_common_item_text_sources.py --output data/boards/common_item_text_sources.json",
        "需 live_sources.json 里有 lifeafter-classic-current（当前缺，脚本内 COMPARISON_SOURCE_ID 写死）。"
        "现状：registry 只有 lifeafter-root-py314-full，直接跑会 ValueError。",
    ),
    "fashion_wardrobe_slots.json": (
        "rebuild_fashion_wardrobe_slots.py",
        "读 live_sources.json + fashion_wardrobe 板，重算槽位。",
    ),
    "weapon_attrs_schema_static.json": (
        "rebuild_weapon_attrs_schema_static.py",
        "由 weapon_attrs schema 静态段导出。",
    ),
    "recipe_book.json": ("build_recipe_board.py", "由还原树 recipe 表重建。"),
    "theme_talent_catalog.json": ("build_theme_talent.py", "由天赋表重建。"),
}


# --------------------------------------------------------------------------
# 静态求值：把 `ROOT / "analysis" / "audit"` 这类拼接还原成绝对路径
# --------------------------------------------------------------------------
def _normalize(p: str | None) -> str | None:
    if not p:
        return None
    s = str(p).replace("\\", "/")
    while "//" in s:
        s = s.replace("//", "/")
    # ROOT / "E:/abs/..." 的同盘符拼接：pathlib 会丢弃左值，这里同步该语义
    m = re.search(r"[A-Za-z]:/", s[2:])
    if m:
        s = s[2 + m.start():]
    # 折叠 ../（rebuild_wiki_v01 那类 WEB/"../01_索引与产物" 写法）
    if "/.." in s:
        s = os.path.normpath(s).replace("\\", "/")
    return s


def _eval(node: ast.AST, env: dict[str, str]) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        return env.get(node.id)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left, right = _eval(node.left, env), _eval(node.right, env)
        if left and right:
            try:
                return _normalize(str(Path(left) / right))
            except (OSError, ValueError):
                return None
        return None
    if isinstance(node, ast.Call):
        fname = getattr(node.func, "id", None)
        if fname in {"Path", "str"} and node.args:
            return _eval(node.args[0], env)
        attr = getattr(node.func, "attr", None)
        if attr == "resolve" and node.func.value is not None:
            return _eval(node.func.value, env)
        if attr == "parent" and node.func.value is not None:
            base = _eval(node.func.value, env)
            return _normalize(str(Path(base).parent)) if base else None
    if isinstance(node, ast.Attribute) and node.attr == "parent":
        base = _eval(node.value, env)
        return _normalize(str(Path(base).parent)) if base else None
    # Path(__file__).resolve().parents[1] —— 本项目 ROOT 的主流写法
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute):
        if node.value.attr == "parents":
            base = _eval(node.value.value, env)
            sl = node.slice
            idx = None
            if isinstance(sl, ast.Constant) and isinstance(sl.value, int):
                idx = sl.value
            if base is not None and idx is not None:
                parents = Path(base).parents
                if idx < len(parents):
                    return _normalize(str(parents[idx]))
    return None


# --------------------------------------------------------------------------
# scan
# --------------------------------------------------------------------------
def scan(tools: Path, web: Path) -> list[dict]:
    sites: list[dict] = []
    for py in sorted(tools.rglob("*.py")):
        if py.name == Path(__file__).name:
            continue
        try:
            src = py.read_text(encoding="utf-8", errors="replace")
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                tree = ast.parse(src)
        except (SyntaxError, OSError):
            continue
        env: dict[str, str] = {"__file__": str(py)}
        assign_paths: list[tuple[int, int, str]] = []
        for _ in range(3):  # 三轮传播，容忍 A = B / "x" 这类链式定义
            for node in ast.walk(tree):
                value = None
                target = None
                if isinstance(node, ast.Assign):
                    value, targets = _eval(node.value, env), node.targets
                elif isinstance(node, ast.AnnAssign) and node.value:
                    value, targets = _eval(node.value, env), [node.target]
                elif isinstance(node, ast.NamedExpr):
                    value, targets = _eval(node.value, env), [node.target]
                else:
                    continue
                if not value:
                    continue
                assign_paths.append((node.lineno, getattr(node, "end_lineno", node.lineno), value))
                for tgt in targets:
                    if isinstance(tgt, ast.Name):
                        env[tgt.id] = value

        lines = src.splitlines()
        write_lines = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
            if name in {
                "write_text", "write_bytes", "dump", "save", "savefig", "imwrite",
                "unlink", "mkdir", "copy", "copy2", "move", "to_csv", "to_excel",
                "writerow", "execute", "executemany",
            }:
                write_lines.add(node.lineno)
            if name == "open":
                mode = ""
                if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                    mode = str(node.args[1].value)
                for kw in node.keywords:
                    if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                        mode = str(kw.value.value)
                if any(c in mode for c in "wax"):
                    write_lines.add(node.lineno)

        for node in ast.walk(tree):
            if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
                continue
            raw = node.value
            if not PATHISH.search(raw) or len(raw) > 300 or "\n" in raw:
                continue
            if raw.startswith(("http://", "https://")) or "*" in raw or raw.startswith("."):
                continue
            # 单段 /xxx.json 是游戏客户端内路径或 URL 片段，不是本机文件
            if raw.startswith("/") or " " in raw:
                continue
            if TEMPLATE.search(raw):
                continue
            lineno = node.lineno
            ctx = lines[lineno - 1].strip() if lineno - 1 < len(lines) else ""
            # 字符串替换/文案映射里的路径不是读取
            if ".replace(" in ctx or '": "' in ctx:
                continue
            # 包内资源名（与 res\*.gpk 并列的 ui/... 小图）不是本机文件读取
            if not Path(raw).is_absolute() and (".gpk" in ctx or "res\\" in ctx):
                continue
            window = " ".join(lines[max(0, lineno - 2): lineno + 2])
            if lineno in write_lines or WRITE_HINT.search(window) or OUT_HINT.search(ctx):
                continue
            expected = None
            if Path(raw).is_absolute() or re.match(r"^[A-Za-z]:", raw):
                expected = _normalize(raw)
            elif "/" in raw or "\\" in raw:
                expected = _normalize(raw)
            else:
                # ① 同行 "Var / 'name'" 形态
                hit = re.search(r"([A-Za-z_]\w*)\s*/\s*[\"']" + re.escape(raw) + r"[\"']", ctx)
                if hit and hit.group(1) in env:
                    expected = _normalize(str(Path(env[hit.group(1)]) / raw))
                if not expected:
                    # ② 所在赋值语句整体可求值（如 SRC = ROOT/"analysis"/"audit"/"x.json"）
                    for lo, hi, val in assign_paths:
                        if lo <= lineno <= hi and Path(val).name == raw:
                            expected = val
                            break
                if not expected:
                    # ③ 常量先赋给变量、再用 "<Dir> / VAR" 拼接（BASE_ENTRY = "018005.bin"）
                    for var, val in env.items():
                        if val != raw:
                            continue
                        for m in re.finditer(r"([A-Za-z_]\w*)\s*/\s*" + re.escape(var) + r"\b", src):
                            base = env.get(m.group(1))
                            if base:
                                expected = _normalize(str(Path(base) / raw))
                                break
                        if expected:
                            break
            if expected and "/" not in expected and not Path(expected).is_absolute():
                expected = None  # 只剩裸文件名，说明目录基址没解出来 → 归 U，不臆造路径
            sites.append({
                "file": str(py.relative_to(web.parent)).replace("\\", "/"),
                "line": lineno,
                "raw": raw,
                "expected": expected,
                "rel_to_web": _rel_to_web(expected, web),
                "ctx": ctx[:160],
            })
    return sites


def _is_inside(path: Path, root: Path) -> bool:
    try:
        Path(path).resolve().relative_to(Path(root).resolve())
        return True
    except (ValueError, OSError):
        return False


def _rel_to_web(expected: str | None, web: Path) -> str | None:
    if not expected:
        return None
    s = str(expected).replace("\\", "/")
    root = str(web).replace("\\", "/")
    if s.startswith(root + "/"):
        return s[len(root) + 1:]
    return None


# --------------------------------------------------------------------------
# 镜像索引：给 B 档找「别处的同尾文件」
# --------------------------------------------------------------------------
def build_tail_index(mirrors: list[Path]) -> dict[tuple[str, ...], list[Path]]:
    index: dict[tuple[str, ...], list[Path]] = defaultdict(list)
    skip = {"__pycache__", ".git", "node_modules", "_重复副本30_分析", "90_临时"}
    for root in mirrors:
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or any(part in skip for part in path.parts):
                continue
            parts = path.parts
            for depth in (3, 2, 1):
                if len(parts) >= depth:
                    index[tuple(parts[-depth:])].append(path)
    return index


def find_twin(expected: str, index: dict[tuple[str, ...], list[Path]]) -> Path | None:
    parts = Path(expected.replace("\\", "/")).parts
    for depth in (3, 2, 1):
        if len(parts) < depth:
            continue
        key = tuple(parts[-depth:])
        cands = [c for c in index.get(key, []) if str(c).replace("\\", "/") != expected]
        if cands:
            # 同名多份时优先「样本/site_*」镜像，其次取路径最短的
            cands.sort(key=lambda p: (0 if any(s.startswith("site_") for s in p.parts) else 1, len(str(p))))
            return cands[0]
    return None


SNAPSHOT = re.compile(r"script_py314_docs_[0-9A-Za-z]+")


def _snapshot_of(path: str) -> str | None:
    m = SNAPSHOT.search(str(path))
    return m.group(0) if m else None


def _remap_target(expected: str, target_root: Path) -> Path:
    tgt = Path(expected)
    if tgt.is_absolute():
        rel = _rel_to_web(str(tgt), DEFAULT_WEB)
        # --root 指向沙盒时，把「真实 web 根下」的绝对路径重映射到沙盒
        if rel and target_root != DEFAULT_WEB:
            return target_root / rel
        return tgt
    # 相对路径：按 web → 项目根 → 01_索引与产物 依次取第一个存在的，否则落 web
    for cand in (target_root / expected, PROJECT / expected, PROJECT / "01_索引与产物" / expected):
        if cand.exists():
            return cand
    return target_root / expected


def classify(sites: list[dict], target_root: Path, index: dict[tuple[str, ...], list[Path]]) -> dict:
    # 先算每个 site 的目标路径，再按目标路径归并（同一文件的不同写法只算一行）
    per_site: dict[str, dict] = {}
    for s in sites:
        key = s["expected"] or f"~{s['raw']}"
        rec = per_site.setdefault(key, {"expected": s["expected"] or s["raw"], "target": None, "readers": set(),
                                        "sites": 0, "ctx": s["ctx"]})
        rec["readers"].add(Path(s["file"]).name)
        rec["sites"] += 1
        if s["expected"]:
            rec["target"] = _remap_target(s["expected"], target_root)

    by_target: dict[str, dict] = {}
    for key, rec in per_site.items():
        tkey = rec["target"] or key
        merged = by_target.setdefault(str(tkey), {"expected": rec["expected"], "target": rec["target"],
                                                 "readers": set(), "sites": 0, "ctx": rec["ctx"]})
        merged["readers"] |= rec["readers"]
        merged["sites"] += rec["sites"]

    rows = []
    for _, rec in by_target.items():
        expected, target = rec["expected"], rec["target"]
        tier, twin = "U", None
        if expected and target:
            if target.exists():
                tier = "A"
            else:
                twin = find_twin(expected if Path(expected).is_absolute() else str(target), index)
                if twin:
                    snap_e = _snapshot_of(str(target))
                    snap_t = _snapshot_of(str(twin))
                    if snap_t and snap_e != snap_t:
                        tier = "X"      # 同名不同快照（或期望路径丢失了快照段）：恢复会灌错数据
                    elif not _is_inside(target, target_root) or _rel_to_web(str(target), target_root) and \
                            _rel_to_web(str(target), target_root).startswith("01_索引与产物"):
                        tier = "P"      # web 内但前缀重复 / web 外：脚本路径拼接缺陷
                    else:
                        tier = "B"
                else:
                    tier = "C"
        rows.append({
            "expected": expected,
            "target": str(target).replace("\\", "/") if target else None,
            "tier": tier,
            "twin": str(twin).replace("\\", "/") if twin else None,
            "readers": sorted(rec["readers"]),
            "sites": rec["sites"],
            "ctx": rec["ctx"],
        })
    rows.sort(key=lambda r: ({"C": 0, "X": 1, "P": 2, "B": 3, "A": 4, "U": 5}[r["tier"]], r["expected"]))
    return {"rows": rows, "counts": Counter(r["tier"] for r in rows)}


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def cmd_scan(args) -> int:
    web = Path(args.root).resolve() if args.root else DEFAULT_WEB
    tools = DEFAULT_WEB / "tools"
    sites = scan(tools, DEFAULT_WEB)
    report = classify(sites, web, build_tail_index(MIRROR_ROOTS))
    counts = report["counts"]

    print(f"扫描 {len(sites)} 处读取路径字面量 → {len(report['rows'])} 个不同输入")
    print(f"  A 存在       {counts.get('A', 0)}")
    print(f"  B 可恢复     {counts.get('B', 0)}   ← ensure 处理这些")
    print(f"  X 快照不符   {counts.get('X', 0)}   ← 同名但快照不同，禁止恢复")
    print(f"  P 路径缺陷   {counts.get('P', 0)}   ← 脚本指向 web 外，改脚本而不是补文件")
    print(f"  C 需重生     {counts.get('C', 0)}")
    print(f"  U 静态不可解 {counts.get('U', 0)}")

    for tier, title in (("C", "C 档 · 全仓库缺失，需产出脚本"),
                        ("X", "X 档 · 同名不同快照（不要恢复）"),
                        ("P", "P 档 · 期望路径在 web 部署树之外（拼接缺陷）"),
                        ("B", "B 档 · 期望路径缺失，别处有同尾文件（可恢复）")):
        rows = [r for r in report["rows"] if r["tier"] == tier]
        if not rows:
            continue
        print(f"\n=== {title} ({len(rows)}) ===")
        for r in rows:
            print(f"[{tier}] {r['expected']}")
            print(f"     readers: {', '.join(r['readers'][:6])}{' …' if len(r['readers']) > 6 else ''}")
            if r["twin"]:
                print(f"     twin   : {r['twin']}")
            if tier == "C":
                name = Path(r["expected"]).name
                if name in PRODUCERS:
                    cmd, note = PRODUCERS[name]
                    print(f"     produc : {cmd}")
                    print(f"     note   : {note}")

    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({k: (dict(v) if isinstance(v, Counter) else v)
                                   for k, v in report.items()}, ensure_ascii=False, indent=1),
                       encoding="utf-8")
        print(f"\nJSON → {out}")
    return 0


def cmd_ensure(args) -> int:
    web = Path(args.root).resolve() if args.root else DEFAULT_WEB
    tools = DEFAULT_WEB / "tools"
    sites = scan(tools, DEFAULT_WEB)
    report = classify(sites, web, build_tail_index(MIRROR_ROOTS))
    todo = [r for r in report["rows"] if r["tier"] == "B" and r["target"]]

    mode = "硬链" if args.link else "复制"
    print(f"{'APPLY' if args.apply else 'DRY-RUN'} · 目标根 {web} · 方式 {mode}")
    print(f"B 档待恢复 {len(todo)} 个\n")

    done = skipped = failed = 0
    for r in todo:
        target = Path(r["target"])
        twin = Path(r["twin"])
        if target.exists():
            print(f"skip  已存在 {target}")
            skipped += 1
            continue
        if not args.apply:
            print(f"plan  {twin}\n   -> {target}")
            continue
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            if args.link:
                try:
                    os.link(twin, target)
                except OSError:
                    shutil.copy2(twin, target)
            else:
                shutil.copy2(twin, target)
            ok = target.exists() and target.stat().st_size == twin.stat().st_size
            print(f"{'ok   ' if ok else 'BAD  '} {target} ({target.stat().st_size if target.exists() else 0} B)")
            done += 1 if ok else 0
            failed += 0 if ok else 1
        except OSError as exc:
            print(f"fail  {target}: {exc}")
            failed += 1

    c_rows = [r for r in report["rows"] if r["tier"] == "C"]
    x_rows = [r for r in report["rows"] if r["tier"] == "X"]
    if x_rows:
        print(f"\nX 档（同名不同快照，禁止恢复）{len(x_rows)} 个：")
        for r in x_rows:
            print(f"  - {r['expected']}")
            print(f"      同名但快照不同: {r['twin']}")
    p_rows = [r for r in report["rows"] if r["tier"] == "P"]
    if p_rows:
        print(f"\nP 档（路径拼接缺陷，本脚本不补；改脚本即可）{len(p_rows)} 个：")
        for r in p_rows[:12]:
            print(f"  - {r['expected']}")
            print(f"      真实位置: {r['twin']}")
        if len(p_rows) > 12:
            print(f"  … 另 {len(p_rows) - 12} 个")
    if c_rows:
        print(f"\nC 档（本脚本不处理，需产出脚本）{len(c_rows)} 个：")
        for r in c_rows:
            name = Path(r["expected"]).name
            hint = PRODUCERS.get(name, (None, None))
            print(f"  - {r['expected']}")
            if hint[0]:
                print(f"      → {hint[0]}")
    if args.apply:
        print(f"\n完成 {done} / 跳过 {skipped} / 失败 {failed}")
    return 0 if failed == 0 else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="审计并补齐 builder 的隐式输入（非 board 依赖）")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("scan", help="静态扫描读取侧输入并分档")
    sp.add_argument("--root", help="期望路径落点（默认 web 根）")
    sp.add_argument("--json", help="把扫描结果写到该 JSON")
    sp.set_defaults(func=cmd_scan)

    ep = sub.add_parser("ensure", help="恢复 B 档输入（默认 dry-run）")
    ep.add_argument("--root", help="期望路径落点（默认 web 根；沙盒演练用）")
    ep.add_argument("--apply", action="store_true", help="真正落盘")
    ep.add_argument("--link", action="store_true", help="用硬链代替复制")
    ep.set_defaults(func=cmd_ensure)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
