# -*- coding: utf-8 -*-
import pathlib, struct, collections, sys
PROJ=pathlib.Path('E:/la拆包项目')
sys.path.insert(0,str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
v=lambda x: x[1] if isinstance(x,tuple) else x
def load_legacy(cd, n):
    raw=(cd/f'{n}.py').read_bytes(); at=raw.find(b'x{')
    L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
    c2=struct.unpack_from('<I',body,0)[0]; blob=body[8+4*c2:]
    p=BT.parse_legacy_chs_pool((cd/f'{n}_chs.py').read_bytes())
    return BT.decode_table_rows(body,p,resolve_jumps=False,lenient=True)[0]
def load_dir(d, name, poolname):
    raw=(d/name).read_bytes(); at=raw.find(b'x{')
    L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
    c2=struct.unpack_from('<I',body,0)[0]; blob=body[8+4*c2:]
    p=BT.parse_legacy_chs_pool((d/poolname).read_bytes())
    return BT.decode_table_rows(body,p,resolve_jumps=False,lenient=True)[0]

D=PROJ/'03_执行/pe_all_equips_基线分片'
AE=load_dir(D, 'all_equips_data__fid1F8E.py', 'all_equips_data_chs__fid94AB.py')
CD=PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
PA=load_legacy(CD, 'player_appear_data')
pend=[r for r in PA if v(r['values'].get('part_type'))=='pendant']
pnames=collections.defaultdict(list)
for r in pend: pnames[str(v(r['values'].get('name')))].append(r)
aen=collections.defaultdict(list)
for r in AE:
    if str(v(r['values'].get('equip_type')))=='0':
        aen[str(v(r['values'].get('name')) or '')].append(r)
hit=[nm for nm in pnames if nm in aen]
hitc=[nm for nm in hit if any(v(r['values'].get('charm_value')) is not None for r in aen[nm])]
print(f'挂饰(pendant) 唯一名 {len(pnames)} | all_equips equip_type=0 同名 {len(hit)} | 其中有charm {len(hitc)}')
print('样例:')
for nm in hit[:12]:
    r=aen[nm][0]
    print(f"  {nm:18s} equip {r['key']} charm {v(r['values'].get('charm_value'))} lv {v(r['values'].get('level'))} | 挂饰行 {pnames[nm][0]['key']} lv {v(pnames[nm][0]['values'].get('level'))}")
miss=[nm for nm in pnames if nm not in aen]
print(f'未同名 {len(miss)}:', miss[:12])
