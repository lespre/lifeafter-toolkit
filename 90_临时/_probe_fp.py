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

print('=== player_fashion_preview_data 全表（找 id / group_id / tag_name）===')
try:
    PR,pb,pp=load('player_fashion_preview_data'); po=mk(pb,pp)
    ids=[]; grp=[]; rows=[]
    for r in PR:
        f=r['values']
        gid=v(f.get('id')); gg=v(f.get('group_id'))
        tag=v(f.get('tag_name')); anim=v(f.get('preview_idle_anim'))
        if gid is not None: ids.append(int(gid))
        if gg is not None: grp.append(int(gg))
        rows.append((r['key'], gid, gg, tag, anim))
    print('  行', len(PR), '| id 字段范围', min(ids), '~', max(ids), '共', len(set(ids)))
    print('  group_id 范围', min(grp), '~', max(grp), '共', len(set(grp)))
    print('  tag_name 分布', collections.Counter(x[3] for x in rows).most_common(8))
    for x in rows[:10]: print('   ', x)
    # fashion preview_id 命中 id 字段？
    fpid=sorted({int(vals(r,'preview_id')[0]) for r in F if vals(r,'preview_id')})
    print('\n  fashion_data.preview_id 取值', fpid)
    idset=set(ids); grpset=set(grp)
    print('  命中 id 字段', sorted(set(fpid)&idset))
    print('  命中 group_id', sorted(set(fpid)&grpset))
except Exception as e:
    print('  fail', e)

print('\n=== preview_id 按值看款式 ===')
byp=collections.defaultdict(list)
for r in F:
    pv=vals(r,'preview_id')
    if pv: byp[int(pv[0])].append(r)
for k in sorted(byp)[:10]:
    rs=byp[k]
    names=[]
    for r in rs:
        n=nm(r)
        if not any(n.endswith(f'-{d}天') for d in (1,3,5,7,14,30)) and n not in names: names.append(n)
    print(f'  preview_id={k:3d} 行{len(rs):4d} 款: {"、".join(names[:4])}')

print('\n=== friendliness 与 level / charm 的关系 ===')
rows_f=[r for r in F if vals(r,'friendliness')]
pairs=collections.defaultdict(set)
for r in rows_f:
    fv=int(vals(r,'friendliness')[0]); cv=v(r['values'].get('charm_value')); lv=v(r['values'].get('level'))
    pairs[(cv, lv)].add(fv)
for k in sorted(pairs, key=lambda x:(str(x[0]),str(x[1])))[:22]:
    print('   charm/level', k, '→ friendliness', sorted(pairs[k]))
