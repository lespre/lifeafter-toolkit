# -*- coding: utf-8 -*-
"""挂饰/投影/戒指 的 model 与 charm 缺口：源头能不能拿到？"""
import sys, pathlib, struct, collections, json
PROJ=pathlib.Path('E:/la拆包项目')
sys.path.insert(0,str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
CD=PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
def load(n):
    raw=(CD/f'{n}.py').read_bytes(); at=raw.find(b'x{')
    if at<0: return None,None,None
    L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
    cnt=struct.unpack_from('<I',body,0)[0]; blob=body[8+4*cnt:]
    pool=BT.parse_legacy_chs_pool((CD/f'{n}_chs.py').read_bytes())
    return BT.decode_table_rows(body,pool,resolve_jumps=False,lenient=True)[0], blob, pool
v=lambda x: x[1] if isinstance(x,tuple) else x

print('=== ① 挂饰：player_module_appear_data 里有没有 model ===')
M,mb,mp=load('player_module_appear_data')
mm={r['key']:r for r in M}
fs=collections.Counter()
for r in M:
    for f in r['values']: fs[f]+=1
print('  字段并集:', sorted(fs))
for f in ('model_name','high_model_name','socket_models','charm_value','part','part_type','icons','female_icon'):
    print(f'   {f:18s} 非空 {fs.get(f,0)}')
print('  样例行:')
for r in M[:3]:
    print('   ', r['key'], {k:str(v(x))[:48] for k,x in r['values'].items()})

print()
print('=== ② 戒指：all_equips 里有没有 ===')
AE,ab,ap=load('all_equips')
if AE:
    efs=collections.Counter()
    for r in AE:
        for f in r['values']: efs[f]+=1
    print('  all_equips 行', len(AE), '| 字段数', len(efs))
    for f in ('name','charm_value','model_name','model_id','icons','icon','part','type','desc','level'):
        if efs.get(f): print(f'   {f:16s} 非空 {efs[f]}')
    # 戒指行
    ring=[r for r in AE if '戒' in str(v(r['values'].get('name')) or '') or 'ring' in str(v(r['values'].get('name')) or '').lower()]
    print('  名字含「戒」的行:', len(ring))
    for r in ring[:5]:
        print('   ', r['key'], {k:str(v(x))[:40] for k,x in r['values'].items() if k in ('name','charm_value','model_name','model_id','icon','icons','desc','level','type')})
