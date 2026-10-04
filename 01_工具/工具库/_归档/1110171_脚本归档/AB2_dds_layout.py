# -*- coding: utf-8 -*-
"""AB2_dds_layout.py — 只读：判定 indoor.dds 的六面是 face-major 还是 mip-major 排布，
   并与磁盘 PNG 面建立最优 1:1 指派（4 翻转 × 2 通道序）。输出 AB2_dds_layout.json/.txt"""
import io, itertools, json, os, struct, sys
import numpy as np
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
W = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin\1110024'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'


def load(path):
    b = open(path, 'rb').read()
    h, w, pitch = struct.unpack('<III', b[12:24])
    mips = struct.unpack('<I', b[28:32])[0]
    return b, w, h, mips


def extract(b, w, h, mips, layout, face):
    if layout == 'face-major':
        off = 128 + face * sum(max(1, w >> m) * max(1, h >> m) * 4 for m in range(mips))
    else:  # mip-major
        off = 128 + face * w * h * 4
    raw = np.frombuffer(b, dtype=np.uint8, count=w * h * 4, offset=off).reshape(h, w, 4)
    return raw


def variants(raw):
    a = raw[..., [2, 1, 0, 3]].astype(np.int16)      # BGRA->RGBA
    b = raw.astype(np.int16)                          # as-is
    out = []
    for cname, x in (('bgra2rgba', a), ('as-is', b)):
        for fname, y in (('identity', x), ('vflip', x[::-1]), ('hflip', x[:, ::-1]), ('hvflip', x[::-1, ::-1])):
            out.append(('%s/%s' % (cname, fname), y[..., :3]))
    return out


res = {}
lines = []
for stem, fname in (('indoor', 'indoor.dds'), ('gdansk_shipyard_buildings', 'gdansk_shipyard_buildings.dds')):
    b, w, h, mips = load(os.path.join(W, 'src_cube', fname))
    pngs = [np.asarray(Image.open(os.path.join(W, 'src_cube', 'faces', '%s_f%d_m0.png' % (stem, j))).convert('RGB')).astype(np.int16)
            for j in range(6)]
    e = {}
    for layout in ('face-major', 'mip-major'):
        mat = np.full((6, 6), 1e9)
        conv = {}
        for i in range(6):
            raw = extract(b, w, h, mips, layout, i)
            for cname, v in variants(raw):
                for j in range(6):
                    if v.shape != pngs[j].shape:
                        continue
                    m = float(np.abs(v - pngs[j][..., :3]).mean())
                    if m < mat[i, j]:
                        mat[i, j] = m
                        conv[(i, j)] = cname
        # 最优 1:1 指派（暴力 6! = 720）
        best = None
        for perm in itertools.permutations(range(6)):
            s = sum(mat[i, perm[i]] for i in range(6))
            if best is None or s < best[0]:
                best = (s, perm)
        e[layout] = {'matrix_mean': [[round(float(mat[i, j]), 2) for j in range(6)] for i in range(6)],
                     'best_assign_sum': round(best[0], 2), 'best_assign_mean': round(best[0] / 6, 2),
                     'best_assign': [{'dds_face': i, 'png_face': best[1][i], 'conv': conv.get((i, best[1][i])),
                                      'mean_abs': round(float(mat[i, best[1][i]]), 2)} for i in range(6)]}
        lines.append('#### %s / %s：最优指派平均|ΔRGB| = %.2f' % (fname, layout, best[0] / 6))
        for it in e[layout]['best_assign']:
            lines.append('   DDS f%s → PNG f%s  [%s]  mean|Δ|=%.2f' % (it['dds_face'], it['png_face'], it['conv'], it['mean_abs']))
    res[stem] = e

json.dump(res, open(os.path.join(OUT, 'AB2_dds_layout.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(os.path.join(OUT, 'AB2_dds_layout.txt'), 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines))
