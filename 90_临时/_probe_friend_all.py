# -*- coding: utf-8 -*-
"""全表扫描：谁有 friendliness / 哪些字段名与好感度相关。"""
import sys, pathlib, collections, struct, re
PROJ = pathlib.Path('E:/la拆包项目')
sys.path.insert(0, str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
CD = PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
KEYS = ('friend','affinity','favor','intimacy','like_','love','heart','relation','companion','affect','bond','charm')
files=[p for p in CD.glob('*.py') if not p.name.endswith('_chs.py')]
print('表文件数', len(files))
hits=collections.defaultdict(set)   # 字段名 -> 表名集合
has_fl=[]
n_ok=0
for i,p in enumerate(files):
    try:
        raw=p.read_bytes(); at=raw.find(b'x{')
        if at<0: continue
        L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
        cnt=struct.unpack_from('<I',body,0)[0]
        pool=BT.parse_legacy_chs_pool((CD/f'{p.stem}_chs.py').read_bytes())
        rows=BT.decode_table_rows(body,pool,resolve_jumps=False,lenient=True)[0]
    except Exception:
        continue
    n_ok+=1
    fields=set()
    for r in rows:
        fields|=set(r['values'].keys())
    for f in fields:
        fl=f.lower()
        if 'friend' in fl or 'affinity' in fl or 'favor' in fl or 'intimacy' in fl or 'relation' in fl or 'bond' in fl or 'affect' in fl:
            hits[f].add(p.stem)
    if 'friendliness' in fields:
        has_fl.append(p.stem)
print('成功解表', n_ok)
print('\n含 friendliness 字段的表:', has_fl)
print('\n相关字段名 → 所在表:')
for f, tabs in sorted(hits.items()):
    print(f'  {f:34s} {len(tabs):3d} 表  例: {sorted(tabs)[:6]}')
