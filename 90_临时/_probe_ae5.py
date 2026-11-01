# -*- coding: utf-8 -*-
"""确认 all_equips 的 charm 与挂饰行的一致性 + 覆盖率 + 板上能补多少卡"""
import pathlib, struct, collections, sys, json
PROJ=pathlib.Path('E:/la拆包项目')
sys.path.insert(0,str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
v=lambda x: x[1] if isinstance(x,tuple) else x
def load_legacy(cd,n):
    raw=(cd/f'{n}.py').read_bytes(); at=raw.find(b'x{')
    L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
    c2=struct.unpack_from('<I',body,0)[0]; blob=body[8+4*c2:]
    p=BT.parse_legacy_chs_pool((cd/f'{n}_chs.py').read_bytes())
    return BT.decode_table_rows(body,p,resolve_jumps=False,lenient=True)[0]
def load_dir(d,name,poolname):
    raw=(d/name).read_bytes(); at=raw.find(b'x{')
    L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
    c2=struct.unpack_from('<I',body,0)[0]; blob=body[8+4*c2:]
    p=BT.parse_legacy_chs_pool((d/poolname).read_bytes())
    return BT.decode_table_rows(body,p,resolve_jumps=False,lenient=True)[0]
D=PROJ/'03_执行/pe_all_equips_基线分片'
AE=load_dir(D,'all_equips_data__fid1F8E.py','all_equips_data_chs__fid94AB.py')
CD=PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
PA=load_legacy(CD,'player_appear_data')
b=json.loads(pathlib.Path('02_wiki/web/data/boards/fashion_wardrobe.json').read_text(encoding='utf-8'))
def pb(it): return (it.get('part_bucket') or ['?'])[0]
# 装备表：equip_type=0 → 挂饰/时装挂件
aen=collections.defaultdict(list)
for r in AE:
    if str(v(r['values'].get('equip_type')))=='0':
        aen[str(v(r['values'].get('name')) or '')].append(r)
# 板上挂饰卡
pin=[it for it in b['items'] if pb(it)=='挂饰']
print('=== 板上 147 张挂饰卡 能补多少 charm ===')
n=0; withc=0; nog=0
for it in pin:
    nm=str(it.get('name') or '')
    rs=aen.get(nm)
    if not rs: nog+=1; continue
    n+=1
    cvs={v(r['values'].get('charm_value')) for r in rs}
    if None not in cvs: withc+=1
print(f'  挂饰卡 {len(pin)} | 装备表同名命中 {n} | 其中有charm {withc} | 未同名 {nog}')
print()
print('=== ★ 顺带：装备表 equip_type=0 里的 charm 覆盖 ===')
p0=[r for r in AE if str(v(r['values'].get('equip_type')))=='0']
print('  equip_type=0 行', len(p0), '| 有 charm', sum(1 for r in p0 if v(r['values'].get('charm_value')) is not None))
print('  charm 分布:', collections.Counter(v(r['values'].get('charm_value')) for r in p0).most_common(10))
print()
print('=== 其他部位（戒指 part=6 / 花苞 part=7）在装备表里能对上吗 ===')
for ptn, cn in (('6','戒指'),('7','花苞')):
    rows=[r for r in PA if str(v(r['values'].get('part')))==ptn]
    nm2={str(v(r['values'].get('name'))) for r in rows}
    hit=nm2 & set(aen)
    print(f'  appear part={ptn} ({cn}) 唯一名 {len(nm2)} | 装备表同名 {len(hit)}')
    for nm in list(hit)[:4]:
        r=aen[nm][0]
        print(f'    {nm:16s} charm {v(r["values"].get("charm_value"))} equip {r["key"]}')
