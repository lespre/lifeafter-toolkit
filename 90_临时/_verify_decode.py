# -*- coding: utf-8 -*-
"""验证 friendliness 不是解错/名字引错：
① schema 是表文件自带的（不是外部映射），dump 一整行看语义自洽性
② 同一款时装在 3 张独立表里解出的 friendliness 是否一致
"""
import sys, pathlib, struct, collections
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
v=lambda x: x[1] if isinstance(x,tuple) else x

F,fb,fp=load('fashion_data')
A,ab,ap=load('player_appear_data')
X,xb,xp=load('fashion_data_for_export')
print('=== ① fashion_data 一整行的字段（看是否语义自洽）===')
r=[x for x in F if x['key']==1960][0] if any(x['key']==1960 for x in F) else F[0]
print('key', r['key'], 'schema_ref', r.get('schema'))
items=list(r['values'].items())
for k,val in items:
    s=str(val)
    print(f'   {k:32s} {s[:78]}')
