# -*- coding: utf-8 -*-
import sys, pathlib, collections, ast
PROJ=pathlib.Path('E:/la拆包项目')
sys.path.insert(0,str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import cdata_nxs
CD=PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
for stem in ('appear_id_2_equip_id','common_item_data','all_equips_data'):
    print('==', stem)
    try:
        t=cdata_nxs.load_table(stem, CD)
        print('  kind', t.kind, 'rows', len(t.rows))
        if t.rows:
            fs=collections.Counter()
            for r in t.rows: fs |= collections.Counter(r['fields'].keys())
            print('  字段:', sorted(fs))
            for r in t.rows[:4]:
                print('   ', r['key'], {k:str(v)[:44] for k,v in list(r['fields'].items())[:7]})
    except Exception as e:
        print('  fail', type(e).__name__, str(e)[:120])
    print()
