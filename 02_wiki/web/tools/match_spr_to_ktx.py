# -*- coding: utf-8 -*-
"""把 .spr 的 atlas 与包内 KTX 对上：按页面尺寸筛候选，再按帧布局一致性打分。

判据：把候选图按 .spr 的矩形切成 N 帧，连续帧应当高度相似（同一动画的相邻帧），
而随机贴图切出来互不相关。分数 = 相邻帧 alpha 通道相关系数的均值。
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

import numpy as np
from PIL import Image

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"))
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
from la_unpack_core import NpkArchive  # noqa: E402
from toolkit_core import android_gpk as AG  # noqa: E402

SPR_DIR = ROOT / "01_索引与产物/30_分析/sfx_1110189_联动_20261031/textures"
SWEEP = ROOT / "01_索引与产物/30_分析/ktx_sweep.json"
OUT = ROOT / "01_索引与产物/30_分析/spr_ktx_match"


def parse_spr(p: pathlib.Path):
    lines = [l.strip() for l in p.read_text(encoding="utf-8", errors="ignore").splitlines() if l.strip()]
    head = lines[0].split()
    if len(head) < 3:
        return None
    pw, ph = int(head[1]), int(head[2])
    n = int(lines[1])
    rects = []
    for ln in lines[3:3 + n]:
        parts = ln.split()
        if len(parts) < 5:
            continue
        rects.append(tuple(int(x) for x in parts[1:5]))
    return pw, ph, rects


def corr(a: np.ndarray, b: np.ndarray) -> float:
    a = a.ravel().astype(np.float32)
    b = b.ravel().astype(np.float32)
    if a.size != b.size or a.size == 0:
        return 0.0
    a -= a.mean()
    b -= b.mean()
    da, db = np.linalg.norm(a), np.linalg.norm(b)
    return float((a @ b) / (da * db)) if da and db else 0.0


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [r for r in json.loads(SWEEP.read_text(encoding="utf-8"))
            if r["fmt"] == "RGBA8_ETC2_EAC"]
    by_dim: dict[tuple[int, int], list[dict]] = {}
    for r in rows:
        by_dim.setdefault((r["w"], r["h"]), []).append(r)

    cache: dict[str, NpkArchive] = {}
    results = {}
    for spr in sorted(SPR_DIR.glob("*.spr")):
        got = parse_spr(spr)
        if not got:
            continue
        pw, ph, rects = got
        cands = by_dim.get((pw, ph), [])
        if not cands:
            print("%-28s 无同尺寸候选" % spr.name)
            continue
        best = []
        for r in cands:
            pack = ROOT / "01_索引与产物/源包/pe_npk_20261029" / r["pack"]
            a = cache.get(r["pack"]) or NpkArchive(str(pack))
            cache[r["pack"]] = a
            try:
                d = a.read_entry(entry_index=r["row"])
                info = AG.parse_ktx(d)
                arr = np.asarray(AG._ktx_rgba(d, info), dtype=np.uint8)
            except Exception:                                   # noqa: BLE001
                continue
            frames = [arr[y0:y1, x0:x1, 3] for (x0, y0, x1, y1) in rects]
            if len(frames) < 2:
                continue
            alphas = [f.astype(np.float32) / 255.0 for f in frames]
            cov = float(np.mean([(a > 0.05).mean() for a in alphas]))
            if not (0.04 <= cov <= 0.60):          # 细结构：既不是全空也不是满幅
                continue
            std = float(np.mean([a.std() for a in alphas]))
            if std < 0.12:                          # 排除整块不透明/纯色贴图
                continue
            border = float(np.mean([np.concatenate([a[0, :], a[-1, :], a[:, 0], a[:, -1]]).mean()
                                    for a in alphas]))
            if border > 0.35:                       # 真正的 atlas：边缘基本透明
                continue
            sims = [corr(frames[i], frames[i + 1]) for i in range(len(frames) - 1)]
            score = float(np.mean(sims)) if sims else 0.0
            best.append((score, r, arr, cov))
        best.sort(key=lambda x: -x[0])
        results[spr.name] = [{"score": round(b[0], 4), "pack": b[1]["pack"], "row": b[1]["row"],
                              "cov": round(b[3], 3)} for b in best[:3]]
        print("%-26s 候选 %4d ｜ 最佳得分 %.3f（%s row=%d）"
              % (spr.name, len(cands), best[0][0], best[0][1]["pack"], best[0][1]["row"]), flush=True)
        for i, (score, r, arr, cov) in enumerate(best[:3]):
            Image.fromarray(arr, "RGBA").save(OUT / ("%s__top%d_%s_%d.png"
                                                     % (spr.stem, i + 1, r["pack"].split(".")[1], r["row"])))
    (OUT / "match.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print("写出", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
