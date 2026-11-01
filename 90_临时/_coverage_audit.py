# -*- coding: utf-8 -*-
"""人物时装板块：提取表 + 字段覆盖 全量核查。"""
import sys, pathlib, struct, json, collections
PROJ = pathlib.Path('E:/la拆包项目')
sys.path.insert(0, str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
CD = PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
def load(n):
    raw=(CD/f'{n}.py').read_bytes(); at=raw.find(b'x{')
    if at<0: return None
    L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
    pool=BT.parse_legacy_chs_pool((CD/f'{n}_chs.py').read_bytes())
    return BT.decode_table_rows(body,pool,resolve_jumps=False,lenient=True)[0]
v=lambda x: x[1] if isinstance(x,tuple) else x

board_text = pathlib.Path('02_wiki/web/data/boards/fashion_wardrobe.json').read_text(encoding='utf-8')
board = json.loads(board_text)
# 产物里出现过的卡字段名集合
card_keys=set()
def walk(o):
    if isinstance(o,dict):
        for k,x in o.items():
            card_keys.add(k); walk(x)
    elif isinstance(o,list):
        for x in o[:50]: walk(x)
walk(board)

for t in ('fashion_data','player_appear_data','player_module_appear_data'):
    rows=load(t)
    if not rows: print('!!',t); continue
    fs=collections.Counter()
    nonnull=collections.Counter()
    for r in rows:
        for f,x in r['values'].items():
            fs[f]+=1
            if x not in (None,'',[],{}): nonnull[f]+=1
    print(f'\n===== {t}  行 {len(rows)}  字段 {len(fs)} =====')
    covered=[f for f in fs if f in card_keys]
    missing=[(f, nonnull[f]) for f in fs if f not in card_keys]
    print(f'  已落卡字段 {len(covered)} / {len(fs)}')
    print('  未落字段（按非空行数降序，前 25）:')
    for f,n in sorted(missing, key=lambda x:-x[1])[:25]:
        print(f'     {f:34s} 非空 {n:6d}')
    if len(missing)>25: print(f'     …还有 {len(missing)-25} 个')
