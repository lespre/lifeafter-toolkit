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
A,ab,ap=load('player_appear_data'); ao=mk(ab,ap)
am={r['key']:r for r in A}

print('=== 挂饰在 player_appear_data 里的模型字段 ===')
for k in (5012201, 15012201, 50054, 150054):
    r=am.get(k)
    if not r: print(' ==',k,'MISS'); continue
    print(' ==', k, ao(r,'name'), '| part', ao(r,'part'), '| part_type', ao(r,'part_type'))
    for f in ('model_name','high_model_name','socket_models','socket_names','v2_socket_model_path','charm_value','icon','icons'):
        print('    ', f, '=', ao(r,f))

print()
print('=== 补充卡能否从 player_appear_data 直接拿 model/charm ===')
board=json.loads(pathlib.Path('02_wiki/web/data/boards/fashion_wardrobe.json').read_text(encoding='utf-8'))
def pb(it): return (it.get('part_bucket') or ['?'])[0]
sup=[it for it in board['items'] if it.get('source','').startswith('player_appear_data')]
nmodel=0; ncharm=0; nhigh=0; nsock=0
for it in sup:
    ks=[int(k) for k in (it.get('row_keys') or []) if str(k).isdigit()]
    recs=[am[k] for k in ks if k in am]
    if not recs: continue
    if any(ao(r,'model_name') for r in recs): nmodel+=1
    if any(ao(r,'high_model_name') for r in recs): nhigh+=1
    if any(ao(r,'socket_models') for r in recs): nsock+=1
    if any(ao(r,'charm_value') is not None for r in recs): ncharm+=1
print(f'  补充卡 {len(sup)}：能拿到 model_name {nmodel} | high_model_name {nhigh} | socket_models {nsock} | charm_value {ncharm}')

print()
print('=== 全部卡：外观层可补字段的覆盖潜力 ===')
allrec=[r for r in A]
cnt=collections.Counter()
for r in A:
    for f in ('model_name','high_model_name','human_body_model_name','socket_models','v2_socket_model_path','charm_value','icon','icons','desc'):
        if ao(r,f) is not None: cnt[f]+=1
print('  player_appear_data 全表字段非空:', cnt.most_common())
