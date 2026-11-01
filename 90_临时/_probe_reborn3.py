# -*- coding: utf-8 -*-
import sys, struct, pathlib, collections, re
PROJ = pathlib.Path('E:/la拆包项目')
sys.path.insert(0, str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
CD = PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
def load(n):
    raw=(CD/f'{n}.py').read_bytes(); at=raw.find(b'x{')
    L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
    pool=BT.parse_legacy_chs_pool((CD/f'{n}_chs.py').read_bytes())
    return BT.decode_table_rows(body,pool,resolve_jumps=False,lenient=True)[0]
F=load('fashion_data')
v=lambda x: x[1] if isinstance(x,tuple) else x
KW=('典藏','幻彩','限定','典')
def bucket(nm):
    for k in KW:
        if k in nm: return k
    return '普通'
c1=collections.Counter(); c0=collections.Counter()
for r in F:
    nm=str(v(r['values'].get('name')) or '')
    b=bucket(nm)
    (c1 if r['values'].get('reborn_vis') else c0)[b]+=1
print('reborn_vis=1 :', c1.most_common())
print('其余        :', c0.most_common())
t1=sum(c1.values()); t0=sum(c0.values())
print(f'典藏类占比: reborn=1 {c1["典藏"]/t1:.1%}  其余 {c0["典藏"]/t0:.1%}')

# 交叉：reborn_vis 与 part_type / 是否有 high model
print()
pt=collections.Counter()
for r in F:
    pt[(v(r['values'].get('part_type')), bool(r['values'].get('reborn_vis')))]+=1
for k in sorted(pt, key=lambda x:(str(x[0]),x[1])):
    print('  part',k,pt[k])

# 名字里含"典藏"的部品行分布
print()
print('典藏名字总数:', sum(1 for r in F if '典藏' in str(v(r['values'].get('name')) or '')))
print('reborn_vis=1 且非典藏 样例:')
n=0
for r in F:
    if r['values'].get('reborn_vis') and '典藏' not in str(v(r['values'].get('name')) or ''):
        print('   ', v(r['values'].get('name')), v(r['values'].get('part_type')))
        n+=1
        if n>=12: break
