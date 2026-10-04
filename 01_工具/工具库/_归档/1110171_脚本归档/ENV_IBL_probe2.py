# -*- coding: utf-8 -*-
"""ENV_IBL_probe2.py — 只读：① 两皮肤 6 张 DDS 的排布/尺寸/mip ② cube_faces_mips.json 摘要
   ③ 面 PNG 与 DDS 逐面一致性。输出 ENV_IBL_probe2.txt"""
import hashlib, io, json, os, struct, sys
import numpy as np
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
W = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
SKINS = {'1110171': ['qiangpi', 'car_studio01', 'fashion_qiangpi'],
         '1110177': ['qiangpi', 'car_studio01', 'fashion_qiangpi']}
lines = []
res = {}


def load(path):
    b = open(path, 'rb').read()
    h, w, pitch = struct.unpack('<III', b[12:24])
    depth = struct.unpack('<I', b[24:28])[0]
    mips = struct.unpack('<I', b[28:32])[0]
    caps2 = struct.unpack('<I', b[112:116])[0]
    return b, w, h, depth, mips, caps2


def extract(b, w, h, mips, layout, face):
    if layout == 'face-major':
        off = 128 + face * sum(max(1, w >> m) * max(1, h >> m) * 4 for m in range(mips))
    else:
        off = 128 + face * w * h * 4
    return np.frombuffer(b, dtype=np.uint8, count=w * h * 4, offset=off).reshape(h, w, 4)


for skin, cubes in SKINS.items():
    res[skin] = {}
    lines.append('#### %s' % skin)
    for c in cubes:
        p = os.path.join(W, skin, 'src_cube', '%s.dds' % c)
        if not os.path.isfile(p):
            lines.append('   %-18s MISSING' % c)
            continue
        b, w, h, depth, mips, caps2 = load(p)
        sizes = [max(1, w >> m) for m in range(mips)]
        # layout 判定：mip-major 时 face i 的 mip0 与磁盘 m0 PNG 应逐像素一致
        best = {}
        for layout in ('mip-major', 'face-major'):
            tot = 0.0
            ok = 0
            for f in range(6):
                png = os.path.join(W, skin, 'src_cube', 'faces', '%s_f%d_m0.png' % (c, f))
                if not os.path.isfile(png):
                    continue
                arr = extract(b, w, h, mips, layout, f)[..., [2, 1, 0, 3]].astype(np.int16)
                pngarr = np.asarray(Image.open(png).convert('RGBA')).astype(np.int16)
                if arr.shape != pngarr.shape:
                    tot += 999
                    continue
                d = float(np.abs(arr - pngarr).mean())
                tot += d
                ok += 1
            best[layout] = {'mean_abs_sum': round(tot, 3), 'faces_compared': ok}
        layout = min(best.items(), key=lambda kv: kv[1]['mean_abs_sum'])[0]
        # 各级 mip 尺寸（面 0）从 PNG 文件检查
        mip_sizes = []
        for m in range(mips):
            pm = os.path.join(W, skin, 'src_cube', 'faces', '%s_f0_m%d.png' % (c, m))
            if os.path.isfile(pm):
                im = Image.open(pm)
                mip_sizes.append('%dx%d' % im.size)
            else:
                mip_sizes.append('missing')
        res[skin][c] = {'bytes': len(b), 'w': w, 'h': h, 'depth': depth, 'mips': mips, 'caps2': hex(caps2),
                        'cubemap': bool(caps2 & 0x200), 'faces_flag': [i for i in range(6) if caps2 & (0x400 << i)],
                        'inflated_bytes_expected': 128 + 6 * sum(max(1, w >> m) * max(1, h >> m) * 4 for m in range(mips)),
                        'layout_verdict': layout, 'layout_scores': best,
                        'mip_sizes_from_png_f0': mip_sizes,
                        'sha16': hashlib.sha256(b).hexdigest()[:16]}
        lines.append('   %-18s %dx%d mips=%d caps2=%s cubemap=%s faces=%s layout=%s(%s) png_mips=%s' % (
            c, w, h, mips, hex(caps2), bool(caps2 & 0x200), res[skin][c]['faces_flag'], layout,
            json.dumps(best, ensure_ascii=False), mip_sizes))

# cube_faces_mips.json 摘要
for skin in SKINS:
    p = os.path.join(W, skin, 'src_cube', 'cube_faces_mips.json')
    lines.append('')
    lines.append('#### %s/src_cube/cube_faces_mips.json exists=%s' % (skin, os.path.isfile(p)))
    if not os.path.isfile(p):
        continue
    j = json.load(open(p, encoding='utf-8'))
    res.setdefault('mips_json', {})[skin] = {}
    for cube, faces in j.items():
        lv = sorted({int(m) for f in faces for m in faces[f]})
        sizes = sorted({faces[f][str(m)]['size'] for f in faces for m in lv if str(m) in faces[f]})
        res['mips_json'][skin][cube] = {'n_faces': len(faces), 'levels': lv, 'sizes': sizes}
        lines.append('   %-18s faces=%d levels=%s sizes=%s' % (cube, len(faces), lv, sizes))

json.dump(res, open(os.path.join(OUT, 'ENV_IBL_probe2.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(os.path.join(OUT, 'ENV_IBL_probe2.txt'), 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines))
