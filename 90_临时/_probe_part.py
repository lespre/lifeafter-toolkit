# -*- coding: utf-8 -*-
import sys, pathlib, struct, collections
PROJ = pathlib.Path('E:/la拆包项目')
sys.path.insert(0, str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
CD = PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
raw=(CD/'fashion_data.py').read_bytes(); at=raw.find(b'x{')
L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
cnt=struct.unpack_from('<I',body,0)[0]; blob=body[8+4*cnt:]
pool=BT.parse_legacy_chs_pool((CD/'fashion_data_chs.py').read_bytes())
F=BT.decode_table_rows(body,pool,resolve_jumps=False,lenient=True)[0]
v=lambda x: x[1] if isinstance(x,tuple) else x
def one(r,f):
    got=r['values'].get(f)
    if not got: return None
    tag,val=got
    if tag!='0x0b': return val
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
    except Exception: return None
print('=== fashion_data.part 分布（× part_type）===')
c=collections.Counter()
for r in F:
    p=v(r['values'].get('part'))
    if p is None: continue
    c[(p, str(v(r['values'].get('part_type'))))]+=1
for k,n in sorted(c.items(), key=lambda x:(-x[1]))[:20]: print('  part=',k[0],'part_type=',k[1],'→',n)
print('\n=== part 为 jump 的行（列表）===')
n=0
for r in F:
    p=one(r,'part')
    if isinstance(p,list):
        print('  ', v(r['values'].get('name')), '→', p)
        n+=1
        if n>=6: break
print('\n=== show_name 与 name 不同的情况 ===')
n=0
for r in F:
    sn=v(r['values'].get('show_name')); nm=v(r['values'].get('name'))
    if sn and nm and sn!=nm:
        print('  ', nm, '→ show_name:', sn)
        n+=1
        if n>=8: break
print('\n=== show_name 缺失但 name 存在 ===')
miss=[r for r in F if not r['values'].get('show_name') and r['values'].get('name')]
print('  行数', len(miss), '例', [v(r['values'].get('name')) for r in miss[:5]])
