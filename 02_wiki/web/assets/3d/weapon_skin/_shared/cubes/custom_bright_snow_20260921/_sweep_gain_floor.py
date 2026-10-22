# -*- coding: utf-8 -*-
u"""_sweep_gain_floor.py —— 为 `custom_bright_snow_20260921` 反解 (增益 g, 抬底 a)。

只读分析；不改任何资产。目的：在「逐面近黑(L<0.05)占比 = 0」与「主体不因变暗而受损」的
双重约束下，找 **最大化 L>1 纹素占比** 的 (g, a)。

口径（与 GI2 终报一致，已用 snow 复算校验 = 20.376%）：
    L = 0.2126*R + 0.7152*G + 0.0722*B ,  (R,G,B) = (rgb_norm * a_norm * 16)^2

候选映射（逐通道，对源解码辐射 L_src 施加）：
    L_new = g * sqrt( L_src^2 + a^2 )          # 增益 g + 软抬底 a（quadrature）

f3 补面：源 f3 全黑 ⇒ 用 +Y(f2 天花) 面镜像（vertical flip）+ 高斯模糊 + 轻微压暗。

用法:
  $env:PYTHONIOENCODING='utf-8'
  & '<venv>\python.exe' _sweep_gain_floor.py
"""
import itertools
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

HERE = os.path.dirname(os.path.abspath(__file__))
CUBES = os.path.dirname(HERE)
SRC = os.path.join(CUBES, 'snow', 'faces')
AXES = ['+X', '-X', '+Y', '-Y', '+Z', '-Z']


def luma_lin(lin):
    return 0.2126 * lin[:, :, 0] + 0.7152 * lin[:, :, 1] + 0.0722 * lin[:, :, 2]


def load_src():
    raw = []
    for i in range(6):
        p = os.path.join(SRC, 'snow_f%d_m0.png' % i)
        a = np.asarray(Image.open(p).convert('RGBA')).astype(np.float64) / 255.0
        L = np.square(a[:, :, :3] * a[:, :, 3:4] * 16.0)      # 逐通道解码辐射
        raw.append(L)
    return raw


def build_f3(plus_y, blur_sigma, dim):
    """f3(-Y) 补面：+Y 天花镜像 + 高斯模糊 + 轻微压暗。返回逐通道线性辐射。"""
    face = plus_y[::-1, :, :]                      # 垂直镜像
    out = np.empty_like(face)
    for c in range(3):
        out[:, :, c] = gaussian_filter(face[:, :, c], sigma=blur_sigma, mode='reflect')
    return out * dim


def stats(L):
    l = luma_lin(L).ravel()
    return {'L_min': float(l.min()), 'L_p50': float(np.percentile(l, 50)),
            'L_mean': float(l.mean()), 'L_max': float(l.max()),
            'gt1_pct': float(100.0 * (l > 1.0).mean()),
            'dark005_pct': float(100.0 * (l < 0.05).mean())}


