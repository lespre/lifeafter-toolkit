# -*- coding: utf-8 -*-
import sys, pathlib, struct, collections
PROJ = pathlib.Path('E:/la拆包项目')
sys.path.insert(0, str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
CD = PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
def load(n):
    raw=(CD/f'{n}.py').read_bytes(); at=raw.find(b'x{')
    if at<0: return None
    L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
    pool=BT.parse_legacy_chs_pool((CD/f'{n}_chs.py').read_bytes())
    rows=BT.decode_table_rows(body,pool,resolve_jumps=False,lenient=True)[0]
    return rows, body, pool
v=lambda x: x[1] if isinstance(x,tuple) else x

for t in ('cohabit_level_data','home_level_data'):
    got=load(t)
    if not got: print('!!', t, '无 legacy 结构'); continue
    rows, body, pool = got
    print(f'== {t} rows={len(rows)}')
    fields=set()
    for r in rows: fields|=set(r['values'].keys())
    print('   字段', sorted(fields))
    for r in rows[:6]:
        print('   ', r['key'], {k:str(v(x))[:40] for k,x in r['values'].items() if 'friend' in k.lower() or k in ('level','name','id','value','desc')})
    print()

# player_appear_data 的 friendliness
A,ab,ap=load('player_appear_data')
fl=[(a['key'], v(a['values'].get('name')), v(a['values'].get('friendliness'))) for a in A if a['values'].get('friendliness')]
print('player_appear_data 有 friendliness 的行:', len(fl), '例:', fl[:6])
