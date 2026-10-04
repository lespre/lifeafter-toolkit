# -*- coding: utf-8 -*-
"""FXSRC_build_1110171.py <frame-bin> <variant-tag> — 为 1110171 生成 effects.json + 待注入对象。
A 挂点：001209.c159 fx_idle_01 4×4 = 平移 (0,0,1.4462)（源级）
C 参数：源 ColorFrame/TrackScale/Smooth*
B 贴图：内容特征候选（candidate_content_feature_not_source）
frame_binding：candidate_between_two_content_verified_frames（f74635 / f74631 两帧都通过内容归属验证）
"""
import os, sys, json, re, struct, hashlib, collections
import numpy as np
from PIL import Image

FRAME = sys.argv[1]
TAG = sys.argv[2]
WIKI = r'E:\la拆包项目\08Lifeafter wiki'
PACK = r'E:\la拆包项目\03拆包产物'
OUT = os.path.join(PACK, '_target_1110171')
S1171 = os.path.join(WIKI, 'assets', '3d', 'weapon_skin', '1110171')
TEXDIR = os.path.join(S1171, 'sfx', 'tex')
C159 = os.path.join(PACK, 'weapon', '001209.c159')
POOL_DIR = os.path.join(PACK, 'render_1003_010', '_sfx_010', 'texture_pool')
FEAT = os.path.join(PACK, 'render_1003_010', '_sfx_010', '_pool_features.json')
EXIST_CAND = os.path.join(PACK, 'render_1003_010', '_sfx_010', 'texture_candidates.json')
sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\06_皮肤定位链')
import dds_rgba_canonical as CAN
import importlib.util
spec = importlib.util.spec_from_file_location('pst', os.path.join(r'E:\la拆包项目\01拆包器本体\工具库\06_皮肤定位链', 'parse_sfx_tracks.py'))
pst = importlib.util.module_from_spec(spec); spec.loader.exec_module(pst)

os.makedirs(TEXDIR, exist_ok=True)
TR = os.path.join(OUT, 'FXSRC_%s_tracks_1110171.json' % TAG)
pst.main(FRAME, TR)
tracks = json.load(open(TR, encoding='utf-8'))
nodes = tracks['nodes']

# A：c159 fx_idle_01 4×4（已锁死：列主序仿射，平移 (0,0,1.4462)）
b = open(C159, 'rb').read()
m = re.search(rb'fx_idle_01', b)
mat = None
for s in range(m.end() + 4, m.end() + 40):
    v = list(struct.unpack_from('<16f', b, s))
    if any(x != x or abs(x) > 1e4 for x in v):
        continue
    if abs(v[3]) < 1e-5 and abs(v[7]) < 1e-5 and abs(v[11]) < 1e-5 and abs(abs(v[15]) - 1) < 1e-5 and sum(1 for x in v if abs(x) > 1e-3) >= 4:
        mat = {'offset': s, 'matrix_colmajor': [round(float(x), 6) for x in v],
               'translation': [round(v[12], 6), round(v[13], 6), round(v[14], 6)]}
        break

feat = [f for f in json.load(open(FEAT, encoding='utf-8'))['rows'] if f.get('file')]
exist = json.load(open(EXIST_CAND, encoding='utf-8'))
def score_ring(f):
    r = f.get('rings') or [0, 0, 0, 0]
    return (sum(r) / 4.0) - float(f.get('center') or 0) + 0.5 * float(f.get('edge') or 0)
def score_glow(f):
    return float(f.get('center') or 0) - 0.6 * float(f.get('edge') or 0) + 0.3 * float(f.get('frac_bright') or 0)

want = collections.OrderedDict()
for n in nodes:
    if n.get('texture'):
        want.setdefault(os.path.basename(n['texture'].replace('\\', '/')), n['tag'])
