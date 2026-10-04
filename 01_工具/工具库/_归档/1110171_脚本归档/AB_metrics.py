# -*- coding: utf-8 -*-
"""AB_metrics.py — 读 AB_raw_<A|B>_r<1|2>.json + AB_<skin>_<G>.png，算固定布局下的武器区指标（只读）。"""
import io, json, os, sys
import numpy as np
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
SKINS = ['1110024', '1110129', '1110145', '1110152', '1110165', '1110171', '1110177']
BG = (7, 16, 21)  # viewer.json background #071015


def lum(a):
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def bbox_of(proj, w, h):
    if not proj:
        return None
    x0 = max(0, int(proj['x0'] * w) - 2); x1 = min(w, int(proj['x1'] * w) + 3)
    y0 = max(0, int(proj['y0'] * h) - 2); y1 = min(h, int(proj['y1'] * h) + 3)
    if x1 <= x0 or y1 <= y0:
        return None
    return [x0, y0, x1, y1]


def metrics(arr, bb):
    sub = arr[bb[1]:bb[3], bb[0]:bb[2], :3].astype(np.float64)
    L = lum(sub)
    bgp10 = float(np.percentile(L, 10))
    thr = bgp10 * 1.35
    nb = float((L > thr).mean() * 100)
    r, g, b = sub[..., 0], sub[..., 1], sub[..., 2]
    gold = float(((r > g) & (g > b) & ((r - b) > 25)).mean() * 100)
    silver = float((((np.abs(r - g) < 12) & (np.abs(g - b) < 12) & (L > 90))).mean() * 100)
    vio = float(((b > r) & (r > g) & ((b - g) > 25)).mean() * 100)
    return {'pixels': int(sub.shape[0] * sub.shape[1]), 'mean_rgb': [round(float(sub[..., i].mean()), 2) for i in range(3)],
            'p50': round(float(np.percentile(L, 50)), 1), 'p95': round(float(np.percentile(L, 95)), 1),
            'bg_p10': round(bgp10, 1), 'nonbg_pct': round(nb, 2),
            'gold_pct': round(gold, 2), 'silver_pct': round(silver, 2), 'violet_pct': round(vio, 2)}


out = {'runs': {}, 'skins': {}}
raws = {}
for grp in ('A', 'B'):
    for rep in ('1', '2'):
        p = os.path.join(OUT, 'AB_raw_%s_r%s.json' % (grp, rep))
        if os.path.isfile(p):
            raws['%s%s' % (grp, rep)] = json.load(open(p, encoding='utf-8'))
out['runs'] = {k: {'viewer_sha': v.get('skins', {}).get(SKINS[0], {}).get('viewer_sha'),
                   'install': v.get('install'), 'a_map': v.get('a_map'),
                   'buffer': {s: (v['skins'][s].get('state') or '') for s in v.get('skins', {})}}
               for k, v in raws.items()}

lines = []
lines.append('| skin | A p50 | B p50 | Δp50 | A p95 | B p95 | Δp95 | A 非背景% | B 非背景% | Δ非背景 | 变化像素% | 平均|Δ| | A sha16 | B sha16 |')
lines.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for s in SKINS:
    e = {}
    for grp in ('A', 'B'):
        p = os.path.join(OUT, 'AB_%s_%s.png' % (s, grp))
        if not os.path.isfile(p):
            e[grp] = None
            continue
        arr = np.asarray(Image.open(p).convert('RGBA'))
        proj = None
        rj = raws.get('%s1' % grp)
        if rj and s in rj['skins']:
            st = rj['skins'][s].get('state')
            if isinstance(st, str) and st.startswith('{'):
                proj = json.loads(st).get('proj')
        bb = bbox_of(proj, arr.shape[1], arr.shape[0]) or [0, 0, arr.shape[1], arr.shape[0]]
        e[grp] = {'metrics': metrics(arr, bb), 'bbox': bb, 'proj': proj,
                  'sha16': rj['skins'][s].get('png_sha16') if rj else None,
                  'size': [arr.shape[1], arr.shape[0]]}
    if e.get('A') and e.get('B'):
        pa, pb = os.path.join(OUT, 'AB_%s_A.png' % s), os.path.join(OUT, 'AB_%s_B.png' % s)
        A = np.asarray(Image.open(pa).convert('RGB')).astype(np.int16)
        B = np.asarray(Image.open(pb).convert('RGB')).astype(np.int16)
        d = np.abs(A - B).max(axis=2)
        bb = e['A']['bbox']
        sub = d[bb[1]:bb[3], bb[0]:bb[2]]
        e['delta'] = {'changed_pct_img': round(float(100.0 * (d > 15).mean()), 2),
                      'changed_pct_bbox': round(float(100.0 * (sub > 15).mean()), 2),
                      'mean_abs_bbox': round(float(sub.mean()), 1)}
    out['skins'][s] = e
    ma, mb = (e.get('A') or {}).get('metrics'), (e.get('B') or {}).get('metrics')
    if ma and mb:
        lines.append('| %s | %s | %s | %+.1f | %s | %s | %+.1f | %s | %s | %+.2f | %s | %s | %s | %s |' % (
            s, ma['p50'], mb['p50'], ma['p50'] - mb['p50'], ma['p95'], mb['p95'], ma['p95'] - mb['p95'],
            ma['nonbg_pct'], mb['nonbg_pct'], ma['nonbg_pct'] - mb['nonbg_pct'],
            e['delta']['changed_pct_bbox'], e['delta']['mean_abs_bbox'], e['A']['sha16'], e['B']['sha16']))
    else:
        lines.append('| %s | missing | | | | | | | | | | | | |' % s)

# 复现性
lines.append('')
lines.append('| skin | A r1 sha16 | A r2 sha16 | A 复现 | B r1 sha16 | B r2 sha16 | B 复现 |')
lines.append('|---|---|---|---|---|---|---|')
for s in SKINS:
    a1 = (raws.get('A1', {}).get('skins', {}).get(s) or {}).get('png_sha16')
    a2 = (raws.get('A2', {}).get('skins', {}).get(s) or {}).get('png_sha16')
    b1 = (raws.get('B1', {}).get('skins', {}).get(s) or {}).get('png_sha16')
    b2 = (raws.get('B2', {}).get('skins', {}).get(s) or {}).get('png_sha16')
    lines.append('| %s | %s | %s | %s | %s | %s | %s |' % (s, a1, a2, 'YES' if a1 == a2 else 'NO', b1, b2, 'YES' if b1 == b2 else 'NO'))

# 布局恒定证据
lines.append('')
lines.append('布局：' + json.dumps({k: {s: (v['skins'][s].get('snapshot') or {}).get('w') if isinstance(v['skins'][s].get('snapshot'), dict) else None for s in v['skins']} for k, v in raws.items()}, ensure_ascii=False))

json.dump(out, open(os.path.join(OUT, 'AB_metrics.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(os.path.join(OUT, 'AB_metrics.md'), 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines))
