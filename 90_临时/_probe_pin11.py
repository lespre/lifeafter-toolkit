# -*- coding: utf-8 -*-
"""挂饰 charm 是否按 level 给：① 衣/头/包 的 charm × level 关系 ② 有没有 level→charm 表"""
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
A=load('player_appear_data'); M=load('player_module_appear_data')
print('=== ① player_module_appear_data: part=20001/2 的 charm × level 交叉 ===')
g=collections.defaultdict(lambda: collections.Counter())
for r in M:
    p=str(v(r['values'].get('part')))
    lv=v(r['values'].get('level'))
    cv=v(r['values'].get('charm_value'))
    if p in ('1','2','20001') and cv is not None:
        g[(p, lv)][cv]+=1
for k in sorted(g, key=lambda x:(x[0], str(x[1]))):
    print(f'  part={k[0]:6s} level={str(k[1]):5s} → charm {dict(g[k])}')
print()
print('=== ② part=20001 的 charm 分布（这批全是 390 行有 charm）===')
c=collections.Counter()
for r in M:
    if str(v(r['values'].get('part')))=='20001':
        c[v(r['values'].get('charm_value'))]+=1
print('  ', c.most_common())
print()
print('=== ③ 挂饰 pendant 的 level 分布（挂饰 level=4 常见）===')
lv=collections.Counter()
for r in A:
    if v(r['values'].get('part_type'))=='pendant':
        lv[v(r['values'].get('level'))]+=1
print('  pendant level 分布:', lv.most_common())
print()
print('=== ④ 对照：module part=20001 的 level 分布 ===')
lv2=collections.Counter()
for r in M:
    if str(v(r['values'].get('part')))=='20001':
        lv2[v(r['values'].get('level'))]+=1
print('  part=20001 level 分布:', lv2.most_common())
