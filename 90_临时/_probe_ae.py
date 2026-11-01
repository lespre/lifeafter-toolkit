# -*- coding: utf-8 -*-
"""解 all_equips_data 完整载荷（03_执行/pe_all_equips_基线分片/）"""
import pathlib, struct, collections, sys
PROJ=pathlib.Path('E:/la拆包项目')
sys.path.insert(0,str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
D=PROJ/'03_执行/pe_all_equips_基线分片'
for f in sorted(D.glob('*.py')):
    raw=f.read_bytes()
    at=raw.find(b'x{')
    print(f'{f.name}: {len(raw)} 字节 | x@ {at}')
    if at<0:
        print('   head:', raw[:32].hex()); continue
    L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
    cnt=struct.unpack_from('<I',body,0)[0]; blob=body[8+4*cnt:]
    pool=BT.parse_legacy_chs_pool((D/'all_equips_data_chs__fid94AB.py').read_bytes())
    rows=BT.decode_table_rows(body,pool,resolve_jumps=False,lenient=True)[0]
    print('   行', len(rows))
    fs=collections.Counter()
    for r in rows:
        for k,x in r['values'].items(): fs[k]+=1
    print('   字段并集:', sorted(fs))
    print('   ★ charm 字段:', [k for k in fs if 'charm' in k.lower()])
    for r in rows[:3]:
        print('   ', r['key'], {k:str(r['values'][k])[:44] for k in list(r['values'])[:10]})