used = set()
tex_meta = {}
for logical, tag in want.items():
    if logical in exist:
        pool_file = exist[logical]
        why = '复用已有候选映射（texture_candidates.json）=%s' % pool_file
        kind = 'existing_candidate_map'
    else:
        kind = 'ring' if ('ring' in logical or 'ray' in logical) else 'glow'
        fn = score_ring if kind == 'ring' else score_glow
        rows = [f for f in feat if f['file'] not in used]
        rows.sort(key=fn, reverse=True)
        pool_file = rows[0]['file']
        why = '内容特征候选（%s，得分 %.4f，top5=%s）' % (kind, fn(rows[0]), [round(fn(x), 4) for x in rows[:5]])
    used.add(pool_file)
    u8, _ = CAN.decode_dds_rgba_u8(os.path.join(POOL_DIR, pool_file), verify_oiio=False)
    png = os.path.splitext(pool_file)[0] + '.png'
    Image.fromarray(u8, 'RGBA').save(os.path.join(TEXDIR, png))
    tex_meta[logical] = {'png': png, 'rel': 'sfx/tex/' + png, 'pool': pool_file, 'kind': kind, 'why': why,
                         'w': int(u8.shape[1]), 'h': int(u8.shape[0]),
                         'sha256_16': hashlib.sha256(open(os.path.join(TEXDIR, png), 'rb').read()).hexdigest()[:16]}
print('贴图 %d 种 → %d 张 PNG' % (len(want), len(tex_meta)))

def build_node(n):
    tex = n.get('texture')
    tm = tex_meta.get(os.path.basename(tex.replace('\\', '/'))) if tex else None
    cn = {'name': n['name'], 'tag': n['tag'], 'pos_offset': n['pos_offset'], 'start': n['start'], 'life': n['life'],
          'radius': n['radius'], 'blend_mode': n['blend_mode'], 'texture': tex,
          'texture_candidate': (tm['png'] if tm else None),
          'texture_binding': ('candidate_content_feature_not_source' if tm else None),
          'is_sprite_sheet': bool(n.get('spr_work_mode') or (tex or '').endswith('.spr')),
          'color_track': (n['tracks'].get('ColorFrame') or []), 'color_track_par': (n['tracks'].get('ColorFramePar') or []),
          'scale_track': (n['tracks'].get('scale_XScale') or []),
          'smooth_start': (n['tracks'].get('SmoothStartFrame') or []), 'smooth_stop': (n['tracks'].get('SmoothStopFrame') or []),
          'emit': n.get('emit') or {}, 'fixpoint': n['tracks'].get('fixpoint'),
          'track_structure': '{time, value:[...]} 来自源 .sfx'}
    flags = {'texture_candidate': 'candidate' if tm else 'absent'}
    for k in ('start', 'life', 'radius', 'blend_mode', 'texture', 'pos_offset'):
        flags[k] = 'source' if (k != 'radius' or n.get('radius')) else 'derived'
    if not (n['tracks'].get('ColorFrame') or n['tracks'].get('ColorFramePar')):
        flags['color_track'] = 'absent_in_source'
    cn['source_flags'] = flags
    cn['renderable_by_adapter'] = (n['tag'] in ('Sprite', 'ParticleSystem')) and bool(tm)
    return cn

