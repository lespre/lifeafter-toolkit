# -*- coding: utf-8 -*-
import sys, pathlib, collections, struct
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
    return rows, blob, pool
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

print('=== uncap_appear_gender × takeoff_head × part ===')
u=[r for r in F if vals(r,'uncap_appear_gender')]
c=collections.Counter((str(vals(r,'uncap_appear_gender')[0]), str(fo(r,'part_type')), bool(r['values'].get('takeoff_head'))) for r in u)
for k,n in sorted(c.items()): print('  值/部位/可脱帽', k, n)
print('\n  脱帽相关字段存在情况（全表）:')
for f in ('takeoff_head','can_take_off','take_off','not_show_rebirth_makeup','uncap_appear_gender'):
    print('   ', f, sum(1 for r in F if r['values'].get(f)))
print('\n  净罪颂祷系列对照:')
for r in F:
    if '净罪颂祷' in nm(r) and not vals(r,'uncap_appear_gender') is None:
        pass
for r in F:
    n=nm(r)
    if n.startswith('净罪颂祷') and '-' not in n.replace('净罪颂祷',''):
        print(f"    {n:22s} part={str(fo(r,'part_type')):6s} uncap={vals(r,'uncap_appear_gender')} takeoff={bool(r['values'].get('takeoff_head'))} appear={vals(r,'appear_ids')} charm={v(r['values'].get('charm_value'))}")
print('\n  含「脱帽」字样的时装名:')
print('   ', [nm(r) for r in F if '脱帽' in nm(r)][:20])

print('\n=== friendliness 更多例子 ===')
fr=[r for r in F if vals(r,'friendliness')]
byv=collections.defaultdict(list)
for r in fr: byv[str(vals(r,'friendliness')[0])].append(r)
for val in sorted(byv, key=lambda x:-len(byv[x]))[:8]:
    rs=byv[val]
    parts=collections.Counter(str(fo(r,'part_type')) for r in rs)
    lvs=collections.Counter(v(r['values'].get('level')) for r in rs)
    print(f"  值 {val:>5s} ({len(rs):4d} 行) 部位{dict(parts)} 等级{dict(lvs)}")
    for r in rs[:3]:
        print(f"      {nm(r):24s} part={str(fo(r,'part_type')):6s} charm={v(r['values'].get('charm_value'))} level={v(r['values'].get('level'))} 典藏={'典藏' in nm(r)} desc={str(v(r['values'].get('desc')) or '')[:26]}")
