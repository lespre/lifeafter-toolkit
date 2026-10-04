# -*- coding: utf-8 -*-
"""FXSRC_build_1110152.py — 1110152 全链：
A 挂点：002729.c159 的 fx_idle_01 4×4（源级）+ 节点 PosOffset（源级）
B 贴图：在 875 dds 池 + _pool_features.json 里按内容特征选 3 个候选 → 规范解码为 PNG → 落盘 1110152/sfx/tex/
C 参数：源级逐项标注（source_flags）
输出：1110152/effects.json（v3）+ _target_1110171/FXSRC_1110152_viewer_effects.json（供 Lead 注入）
"""
import os, re, json, struct, hashlib, shutil, colorsys, sys
import numpy as np
from PIL import Image

WIKI = r'E:\la拆包项目\08Lifeafter wiki'
PACK = r'E:\la拆包项目\03拆包产物'
OUT = r'E:\la拆包项目\_target_1110171' if False else r'E:\la拆包项目\03拆包产物\_target_1110171'
S152 = os.path.join(WIKI, 'assets', '3d', 'weapon_skin', '1110152')
TEXDIR = os.path.join(S152, 'sfx', 'tex')
C159 = os.path.join(PACK, 'weapon', '002729.c159')
TRACKS = os.path.join(OUT, 'FXFX_tracks_1110152.json')
POOL_DIR = os.path.join(PACK, 'render_1003_010', '_sfx_010', 'texture_pool')
FEAT = os.path.join(PACK, 'render_1003_010', '_sfx_010', '_pool_features.json')
sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\06_皮肤定位链')
import dds_rgba_canonical as CAN

os.makedirs(TEXDIR, exist_ok=True)

# ---------- A 挂点 ----------
b = open(C159, 'rb').read()
m = re.search(rb'fx_idle_01', b)
mat = None
if m:
    end = m.end()
    for s in range(end + 4, min(end + 40, len(b) - 64)):
        v = list(struct.unpack_from('<16f', b, s))
        if any(x != x or abs(x) > 1e4 for x in v):
            continue
        colmaj = (abs(v[3]) < 1e-5 and abs(v[7]) < 1e-5 and abs(v[11]) < 1e-5 and abs(abs(v[15]) - 1) < 1e-5)
        basis = sum(1 for x in v if abs(x) > 0.001)
        if colmaj and basis >= 4:
            mat = {'offset': s, 'rel_to_name_end': s - end, 'matrix_colmajor': [round(float(x), 6) for x in v],
                   'translation': [round(v[12], 6), round(v[13], 6), round(v[14], 6)]}
            break
print('== A 挂点 002729.c159 fx_idle_01:', json.dumps(mat, ensure_ascii=False))
sock_names = [x.decode('latin1') for x in re.findall(rb'[\x20-\x7e]{3,}', b) if re.fullmatch(rb'fx_[\w]+|bag|hongwai|sound|muzzle_fire|rotation', x)]
print('   socket 名:', sock_names)

# ---------- C 参数（来自裸 XML，已交叉验证身份） ----------
tracks = json.load(open(TRACKS, encoding='utf-8'))
nodes = tracks['nodes']
pos_by_name = {n['name']: n.get('pos_offset') for n in nodes}

# ---------- B 贴图：内容特征候选 ----------
feat = json.load(open(FEAT, encoding='utf-8'))['rows']
feat = [f for f in feat if f.get('file')]
def score_ring(f):
    r = f.get('rings') or [0, 0, 0, 0]
    return (sum(r) / 4.0) - float(f.get('center') or 0) + 0.5 * float(f.get('edge') or 0)
def score_glow(f):
    return float(f.get('center') or 0) - 0.6 * float(f.get('edge') or 0) + 0.3 * float(f.get('frac_bright') or 0)
picks = {}
WANT = {
    'tex_ring_keji_hgz01_02.tga': ('ring', score_ring, '旋转光环贴图：环状（中心低、环带亮）'),
    'heitiane_04_lmq_djs.tga': ('ring', score_ring, '第二旋转光环：环状'),
    'glow25.tga': ('glow', score_glow, '枪口辉光：径向渐变、中心亮'),
}
used = set()
for logical, (kind, fn, why) in WANT.items():
    rows = [f for f in feat if f['file'] not in used]
    rows.sort(key=fn, reverse=True)
    top = rows[:5]
    best = top[0]
    picks[logical] = {'kind': kind, 'why': why, 'pool_file': best['file'], 'idx_hash': best['idx_hash'],
                      'sha16': best['sha16'], 'w': best['w'], 'h': best['h'], 'fourcc': best['fourcc'],
                      'features': {k: best[k] for k in ('rings', 'edge', 'periodic', 'frac_bright', 'center', 'corner')},
                      'top5': [{'file': t['file'], 'score': round(fn(t), 4)} for t in top]}
    used.add(best['file'])
