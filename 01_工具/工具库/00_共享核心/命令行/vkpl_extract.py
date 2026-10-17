# -*- coding: utf-8 -*-
r"""VKPL 全量自检 + 导出（本次热更 0007.gpk 新增行）。

用法：
  python vkpl_extract.py --gpk E:/mrzh/Documents/gres/0007.gpk \
      --baseline <旧 0007 快照.gpk> --out <目录> [--limit N] [--export]
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys
import time

PROJ = pathlib.Path(__file__).resolve().parents[4]           # …/01_工具/工具库/00_共享核心/命令行 → 项目根
sys.path.insert(0, str(PROJ / "01_工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "01_工具/工具库/02_图文音频渲染/皮肤链与渲染"))

from gpk_npk_index import _gpk_blockchain                    # noqa: E402
from toolkit_core import vkpl_shader as VK                   # noqa: E402
import zstandard as zstd                                     # noqa: E402


def rows(path: pathlib.Path):
    return {int(r[0]): (int(r[2]), int(r[3]), int(r[4]))
            for r in _gpk_blockchain(str(path), with_crc=True)[1]()}


def main() -> int:
    ap = argparse.ArgumentParser(description="VKPL（Vulkan SPIR-V 着色器容器）自检 / 导出")
    ap.add_argument("--gpk", required=True, type=pathlib.Path)
    ap.add_argument("--baseline", type=pathlib.Path, default=None,
                    help="旧快照 gpk；给了就只处理「新增行」")
    ap.add_argument("--rows", default=None, help="行号区间 a-b（不给=全量）")
    ap.add_argument("--out", required=True, type=pathlib.Path)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--export", action="store_true", help="把模块落成 .spv")
    args = ap.parse_args()

    t0, all_rows = time.time(), rows(args.gpk)
    if args.baseline:
        base = rows(args.baseline)
        todo = sorted(set(all_rows) - set(base))
    elif args.rows:
        a, b = (int(x) for x in args.rows.split("-"))
        todo = list(range(a, b + 1))
    else:
        todo = sorted(all_rows)
    if args.limit:
        todo = todo[:args.limit]

    blob = args.gpk.read_bytes()
    d = zstd.ZstdDecompressor()
    args.out.mkdir(parents=True, exist_ok=True)
    stat = collections.Counter()
    stages = collections.Counter()
    per_cnt = collections.Counter()
    bad, entries = [], []
    for r in todo:
        poff, packed, decoded = all_rows[r]
        raw = blob[poff:poff + packed]
        try:
            buf = d.decompress(raw, max_output_size=max(decoded, 1))
        except zstd.ZstdError:
            buf = raw
            stat["行载荷非 zstd"] += 1
        if not VK.is_vkpl(buf):
            stat["非 VKPL 行"] += 1
            continue
        info = VK.parse(buf)
        if not info.get("ok"):
            bad.append({"row": r, "why": info["why"]})
            stat["解不开"] += 1
            continue
        stat["VKPL 行"] += 1
        per_cnt[info["count"]] += 1
        if not info.get("struct_ok"):
            stat["结构自检不过（走 magic 兜底）"] += 1
        if not info.get("scan_ok"):
            stat["magic 数≠模块数"] += 1
        for m in info["modules"]:
            stages[m["stage"] or "未知"] += 1
        if args.export:
            files = VK.extract(buf, args.out / "spv", "%08d" % r)
            entries.append({"row": r, "count": info["count"], "bytes": info["bytes"],
                            "modules": [{"stage": f["stage"], "size": f["size"]} for f in files]})
    total_mods = sum(k * v for k, v in per_cnt.items())
    rep = {"gpk": str(args.gpk), "处理行": len(todo), "VKPL 行": stat["VKPL 行"],
           "非 VKPL 行": stat["非 VKPL 行"], "解不开": stat["解不开"],
           "模块数合计": total_mods, "模块数分布": dict(per_cnt), "阶段分布": dict(stages),
           "自检": {k: v for k, v in stat.items()},
           "bad 样例": bad[:5], "秒": round(time.time() - t0, 1)}
    (args.out / "vkpl_report.json").write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    if entries:
        (args.out / "vkpl_index.json").write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    print("\n产物 →", args.out / "vkpl_report.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
