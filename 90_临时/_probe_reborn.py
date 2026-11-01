# -*- coding: utf-8 -*-
import sys, struct, pathlib, collections
PROJ = pathlib.Path('E:/la拆包项目')
sys.path.insert(0, str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
CD = PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
def load(n):
    raw=(CD/f'{n}.py').read_bytes(); at=raw.find(b'x{')
    L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
    cnt=struct.unpack_from('<I',body,0)[0]; blob=body[8+4*cnt:]
    pool=BT.parse_legacy_chs_pool((CD/f'{n}_chs.py').read_bytes())
    rows=BT.decode_table_rows(body,pool,resolve_jumps=False,lenient=True)[0]
    return rows

for t in ('fashion_data','player_appear_data'):
    rows=load(t)
    print('====',t,len(rows))
    have=miss=0; raw_vals=collections.Counter()
    for r in rows:
        got=r['values'].get('reborn_vis')
        if got is None: miss+=1; continue
        have+=1; raw_vals[repr(got)]+=1
    print(' 有键',have,'无键',miss)
    print(' 原始值分布',raw_vals.most_common(8))
    # 同样看几个参照字段的原始值，判断解码是否保留 0
    for f in ('hide_in_bag','show_no_have','fashion_preview','not_show_rebirth_makeup','takeoff_head'):
        c=collections.Counter()
        for r in rows:
            got=r['values'].get(f)
            c[repr(got)]+=1
        print(f'  {f:24s}',c.most_common(5))
