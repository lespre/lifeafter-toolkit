# -*- coding: utf-8 -*-
"""按 part_type 细分：pendant / light 的 charm 覆盖；再全库找含 charm 的表"""
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
A=load('player_appear_data')
print('=== player_appear_data 按 (part, part_type) 的 charm 覆盖 ===')
g=collections.defaultdict(lambda:[0,0])
for r in A:
    k=(str(v(r['values'].get('part'))), str(v(r['values'].get('part_type'))))
    g[k][0]+=1
    if v(r['values'].get('charm_value')) is not None: g[k][1]+=1
for k in sorted(g, key=lambda x:(x[0],x[1])):
    print(f'  part={k[0]:6s} type={k[1]:8s} 行{g[k][0]:5d}  有charm {g[k][1]:5d}')
print()
print('=== pendant 行的 charm 值样例 ===')
pend=[r for r in A if v(r['values'].get('part_type'))=='pendant']
print('  pendant 行', len(pend), '| 有 charm', sum(1 for r in pend if v(r['values'].get('charm_value')) is not None))
for r in pend[:5]:
    d=r['values']
    print('   ', r['key'], v(d.get('name')), '| charm', v(d.get('charm_value')), '| level', v(d.get('level')), '| part', v(d.get('part')))
print()
print('=== 全库：含 charm_value 字段的表 ===')
hits=[]
for p in CD.glob('*.py'):
    if p.name.endswith('_chs.py'): continue
    try: r=load(p.stem)
    except Exception: continue
    if not r: continue
    fs=set()
    for x in r:
        fs |= set(x['values'].keys())
    if 'charm_value' in fs:
        nn=sum(1 for x in r if v(x['values'].get('charm_value')) is not None)
        hits.append((p.stem, len(r), nn))
for t,n,nn in sorted(hits, key=lambda x:-x[2]):
    print(f'  {t:44s} 行{n:6d}  有charm {nn:6d}')
