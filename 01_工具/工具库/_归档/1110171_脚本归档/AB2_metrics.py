# -*- coding: utf-8 -*-
"""AB2_metrics.py — 1110024 IBL A/B 指标（p50/p95/受光%/金银紫%）+ 复现性 + 布局恒定。"""
import io, json, os, sys
import numpy as np
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
SKIN = '1110024'


def lum(a):
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def metrics(arr, bb):
    sub = arr[bb[1]:bb[3], bb[0]:bb[2], :3].astype(np.float64)
    L = lum(sub)
    bg = float(np.percentile(L, 10)); thr = bg * 1.35
    r, g, b = sub[..., 0], sub[..., 1], sub[..., 2]
    return {'pixels': int(sub.shape[0] * sub.shape[1]), 'mean_rgb': [round(float(sub[..., i].mean()), 2) for i in range(3)],
            'p50': round(float(np.percentile(L, 50)), 1), 'p95': round(float(np.percentile(L, 95)), 1),
            'bg_p10': round(bg, 1), 'lit_pct': round(float((L > thr).mean() * 100), 2),
            'gold_pct': round(float(((r > g) & (g > b) & ((r - b) > 25)).mean() * 100), 2),
            'silver_pct': round(float(((np.abs(r - g) < 12) & (np.abs(g - b) < 12) & (L > 90)).mean() * 100), 2),
            'violet_pct': round(float(((b > r) & (r > g) & ((b - g) > 25)).mean() * 100), 2)}


raws = {}
for g in ('A', 'B'):
    for r in ('1', '2'):
        p = os.path.join(OUT, 'AB2_raw_%s_r%s.json' % (g, r))
        if os.path.isfile(p):
            raws['%s%s' % (g, r)] = json.load(open(p, encoding='utf-8'))

out = {'skins': {}, 'version': {}}
for k, v in raws.items():
    st = v.get('state')
    proj = json.loads(st).get('proj') if isinstance(st, str) and st.startswith('{') else None
    bb = [max(0, int(proj['x0'] * 1178) - 2), max(0, int(proj['y0'] * 718) - 2),
          min(1178, int(proj['x1'] * 1178) + 3), min(718, int(proj['y1'] * 718) + 3)] if proj else None
    out['version'][k] = {'viewer_sha': v.get('viewer_sha'), 'frozen': v.get('frozen'), 'rew': v.get('rew_count'),
                         'pinned': v.get('pinned'), 'png_sha16': v.get('png_sha16'),
                         'changed_defaults': v.get('default_files_changed_during_run'),
                         'snapshot': v.get('snapshot'), 'proj': proj, 'bbox': bb, 'png': v.get('png')}

lines = []
lines.append('| 组 | p50 | p95 | 受光% | 金% | 银% | 紫% | meanRGB | 画布 | sha16 |')
lines.append('|---|---|---|---|---|---|---|---|---|---|')
for g in ('A', 'B'):
    for r in ('1', '2'):
        k = g + r
        if k not in raws:
            continue
        p = os.path.join(OUT, 'AB2_%s_%s%s.png' % (SKIN, g, '' if r == '1' else '_r' + r))
        arr = np.asarray(Image.open(p).convert('RGBA'))
        bb = out['version'][k]['bbox'] or [0, 0, arr.shape[1], arr.shape[0]]
        m = metrics(arr, bb)
        out['skins']['%s_%s' % (g, r)] = {'metrics': m, 'bbox': bb, 'size': [arr.shape[1], arr.shape[0]]}
        lines.append('| %s r%s | %s | %s | %s | %s | %s | %s | %s | %dx%d | %s |' % (
            g, r, m['p50'], m['p95'], m['lit_pct'], m['gold_pct'], m['silver_pct'], m['violet_pct'],
            m['mean_rgb'], arr.shape[1], arr.shape[0], out['version'][k]['png_sha16']))

# A/B 差异（r1）
a = os.path.join(OUT, 'AB2_%s_A.png' % SKIN)
b = os.path.join(OUT, 'AB2_%s_B.png' % SKIN)
if os.path.isfile(a) and os.path.isfile(b):
    A = np.asarray(Image.open(a).convert('RGB')).astype(np.int16)
    B = np.asarray(Image.open(b).convert('RGB')).astype(np.int16)
    d = np.abs(A - B).max(axis=2)
    bb = out['version']['A1']['bbox'] or [0, 0, A.shape[1], A.shape[0]]
    sub = d[bb[1]:bb[3], bb[0]:bb[2]]
    out['delta'] = {'changed_pct_img': round(float(100.0 * (d > 15).mean()), 2),
                    'changed_pct_bbox': round(float(100.0 * (sub > 15).mean()), 2),
                    'mean_abs_bbox': round(float(sub.mean()), 1)}
    lines.append('')
    lines.append('A vs B（r1）：整图变化 %.2f%%，武器框内变化 %.2f%%，框内平均|Δ| %.1f' % (
        out['delta']['changed_pct_img'], out['delta']['changed_pct_bbox'], out['delta']['mean_abs_bbox']))

lines.append('')
lines.append('| 组 | r1 sha16 | r2 sha16 | 复现 |')
lines.append('|---|---|---|---|')
for g in ('A', 'B'):
    s1 = (raws.get(g + '1') or {}).get('png_sha16')
    s2 = (raws.get(g + '2') or {}).get('png_sha16')
    lines.append('| %s | %s | %s | %s |' % (g, s1, s2, 'YES' if s1 == s2 else 'NO'))
lines.append('')
lines.append('版本：' + json.dumps({k: {'viewer_sha': v['viewer_sha'], 'frozen_neox': (v['frozen'] or {}).get(SKIN, {}).get('neox_sha16'),
                                        'rew': v['rew'], 'pinned': v['pinned'], 'changed_defaults': v['changed_defaults']}
                                   for k, v in out['version'].items()}, ensure_ascii=False))

json.dump(out, open(os.path.join(OUT, 'AB2_metrics.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(os.path.join(OUT, 'AB2_metrics.md'), 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines))
