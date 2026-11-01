# -*- coding: utf-8 -*-
"""具体挂饰全字段 dump + 全库同名行"""
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
A=load('player_appear_data')
print('=== pendant 行 5003902（雪国之徽）完整字段 ===')
r=[x for x in A if x['key']==5003902][0]
for f,val in sorted(r['values'].items()):
    print(f'   {f:30s} {str(val)[:90]}')
print()
print('=== 挂饰名在全库同名行 ===')
NAMES={'雪国之徽','心易俱乐部挂饰','驰光纪念','一串小饼干'}
for p in sorted(CD.glob('*.py')):
    if p.name.endswith('_chs.py'): continue
    try: rr=load(p.stem)
    except Exception: continue
    if not rr: continue
    hits=[x for x in rr if any(n in str(v(x['values'].get('name')) or '') for n in NAMES)]
    if hits:
        print(f'  {p.stem}: {len(hits)} 行')
        for x in hits[:4]:
            d=x['values']
            print('     ', x['key'], v(d.get('name')), '| charm', v(d.get('charm_value')), '| part', v(d.get('part')), '| type', v(d.get('part_type')), '| level', v(d.get('level')))
