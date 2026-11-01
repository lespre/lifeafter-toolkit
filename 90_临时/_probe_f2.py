# -*- coding: utf-8 -*-
"""fashion_data 里有没有挂饰行？part=None 的 1625 行是什么"""
import sys, pathlib, struct, collections
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
F=load('fashion_data')
pn=[r for r in F if v(r['values'].get('part')) is None]
print('=== fashion_data part=None 的 1625 行：名字里有没有挂饰 ===')
kw=collections.Counter()
for r in pn:
    nm=str(v(r['values'].get('name')) or '')
    for k in ('挂饰','徽章','挂件','坠','铃','耳环','项链','手链','戒指','胸针','钥匙扣','配件'):
        if k in nm: kw[k]+=1
print('  关键词命中:', kw.most_common())
ex=[r for r in pn if any(k in str(v(r['values'].get('name')) or '') for k in ('挂饰','徽章','挂件'))]
print('  含挂饰/徽章/挂件的行:', len(ex))
for r in ex[:6]:
    d=r['values']
    print('   ', r['key'], v(d.get('name')), '| charm', v(d.get('charm_value')), '| part', v(d.get('part')), '| type', v(d.get('part_type')), '| level', v(d.get('level')), '| desc', str(v(d.get('desc')))[:40])
print()
print('=== fashion_data 全表：part 码 vs 有多少行 ===')
c=collections.Counter(str(v(r['values'].get('part'))) for r in F)
print(' ', c.most_common())
print()
print('=== ★ 关键：all_equips 里的挂饰名，能不能在 fashion_data 找到同名 ===')
import json
AE=json.loads(pathlib.Path('01_索引与产物/30_分析/all_equips_全量_node索引_20261029/all_equips_attrs_classic.json').read_text(encoding='utf-8'))['rows']
fnames={str(v(r['values'].get('name')) or '') for r in F}
pend_ae=[x for x in AE if x.get('equip_type')=='0']
hit=[x for x in pend_ae if str(x.get('name') or '') in fnames]
print(f'  all_equips equip_type=0 行 {len(pend_ae)} | 在 fashion_data 有同名的 {len(hit)}')
for x in hit[:6]: print('    ', x['key'], x['name'])
