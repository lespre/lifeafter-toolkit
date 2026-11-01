# -*- coding: utf-8 -*-
"""列出所有带 friendliness（同居好感度）的时装。"""
import sys, pathlib, struct, collections, json, re
PROJ = pathlib.Path('E:/la拆包项目')
sys.path.insert(0, str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
CD = PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
def load(n):
    raw=(CD/f'{n}.py').read_bytes(); at=raw.find(b'x{')
    L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
    pool=BT.parse_legacy_chs_pool((CD/f'{n}_chs.py').read_bytes())
    return BT.decode_table_rows(body,pool,resolve_jumps=False,lenient=True)[0]
v=lambda x: x[1] if isinstance(x,tuple) else x
F=load('fashion_data')
CH=load('cohabit_level_data')
levels=[(int(v(r['values'].get('friendliness'))), str(v(r['values'].get('desc')))) for r in CH]
levels.sort()
def tier(x):
    cur='—'; nxt=None
    for need,name in levels:
        if x>=need: cur=name
        elif nxt is None: nxt=(need,name)
    return cur, nxt
def base(s): return re.sub(r'-\d+天$','',str(s or ''))
rows=[]
for r in F:
    fv=v(r['values'].get('friendliness'))
    if fv is None: continue
    rows.append({'key':r['key'],'name':str(v(r['values'].get('name')) or ''),
                 'base':base(v(r['values'].get('name'))),
                 'part':str(v(r['values'].get('part_type')) or ''),
                 'pcode':v(r['values'].get('part')),
                 'fl':int(fv),'charm':v(r['values'].get('charm_value')),
                 'level':v(r['values'].get('level')),'show':str(v(r['values'].get('show_name')) or '')})
print('行级有 friendliness 的行:', len(rows))
styles=collections.defaultdict(list)
for r in rows: styles[r['base']].append(r)
print('去重款式数:', len(styles))
print('其中有永久行的款式:', sum(1 for b,rs in styles.items() if any('-天' not in x['name'] for x in rs)))
print('\n按部位（款式级，取该款任一行）:')
pc=collections.Counter()
for b,rs in styles.items(): pc[rs[0]['part'] or '未标']+=1
print(' ', pc.most_common())
print('\n按数值档位（行级）:')
tc=collections.Counter()
for r in rows: tc[(r['fl'], tier(r['fl'])[0])]+=1
for (x,t),n in sorted(tc.items()): print(f'   {x:5d}  达「{t}」  {n:5d} 行')
# 板级
b=json.loads(pathlib.Path('02_wiki/web/data/boards/fashion_wardrobe.json').read_text(encoding='utf-8'))
own={}
for it in b['items']:
    for k in (it.get('row_keys') or []):
        try: own[int(k)]=it['name']
        except Exception: pass
cards=set()
for r in rows:
    if r['key'] in own: cards.add(own[r['key']])
print('\n落到板上的卡数:', len(cards))
# 清单文件
out=pathlib.Path('90_临时/friendliness_清单.md')
L=['# 带 friendliness（同居好感度）的时装清单','',
   f'口径：`fashion_data.friendliness` = 该时装提供的**同居（伴侣）好感度**点数。',
   f'同居五档：'+ ' / '.join(f'{n} {x}' for x,n in levels)+'（`home_level_data.upgrade_friendliness_limit` 按家园等级封顶）。','',
   f'行级 {len(rows)} 行 → 去重 **{len(styles)} 款** → 板卡 {len(cards)} 张。','',
   '| 款式 | 部位 | 部位码 | 好感度 | 达到档位 | 距下一档 | 魅力值 | 品级 | 时限行数 |',
   '|---|---|---|---|---|---|---|---|---|']
for bk in sorted(styles, key=lambda x: (-max(r['fl'] for r in styles[x]), x)):
    rs=styles[bk]
    mx=max(rs, key=lambda r: r['fl'])
    cur,nxt=tier(mx['fl'])
    gap = (nxt[0]-mx['fl']) if nxt else 0
    ntim=sum(1 for r in rs if '-天' in r['name'])
    L.append(f"| {mx['name'].replace('|','／')} | {mx['part'] or '—'} | {mx['pcode']} | {mx['fl']} | {cur} | {gap if nxt else '—'} | {mx['charm'] if mx['charm'] is not None else '—'} | {mx['level'] if mx['level'] is not None else '—'} | {ntim} |")
out.write_text('\n'.join(L), encoding='utf-8')
print('\n清单已写:', out, len(L)-10, '行')
