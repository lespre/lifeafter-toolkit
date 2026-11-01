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
def base(s): 
    import re; return re.sub(r'-\d+天$','',str(s or ''))

# 主题表（fashion_obtain_handbook_data）
H,hb,hp=load('fashion_obtain_handbook_data'); ho=mk(hb,hp)
theme_of={}
for r in H:
    ids=ho(r,'fashion_ids') or []
    for i in ids:
        if isinstance(i,int): theme_of.setdefault(i, ho(r,'theme_name'))

print('=== 检验1：同一套装主题内 friendliness 是否一致 ===')
g=collections.defaultdict(set)
for r in F:
    t=theme_of.get(r['key'])
    if not t: continue
    fv=vals(r,'friendliness')
    if fv: g[t].add(int(fv[0]))
same=sum(1 for t,s in g.items() if len(s)==1); tot=len(g)
print(f'  主题 {tot} 个 | 组内 friendliness 唯一的主题 {same} 个')
for t in list(g)[:8]:
    print('   ', t, sorted(g[t]), [ (nm(r), vals(r,'friendliness')) for r in F if theme_of.get(r['key'])==t and vals(r,'friendliness')][:3])

print('\n=== 检验2：同名基础款的不同部件 friendliness 是否一致 ===')
g2=collections.defaultdict(set)
for r in F:
    fv=vals(r,'friendliness')
    if fv: g2[base(nm(r))].add(int(fv[0]))
multi=[(k,s) for k,s in g2.items() if len(s)>1]
print('  同名多值的基础款', len(multi), '/', len(g2))
for k,s in multi[:6]:
    print('   ', k, sorted(s), [(nm(r), str(fo(r,'part_type')), vals(r,'friendliness')) for r in F if base(nm(r))==k and vals(r,'friendliness')][:3])

print('\n=== 检验3：时限变体 vs 永久 是否同值 ===')
pairs=collections.defaultdict(set)
for r in F:
    fv=vals(r,'friendliness')
    if fv:
        b=base(nm(r)); pairs[b].add(int(fv[0]))
consistent=sum(1 for b,s in pairs.items() if len(s)==1)
print('  基础款内 friendliness 唯一:', consistent, '/', len(pairs))

print('\n=== 检验4：与 charm_value 的秩相关（Spearman 近似）===')
xs=[]
for r in F:
    fv=vals(r,'friendliness'); cv=v(r['values'].get('charm_value'))
    if fv and cv is not None: xs.append((int(fv[0]), int(cv)))
import statistics
def rank(data, idx):
    order=sorted(range(len(data)), key=lambda i: data[i][idx])
    rk=[0]*len(data); i=0
    while i<len(order):
        j=i
        while j+1<len(order) and data[order[j+1]][idx]==data[order[i]][idx]: j+=1
        avg=(i+j)/2+1
        for k in range(i,j+1): rk[order[k]]=avg
        i=j+1
    return rk
a=rank(xs,0); b=rank(xs,1)
n=len(xs); d2=sum((a[i]-b[i])**2 for i in range(n))
rho=1-6*d2/(n*(n*n-1))
print(f'  n={n}  Spearman(friendliness, charm_value) ≈ {rho:.3f}')
