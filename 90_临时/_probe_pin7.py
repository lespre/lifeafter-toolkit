# -*- coding: utf-8 -*-
"""挂饰 charm 的真正来源：尝试所有可能的表"""
import sys, pathlib, struct, collections, json
PROJ=pathlib.Path('E:/la拆包项目')
sys.path.insert(0,str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
from toolkit_core import cdata_nxs
CD=PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
def load(n):
    raw=(CD/f'{n}.py').read_bytes(); at=raw.find(b'x{')
    if at<0: return None
    L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
    pool=BT.parse_legacy_chs_pool((CD/f'{n}_chs.py').read_bytes())
    return BT.decode_table_rows(body,pool,resolve_jumps=False,lenient=True)[0]
v=lambda x: x[1] if isinstance(x,tuple) else x

# ① fashion_charm_desc_data（新格式？用 cdata_nxs）
print('=== ① fashion_charm_desc_data ===')
for cand in ('fashion_charm_desc_data',):
    for ext in ('.nxs','.py'):
        p=CD/f'{cand}{ext}'
        if not p.exists(): continue
        try:
            t=cdata_nxs.load_table(cand, CD)
            print(f'  {ext} kind={t.kind} rows={len(t.rows)}')
            for r in t.rows[:6]:
                print('   ', r['key'], {k:str(v)[:48] for k,v in list(r['fields'].items())[:6]})
        except Exception as e:
            print(f'  {ext} fail: {type(e).__name__} {str(e)[:80]}')

# ② 挂饰 item_id 5xxxxxx / 15xxxxx 能在别的表找到吗
print()
print('=== ② 挂饰行键（5002405 等）在哪些表的主键里出现过 ===')
A=load('player_appear_data')
pend=[r for r in A if str(v(r['values'].get('part')))=='5' and str(v(r['values'].get('part_type')))=='pendant']
keys={r['key'] for r in pend}
print('  pendant 行键样例:', sorted(keys)[:8], f'(共 {len(keys)} 个)')
cands=['appear_id_2_equip_id','all_equips_data','player_appear_v2_bag_data','fashion_data','weapon_skin_data','super_fashion_change_color_data']
for t in cands:
    r=load(t)
    if not r:
        print(f'  {t:34s} legacy 解不出'); continue
    ks={x['key'] for x in r}
    print(f'  {t:34s} 行{len(r):6d} | 命中 pendant key {len(keys & ks)}')
