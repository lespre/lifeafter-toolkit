# -*- coding: utf-8 -*-
"""AB2_precheck.py — task-23 先决核查（只读）：
   ① 1110024 的 indoor.dds / gdansk.dds 结构 + 六面 PNG 是否齐全且互异
   ② manifest 的 t_custom_ibl（含 faces_glob）
   ③ c159 直证逐条：(t_basecolor 声明、1110145 logical_path 取块、indoor.cube 字节位次)
   输出 AB2_precheck.txt / AB2_precheck.json
"""
import glob, hashlib, io, json, os, struct, sys
import numpy as np
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
W = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
C159DIRS = [r'E:\la拆包项目\03拆包产物\weapon', r'E:\la拆包项目\03拆包产物', r'E:\la拆包项目\01拆包器本体\工具库\06_皮肤定位链']
res = {'faces': {}, 'dds': {}, 'manifest': {}, 'c159': {}}
lines = []

# ── ① 磁盘：src_cube 内容
for skin in ('1110024',):
    d = os.path.join(W, skin, 'src_cube')
    files = sorted(os.path.relpath(p, os.path.join(W, skin)) for p in glob.glob(os.path.join(d, '**', '*'), recursive=True) if os.path.isfile(p))
    res['faces'][skin] = files
    lines.append('#### %s src_cube 内容：' % skin)
    for f in files:
        p = os.path.join(W, skin, f)
        lines.append('   %-46s %9d B  sha16=%s' % (f, os.path.getsize(p), hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]))


def dds_info(p):
    b = open(p, 'rb').read()
    if b[:4] != b'DDS ':
        return {'error': 'not_dds'}
    flags, h, w, pitch, depth, mips = struct.unpack('<6I', b[8:32])
    pf = b[76:108]
    pf_flags, fourcc, rgbbits = struct.unpack('<I4sI', pf[:12])
    caps, caps2 = struct.unpack('<II', b[108:116])
    faces = [i for i in range(6) if caps2 & (0x400 << i)]
    return {'bytes': len(b), 'w': w, 'h': h, 'depth': depth, 'mips': mips,
            'pf_flags': hex(pf_flags), 'fourcc': fourcc.decode('latin1').strip('\x00'),
            'rgbbits': rgbbits, 'caps': hex(caps), 'caps2': hex(caps2),
            'cubemap_caps2_flag': bool(caps2 & 0x200), 'faces_present': faces,
            'header_hex_snippet': b[:4].decode('latin1')}


for name in ('indoor.dds', 'gdansk_shipyard_buildings.dds'):
    p = os.path.join(W, '1110024', 'src_cube', name)
    res['dds'][name] = dds_info(p) if os.path.isfile(p) else {'error': 'missing'}
    lines.append('#### DDS %s → %s' % (name, json.dumps(res['dds'][name], ensure_ascii=False)))

# face PNG 齐全性 + 互异性
for stem in ('indoor', 'gdansk_shipyard_buildings'):
    rows = []
    arrs = []
    for i in range(6):
        p = os.path.join(W, '1110024', 'src_cube', 'faces', '%s_f%d_m0.png' % (stem, i))
        if os.path.isfile(p):
            a = np.asarray(Image.open(p).convert('RGB')).astype(np.int16)
            arrs.append((i, a, p))
            rows.append({'face': i, 'exists': True, 'size': [a.shape[1], a.shape[0]],
                         'sha16': hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16],
                         'mean_rgb': [round(float(a[..., c].mean()), 1) for c in range(3)]})
        else:
            rows.append({'face': i, 'exists': False})
    pairwise = []
    for x in range(len(arrs)):
        for y in range(x + 1, len(arrs)):
            if arrs[x][1].shape == arrs[y][1].shape:
                d = np.abs(arrs[x][1] - arrs[y][1])
                pairwise.append({'pair': 'f%d-f%d' % (arrs[x][0], arrs[y][0]),
                                 'identical_pct': round(float(100.0 * (d.max(axis=2) == 0).mean()), 2),
                                 'mean_abs': round(float(d.mean()), 2)})
    res['faces']['facesets'] = res['faces'].get('facesets', {})
    res['faces']['facesets'][stem] = {'rows': rows, 'pairwise': pairwise,
                                      'complete': all(r.get('exists') for r in rows),
                                      'all_distinct': all(pw['identical_pct'] < 1.0 for pw in pairwise) if pairwise else None}
    lines.append('#### faces/%s_* → complete=%s distinct=%s' % (stem, res['faces']['facesets'][stem]['complete'],
                                                               res['faces']['facesets'][stem]['all_distinct']))
    for r in rows:
        lines.append('   f%s exists=%s %s' % (r['face'], r.get('exists'), json.dumps({k: v for k, v in r.items() if k not in ('face', 'exists')}, ensure_ascii=False)))
    for pw in pairwise:
        lines.append('   pair %s identical=%.2f%% mean|Δ|=%.2f' % (pw['pair'], pw['identical_pct'], pw['mean_abs']))

