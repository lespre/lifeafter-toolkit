# -*- coding: utf-8 -*-
"""module 表 desc「时装挂饰」分类 + charm 覆盖 + 板上对应"""
import sys, pathlib, struct, collections, json, re
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
M=load('player_module_appear_data')
print('=== module 表：desc 是否以「时装挂饰」开头 ===')
g=collections.defaultdict(lambda:[0,0,0])
for r in M:
    d=str(v(r['values'].get('desc')) or '')
    p=str(v(r['values'].get('part')))
    tag='时装挂饰' if d.startswith('时装挂饰') else ('其他' if d else '空')
    g[(p,tag)][0]+=1
    if v(r['values'].get('charm_value')) is not None: g[(p,tag)][1]+=1
for k in sorted(g):
    print(f'  part={k[0]:6s} desc={k[1]:8s} 行{g[k][0]:5d}  有charm {g[k][1]:5d}')
print()
print('=== ★ desc 含「时装挂饰」的 module 行 → charm 覆盖 ===')
ts=[r for r in M if str(v(r['values'].get('desc')) or '').startswith('时装挂饰')]
print('  行数', len(ts), '| 有 charm', sum(1 for r in ts if v(r['values'].get('charm_value')) is not None))
print('  part 分布:', collections.Counter(str(v(r['values'].get('part'))) for r in ts).most_common())
print('  charm 分布:', collections.Counter(v(r['values'].get('charm_value')) for r in ts).most_common())
print()
print('=== 佩戴部位提取（desc 里「可配戴在X部位」）===')
slot=collections.Counter()
for r in ts:
    d=str(v(r['values'].get('desc')) or '')
    m=re.search(r'可配戴在(.{1,4}?)部位', d)
    slot[m.group(1) if m else '(无)']+=1
print('  ', slot.most_common())
print()
print('=== 板上：module 卡按 desc 是否「时装挂饰」分组 ===')
b=json.loads(pathlib.Path('02_wiki/web/data/boards/fashion_wardrobe.json').read_text(encoding='utf-8'))
def pb(it): return (it.get('part_bucket') or ['?'])[0]
am={r['key']:r for r in M}
mc=[it for it in b['items'] if it.get('part_source')=='player_module_appear_data']
c=collections.Counter()
for it in mc:
    pk=(it.get('provenance') or {}).get('row_key')
    r=am.get(int(pk)) if pk and str(pk).isdigit() else None
    d=str(v(r['values'].get('desc')) or '') if r else ''
    tag='时装挂饰' if d.startswith('时装挂饰') else '其他'
    c[(tag, pb(it), bool(it.get('charm_value') is not None))]+=1
for k,n in sorted(c.items()): print(f'  {k[0]:8s} 桶{k[1]:4s} charm={k[2]} → {n} 张')
