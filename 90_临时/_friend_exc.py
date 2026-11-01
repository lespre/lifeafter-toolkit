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
DEF={'hat':680,'cloth':1280,'bag':1960,'light':1960,'suit':None}
print('=== 例外行（与部位默认值不符）===')
exc=collections.defaultdict(list)
for r in F:
    fv=v(r['values'].get('friendliness'))
    if fv is None: continue
    pt=str(v(r['values'].get('part_type')) or '未标')
    d=DEF.get(pt)
    if d is None or int(fv)!=d:
        exc[(pt,int(fv))].append((str(v(r['values'].get('name'))), v(r['values'].get('charm_value')), str(v(r['values'].get('level'))), v(r['values'].get('part'))))
for k in sorted(exc, key=lambda x:(x[0],-x[1])):
    lst=exc[k]
    print(f'  part={k[0]:5s} fl={k[1]:5d}  {len(lst):4d} 行   例: {lst[0][0]}（charm {lst[0][1]}, level {lst[0][2]}, part码 {lst[0][3]}）')
print('\n=== 整套 suit 的取值分布 ===')
sc=collections.Counter()
for r in F:
    pt=str(v(r['values'].get('part_type')) or '')
    if pt=='suit':
        sc[int(v(r['values'].get('friendliness')) or 0)]+=1
print(' ', sc.most_common())
print('\n=== 头饰 680 / 衣服 1280 / 背包 1960 的组合检验 ===')
print('  头饰680 + 衣服1280 =', 680+1280, ' → 达「相伴」(1500)?', 680+1280>=1500)
print('  +背包1960 =', 680+1280+1960, ' → 达「同行」(3000)?', 680+1280+1960>=3000)
print('  只穿头饰 680 → 达「相知」(700)?', 680>=700)
