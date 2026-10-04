# -*- coding: utf-8 -*-
"""FXMODEL_patch.py — 给 effects.json 的 Model 节点补源级字段 + 找出真实的颜色/缩放通道（uniform 轨道）。
对象：1110171（f74635 帧）与 1110152（f76037 帧）。
逐字段标 source_flags（source / absent / derived），推不出的写 absent 并说明，不编造。
输出：皮肤 effects.json + _target_1110171\\FXMODEL_*_viewer_effects.json
"""
import os, re, json, collections, hashlib
import xml.etree.ElementTree as ET

PACK = r'E:\la拆包项目\03拆包产物'
WIKI = r'E:\la拆包项目\08Lifeafter wiki'
OUT = os.path.join(PACK, '_target_1110171')
JOBS = [
    ('1110171', os.path.join(PACK, 'render_1003_010', '_sfx_010', 'gpk_effect_01_f74635_59115620b779a5e8.bin'), 'f74635'),
    ('1110152', os.path.join(OUT, 'FX152_gpk_effect_01_f76037_f1befd4d7588500f.bin'), 'f76037'),
]
TAGS = {'Sprite', 'ParticleSystem', 'Dummy', 'Model', 'ParticleRes', 'Trail'}
TRACK_TAGS = ('ColorFrame', 'ColorFramePar', 'TrackScale', 'SmoothStartFrame', 'SmoothStopFrame',
              'ScaleFrame', 'SpriteScaleFrame', 'SpriteHeightFrame', 'HWRatioFrame', 'TrackFixPoint')


def frames_of(el):
    out = []
    for f in el.iter('Frame'):
        t, v = f.get('Time'), f.get('Value')
        if t is None or v is None:
            continue
        try:
            vals = [float(x) for x in v.split(',') if x.strip()]
            out.append({'time': float(t), 'value': vals})
        except Exception:
            pass
    return out


