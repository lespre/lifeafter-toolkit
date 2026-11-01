# -*- coding: utf-8 -*-
import sys, pathlib, collections, struct, json
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

print('=== add_friendliness_data 全档（add_range 展开）===')
AF,ab,ap=load('add_friendliness_data'); ao=mk(ab,ap)
for r in AF:
    f=r['values']
    cp=f.get('critical_prob'); cr=f.get('critical_ratio'); ar=ao(r,'add_range')
    print('  档', r['key'], 'prob', cp[1] if isinstance(cp,tuple) else cp,
          'ratio', cr[1] if isinstance(cr,tuple) else cr, 'range', ar)

print('\n=== fashion_data 里 friendliness 的取值集合 ===')
F,fb,fp=load('fashion_data'); fo=mk(fb,fp)
v=lambda x: x[1] if isinstance(x,tuple) else x
def vals(r,f):
    x=fo(r,f); return x if isinstance(x,list) else ([] if x in (None,'') else [x])
fs=sorted({int(vals(r,'friendliness')[0]) for r in F if vals(r,'friendliness')})
print('  ', fs)

print('\n=== uncap_appear_gender × 板上 gender_scope ===')
board=json.loads(pathlib.Path('02_wiki/web/data/boards/fashion_wardrobe.json').read_text(encoding='utf-8'))
scope={}
for it in board['items']:
    for k in (it.get('row_keys') or []):
        try: scope[int(k)]=(it.get('gender_scope') or '?', it.get('name'))
        except Exception: pass
cross=collections.Counter(); ex=collections.defaultdict(list)
for r in F:
    u=vals(r,'uncap_appear_gender')
    if not u: continue
    val=str(u[0]); g=scope.get(r['key'],('未入板',''))[0]
    cross[(val,g)]+=1
    if len(ex[(val,g)])<3: ex[(val,g)].append((str(fo(r,'name')), str(fo(r,'part_type'))))
for k,n in sorted(cross.items()):
    print(f'  uncap={k[0]}  性别范围={k[1]:6s} {n:4d} 行   例:', ex[k][:2])
