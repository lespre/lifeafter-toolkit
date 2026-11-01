# -*- coding: utf-8 -*-
"""挂饰真相：查 board 上挂饰卡的来源 + 它们对应 game 里的什么 + 谁有 charm"""
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
A=load('player_appear_data'); am={r['key']:r for r in A}
b=json.loads(pathlib.Path('02_wiki/web/data/boards/fashion_wardrobe.json').read_text(encoding='utf-8'))
def pb(it): return (it.get('part_bucket') or ['?'])[0]
pin=[it for it in b['items'] if pb(it)=='挂饰']
print('=== 板上 147 张挂饰卡：来源表 + 源行 part/part_type + charm ===')
c=collections.Counter()
for it in pin:
    ks=[int(k) for k in (it.get('row_keys') or []) if str(k).isdigit()]
    recs=[am[k] for k in ks if k in am]
    ptypes=tuple(sorted({str(v(r['values'].get('part_type'))) for r in recs}))
    hascharm=any(v(r['values'].get('charm_value')) is not None for r in recs)
    c[(ptypes, hascharm)]+=1
for k,n in c.most_common(): print('   ', k, n)
print()
print('=== 关键：这些挂饰卡在 fashion_data 里有对应行吗（挂饰也是时装商品）===')
F=load('fashion_data')
fnames={v(r['values'].get('name')) for r in F}
hit=0
for it in pin:
    if it.get('name') in fnames: hit+=1
print(f'  挂饰卡名能在 fashion_data 找到同名行的: {hit}/{len(pin)}')
print('  例:', [(it.get('name'), it.get('name') in fnames) for it in pin[:6]])
print()
print('=== 若有：fashion_data 同名行的 charm ===')
fmap={}
for r in F:
    fmap.setdefault(str(v(r['values'].get('name'))), []).append(r)
for it in pin[:8]:
    nm=it.get('name')
    rs=fmap.get(str(nm))
    if rs:
        r=rs[0]
        print(f"   {nm:16s} fashion_data key={r['key']} part={v(r['values'].get('part'))} type={v(r['values'].get('part_type'))} charm={v(r['values'].get('charm_value'))}")
