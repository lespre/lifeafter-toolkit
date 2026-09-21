# -*- coding: utf-8 -*-
"""明日之后拆包器统一命令行：索引优先、定点查询、定点提取。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from toolkit_core.paths import DEFAULT_OUTPUT_ROOT
from toolkit_core.unified_index import (
    AmbiguousMatch, IndexNotReady, UnifiedFileIndex, build_database, path_fid)

for _stream in ("stdout", "stderr"):
    try:
        getattr(sys, _stream).reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DB = DEFAULT_OUTPUT_ROOT / "indexes" / "lifeafter_files.sqlite3"
DEFAULT_FPK_INDEX = PROJECT_ROOT / "03拆包产物" / "fpk_fid_index.json"
DEFAULT_RES_ROOT = Path(r"E:\mrzh")


def _dump(value: object, destination: str | None = None) -> None:
    text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if destination:
        path = Path(destination).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"已写入：{path}")
    else:
        print(text, end="")


def _open(args) -> UnifiedFileIndex:
    return UnifiedFileIndex(args.db, res_root=getattr(args, "res_root", None))


def cmd_index_build(args) -> int:
    report = build_database(args.db, res_root=args.res_root, fpk_index=args.fpk_index,
                            include=args.include, progress=None if args.quiet else print)
    _dump(report, args.json)
    return 0 if not report["failures"] else 4


def cmd_index_status(args) -> int:
    try:
        with _open(args) as index:
            report = index.status(check_sources=not args.no_source_check)
    except IndexNotReady as exc:
        print(str(exc), file=sys.stderr); return 3
    _dump(report, args.json)
    if report["quick_check"] != "ok": return 4
    return 5 if report["stale"] is True else 0


def cmd_find(args) -> int:
    try:
        with _open(args) as index:
            result = index.find(args.path, variants=args.variants, deep=args.deep_variants)
    except (IndexNotReady, ValueError) as exc:
        print(str(exc), file=sys.stderr); return 3
    _dump(result.as_dict(), args.json)
    return 0 if result.hits else 5


def cmd_extract(args) -> int:
    try:
        with _open(args) as index:
            report = index.extract_path(
                args.path, args.output, container=args.container, row=args.row,
                variants=args.variants, deep=args.deep_variants,
                decode=not args.raw, overwrite=args.force)
    except AmbiguousMatch as exc:
        print(str(exc), file=sys.stderr); return 6
    except (IndexNotReady, KeyError, FileNotFoundError, ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr); return 5
    _dump(report, args.json)
    return 0


def cmd_verify(args) -> int:
    expected = {
        r"common\env_map\qiangpi.cube": 14213,
        r"common\env_map\car_studio01.cube": 12100,
        r"common\env_map\fashion_qiangpi.cube": 4620,
    }
    checks = []
    try:
        with _open(args) as index:
            status = index.status(check_sources=not args.no_source_check)
            for path, row in expected.items():
                fid = f"{path_fid(path):016X}"
                result = index.find(path)
                good = [h for h in result.hits if h.fid_hex == fid and h.row == row]
                checks.append({"path": path, "expected_fid": fid, "expected_row": row,
                               "pass": bool(good), "hits": [h.as_dict() for h in result.hits]})
    except IndexNotReady as exc:
        print(str(exc), file=sys.stderr); return 3
    report = {"pass": status["quick_check"] == "ok" and all(x["pass"] for x in checks),
              "status": status, "checks": checks,
              "note": "三条 ground truth 只验证路径键/索引链；不替代资产语义验收。"}
    _dump(report, args.json)
    return 0 if report["pass"] else 4


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lifeafter-toolkit",
        description="明日之后拆包器统一入口（文件索引优先；源包只读）")
    sub = parser.add_subparsers(dest="command", required=True)
    index = sub.add_parser("index", help="统一文件索引")
    index_sub = index.add_subparsers(dest="index_command", required=True)
    build = index_sub.add_parser("build", help="构建/原子更新 SQLite 索引")
    build.add_argument("--res-root", type=Path, default=DEFAULT_RES_ROOT)
    build.add_argument("--fpk-index", type=Path, default=DEFAULT_FPK_INDEX)
    build.add_argument("--db", type=Path, default=DEFAULT_DB)
    build.add_argument("--include", nargs="+", choices=("gpk", "fpk", "npk"), default=("gpk", "fpk", "npk"))
    build.add_argument("--quiet", action="store_true"); build.add_argument("--json")
    build.set_defaults(func=cmd_index_build)
    status = index_sub.add_parser("status", help="检查索引完整性与源包是否变化")
    status.add_argument("--db", type=Path, default=DEFAULT_DB); status.add_argument("--res-root", type=Path)
    status.add_argument("--no-source-check", action="store_true"); status.add_argument("--json")
    status.set_defaults(func=cmd_index_status)
    find = sub.add_parser("find", help="逻辑路径查全部物理候选")
    find.add_argument("path"); find.add_argument("--db", type=Path, default=DEFAULT_DB)
    find.add_argument("--res-root", type=Path); find.add_argument("--variants", action="store_true")
    find.add_argument("--deep-variants", action="store_true"); find.add_argument("--json")
    find.set_defaults(func=cmd_find)
    extract = sub.add_parser("extract", help="按索引定点提取一个条目")
    extract.add_argument("path"); extract.add_argument("output")
    extract.add_argument("--db", type=Path, default=DEFAULT_DB); extract.add_argument("--res-root", type=Path)
    extract.add_argument("--container", help="多命中时按容器路径子串筛选")
    extract.add_argument("--row", type=int, help="多命中时按原始条目号筛选")
    extract.add_argument("--variants", action="store_true"); extract.add_argument("--deep-variants", action="store_true")
    extract.add_argument("--raw", action="store_true", help="输出压缩载荷，不解码")
    extract.add_argument("--force", action="store_true", help="允许覆盖既有输出"); extract.add_argument("--json")
    extract.set_defaults(func=cmd_extract)
    verify = sub.add_parser("verify", help="SQLite + 三条已知路径端到端自检")
    verify.add_argument("--db", type=Path, default=DEFAULT_DB); verify.add_argument("--res-root", type=Path)
    verify.add_argument("--no-source-check", action="store_true"); verify.add_argument("--json")
    verify.set_defaults(func=cmd_verify)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
