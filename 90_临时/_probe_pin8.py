# -*- coding: utf-8 -*-
"""拿具体挂饰反查：雪国之徽(5003902) / 板上的挂饰卡在全库哪些表出现"""
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

TARGET_KEYS={5003902, 15003902, 5002405, 5012201}
TARGET_NAMES={'雪国之徽','一串小饼干','迷途歌谣'}
print('=== 全库搜：目标行键作为主键出现 / 目标名作为字符串值出现 ===')
found=collections.defaultdict(list)
for p in sorted(CD.glob('*.py')):
    if p.name.endswith('_chs.py'): continue
    try: r=load(p.stem)
    except Exception: continue
    if not r: continue
    for x in r:
        hit=False
        if x['key'] in TARGET_KEYS: hit=True
        if not hit:
            for f,val in x['values'].items():
                s=str(val)
                if any(t in s for t in TARGET_NAMES): hit=True; break
        if hit:
            found[p.stem].append(x['key'])
            break
for t,ks in sorted(found.items()):
    print(f'  {t:44s} 命中 {len(ks)} 行  例 {ks[:3]}')
