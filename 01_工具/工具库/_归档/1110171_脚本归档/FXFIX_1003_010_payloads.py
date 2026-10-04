# -*- coding: utf-8 -*-
"""FXFIX_1003_010_payloads.py — ① 枚举 skin_1003_010 全部 fx 载荷（GPK 内容通道 + FPK fid 通道）
② 001209.c159 全部 fx socket 与引用 ③ 每个候选载荷的特征（节点分布/颜色/贴图/Model/EndLessPlay/SfxName 子引用）
只读；写 _target_1110171\\FXFIX_*。
"""
import os, re, sys, json, glob, hashlib, collections, colorsys
sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\10_应用核心')
from toolkit_core.resource_resolver import path_id

PACK = r'E:\la拆包项目\03拆包产物'
OUT = os.path.join(PACK, '_target_1110171')
D = os.path.join(PACK, 'render_1003_010', '_sfx_010')
C159 = os.path.join(PACK, 'weapon', '001209.c159')
FIDX = json.load(open(os.path.join(PACK, 'fpk_fid_index.json'), encoding='utf-8'))['fid2info']

rep = {}

# ---------- ② c159 的全部 fx socket / 引用 ----------
b = open(C159, 'rb').read()
names = [m.group().decode('latin1') for m in re.finditer(rb'[\x20-\x7e]{3,}', b)]
fx_socks = [n for n in names if re.fullmatch(r'fx[_\w]*', n) or n in ('bag', 'sound', 'rotation', 'muzzle_fire', 'hongwai', 'pifuguashi')]
sfx_paths = sorted(set(x.decode('latin1') for x in re.findall(rb'[\x20-\x7e]*effect\\fx\\[\x20-\x7e]*\.sfx', b)))
rep['c159'] = {'path': C159, 'bytes': len(b), 'fx_sockets_all': fx_socks,
               'sfx_paths_in_c159': sfx_paths, 'n_ascii_strings': len(names),
               'all_names': names}
print('== 001209.c159 socket/引用 ==')
print('   fx socket 名:', fx_socks)
print('   c159 内 .sfx 路径:', sfx_paths)
print('   （全部可打印串 %d 条，见 FXFIX json）' % len(names))

# ---------- ①a GPK 内容通道：全部含 skin_1003_010 的 FxGroup 帧 ----------
def feat(txt, size, sha):
    tags = re.findall(r'<(Sprite|ParticleSystem|Dummy|Model|ParticleRes|Trail)\b', txt)
    tc = dict(collections.Counter(tags))
    tex = sorted(set(re.findall(r'Texture\s*=\s*"([^"]+)"', txt)))
    meshes = sorted(set(re.findall(r'ModelName\s*=\s*"([^"]+)"', txt)))
    child = sorted(set(re.findall(r'SfxName\s*=\s*"([^"]+)"', txt)))
    root = re.search(r'<FxGroup\b([^>]*)>', txt)
    ra = dict(re.findall(r'([A-Za-z_]\w*)\s*=\s*"([^"]*)"', root.group(1))) if root else {}
    # 颜色
    cols = collections.Counter()
    for m in re.finditer(r'<(?:ColorFrame|ColorFramePar)\b[^>]*Value\s*=\s*"([^"]+)"', txt):
        v = [float(x) for x in m.group(1).split(',') if x.strip()]
        if len(v) >= 4 and v[0] > 20:
            h, s, val = colorsys.rgb_to_hsv(v[1] / 255., v[2] / 255., v[3] / 255.)
            deg = h * 360
            if deg < 20 or deg > 340: cols['红/品红'] += 1
            elif deg < 70: cols['金/橙'] += 1
            elif deg < 160: cols['绿/青绿'] += 1
            elif deg < 215: cols['青/蓝'] += 1
            elif deg < 290: cols['紫'] += 1
            else: cols['品红'] += 1
    lives = [float(x) for x in re.findall(r'FxLifeSpan\s*=\s*"([\d.]+)"', txt)]
    return {'bytes': size, 'sha16': sha, 'tags': tc, 'n_nodes': len(tags),
            'has_model': tc.get('Model', 0), 'textures': tex,
            'meshes_1003_010': [m.split('\\')[-1] for m in meshes if '1003_010' in m],
            'child_sfx': child, 'end_less_play': ra.get('EndLessPlay'), 'loop': ra.get('Loop'),
            'max_life': max(lives or [0]), 'color_mix': dict(cols)}

gpk = []
for p in sorted(glob.glob(os.path.join(D, 'gpk_effect_01_*.bin'))):
    raw = open(p, 'rb').read()
    if b'<FxGroup' not in raw[:400]:
        continue
    t = raw.decode('gbk', 'replace')
    if 'skin_1003_010' not in t:
        continue
    sha = hashlib.sha256(raw).hexdigest()[:16]
    f = feat(t, len(raw), sha)
    f['frame'] = int(re.search(r'_f(\d+)_', os.path.basename(p)).group(1))
    gpk.append(f)
gpk.sort(key=lambda x: x['frame'])
rep['gpk_payloads'] = gpk
print('\n== ① GPK 内容通道：含 skin_1003_010 的 FxGroup 帧 = %d 个 ==' % len(gpk))
print('%-8s %-18s %-6s %-34s %-16s %s' % ('frame', 'sha16', 'nodes', 'tags', '颜色混合', '子引用/特征'))
for f in gpk:
    print('%-8d %-18s %-6d %-34s %-16s %s' % (
        f['frame'], f['sha16'], f['n_nodes'],
        json.dumps(f['tags'], ensure_ascii=False),
        json.dumps(f['color_mix'], ensure_ascii=False),
        ('child=%s ' % [c.split('/')[-1] for c in f['child_sfx']]) if f['child_sfx'] else '' +
        ('ELP=%s ' % f['end_less_play']) + ('maxLife=%.1f ' % f['max_life']) + ('M=%d ' % f['has_model'])))

# ---------- ①b FPK fid 通道 ----------
cands = []
base = r'effect\fx\weapon\skin\skin_1003_010\fx_skin_1003_010_%s.sfx'
for suf in ('idle_01', 'idle', 'idle_02', 'zs_01', 'zs_02', 'zs_03', 'zs_04', 'zs_05',
            'jisha_01', 'jisha_02', 'jisha_03', 'dm_01', 'dm_02', 'feichuai_ql_1', 'feichuai_ql_2',
            'show_01', 'mvp', 'mvp_01', 'attack_01', 'hit_01', 'ready_01', 'xuli_01'):
    cands.append(base % suf)
cands += [r'effect\fx\weapon\skin\skin_1003_010\fx_nucleus_attack_16_02_gyyt_%s.sfx' % s for s in ('01', '02')]
fid_hits = []
for c in cands:
    fid = '%016X' % path_id(c)
    if fid in FIDX:
        fid_hits.append({'path': c, 'fid': fid, 'info': FIDX[fid]})
rep['fpk_fid_probe'] = {'tried': len(cands), 'hits': fid_hits}
print('\n== ① FPK fid 通道：探测 %d 个命名 → 命中 %d 个 ==' % (len(cands), len(fid_hits)))
for h in fid_hits:
    print('   ★ %s fid=%s %s' % (h['path'], h['fid'], h['info']))
if not fid_hits:
    print('   ⇒ skin_1003_010 的 fx 载荷在 fid 索引中 0 命中（全部只存在于匿名 GPK）')

json.dump(rep, open(os.path.join(OUT, 'FXFIX_1003_010_payloads.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\njson ->', os.path.join(OUT, 'FXFIX_1003_010_payloads.json'))
