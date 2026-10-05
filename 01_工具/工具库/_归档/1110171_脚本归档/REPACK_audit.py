# -*- coding: utf-8 -*-
"""REPACK_audit.py — 逐皮肤核对 param_repack_*/rough_repack_* 的通道摆法是否自洽（只读）。
判据（源语义）：metal = sat(ParamMap.G) → three 读 metalnessMap.B；rough = clamp(ParamMap.R) → three 读 roughnessMap.G。
输出表：皮肤 × repack 文件 × R/G/B(/A) 均值与极值 × 与源同名通道的一致性 × 判定。
"""
import os, json, glob, collections
import numpy as np
from PIL import Image

WIKI = r'E:\la拆包项目\08Lifeafter wiki'
S3D = os.path.join(WIKI, 'assets', '3d', 'weapon_skin')
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
LEAD_SKINS = ['1110024', '1110129', '1110145', '1110152', '1110165', '1110171', '1110177']


def ch_stats(path):
    a = np.asarray(Image.open(path).convert('RGBA')).astype(np.float32)
    out = {}
    for i, c in enumerate('RGBA'):
        v = a[:, :, i]
        out[c] = {'mean': round(float(v.mean()), 1), 'min': round(float(v.min()), 1), 'max': round(float(v.max()), 1),
                  'std': round(float(v.std()), 1)}
    out['_size'] = list(a.shape[:2])
    return out


def load_param_src(skin):
    """从 neox_material.json 找 ParamMap 的 local_file。"""
    p = os.path.join(S3D, skin, 'neox_material.json')
    if not os.path.isfile(p):
        return None
    man = json.load(open(p, encoding='utf-8'))
    for pr in man.get('primitives', []):
        t = (pr.get('textures') or {}).get('ParamMap')
        if t and t.get('local_file'):
            return t['local_file']
    return None


rows = []
for skin in sorted(set(LEAD_SKINS) | {os.path.basename(d) for d in glob.glob(os.path.join(S3D, '1*')) if os.path.isdir(d)}):
    d = os.path.join(S3D, skin)
    if not os.path.isdir(d):
        continue
    src_tex = os.path.join(d, 'src_tex')
    rec = {'skin': skin, 'param': None, 'rough': None, 'src_param': load_param_src(skin), 'verdict': []}
    pm = sorted(glob.glob(os.path.join(src_tex, 'param_repack_*.png')))
    rm = sorted(glob.glob(os.path.join(src_tex, 'rough_repack_*.png')))
    srcp = os.path.join(WIKI, rec['src_param']) if rec['src_param'] else None
    psrc = ch_stats(srcp) if srcp and os.path.isfile(srcp) else None
    rec['src_param_stats'] = psrc
    # 源基色 alpha（用于 rough 来源判定）
    for cand in ('src_tex/012_a.png', 'src_tex/010_a.png', 'src_tex/024_a.png'):
        cp = os.path.join(WIKI, os.path.dirname(cand), cand.split('/')[-1]) if False else os.path.join(d, cand)
        if os.path.isfile(cp):
            rec['basecolor_alpha'] = ch_stats(cp)['A']
            break
    if pm:
        st = ch_stats(pm[0])
        rec['param'] = {'file': os.path.basename(pm[0]), 'stats': st}
        if psrc:
            rec['verdict'].append('param.B==src.G? %s (B均值 %.1f vs srcG %.1f)' % (
                abs(st['B']['mean'] - psrc['G']['mean']) < 1.5, st['B']['mean'], psrc['G']['mean']))
            rec['verdict'].append('param.G==src.R? %s (G均值 %.1f vs srcR %.1f)' % (
                abs(st['G']['mean'] - psrc['R']['mean']) < 1.5, st['G']['mean'], psrc['R']['mean']))
            rec['verdict'].append('param.B≡1(255)? %s (min %.1f max %.1f)' % (
                st['B']['min'] >= 254.5, st['B']['min'], st['B']['max']))
        rec['verdict'].append('param.R均值 %.1f / param.G均值 %.1f' % (st['R']['mean'], st['G']['mean']))
    if rm:
        st = ch_stats(rm[0])
        rec['rough'] = {'file': os.path.basename(rm[0]), 'stats': st}
        if psrc:
            rec['verdict'].append('rough.G==src.R? %s (G均值 %.1f vs srcR %.1f)' % (
                abs(st['G']['mean'] - psrc['R']['mean']) < 1.5, st['G']['mean'], psrc['R']['mean']))
        if rec.get('basecolor_alpha'):
            ba = rec['basecolor_alpha']
            rec['verdict'].append('rough.G==basecolor.alpha? %s (G均值 %.1f vs a %.1f)' % (
                abs(st['G']['mean'] - ba['mean']) < 1.5, st['G']['mean'], ba['mean']))
    rows.append(rec)

print('%-9s %-24s %-28s %-28s %s' % ('skin', 'param_repack', 'R/G/B (/255)', 'rough_repack G', '判定'))
for r in rows:
    ps = (r['param'] or {}).get('stats')
    rs = (r['rough'] or {}).get('stats')
    print('%-9s %-24s %-28s %-28s' % (r['skin'], (r['param'] or {}).get('file') or '-',
                                      ('R%.1f G%.1f B%.1f' % (ps['R']['mean'], ps['G']['mean'], ps['B']['mean'])) if ps else '-',
                                      ('G%.1f (min %.0f max %.0f)' % (rs['G']['mean'], rs['G']['min'], rs['G']['max'])) if rs else '-'))
    for v in r['verdict']:
        print('            · %s' % v)
    if r.get('src_param'):
        print('            src ParamMap = %s' % r['src_param'])
json.dump(rows, open(os.path.join(OUT, 'REPACK_audit.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\njson ->', os.path.join(OUT, 'REPACK_audit.json'))
