# -*- coding: utf-8 -*-
"""AB_prep.py — 只读：导出 7 皮肤的槽位绑定 + `_a` 对应文件存在性 + c159 工件清单 → AB_bindings.json / AB_prep.txt。"""
import glob, hashlib, io, json, os, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
W = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
SKINS = ['1110024', '1110129', '1110145', '1110152', '1110165', '1110171', '1110177']
SLOTS = ['Tex0', 't_basecolor', 'ParamMap', 'NormalMap', 't_custom_ibl', 't_surfacemap', 'DetailMap']


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


res = {'skins': {}, 'c159_artifacts': []}
for s in SKINS:
    d = json.load(open(os.path.join(W, s, 'neox_material.json'), encoding='utf-8'))
    rows = []
    for i, pr in enumerate(d.get('primitives', [])):
        T = pr.get('textures') or {}
        row = {'prim': i, 'material': pr.get('material'), 'shader': pr.get('shader'),
               'kind': (str(pr.get('shader_kind') or '').lower() or ('crystal' if 'crystal' in str(pr.get('shader') or '') else 'weapon')),
               'slots': {}, 'req': pr.get('required_slots'), 'missing': pr.get('missing_required')}
        for k in SLOTS:
            v = T.get(k)
            if v is None:
                row['slots'][k] = None
                continue
            lf = v.get('local_file')
            e = {'local_file': lf, 'logical_path': v.get('logical_path'), 'slot_field': v.get('slot'),
                 'confidence': v.get('confidence'), 'binding_basis': v.get('binding_basis'),
                 'why_not_direct': v.get('why_not_direct'), 'evidence': (v.get('evidence') or '')[:160],
                 'group_index': v.get('GROUP_INDEX', v.get('group_index')), 'pos_in_group': v.get('POS_IN_GROUP', v.get('pos_in_group')),
                 'src_sha16': v.get('rgba_sha16') or v.get('local_sha16') or (v.get('sha256') or '')[:16] or v.get('rgba_sha256')}
            if lf:
                p = os.path.join(W, s, lf.replace('/', os.sep))
                e['on_disk'] = os.path.isfile(p)
                e['disk_sha16'] = sha16(p) if e['on_disk'] else None
                e['disk_bytes'] = os.path.getsize(p) if e['on_disk'] else None
                if k == 'Tex0' and lf.endswith('_b_m.png'):
                    a = lf.replace('_b_m.png', '_a.png')
                    pa = os.path.join(W, s, a.replace('/', os.sep))
                    e['A_local_file'] = a
                    e['A_on_disk'] = os.path.isfile(pa)
                    e['A_sha16'] = sha16(pa) if e['A_on_disk'] else None
                    e['A_bytes'] = os.path.getsize(pa) if e['A_on_disk'] else None
                    e['text_diff'] = '%s vs %s' % (os.path.basename(a), os.path.basename(lf))
            row['slots'][k] = e
        rows.append(row)
    res['skins'][s] = {'file': os.path.join(W, s, 'neox_material.json'), 'sha16': sha16(os.path.join(W, s, 'neox_material.json')),
                       'top_keys': sorted(d.keys()), 'block_rule': d.get('block_rule'), 'source': d.get('source'),
                       'slot_binding_basis': d.get('slot_binding_basis'), 'observed_but_unbound': d.get('observed_but_unbound'),
                       'prims': rows}

# c159 工件搜索（限定目录，避免全树 glob 超时）
for base in (OUT, r'E:\la拆包项目\01拆包器本体\工具库\06_皮肤定位链', r'E:\la拆包项目\03拆包产物'):
    try:
        entries = os.listdir(base)
    except Exception:
        continue
    for e in entries:
        low = e.lower()
        if 'c159' in low or '槽位直证' in e or 'straight' in low:
            p = os.path.join(base, e)
            res['c159_artifacts'].append({'path': p, 'dir': os.path.isdir(p), 'bytes': (os.path.getsize(p) if os.path.isfile(p) else None)})

json.dump(res, open(os.path.join(OUT, 'AB_bindings.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

lines = []
for s in SKINS:
    lines.append('#### %s  manifest sha16=%s' % (s, res['skins'][s]['sha16']))
    lines.append('   block_rule=%s | slot_binding_basis=%s' % (json.dumps(res['skins'][s]['block_rule'], ensure_ascii=False)[:200], json.dumps(res['skins'][s]['slot_binding_basis'], ensure_ascii=False)[:300]))
    for r in res['skins'][s]['prims']:
        t0 = r['slots'].get('Tex0') or {}
        lines.append('  prim%-2d %-18s %-22s kind=%-7s Tex0=%s  A=%s(A_on_disk=%s)' % (
            r['prim'], r['material'], str(r['shader']).split('\\')[-1], r['kind'], t0.get('local_file'),
            t0.get('A_local_file'), t0.get('A_on_disk')))
        lines.append('        src_slot=%s logical=%s evidence=%s' % (t0.get('slot_field'), t0.get('logical_path'), (t0.get('evidence') or '').replace('\n', ' ')))
        lines.append('        why_not_direct=%s' % ((t0.get('why_not_direct') or '').replace('\n', ' ')[:200]))
        lines.append('        sha16 cur=%s (%sB)  A=%s (%sB)' % (t0.get('disk_sha16'), t0.get('disk_bytes'), t0.get('A_sha16'), t0.get('A_bytes')))
lines.append('#### c159 artifacts:')
for a in res['c159_artifacts']:
    lines.append('   %s %s %s' % ('DIR ' if a['dir'] else 'FILE', a['bytes'], a['path']))
open(os.path.join(OUT, 'AB_prep.txt'), 'w', encoding='utf-8').write('\n'.join(lines))
print('bindings -> AB_bindings.json ; text -> AB_prep.txt ; c159 candidates=%d' % len(res['c159_artifacts']))
