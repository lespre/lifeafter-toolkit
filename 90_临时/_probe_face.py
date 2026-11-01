# -*- coding: utf-8 -*-
"""捏脸/面饰/挂饰全量性核对：player_module_appear_data 1200 行 vs 板上卡"""
import sys, pathlib, struct, collections, json
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
# 板上所有 card 的 row_variants（module 卡用 row_variants 而不是 row_keys）
covered=set()
for it in board['items']:
    for k in (it.get('row_variants') or []):
        covered.add(str(k))
    for k in (it.get('row_keys') or []):
        covered.add(str(k))
print('module 表行数', len(M))
print('板上引用到的 module 行数', len([str(r['key']) for r in M if str(r['key']) in covered]))
print('未覆盖的 module 行', len([r for r in M if str(r['key']) not in covered]))
# 按 part 分组看覆盖
cp=collections.Counter(); cu=collections.Counter()
for r in M:
    pt=str(mo(r,'part'))
    (cp if str(r['key']) in covered else cu)[pt]+=1
print('已覆盖 part 分布:', cp.most_common())
print('未覆盖 part 分布:', cu.most_common())
print()
print('=== 未覆盖行的样例 ===')
n=0
for r in M:
    if str(r['key']) in covered: continue
    print('  ', r['key'], '|', mo(r,'name'), '| part', mo(r,'part'), '| part_type', mo(r,'part_type'), '| icon', mo(r,'icon'), '| charm', mo(r,'charm_value'))
    n+=1
    if n>=12: break
