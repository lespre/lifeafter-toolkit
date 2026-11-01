# -*- coding: utf-8 -*-
import sys, struct, pathlib, collections, re
PROJ = pathlib.Path('E:/la拆包项目')
sys.path.insert(0, str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
CD = PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
def load(n):
    raw=(CD/f'{n}.py').read_bytes(); at=raw.find(b'x{')
    L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
    return BT.decode_table_rows(body,BT.parse_legacy_chs_pool((CD/f'{n}_chs.py').read_bytes()),resolve_jumps=False,lenient=True)[0]
F=load('fashion_data'); A=load('player_appear_data')
v=lambda x: x[1] if isinstance(x,tuple) else x

# 1) socket_model_only_for_reborn 的 15 行全列
print('=== socket_model_only_for_reborn 15 行 ===')
for a in A:
    if a['values'].get('socket_model_only_for_reborn'):
        print(' ', a['key'], v(a['values'].get('name')), 'gender', v(a['values'].get('gender')),
              'sock', v(a['values'].get('socket_names')), v(a['values'].get('socket_models')))

# 2) 这 15 行对应的商品是否都有 replace_flower_path
names={v(a['values'].get('name')) for a in A if a['values'].get('socket_model_only_for_reborn')}
print('\n涉及款名:', sorted(names))
fh=[(r['key'], v(r['values'].get('name'))) for r in F if r['values'].get('replace_flower_path')]
print('换花行数', len(fh), '款', sorted({n for _,n in fh}))

# 3) 白月魁 appear 行是否在 module 表
M=load('player_module_appear_data')
mk={m['key']:m for m in M}
print('\nplayer_module_appear_data rows', len(M))
for k in (463901, 284328):
    m=mk.get(k)
    print(' ', k, {f:v(x) for f,x in m['values'].items()} if m else 'MISS')

# 4) reborn_vis 的 135 款里，有没有同时在 module 表
