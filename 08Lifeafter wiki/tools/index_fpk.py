# -*- coding: utf-8 -*-
"""P1-8 Stage 3b-2：FPK 条目（zstd 帧）索引 —— 多进程按包并行版。

zstd 帧边界只能靠完整解压确定（无索引），因此加速策略=按包并行：
每 worker 处理一个包，逐帧流式解压并只记录元数据（不保留 payload）。
已完成包（jsonl 存在且非空）自动跳过（--skip-existing）。
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "data" / "source_registry.json"
OUT_DIR = ROOT / "data" / "audit" / "package_indexes"
TOOLKIT = str(Path(r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心"))
TOOLS = str(Path(__file__).resolve().parent)


def _index_one(args: tuple) -> dict:
    client_channel, rel_path, sha, size, out_path_str = args
    out_path = Path(out_path_str)
    if out_path.is_file() and out_path.stat().st_size > 0:
        # 已完成（含部分完成=异常中断残留：为安全跳过；摘要会按行数核对）
        return {"client_channel": client_channel, "path": rel_path,
                "status": "skipped-existing", "frames_file": out_path_str}
    sys.path[:0] = [TOOLS, TOOLKIT]
    from toolkit_core.fpk_frames import iter_fpk_frames, FpkFrameError
    client_root = Path(r"E:\mrzh" if client_channel == "test" else r"E:\LifeAfter")
    pkg = client_root / rel_path
    magic_counter: Counter = Counter()
    storage_counter: Counter = Counter()
    n = 0
    rec = {"client_channel": client_channel, "path": rel_path,
           "registry_sha256": sha, "size": size}
    try:
        with out_path.open("w", encoding="utf-8", newline="\n") as f:
            for frame, _payload in iter_fpk_frames(pkg):
                f.write(json.dumps({
                    "frame_index": frame.index,
                    "offset": frame.offset,
                    "packed_size": frame.packed_size,
                    "output_size": frame.output_size,
                    "output_magic": frame.output_magic,
                    "storage": frame.storage,
                    "padding_size": getattr(frame, "padding_size", 0),
                }) + "\n")
                magic_counter[frame.output_magic] += 1
                storage_counter[frame.storage] += 1
                n += 1
        rec["status"] = "indexed"
        rec["frame_count"] = n
        rec["output_magic_top"] = dict(magic_counter.most_common(20))
        rec["storage_distribution"] = dict(storage_counter)
    except (FpkFrameError, OSError, ValueError) as exc:
        rec["status"] = f"error: {exc}"
        if n:
            rec["partial_frames"] = n
    rec["frames_file"] = out_path_str
    return rec


def main() -> int:
    reg = json.loads(REG.read_text(encoding="utf-8"))
    fpks = [s for s in reg["sources"] if s["kind"] == "容器(fpk)"]
    fpks.sort(key=lambda s: (s["client_channel"], s["path"]))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tasks = []
    for s in fpks:
        slug = s["path"].replace("/", "_").replace(".", "_")
        out = OUT_DIR / f"fpk_{s['client_channel']}_{slug}.frames.jsonl"
        tasks.append((s["client_channel"], s["path"], s["sha256"], s["size"],
                      str(out)))
    workers = min(14, max(4, (__import__("os").cpu_count() or 8) - 2))
    results = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for i, r in enumerate(ex.map(_index_one, tasks), 1):
            results.append(r)
            print(f"[{i}/{len(tasks)}] {r['client_channel']} {r['path']}: "
                  f"{r.get('status')} frames={r.get('frame_count', '-')}",
                  flush=True)
    summary = {"packages": [], "failures": []}
    for r in results:
        if r.get("frames_file"):
            r["frames_file"] = str(Path(r["frames_file"]).relative_to(ROOT))
        (summary["packages"] if r["status"] == "indexed"
         else summary["failures"]).append(r)
        summary["packages"].append(r) if r["status"] == "skipped-existing" else None
    (OUT_DIR / "fpk_index_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    indexed = sum(1 for p in results if p["status"] == "indexed")
    skipped = sum(1 for p in results if p["status"] == "skipped-existing")
    failed = sum(1 for p in results if p["status"] != "indexed"
                 and p["status"] != "skipped-existing")
    print(f"fpk indexed {indexed} + skipped {skipped} / {len(results)}; "
          f"failures {failed}; workers={workers}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