def main():
    src = load_src()
    base_l = np.concatenate([luma_lin(f).ravel() for f in src])
    print('=== 源 snow（六面合并，f3 全黑） ===')
    print('  L_mean=%.4f p50=%.4f >1.0=%.3f%% dark(<0.05)=%.3f%%'
          % (base_l.mean(), np.percentile(base_l, 50), 100.0 * (base_l > 1.0).mean(),
             100.0 * (base_l < 0.05).mean()))

    # ── f3 补面候选 ──
    print()
    print('=== f3 补面候选（+Y 镜像 + 高斯模糊 sigma + 压暗 dim）===')
    f3_cands = []
    for sigma in (6.0, 10.0, 14.0, 20.0):
        for dim in (0.55, 0.7, 0.85):
            f3 = build_f3(src[2], sigma, dim)
            s = stats(f3)
            f3_cands.append({'sigma': sigma, 'dim': dim, **s})
            print('  sigma=%-5.1f dim=%-5.2f  L_min=%-7.4f p50=%-7.4f mean=%-7.4f max=%-7.3f '
                  '>1.0=%-6.2f%% dark=%.2f%%'
                  % (sigma, dim, s['L_min'], s['L_p50'], s['L_mean'], s['L_max'],
                     s['gt1_pct'], s['dark005_pct']))

    # 选 f3：L_min 最高（补面必须有能量）、>1.0 占比尽量接近其它面、模糊充分
    best_f3 = sorted(f3_cands, key=lambda r: (r['dark005_pct'] > 0.0, -r['gt1_pct']))[0]
    print('  ⇒ 初选 sigma=%.1f dim=%.2f' % (best_f3['sigma'], best_f3['dim']))

    # ── (g, a) 扫描 ──
    print()
    print('=== (g, a) 扫描：目标 = dark%==0 且最大化 L>1 ===')
    rows = []
    for g in (1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 2.0):
        for a in (0.0, 0.05, 0.08, 0.10, 0.12, 0.15, 0.20, 0.25, 0.30):
            faces = []
            for i, L in enumerate(src):
                faces.append(build_f3(src[2], best_f3['sigma'], best_f3['dim'])
                             if i == 3 else L)
            # 逐面统计（必须逐面 dark==0）
            per = [stats(g * np.sqrt(L ** 2 + a ** 2)) for L in faces]
            allv = np.concatenate([luma_lin(g * np.sqrt(L ** 2 + a ** 2)).ravel() for L in faces])
            worst_dark = max(p['dark005_pct'] for p in per)
            rows.append({'g': g, 'a': a,
                         'gt1_pct': round(float(100.0 * (allv > 1.0).mean()), 3),
                         'dark_worst_pct': round(worst_dark, 4),
                         'min_L_over_faces': round(min(p['L_min'] for p in per), 5),
                         'mean_L': round(float(allv.mean()), 4),
                         'p50_L': round(float(np.percentile(allv, 50)), 4),
                         'per_face_gt1': [round(p['gt1_pct'], 2) for p in per]})
    ok = [r for r in rows if r['dark_worst_pct'] == 0.0 and r['min_L_over_faces'] > 0.05]
    ok.sort(key=lambda r: -r['gt1_pct'])
    print('  可行（dark==0 且逐面 min>0.05）候选 %d / %d，按 L>1 降序前 12：' % (len(ok), len(rows)))
    print('  %-6s %-6s %-9s %-9s %-9s %-9s %s' % ('g', 'a', 'L>1%', 'mean', 'p50', 'minL', 'per_face_gt1'))
    for r in ok[:12]:
        print('  %-6.2f %-6.2f %-9.3f %-9.4f %-9.4f %-9.5f %s'
              % (r['g'], r['a'], r['gt1_pct'], r['mean_L'], r['p50_L'],
                 r['min_L_over_faces'], r['per_face_gt1']))

    print()
    print('  不可行样例（dark>0）:')
    bad = [r for r in rows if r['dark_worst_pct'] > 0.0]
    bad.sort(key=lambda r: r['dark_worst_pct'])
    for r in bad[:6]:
        print('  g=%-5.2f a=%-5.2f L>1=%-7.3f%% dark_worst=%.4f%% minL=%.5f'
              % (r['g'], r['a'], r['gt1_pct'], r['dark_worst_pct'], r['min_L_over_faces']))

    json.dump({'source_baseline': {'L_mean': round(float(base_l.mean()), 4),
                                   'L_p50': round(float(np.percentile(base_l, 50)), 4),
                                   'gt1_pct': round(float(100.0 * (base_l > 1.0).mean()), 3),
                                   'dark005_pct': round(float(100.0 * (base_l < 0.05).mean()), 3)},
               'f3_candidates': f3_cands, 'chosen_f3': best_f3,
               'grid': rows},
              open(os.path.join(HERE, '_sweep_20260921.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print()
    print('wrote _sweep_20260921.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
