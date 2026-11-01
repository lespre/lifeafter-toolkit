# -*- coding: utf-8 -*-
import sys, pathlib, struct, collections
PROJ = pathlib.Path('E:/la拆包项目')
sys.path.insert(0, str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
CD = PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
raw=(CD/'fashion_data.py').read_bytes(); at=raw.find(b'x{')
L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
cnt=struct.unpack_from('<I',body,0)[0]; blob=body[8+4*cnt:]
pool=BT.parse_legacy_chs_pool((CD/'fashion_data_chs.py').read_bytes())
F=BT.decode_table_rows(body,pool,resolve_jumps=False,lenient=True)[0]
v=lambda x: x[1] if isinstance(x,tuple) else x
rows=[]
for r in F:
    fv=v(r['values'].get('friendliness')); cv=v(r['values'].get('charm_value'))
    if fv is None or cv is None: continue
    rows.append((str(v(r['values'].get('part_type')) or '未标'), int(cv), int(fv), str(v(r['values'].get('name')))))
print('同时有 charm 与 friendliness 的行:', len(rows))
print('\n=== 按部位看 charm → friendliness 的映射 ===')
for pt in ('cloth','hat','suit','bag','light','未标'):
    m=collections.defaultdict(collections.Counter)
    for p,c,f,n in rows:
        if p==pt: m[c][f]+=1
    if not m: continue
    print(f'\n-- part_type={pt} --')
    for c in sorted(m):
        fs=m[c]
        s=' '.join(f'{k}×{v}' for k,v in fs.most_common())
        print(f'   charm {c:5d} → {s}')
print('\n=== 检验 friendliness == charm*10 - 20 / charm*10 ===')
cnt=collections.Counter()
for p,c,f,n in rows:
    if f==c*10: cnt[(p,'=charm*10')]+=1
    elif f==c*10-20: cnt[(p,'=charm*10-20')]+=1
    else: cnt[(p,'其它')]+=1
for p in ('cloth','hat','suit','bag','light','未标'):
    a=cnt.get((p,'=charm*10'),0); b=cnt.get((p,'=charm*10-20'),0); o=cnt.get((p,'其它'),0)
    if a+b+o: print(f'   {p:5s} =charm*10:{a:5d}  =charm*10-20:{b:5d}  其它:{o:5d}')
print('\n=== “其它”样本 ===')
n=0
for p,c,f,nm in rows:
    if not (f==c*10 or f==c*10-20):
        print(f'   {nm:26s} part={p:5s} charm={c:5d} friendliness={f}')
        n+=1
        if n>=15: break
