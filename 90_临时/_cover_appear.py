# -*- coding: utf-8 -*-
import sys, pathlib, struct, json, collections
PROJ=pathlib.Path('E:/la拆包项目')
sys.path.insert(0,str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
CD=PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
def load(n):
    raw=(CD/f'{n}.py').read_bytes(); at=raw.find(b'x{')
    L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
    cnt=struct.unpack_from('<I',body,0)[0]; blob=body[8+4*cnt:]
    pool=BT.parse_legacy_chs_pool((CD/f'{n}_chs.py').read_bytes())
    rows=BT.decode_table_rows(body,pool,resolve_jumps=False,lenient=True)[0]
    return rows, blob, pool
v=lambda x: x[1] if isinstance(x,tuple) else x
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
        tag,val=got
        if tag!='0x0b': return val
        try:
            off=int(str(val).split(':')[1]); out=[]
            g=BT.read_27_group(blob,off)
            if g: ev(g,out)
            return out
        except Exception: return None
    return one
A,ab,ap=load('player_appear_data'); ao=mk(ab,ap)
board=json.loads(pathlib.Path('02_wiki/web/data/boards/fashion_wardrobe.json').read_text(encoding='utf-8'))
keys=set()
for it in board['items']:
    keys|=set(it.keys())
non=collections.Counter(); samp={}
for r in A:
    for f,x in r['values'].items():
        if x in (None,'',[],{}): continue
        non[f]+=1
        if f not in samp:
            v1=ao(r,f)
            samp[f]=(str(v(r['values'].get('name'))), str(v1)[:60])
miss=[(f,n) for f,n in non.items() if f not in keys]
print('player_appear_data 未落卡字段', len(miss))
for f,n in sorted(miss, key=lambda x:-x[1])[:40]:
    print(f'  {f:32s} 非空{n:6d}  例: {samp[f][0]} → {samp[f][1]}')
