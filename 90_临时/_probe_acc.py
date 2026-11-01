# -*- coding: utf-8 -*-
"""yk_accessory_model_line_id：挂饰的 charm 走 accessory 体系？"""
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
W=load('weapon_skin_data')
print('=== weapon_skin_data: yk_accessory_model_line_id × charm_value ===')
g=collections.defaultdict(collections.Counter)
for r in W:
    a=v(r['values'].get('yk_accessory_model_line_id'))
    c=v(r['values'].get('charm_value'))
    g[a][c]+=1
for a in sorted(g, key=lambda x: str(x)):
    print(f'  accessory_line={str(a):6s} → charm {dict(g[a])}')
print()
print('=== weapon_skin_data 有 name 吗 ===')
fs=set()
for r in W: fs|=set(r['values'].keys())
print('  含 name:', 'name' in fs)
print()
# 挂饰表
print('=== 找 accessory 相关表 ===')
for p in sorted(CD.glob('*.py')):
    if p.name.endswith('_chs.py'): continue
    n=p.stem
    if 'accessory' in n or 'yuke' in n or 'yk_' in n:
        r=load(n)
        print(f'  {n:44s} {len(r) if r else 0} 行')
