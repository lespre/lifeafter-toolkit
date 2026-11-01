# -*- coding: utf-8 -*-
"""板上挂饰卡 35 张 part_type=None 的真实身份"""
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
print('=== 35 张 part_type=None 的挂饰卡：名字 + 源行全部字段 ===')
n=0
for it in pin:
    ks=[int(k) for k in (it.get('row_keys') or []) if str(k).isdigit()]
    recs=[am[k] for k in ks if k in am]
    if not recs: continue
    ptypes={str(v(r['values'].get('part_type'))) for r in recs}
    if ptypes!={'None'}: continue
    n+=1
    if n>6: break
    print(' ==', it.get('name'), '| keys', ks[:3], '| card charm', it.get('charm_value'))
    for r in recs[:2]:
        d=r['values']
        print('    行', r['key'], {k:str(v(x))[:50] for k,x in d.items()})
print()
print('=== part_type=None 且 part=5 的 310 行：都是挂饰吗 ===')
p5n=[r for r in A if str(v(r['values'].get('part')))=='5' and not v(r['values'].get('part_type'))]
print('  行数', len(p5n))
print('  名字样例:', [v(r['values'].get('name')) for r in p5n[:12]])
print('  有 socket_models:', sum(1 for r in p5n if r['values'].get('socket_models')))
print('  有 charm:', sum(1 for r in p5n if v(r['values'].get('charm_value')) is not None))
