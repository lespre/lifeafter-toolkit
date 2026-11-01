# -*- coding: utf-8 -*-
import sys, struct, pathlib, collections, datetime
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
F,fb,fp=load('fashion_data'); fo=mk(fb,fp)
def vals(r,f):
    x=fo(r,f); return x if isinstance(x,list) else ([] if x in (None,'') else [x])

print('### anim_graph_data 结构 + 对应')
try:
    AR,ab,ap=load('anim_graph_data'); ao=mk(ab,ap)
    amap={r['key']:r for r in AR}
    ids=set()
    for r in F:
        for f in ('anim_graph_id','ui_anim_graph_id'):
            for s in vals(r,f):
                for p in str(s).split(';'):
                    if p.strip().isdigit(): ids.add(int(p))
    print('  表行', len(AR), 'fashion 侧 id 数', len(ids), '对上', sum(1 for i in ids if i in amap))
    for i in list(ids)[:3]:
        r=amap.get(i)
        if r: print('   id',i,{k:str(ao(r,k))[:60] for k in sorted(r['values'])})
except Exception as e: print('  fail', e)

print('\n### preview_id 到底指向哪')
import subprocess
pids=set()
for r in F:
    for i in vals(r,'preview_id'): pids.add(int(i))
print('  preview_id 集', sorted(pids)[:20], '共', len(pids))
# 扫描所有表看哪个表主键覆盖这些 id
hits=[]
for f in CD.glob('*.py'):
    if f.name.endswith('_chs.py'): continue
    n=f.stem
    if any(k in n for k in ('preview','fashion','appear','player')):
        try:
            R,_,_=load(n)
        except Exception: continue
        keys={r['key'] for r in R}
        ov=keys & pids
        if len(ov)>=len(pids)*0.5: hits.append((n,len(R),len(ov)))
print('  覆盖 >=50% 的表:', hits[:8])

print('\n### start_show_ts → 日期')
ts=[]
for r in F:
    for t in vals(r,'start_show_ts'):
        try: ts.append((int(t), fo(r,'name')))
        except Exception: pass
ts.sort()
for t,n in ts[:3]+ts[-3:]:
    try: print('  ', t, datetime.datetime.utcfromtimestamp(t).strftime('%Y-%m-%d'), n)
    except Exception: print('  ', t, n)

print('\n### gift_package_id')
c=collections.Counter(); ex=[]
for r in F:
    g=vals(r,'gift_package_id')
    if g:
        c[tuple(g)]+=1
        if len(ex)<5: ex.append((fo(r,'name'), g))
print('  ', c.most_common(5)); print('  样例', ex)

print('\n### other_get_methods')
for r in F:
    o=vals(r,'other_get_methods')
    if o: print('  ', r['key'], fo(r,'name'), o)

print('\n### valid_scene_ids 280 是什么')
import os
cands=[f.stem for f in CD.glob('*.py') if 'scene' in f.stem and not f.name.endswith('_chs.py')]
print('  scene 候选表', cands[:14])
