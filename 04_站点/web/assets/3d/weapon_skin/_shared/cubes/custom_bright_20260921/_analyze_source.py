# -*- coding: utf-8 -*-
"""_analyze_source.py —— 自造亮环境 cube 的**源侧实测**（只读，不改任何源资产）。

目的（先把机制量出来，再决定构造参数）：
  ① 源六面 PNG 到底是 RGB 还是 RGBA？alpha 是不是 RGBM 乘子 M？
  ② 按 asm 542-544 `pow(rgb*a*16, 2)` 解码，每面的**实际辐射** L 落在哪（min/p50/p95/max）？
  ③ 有没有「大面积近黑」（luma<0.05）的面 —— 这是「镜面发黑」的直接来源。
  ④ 目标区间（解码后逐面 p50 0.25~0.45、最小 ≥0.12）对应的 alpha / 增益是多少？

只读：只 open() 源 faces，不写任何源目录。
用法：$env:PYTHONIOENCODING='utf-8'; & <venv>\python.exe _analyze_source.py
产出：_source_analysis.json（本目录内）
"""
import hashlib
import json
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CUBES = os.path.dirname(HERE)                      # ...\_shared\cubes
SRC = 'gdansk_shipyard_buildings02'                # 主基底
ALT = 'over_the_clouds'                            # 备用补面来源
AXES = ['+X', '-X', '+Y', '-Y', '+Z', '-Z']


def stats(x):
    x = np.asarray(x, dtype=np.float64).ravel()
    return {'min': round(float(x.min()), 5), 'p05': round(float(np.percentile(x, 5)), 5),
            'p50': round(float(np.percentile(x, 50)), 5), 'p95': round(float(np.percentile(x, 95)), 5),
            'max': round(float(x.max()), 5), 'mean': round(float(x.mean()), 5)}


def analyze(cube):
    out = {'cube': cube, 'faces': []}
    d = os.path.join(CUBES, cube, 'faces')
    for i in range(6):
        p = os.path.join(d, '%s_f%d_m0.png' % (cube, i))
        if not os.path.exists(p):
            out['faces'].append({'face': i, 'axis': AXES[i], 'missing': True})
            continue
        im = Image.open(p)
        mode = im.mode
        sz = im.size
        rgba = np.asarray(im.convert('RGBA')).astype(np.float64) / 255.0
        rgb = rgba[:, :, :3]
        a = rgba[:, :, 3]
        lum = 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]
        # asm 542-544 解码
        L = (rgb * a[:, :, None] * 16.0) ** 2
        Lm = L.mean(axis=2)
        row = {
            'face': i, 'axis': AXES[i], 'file': os.path.basename(p), 'png_mode': mode,
            'size': list(sz), 'bytes': os.path.getsize(p),
            'sha256': hashlib.sha256(open(p, 'rb').read()).hexdigest(),
            'rgb_lum': stats(lum),
            'rgb_min_channel_p50': stats(rgb.reshape(-1, 3).min(axis=1)),
            'alpha': stats(a),
            'alpha_is_constant': bool(a.max() - a.min() < 1e-9),
            'decoded_L': stats(Lm),
            'dark_luma_lt_0.05_pct': round(float(100.0 * (lum < 0.05).mean()), 3),
            'dark_L_lt_0.01_pct': round(float(100.0 * (Lm < 0.01).mean()), 3),
        }
        out['faces'].append(row)
        print('%-3s %-20s mode=%-4s %sx%s  rgblum p50=%.4f min=%.4f | alpha p50=%.5f max=%.5f const=%s | '
              'decL p50=%.5f min=%.5f | dark(lum<.05)=%.2f%%'
              % (AXES[i], row['file'], mode, sz[0], sz[1], row['rgb_lum']['p50'], row['rgb_lum']['min'],
                 row['alpha']['p50'], row['alpha']['max'], row['alpha_is_constant'],
                 row['decoded_L']['p50'], row['decoded_L']['min'], row['dark_luma_lt_0.05_pct']))
    return out


def main():
    rep = {'note': '只读分析；源资产未被修改。decode = pow(rgb*a*16,2) per asm 542-544.'}
    for c in (SRC, ALT):
        print('=== %s ===' % c)
        rep[c] = analyze(c)
        print()
    json.dump(rep, open(os.path.join(HERE, '_source_analysis.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('wrote _source_analysis.json')


if __name__ == '__main__':
    main()
