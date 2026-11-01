# -*- coding: utf-8 -*-
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
A,ab,ap=load('player_appear_data'); ao=mk(ab,ap)
print('=== player_appear_data 按 part 的 charm/model 覆盖 ===')
g=collections.defaultdict(lambda: [0,0,0,0,0])
for r in A:
    pt=str(ao(r,'part'))
    g[pt][0]+=1
    if ao(r,'charm_value') is not None: g[pt][1]+=1
    if ao(r,'model_name') or ao(r,'high_model_name'): g[pt][2]+=1
    if ao(r,'socket_models'): g[pt][3]+=1
    if ao(r,'icon') or ao(r,'icons'): g[pt][4]+=1
print('  part | 行数 | 有charm | 有model | 有socket_models | 有icon')
for pt in sorted(g, key=lambda x:-g[x][0]):
    v=g[pt]; print(f'  {pt:8s} {v[0]:5d} {v[1]:6d} {v[2]:6d} {v[3]:8d} {v[4]:8d}')

print()
print('=== 板上挂饰/戒指卡 能否从 row_keys 直取 socket_models/charm ===')
board=json.loads(pathlib.Path('02_wiki/web/data/boards/fashion_wardrobe.json').read_text(encoding='utf-8'))
am={r['key']:r for r in A}
def pb(it): return (it.get('part_bucket') or ['?'])[0]
for bucket in ('挂饰','戒指','半感染者花苞'):
    cards=[it for it in board['items'] if pb(it)==bucket]
    nsm=0; nch=0; nmod=0
    for it in cards:
        ks=[int(k) for k in (it.get('row_keys') or []) if str(k).isdigit()]
        recs=[am[k] for k in ks if k in am]
        if any(ao(r,'socket_models') for r in recs): nsm+=1
        if any(ao(r,'charm_value') is not None for r in recs): nch+=1
        if any(ao(r,'model_name') or ao(r,'high_model_name') for r in recs): nmod+=1
    print(f'  {bucket:10s} 卡 {len(cards):4d} | 直取可得 socket_models {nsm} | charm {nch} | model_name {nmod}')

print()
print('=== 现有 face_ 卡的 _media 落地方式 ===')
face=[it for it in board['items'] if it['id'].startswith('face_')][0]
print(json.dumps(face, ensure_ascii=False, indent=1)[:1200])
