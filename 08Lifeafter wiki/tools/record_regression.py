"""记录一次**真实**回归结果到 state/REGRESSION.json（不伪造任何数字）。

用法：
    python tools/record_regression.py                      # 自己跑全量测试再记录
    python tools/record_regression.py --from .tmp_reg.txt   # 解析已有输出（不重跑）
    python tools/record_regression.py --from x.txt --exit-code 0

解析自真实 unittest 输出（-q）：
    "Ran N tests in Xs"
    "OK" / "OK (expected failures=K)" / "FAILED (failures=F, errors=E[, expected failures=K])"

写入字段（v1.3 冻结口径，向后兼容旧键）：
    at / commit / base / total_tests / passed / failures / errors /
    expected_failures / exit_code / status / result / tests / command
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "state" / "REGRESSION.json"
DEFAULT_CMD = "python -m unittest discover -s tests -q"
SUMMARY = re.compile(r"^Ran (\d+) tests? in ", re.M)
OK = re.compile(r"^OK(?: \((.*?)\))?\s*$", re.M)
FAILED = re.compile(r"^FAILED \((.*?)\)\s*$", re.M)


def _git(*args: str) -> str:
    try:
        r = subprocess.run(["git", *args], cwd=str(REPO), capture_output=True, text=True, timeout=60)
        return r.stdout.strip()
    except Exception:  # noqa: BLE001
        return ""


def parse(text: str, exit_code: int | None, command: str) -> dict:
    m = SUMMARY.search(text)
    total = int(m.group(1)) if m else 0
    ok = OK.search(text)
    bad = FAILED.search(text)
    failures = errors = expected_failures = 0
    if bad:
        detail = bad.group(1)
        f = re.search(r"failures=(\d+)", detail)
        e = re.search(r"errors=(\d+)", detail)
        x = re.search(r"expected failures=(\d+)", detail)
        failures = int(f.group(1)) if f else 0
        errors = int(e.group(1)) if e else 0
        expected_failures = int(x.group(1)) if x else 0
        status = "FAILED"
        exit_code = 1 if exit_code is None else exit_code
    elif ok:
        x = re.search(r"expected failures=(\d+)", ok.group(1) or "")
        expected_failures = int(x.group(1)) if x else 0
        status = "OK"
        exit_code = 0 if exit_code is None else exit_code
    else:
        status = "UNKNOWN"
        exit_code = -1 if exit_code is None else exit_code
    passed = max(0, total - failures - errors)
    commit = _git("rev-parse", "--short", "HEAD")
    return {
        # v1.3 冻结口径
        "at": __import__("datetime").datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "commit": commit,
        "base": "workbench v1.3 (api-first paginated web client)",
        "total_tests": total,
        "passed": passed,
        "failures": failures,
        "errors": errors,
        "expected_failures": expected_failures,
        "exit_code": exit_code,
        "status": status,
        # 向后兼容（coverage_service / 状态页读这些键）
        "tests": total,
        "result": status,
        "command": command,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", help="解析已有输出文件（不重跑）")
    ap.add_argument("--exit-code", type=int, default=None)
    ap.add_argument("--command", default=DEFAULT_CMD)
    args = ap.parse_args()

    exit_code = args.exit_code
    if args.src:
        text = Path(args.src).read_text(encoding="utf-8", errors="ignore")
    else:
        proc = subprocess.run(args.command.split(), cwd=str(REPO), capture_output=True,
                              text=True, encoding="utf-8", timeout=3600)
        text = (proc.stdout or "") + (proc.stderr or "")
        exit_code = proc.returncode if exit_code is None else exit_code
    doc = parse(text, exit_code, args.command)
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(doc, ensure_ascii=False, indent=1))
    return 0 if doc["status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
