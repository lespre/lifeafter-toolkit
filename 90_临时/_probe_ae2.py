# -*- coding: utf-8 -*-
"""解 all_equips_data 完整表：挂饰的 charm_value"""
import pathlib, struct, collections, sys, json
PROJ=pathlib.Path('E:/la拆包项目')
sys.path.insert(0,str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
D=PROJ/'03_执行/pe_all_equips_基线分片'
raw=(D/'all_equips_data__fid1F8E.py').read_bytes()
at=raw.find(b'x{')
L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
cnt=struct.unpack_from('<I',body,0)[0]; blob=body[8+4*cnt:]
pool=BT.parse_legacy_chs_pool((D/'all_equips_data_chs__fid94AB.py').read_bytes())
rows=BT.decode_table_rows(body,pool,resolve_jumps=False,lenient=True)[0]
print('行', len(rows))
v=lambda x: x[1] if isinstance(x,tuple) else x
# charm 覆盖
ch=[r for r in rows if v(r['values'].get('charm_value')) is not None]
print('有 charm_value 的行:', len(ch))
# equip_type=0（挂饰）
p0=[r for r in rows if str(v(r['values'].get('equip_type')))=='0']
print('equip_type=0 行:', len(p0), '| 有 charm', sum(1 for r in p0 if v(r['values'].get('charm_value')) is not None))
print()
print('=== 挂饰（equip_type=0）样例 ===')
for r in p0[:8]:
    d=r['values']
    print('  ', r['key'], str(v(d.get('name')))[:22], '| charm', v(d.get('charm_value')), '| level', v(d.get('level')), '| type', v(d.get('type')))
print()
print('=== 名字含「挂饰/徽章/挂件」的行 ===')
for r in rows:
    nm=str(v(r['values'].get('name')) or '')
    if any(k in nm for k in ('挂饰','徽章','挂件')):
        d=r['values']
        print('  ', r['key'], nm[:24], '| equip_type', v(d.get('equip_type')), '| charm', v(d.get('charm_value')), '| level', v(d.get('level')), '| slot', v(d.get('slot')), '| type', v(d.get('type')))
