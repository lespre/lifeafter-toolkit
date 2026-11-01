# -*- coding: utf-8 -*-
"""挂饰在游戏里到底是哪个部位？查 part=5 的三类与 module 表挂件的关系 + 物品分类表"""
import sys, pathlib, struct, collections, json, re
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
print('=== part=5 的三类：名字 + model 路径特征 ===')
for ptype in ('light','pendant',None):
    rs=[r for r in A if str(v(r['values'].get('part')))=='5' and str(v(r['values'].get('part_type')))==ptype]
    print(f'\n-- part_type={ptype} ({len(rs)} 行)')
    names=[v(r['values'].get('name')) for r in rs]
    print('   名字样例:', names[:8])
    # 首个非空 model 路径
    got=0
    for r in rs:
        for f in ('model_name','high_model_name','socket_models'):
            pass
        break
    print('   key 样例:', [r['key'] for r in rs[:5]])
print()
print('=== 板上「荧光棒」桶 228 张来自哪些 part_type ===')
b=json.loads(pathlib.Path('02_wiki/web/data/boards/fashion_wardrobe.json').read_text(encoding='utf-8'))
def pb(it): return (it.get('part_bucket') or ['?'])[0]
lig=[it for it in b['items'] if pb(it)=='荧光棒']
print('  荧光棒卡', len(lig), '| source:', collections.Counter(str(it.get('source'))[:40] for it in lig).most_common(3))
# 抽一个看其 row_keys 在 A 里的 part/part_type
am={r['key']:r for r in A}
for it in lig[:3]:
    ks=[int(k) for k in (it.get('row_keys') or []) if str(k).isdigit()]
    for k in ks[:2]:
        r=am.get(k)
        if r: print('   ', it.get('name'), '| key', k, 'part', v(r['values'].get('part')), 'type', v(r['values'].get('part_type')), 'charm', v(r['values'].get('charm_value')))
print()
print('=== 关键：module 表 part=2/20001 里 desc 说「挂饰」的 19+? 行 ===')
M=load('player_module_appear_data')
for pt in ('2','20001'):
    rs=[r for r in M if str(v(r['values'].get('part')))==pt and '挂饰' in str(v(r['values'].get('desc')) or '')]
    print(f'  part={pt} 含「挂饰」desc 的行 {len(rs)}')
    for r in rs[:4]:
        print('    ', r['key'], v(r['values'].get('name')), '| charm', v(r['values'].get('charm_value')), '| desc', str(v(r['values'].get('desc')))[:56])
