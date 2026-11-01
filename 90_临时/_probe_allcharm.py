# -*- coding: utf-8 -*-
"""全库扫：任何含 charm/魅力 相关字段的表（不限字段名 charm_value）"""
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
KW=('charm','meili','魅力')
hits=collections.defaultdict(set)
for p in CD.glob('*.py'):
    if p.name.endswith('_chs.py'): continue
    try: r=load(p.stem)
    except Exception: continue
    if not r: continue
    fs=set()
    for x in r: fs |= set(x['values'].keys())
    m=[f for f in fs if any(k in f.lower() for k in KW)]
    if m: hits[p.stem]=set(m)
for t,fs in sorted(hits.items()):
    print(f'  {t:44s} {sorted(fs)}')
