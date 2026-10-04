# -*- coding: utf-8 -*-
"""T5 step2：核对三项可复用的既有配方（只读 1110171 既有产物）：
  ① cube DDS(legacy B8G8R8A8, 6面, 8mip) → faces/<name>_f{i}_m0.png 的解码是否与 1110171 既有面一致
  ② param_repack_<fam>.png 的通道重排规则
  ③ rough_repack_<fam>.png 的通道重排规则
输出：_t5_rule_check.json
"""
import os, json, hashlib
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
S171 = r'E:\la拆包项目\04_站点\\web\assets\3d\weapon_skin\1110171'
OUT = {}


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def load_rgba(p):
    return np.asarray(Image.open(p).convert('RGBA')).astype(np.uint8)


def decode_cube_legacy(path):
    """legacy DDS cube: 128B header, 6 faces, mips; B8G8R8A8 → RGBA。"""
    d = open(path, 'rb').read()
    assert d[:4] == b'DDS ', 'not DDS'
    h = int.from_bytes(d[12:16], 'little'), int.from_bytes(d[16:20], 'little')
    hh, ww = h[0], h[1]
    caps2 = int.from_bytes(d[112:116], 'little')
    faces = bin(caps2).count('1') or 6
    off = 128
    out, pos = [], off
    for fi in range(6):
        m0 = np.frombuffer(d, dtype=np.uint8, count=ww * hh * 4, offset=pos).reshape(hh, ww, 4)
        rgba = m0[:, :, [2, 1, 0, 3]].copy()      # BGRA -> RGBA
        out.append(rgba)
        # advance one face
        w, hgt, sz = ww, hh, 0
        while w >= 1 and hgt >= 1:
            sz += w * hgt * 4
            w //= 2; hgt //= 2
        pos += sz
    return out, dict(width=ww, height=hh, caps2=hex(caps2), faces=faces, bytes=len(d))


# ① cube
for name in ('qiangpi', 'car_studio01'):
    ddsp = os.path.join(S171, 'src_cube', name + '.dds')
    faces, meta = decode_cube_legacy(ddsp)
    row = {'meta': meta, 'faces': []}
    for fi in range(6):
        mine = sha16(faces[fi].tobytes())
        ref_p = os.path.join(S171, 'src_cube', 'faces', '%s_f%d_m0.png' % (name, fi))
        ref = load_rgba(ref_p)
        same = bool(np.array_equal(faces[fi], ref))
        row['faces'].append({'f': fi, 'mine_sha16': mine, 'ref_sha16': sha16(ref.tobytes()), 'pixel_equal': same,
                             'shape': list(faces[fi].shape)})
    row['all_equal'] = all(x['pixel_equal'] for x in row['faces'])
    OUT['cube_' + name] = row
    print('cube %-14s faces_equal=%s  %s' % (name, row['all_equal'], meta))

# ② param_repack
for fam in ('010', '012'):
    m = load_rgba(os.path.join(S171, 'src_tex', '%s_m.png' % fam))
    pr = load_rgba(os.path.join(S171, 'src_tex', 'param_repack_%s.png' % fam))
    rule = {
        'R<-m.R': bool(np.array_equal(pr[:, :, 0], m[:, :, 0])),
        'R<-255': bool(np.array_equal(pr[:, :, 0], np.full_like(pr[:, :, 0], 255))),
        'G<-m.R': bool(np.array_equal(pr[:, :, 1], m[:, :, 0])),
        'G<-m.G': bool(np.array_equal(pr[:, :, 1], m[:, :, 1])),
        'B<-m.G': bool(np.array_equal(pr[:, :, 2], m[:, :, 1])),
        'B<-m.B': bool(np.array_equal(pr[:, :, 2], m[:, :, 2])),
        'A<-m.A': bool(np.array_equal(pr[:, :, 3], m[:, :, 3])),
        'A<-255': bool(np.array_equal(pr[:, :, 3], np.full_like(pr[:, :, 3], 255))),
    }
    OUT['param_repack_' + fam] = rule
    print('param_repack_%s: %s' % (fam, {k: v for k, v in rule.items() if v}))

# ③ rough_repack
for fam in ('010', '012'):
    a = load_rgba(os.path.join(S171, 'src_tex', '%s_a.png' % fam))
    rr = load_rgba(os.path.join(S171, 'src_tex', 'rough_repack_%s.png' % fam))
    rule = {
        'G<-a.A': bool(np.array_equal(rr[:, :, 1], a[:, :, 3])),
        'R<-255': bool(np.array_equal(rr[:, :, 0], np.full_like(rr[:, :, 0], 255))),
        'B<-255': bool(np.array_equal(rr[:, :, 2], np.full_like(rr[:, :, 2], 255))),
        'A<-255': bool(np.array_equal(rr[:, :, 3], np.full_like(rr[:, :, 3], 255))),
        'A<-a.A': bool(np.array_equal(rr[:, :, 3], a[:, :, 3])),
    }
    OUT['rough_repack_' + fam] = rule
    print('rough_repack_%s: %s' % (fam, {k: v for k, v in rule.items() if v}))

json.dump(OUT, open(os.path.join(HERE, '_t5_rule_check.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('[saved] _t5_rule_check.json')
