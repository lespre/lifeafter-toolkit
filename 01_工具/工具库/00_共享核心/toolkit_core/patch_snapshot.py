# -*- coding: utf-8 -*-
r"""patch_snapshot.py — 带 H 的 H-2 段：本地容器快照与终态判定。

为什么需要它
------------
H-1（`patch_delta`）看的是【服务端清单】，只能说到「哪个包变了」。
要说到「本地哪些行是新的」，前提是**本地有两次可比的快照** —— 这就是 H-2。

它解决三个具体问题
------------------
1. **全量 sha256 太慢**（89 GB）；实测 mtime/size 变了才值得重算哈希。
   ⇒ 两段式：先廉价 stat 扫，再只对候选做 sha256。

2. **mtime 变化不是内容变化**。游戏启动会 touch 部分容器。
   ⇒ 只有 sha256 变了才算「内容变更」；sha 相同但 mtime 变的单列为
      `mtime_only_changed`，**永不作为更新证据**。

3. ★ **写入窗口污染**（最容易出错的一条）：游戏在跑时扫描，可能采到
   「文件正在写」的中间态 —— 此时算出的 sha256 是**假的**，而且它自己不会报错。
   实测踩过：5 个 .idx/.wpk 的扫描值与复核值不同。
   ⇒ 判据：**算完 sha256 再回读一次 (size, mtime_ns)，与算之前一致才算终态**；
      不一致就重试，重试仍不稳就标 `unstable` 并排除出结论。

用法（库）
----------
    from toolkit_core import patch_snapshot as PS
    PS.scan_and_lock("E:/mrzh", "03_执行/…", baseline=<上次 source_lock.json>)

与 `source_lock.py` 的关系
--------------------------
`source_lock.py` 已经实现了「内容寻址快照 + diff + mtime_only 分离」，
本模块**不重写它**：
  · 复用它的 snapshot schema 与 compare_snapshots 语义
  · 在它之上补两件它没有的：**写入窗口守卫** 与 **两段式快扫**
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

try:                                    # 复用既有实现，不重写
    from . import source_lock as SL
except ImportError:                     # 单独跑时的退路
    import source_lock as SL            # type: ignore

# 游戏资源容器的后缀（与项目既有口径一致）
CONTAINER_SUFFIXES = {".gpk", ".npk", ".fpk", ".wpk", ".idx", ".pi", ".bin", ".nxs"}

SCHEMA = "lifeafter-patch-snapshot-v1"


def _stat_tuple(p: Path) -> tuple[int, int]:
    st = p.stat()
    return (st.st_size, st.st_mtime_ns)


def stable_sha256(path: Path, *, attempts: int = 3, wait: float = 0.4) -> dict[str, Any]:
    """算 sha256，并守卫「写入窗口」。

    做法：算之前记 (size, mtime_ns) → 算 → 再记一次；两次一致才算终态。
    不一致（说明文件在算的过程中被写过）就等一下重试；重试完仍不一致标 unstable。

    返回 {sha256, size, mtime_ns, stable, attempts, note}
    """
    last_err: str | None = None
    for i in range(1, attempts + 1):
        try:
            before = _stat_tuple(path)
            sha = SL.sha256_file(path)
            after = _stat_tuple(path)
        except OSError as exc:
            last_err = "%s: %s" % (type(exc).__name__, exc)
            time.sleep(wait)
            continue
        if before == after:
            return {"sha256": sha, "size": after[0], "mtime_ns": after[1],
                    "stable": True, "attempts": i, "note": ""}
        last_err = "stat 在哈希期间变化：%s → %s" % (before, after)
        time.sleep(wait)
    return {"sha256": None, "size": None, "mtime_ns": None,
            "stable": False, "attempts": attempts,
            "note": last_err or "多次尝试后仍不稳定"}


def scan_containers(root: Path | str, *,
                    suffixes: Iterable[str] | None = CONTAINER_SUFFIXES,
                    include_all: bool = False) -> dict[str, dict[str, Any]]:
    """第一段：廉价扫（只 stat，不算哈希）。返回 {相对路径: {size, mtime_ns}}。"""
    src = Path(root).resolve()
    if not src.is_dir():
        raise FileNotFoundError("源根不存在：%s" % src)
    want = None if include_all else {s.lower() for s in (suffixes or CONTAINER_SUFFIXES)}
    out: dict[str, dict[str, Any]] = {}
    for p in src.rglob("*"):
        if not p.is_file():
            continue
        if want is not None and p.suffix.lower() not in want:
            continue
        try:
            st = p.stat()
        except OSError:
            continue
        out[p.relative_to(src).as_posix()] = {"size": st.st_size, "mtime_ns": st.st_mtime_ns}
    return out


def pick_candidates(baseline: dict[str, Any], cheap: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    """第二段的前置：哪些文件值得重算哈希。

    · 新出现 → added（要算）
    · 消失   → removed（无需算）
    · size 或 mtime_ns 变 → stat_changed（要算，但算完可能只是 mtime-only）
    · 两者都没变 → 直接沿用基线的 sha256（不算）
    """
    before = {row["relative_path"]: row for row in baseline.get("files", [])}
    added = sorted(set(cheap) - set(before))
    removed = sorted(set(before) - set(cheap))
    stat_changed = sorted(
        p for p in (set(cheap) & set(before))
        if before[p].get("size") != cheap[p]["size"]
        or before[p].get("mtime_ns") != cheap[p]["mtime_ns"])
    return {"added": added, "removed": removed, "stat_changed": stat_changed}


def lock(root: Path | str, *, baseline_path: Path | str | None = None,
         suffixes: Iterable[str] | None = CONTAINER_SUFFIXES,
         include_all: bool = False, progress=None, quiet: bool = False) -> dict[str, Any]:
    """扫 + 锁：产出可比的快照与差分（含写入窗口判定结果）。

    ★ quiet=False 是默认值 ⇒ 行为与加参数前完全一致（CLI 只在 `--json -` 时传 True，
      否则进度行会混进 stdout，机器读不到纯 JSON）。
    """
    src = Path(root).resolve()
    t0 = time.time()
    if not quiet:
        print("[1/3] 廉价扫（只 stat）…", flush=True)
    cheap = scan_containers(src, suffixes=suffixes, include_all=include_all)
    if not quiet:
        print("      %d 个文件" % len(cheap), flush=True)

    baseline = None
    if baseline_path:
        bp = Path(baseline_path)
        if bp.is_file():
            baseline = SL.read_snapshot(bp)
            if not quiet:
                print("      基线：%s（%d 条）" % (bp.name, len(baseline.get("files", []))), flush=True)

    if baseline:
        cand = pick_candidates(baseline, cheap)
        need = sorted(set(cand["added"]) | set(cand["stat_changed"]))
        reuse = {r["relative_path"]: r for r in baseline["files"]}
        if not quiet:
            print("[2/3] 需重算哈希：%d 个（新增 %d · stat 变 %d）；其余沿用基线"
                  % (len(need), len(cand["added"]), len(cand["stat_changed"])), flush=True)
    else:
        need = sorted(cheap)
        reuse = {}
        cand = None
        if not quiet:
            print("[2/3] 无基线 ⇒ 全量算哈希：%d 个" % len(need), flush=True)

    files: list[dict[str, Any]] = []
    unstable: list[dict[str, Any]] = []
    for i, rel in enumerate(need, 1):
        p = src / rel
        r = stable_sha256(p)
        row = {"relative_path": rel, "size": r["size"], "mtime_ns": r["mtime_ns"],
               "sha256": r["sha256"]}
        if not r["stable"]:
            row["unstable"] = True
            row["note"] = r["note"]
            unstable.append({"relative_path": rel, "note": r["note"],
                             "attempts": r["attempts"]})
        files.append(row)
        if progress and i % 20 == 0:
            progress(i, len(need))
        elif not quiet and i % 50 == 0:
            print("      …%d/%d" % (i, len(need)), flush=True)

    done = {f["relative_path"] for f in files}
    for rel, meta in cheap.items():
        if rel in done:
            continue
        b = reuse.get(rel)
        if b:
            files.append({"relative_path": rel, "size": meta["size"],
                          "mtime_ns": meta["mtime_ns"], "sha256": b.get("sha256"),
                          "from_baseline": True})
        else:
            files.append({"relative_path": rel, "size": meta["size"],
                          "mtime_ns": meta["mtime_ns"], "sha256": None})

    snapshot = {
        "schema": SL.SNAPSHOT_SCHEMA,            # 沿用既有 schema，保证可比
        "root": str(src),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "generator": SCHEMA,
        "files": sorted(files, key=lambda x: x["relative_path"]),
        "unstable": unstable,
    }

    delta = None
    if baseline:
        delta = SL.compare_snapshots(baseline, snapshot)
        delta["unstable_count"] = len(unstable)
        delta["stat_changed_but_sha_same"] = sorted(
            p for p in cand["stat_changed"]
            if next((f for f in snapshot["files"] if f["relative_path"] == p), {}).get("sha256")
            == reuse.get(p, {}).get("sha256"))
    if not quiet:
        print("[3/3] 完成，用时 %.1f 秒；不稳定 %d 个" % (time.time() - t0, len(unstable)), flush=True)

    return {"snapshot": snapshot, "delta": delta, "candidates": cand if baseline else None,
            "seconds": round(time.time() - t0, 1)}


def write_run(result: dict[str, Any], out_dir: Path | str) -> dict[str, Path]:
    """落盘三件：source_lock.json · patch_delta.json · CURRENT_STATE.json。"""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {}
    paths["lock"] = SL.write_snapshot(result["snapshot"], out / "source_lock.json")
    if result.get("delta") is not None:
        p = out / "patch_delta.json"
        p.write_text(json.dumps(result["delta"], ensure_ascii=False, indent=2) + "\n",
                     encoding="utf-8", newline="\n")
        paths["delta"] = p
    state = {
        "schema": SCHEMA,
        "root": result["snapshot"]["root"],
        "scanned_files": len(result["snapshot"]["files"]),
        "unstable_count": len(result["snapshot"]["unstable"]),
        "seconds": result["seconds"],
        "conclusion_boundary": (
            "mtime 变化不是内容变化；unstable 文件被排除出内容结论；"
            "写入窗口守卫：sha256 前后 stat 必须一致才算终态。"),
    }
    if result.get("delta"):
        state["totals"] = {k: len(v) for k, v in result["delta"].items() if isinstance(v, list)}
    p = out / "CURRENT_STATE.json"
    p.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n",
                 encoding="utf-8", newline="\n")
    paths["state"] = p
    return paths


def find_latest_baseline(search_root: Path | str) -> Path | None:
    """在项目里找最近一次 source_lock.json（按 mtime）。"""
    root = Path(search_root)
    if not root.is_dir():
        return None
    best, best_m = None, -1.0
    for p in root.rglob("source_lock.json"):
        try:
            m = p.stat().st_mtime
        except OSError:
            continue
        if m > best_m:
            best, best_m = p, m
    return best
