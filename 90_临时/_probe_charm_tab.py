# -*- coding: utf-8 -*-
"""挂饰魅力值的真正来源表：fashion_charm_desc_data / fashion_charm_reward_data 等"""
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
for t in ('fashion_charm_desc_data','fashion_charm_reward_data','fashion_charm_first_in_popup_data','fashion_charm_period_data'):
    r=load(t)
    if not r: print('!!',t); continue
    fs=collections.Counter()
    for x in r:
        for f in x['values']: fs[f]+=1
    print(f'== {t}: {len(r)} 行 | 字段 {sorted(fs)}')
    for x in r[:4]:
        print('   ', x['key'], {k:str(v(val))[:56] for k,val in x['values'].items()})
    print()
