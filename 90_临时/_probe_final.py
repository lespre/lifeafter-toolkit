# -*- coding: utf-8 -*-
"""决定性：挂饰的 charm 在 fashion_data？
fashion_data 的 light 903 行 = 荧光棒（游戏里的「手持」外观）
fashion_data 里有没有挂饰？看 brand_id / model_id 是否能对上 pendant 行"""
import sys, pathlib, struct, collections
PROJ=pathlib.Path('E:/la拆包项目')
sys.path.insert(0,str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
CD=PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
def load(n):
    raw=(CD/f'{n}.py').read_bytes(); at=raw.find(b'x{')
    L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
    pool=BT.parse_legacy_chs_pool((CD/f'{n}_chs.py').read_bytes())
    return BT.decode_table_rows(body,pool,resolve_jumps=False,lenient=True)[0]
v=lambda x: x[1] if isinstance(x,tuple) else x
F=load('fashion_data'); A=load('player_appear_data')
M=load('player_module_appear_data')
# 挂饰名集合
pend_names={str(v(r['values'].get('name'))) for r in A if v(r['values'].get('part_type'))=='pendant'}
f_names={str(v(r['values'].get('name'))) for r in F}
print('=== 挂饰(pendant) 名 ∩ fashion_data 名 ===')
inter=pend_names & f_names
print('  交集', len(inter), list(inter)[:8])
print()
print('=== 挂饰名 ∩ module 表名 ===')
m_names={str(v(r['values'].get('name'))) for r in M}
print('  交集', len(pend_names & m_names))
print()
print('=== ★ fashion_data light 903 行的 charm 全空吗？再逐行核 ===')
lt=[r for r in F if v(r['values'].get('part_type'))=='light']
withch=[r for r in lt if v(r['values'].get('charm_value')) is not None]
print('  light 行', len(lt), '| 有 charm', len(withch))
print()
print('=== ★★ 换个角度：module 表 part=20001（390 行，全有 charm，值 10/50/100/200）
这批在游戏里是「挂饰」吗？看它们的 model_paths 指向哪 ===')
m20001=[r for r in M if str(v(r['values'].get('part')))=='20001']
import toolkit_core.bindict_table as BT2
cnt=struct.unpack_from('<I',body,0)[0] if False else None
for r in m20001[:3]:
    d=r['values']
    print('  ', r['key'], v(d.get('name')), '| model_paths', str(v(d.get('model_paths')))[:80])
    print('       charm', v(d.get('charm_value')), '| desc', str(v(d.get('desc')))[:70])
