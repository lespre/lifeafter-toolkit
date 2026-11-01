# -*- coding: utf-8 -*-
import sys, struct, pathlib, collections
PROJ = pathlib.Path('E:/la拆包项目')
sys.path.insert(0, str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
sys.path.insert(0, str(PROJ/'02_wiki/web/tools'))
import importlib
m = importlib.import_module('enrich_fashion_dimensions')
fmap, amap = m.load_board_rows()
only_m = collections.Counter()
samples=[]
for k,fr in fmap.items():
    ids=[x for x in fr['appear_ids'] if isinstance(x,int)]
    f_app = amap.get(ids[0]) if len(ids)>0 else None
    m_app = amap.get(ids[1]) if len(ids)>1 else None
    s,n = m.gender_scope_of(fr, f_app, m_app)
    if s=='仅男':
        mn=(m_app or {}).get('model_name') or (m_app or {}).get('high_model_name') or ''
        key = '_m_' if '_m_' in str(mn) else ('_f_' if '_f_' in str(mn) else 'other')
        only_m[key]+=1
        if len(samples)<6: samples.append((k, fr['name'], ids, mn, (f_app or {}).get('name')))
print('仅男 by 模型路径:', only_m)
for s in samples: print(' ',s)
# 也统计整体 order 检查
tot=collections.Counter()
for k,fr in fmap.items():
    ids=[x for x in fr['appear_ids'] if isinstance(x,int)]
    if len(ids)<2: tot['len<2']+=1; continue
    f0=amap.get(ids[0]); m1=amap.get(ids[1])
    p0=(f0 or {}).get('model_name') or ''
    p1=(m1 or {}).get('model_name') or ''
    tot[(('f' if '_f_' in str(p0) else ('m' if '_m_' in str(p0) else '-')),('f' if '_f_' in str(p1) else ('m' if '_m_' in str(p1) else '-')))]+=1
for k,v in tot.most_common(10): print(k,v)
