# -*- coding: utf-8 -*-
import sys, pathlib, struct, collections
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
v=lambda x: x[1] if isinstance(x,tuple) else x
def jl(blob,row,field,pool):
    got=row['values'].get(field)
    if not got: return []
    tag,val=got
    if tag!='0x0b': return [val]
    try:
        off=int(str(val).split(':')[1]); out=[]
        def walk(g):
            k,els=g
            for e in els:
                if k==0x0b:
                    g2=BT.read_27_group(blob,e)
                    if g2: walk(g2)
                elif k==0x05: out.append(pool[e] if e<len(pool) else None)
                else: out.append(e)
        g=BT.read_27_group(blob,off)
        if g: walk(g)
        return out
    except Exception: return []

F,fb,fp=load('fashion_data')
A,ab,ap=load('player_appear_data')
X,xb,xp=load('fashion_data_for_export')
fm={r['key']:r for r in F}; am={r['key']:r for r in A}; xm={r['key']:r for r in X}

print('=== ② 跨表一致性：同一款时装在 3 张表里的 friendliness ===')
same=0; tot=0; diff=[]
for k,r in list(fm.items()):
    fv=v(r['values'].get('friendliness'))
    if fv is None: continue
    tot+=1
    ids=[i for i in jl(fb,r,'appear_ids',fp) if isinstance(i,int)]
    avs={v(am[i]['values'].get('friendliness')) for i in ids if i in am}
    xv=v(xm[k]['values'].get('friendliness')) if k in xm else 'NO_ROW'
    ok = (avs=={fv}) and (xv==fv)
    if ok: same+=1
    elif len(diff)<8: diff.append((k, str(v(r['values'].get('name'))[:12]), fv, sorted(str(x) for x in avs), xv))
print(f'  三表(fashion_data / player_appear_data / fashion_data_for_export) 完全一致: {same}/{tot}')
for d in diff: print('   不一致:', d)

print('\n=== ③ schema 里 friendliness 的位置与邻居 ===')
def schema_fields(blob, ref, pool):
    pos=ref
    n,pos=BT.uleb(blob,pos,len(blob))
    bits,pos=BT.uleb(blob,pos,len(blob))
    out=[]
    for _ in range(n):
        slot,pos=BT.uleb(blob,pos,len(blob))
        tb=blob[pos]; pos+=1
        out.append((slot,tb,pool[slot] if slot<len(pool) else f'<slot_{slot}>'))
    return out
seen=set()
for r in F[:400]:
    sr=r.get('schema')
    if sr is None or sr in seen: continue
    seen.add(sr)
    try: fs=schema_fields(fb, sr, fp)
    except Exception: continue
    idx=[i for i,(s,t,n) in enumerate(fs) if n=='friendliness']
    if idx:
        i=idx[0]
        nb=[f'{n}(t{t})' for s,t,n in fs[max(0,i-2):i+3]]
        print(f"  schema {sr}: ... {' | '.join(nb)} ...")
