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

def head(t, n=3):
    try:
        rows,blob,pool=load(t)
    except Exception as e:
        print('!!', t, 'load fail', e); return
    o=mk(blob,pool)
    keys=set()
    for r in rows: keys|=set(r['values'].keys())
    print(f'== {t} rows={len(rows)} fields={len(keys)}')
    for r in rows[:n]:
        print('   ', r['key'], {k:(o(r,k) if isinstance(o(r,k),(list,dict)) else str(o(r,k))[:40]) for k in sorted(r['values'].keys())})
    return rows, o

for t in ('appear_change_color_data','fashion_bg_data','player_fashion_preview_data','available_glowstick_data','fashion_bg_type_data'):
    head(t, 2); print()
