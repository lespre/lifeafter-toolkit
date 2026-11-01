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
# 1) 全表是否出现过 False
tf=collections.Counter()
for rows in (F,A):
    for r in rows:
        for k,(tag,v) in r['values'].items():
            if isinstance(v,bool): tf[(tag,v)]+=1
print('bool 值分布(全表):', tf.most_common(10))
print('出现过 False 吗:', any(k[1] is False for k in tf))

# 2) reborn_vis=1 的样例名字 + 部位
v=lambda x: x[1] if isinstance(x,tuple) else x
g=collections.Counter(); names=collections.defaultdict(list)
for r in F:
    if r['values'].get('reborn_vis'):
        pt=v(r['values'].get('part_type')) or '空'
        g[pt]+=1
        if len(names[pt])<12: names[pt].append(v(r['values'].get('name')))
print('\nreborn_vis 行按 part_type:', g.most_common())
for k,ns in names.items():
    print(' ',k,':', '、'.join(str(x) for x in ns))

# 3) socket_model_only_for_reborn 样例
print('\nsocket_model_only_for_reborn 行:')
c=0
for r in A:
    if r['values'].get('socket_model_only_for_reborn'):
        print(' ', r['key'], v(r['values'].get('name')), v(r['values'].get('part_type')),
              r['values'].get('socket_model_only_for_reborn'), 'sock=', str(r['values'].get('socket_names'))[:60])
        c+=1
        if c>=8: break
