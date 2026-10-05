# -*- coding: utf-8 -*-
"""AB2_dds_verify.py — 只读：解 indoor.dds / gdansk.dds 的 6 个 mip0 面，与磁盘上的 *_f{i}_m0.png 逐面比对，
   判定「黑面」是源资产本来如此，还是导出/提取产物。输出 AB2_dds_verify.json/.txt（不生成任何渲染用面）。"""
import hashlib, io, json, os, struct, sys
import numpy as np
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
W = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'


def decode_cube(path):
    b = open(path, 'rb').read()
    assert b[:4] == b'DDS '
    h, w, pitch = struct.unpack('<III', b[12:24])
    mips = struct.unpack('<I', b[28:32])[0]
    face_size = sum(max(1, w >> m) * max(1, h >> m) * 4 for m in range(max(1, mips)))
    faces = []
    for i in range(6):
        off = 128 + i * face_size
        raw = np.frombuffer(b, dtype=np.uint8, count=w * h * 4, offset=off).reshape(h, w, 4)
        faces.append(raw[..., [2, 1, 0, 3]].copy())  # BGRA -> RGBA
    return {'w': w, 'h': h, 'mips': mips, 'face_size': face_size, 'faces': faces, 'bytes': len(b)}


def cmp(a, b):
    """RGB-only（排除 alpha 干扰，单独报 alpha 统计）"""
    a3, b3 = a[..., :3], b[..., :3]
    out = {}
    for name, x in (('identity', a3), ('vflip', a3[::-1]), ('hflip', a3[:, ::-1]), ('hvflip', a3[::-1, ::-1])):
        d = np.abs(x.astype(np.int16) - b3.astype(np.int16))
        out[name] = {'max': int(d.max()), 'mean': round(float(d.mean()), 3),
                     'identical_pct': round(float(100.0 * (d.max(axis=2) == 0).mean()), 2),
                     'near2_pct': round(float(100.0 * (d.max(axis=2) <= 2).mean()), 2)}
    return out


res = {}
lines = []
for stem, fname in (('indoor', 'indoor.dds'), ('gdansk_shipyard_buildings', 'gdansk_shipyard_buildings.dds')):
    dds = decode_cube(os.path.join(W, '1110024', 'src_cube', fname))
    e = {'dds': {'w': dds['w'], 'h': dds['h'], 'mips': dds['mips'], 'bytes': dds['bytes']}, 'faces': []}
    lines.append('#### %s（%dx%d, mips=%d）' % (fname, dds['w'], dds['h'], dds['mips']))
    # 6x6 匹配矩阵（DDS 面 × PNG 面，RGB-only，取四种翻转里最优）
    pngfaces = []
    for j in range(6):
        p = os.path.join(W, '1110024', 'src_cube', 'faces', '%s_f%d_m0.png' % (stem, j))
        pngfaces.append(np.asarray(Image.open(p).convert('RGBA')) if os.path.isfile(p) else None)
    matrix = []
    for i in range(6):
        best_j, best = None, None
        rowm = []
        for j in range(6):
            if pngfaces[j] is None or pngfaces[j].shape != dds['faces'][i].shape:
                rowm.append(None)
                continue
            c = cmp(dds['faces'][i], pngfaces[j])
            bn = min(c.items(), key=lambda kv: kv[1]['mean'])
            rowm.append({'png_face': j, 'conv': bn[0], 'mean': bn[1]['mean'], 'identical_pct': bn[1]['identical_pct']})
            if best is None or bn[1]['mean'] < best['mean']:
                best = {'png_face': j, 'conv': bn[0], 'mean': bn[1]['mean'], 'identical_pct': bn[1]['identical_pct']}
        matrix.append({'dds_face': i, 'row': rowm, 'best': best})
        lines.append('   DDS f%d → best PNG f%s (%s) mean|Δ|=%.2f identical=%.2f%%' % (
            i, best['png_face'] if best else '?', best['conv'] if best else '?',
            best['mean'] if best else -1, best['identical_pct'] if best else -1))
    e['matrix'] = matrix
    e['png_alpha_mean'] = [(round(float(f[..., 3].mean()), 1) if f is not None else None) for f in pngfaces]
    lines.append('   PNG alpha 均值逐面: %s ｜ DDS alpha 均值逐面: %s' % (
        e['png_alpha_mean'], [round(float(dds['faces'][i][..., 3].mean()), 1) for i in range(6)]))
    for i in range(6):
        face = dds['faces'][i]
        png_p = os.path.join(W, '1110024', 'src_cube', 'faces', '%s_f%d_m0.png' % (stem, i))
        row = {'face': i, 'dds_mean_rgb': [round(float(face[..., c].mean()), 1) for c in range(3)],
               'dds_mean_a': round(float(face[..., 3].mean()), 1),
               'dds_all_black': bool(face[..., :3].max() == 0)}
        if os.path.isfile(png_p):
            png = np.asarray(Image.open(png_p).convert('RGBA'))
            row['png_mean_rgb'] = [round(float(png[..., c].mean()), 1) for c in range(3)]
            row['png_all_black'] = bool(png[..., :3].max() == 0)
            row['cmp'] = cmp(face, png) if png.shape == face.shape else 'shape_mismatch'
            best = min(row['cmp'].items(), key=lambda kv: kv[1]['mean']) if isinstance(row['cmp'], dict) else None
            row['best_convention'] = ({'name': best[0], **best[1]} if best else None)
        e['faces'].append(row)
        lines.append('   f%d dds_mean=%s a=%.1f black=%s | png_mean=%s black=%s | best=%s' % (
            i, row['dds_mean_rgb'], row['dds_mean_a'], row['dds_all_black'], row.get('png_mean_rgb'),
            row.get('png_all_black'), json.dumps(row.get('best_convention'), ensure_ascii=False)))
    res[stem] = e

json.dump(res, open(os.path.join(OUT, 'AB2_dds_verify.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(os.path.join(OUT, 'AB2_dds_verify.txt'), 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines))
