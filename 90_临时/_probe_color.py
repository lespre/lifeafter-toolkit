# -*- coding: utf-8 -*-
import sys, pathlib, collections, struct
PROJ = pathlib.Path('E:/la拆包项目')
sys.path.insert(0, str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
sys.path.insert(0, str(PROJ/'02_wiki/web/tools'))
from toolkit_core import bindict_table as BT
CD = PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
def load(n):
    raw=(CD/f'{n}.py').read_bytes(); at=raw.find(b'x{')
    L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
    cnt=struct.unpack_from('<I',body,0)[0]; blob=body[8+4*cnt:]
    pool=BT.parse_legacy_chs_pool((CD/f'{n}_chs.py').read_bytes())
    return BT.decode_table_rows(body,pool,resolve_jumps=False,lenient=True)[0], blob, pool
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
R,bl,pl=load('appear_change_color_data'); o=mk(bl,pl)
c=collections.Counter(); ex=[]
for r in R:
    cols=o(r,'colors') or []
    cv=o(r,'color_values') or []
    c[('colors' if cols else '', 'cv' if cv else '')]+=1
    if len(ex)<6 and cols: ex.append((r['key'], cols, cv))
print('appear_change_color_data 字段组合', c.most_common())
for e in ex: print('  ', e)
# 字段全集
keys=set()
for r in R: keys|=set(r['values'].keys())
print('字段', sorted(keys))
