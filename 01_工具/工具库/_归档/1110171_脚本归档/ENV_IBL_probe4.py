# -*- coding: utf-8 -*-
"""ENV_IBL_probe4.py — 只读：① three 原 getIBLRadiance 正文（引用用）② 两皮肤 cube 资产跨皮肤同一性
   ③ 作者 mip vs 自动降采样差异 ④ 各 cube 的源 RGBM env 量级。输出 ENV_IBL_probe4.txt"""
import hashlib, io, json, os, re, sys
import numpy as np
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
W = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin'
THREE = r'E:\la拆包项目\08Lifeafter wiki\assets\vendor\three\three.module.min.js'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
lines = []
res = {}

# ① three 原 getIBLRadiance 正文
t = open(THREE, encoding='utf-8', errors='replace').read()
i = t.find('vec3 getIBLRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness )')
body = t[i:i + 700]
res['three_getIBLRadiance'] = body
lines.append('#### three r180 原 getIBLRadiance（vendor three.module.min.js @%d）' % i)
for ln in body.split('\\n')[:18]:
    lines.append('   ' + ln.replace('\t', '  ')[:200])

# ② 跨皮肤 cube 资产同一性
def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


cubes = ('qiangpi', 'car_studio01', 'fashion_qiangpi')
res['cube_hashes'] = {}
lines.append('')
lines.append('#### cube 资产 sha16（跨皮肤同一性）')
for c in cubes:
    row = {}
    for s in ('1110171', '1110177', '1110024', '1110129', '1110145'):
        p = os.path.join(W, s, 'src_cube', '%s.dds' % c)
        row[s] = sha16(p) if os.path.isfile(p) else None
    res['cube_hashes'][c] = row
    lines.append('   %-18s %s' % (c, json.dumps(row, ensure_ascii=False)))
# 面文件
res['face_hashes'] = {}
for c in cubes:
    for f in range(6):
        a = os.path.join(W, '1110171', 'src_cube', 'faces', '%s_f%d_m0.png' % (c, f))
        b = os.path.join(W, '1110177', 'src_cube', 'faces', '%s_f%d_m0.png' % (c, f))
        if os.path.isfile(a) and os.path.isfile(b):
            res['face_hashes']['%s_f%d' % (c, f)] = {'1110171': sha16(a), '1110177': sha16(b),
                                                     'same': sha16(a) == sha16(b)}
lines.append('   面 m0 同哈希：%s' % json.dumps({k: v['same'] for k, v in res['face_hashes'].items()}, ensure_ascii=False))

# ③ 作者 mip vs 自动降采样
lines.append('')
lines.append('#### 作者 mip vs m0 盒降采样（m1 64²）')
res['mip_vs_auto'] = {}
for s in ('1110171',):
    for c in cubes:
        rows = []
        for f in range(6):
            p0 = os.path.join(W, s, 'src_cube', 'faces', '%s_f%d_m0.png' % (c, f))
            p1 = os.path.join(W, s, 'src_cube', 'faces', '%s_f%d_m1.png' % (c, f))
            if not (os.path.isfile(p0) and os.path.isfile(p1)):
                rows.append({'face': f, 'authored_m1': os.path.isfile(p1)})
                continue
            a0 = np.asarray(Image.open(p0).convert('RGBA')).astype(np.float64)
            a1 = np.asarray(Image.open(p1).convert('RGBA')).astype(np.float64)
            h, w = a1.shape[:2]
            box = a0[:h * 2, :w * 2].reshape(h, 2, w, 2, 4).mean(axis=(1, 3))
            d = np.abs(box - a1)
            rows.append({'face': f, 'authored_m1': True, 'mean_abs_rgb': round(float(d[..., :3].mean()), 2),
                         'max_abs_rgb': int(d[..., :3].max()), 'alpha_mean_authored': round(float(a1[..., 3].mean()), 1),
                         'alpha_mean_box': round(float(box[..., 3].mean()), 1)})
        res['mip_vs_auto'][c] = rows
        lines.append('   %-18s %s' % (s + '/' + c, json.dumps(rows, ensure_ascii=False)[:600]))

# ④ 源 RGBM env 量级（每 cube 每面 + 均值）
lines.append('')
lines.append('#### 源 RGBM env 项 (rgb*a*16)^2 与六面均值')
res['env_term'] = {}
for s in ('1110171', '1110177'):
    for c in cubes:
        val = []
        for f in range(6):
            p0 = os.path.join(W, s, 'src_cube', 'faces', '%s_f%d_m0.png' % (c, f))
            if not os.path.isfile(p0):
                val.append(None)
                continue
            a = np.asarray(Image.open(p0).convert('RGBA')).astype(np.float64) / 255.0
            L = ((a[..., :3] * a[..., 3:4] * 16.0) ** 2).mean(axis=(0, 1))  # per-channel mean over pixels
            val.append([round(float(x), 4) for x in L])
        means = [v for v in val if v]
        res['env_term'][s + '/' + c] = {'per_face': val,
                                       'mean_over_faces': ([round(float(np.mean([v[k] for v in means])), 4) for k in range(3)] if means else None)}
        lines.append('   %-26s mean=%s per_face=%s' % (s + '/' + c, res['env_term'][s + '/' + c]['mean_over_faces'],
                                                      json.dumps(val, ensure_ascii=False)[:300]))

json.dump(res, open(os.path.join(OUT, 'ENV_IBL_probe4.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(os.path.join(OUT, 'ENV_IBL_probe4.txt'), 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines))
