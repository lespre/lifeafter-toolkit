# -*- coding: utf-8 -*-
"""fashion_data 按 part 码的 charm 覆盖 + part=5 是什么"""
import sys, pathlib, struct, collections
PROJ=pathlib.Path('E:/la拆包项目')
sys.path.insert(0,str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
CD=PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
def load(n):
    raw=(CD/f'{n}.py').read_bytes(); at=raw.find(b'x{')
    L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
    pool=BT.parse_legacy_chs_pool((CD/f'{n}_chs.py').read_bytes())
    return BT.decode_table_rows(body,pool,resolve_jumps=False,lenient=True)[0]
v=lambda x: x[1] if isinstance(x,tuple) else x
F=load('fashion_data')
print('=== fashion_data 按 (part, part_type) 的 charm 覆盖 ===')
g=collections.defaultdict(lambda:[0,0])
for r in F:
    k=(str(v(r['values'].get('part'))), str(v(r['values'].get('part_type'))))
    g[k][0]+=1
    if v(r['values'].get('charm_value')) is not None: g[k][1]+=1
for k in sorted(g, key=lambda x:(x[0],x[1])):
    print(f'  part={k[0]:6s} type={k[1]:8s} 行{g[k][0]:5d}  有charm {g[k][1]:5d}')
print()
print('=== fashion_data part=5 的样例 ===')
p5=[r for r in F if str(v(r['values'].get('part')))=='5']
for r in p5[:8]:
    d=r['values']
    print('  ', r['key'], v(d.get('name')), '| type', v(d.get('part_type')), '| charm', v(d.get('charm_value')), '| level', v(d.get('level')))
print()
print('=== fashion_data part=5 且 part_type 空 的行（老款？）===')
p5n=[r for r in F if str(v(r['values'].get('part')))=='5' and not v(r['values'].get('part_type'))]
print('  行数', len(p5n), '| 有 charm', sum(1 for r in p5n if v(r['values'].get('charm_value')) is not None))
for r in p5n[:6]:
    d=r['values']
    print('   ', r['key'], v(d.get('name')), '| charm', v(d.get('charm_value')), '| level', v(d.get('level')), '| brand', v(d.get('brand_id')))
