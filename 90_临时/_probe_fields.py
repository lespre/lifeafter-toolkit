# -*- coding: utf-8 -*-
import sys, struct, pathlib
PROJ = pathlib.Path('E:/la拆包项目')
sys.path.insert(0, str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core.bindict_table import decode_table_rows, parse_legacy_chs_pool
CD = PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
def load(n):
    raw=(CD/f'{n}.py').read_bytes(); at=raw.find(b'x{')
    L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
    pool=parse_legacy_chs_pool((CD/f'{n}_chs.py').read_bytes())
    rows,unb=decode_table_rows(body,pool,resolve_jumps=False,lenient=True)
    return rows
for t in ('fashion_data','player_appear_data'):
    rows=load(t)
    print('==',t,'rows',len(rows))
    ks=list(rows[0]['values'].keys())
    print('fields',len(ks)); print(ks)
    best=max(rows[:400], key=lambda x: len(x['values']))
    print('row fields', len(best['values']))
    for k in ks:
        if k in best['values']:
            print('  ',k,'=',repr(best['values'][k])[:160])
