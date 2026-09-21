# -*- coding: utf-8 -*-
"""建立**武器皮肤图像定位链**的地基：全 fpk 帧级资源索引（一趟建好，永久复用）。

为什么需要：现在的痛点是「皮肤 stem → 容器里的哪一帧」只能临时搜，又慢又不稳。
本工具把 64 个 fpk 的**每一帧**登记成一行 JSONL，之后任何皮肤都能查表定位：

  每行：{pack, frame, offset, magic, size, atlas_names[], stems[], paths[]}
  · magic: ATLAS / DDS / JSON / FSB5 / 其它
  · atlas_names: 若该帧是 ATLAS 清单，抽出里面所有 *.png 切片名（这是**真名**，最关键的定位锚）
  · stems: 帧内容里出现的 skin_XXXX_YYY
  · paths: 帧内容里的资源路径（weapon/... 、ui/... 等）

用法：python tools/build_fpk_index.py [--packs 001,002] [--workers 24] [--max-frames 0]
产物：data/fpk_index/fpk_index.jsonl（追加写）+ data/fpk_index/_summary.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLKIT = r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心"
sys.path.insert(0, TOOLKIT)
RES = Path(r"E:\mrzh\res")
OUT = ROOT / "data" / "fpk_index"
IDX = OUT / "fpk_index.jsonl"
STEM_RE = re.compile(rb"skin_\d{4}_\d{3}[A-Za-z0-9_]*")
NAME_RE = re.compile(rb"[A-Za-z0-9_]{3,64}\.png")
PATH_RE = re.compile(rb"(?:weapon|ui|effect|character|model|res|utility|scene)[A-Za-z0-9_/\\\.-]{4,160}\.(?:gim|tga|dds|png|mat|fx|sfx|anim)")


def scan(pack: str, max_frames: int) -> dict:
    sys.path.insert(0, TOOLKIT)
    from toolkit_core.fpk_frames import iter_fpk_frames
    pk = RES / f"{pack}.fpk"
    rows = []
    if not pk.exists():
        return {"pack": pack, "exists": False, "frames": 0}
    for frame, data in iter_fpk_frames(pk):
        if max_frames and frame.index > max_frames:
            break
        row = {"pack": pack, "frame": frame.index, "offset": frame.offset,
               "magic": frame.output_magic, "size": frame.output_size}
        if frame.output_magic == "ATLAS":
            row["atlas_names"] = sorted({x.decode("latin1") for x in NAME_RE.findall(data)})[:400]
        head = data[:2_000_000]
        st = sorted({x.decode("latin1") for x in STEM_RE.findall(head)})
        if st:
            row["stems"] = st[:80]
        pa = sorted({x.decode("latin1").replace("\\", "/") for x in PATH_RE.findall(head)})
        if pa:
            row["paths"] = pa[:120]
        rows.append(row)
    return {"pack": pack, "exists": True, "frames": len(rows), "rows": rows}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--packs", default="")
    ap.add_argument("--workers", type=int, default=24)
    ap.add_argument("--max-frames", type=int, default=0)
    a = ap.parse_args()
    packs = ([x.strip() for x in a.packs.split(",") if x.strip()]
             or [f"{i:03d}" for i in range(1, 65)])
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    summary = {"schema": "fpk-index-v1",
               "generated": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
               "packs": []}
    with IDX.open("a", encoding="utf-8") as fh, ProcessPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(scan, p, a.max_frames): p for p in packs}
        done = 0
        for fut in as_completed(futs):
            r = fut.result()
            done += 1
            if r.get("rows"):
                for row in r["rows"]:
                    fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            fh.flush()
            summary["packs"].append({"pack": r["pack"], "exists": r.get("exists"),
                                     "frames": r.get("frames", 0)})
            print(f"[{done}/{len(packs)}] {r['pack']}: {r.get('frames',0)} 帧 ({time.time()-t0:.0f}s)", flush=True)
    summary["total_frames"] = sum(p["frames"] for p in summary["packs"])
    summary["seconds"] = round(time.time() - t0, 1)
    (OUT / "_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"完成：{summary['total_frames']:,} 帧 / {summary['seconds']}s → {IDX}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
