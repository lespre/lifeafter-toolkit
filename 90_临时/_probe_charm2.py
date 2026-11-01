# -*- coding: utf-8 -*-
"""挂饰 charm：① 全库字段名含 charm 的表 ② follow_charm_conf_data 全表 ③ item 表能否对上挂饰"""
import sys, pathlib, struct, collections
PROJ=pathlib.Path('E:/la拆包项目')
sys.path.insert(0,str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
CD=PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
def load(n):
    raw=(CD/f'{n}.py').read_bytes(); at=raw.find(b'x{')
    if at<0: return None
    L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
    pool=BT.parse_legacy_chs_pool((CD/f'{n}_chs.py').read_bytes())
    return BT.decode_table_rows(body,pool,resolve_jumps=False,lenient=True)[0]
v=lambda x: x[1] if isinstance(x,tuple) else x

print('=== ① 全库：字段名含 charm 的表 ===')
hits=collections.defaultdict(set)
for p in CD.glob('*.py'):
    if p.name.endswith('_chs.py'): continue
    try: r=load(p.stem)
    except Exception: continue
    if not r: continue
    fs=set()
    for x in r:
        fs |= set(x['values'].keys())
    ch=[f for f in fs if 'charm' in f.lower()]
    if ch: hits[p.stem]=set(ch)
for t,fs in sorted(hits.items()):
    print(f'  {t:46s} {sorted(fs)}')
print()
print('=== ② follow_charm_conf_data 全表（53 有 charm）===')
r=load('follow_charm_conf_data')
if r:
    for x in r[:8]:
        print('   ', x['key'], {k:str(v(val))[:60] for k,val in x['values'].items()})
    print('  ...共', len(r), '行')
