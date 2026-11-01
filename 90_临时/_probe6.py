# -*- coding: utf-8 -*-
import sys, struct, pathlib, collections
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
    return rows
F=load('fashion_data')
v=lambda x: x[1] if isinstance(x,tuple) else x
c=collections.Counter(); tot=collections.Counter()
for r in F:
    pt=v(r['values'].get('part_type'))
    tot[pt]+=1
    if v(r['values'].get('reborn_vis')): c[pt]+=1
print('part_type : reborn_vis True / 总')
for k in tot: print(' ',k, c[k],'/',tot[k])
print('reborn_vis 总数', sum(c.values()))
# 名字样例
ex=[v(r['values'].get('name')) for r in F if v(r['values'].get('reborn_vis'))][:25]
print(ex)