print('\n== B 贴图候选（内容特征，非源级）==')
tex_meta = {}
for logical, p in picks.items():
    src = os.path.join(POOL_DIR, p['pool_file'])
    u8, prov = CAN.decode_dds_rgba_u8(src, verify_oiio=False)
    png_name = p['sha16'] + '.png'
    png_path = os.path.join(TEXDIR, png_name)
    Image.fromarray(u8, 'RGBA').save(png_path)
    rel = 'sfx/tex/' + png_name
    tex_meta[logical] = {'file': png_name, 'rel': rel, 'from_pool': p['pool_file'], 'bytes': os.path.getsize(png_path),
                         'sha256_16': hashlib.sha256(open(png_path, 'rb').read()).hexdigest()[:16],
                         'w': int(u8.shape[1]), 'h': int(u8.shape[0]), 'why': p['why'],
                         'features': p['features'], 'top5': p['top5']}
    print('   %-30s → %-24s (%dx%d) 依据=%s' % (logical, png_name, u8.shape[1], u8.shape[0], p['why']))
    print('      top5:', json.dumps(p['top5'], ensure_ascii=False))

# ---------- 生成 effects.json（v3） ----------
def build_node(n):
    tex = n.get('texture')
    tm = tex_meta.get(os.path.basename(tex.replace('\\', '/'))) if tex else None
    cn = {'name': n['name'], 'tag': n['tag'], 'pos_offset': n['pos_offset'], 'start': n['start'], 'life': n['life'],
          'radius': n['radius'], 'blend_mode': n['blend_mode'], 'texture': tex,
          'texture_candidate': (tm['file'] if tm else None),
          'texture_binding': ('candidate_content_feature_not_source' if tm else None),
          'is_sprite_sheet': bool(n.get('spr_work_mode') or (tex or '').endswith('.spr')),
          'color_track': (n['tracks'].get('ColorFrame') or []),
          'color_track_par': (n['tracks'].get('ColorFramePar') or []),
          'scale_track': (n['tracks'].get('scale_XScale') or []),
          'smooth_start': (n['tracks'].get('SmoothStartFrame') or []),
          'smooth_stop': (n['tracks'].get('SmoothStopFrame') or []),
          'emit': n.get('emit') or {}, 'fixpoint': n['tracks'].get('fixpoint'),
          'track_structure': '{time, value:[...]} 来自源 .sfx（已交叉验证身份）'}
    flags = {'texture_candidate': 'candidate' if tm else 'absent'}
    for k, src in (('start', 'FxStartTime'), ('life', 'FxLifeSpan'), ('radius', 'Radius'), ('blend_mode', 'BlendMode'),
                   ('texture', 'Texture'), ('pos_offset', 'PosOffset')):
        flags[k] = 'source_or_absent'
    if not n.get('radius'):
        flags['radius'] = 'derived' if n['tag'] in ('ParticleSystem', 'ParticleRes', 'Dummy', 'Model') else 'source'
    if not (n['tracks'].get('ColorFrame') or n['tracks'].get('ColorFramePar')):
        flags['color_track'] = 'absent_in_source'
    cn['source_flags'] = flags
    cn['renderable_by_adapter'] = (n['tag'] in ('Sprite', 'ParticleSystem')) and bool(tm)
    return cn

