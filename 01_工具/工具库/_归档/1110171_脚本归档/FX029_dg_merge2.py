# -*- coding: utf-8 -*-
'''task-66：把 daoguang_02（gres\\0057.gpk row 32153）的**源参数**补进 1110177 的 23 个 dg 节点。
- 源：自解 row 32153（block_base+off+20 → zstd → GBK XML），并与 lead 的 DG_SRC JSON 交叉核对；
- 只改 dg 节点的「参数」字段；**贴图字段只读不改**；其余 66 节点逐字节不动；
- 用法：python FX029_dg_merge2.py --dry-run | (无参数=真跑，先 copy2 备份)'''
import io, json, os, re, sys, hashlib, shutil, time, zstandard
sys.stdout.reconfigure(encoding='utf-8')
DRY = '--dry-run' in sys.argv
BASE = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin\1110177'
EFF = os.path.join(BASE, 'effects.json')
INV = r'E:\la拆包项目\03拆包产物\_target_1110171\FX029_dg_inventory.json'
LEAD_SRC = r'E:\la拆包项目\03拆包产物\_target_1110171\DG_SRC_daoguang02_20260919.json'
REP = r'E:\la拆包项目\03拆包产物\_target_1110171\FX029_dg_merge2_report.md'
TAGS = ('Dummy', 'Model', 'ParticleSystem', 'ParticleRes', 'Sprite')
TEXTURE_KEYS = ('texture', 'texture_candidate', 'texture_binding', 'texture_status', 'texture_selection',
                'spr_sheet', 'spr_frames', 'spr_frames_source', 'spr_source', 'spr_hard_dims', 'atlas_provenance',
                'is_sprite_sheet')
src = json.loads(open(INV, 'rb').read().decode('utf-8'))['source']
f = open(r'E:\mrzh\Documents\gres\0057.gpk', 'rb')
f.seek(src['block_base'] + src['off'] + 20)
raw = f.read(src['comp']); f.close()
data = zstandard.ZstdDecompressor().decompress(raw, max_output_size=src['dec'] * 4)
sha = hashlib.sha256(data).hexdigest()[:16].upper()
assert sha == '9F4FE3A6AD3F8851', 'sha 不符: %s' % sha
txt = data.decode('gbk', 'replace')
print('[源] row 32153 解出 %d B sha16=%s' % (len(data), sha))

def frames_of(body):
    out = []
    for fm in re.finditer(r'<Frame\s+([^>/]*)/?>', body):
        a = dict(re.findall(r'(\w+)\s*=\s*"([^"]*)"', fm.group(1)))
        if 'Time' not in a or 'Value' not in a:
            continue
        v = a['Value']
        val = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', v)] if ',' in v else (
            float(v) if re.match(r'^-?\d+(\.\d+)?$', v.strip()) else v)
        out.append({'time': float(a['Time']), 'value': val})
    return out

def children_of(blk):
    out = []
    for m in re.finditer(r'<([A-Za-z_]\w*)\b([^>]*?)(?:/>|>(.*?)</\1>)', blk, re.S):
        tag, at, body = m.group(1), m.group(2), (m.group(3) or '')
        if tag in TAGS or tag in ('FxGroup', 'Semantic', 'Variables', 'Macros', 'Uniforms'):
            continue
        out.append({'tag': tag, 'attrs': dict(re.findall(r'(\w+)\s*=\s*"([^"]*)"', at)), 'frames': frames_of(body)})
    return out

SRC = {}
for m in re.finditer(r'<(%s)\b([^>]*)>' % '|'.join(TAGS), txt):
    tag, at = m.group(1), m.group(2)
    nxt = re.search(r'<(?:%s)\b' % '|'.join(TAGS), txt[m.end():])
    blk = txt[m.end():(m.end() + nxt.start()) if nxt else (m.end() + 60000)]
    a = dict(re.findall(r'(\w+)\s*=\s*"([^"]*)"', at))
    if a.get('Name'):
        SRC[a['Name']] = {'tag': tag, 'attrs': a, 'children': children_of(blk)}
print('[源] 顶层节点 %d 个，其中带 Name 且已解析 %d 个' % (len(re.findall(r'<(%s)\b' % '|'.join(TAGS), txt)), len(SRC)))

