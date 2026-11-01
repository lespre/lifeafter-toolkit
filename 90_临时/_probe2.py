# -*- coding: utf-8 -*-
import sys, struct, pathlib, json, collections
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
F=load('fashion_data'); A=load('player_appear_data')
print('F rows',len(F),'A rows',len(A))
cnt=collections.Counter()
for r in F:
    for k in r['values']: cnt[k]+=1
print('fashion字段总数',len(cnt))
for k,v in cnt.most_common(): print(f'  {k:32s}{v}')
