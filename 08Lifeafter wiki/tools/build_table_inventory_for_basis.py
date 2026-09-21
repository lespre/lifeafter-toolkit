# -*- coding: utf-8 -*-
"""A2：为**指定工作副本**建基线内的表清单（table inventory，含 FID）。

与 `tools/build_table_index.py` 同一套扫描规则（不解释语义）：
  co_filename = 条目内嵌字面 `com\\cdata\\<X>.py` 且其后 40B 内邻接 `<module>`（= 自身模块路径）
  table_body  = 存在合法 `x{` 容器（blen<=len, 0<cnt<2e6, reserved=0）
  merge_shell = 含 MergedTableData / SplitTableData 字面
  role/family = 文件名后缀字符串规则（_base/_chs/_inc/_del/_merged）

与旧清单的区别（本工具的目的）：
  * 逐条附 `file_id`（取自同目录 manifest.json 的 entries[]）——v1.2 跨基准定位要按 FID 对齐
  * 显式写 `snapshot_id` + `entry_basis`，声明「entry 序号只在本基准内有效」

输出（默认）：data/table_index_entries_<sha8>.jsonl  +  data/table_index_<sha8>.summary.json
用法：python tools/build_table_inventory_for_basis.py --workcopy <dir> --snapshot-id <id> [--sha8 328b8446]
"""
from __future__ import annotations

import argparse
import json
import os
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CDATA = b"com" + bytes([92]) + b"cdata" + bytes([92])
MODULE_TAG = b"<module>"
XOPEN = b"x{"
ROLE_SUFFIXES = ("_base", "_chs", "_inc", "_del", "_merged")

_ENTRIES_DIR: Path | None = None


def _init_worker(entries_dir: str) -> None:
    """Windows 是 spawn：子进程必须自建全局（模块级变量不会继承）。"""
    global _ENTRIES_DIR
    _ENTRIES_DIR = Path(entries_dir)


def find_cdata_paths(data: bytes) -> list[str]:
    out, start = [], 0
    while True:
        i = data.find(CDATA, start)
        if i < 0:
            break
        j = i
        while j < len(data) and (data[j:j + 1].isalnum() or data[j:j + 1] in (b"\\", b"_", b".")):
            j += 1
        chunk = data[i:j]
        if chunk.endswith(b".py") and len(chunk) < 200:
            try:
                out.append(chunk.decode("utf-8"))
            except UnicodeDecodeError:
                pass
        start = j if j > i else i + 1
    return out


def has_x_container(data: bytes) -> bool:
    pos = 0
    while True:
        at = data.find(XOPEN, pos)
        if at < 0:
            return False
        if at + 18 <= len(data):
            blen = int.from_bytes(data[at + 2:at + 6], "little")
            cnt = int.from_bytes(data[at + 6:at + 10], "little")
            res = int.from_bytes(data[at + 10:at + 14], "little")
            if res == 0 and 0 < cnt < 2_000_000 and blen <= len(data):
                return True
        pos = at + 2


def role_of(basename: str) -> tuple[str, str]:
    stem = basename[:-3] if basename.endswith(".py") else basename
    roles, changed = [], True
    while changed:
        changed = False
        for suf in ROLE_SUFFIXES:
            if stem.endswith(suf):
                roles.append(suf[1:])
                stem = stem[: -len(suf)]
                changed = True
                break
    if not roles:
        return stem, "plain"
    return stem, roles[0]


def _process(fn: str) -> dict:
    d = (_ENTRIES_DIR / fn).read_bytes()            # type: ignore[operator]
    paths = find_cdata_paths(d)
    co_name = None
    for p in paths:
        i = d.find(p.encode("utf-8"))
        j = i + len(p.encode("utf-8")) if i >= 0 else i
        if i >= 0 and MODULE_TAG in d[j:j + 40]:
            co_name = p
            break
    return {
        "entry": int(fn[:6]),
        "size": len(d),
        "co_filename": co_name,
        "table_body": has_x_container(d),
        "merge_shell": (b"MergedTableData" in d or b"SplitTableData" in d),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workcopy", required=True)
    ap.add_argument("--snapshot-id", required=True)
    ap.add_argument("--sha8", required=True)
    a = ap.parse_args()

    global _ENTRIES_DIR
    wc = Path(a.workcopy)
    _ENTRIES_DIR = wc / "entries"
    man = json.loads((wc / "manifest.json").read_text(encoding="utf-8"))
    fid_of = {e["index"]: e.get("file_id") for e in man["entries"]}
    files = sorted(f.name for f in _ENTRIES_DIR.iterdir() if f.suffix == ".bin")
    n_expect = man["summary"]["entry_count"]
    assert len(files) == n_expect, f"entries 文件数 {len(files)} != manifest {n_expect}"

    workers = min(12, (os.cpu_count() or 4))
    with ProcessPoolExecutor(max_workers=workers, initializer=_init_worker,
                             initargs=(str(_ENTRIES_DIR),)) as ex:
        recs = list(ex.map(_process, files, chunksize=64))
    recs.sort(key=lambda r: r["entry"])

    out_rows = []
    fam: dict[str, Counter] = {}
    for r in recs:
        row = {
            "snapshot_id": a.snapshot_id,
            "entry_basis": f"{a.snapshot_id}:package-native",
            "client_channel": "test",
            "package": "Documents/script.py314.lc.npk",
            "entry": r["entry"],
            "file_id": fid_of.get(r["entry"]),
            "table_name": None,
            "family": None,
            "role": None,
            "evidence": "none",
            "table_body": r["table_body"],
            "merge_shell": r["merge_shell"],
            "size": r["size"],
        }
        if r["co_filename"]:
            row["table_name"] = r["co_filename"]
            fam_name, role = role_of(r["co_filename"].split("\\")[-1])
            row["family"], row["role"], row["evidence"] = fam_name, role, "co_filename"
            fam.setdefault(fam_name, Counter())[role] += 1
        elif r["merge_shell"]:
            row["evidence"], row["role"] = "merge_shell", "merge_shell"
        out_rows.append(row)

    OUT = ROOT / "data" / f"table_index_entries_{a.sha8}.jsonl"
    with OUT.open("w", encoding="utf-8", newline="\n") as f:
        for r in out_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    summary = {
        "schema_version": 1,
        "snapshot_id": a.snapshot_id,
        "entry_basis": f"{a.snapshot_id}:package-native",
        "workcopy": str(wc),
        "source": man.get("source"),
        "source_unchanged": man.get("source_unchanged"),
        "entry_count": len(out_rows),
        "named": sum(1 for r in out_rows if r["table_name"]),
        "table_body": sum(1 for r in out_rows if r["table_body"]),
        "merge_shell": sum(1 for r in out_rows if r["merge_shell"]),
        "family_count": len(fam),
        "note": "entry 序号只在本 snapshot 的 package-native 基准内有效；FID 用于跨基准对齐",
    }
    (ROOT / "data" / f"table_index_{a.sha8}.summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
