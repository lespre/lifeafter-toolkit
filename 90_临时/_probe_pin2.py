# -*- coding: utf-8 -*-
"""挂饰在 module 表(part=20001) vs appear 表(part=5) 的交叉：是不是同一批？"""
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

m20001=[r for r in M if str(v(r['values'].get('part')))=='20001']
m1=[r for r in M if str(v(r['values'].get('part')))=='1']
a5=[r for r in A if str(v(r['values'].get('part')))=='5']
print('module part=20001 行', len(m20001), '| part=1 行', len(m1), '| appear part=5 行', len(a5))
print()
print('=== module part=20001 的样例 ===')
for r in m20001[:5]:
    d=r['values']
    print('  ', r['key'], v(d.get('name')), '| charm', v(d.get('charm_value')), '| icon', v(d.get('icon')), '| part_type', v(d.get('part_type')), '| desc', str(v(d.get('desc')))[:44])
print()
print('=== appear part=5 的样例 ===')
for r in a5[:5]:
    d=r['values']
    print('  ', r['key'], v(d.get('name')), '| charm', v(d.get('charm_value')), '| part_type', v(d.get('part_type')), '| socket', v(d.get('socket_models')) if 'socket_models' in d else '(jump)')
print()
# 名字交集
mn={v(r['values'].get('name')) for r in m20001}
an={v(r['values'].get('name')) for r in a5}
print('module part=20001 名字数', len(mn), '| appear part=5 名字数', len(an), '| 交集', len(mn&an))
print('  交集样例:', list(mn&an)[:6])
print('  仅 module:', list(mn-an)[:6])
print('  仅 appear:', list(an-mn)[:6])
print()
# 板上：module 卡分桶逻辑 —— 121 头饰 + 56 面饰 + 13 挂饰
mcards=[it for it in b['items'] if it.get('part_source')=='player_module_appear_data']
print('=== 板上 module 卡分桶 ===')
for bucket in ('头饰','面饰','挂饰'):
    xs=[it for it in mcards if pb(it)==bucket]
    print(f'  {bucket} {len(xs)} 张 | 有charm {sum(1 for it in xs if it.get("charm_value") is not None)} | 样例:', [it.get('name') for it in xs[:3]])
print()
print('=== module part=20001 的行在板上被引用了吗 ===')
used=set()
for it in mcards:
    pk=(it.get('provenance') or {}).get('row_key')
    if pk: used.add(str(pk))
    for k in (it.get('row_variants') or []): used.add(str(k))
hit=[r for r in m20001 if str(r['key']) in used]
print('  part=20001 被引用行', len(hit), '/', len(m20001))
print('  这些行所属卡:', collections.Counter(pb([it for it in mcards if str((it.get("provenance") or {}).get("row_key")) in {str(r["key"]) for r in hit} or any(str(k) in {str(r["key"]) for r in hit} for k in (it.get("row_variants") or []))][0]) for it in mcards if ((it.get("provenance") or {}).get("row_key") in {str(r["key"]) for r in hit}) or any(str(k) in {str(r["key"]) for r in hit} for k in (it.get("row_variants") or []))).most_common())
