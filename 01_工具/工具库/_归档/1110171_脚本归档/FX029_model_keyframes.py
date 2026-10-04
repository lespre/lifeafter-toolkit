# -*- coding: utf-8 -*-
'''task-61 步骤2-a：把 1110177 两个 .sfx 里 Model 节点的**源** uniform 关键帧与源属性写进 effects.json
口径：只做「源字段注入」——逐节点解析 <Uniforms><Variables> 下的 <u_*_Keyframe> 帧；
      不做任何数值解释/换算/补值；不与 1110152 桥混用（桥仅在运行时缺项时兜底，本轮字段齐全即让位）。'''
import io, os, re, json, sys, shutil, hashlib, time
sys.stdout.reconfigure(encoding='utf-8')
P = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin\1110177\effects.json'
SRC = r'E:\la拆包项目\03拆包产物\_target_1110171\FX029_src'
raw = open(P, 'rb').read()
eff = json.loads(raw.decode('utf-8'))
SFX = {}
for fn in os.listdir(SRC):
    if fn.endswith('.sfx'):
        SFX[fn] = io.open(os.path.join(SRC, fn), 'rb').read().decode('gbk', 'replace')

def block(name, txt):
    i = txt.find('Name = "%s"' % name)
    if i < 0:
        return None
    m = re.search(r'<(ParticleSystem|Sprite|Model|Dummy|ParticleRes|Trail)\b', txt[i + 10:])
    return txt[i:(i + 10 + m.start()) if m else (i + 60000)]

def frames_of(body):
    out = []
    for fm in re.finditer(r'<Frame\s+([^>/]*)/?>', body):
        a = dict(re.findall(r'(\w+)\s*=\s*"([^"]*)"', fm.group(1)))
        if 'Time' not in a or 'Value' not in a:
            continue
        v = a['Value']
        val = [int(x) for x in re.findall(r'-?\d+', v)] if ',' in v else (float(v) if re.match(r'^-?\d+(\.\d+)?$', v.strip()) else v)
        out.append({'time': float(a['Time']), 'value': val})
    return out

MODELS = [n for n in eff['nodes'] if n.get('tag') == 'Model']
stat = {'rows': 0, 'tracks': 0, 'frames': 0, 'no_block': 0, 'per_driver': {}}
for n in MODELS:
    mf = n.setdefault('model_fields', {})
    xa = mf.get('xml_attrs') or {}
    blk = block(n['name'], SFX.get(n.get('source_sfx') or '', ''))
    if blk is None:
        stat['no_block'] += 1
        continue
    uni = re.search(r'<Uniforms>.*?</Uniforms>', blk, re.S)
    tracks, meta = {}, {}
    if uni:
        for m in re.finditer(r'<(u_[A-Za-z0-9_]+)\b([^>]*?)(?:/>|>(.*?)</\1>)', uni.group(0), re.S):
            tag, at, body = m.group(1), m.group(2), (m.group(3) or '')
            fr = frames_of(body)
            if not fr:
                continue
            tracks[tag] = fr
            meta[tag] = dict(re.findall(r'(\w+)\s*=\s*"([^"]*)"', at))
            stat['tracks'] += 1
            stat['frames'] += len(fr)
    mf['uniform_tracks'] = tracks
    mf['uniform_tracks_meta'] = meta
    for src, dst in (('TransparentMode', 'transparent_mode'), ('RenderBias', 'render_bias'),
                     ('TrackType', 'track_type'), ('RenderOrder', 'render_order'), ('DirType', 'dir_type'),
                     ('RenderLevel', 'render_level'), ('FxStartTime', 'fx_start_time'), ('FxLifeSpan', 'fx_life_span'),
                     ('ModelName', 'model_name'), ('PostProcessKind', 'post_process_kind'), ('Scale', 'scale_type')):
        if src in xa:
            mf[dst] = xa[src]
    mf['keyframe_source'] = {'sfx': n.get('source_sfx'), 'node': n['name'], 'container': 'Uniforms/Variables',
                             'tag_rule': '<u_*_Keyframe ChangeType Interpolator><Frame Time Value/>',
                             'tracks': sorted(tracks.keys()), 'frames_total': sum(len(v) for v in tracks.values()),
                             'note': '原样注入，未做任何解释/换算；u_dissolve_amount 等未接线项仅在源里存在'}
    stat['rows'] += 1
    for t in tracks:
        stat['per_driver'][t] = stat['per_driver'].get(t, 0) + 1

# 源属性 vs 分类（仅统计，不写判断结果）
A = sum(1 for n in MODELS if 'u_emissivecolor_Keyframe' in ((n['model_fields'].get('uniform_tracks')) or {}))
Bv = sum(1 for n in MODELS if 'u_emissivecolor_Keyframe' not in ((n['model_fields'].get('uniform_tracks')) or {})
         and ('u_diffuse_color_Keyframe' in ((n['model_fields'].get('uniform_tracks')) or {})))
C = len(MODELS) - A - Bv
eff['model_field_patch'] = dict(eff.get('model_field_patch') or {})
eff['model_field_patch']['model_keyframes'] = {
    'when': time.strftime('%Y-%m-%d %H:%M:%S'), 'by': 'chain-auditor task-61',
    'scope': 'Model 节点源 uniform 关键帧 + 源属性（只读注入，不含解释）',
    'rows': stat['rows'], 'no_block': stat['no_block'], 'tracks': stat['tracks'], 'frames': stat['frames'],
    'driver_rows': dict(sorted(stat['per_driver'].items(), key=lambda x: -x[1])),
    'class_source_counts': {'A_emissivecolor': A, 'B_diffuse_color_only': Bv, 'C_no_color_driver': C},
}
bs = P + '.bak_modelkf_' + time.strftime('%Y%m%d_%H%M%S')
shutil.copy2(P, bs)
pretty = '\n' in raw.decode('utf-8', 'replace')[:4000]
txt = json.dumps(eff, ensure_ascii=False, indent=1 if pretty else None,
                 separators=None if pretty else (',', ':'))
open(P, 'w', encoding='utf-8', newline='\n').write(txt)
nb = open(P, 'rb').read()
print('行数=%d 无块=%d 轨道=%d 帧=%d' % (stat['rows'], stat['no_block'], stat['tracks'], stat['frames']))
print('驱动行数:', json.dumps(dict(sorted(stat['per_driver'].items(), key=lambda x: -x[1])), ensure_ascii=False))
print('源侧分类计数: A=%d B=%d C=%d (总 %d)' % (A, Bv, C, len(MODELS)))
print('备份:', os.path.basename(bs))
print('effects.json 新 sha16 =', hashlib.sha256(nb).hexdigest()[:16].upper(), len(nb), 'B (旧', len(raw), 'B)')
