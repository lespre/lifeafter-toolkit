# -*- coding: utf-8 -*-
"""FXSRC_pathid_lookup.py — 用项目已验证的 path_id（双 Murmur3 x86_32，UTF-8、反斜杠逻辑路径）
在 fpk_fid_index.json(fid→容器/条目/offset/size) 里精确定位 .sfx 与贴图。只读源 + 写本目录。

验证：先用文档已知样例 qiangpi.cube → D763973EACDC554E 校验实现。
"""
import json, os, struct, sys, glob

sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\10_应用核心')
from toolkit_core.resource_resolver import path_id, murmur3_x86_32

OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
IDX = r'E:\la拆包项目\03拆包产物\fpk_fid_index.json'
print('已知样例校验：qiangpi.cube → 期望 D763973EACDC554E')
for v in ('qiangpi.cube', 'common\\env_map\\qiangpi.cube', 'env_map\\qiangpi.cube', 'effect\\fx\\weapon\\skin\\skin_1003_010\\fx_skin_1003_010_zs_02.sfx'):
    fid = path_id(v)
    print('   %-70s fid=%016X' % (v, fid))

print('\n加载 fpk_fid_index.json ...')
d = json.load(open(IDX, encoding='utf-8'))
f2i = d['fid2info']
print('  条目数', len(f2i), ' 顶层键', list(d.keys()))
sample = list(f2i.items())[:2]
print('  样例:', sample)

TARGETS = [
    'effect\\fx\\weapon\\skin\\skin_1003_010\\fx_skin_1003_010_zs_02.sfx',
    'effect\\fx\\weapon\\skin\\skin_1012_009\\fx_skin_1012_009_idle_01.sfx',
    'effect\\fx\\weapon\\skin\\skin_1006_004\\fx_skin_1006_004_zishen.sfx',
    'effect\\textures\\glow\\glow_01.tga',
    'effect\\textures\\glow\\glow25.tga',
    'effect\\textures\\ring\\tex_ring_keji_hgz01_02.tga',
]
rep = {}
for t in TARGETS:
    fid = path_id(t)
    key = '%016X' % fid
    info = f2i.get(key)
    rep[t] = {'fid': key, 'info': info}
    print('  %-72s fid=%s → %s' % (t, key, info))
json.dump({'results': rep, 'index_size': len(f2i)}, open(os.path.join(OUT, 'FXSRC_pathid_lookup.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\njson ->', os.path.join(OUT, 'FXSRC_pathid_lookup.json'))
