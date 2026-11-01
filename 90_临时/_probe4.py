# -*- coding: utf-8 -*-
import sys, struct, pathlib, collections
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
F,fb,fp = load('fashion_data'); A,ab,ap = load('player_appear_data')
am={a['key']:a for a in A}
def v(x): return x[1] if isinstance(x,tuple) else x
def jlist(blob,row,f,pool):
    got=row['values'].get(f)
    if not got: return []
    tag,val=got
    if tag!='0x0b': return [val]
    off=int(str(val).split(':')[1]); out=[]
    def ev(g):
        k,els=g
        for e in els:
            if k==0x0b:
                g2=BT.read_27_group(blob,e)
                if g2: ev(g2)
            elif k==0x05: out.append(pool[e] if e<len(pool) else None)
            else: out.append(e)
    g=BT.read_27_group(blob,off)
    if g: ev(g)
    return out
def has_model(a):
    if not a: return False
    m=jlist(ab,a,'model_name',ap)
    return bool(m and str(m[0]).strip())
stat=collections.Counter()
ex=collections.defaultdict(list)
for r in F:
    ids=jlist(fb,r,'appear_ids',fp)
    f_ok = has_model(am.get(ids[0])) if len(ids)>0 else False
    m_ok = has_model(am.get(ids[1])) if len(ids)>1 else False
    fg = v(r['values'].get('force_gender'))
    key=(fg, f_ok, m_ok)
    stat[key]+=1
    if len(ex[key])<4: ex[key].append((r['key'], jlist(fb,r,'name',fp), ids))
print('force_gender | 女有模型 | 男有模型 : 行数')
for k,c in sorted(stat.items(), key=lambda x:-x[1]):
    print('  ', k, c, ex[k][:3])
