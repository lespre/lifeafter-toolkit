# -*- coding: utf-8 -*-
"""挂饰 charm 是不是按 level 给：对照 module 表 part=2 的 (level, charm) 分档
挂饰 pendant: level 3(72) 4(126) 5(2)
module part=2: level3→10, level4→10/50/100/200, level5→200/350"""
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
A=load('player_appear_data'); M=load('player_module_appear_data')
print('=== 所有表里 charm × level 的对应（看 charm 是否只由 level 决定）===')
for t,rows in (('fashion_data',None),('player_appear_data',A),('player_module_appear_data',M)):
    if rows is None: rows=load('fashion_data')
    g=collections.defaultdict(set)
    for r in rows:
        lv=v(r['values'].get('level')); cv=v(r['values'].get('charm_value'))
        if cv is not None: g[lv].add(cv)
    print(f'  == {t}')
    for lv in sorted(g, key=lambda x: str(x)):
        vals=sorted(g[lv])
        print(f'     level {str(lv):5s} → charm {vals[:12]}{" …" if len(vals)>12 else ""} ({len(vals)})')
