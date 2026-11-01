# -*- coding: utf-8 -*-
import sys, pathlib, struct, collections, json
PROJ=pathlib.Path('E:/la拆包项目')
sys.path.insert(0,str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
CD=PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
def load(n):
    raw=(CD/f'{n}.py').read_bytes(); at=raw.find(b'x{')
    if at<0: return None,None,None
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
F,fb,fp=load('fashion_data'); fo=mk(fb,fp)

print('=== 荧光棒（part_type=light）的 charm_value 在源表有没有 ===')
lt=[r for r in F if fo(r,'part_type')=='light']
print('  light 行', len(lt), '| 有 charm_value', sum(1 for r in lt if v(r['values'].get('charm_value')) is not None))
print('  样例:')
for r in lt[:3]:
    print('   ', fo(r,'name'), '| charm', v(r['values'].get('charm_value')), '| level', v(r['values'].get('level')))

print()
print('=== 戒指/半感染者花苞 在 fashion_data 里有没有 ===')
for kw in ('戒指','花苞','控制器','花朵'):
    hits=[r for r in F if kw in str(fo(r,'name') or '')]
    print(f'  名字含「{kw}」: {len(hits)} 行 | 有 charm {sum(1 for r in hits if v(r["values"].get("charm_value")) is not None)}')

print()
print('=== 荧光棒 / 挂饰 / 戒指 的 part_type 汇总（fashion_data）===')
c=collections.Counter(); ch=collections.Counter()
for r in F:
    pt=str(fo(r,'part_type') or '空')
    c[pt]+=1
    if v(r['values'].get('charm_value')) is not None: ch[pt]+=1
for k,n in c.most_common():
    print(f'   {k:8s} 行{n:6d}  有charm {ch[k]:6d}')
