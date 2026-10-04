# -*- coding: utf-8 -*-
"""FXMODEL_backfill.py — 用 GIM_manifest 回填 Model 节点的 mesh（GLB 路径）+ 从 .gim 取 MtlIdx。
· mesh：stem 匹配（ModelName basename 去扩展名）→ 复制 GLB 到 <skin>/sfx/model/ → 写 web 相对路径
· MtlIdx：在 .gim 里定位 MtlIdx 邻域取整（best-effort；取不到如实标 unresolved）
写：<skin>/effects.json + <skin>/sfx/model/*.glb + _target_1110171/FXMODEL_*_viewer_effects.json
"""
import os, re, json, shutil, struct, collections

PACK = r'E:\la拆包项目\03拆包产物'
WIKI = r'E:\la拆包项目\08Lifeafter wiki'
OUT = os.path.join(PACK, '_target_1110171')
GIM = os.path.join(PACK, '_gim_out')
RAW = os.path.join(GIM, 'raw')

menus = {}
for man, glbdir, tag in ((os.path.join(GIM, 'GIM_manifest.json'), GIM, '1110152'),
                         (os.path.join(GIM, 'GIM_manifest_1110171.json'), os.path.join(GIM, '1110171'), '1110171')):
    if not os.path.isfile(man):
        continue
    d = json.load(open(man, encoding='utf-8'))
    models = d['models'] if isinstance(d.get('models'), list) else list((d.get('models') or {}).values())
    for m in models:
        menus.setdefault(m['model'], {})['manifest'] = m
        menus[m['model']]['glb_src'] = os.path.join(glbdir, m.get('glb') or (m['model'] + '.glb'))
        menus[m['model']]['from'] = os.path.basename(man)
print('manifest 合计模型 %d 个' % len(menus))

fb = {}
for tag in menus:
    p = os.path.join(RAW, tag + '.gim')
    if not os.path.isfile(p):
        continue
    b = open(p, 'rb').read()
    i = b.find(b'MtlIdx')
    info = {'gim_bytes': len(b), 'magic': b[:4].hex(), 'mtlidx_offset': i}
    if i >= 0:
        seg = b[i + 6:i + 6 + 32]
        vals = []
        for off in range(0, min(24, len(seg) - 3)):
            v = struct.unpack_from('<I', seg, off)[0]
            if 0 <= v <= 512:
                vals.append({'off': off, 'u32': v})
        info['candidates'] = vals[:8]
        info['hex'] = seg.hex()
    fb[tag] = info
print('gim MtlIdx 探查：%d/%d 命中' % (sum(1 for v in fb.values() if v['mtlidx_offset'] >= 0), len(fb)))

summary = {}
for skin, tag in (('1110171', '1110171'), ('1110152', '1110152')):
    eff_path = os.path.join(WIKI, 'assets', '3d', 'weapon_skin', skin, 'effects.json')
    eff = json.load(open(eff_path, encoding='utf-8'))
    modeldir = os.path.join(WIKI, 'assets', '3d', 'weapon_skin', skin, 'sfx', 'model')
    os.makedirs(modeldir, exist_ok=True)
    filled = absent = 0
    for n in eff['nodes']:
        if n.get('tag') != 'Model':
            continue
        mf = n.setdefault('model_fields', {})
        mn = mf.get('ModelName') or ''
        stem = os.path.splitext(os.path.basename(mn.replace('\\', '/')))[0]
        rec = menus.get(stem)
        if rec and os.path.isfile(rec['glb_src']):
            dst = os.path.join(modeldir, os.path.basename(rec['glb_src']))
            if not os.path.isfile(dst):
                shutil.copyfile(rec['glb_src'], dst)
            mf['mesh'] = 'sfx/model/' + os.path.basename(dst)
            mf['mesh_evidence'] = {'manifest': rec['from'], 'glb_src': rec['glb_src'],
                                   'mesh_fid': rec['manifest'].get('mesh_fid'), 'mesh_frame': rec['manifest'].get('frame'),
                                   'glb_sha16': rec['manifest'].get('glb_sha16'),
                                   'vertices': rec['manifest'].get('vertices'), 'faces': rec['manifest'].get('faces'),
                                   'bbox_span': rec['manifest'].get('bbox_span'),
                                   'gim_sha16': rec['manifest'].get('gim_sha16')}
            n['source_flags']['mesh'] = 'source: GIM_manifest(%s)＋.mesh 同 stem' % rec['from']
            filled += 1
        else:
            mf['mesh'] = None
            n['source_flags']['mesh'] = 'absent: GIM_manifest 中无此 stem 的 GLB'
            absent += 1
        g = fb.get(stem)
        if g and g.get('mtlidx_offset', -1) >= 0:
            cand = [c['u32'] for c in g['candidates']]
            mf['MtlIdx'] = cand
            mf['MtlIdx_evidence'] = {'source': 'raw/%s.gim' % stem, 'offset': g['mtlidx_offset'],
                                     'method': 'bytes_after_MtlIdx_best_effort', 'hex': g['hex']}
            n['source_flags']['MtlIdx'] = 'source(best-effort): .gim 中 MtlIdx 邻域整数值，未做结构级确认'
        else:
            mf['MtlIdx'] = None
            n['source_flags']['MtlIdx'] = 'unresolved: .gim 里未定位到 MtlIdx'
    eff['model_field_patch'] = dict(eff.get('model_field_patch') or {})
    eff['model_field_patch'].update({'mesh_backfill': {'filled': filled, 'absent': absent,
                                                       'source': '03拆包产物/_gim_out/GIM_manifest*.json',
                                                       'glb_copied_to': 'assets/3d/weapon_skin/%s/sfx/model/' % skin}})
    json.dump(eff, open(eff_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    inj = os.path.join(OUT, 'FXMODEL_%s_inj_viewer_effects.json' % skin)
    json.dump(eff, open(inj, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    summary[skin] = {'filled': filled, 'absent': absent, 'inj': inj, 'models': len(os.listdir(modeldir))}
    print('== %s：Model mesh 回填 %d 个，absent %d 个；GLB 落盘 %d 个 → %s' % (
        skin, filled, absent, len(os.listdir(modeldir)), inj))
json.dump(summary, open(os.path.join(OUT, 'FXMODEL_backfill.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('summary ->', os.path.join(OUT, 'FXMODEL_backfill.json'))
