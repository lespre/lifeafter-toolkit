# -*- coding: utf-8 -*-
u"""_sweep_minimal.py —— 找**最小整体增亮**下满足全部硬约束的 (g, a)。

硬约束：
  ① 逐面 近黑 L<0.05 占比 == 0 且逐面 min L > 0.05
  ② 六面合并 L>1 占比 ≥ 20.376%（= 源 snow）
  ③ 六面合并均值尽量低（越接近源 snow 0.5050 越好）—— 防止「靠整体变亮换金属」
对每个 g，二分求**最小** a 使 ① 成立；再报告该点的 ② ③。
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
from _sweep_gain_floor import build_f3, luma_lin   # noqa: E402

F3_SIGMA, F3_DIM = 6.0, 0.85


def load():
    out = []
    for i in range(6):
        a = np.asarray(Image.open(os.path.join(SRC, 'snow_f%d_m0.png' % i)).convert('RGBA')
                       ).astype(np.float64) / 255.0
        out.append(np.square(a[:, :, :3] * a[:, :, 3:4] * 16.0))
    out[3] = build_f3(out[2], F3_SIGMA, F3_DIM)
    return out


def apply(src, g, a):
    return [g * np.sqrt(L ** 2 + a ** 2) for L in src]


def evaluate(faces):
    per_l = [luma_lin(L).ravel() for L in faces]
    allv = np.concatenate(per_l)
    return {
        'dark_worst_pct': max(float(100.0 * (l < 0.05).mean()) for l in per_l),
        'min_L_over_faces': min(float(l.min()) for l in per_l),
        'gt1_pct': float(100.0 * (allv > 1.0).mean()),
        'mean_L': float(allv.mean()),
        'p50_L': float(np.percentile(allv, 50)),
        'gt085_pct': float(100.0 * (allv > 0.85).mean()),
        'per_face_gt1': [round(float(100.0 * (l > 1.0).mean()), 2) for l in per_l],
        'per_face_min': [round(float(l.min()), 4) for l in per_l],
        'per_face_p50': [round(float(np.percentile(l, 50)), 4) for l in per_l],
        'per_face_dark': [round(float(100.0 * (l < 0.05).mean()), 3) for l in per_l],
    }


def main():
    src = load()
    base_mean = float(np.concatenate([luma_lin(L).ravel() for L in src]).mean())
    print('源 snow（f3 已补）均值基线 = %.4f' % base_mean)
    print()
    print('%-6s %-9s %-9s %-9s %-9s %-9s %s'
          % ('g', 'a*(最小)', 'L>1%', 'mean', 'ratio', 'p50', 'per_face_gt1'))
    rows = []
    for g in (1.00, 1.02, 1.05, 1.08, 1.10, 1.12, 1.15, 1.18, 1.20, 1.25, 1.30):
        lo, hi = 0.0, 0.6
        if evaluate(apply(src, g, hi))['dark_worst_pct'] > 0.0:
            print('  g=%.2f 即使 a=%.2f 仍不满足 dark==0' % (g, hi))
            continue
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if evaluate(apply(src, g, mid))['dark_worst_pct'] == 0.0:
                hi = mid
            else:
                lo = mid
        a = hi
        ev = evaluate(apply(src, g, a))
        ev.update({'g': g, 'a': round(a, 6), 'mean_ratio_vs_snow': round(ev['mean_L'] / base_mean, 4)})
        ev = {k: (round(v, 6) if isinstance(v, float) else v) for k, v in ev.items()}
        rows.append(ev)
        print('%-6.2f %-9.5f %-9.3f %-9.4f %-9.4f %-9.4f %s'
              % (g, a, ev['gt1_pct'], ev['mean_L'], ev['mean_ratio_vs_snow'], ev['p50_L'],
                 ev['per_face_gt1']))
    json.dump({'base_mean': base_mean, 'f3': {'sigma': F3_SIGMA, 'dim': F3_DIM}, 'rows': rows},
              open(os.path.join(HERE, '_sweep_minimal_20260921.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    return 0


if __name__ == '__main__':
    sys.exit(main())
