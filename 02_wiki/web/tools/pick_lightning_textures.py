# -*- coding: utf-8 -*-
"""从 res.layers KTX 候选里挑「闪电类」纹理：透明底 + 细亮结构。

评分：alpha 覆盖 3%~50%（细结构）、非透明区亮度高、边缘细（覆盖率低但亮点多）。
输出 png + 排序清单，供肉眼确认。
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
from PIL import Image

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"))
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
from la_unpack_core import NpkArchive  # noqa: E402
from toolkit_core import android_gpk as AG  # noqa: E402

SWEEP = ROOT / "01_索引与产物/30_分析/ktx_sweep.json"
OUT = ROOT / "_截图/ktx_lightning_candidates"


def main(argv: list[str]) -> int:
    rows = json.loads(SWEEP.read_text(encoding="utf-8"))
    rows = [r for r in rows if r["fmt"] == "RGBA8_ETC2_EAC"]
    print("可解码候选", len(rows), flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.png"):
        old.unlink()

    cache: dict[str, NpkArchive] = {}
    scored = []
    for i, r in enumerate(rows):
        pack = ROOT / "01_索引与产物/源包/pe_npk_20261029" / r["pack"]
        a = cache.get(r["pack"])
        if a is None:
            a = NpkArchive(str(pack))
            cache[r["pack"]] = a
        try:
            d = a.read_entry(entry_index=r["row"])
            info = AG.parse_ktx(d)
            rgba = AG._ktx_rgba(d, info)
        except Exception:                                        # noqa: BLE001
            continue
        arr = np.asarray(rgba, dtype=np.uint8)
        alpha = arr[:, :, 3].astype(np.float32) / 255.0
        cov = float((alpha > 0.05).mean())
        if not (0.02 <= cov <= 0.55):
            continue
        rgb = arr[:, :, :3].astype(np.float32)
        bright = float((rgb.mean(axis=2)[alpha > 0.05]).mean()) if (alpha > 0.05).any() else 0
        score = bright * (1 - abs(cov - 0.15))
        scored.append((score, cov, bright, r, arr))
        if i % 200 == 0:
            print("  ..%d 通过 %d" % (i, len(scored)), flush=True)

    scored.sort(key=lambda x: -x[0])
    keep = scored[:60]
    print("候选", len(scored), "取前", len(keep))
    meta = []
    for idx, (score, cov, bright, r, arr) in enumerate(keep):
        name = f"{idx:02d}_{r['pack'].split('.')[1]}_{r['row']}_{r['w']}x{r['h']}.png"
        Image.fromarray(arr, "RGBA").save(OUT / name)
        meta.append({"file": name, "score": round(score, 1), "alpha_cov": round(cov, 3),
                     "brightness": round(bright, 1), "row": r["row"], "pack": r["pack"]})
    (OUT / "candidates.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print("写出", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
