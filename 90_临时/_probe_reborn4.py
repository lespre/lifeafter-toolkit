# -*- coding: utf-8 -*-
import sys, struct, pathlib, collections
PROJ = pathlib.Path('E:/la拆包项目')
sys.path.insert(0, str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
CD = PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
def load(n):
    raw=(CD/f'{n}.py').read_bytes(); at=raw.find(b'x{')
    L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
    pool=BT.parse_legacy_chs_pool((CD/f'{n}_chs.py').read_bytes())
    return BT.decode_table_rows(body,pool,resolve_jumps=False,lenient=True)[0]
F=load('fashion_data'); A=load('player_appear_data')
v=lambda x: x[1] if isinstance(x,tuple) else x

both=[r for r in F if r['values'].get('reborn_vis') and r['values'].get('replace_flower_path')]
print('reborn_vis=1 且有 replace_flower_path 的行:', len(both))
fl=[r for r in F if r['values'].get('replace_flower_path')]
print('replace_flower_path 行总数:', len(fl), '其中有 reborn_vis:', sum(1 for r in fl if r['values'].get('reborn_vis')))

# 去时长变体后，"款"数
def base(nm):
    import re
    return re.sub(r'-\d+天$','',str(nm))
s1={base(v(r['values'].get('name'))) for r in F if r['values'].get('reborn_vis')}
print('reborn_vis 去时限后款式数:', len(s1))
s2={base(v(r['values'].get('name'))) for r in F if r['values'].get('replace_flower_path')}
print('换花款式:', sorted(s2))

# 换花的 5 款衣服，看它们 reborn_vis / show_no_have / part_type
print()
for r in F:
    if r['values'].get('replace_flower_path'):
        print(' ', v(r['values'].get('name')), '| reborn=', bool(r['values'].get('reborn_vis')),
              '| show_no_have=', v(r['values'].get('show_no_have')))