# 与 lead 的 DG_SRC 交叉核对（20 个命中名，逐字段比 FxStartTime/FxLifeSpan/TransparentMode/ModelName）
lead = json.loads(open(LEAD_SRC, 'rb').read().decode('utf-8'))
xchk = {'same': 0, 'diff': [], 'missing': []}
for nm, ln in lead['nodes'].items():
    if nm not in SRC:
        xchk['missing'].append(nm); continue
    bad = []
    for k in ('FxStartTime', 'FxLifeSpan', 'TransparentMode', 'RenderBias', 'ModelName', 'TrackType', 'DirType'):
        a, b = ln['attrs'].get(k), SRC[nm]['attrs'].get(k)
        if a is not None and str(a) != str(b):
            bad.append((k, a, b))
    if bad:
        xchk['diff'].append((nm, bad))
    else:
        xchk['same'] += 1
print('[核对] 与 lead 源 JSON 一致 %d 个；不一致 %s；我这边缺 %s' % (xchk['same'], xchk['diff'][:3], xchk['missing']))

eff = json.loads(open(EFF, 'rb').read().decode('utf-8'))
old_raw = open(EFF, 'rb').read()
dg = [n for n in eff['nodes'] if n.get('dg') or n.get('source_sfx_id')]
print('[目标] dg 节点 %d 个（%s）' % (len(dg), dict((t, sum(1 for n in dg if n.get('tag') == t)) for t in TAGS if any(n.get('tag') == t for n in dg))))
before_tex = {n['name']: {k: json.dumps(n.get(k), ensure_ascii=False, sort_keys=True) for k in TEXTURE_KEYS} for n in dg}
before_other = json.dumps([n for n in eff['nodes'] if not (n.get('dg') or n.get('source_sfx_id'))],
                          ensure_ascii=False, sort_keys=True)

def fnum(x):
    try:
        return float(x)
    except Exception:
        return None

rows, no_src = [], []
for n in dg:
    key = n['name'].replace('__dg', '')
    s = SRC.get(key)
    n['dg_param_status'] = 'ok' if s else 'no_source_node'
    if not s:
        no_src.append(n['name']); rows.append({'node': n['name'], 'src': key, 'status': 'no_source_node', 'fields': []}); continue
    a, ch = s['attrs'], s['children']
    prov = {}
    def put(field, value, srckey):
        n[field] = value
        prov[field] = 'dg_src:gres\\0057.gpk#32153:%s:%s' % (key, srckey)
    if 'FxStartTime' in a: put('start', fnum(a['FxStartTime']), 'FxStartTime')
    if 'FxLifeSpan' in a: put('life', fnum(a['FxLifeSpan']), 'FxLifeSpan')
    if 'PosOffset' in a:
        v = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', a['PosOffset'])]
        if len(v) == 3: put('pos_offset', v, 'PosOffset')
    for sk, dk in (('RenderBias', 'render_bias'), ('TransparentMode', 'transparent_mode'), ('TrackType', 'track_type'),
                   ('DirType', 'dir_type'), ('RenderOrder', 'render_order'), ('RenderLevel', 'render_level'),
                   ('BlendMode', 'blend_mode'), ('ParticlesPerSecond', 'particlesPerSecond'),
                   ('MinParticlesPerSecond', 'minParticlesPerSecond'), ('MaxParticlesPerSecond', 'maxParticlesPerSecond'),
                   ('MinSpriteLifespan', 'minSpriteLifespan'), ('MaxSpriteLifespan', 'maxSpriteLifespan'),
                   ('MinRadius', 'minRadius'), ('MaxRadius', 'maxRadius'), ('EmissionType', 'emissionType'),
                   ('EmitAtBegin', 'emitAtBegin'), ('Inside', 'inside'), ('ParticleDir', 'particleDir')):
        if sk in a:
            v = a[sk]
            if dk in ('particlesPerSecond', 'minParticlesPerSecond', 'maxParticlesPerSecond',
                      'minSpriteLifespan', 'maxSpriteLifespan', 'minRadius', 'maxRadius'):
                v = fnum(v)
            put(dk, v, sk)
    if n.get('tag') == 'Model' and 'ModelName' in a:
        put('model_name', a['ModelName'], 'ModelName')
        mf = n.setdefault('model_fields', {})
        mf['ModelName'] = a['ModelName']
        for sk, dk in (('TransparentMode', 'transparent_mode'), ('RenderBias', 'render_bias'), ('TrackType', 'track_type'),
                       ('DirType', 'dir_type'), ('RenderOrder', 'render_order'), ('FxStartTime', 'fx_start_time'),
                       ('FxLifeSpan', 'fx_life_span'), ('ModelName', 'model_name'), ('Scale', 'scale_type')):
            if sk in a:
                mf[dk] = a[sk]
    # 子轨道 → emit（全部），另抽 scale/color
    emit = {}
    for c in ch:
        if c['frames']:
            emit[c['tag']] = c['frames']
    if emit:
        n['emit'] = emit
        prov['emit'] = 'dg_src:gres\\0057.gpk#32153:%s:children(<Frame Time Value>)' % key
    def first_track(names):
        for nmx in names:
            if nmx in emit:
                return emit[nmx]
        return None
    st = first_track(('ScaleFrame', 'TrackScale', 'Scale'))
    if st:
        n['scale_track'] = st
        prov['scale_track'] = 'dg_src:gres\\0057.gpk#32153:%s:ScaleFrame' % key
    ct = first_track(('TrackColor', 'ColorFrame', 'ColorKeyFrame'))
    if ct:
        n['color_track'] = ct
        prov['color_track'] = 'dg_src:gres\\0057.gpk#32153:%s:TrackColor' % key
    n['dg_param_provenance'] = prov
    if 'ParticlesPerSecond' not in a and n.get('tag') == 'ParticleSystem':
        n['particlesPerSecond'] = None
        prov['particlesPerSecond'] = 'dg_src:gres\\0057.gpk#32153:%s:(源无 ParticlesPerSecond 属性) ⇒ 如实 null' % key
    rows.append({'node': n['name'], 'src': key, 'status': 'ok', 'tag': s['tag'],
                 'fields': sorted(prov.keys()), 'emit_tracks': sorted(emit.keys()),
                 'rate': a.get('ParticlesPerSecond'), 'life': a.get('FxLifeSpan'), 'start': a.get('FxStartTime')})
