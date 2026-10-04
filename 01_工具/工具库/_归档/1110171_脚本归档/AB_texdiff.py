# -*- coding: utf-8 -*-
"""AB_texdiff.py — `_a.png` vs `_b_m.png` 像素级差异（只读磁盘贴图）→ AB_texdiff.json/.txt。
   回答：是不是同一张图的不同打包？（跨通道等式扫描 + 逐通道统计 + alpha 分布）"""
import io, json, os, sys
import numpy as np
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
W = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
PAIRS = {
    '1110024': [('024_a.png', '024_b_m.png')],
    '1110129': [('008_a.png', '008_b_m.png'), ('008_c_a.png', '008_c_b_m.png'), ('008_d_a.png', '008_d_b_m.png'),
                ('008_e_a.png', '008_e_b_m.png'), ('008_f_a.png', '008_f_b_m.png')],
    '1110145': [('014_a.png', '014_b_m.png')],
    '1110152': [('009_a.png', '009_b_m.png'), ('009_c_a.png', '009_c_b_m.png')],
    '1110165': [('165_a.png', '165_b_m.png'), ('165_c_a.png', '165_c_b_m.png')],
    '1110171': [('012_a.png', '012_b_m.png'), ('010_a.png', '010_b_m.png')],
    '1110177': [('029_a.png', '029_b_m.png')],
}


def stats(arr):
    out = {}
    for i, ch in enumerate('RGBA'):
        c = arr[..., i].astype(np.float64)
        out[ch] = {'mean': round(float(c.mean()), 2), 'p50': float(np.percentile(c, 50)),
                   'p95': float(np.percentile(c, 95)), 'std': round(float(c.std()), 2),
                   'eq255_pct': round(float(100.0 * (c >= 255).mean()), 2),
                   'eq0_pct': round(float(100.0 * (c <= 0).mean()), 2)}
    return out


res = {'pairs': []}
lines = []
for skin, pairs in PAIRS.items():
    for a_name, b_name in pairs:
        pa = os.path.join(W, skin, 'src_tex', a_name)
        pb = os.path.join(W, skin, 'src_tex', b_name)
        if not (os.path.isfile(pa) and os.path.isfile(pb)):
            res['pairs'].append({'skin': skin, 'a': a_name, 'b_m': b_name, 'error': 'missing_on_disk',
                                 'a_exists': os.path.isfile(pa), 'b_exists': os.path.isfile(pb)})
            lines.append('%s %s vs %s : MISSING (a=%s b=%s)' % (skin, a_name, b_name, os.path.isfile(pa), os.path.isfile(pb)))
            continue
        ia, ib = Image.open(pa).convert('RGBA'), Image.open(pb).convert('RGBA')
        A = np.asarray(ia).astype(np.int16)
        B = np.asarray(ib).astype(np.int16)
        e = {'skin': skin, 'a': a_name, 'b_m': b_name, 'a_size': list(ia.size), 'b_size': list(ib.size),
             'a_mode': Image.open(pa).mode, 'b_mode': Image.open(pb).mode,
             'a_stats': stats(A), 'b_stats': stats(B), 'cross_channel': {}}
        if ia.size == ib.size:
            e['same_size'] = True
            diff = np.abs(A - B)
            e['identical_pixels_pct'] = round(float(100.0 * (diff.max(axis=2) == 0).mean()), 2)
            e['near_identical_pct'] = round(float(100.0 * (diff.max(axis=2) <= 2).mean()), 2)
            e['mean_abs_diff_rgb'] = [round(float(diff[..., i].mean()), 2) for i in range(3)]
            # 跨通道等式扫描：A 的哪个通道 ≈ B 的哪个通道（±2）
            for i, ca in enumerate('RGBA'):
                for j, cb in enumerate('RGBA'):
                    eq = float(100.0 * (np.abs(A[..., i] - B[..., j]) <= 2).mean())
                    if eq >= 95.0:
                        e['cross_channel']['%s~%s' % (ca, cb)] = round(eq, 2)
            # 线性关系候选：B.k ≈ f(A.k)
            for i, ch in enumerate('RGBA'):
                av = A[..., i].astype(np.float64); bv = B[..., i].astype(np.float64)
                if av.std() > 1e-6 and bv.std() > 1e-6:
                    c = float(np.corrcoef(av, bv)[0, 1])
                    if c > 0.5:
                        e.setdefault('per_channel_corr', {})[ch] = round(c, 4)
            # B 的第 4 通道是否为常数
            e['b_alpha_const'] = bool(B[..., 3].std() < 0.5)
            e['a_alpha_const'] = bool(A[..., 3].std() < 0.5)
        else:
            e['same_size'] = False
        res['pairs'].append(e)
        lines.append('%s %s(%s) vs %s(%s): same_size=%s identical=%.2f%% near<=2=%.2f%% meanAbsRGB=%s a_meanRGBA=%s b_meanRGBA=%s' % (
            skin, a_name, e['a_size'], b_name, e['b_size'], e.get('same_size'),
            e.get('identical_pixels_pct', -1), e.get('near_identical_pct', -1), e.get('mean_abs_diff_rgb'),
            [e['a_stats'][c]['mean'] for c in 'RGBA'], [e['b_stats'][c]['mean'] for c in 'RGBA']))
        if e.get('cross_channel'):
            lines.append('     cross-channel ~>=95%%: %s ; per-channel corr: %s' % (
                json.dumps(e['cross_channel'], ensure_ascii=False), json.dumps(e.get('per_channel_corr', {}), ensure_ascii=False)))
        lines.append('     a alpha: mean=%.1f eq255=%.2f%% eq0=%.2f%% std=%.1f const=%s | b alpha: mean=%.1f eq255=%.2f%% eq0=%.2f%% std=%.1f const=%s' % (
            e['a_stats']['A']['mean'], e['a_stats']['A']['eq255_pct'], e['a_stats']['A']['eq0_pct'], e['a_stats']['A']['std'], e.get('a_alpha_const'),
            e['b_stats']['A']['mean'], e['b_stats']['A']['eq255_pct'], e['b_stats']['A']['eq0_pct'], e['b_stats']['A']['std'], e.get('b_alpha_const')))

json.dump(res, open(os.path.join(OUT, 'AB_texdiff.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(os.path.join(OUT, 'AB_texdiff.txt'), 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines))
