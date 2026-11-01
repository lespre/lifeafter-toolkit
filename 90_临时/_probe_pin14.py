# -*- coding: utf-8 -*-
"""挂饰 charm：common_item_data / appear_id_2_equip_id / all_equips_data"""
import sys, pathlib, struct, collections
PROJ=pathlib.Path('E:/la拆包项目')
sys.path.insert(0,str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
CD=PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
def load(n):
    raw=(CD/f'{n}.py').read_bytes(); at=raw.find(b'x{')
    if at<0: return None
    L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
    try:
        pool=BT.parse_legacy_chs_pool((CD/f'{n}_chs.py').read_bytes())
    except Exception:
        return None
    return BT.decode_table_rows(body,pool,resolve_jumps=False,lenient=True)[0]
v=lambda x: x[1] if isinstance(x,tuple) else x

# appear_id_2_equip_id：appear_id → equip_id？
print('=== appear_id_2_equip_id ===')
r=load('appear_id_2_equip_id')
if r:
    print('  行', len(r))
    for x in r[:6]:
        print('   ', x['key'], {k:str(v(val))[:50] for k,val in x['values'].items()})
else:
    print('  legacy 解不出（可能是 nxs 新格式）')
print()
print('=== common_item_data ===')
r=load('common_item_data')
if r:
    fs=collections.Counter(); nn=collections.Counter()
    for x in r:
        for f,val in x['values'].items():
            fs[f]+=1
            if val not in (None,'',[],{}): nn[f]+=1
    print('  行', len(r), '| 字段', sorted(fs))
    print('  ★ 含 charm 的字段:')
    for f in sorted(fs):
        if 'charm' in f.lower() or 'meili' in f.lower() or 'attr' in f.lower() or 'value' in f.lower():
            print(f'     {f:28s} 非空 {nn[f]}')
    for x in r[:3]:
        print('   ', x['key'], {k:str(v(val))[:44] for k,val in list(x['values'].items())[:8]})
else:
    print('  legacy 解不出')
