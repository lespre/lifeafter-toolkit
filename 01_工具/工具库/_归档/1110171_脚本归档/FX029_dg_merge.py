# -*- coding: utf-8 -*-
'''task-62 (b)：把 _dg.sfx 的 23 节点合并进 1110177/effects.json（窄范围单目的）
用法：python FX029_dg_merge.py --dry-run   # 只解析+断言，不写任何文件
      python FX029_dg_merge.py             # 先 copy2 备份，再写盘，最后打印 sha16 + 断言结果
口径：见 FX029_dg_handover.md；本脚本不解释任何数值、不猜贴图、不写 models_enabled。'''
import io, json, os, re, sys, zlib, hashlib, shutil, time
from collections import Counter
import zstandard
sys.stdout.reconfigure(encoding='utf-8')
DRY = '--dry-run' in sys.argv
BASE = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin\1110177'
EFF = os.path.join(BASE, 'effects.json')
INV = r'E:\la拆包项目\03拆包产物\_target_1110171\FX029_dg_inventory.json'
TAGS = ('Dummy', 'Model', 'ParticleSystem', 'ParticleRes', 'Sprite')
inv = json.loads(open(INV, 'rb').read().decode('utf-8'))
src = inv['source']
sfx_bytes = None
f = open(r'E:\mrzh\Documents\gres\0057.gpk', 'rb')
f.seek(src['block_base'] + src['off'] + 20)
raw = f.read(src['comp']); f.close()
sfx_bytes = zstandard.ZstdDecompressor().decompress(raw, max_output_size=src['dec'] * 4)
sha = hashlib.sha256(sfx_bytes).hexdigest()[:16].upper()
assert sha == inv['sha16'] == '9F4FE3A6AD3F8851', 'dg.sfx sha 不符: %s' % sha
txt = sfx_bytes.decode('gbk', 'replace')
print('解出 %d B sha16=%s （与 env-auditor 互证）' % (len(sfx_bytes), sha))

def nodes_of(t):
    out = []
    for m in re.finditer(r'<(%s)\b([^>]*)>' % '|'.join(TAGS), t):
        tag, at = m.group(1), m.group(2)
        nxt = re.search(r'<(?:%s)\b' % '|'.join(TAGS), t[m.end():])
        blk = t[m.end():(m.end() + nxt.start()) if nxt else (m.end() + 60000)]
        out.append({'tag': tag, 'attrs': dict(re.findall(r'(\w+)\s*=\s*"([^"]*)"', at)), 'blk': blk})
    return out
N = nodes_of(txt)
print('解析节点数:', len(N), {t: sum(1 for n in N if n['tag'] == t) for t in TAGS if any(n['tag'] == t for n in N)})
allkeys = sorted({k for n in N for k in n['attrs']})
print('节点头部属性键全集:', json.dumps(allkeys, ensure_ascii=False)[:400])
print('Parent 类键命中:', json.dumps({k: sum(1 for n in N if k in n['attrs']) for k in allkeys if re.search(r'parent|owner|link', k, re.I)}, ensure_ascii=False))
print('属性值样例:', json.dumps(N[0]['attrs'], ensure_ascii=False)[:300])

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

def tracks_of(blk):
    tracks, meta = {}, {}
    for unit in re.finditer(r'<Uniforms>.*?</Uniforms>', blk, re.S):
        for m in re.finditer(r'<(u_[A-Za-z0-9_]+)\b([^>]*?)(?:/>|>(.*?)</\1>)', unit.group(0), re.S):
            tag, at, body = m.group(1), m.group(2), (m.group(3) or '')
            fr = frames_of(body)
            if not fr:
                continue
            tracks[tag] = fr
            meta[tag] = dict(re.findall(r'(\w+)\s*=\s*"([^"]*)"', at))
    return tracks, meta

def semantics_of(blk):
    out = []
    for cm in re.finditer(r'<ShaderComponent\b([^>]*?)>(.*?)</ShaderComponent>', blk, re.S):
        for sm in re.finditer(r'<Semantic\b([^>]*?)/?>', cm.group(2)):
            out.append(dict(re.findall(r'(\w+)\s*=\s*"([^"]*)"', sm.group(1))))
    return out

eff = json.loads(open(EFF, 'rb').read().decode('utf-8'))
existing = {n.get('name') for n in eff['nodes']}
OLD_COUNT = len(eff['nodes'])
# 隔离：dg 里与现有同名者改名
renames = {}
for n in N:
    nm = n['attrs'].get('Name')
    if nm and nm in existing:
        renames[nm] = nm + '__dg'
