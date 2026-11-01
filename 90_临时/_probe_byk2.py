# -*- coding: utf-8 -*-
import sys, struct, pathlib, collections
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
am={a['key']:a for a in A}

# 1) 白月魁 appear 行到底有没有 reborn 相关
for fm in (467480, 468880):
    fr=[r for r in F if r['key']==fm][0]
    ids=[int(str(v(fr['values']['appear_ids'])).split(':')[1])] if 'appear_ids' in fr['values'] else []
    print('== fashion', fm, v(fr['values'].get('name')), 'appear_ids', ids)
    for aid in ids:
        a=am.get(aid)
        if not a: print('   ', aid, 'MISS'); continue
        d=a['values']
        print('   ', aid, {k:v(x) for k,x in d.items() if k in
            ('name','part','gender','model_name','high_model_name','socket_names','socket_models',
             'socket_model_only_for_reborn','reborn_vis','hide_in_bag','is_slim_bag')})

# 2) socket_model_only_for_reborn 全表分布
c=collections.Counter(); ex=[]
for a in A:
    if a['values'].get('socket_model_only_for_reborn'):
        c[v(a['values'].get('part'))]+=1
        if len(ex)<8: ex.append((a['key'], v(a['values'].get('name')), v(a['values'].get('part'))))
print('\nsocket_model_only_for_reborn 总数', sum(c.values()), '按部位', c.most_common())
print('样例', ex)

# 3) reborn_vis 覆盖：款式数 vs 全量款式数
import re
base=lambda s: re.sub(r'-\d+天$','',str(s))
allb={base(v(r['values'].get('name'))) for r in F}
rb={base(v(r['values'].get('name'))) for r in F if r['values'].get('reborn_vis')}
print('\n全量款式', len(allb), '带 reborn', len(rb), f'{len(rb)/len(allb):.1%}')
# 按部位
for pt in ('cloth','hat','suit'):
    a2={base(v(r['values'].get('name'))) for r in F if v(r['values'].get('part_type'))==pt}
    b2={base(v(r['values'].get('name'))) for r in F if v(r['values'].get('part_type'))==pt and r['values'].get('reborn_vis')}
    print(f'  {pt}: {len(b2)}/{len(a2)} = {len(b2)/max(1,len(a2)):.1%}')
