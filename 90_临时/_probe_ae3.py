# -*- coding: utf-8 -*-
"""挂饰名 → all_equips 行：能否对上？覆盖多少？"""
import pathlib, struct, collections, sys, json, re
PROJ=pathlib.Path('E:/la拆包项目')
sys.path.insert(0,str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
D=PROJ/'03_执行/pe_all_equips_基线分片'
raw=(D/'all_equips_data__fid1F8E.py').read_bytes()
at=raw.find(b'x{'); L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
cnt=struct.unpack_from('<I',body,0)[0]; blob=body[8+4*cnt:]
pool=BT.parse_legacy_chs_pool((D/'all_equips_data_chs__fid94AB.py').read_bytes())
AE=BT.decode_table_rows(body,pool,resolve_jumps=False,lenient=True)[0]
v=lambda x: x[1] if isinstance(x,tuple) else x
A=BT.decode_table_rows(*(lambda n: (lambda r,b,p: (r,b,p))(*(
    (lambda raw2: (lambda at2,L2: (raw2[at2+6:at2+6+L2],))(raw2, struct.unpack_from('<I',raw2,at2+2)[0])
  )( (PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata/player_appear_data.py').read_bytes().find(b'x{') ))(
    (lambda raw2: (lambda at2,L2: (struct.unpack_from('<I',raw2,at2+2)[0],))(raw2,0))(0)) )) if False else (None,None,None)
print()
# 简化：直接读 player_appear_data
def load(n, cd):
    raw=(cd/f'{n}.py').read_bytes(); at=raw.find(b'x{')
    L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
    c2=struct.unpack_from('<I',body,0)[0]; blob=body[8+4*c2:]
    p=BT.parse_legacy_chs_pool((cd/f'{n}_chs.py').read_bytes())
    return BT.decode_table_rows(body,p,resolve_jumps=False,lenient=True)[0]
CD=PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
PA=load('player_appear_data', CD)
pend=[r for r in PA if v(r['values'].get('part_type'))=='pendant']
pnames=collections.defaultdict(list)
for r in pend: pnames[str(v(r['values'].get('name')))].append(r)
# all_equips 按名索引（equip_type=0 且有 charm）
aen=collections.defaultdict(list)
for r in AE:
    nm=str(v(r['values'].get('name')) or '')
    if str(v(r['values'].get('equip_type')))=='0':
        aen[nm].append(r)
hit=[nm for nm in pnames if nm in aen]
print(f'挂饰(pendant) 唯一名 {len(pnames)} | 在 all_equips equip_type=0 里同名 {len(hit)}')
hitc=[nm for nm in hit if any(v(r["values"].get("charm_value")) is not None for r in aen[nm])]
print(f'  其中对方有 charm 的: {len(hitc)}')
print('  样例:')
for nm in hit[:10]:
    r=aen[nm][0]
    print(f"    {nm:16s} equip key {r['key']} charm {v(r['values'].get('charm_value'))} level {v(r['values'].get('level'))} | 挂饰行 {pnames[nm][0]['key']} level {v(pnames[nm][0]['values'].get('level'))}")
print()
print('=== 未对上的挂饰样例 ===')
miss=[nm for nm in pnames if nm not in aen]
print('  ', len(miss), miss[:10])