print('同名需隔离:', json.dumps(renames, ensure_ascii=False))
# ★ lead 裁定 2026-09-19：**主键 = 容器坐标（直证）**；人类可读名 = 同族命名**推定**，不得写成直证名。
SRC_ID = 'gres\\0057.gpk#%d' % src['row']
SRC_NAME_INFERRED = 'fx_skin_2003_029_dg.sfx'
dg_nodes = []
stat = {'rows': 0, 'tracks': 0, 'frames': 0, 'renamed_parent_refs': 0, 'parent_keys': {}}
for n in N:
    nm, at, blk = n['attrs'].get('Name'), n['attrs'], n['blk']
    newname = renames.get(nm, nm)
    par = None
    # 证据：dg 源全文 "parent"（排除 TransparentMode）出现 0 次 ⇒ 无显式父子键；下列键仅为兼容性兜底
    for k in ('Parent', 'ParentName', 'Owner', 'Link', 'LinkName', 'DummyName', 'BindDummy', 'BindDummyName', 'HostName', 'AttachName'):
        if at.get(k):
            par = at[k]; stat['parent_keys'][k] = stat['parent_keys'].get(k, 0) + 1
            break
    if par in renames:
        par = renames[par]; stat['renamed_parent_refs'] += 1
    row = {'name': newname, 'tag': n['tag'], 'parent': par,
           'source_sfx_id': SRC_ID, 'source_sfx_name_inferred': SRC_NAME_INFERRED,
           'source_sfx_name_evidence': 'inferred_from_family_naming',
           'dg': True, 'dg_sha16': sha,
           'dg_provenance': {'container': 'gres\\0057.gpk', 'row': src['row'], 'off': src['off'],
                             'dec': src['dec'], 'sha16': sha,
                             'note': '资产已按容器坐标定位并接入；文件名为同族命名推定（盘点清单只直证了同族 daoguang_02.sfx）'}}
    if n['tag'] == 'Model':
        tr, meta = tracks_of(blk)
        stem = re.sub(r'\.gim$', '', os.path.basename(at.get('ModelName', '')))
        row.update({'model_name': at.get('ModelName'), 'model_glb': 'sfx/dg/%s.glb' % stem,
                    'renderable_by_adapter': False,
                    'model_fields': {'uniform_tracks': tr, 'uniform_tracks_meta': meta,
                                     'keyframe_source': {'source_sfx_id': SRC_ID, 'source_sfx_name_inferred': SRC_NAME_INFERRED,
                                                         'node': nm, 'container': 'Uniforms/Variables',
                                                         'tag_rule': '<u_*_Keyframe ChangeType Interpolator><Frame Time Value/>',
                                                         'tracks': sorted(tr.keys()),
                                                         'frames_total': sum(len(v) for v in tr.values()),
                                                         'note': '原样注入，未做解释/换算'},
                                     'shader': {'ShaderComponent': semantics_of(blk)}}})
        for s, d in (('TransparentMode', 'transparent_mode'), ('RenderBias', 'render_bias'), ('TrackType', 'track_type'),
                     ('RenderOrder', 'render_order'), ('DirType', 'dir_type'), ('RenderLevel', 'render_level'),
                     ('FxStartTime', 'fx_start_time'), ('FxLifeSpan', 'fx_life_span'), ('ModelName', 'model_name_attr'),
                     ('PostProcessKind', 'post_process_kind'), ('Scale', 'scale_type')):
            if s in at:
                row['model_fields'][d] = at[s]
        stat['tracks'] += len(tr); stat['frames'] += sum(len(v) for v in tr.values())
    elif at.get('Texture'):
        row['texture'] = at['Texture']
    dg_nodes.append(row)
    stat['rows'] += 1
print('构造 dg 行:', stat['rows'], ' 轨道=%d 帧=%d 父引用被改名=%d' % (stat['tracks'], stat['frames'], stat['renamed_parent_refs']))
print('dg Model 数:', sum(1 for r in dg_nodes if r['tag'] == 'Model'), ' Dummy 改名后:', [r['name'] for r in dg_nodes if r['tag'] == 'Dummy'])
# 断言
def cls_of(node):
    ut = (node.get('model_fields') or {}).get('uniform_tracks') or {}
    return 'A' if (ut.get('u_emissivecolor_Keyframe') or ut.get('u_emissive_color_Keyframe')) else ('B' if ut.get('u_diffuse_color_Keyframe') else 'C')