eff_nodes = [build_node(n) for n in nodes]
renderable = [n for n in eff_nodes if n['renderable_by_adapter']]
loop = max([n['life'] for n in nodes if n.get('life')] or [2.0])
eff = {
    'schema': 'lifeafter-weapon-skin-effects/3',
    'note': '节点/颜色/时序/半径/blend 来自源 .sfx；贴图为内容特征候选（非源级）。A 挂点=001209.c159 fx_idle_01 4×4（源级）。',
    'skin': {'primary': 'skin_1003_010', 'secondary': 'skin_1003_012', 'display_name': '光影咏叹调'},
    'status': 'partial',
    'status_reason': ('【上游元数据自证错误】render_1003_010/_sfx_010/effect_skin_1003_010_zs_02.json 的 found_in 自述'
                      '「effect_01.gpk frame 14761 (zstd frame, 内容实证含 skin_1003_010)」，但实测该帧内 skin_1003_010 出现 0 次，'
                      '其 ModelName/SfxName 全属 skin_1006_010 ⇒ 现有（旧版）effects.json 的 8 Sprite + 5 ParticleSystem 正来自该错帧。'
                      '本份改用内容归属已验证的帧：%s。' % os.path.basename(FRAME)) +
                     ('frame_binding=candidate_between_two_content_verified_frames（f74635 44节点 / f74631 43节点，二者内容均属 skin_1003_010，'
                      '哪一个是 zs_02 无名字索引可证；本份=%s）。' % TAG) +
                     '贴图：fid 不在 idx_hash、2844 路径变体 × fid 索引 0 命中 ⇒ 内容特征候选。',
    'frame_binding': 'candidate_between_two_content_verified_frames',
    'frame_evidence': {'frame_bin': os.path.basename(FRAME), 'nodes': len(nodes),
                       'content_check': 'skin_1003_010 出现 48~50 次（另一候选同）；skin_1006_010 出现 0 次',
                       'sibling': '另一候选 f74631(43节点, 083bd15770f26221) / f74635(44节点, 59115620b779a5e8)'},
    'loop_seconds': loop, 'assets_base': '', 'textures_dir': 'sfx/tex/',
    'color_format': 'ColorFrame Value=(A,R,G,B)，alpha 由 SmoothStart/Stop 调制',
    'blend_mode_map': {'0': 'normal', '2': 'additive', '5': 'additive', '8': 'additive'},
    'attach': {'mode': 'binding_fx_idle_01', 'anchor': (mat or {}).get('translation', [0.0, 0.0, 1.4462]),
               'evidence': ('源级：weapon/001209.c159 内 fx_idle_01 名后 @%s 的 16 float 列主序仿射，平移量 %s；'
                            'FX XML 侧无骨骼挂点（BindBonesHead=FALSE / SelBindBonesIdx="" / AnchorSum=0）。'
                            % ((mat or {}).get('offset'), (mat or {}).get('translation'))),
               'matrix_colmajor': (mat or {}).get('matrix_colmajor'),
               'per_node_offset': {n['name']: n['pos_offset'] for n in nodes},
               'unresolved': '其它 socket（bag/hongwai/sound/muzzle_fire）4×4 对齐未锁死，本皮肤不使用。'},
    'texture_binding_status': 'candidate_content_feature_not_source',
    'texture_selection': {k: {'why': v['why'], 'pool': v['pool'], 'png': v['png']} for k, v in tex_meta.items()},
    'sfx_source': {'logical_path': 'effect\\fx\\weapon\\skin\\skin_1003_010\\fx_skin_1003_010_zs_02.sfx',
                   'frame_bin': os.path.basename(FRAME), 'nodes': len(nodes),
                   'encoding': 'GBK XML (FxGroup)，取自 GPK 帧', 'container': 'XML FxGroup'},
    'unsupported': ['Model 节点：模型特效，适配器不渲染', 'ParticleRes：粒子资源', 'Dummy：容器节点'],
    'pending': ['frame_binding 二选一未定（f74635/f74631）', '真实 zs_02 的帧↔名绑定需名字索引（不可得）'],
    'nodes': eff_nodes,
}
json.dump(eff, open(os.path.join(S1171, 'effects.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
injf = os.path.join(OUT, 'FXSRC_1110171_%s_viewer_effects.json' % TAG)
json.dump(eff, open(injf, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('effects.json -> %s（节点 %d，可渲染 %d）' % (os.path.join(S1171, 'effects.json'), len(eff_nodes), len(renderable)))
print('注入对象 -> %s' % injf)
print('可渲染节点:', [n['name'] for n in renderable])
print('贴图:', json.dumps({k: v['png'] for k, v in tex_meta.items()}, ensure_ascii=False))
print('attach.anchor =', eff['attach']['anchor'], '| loop =', loop, '| frame =', os.path.basename(FRAME))
