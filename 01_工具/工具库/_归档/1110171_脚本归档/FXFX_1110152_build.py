# -*- coding: utf-8 -*-
"""FXFX_1110152_build.py — ① 试贴图精确化（path_id 是否出现在 effect 贴图池的 idx_hash 中）
② 用已交叉验证身份的裸 XML 帧 f76037（= fx_skin_1012_009_idle_01.sfx）解析出源级节点树。
只读；写本目录 FXFX_*。
"""
import os, sys, json, re, importlib.util, collections
sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\10_应用核心')
from toolkit_core.resource_resolver import path_id

OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
POOL = r'E:\la拆包项目\03拆包产物\render_1003_010\_sfx_010\effect_texture_pool.json'
FRAME = os.path.join(OUT, 'FX152_gpk_effect_01_f76037_f1befd4d7588500f.bin')

# ① 贴图：idx_hash 里是否含 path_id
pool = json.load(open(POOL, encoding='utf-8'))
idx_h = set(e['idx_hash'] for e in pool['entries'])
tex_paths = [r'effect\textures\glow\glow25.tga', r'effect\textures\ring\tex_ring_keji_hgz01_02.tga',
             r'effect\textures\special\heitiane_04_lmq_djs.tga', r'effect\textures\glow\glow_01.tga']
hits = []
for t in tex_paths:
    fid = '%016X' % path_id(t)
    fidl = fid.lower()
    for h in idx_h:
        if fidl in h or h.startswith(fidl[:12]):
            hits.append({'path': t, 'fid': fid, 'idx_hash': h})
print('== 贴图 fid 是否出现在 idx_hash 中: %d 命中' % len(hits))
for h in hits: print('   ', h)
print('   （idx_hash 样例 %s）' % list(idx_h)[:3])

# ② 解析 f76037（已交叉验证 = idle_01）
TOOL = r'E:\la拆包项目\01拆包器本体\工具库\06_皮肤定位链\parse_sfx_tracks.py'
spec = importlib.util.spec_from_file_location('pst', TOOL)
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
dst = os.path.join(OUT, 'FXFX_tracks_1110152.json')
mod.main(FRAME, dst)
d = json.load(open(dst, encoding='utf-8'))
nodes = d['nodes']
tags = collections.Counter(n['tag'] for n in nodes)
tex = sorted(set(n['texture'] for n in nodes if n.get('texture')))
print('\n== f76037 (=1110152 idle_01) 节点 %d  %s' % (len(nodes), json.dumps(dict(tags), ensure_ascii=False)))
print('   根属性:', json.dumps(d.get('root_attrib'), ensure_ascii=False)[:300])
print('   贴图引用 %d 种:' % len(tex))
for t in tex: print('      ', t)
print('   anomalies:', len(d.get('anomalies') or []))
# 颜色：能否解释青色
import colorsys
cy = gold = 0
samples = []
for n in nodes:
    for key in ('ColorFrame', 'ColorFramePar'):
        for f in (n['tracks'].get(key) or []):
            v = f['value']
            if len(v) >= 4 and v[0] > 20:
                h, s, vv = colorsys.rgb_to_hsv(v[1] / 255., v[2] / 255., v[3] / 255.)
                deg = h * 360
                if 140 <= deg <= 215 and s > 0.2:
                    cy += 1
                    if len(samples) < 4: samples.append({'node': n['name'], 'rgba': v, 'hue': round(deg)})
                if 20 <= deg <= 70 and s > 0.2:
                    gold += 1
print('   青色调帧 %d / 金调帧 %d；青样例 %s' % (cy, gold, json.dumps(samples, ensure_ascii=False)))
json.dump({'texture_fid_hits': hits, 'node_count': len(nodes), 'tags': dict(tags), 'textures': tex,
           'cyan_frames': cy, 'gold_frames': gold, 'cyan_samples': samples,
           'root_attrib': d.get('root_attrib')},
          open(os.path.join(OUT, 'FXFX_1110152_probe.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('json ->', os.path.join(OUT, 'FXFX_1110152_probe.json'))
