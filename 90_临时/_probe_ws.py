# -*- coding: utf-8 -*-
"""weapon_skin_data / player_appear_v2_bag_data：挂饰 charm 会不会在这"""
import sys, pathlib, struct, collections
PROJ=pathlib.Path('E:/la拆包项目')
sys.path.insert(0,str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
CD=PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
def load(n):
    raw=(CD/f'{n}.py').read_bytes(); at=raw.find(b'x{')
    if at<0: return None
    L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
    pool=BT.parse_legacy_chs_pool((CD/f'{n}_chs.py').read_bytes())
    return BT.decode_table_rows(body,pool,resolve_jumps=False,lenient=True)[0]
v=lambda x: x[1] if isinstance(x,tuple) else x
for t in ('weapon_skin_data','player_appear_v2_bag_data'):
    r=load(t)
    print(f'== {t} ({len(r)} 行)')
    fs=collections.Counter()
    for x in r:
        for f,val in x['values'].items():
            if val not in (None,'',[],{}): fs[f]+=1
    print('  字段:', sorted(fs))
    for x in r[:4]:
        print('   ', x['key'], {k:str(v(val))[:46] for k,val in x['values'].items()})
    print()
