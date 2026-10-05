# -*- coding: utf-8 -*-
"""AB_texdiff2.py — 深挖 `_a` vs `_b_m` 关系：线性拟合 / gamma 假设 / 通道置换矩阵（只读）→ AB_texdiff2.json/.txt"""
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
CH = 'RGBA'
res = {'pairs': []}
lines = []


def fit(x, y):
    x = x.astype(np.float64).ravel(); y = y.astype(np.float64).ravel()
    if x.std() < 1e-9:
        return None
    a, b = np.polyfit(x, y, 1)
    yh = a * x + b
    ss = ((y - y.mean()) ** 2).sum()
    r2 = float(1 - ((y - yh) ** 2).sum() / ss) if ss > 0 else None
    return {'slope': round(float(a), 4), 'intercept': round(float(b), 2), 'r2': (round(r2, 4) if r2 is not None else None)}


for skin, pairs in PAIRS.items():
    for a_name, b_name in pairs:
        pa = os.path.join(W, skin, 'src_tex', a_name)
        pb = os.path.join(W, skin, 'src_tex', b_name)
        if not (os.path.isfile(pa) and os.path.isfile(pb)):
            continue
        A = np.asarray(Image.open(pa).convert('RGBA')).astype(np.int16)
        B = np.asarray(Image.open(pb).convert('RGBA')).astype(np.int16)
        if A.shape != B.shape:
            continue
        e = {'skin': skin, 'a': a_name, 'b_m': b_name, 'same_index_fit': {}, 'gamma': {}, 'best_perm': [], 'alpha_relation': {}}
        for i, c in enumerate(CH):
            f = fit(A[..., i], B[..., i])
            if f:
                e['same_index_fit'][c] = f
            # gamma 假设：B = 255*(A/255)^g 与 A = 255*(B/255)^g 的最优 g
            x = A[..., i].astype(np.float64) / 255.0
            y = B[..., i].astype(np.float64) / 255.0
            nz = (x > 1e-6) & (y > 1e-6)
            if nz.sum() > 1000:
                g1 = float(np.exp(np.mean(np.log(y[nz]) / np.log(x[nz])))) if (x[nz] < 1).all() else None
                e['gamma']['B=A^g'] = (round(g1, 3) if g1 else None)
                g2 = float(np.exp(np.mean(np.log(x[nz]) / np.log(y[nz])))) if (y[nz] < 1).all() else None
                e['gamma']['A=B^g'] = (round(g2, 3) if g2 else None)
        # 通道置换/交叉最优（按线性 R²）
        for i, ca in enumerate(CH):
            row = []
            for j, cb in enumerate(CH):
                f = fit(A[..., i], B[..., j])
                if f and f['r2'] is not None:
                    row.append((f['r2'], '%s->%s' % (ca, cb), f['slope'], f['intercept']))
            row.sort(reverse=True)
            e['best_perm'].append({'a_chan': ca, 'top': [{'r2': r[0], 'pair': r[1], 'slope': r[2], 'intercept': r[3]} for r in row[:2]]})
        # alpha 关系（决定 rough_repack 来源的旁证）
        aA, bA = A[..., 3], B[..., 3]
        e['alpha_relation'] = {'a_alpha_mean': round(float(aA.mean()), 2), 'b_alpha_mean': round(float(bA.mean()), 2),
                               'corr': (round(float(np.corrcoef(aA, bA)[0, 1]), 4) if aA.std() > 0 and bA.std() > 0 else None),
                               'eq_within2_pct': round(float(100.0 * (np.abs(aA - bA) <= 2).mean()), 2),
                               'a_B_mean': round(float(A[..., 2].mean()), 2), 'b_A_mean': round(float(B[..., 3].mean()), 2),
                               'b_A_equals_a_B_pct': round(float(100.0 * (np.abs(B[..., 3] - A[..., 2]) <= 2).mean()), 2)}
        res['pairs'].append(e)
        lines.append('%s %s -> %s' % (skin, a_name, b_name))
        lines.append('   same-index fit: ' + json.dumps(e['same_index_fit'], ensure_ascii=False))
        lines.append('   best cross pair per A-chan: ' + json.dumps(e['best_perm'], ensure_ascii=False)[:400])
        lines.append('   alpha: ' + json.dumps(e['alpha_relation'], ensure_ascii=False))
        lines.append('   gamma: ' + json.dumps(e['gamma'], ensure_ascii=False))

json.dump(res, open(os.path.join(OUT, 'AB_texdiff2.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(os.path.join(OUT, 'AB_texdiff2.txt'), 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines))