print('[补全] ok=%d no_source_node=%d' % (sum(1 for r in rows if r['status'] == 'ok'), len(no_src)))
for r in rows:
    if r['status'] == 'ok' and r.get('tag') != 'Model':
        print('   %-18s %-14s rate=%s life=%s start=%s emit=%d 轨' % (r['node'], r['tag'], r['rate'], r['life'], r['start'], len(r['emit_tracks'])))
print('   no_source_node:', no_src)
# 自证：贴图字段与其余节点未变
tex_ok = all(before_tex[n['name']] == {k: json.dumps(n.get(k), ensure_ascii=False, sort_keys=True) for k in TEXTURE_KEYS}
             for n in eff['nodes'] if (n.get('dg') or n.get('source_sfx_id')))
other_ok = before_other == json.dumps([n for n in eff['nodes'] if not (n.get('dg') or n.get('source_sfx_id'))],
                                      ensure_ascii=False, sort_keys=True)
print('[自证] 23 个 dg 节点的贴图字段未变: %s ；其余 %d 个节点逐字节未变: %s' % (
    tex_ok, sum(1 for n in eff['nodes'] if not (n.get('dg') or n.get('source_sfx_id'))), other_ok))
if DRY:
    print('** dry-run：未写任何文件 **'); sys.exit(0)
if not (tex_ok and other_ok):
    print('** 自证未过 ⇒ 拒绝写盘 **'); sys.exit(3)
bs = EFF + '.bak_dgmerge2_' + time.strftime('%Y%m%d_%H%M%S')
shutil.copy2(EFF, bs)
pp = '\n' in old_raw.decode('utf-8', 'replace')[:4000]
open(EFF, 'w', encoding='utf-8', newline='\n').write(
    json.dumps(eff, ensure_ascii=False, indent=1 if pp else None, separators=None if pp else (',', ':')))
nb = open(EFF, 'rb').read()
print()
print('备份:', os.path.basename(bs))
print('effects.json sha16: %s -> %s  (%d -> %d B)' % (
    hashlib.sha256(old_raw).hexdigest()[:16].upper(), hashlib.sha256(nb).hexdigest()[:16].upper(), len(old_raw), len(nb)))
json.dump({'source': {'container': 'gres\\0057.gpk', 'row': src['row'], 'sha16': sha, 'bytes': len(data)},
           'cross_check_with_lead_json': {'same': xchk['same'], 'diff': xchk['diff'], 'missing': xchk['missing']},
           'rows': rows, 'no_source_node': no_src,
           'self_proof': {'texture_fields_unchanged': tex_ok, 'other_nodes_unchanged': other_ok}},
          io.open(r'E:\la拆包项目\03拆包产物\_target_1110171\FX029_dg_merge2_rows.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('逐条表 -> FX029_dg_merge2_rows.json')
