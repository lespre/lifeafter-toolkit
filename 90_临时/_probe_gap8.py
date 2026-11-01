# -*- coding: utf-8 -*-
import sys, pathlib, struct, collections
PROJ=pathlib.Path('E:/la拆包项目')
sys.path.insert(0,str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
CD=PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
raw=(CD/'all_equips_data.py').read_bytes()
at=raw.find(b'x{')
print('x{ at', at, '| file size', len(raw))
if at<0:
    print('head:', raw[:80])
else:
    L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
    cnt=struct.unpack_from('<I',body,0)[0]; blob=body[8+4*cnt:]
    pool=BT.parse_legacy_chs_pool((CD/'all_equips_data_chs.py').read_bytes())
    rows=BT.decode_table_rows(body,pool,resolve_jumps=False,lenient=True)[0]
    print('rows', len(rows))
    fs=collections.Counter()
    for r in rows:
        for f in r['values']: fs[f]+=1
    print('字段并集:', sorted(fs))
    # 戒指
    v=lambda x: x[1] if isinstance(x,tuple) else x
    ring=[r for r in rows if '戒' in str(v(r['values'].get('name')) or '') or 'ring' in str(v(r['values'].get('name')) or '').lower()]
    print('名字含戒/ring:', len(ring))
    for r in ring[:4]:
        print('  ', r['key'], {k:str(v(x))[:44] for k,x in r['values'].items() if k in ('name','charm_value','model_name','model_id','icon','icons','desc','level','type','part')})
