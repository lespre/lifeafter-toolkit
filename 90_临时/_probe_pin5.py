# -*- coding: utf-8 -*-
"""module 表 part=1/2/20001 到底是什么部位 + 板上分桶是否正确"""
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

print('=== module 表按 part 的 desc 部位关键词（细分）===')
for pt in ('1','2','20001'):
    rs=[r for r in M if str(v(r['values'].get('part')))==pt]
    kw=collections.Counter()
    for r in rs:
        d=str(v(r['values'].get('desc')) or '')
        for k in ('眼睛','面部','头部','头顶','脸部','可配戴在'):
            if k in d: kw[k]+=1
    # 提取「可配戴在X部位」
    slot=collections.Counter()
    for r in rs:
        d=str(v(r['values'].get('desc')) or '')
        m=re.search(r'可配戴在(.{1,6}?)部位', d)
        if m: slot[m.group(1)]+=1
    print(f'  part={pt:6s} ({len(rs):4d} 行) 关键词 {kw.most_common(5)}')
    print(f'          佩戴部位: {slot.most_common(5)}')
print()
print('=== 板上 module 卡：name → 桶 / charm（看分桶对不对）===')
b=json.loads(pathlib.Path('02_wiki/web/data/boards/fashion_wardrobe.json').read_text(encoding='utf-8'))
def pb(it): return (it.get('part_bucket') or ['?'])[0]
mc=[it for it in b['items'] if it.get('part_source')=='player_module_appear_data']
# 每个卡的 prov.row_key → module 行 → part
am={r['key']:r for r in M}
cross=collections.Counter()
for it in mc:
    pk=(it.get('provenance') or {}).get('row_key')
    r=am.get(int(pk)) if pk and str(pk).isdigit() else None
    p=str(v(r['values'].get('part'))) if r else '?'
    cross[(p, pb(it))]+=1
print('  module part → 板上桶:')
for k,n in sorted(cross.items()): print(f'    part={k[0]:6s} → 桶 {k[1]:4s} {n:4d} 张')
print()
print('  样例（头饰桶 vs 面饰桶）:')
for bucket in ('头饰','面饰','挂饰'):
    xs=[it for it in mc if pb(it)==bucket][:3]
    for it in xs:
        pk=(it.get('provenance') or {}).get('row_key')
        r=am.get(int(pk)) if pk and str(pk).isdigit() else None
        d=str(v(r['values'].get('desc')) or '')[:50] if r else ''
        print(f'    [{bucket}] {it.get("name"):16s} charm={it.get("charm_value")} desc={d}')
