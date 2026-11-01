# -*- coding: utf-8 -*-
"""friendliness 到底跟什么相关：特征 × 数值 的互信息分析。"""
import sys, pathlib, struct, collections, math, re, json
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
def has(r,f): return bool(fo(r,f))
def s(r,f): return str(fo(r,f) or '')

rows=[r for r in F if v(r['values'].get('friendliness'))]
allrows=F
print('有值行', len(rows))

def mi(feature_fn, data):
    """互信息 I(feature; friendliness)，以 bit 计。"""
    joint=collections.Counter(); pa=collections.Counter(); pb=collections.Counter()
    n=0
    for r in data:
        fv=int(v(r['values'].get('friendliness'))) if v(r['values'].get('friendliness')) is not None else None
        x=feature_fn(r)
        joint[(x,fv)]+=1; pa[x]+=1; pb[fv]+=1; n+=1
    I=0.0
    for (x,y),c in joint.items():
        p=c/n
        I+=p*math.log2(p/((pa[x]/n)*(pb[y]/n)))
    hx=0.0
    for x,c in pa.items():
        p=c/n; hx-=p*math.log2(p)
    hy=0.0
    for y,c in pb.items():
        p=c/n; hy-=p*math.log2(p)
    return I, hx, hy

feats={
 'part_type': lambda r: s(r,'part_type') or '未标',
 'part_code': lambda r: str(v(r['values'].get('part'))),
 'level(品级)': lambda r: str(v(r['values'].get('level'))),
 'brand_id': lambda r: str(v(r['values'].get('brand_id'))),
 'charm_value': lambda r: str(v(r['values'].get('charm_value'))),
 '有套装buff': lambda r: bool(fo(r,'suit_buff_id')),
 '有互斥模块': lambda r: bool(fo(r,'mutex_modules')),
 '有专属动作': lambda r: bool(fo(r,'special_idle_anims2')),
 '可染色': lambda r: bool(fo(r,'change_color_id')),
 '藏花reborn': lambda r: bool(r['values'].get('reborn_vis')),
 '未拥有也显示': lambda r: bool(v(r['values'].get('show_no_have'))),
 '可预览': lambda r: bool(v(r['values'].get('fashion_preview'))),
 '名字含典藏': lambda r: '典藏' in s(r,'name'),
 '名字含幻彩': lambda r: '幻彩' in s(r,'name'),
 '名字含联动': lambda r: '联动' in s(r,'name'),
 '名字含幻典': lambda r: '幻典' in s(r,'name'),
 '名字含限定': lambda r: '限定' in s(r,'name'),
 'desc非空': lambda r: bool(v(r['values'].get('desc'))),
 '有model_id': lambda r: bool(v(r['values'].get('model_id'))),
 'foreign_name(海外)': lambda r: bool(v(r['values'].get('foreign_name'))),
 'is_2025': lambda r: bool(v(r['values'].get('is_2025'))),
 '有时限变体': lambda r: '天' in s(r,'name'),
 'part=衣服且level': lambda r: (s(r,'part_type'), str(v(r['values'].get('level')))),
}
res=[]
for name,fn in feats.items():
    I,hx,hy=mi(fn, allrows)
    res.append((I,name,hx))
res.sort(reverse=True)
print('\n互信息 I(特征; friendliness)  —— 只在「有 friendliness 的行」里算更有意义：')
rows2=[r for r in F if v(r['values'].get('friendliness'))]
res2=[]
for name,fn in feats.items():
    I,hx,hy=mi(fn, rows2)
    res2.append((I,name,hx,hy))
res2.sort(reverse=True)
for I,name,hx,hy in res2:
    print(f'  {name:18s} I={I:.4f} bit   H(特征)={hx:.3f}  H(数值)={hy:.3f}   归一化={I/hy if hy else 0:.2%}')
