# -*- coding: utf-8 -*-
import sys, struct, pathlib, collections, json
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

def mk_expand(blob,pool):
    def ev(g,out):
        k,els=g
        for e in els:
            if k==0x0b:
                g2=BT.read_27_group(blob,e)
                if g2: ev(g2,out)
            elif k==0x05: out.append(pool[e] if e<len(pool) else None)
            else: out.append(e)
    def one(row,f):
        got=row['values'].get(f)
        if not got: return None
        tag,v=got
        if tag!='0x0b': return v
        try:
            off=int(str(v).split(':')[1]); out=[]
            g=BT.read_27_group(blob,off)
            if g: ev(g,out)
            return out
        except Exception: return ['<jump>']
    return one

def census(tname):
    rows,blob,pool=load(tname); one=mk_expand(blob,pool)
    keys=set()
    for r in rows: keys|=set(r['values'].keys())
    res=[]
    for f in sorted(keys):
        non=0; distinct=set(); samples=[]
        for r in rows:
            v=one(r,f)
            if v in (None,'',[],{},0,False): continue
            if isinstance(v,list):
                if not v: continue
                non+=1
                s='['+', '.join(str(x) for x in v[:4])+('…]' if len(v)>4 else ']')
                distinct.add(str(v)[:120])
            else:
                non+=1; s=str(v)
                distinct.add(str(v)[:120])
            if len(samples)<3 and s not in samples: samples.append(s[:50])
        res.append((f, non, len(distinct), samples))
    return len(rows), res

for t in ('fashion_data','player_appear_data'):
    n,res=census(t)
    print(f'### {t}  rows={n}  fields={len(res)}')
    for f,non,nd,s in res:
        print(f'{f}\t{non}\t{nd}\t{" | ".join(s)}')
    print()
