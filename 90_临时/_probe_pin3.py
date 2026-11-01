# -*- coding: utf-8 -*-
"""挂饰的真实身份 + 全库找 charm 来源表"""
import sys, pathlib, struct, collections, json
PROJ=pathlib.Path('E:/la拆包项目')
sys.path.insert(0,str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
CD=PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
def load(n):
    raw=(CD/f'{n}.py').read_bytes(); at=raw.find(b'x{')
    if at<0: return None
    L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
    pool=BT.parse_legacy_chs_pool((CD/f'{n}_chs.py').read_bytes())
    return BT.decode_table_rows(body,pool,resolve_jumps=False,lenient=True)[0]
v=lambda x: x[1] if isinstance(x,tuple) else x
A=load('player_appear_data')
M=load('player_module_appear_data')

print('=== ① player_appear_data part=5 的 768 行名字分布（看是不是武器/荧光棒）===')
a5=[r for r in A if str(v(r['values'].get('part')))=='5']
pt=collections.Counter(str(v(r['values'].get('part_type'))) for r in a5)
print('  part_type 分布:', pt.most_common())
names=[v(r['values'].get('name')) for r in a5]
print('  名字样例:', names[:14])
print('  含「挂饰」:', sum(1 for n in names if '挂饰' in str(n)), '| 含「骑士」:', sum(1 for n in names if '骑士' in str(n)))

print()
print('=== ② module 表 part=1（13 行）到底是什么 ===')
m1=[r for r in M if str(v(r['values'].get('part')))=='1']
for r in m1:
    d=r['values']
    print('  ', r['key'], v(d.get('name')), '| charm', v(d.get('charm_value')), '| icon', v(d.get('icon')), '| desc', str(v(d.get('desc')))[:60])

print()
print('=== ③ module 表 part=2 / 20001 的 desc 关键词 ===')
for pt_ in ('2','20001'):
    rs=[r for r in M if str(v(r['values'].get('part')))==pt_]
    kw=collections.Counter()
    for r in rs:
        d=str(v(r['values'].get('desc')) or '')
        for k in ('面饰','挂饰','头部','眼睛','头顶','脸部'):
            if k in d: kw[k]+=1
    print(f'  part={pt_} ({len(rs)} 行) desc 关键词:', kw.most_common())