# ── ② manifest t_custom_ibl（7 皮肤全列）
for skin in ('1110024', '1110129', '1110145', '1110152', '1110165', '1110171', '1110177'):
    d = json.load(open(os.path.join(W, skin, 'neox_material.json'), encoding='utf-8'))
    rows = []
    for i, pr in enumerate(d.get('primitives', [])):
        t = (pr.get('textures') or {}).get('t_custom_ibl')
        if t is None:
            continue
        rows.append({'prim': i, 'kind': pr.get('shader_kind'), 'local_file': t.get('local_file'),
                     'logical': t.get('logical_path') or t.get('logical'), 'faces_glob': t.get('faces_glob'),
                     'state': t.get('state'), 'evidence': (t.get('evidence') or '')[:140]})
    res['manifest'][skin] = rows
    lines.append('#### manifest %s t_custom_ibl：' % skin)
    for r in rows:
        lines.append('   prim%-2s %-8s local=%-42s glob=%-40s logical=%s' % (
            r['prim'], r['kind'], r['local_file'], r['faces_glob'], r['logical']))

# ── ③ c159 直证
c159fixed = json.load(open(os.path.join(OUT, 'C159PARSE_skins_fixed.json'), encoding='utf-8'))
for key in ('1110177', '1110171_dual', '1110145', '1110024'):
    rows = c159fixed.get(key, {}).get('rows', [])
    res['c159'][key] = {'file': c159fixed.get(key, {}).get('file'), 'rows': rows}
    lines.append('#### c159 %s (%s) rows=%d' % (key, c159fixed.get(key, {}).get('file'), len(rows)))
    for r in rows:
        lines.append('   blk%-2s %-16s ref=%-46s off=%s dual=%s order_only=%s' % (
            r.get('material_block'), r.get('slot_class'), r.get('ref'), r.get('off'), r.get('dual_proof'), r.get('agree_by_order_only')))
    tb = [r for r in rows if r.get('slot_class') == 't_basecolor']
    lines.append('   ⇒ t_basecolor 声明条数 = %d %s' % (len(tb), [(r['material_block'], r['ref']) for r in tb]))

# c159 原始文件里的字节位次（indoor.cube / gdansk / 014001a|b_m / t_basecolor 名）
found = {}
for name in ('001386.c159', '000654.c159', '003996.c159', '001265.c159'):
    p = next((os.path.join(d0, name) for d0 in C159DIRS if os.path.isfile(os.path.join(d0, name))), None)
    if not p:
        found[name] = {'error': 'file_not_found', 'searched': C159DIRS}
        continue
    raw = open(p, 'rb').read()
    hits = {}
    for tok in (b'indoor.cube', b'gdansk', b'014001a', b'014001b_m', b't_basecolor', b'029001a', b'029001b_m', b'skin_1003_010001a', b'skin_1003_012001a'):
        offs = []
        st = 0
        while True:
            k = raw.find(tok, st)
            if k < 0:
                break
            offs.append(k)
            st = k + 1
        if offs:
            hits[tok.decode('latin1')] = {'count': len(offs), 'offsets': offs[:12]}
    found[name] = {'path': p, 'bytes': len(raw), 'hits': hits}
res['c159']['raw_files'] = found
lines.append('#### c159 原始文件字节命中：')
for k, v in found.items():
    lines.append('   %s → %s' % (k, json.dumps({kk: vv for kk, vv in v.items() if kk != 'hits'}, ensure_ascii=False)))
    for tok, hv in (v.get('hits') or {}).items():
        lines.append('      %-22s count=%-3d offsets=%s' % (tok, hv['count'], hv['offsets']))

json.dump(res, open(os.path.join(OUT, 'AB2_precheck.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(os.path.join(OUT, 'AB2_precheck.txt'), 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines[:120]))
print('... -> AB2_precheck.txt/.json')