merged = json.loads(json.dumps(eff))
merged['nodes'] = merged['nodes'] + dg_nodes
MD = [n for n in merged['nodes'] if n.get('tag') == 'Model']
cc = {c: sum(1 for n in MD if cls_of(n) == c) for c in 'ABC'}
glb = [n.get('model_glb') for n in MD]
missing = [g for g in glb if not os.path.isfile(os.path.join(BASE, str(g).replace('/', os.sep)))]
sfxdist = {}
for n in merged['nodes']:
    k = n.get('source_sfx') or n.get('source_sfx_id') or '(none)'
    sfxdist[k] = sfxdist.get(k, 0) + 1
print()
print('=== 断言 ===')
print('A1 节点数: %d -> %d （期望 %d）%s' % (OLD_COUNT, len(merged['nodes']), OLD_COUNT + 23, 'OK' if len(merged['nodes']) == OLD_COUNT + 23 else 'FAIL'))
print('A2 source_sfx 分布:', json.dumps(sfxdist, ensure_ascii=False))
old_dup = {k: v for k, v in Counter(x.get('name') for x in eff['nodes']).items() if v > 1}
new_dup = {k: v for k, v in Counter(x.get('name') for x in merged['nodes']).items() if v > 1}
introduced = sorted(set(new_dup) - set(old_dup))
print('A2b 既有重名(合并前) %d 处 %s；合并后 %d 处；**dg 新增重名: %s** %s' % (
    len(old_dup), sorted(old_dup), len(new_dup), introduced, 'OK' if not introduced else 'FAIL'))
print('   父键命中:', json.dumps(stat['parent_keys'], ensure_ascii=False), '（dg 源 0 处 Parent ⇒ 全为 None 是如实的）')
print('A3 class_counts（含 dg）: %s  期望 A25/B7/C10 %s' % (json.dumps(cc), 'OK' if cc == {'A': 25, 'B': 7, 'C': 10} else 'FAIL'))
print('A4 model_glb 总数 %d，缺失 %d %s' % (len(glb), len(missing), 'OK' if not missing else 'FAIL: %s' % missing[:6]))
print('A6 models_enabled:', repr(merged.get('models_enabled')), '（缺省=默认关）', 'OK' if not merged.get('models_enabled') else 'FAIL')
if DRY:
    print()
    print('** dry-run：未写任何文件 **')
    sys.exit(0)
if missing:
    print()
    print('** A4 未通过 ⇒ 拒绝写盘（缺 %d 个 GLB）：%s **' % (len(missing), missing[:8]))
    sys.exit(3)
bs = EFF + '.bak_dgmerge_' + time.strftime('%Y%m%d_%H%M%S')
shutil.copy2(EFF, bs)
merged['model_field_patch'] = dict(merged.get('model_field_patch') or {})
merged['model_field_patch']['dg_merge'] = {
    'when': time.strftime('%Y-%m-%d %H:%M:%S'), 'by': 'chain-auditor task-62(b)',
    'source_sfx_id': SRC_ID, 'source_sfx_name_inferred': SRC_NAME_INFERRED,
    'source_sfx_name_evidence': 'inferred_from_family_naming',
    'container': 'gres\\0057.gpk', 'row': src['row'], 'sfx_sha16': sha,
    'rows_added': stat['rows'], 'tracks': stat['tracks'], 'frames': stat['frames'],
    'dummies_renamed': renames, 'parent_refs_rewritten': stat['renamed_parent_refs'],
    'assertions': {'nodes': len(merged['nodes']), 'class_counts': cc, 'model_glb_missing': missing}}
raw2 = open(EFF, 'rb').read()
pretty = '\n' in raw2.decode('utf-8', 'replace')[:4000]
open(EFF, 'w', encoding='utf-8', newline='\n').write(
    json.dumps(merged, ensure_ascii=False, indent=1 if pretty else None, separators=None if pretty else (',', ':')))
nb = open(EFF, 'rb').read()
print()
print('备份:', os.path.basename(bs))
print('effects.json sha16: %s -> %s  (%d -> %d B)' % (
    hashlib.sha256(raw2).hexdigest()[:16].upper(), hashlib.sha256(nb).hexdigest()[:16].upper(), len(raw2), len(nb)))
