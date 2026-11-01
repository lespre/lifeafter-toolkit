# -*- coding: utf-8 -*-
"""module 表未覆盖的 180 行：是什么？分组键是什么？"""
import sys, pathlib, struct, collections, json, re
PROJ=pathlib.Path('E:/la拆包项目')
sys.path.insert(0,str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
CD=PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
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
        except Exception as e: return f'<err {e}>'
    return one
v=lambda x: x[1] if isinstance(x,tuple) else x
M,mb,mp=load('player_module_appear_data'); mo=mk(mb,mp)
board=json.loads(pathlib.Path('02_wiki/web/data/boards/fashion_wardrobe.json').read_text(encoding='utf-8'))
covered=set()
for it in board['items']:
    for k in (it.get('row_variants') or [])+(it.get('row_keys') or []): covered.add(str(k))
unc=[r for r in M if str(r['key']) not in covered]
print('未覆盖', len(unc))
def base(s):
    s=str(s or '')
    return re.sub(r'-\d+天$','',s)
g=collections.defaultdict(list)
for r in unc: g[(str(mo(r,'part')), base(mo(r,'name')))].append(r)
print('按 (part, 基础名) 分组:', len(g), '组')
for k,v in list(g.items())[:14]:
    print(f'   part={k[0]:6s} {k[1]:22s} {len(v)} 行  keys={[x["key"] for x in v][:4]}  charm={[mo(x,"charm_value") for x in v][:3]}')
# 名称是否有重复出现（已覆盖的里同名）
print()
print('=== 未覆盖行的名字是否已在板上存在（同名的已覆盖行）===')
covnames={mo(r,'name') for r in M if str(r['key']) in covered}
hit=sum(1 for r in unc if mo(r,'name') in covnames)
print(f'  未覆盖行中，名字已出现在板上的: {hit}/{len(unc)}')