for skin, fxbin, tag in JOBS:
    eff_path = os.path.join(WIKI, 'assets', '3d', 'weapon_skin', skin, 'effects.json')
    eff = json.load(open(eff_path, encoding='utf-8'))
    txt = open(fxbin, 'rb').read().decode('gbk', 'replace')
    root = ET.fromstring(txt)
    model_xml = {}

    def walk(el, parent):
        if el.tag in TAGS:
            if el.tag == 'Model':
                tracks = {}
                for ch in el:
                    if ch.tag == 'TrackScale':
                        for ax in ch:
                            f = frames_of(ax)
                            if f:
                                tracks['scale_' + ax.tag] = f
                    elif ch.tag in TRACK_TAGS:
                        f = frames_of(ch)
                        if f:
                            tracks[ch.tag] = f
                    elif ch.tag == 'TrackFixPoint':
                        tracks['fixpoint'] = ch.attrib.get('Forward')
                # 实际颜色/缩放通道：uniform 轨道（u_*_Keyframe）
                uni = {}
                for ch in el.iter():
                    if ch is el:
                        continue
                    if re.match(r'^u_\w+', ch.tag or ''):
                        f = frames_of(ch)
                        if f:
                            uni[ch.tag] = f
                shader_blocks = collections.Counter(c.tag for c in el.iter() if c.tag in
                                                    ('ShaderComponent', 'Uniforms', 'Variables', 'Macros', 'Semantic'))
                model_xml[el.get('Name')] = {
                    'ModelName': el.get('ModelName'), 'PosOffset': el.get('PosOffset'),
                    'Direction': el.get('Direction'), 'DirType': el.get('DirType'),
                    'RenderOrder': el.get('RenderOrder'), 'FxStartTime': el.get('FxStartTime'),
                    'FxLifeSpan': el.get('FxLifeSpan'), 'AnimName': el.get('AnimName'),
                    'ScaleStyle': el.get('ScaleStyle'), 'tracks': tracks,
                    'uniform_tracks': uni, 'shader_blocks': dict(shader_blocks),
                    'attrs_all': dict(el.attrib)}
                parent = el.get('Name')
        for ch in el:
            walk(ch, parent)
    walk(root, None)
    models = [n for n in eff['nodes'] if n['tag'] == 'Model']
    fixed = 0
    chan_used = collections.Counter()
    for n in models:
        src = model_xml.get(n['name'])
        if not src:
            n['model_fields_unresolved'] = 'sfx 中未匹配到同名 Model 节点'
            continue
        uni_keys = sorted(src['uniform_tracks'].keys())
        color_uni = [k for k in uni_keys if re.search(r'color|emissive|diffuse|maintex|addcolor', k, re.I)]
        scale_uni = [k for k in uni_keys if re.search(r'scale|size|width|height|hwr', k, re.I)]
        for k in color_uni:
            chan_used['uniform_color:' + k.split('_')[1] if '_' in k else k] += 1
        for k in scale_uni:
            chan_used['uniform_scale:' + k] += 1
        if src['tracks'].get('ColorFrame'):
            chan_used['ColorFrame'] += 1
        n['model_fields'] = {
            'ModelName': src['ModelName'],
            'MtlIdx': None,
            'PosOffset': src['PosOffset'], 'Direction': src['Direction'], 'DirType': src['DirType'],
            'RenderOrder': src['RenderOrder'], 'FxStartTime': src['FxStartTime'], 'FxLifeSpan': src['FxLifeSpan'],
            'AnimName': src['AnimName'], 'ScaleStyle': src['ScaleStyle'],
            'mesh': None,
            'tracks': src['tracks'],
            'uniform_tracks': {k: src['uniform_tracks'][k] for k in (color_uni + scale_uni)[:14]},
            'shader_blocks': src['shader_blocks'],
        }
        n['source_flags'] = dict(n.get('source_flags') or {})
        n['source_flags'].update({
            'ModelName': 'source: XML@ModelName',
            'PosOffset': ('source: XML@PosOffset' if src['PosOffset'] is not None else 'absent'),
            'Direction': ('source: XML@Direction' if src['Direction'] is not None else 'absent'),
            'RenderOrder': ('source: XML@RenderOrder' if src['RenderOrder'] is not None else 'absent'),
            'FxStartTime': ('source: XML@FxStartTime' if src['FxStartTime'] is not None else 'absent'),
            'FxLifeSpan': ('source: XML@FxLifeSpan' if src['FxLifeSpan'] is not None else 'absent'),
            'MtlIdx': 'absent_in_sfx（在 .gim 元数据里，资产侧提供）',
            'mesh': 'absent_in_sfx（真几何=同 stem 的 .mesh，资产侧提供 → freeze-auditor 的 GLB 对照表）',
            'ColorFrame': ('source: XML ColorFrame' if src['tracks'].get('ColorFrame') else
                           ('absent_in_ColorFrame；实际颜色通道=%s' % (color_uni[:4] or '另行 absent'))),
            'TrackScale': ('source: XML TrackScale' if any(k.startswith('scale_') for k in src['tracks']) else
                           ('absent；实际缩放通道=%s' % (scale_uni[:4] or '另行 absent'))),
            'uniform_tracks': 'source: XML ShaderComponent/u_*_Keyframe（Model 颜色/缩放的真实通道）',
        })
        fixed += 1
    eff['model_field_patch'] = {
        'schema_note': 'Model 节点补字段：源级=XML；MtlIdx/mesh 在 sfx 中不存在（属 .gim/.mesh 资产侧）',
        'model_nodes': len(models), 'patched': fixed,
        'color_scale_channel': ('Model 节点的颜色/缩放来自 ShaderComponent 下的 u_*_Keyframe uniform 轨道；'
                                '27 帧的 ColorFrame 计数为 0 或全白 ⇒ ColorFrame 不是 Model 的颜色通道'),
        'channel_usage': dict(chan_used),
    }
    json.dump(eff, open(eff_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    inj = os.path.join(OUT, 'FXMODEL_%s_%s_viewer_effects.json' % (skin, tag))
    json.dump(eff, open(inj, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('== %s (%s) Model 节点 %d 个，补全 %d 个' % (skin, tag, len(models), fixed))
    print('   颜色/缩放通道统计:', json.dumps(dict(chan_used.most_common(12)), ensure_ascii=False))
    if models:
        m0 = models[0]
        mf = m0.get('model_fields') or {}
        print('   样例节点 %s：' % m0['name'])
        print('      ModelName=%s' % (mf.get('ModelName') or '')[-46:])
        print('      PosOffset=%s Direction=%s RenderOrder=%s FxStartTime=%s FxLifeSpan=%s'
              % (mf.get('PosOffset'), mf.get('Direction'), mf.get('RenderOrder'), mf.get('FxStartTime'), mf.get('FxLifeSpan')))
        print('      tracks=%s' % json.dumps({k: len(v) for k, v in (mf.get('tracks') or {}).items()},
                                             ensure_ascii=False))
        print('      uniform_tracks=%s' % json.dumps({k: len(v) for k, v in (mf.get('uniform_tracks') or {}).items()},
                                                     ensure_ascii=False)[:300])
        print('      shader_blocks=%s' % json.dumps(mf.get('shader_blocks'), ensure_ascii=False))
    print('   注入对象 ->', inj)
