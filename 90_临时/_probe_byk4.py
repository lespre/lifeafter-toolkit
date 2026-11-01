# -*- coding: utf-8 -*-
import sys, struct, pathlib
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
F,fb,fp=load('fashion_data'); A,ab,ap=load('player_appear_data')
fo=mk(fb,fp); ao=mk(ab,ap)
am={a['key']:a for a in A}
print('=== 换花 5 款（女版 appear 行）===')
for k in (3349901, 3355101, 3364501, 3366101, 3346001):
    a=am[k]
    print('==', k, ao(a,'name'))
    for f in ('socket_names','socket_models','v2_socket_names','socket_model_only_for_reborn','replace_flower_id','model_name'):
        print('   ', f, '=', ao(a,f))
print()
print('=== fashion 侧 replace_flower_* ===')
for r in F:
    if r['values'].get('replace_flower_path') and v0(r):
        pass
v=lambda x: x[1] if isinstance(x,tuple) else x
n=0
for r in F:
    if r['values'].get('replace_flower_path'):
        print(' ', r['key'], v(r['values'].get('name')), '| path=', fo(r,'replace_flower_path'), '| id=', fo(r,'replace_flower_id'))
        n+=1
        if n>=4: break
