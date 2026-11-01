# -*- coding: utf-8 -*-
import sys, struct, pathlib, collections
PROJ = pathlib.Path('E:/la拆包项目')
sys.path.insert(0, str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
CD = PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
def load(n):
    raw=(CD/f'{n}.py').read_bytes(); at=raw.find(b'x{')
    L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
    return BT.decode_table_rows(body,BT.parse_legacy_chs_pool((CD/f'{n}_chs.py').read_bytes()),resolve_jumps=False,lenient=True)[0]
F=load('fashion_data'); A=load('player_appear_data')
v=lambda x: x[1] if isinstance(x,tuple) else x
hits=[r for r in F if '白月魁' in str(v(r['values'].get('name')) or '')]
print('白月魁 fashion_data 行数', len(hits))
for r in hits:
    d=r['values']
    print('==', r['key'], v(d.get('name')), '| part', v(d.get('part_type')))
    print('   fields:', {k:(v(x) if not isinstance(v(x),(list,dict)) else str(v(x))[:80]) for k,x in d.items() if k in
        ('reborn_vis','replace_flower_path','replace_flower_id','show_no_have','fashion_preview','takeoff_head',
         'hide_part','hide_other_part','not_show_rebirth_makeup','uncap_appear_gender','force_gender',
         'appear_ids','model_id','brand_id','is_2025','sort_key','socket_model_use_high_model')})
