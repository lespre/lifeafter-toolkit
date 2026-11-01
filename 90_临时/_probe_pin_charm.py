# -*- coding: utf-8 -*-
"""挂饰魅力值：板上挂饰卡到底来自哪些表？module 表 part=20001 有没有 charm？"""
import sys, pathlib, struct, collections, json
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
M=load('player_module_appear_data'); A=load('player_appear_data')
b=json.loads(pathlib.Path('02_wiki/web/data/boards/fashion_wardrobe.json').read_text(encoding='utf-8'))
def pb(it): return (it.get('part_bucket') or ['?'])[0]

print('=== ① player_module_appear_data 按 part 的 charm 覆盖 ===')
g=collections.defaultdict(lambda:[0,0,0])
for r in M:
    pt=str(v(r['values'].get('part')))
    g[pt][0]+=1
    if v(r['values'].get('charm_value')) is not None: g[pt][1]+=1
    if v(r['values'].get('model_paths')): g[pt][2]+=1
print('  part | 行数 | 有charm | 有model_paths')
for pt in sorted(g): print(f'  {pt:8s} {g[pt][0]:5d} {g[pt][1]:6d} {g[pt][2]:8d}')

print()
print('=== ② 板上挂饰卡的来源与 charm ===')
pin=[it for it in b['items'] if pb(it)=='挂饰']
print('  挂饰卡', len(pin))
print('  按 id 前缀:', collections.Counter(it['id'].split('_')[0] for it in pin).most_common())
print('  按 part_source:', collections.Counter(it.get('part_source') or '(无)' for it in pin).most_common())
print('  有 charm:', sum(1 for it in pin if it.get('charm_value') is not None))
# module 卡的 part=20001
m20001=[r for r in M if str(v(r['values'].get('part')))=='20001']
print('  module 表 part=20001 行数:', len(m20001), '| 有 charm:', sum(1 for r in m20001 if v(r['values'].get('charm_value')) is not None))
# 这些 module 卡在板上吗
mcards=[it for it in b['items'] if it.get('part_source')=='player_module_appear_data']
print('  板上 module 卡', len(mcards), '| 分桶:', collections.Counter(pb(it) for it in mcards).most_common())
print('  板上 module 卡有 charm:', sum(1 for it in mcards if it.get('charm_value') is not None))
print()
print('=== ③ 面上 147 张挂饰的 id 前缀 × 有charm ===')
c=collections.Counter()
for it in pin:
    c[(it['id'].split('_')[0], bool(it.get('charm_value') is not None))]+=1
print('  ', c.most_common())
