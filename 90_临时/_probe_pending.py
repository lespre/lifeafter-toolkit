# -*- coding: utf-8 -*-
import sys, pathlib, collections, struct, json
PROJ = pathlib.Path('E:/la拆包项目')
sys.path.insert(0, str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
sys.path.insert(0, str(PROJ/'02_wiki/web/tools'))
from toolkit_core import bindict_table as BT
CD = PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
def load(n):
    raw=(CD/f'{n}.py').read_bytes(); at=raw.find(b'x{')
    L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
    cnt=struct.unpack_from('<I',body,0)[0]; blob=body[8+4*cnt:]
    pool=BT.parse_legacy_chs_pool((CD/f'{n}_chs.py').read_bytes())
    return BT.decode_table_rows(body,pool,resolve_jumps=False,lenient=True)[0], blob, pool
def mk(blob,pool):
    def ev(g,out):
        k,els=g
        for e in els:
            if k==0x0b:
                g2=BT.read_27_group(blob,e)
                if g2: ev(g2,out)
            elif k==0x05: out.append(pool[e] if e<len(pool) else None)
            else: out.append(e)
    def one(r,f):
        got=r['values'].get(f)
        if not got: return None
        tag,v=got
        if tag!='0x0b': return v
        try:
            off=int(str(v).split(':')[1]); out=[]
            g=BT.read_27_group(blob,off)
            if g: ev(g,out)
            return out
        except Exception: return None
    return one
F,fb,fp=load('fashion_data'); fo=mk(fb,fp)
v=lambda x: x[1] if isinstance(x,tuple) else x
def vals(r,f):
    x=fo(r,f); return x if isinstance(x,list) else ([] if x in (None,'') else [x])
nm=lambda r: str(fo(r,'name') or '')

print('=== 1. friendliness（1,043 卡 / 1,355 行）===')
fr=[r for r in F if vals(r,'friendliness')]
print('  值分布', collections.Counter(str(vals(r,'friendliness')[0]) for r in fr).most_common())
print('  与 charm_value 同现:')
both=[r for r in fr if v(r['values'].get('charm_value'))]
print('   有 friendliness 的行里，有 charm_value 的', len(both), '/', len(fr))
cv=collections.Counter(v(r['values'].get('charm_value')) for r in both)
print('   其中 charm_value 分布', cv.most_common(6))
print('  样例（按值）:')
seen=set()
for r in fr:
    val=str(vals(r,'friendliness')[0])
    if val in seen: continue
    seen.add(val)
    print(f"    {nm(r):22s} part={str(fo(r,'part_type')):6s} friendliness={val} charm={v(r['values'].get('charm_value'))} level={v(r['values'].get('level'))} 典藏={'典藏' in nm(r)}")
    if len(seen)>=6: break
print('  典藏占比: 有 friendliness 的行中典藏名', sum(1 for r in fr if '典藏' in nm(r)), '/', len(fr),
      '| 全表典藏名行', sum(1 for r in F if '典藏' in nm(r)))

print('\n=== 2. uncap_appear_gender（17 卡 / 133 行）===')
for val in ('1','2','3'):
    rs=[r for r in F if str(vals(r,'uncap_appear_gender')[0] if vals(r,'uncap_appear_gender') else '')==val]
    if not rs: continue
    print(f'  值 {val}: {len(rs)} 行')
    for r in rs[:3]:
        print(f"    {nm(r):24s} part={str(fo(r,'part_type')):6s} force_gender={v(r['values'].get('force_gender'))} "
              f"appear={vals(r,'appear_ids')} reborn={bool(r['values'].get('reborn_vis'))} charm={v(r['values'].get('charm_value'))}")

print('\n=== 3. rebirth_tex（58 卡 / 427 行）===')
rt=[r for r in F if r['values'].get('rebirth_tex')]
print('  值分布', collections.Counter(str(v(r['values'].get('rebirth_tex'))) for r in rt).most_common(3))
print('  与 reborn_vis(藏花) 同现:', sum(1 for r in rt if r['values'].get('reborn_vis')), '/', len(rt))
print('  部位', collections.Counter(fo(r,'part_type') for r in rt).most_common())
for r in rt[:4]:
    print(f"    {nm(r):24s} part={str(fo(r,'part_type')):6s} 藏花={bool(r['values'].get('reborn_vis'))} charm={v(r['values'].get('charm_value'))}")

print('\n=== 4. value_word_ids（85 卡 / 412 行）===')
vw=[r for r in F if vals(r,'value_word_ids')]
for r in vw[:5]:
    print(f"    {nm(r):24s} value_word_ids={vals(r,'value_word_ids')} charm={v(r['values'].get('charm_value'))} desc={str(v(r['values'].get('desc')) or '')[:30]}")
print('  值分布', collections.Counter(str(vals(r,'value_word_ids')) for r in vw).most_common(6))

print('\n=== 5. preview_id（72 卡 / 621 行）===')
pv=[r for r in F if vals(r,'preview_id')]
print('  值分布', collections.Counter(str(vals(r,'preview_id')[0]) for r in pv).most_common(8))
for r in pv[:4]:
    print(f"    {nm(r):24s} preview_id={vals(r,'preview_id')} theme_codes={vals(r,'theme_codes')}")

print('\n=== 6. is_new_bone / new_bone_soft_bone_id / green_model_path_female ===')
nb=[r for r in F if r['values'].get('is_new_bone')]
print('  is_new_bone 行', len(nb))
for r in nb[:4]:
    print(f"    {nm(r):24s} part={str(fo(r,'part_type')):6s} soft_bone={vals(r,'new_bone_soft_bone_id')} model={vals(r,'model_id')}")
gp=[r for r in F if vals(r,'green_model_path_female')]
print('  green_model_path_female 行', len(gp))
for r in gp[:3]:
    print(f"    {nm(r):24s} part={str(fo(r,'part_type')):6s} path={vals(r,'green_model_path_female')}")

print('\n=== 7. other_get_methods（2 卡）===')
for r in F:
    if vals(r,'other_get_methods'):
        print(f"    {nm(r):12s} key={r['key']} other_get_methods={vals(r,'other_get_methods')} part={fo(r,'part_type')} charm={v(r['values'].get('charm_value'))}")