eff_nodes = [build_node(n) for n in nodes]
renderable = [n for n in eff_nodes if n['renderable_by_adapter']]
loop = max([n['life'] for n in nodes if n.get('life')] or [1.0])
eff = {
    'schema': 'lifeafter-weapon-skin-effects/3',
    'note': '节点/颜色/时序/半径/blend 全部来自源 .sfx（fx_skin_1012_009_idle_01.sfx）；贴图为内容特征候选（非源级）。',
    'skin': {'primary': 'skin_1012_009', 'secondary': None, 'display_name': '灵态诱导'},
    'status': 'partial',
    'status_reason': ('帧身份：c159 的 FxGroup 子引用（fx_skin_1012_009_idle_part_01/02.sfx）与 GPK 裸 XML 帧 f76037 的 '
                      'SfxName 完全一致，且类名表 {Sprite,Dummy,ParticleRes,Model} 与其标签分布一致、无 ParticleSystem '
                      '⇒ 源级同源（非候选）。贴图：fid 不在 idx_hash、2844 路径变体 0 命中 ⇒ 内容特征候选。'),
    'loop_seconds': loop,
    'assets_base': '',
    'textures_dir': 'sfx/tex/',
    'color_format': 'ColorFrame Value=(A,R,G,B)，alpha 由 SmoothStart/Stop 调制',
    'blend_mode_map': {'0': 'normal', '2': 'additive', '5': 'additive', '8': 'additive',
                       'note': '8/5 的精确语义未直接验证，按加法处理（approximate）'},
    'attach': {
        'mode': 'binding_fx_idle_01',
        'anchor': (mat or {}).get('translation', [0.0, 0.0, 0.0]),
        'evidence': ('源级：weapon/002729.c159（含 skin_1012_009 与 fx_idle_01）中 fx_idle_01 名后 @%s 的 16 float 列主序仿射，'
                     '平移量 %s；FX XML 侧无骨骼挂点（BindBonesHead/SelBindBonesIdx 见逐节点 source_flags）。'
                     '证据文件：FXSRC_build_1110152.json' % ((mat or {}).get('offset'), (mat or {}).get('translation'))),
        'matrix_colmajor': (mat or {}).get('matrix_colmajor'),
        'per_node_offset': pos_by_name,
        'unresolved': '同 c159 内其它 socket 的 4×4 对齐未逐一锁死（本皮肤只用 fx_idle_01）。',
    },
    'texture_binding_status': 'candidate_content_feature_not_source',
    'texture_binding_status_note': ('3 张贴图按内容特征从 effect 贴图池（875 dds + _pool_features.json）选取并规范解码为 RGBA PNG；'
                                    '源级精确绑定不可得：fid 不出现在 effect.idx 的 idx_hash；2844 条路径变体 × fid 索引 0 命中；'
                                    '项目 toolkit_core/texture_extractor.py 自述匿名 gpk 无路径 fid。'
                                    '选择依据见 texture_selection。'),
    'texture_selection': {k: {'why': v['why'], 'pool_file': v['from_pool'], 'features': v['features'],
                              'top5': v['top5'], 'png': v['file']} for k, v in tex_meta.items()},
    'frame_identity_evidence': {
        'source_path_exact': 'effect\\fx\\weapon\\skin\\skin_1012_009\\fx_skin_1012_009_idle_01.sfx',
        'fid': '205B2915C682DB02', 'fpk': '048.fpk entry 27222 @155777492 (packed 3726 / raw 33093, zstd)',
        'sha16': '33469786ecfaaf82',
        'xml_twin_frame': 'effect_01.gpk frame 76037 (size 78114)',
        'cross_check': 'c159 子引用 {idle_part_01, idle_part_02} == f76037 SfxName；类名表 vs 标签分布一致',
    },
    'unsupported': ['Model 节点（26 个）：模型特效，网页适配器不渲染',
                    'ParticleRes（4 个）：粒子资源引用，适配器不渲染',
                    'Dummy（6 个）：容器节点'],
    'pending': ['贴图=内容特征候选（非源级）', 'ParticleSystem 节点：本 fx 无'],
    'sfx_source': {'logical_path': 'effect\\fx\\weapon\\skin\\skin_1012_009\\fx_skin_1012_009_idle_01.sfx',
                   'sha16': '33469786ecfaaf82', 'bytes': 33093, 'encoding': 'c159-FxGroup(容器内) / 裸GBK XML(GPK同源帧)',
                   'container': 'XML FxGroup'},
    'nodes': eff_nodes,
}
json.dump(eff, open(os.path.join(S152, 'effects.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n== effects.json 已写 %s（节点 %d，其中适配器可渲染 %d）' % (os.path.join(S152, 'effects.json'), len(eff_nodes), len(renderable)))
# 供 Lead 注入的对象（不含 nodes 之外的多余东西？保留完整）
inj = dict(eff)
json.dump(inj, open(os.path.join(OUT, 'FXSRC_1110152_viewer_effects.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('   待注入对象 ->', os.path.join(OUT, 'FXSRC_1110152_viewer_effects.json'))
json.dump({'attach': mat, 'textures': tex_meta, 'renderable_nodes': [n['name'] for n in renderable]},
          open(os.path.join(OUT, 'FXSRC_build_1110152.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('   可渲染节点:', [n['name'] for n in renderable])
