# -*- coding: utf-8 -*-
u"""_sweep_refine.py —— 细化 (g, a) 网格：在「cube 均值 ≈ 源 snow」的邻域内最大化 L>1。

约束（任务书规格 2 + 验收 ⑤）：
  · 逐面 近黑 L<0.05 占比 == 0
  · 六面合并 L>1 占比 ≥ snow 的 20.376%
  · **cube 合并均值不得显著高于源 snow**（否则就是「靠整体变亮换金属」，验收 ⑤ 不认）
用法同上。
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CUBES = os.path.dirname(HERE)
SRC = os.path.join(CUBES, 'snow', 'faces')
sys.path.insert(0, HERE)
from _sweep_gain_floor import build_f3, luma_lin, stats   # noqa: E402

F3_SIGMA, F3_DIM = 6.0, 0.85


def main():
    src = []
    for i in range(6):
        a = np.asarray(Image.open(os.path.join(SRC, 'snow_f%d_m0.png' % i)).convert('RGBA')
                       ).astype(np.float64) / 255.0
        src.append(np.square(a[:, :, :3] * a[:, :, 3:4] * 16.0))
    base_mean = float(np.concatenate([luma_lin(f).ravel() for f in src]).mean())

    rows = []
    for g in (1.15, 1.20, 1.25, 1.30, 1.35, 1.40, 1.45, 1.50):
        for a in (0.15, 0.18, 0.20, 0.22, 0.25, 0.28, 0.30, 0.35):
            faces = [build_f3(src[2], F3_SIGMA, F3_DIM) if i == 3 else src[i] for i in range(6)]
            per = [stats(g * np.sqrt(L ** 2 + a ** 2)) for L in faces]
            allv = np.concatenate([luma_lin(g * np.sqrt(L ** 2 + a ** 2)).ravel() for L in faces])
            rows.append({
                'g': g, 'a': a,
                'gt1_pct': round(float(100.0 * (allv > 1.0).mean()), 3),
                'mean_L': round(float(allv.mean()), 4),
                'mean_ratio_vs_snow': round(float(allv.mean()) / base_mean, 4),
                'p50_L': round(float(np.percentile(allv, 50)), 4),
                'p85_L': round(float(np.percentile(allv, 85)), 4),
                'dark_worst_pct': round(max(p['dark005_pct'] for p in per), 4),
                'min_L_over_faces': round(min(p['L_min'] for p in per), 5),
                'gt085_pct': round(float(100.0 * (allv > 0.85).mean()), 3),
                'per_face_gt1': [round(p['gt1_pct'], 2) for p in per],
                'per_face_dark': [round(p['dark005_pct'], 3) for p in per],
            })

    ok = [r for r in rows if r['dark_worst_pct'] == 0.0 and r['gt1_pct'] >= 20.376]
    ok.sort(key=lambda r: (abs(r['mean_ratio_vs_snow'] - 1.0), -r['gt1_pct']))
    print('源 snow cube 均值 = %.4f；可行候选 %d/%d（按 |均值比-1| 升序）' % (base_mean, len(ok), len(rows)))
    print('%-6s %-6s %-9s %-8s %-9s %-8s %-9s %-9s %s'
          % ('g', 'a', 'L>1%', 'mean', 'ratio', 'p50', '>0.85%', 'minL', 'per_face_gt1'))
    for r in ok[:20]:
        print('%-6.2f %-6.2f %-9.3f %-8.4f %-9.4f %-8.4f %-9.3f %-9.5f %s'
              % (r['g'], r['a'], r['gt1_pct'], r['mean_L'], r['mean_ratio_vs_snow'],
                 r['p50_L'], r['gt085_pct'], r['min_L_over_faces'], r['per_face_gt1']))
    json.dump({'base_mean': base_mean, 'f3': {'sigma': F3_SIGMA, 'dim': F3_DIM}, 'rows': rows},
              open(os.path.join(HERE, '_sweep_refine_20260921.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    return 0


if __name__ == '__main__':
    sys.exit(main())
