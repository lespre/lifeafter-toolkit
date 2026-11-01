# -*- coding: utf-8 -*-
import sys, struct, pathlib
PROJ = pathlib.Path('E:/la拆包项目')
sys.path.insert(0, str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
CD = PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
def load(n):
    raw=(CD/f'{n}.py').read_bytes(); at=raw.find(b'x{')
    L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
    cnt=struct.unpack_from('<I',body,0)[0]; blob=body[8+4*cnt:]
    pool=BT.parse_legacy_chs_pool((CD/f'{n}_chs.py').read_bytes())
    rows=BT.decode_table_rows(body,pool,resolve_jumps=False,lenient=True)[0]
    return rows, blob, pool
A,ab,ap=load('player_appear_data')
am={a['key']:a for a in A}
for k in (150002, 50002, 3500401, 13500401, 13363301, 3363301, 13365801):
    a=am.get(k)
    if not a: print(k,'MISSING'); continue
    print('==',k,{f:(str(v)[:70]) for f,v in a['values'].items()})
    print()
M,mb,mp=load('player_module_appear_data')
print('module rows',len(M))
mk={m['key']:m for m in M}
for k in (150002,13500401,3500401,13365801):
    m=mk.get(k)
    print('module',k,'->', {f:str(v)[:60] for f,v in m['values'].items()} if m else 'MISSING')
