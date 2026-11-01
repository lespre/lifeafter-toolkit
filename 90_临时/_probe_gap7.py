# -*- coding: utf-8 -*-
"""all_equips_data（戒指/半感染者装备）能不能解出 charm/model"""
import sys, pathlib, collections
PROJ=pathlib.Path('E:/la拆包项目')
sys.path.insert(0,str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import cdata_nxs
CD=PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
t=cdata_nxs.load_table('all_equips_data', CD)
print('kind', t.kind, 'rows', len(t.rows))
fs=collections.Counter()
for r in t.rows:
    for k in r['fields']: fs[k]+=1
print('字段并集:', sorted(fs))
for r in t.rows[:3]:
    print('  ', r['key'], {k:str(v)[:50] for k,v in list(r['fields'].items())[:10]})
