# -*- coding: utf-8 -*-
"""挂饰(pendant) 魅力值来源：挂饰是道具，走 common_item / item 表？"""
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
A=load('player_appear_data')
pend=[r for r in A if v(r['values'].get('part_type'))=='pendant']
print('=== pendant 200 行的全部字段（并集）+ 非空数 ===')
fs=collections.Counter(); nn=collections.Counter()
for r in pend:
    for f,x in r['values'].items():
        fs[f]+=1
        if x not in (None,'',[],{}): nn[f]+=1
for f in sorted(fs):
    print(f'   {f:28s} 有键{fs[f]:4d} 非空{nn[f]:4d}')
print()
print('=== 挂饰的 model_id 分布（39 是什么）===')
print(collections.Counter(v(r['values'].get('model_id')) for r in pend).most_common(8))
print()
print('=== model_id=39 的行：是不是「挂饰模型」共用的 ===')
for r in pend[:3]:
    d=r['values']
    print('  ', r['key'], v(d.get('name')), '| model_id', v(d.get('model_id')), '| level', v(d.get('level')), '| model_change_color_id', v(d.get('model_change_color_id')), '| sort_key', v(d.get('sort_key')))
print()
print('=== 有没有「时装品级 → 魅力值」的表（level 1..6 的 charm）===')
F=load('fashion_data')
g=collections.defaultdict(set)
for r in F:
    lv=v(r['values'].get('level')); cv=v(r['values'].get('charm_value'))
    if cv is not None: g[lv].add(cv)
for lv in sorted(g, key=lambda x: str(x)):
    vals=sorted(g[lv])
    print(f'  level {lv}: charm 取值 {vals[:14]}{" …" if len(vals)>14 else ""} ({len(vals)} 个)')
