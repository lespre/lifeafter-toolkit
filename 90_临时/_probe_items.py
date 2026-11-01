# -*- coding: utf-8 -*-
import sys, struct, pathlib, collections, re
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
            elif k==0x05: out.append(pool[e] if e<len(pool) else f'<oob{e}>')
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
        except Exception as e: return f'<err {e}>'
    return one
F,fb,fp=load('fashion_data')
fo=mk(fb,fp)
rows=F
def vals(r,f):
    x=fo(r,f)
    return x if isinstance(x,list) else ([] if x in (None,'') else [x])

print('### #1/#2 染色')
cc=[r for r in rows if vals(r,'change_color_id')]
print('change_color_id 行', len(cc))
ids=[]
for r in cc:
    for i in vals(r,'change_color_id'):
        if i not in ids: ids.append(i)
print('不同 change_color_id 数', len(ids), '样例', ids[:8])
try:
    CR,cb,cp=load('appear_change_color_data'); co=mk(cb,cp)
    cmap={r['key']:r for r in CR}
    hit=sum(1 for i in ids if i in cmap)
    print('appear_change_color_data 行', len(CR), '| 能对上', hit, '/', len(ids))
    for i in ids[:3]:
        r=cmap.get(i)
        if r: print('   id',i, {k:str(co(r,k))[:70] for k in r['values']})
except Exception as e: print('color table fail', e)
try:
    HR,hb,hp=load('appear_change_hair_color_data'); ho=mk(hb,hp)
    hmap={r['key']:r for r in HR}
    hids=[]
    for r in rows:
        for i in vals(r,'hair_change_color_id'):
            if i not in hids: hids.append(i)
    print('hair_change_color_id 不同 id', len(hids), '表行', len(HR), '对上', sum(1 for i in hids if i in hmap))
    for i in hids[:2]:
        r=hmap.get(i)
        if r: print('   id',i, {k:str(ho(r,k))[:70] for k in r['values']})
except Exception as e: print('hair color fail', e)

print('\n### #7 faked_times_limit × valid_days')
c=collections.Counter()
for r in rows:
    fl=vals(r,'faked_times_limit'); vd=vals(r,'valid_days')
    if fl: c[(tuple(fl), tuple(vd))]+=1
for k,v in c.most_common(6): print('   ', k, v)

print('\n### #8 valid_scene_ids')
sc=[(r['key'], vals(r,'valid_scene_ids')) for r in rows if vals(r,'valid_scene_ids')]
for k,v in sc[:6]: print('   ', k, v)

print('\n### #12 uncap_appear_gender')
c=collections.Counter()
for r in rows:
    u=vals(r,'uncap_appear_gender')
    if u: c[tuple(u)]+=1
print('   ', c.most_common())

print('\n### #14 friendliness')
c=collections.Counter()
for r in rows:
    f=vals(r,'friendliness')
    if f: c[tuple(f)]+=1
print('   ', c.most_common(8))

print('\n### #10 is_slim_bag 部位分布')
c=collections.Counter()
for r in rows:
    if vals(r,'is_slim_bag'):
        c[fo(r,'part_type')]+=1
print('   ', c.most_common())

print('\n### #19 theme_codes')
c=collections.Counter(); ex=[]
for r in rows:
    t=vals(r,'theme_codes')
    if t:
        for x in t: c[str(x)]+=1
        if len(ex)<5: ex.append((fo(r,'name'), t))
print('   ', c.most_common(12)); print('   样例', ex)

print('\n### #16 anim_graph_id / ui_anim_graph_id')
c=collections.Counter(); ex=[]
for r in rows:
    for f in ('anim_graph_id','ui_anim_graph_id'):
        v=vals(r,f)
        if v:
            for x in v: c[(f,str(x)[:30])]+=1
            if len(ex)<5: ex.append((fo(r,'name'), f, v[:2]))
print('   不同值', len(c), c.most_common(6)); print('   样例', ex)

print('\n### #17 preview_id / #18 bg_ids')
try:
    PR,pb,pp=load('player_fashion_preview_data'); pmap={r['key']:r for r in PR}
    pids=[]
    for r in rows:
        for i in vals(r,'preview_id'):
            if i not in pids: pids.append(i)
    print('preview_id 不同', len(pids), '表行', len(PR), '对上', sum(1 for i in pids if i in pmap))
    for i in pids[:3]:
        r=pmap.get(i)
        if r: print('   id',i,{k:str(pmap and fo(r,k))[:60] for k in r['values']})
except Exception as e: print('preview fail', e)
try:
    BR,bb,bp=load('fashion_bg_data'); bmap={r['key']:r for r in BR}
    bids=[]
    for r in rows:
        for i in vals(r,'bg_ids'):
            if i not in bids: bids.append(i)
    print('bg_ids 不同', len(bids), '表行', len(BR), '对上', sum(1 for i in bids if i in bmap))
    for i in bids[:3]:
        r=bmap.get(i)
        if r: print('   id',i,'bg_type',fo(r,'bg_type'),'img',fo(r,'bg_img_path'),'scn',fo(r,'scn_file'))
except Exception as e: print('bg fail', e)
