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
    return BT.decode_table_rows(body,pool,resolve_jumps=False,lenient=True)[0], blob, pool
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
am={k:a for k,a in ((a['key'],a) for a in A)}
for fm in (467480, 468880):
    fr=[r for r in F if r['key']==fm][0]
    print('==', fm, fo(fr,'name'), '| reborn_vis=', fr['values'].get('reborn_vis'),
          '| replace_flower_path=', fo(fr,'replace_flower_path'))
    ids=fo(fr,'appear_ids')
    print('   appear_ids', ids)
    for aid in ids:
        a=am.get(aid)
        if not a: print('   ', aid,'MISS'); continue
        print('   ', aid, '| sock_names', ao(a,'socket_names'), '| sock_models', ao(a,'socket_models'))
        print('        only_for_reborn', ao(a,'socket_model_only_for_reborn'), '| replace_flower_id', ao(a,'replace_flower_id'))
# 统计：socket_names 里带 flower 的行有多少、是否都 socket_model_only_for_reborn=1
cnt=0; both=0
for a in A:
    sn=ao(a,'socket_names') or []
    if isinstance(sn,list) and 'flower' in [str(x) for x in sn]:
        cnt+=1
        om=ao(a,'socket_model_only_for_reborn') or []
        idx=[i for i,x in enumerate([str(y) for y in sn]) if x=='flower']
        if any(i < len(om) and om[i] for i in idx): both+=1
print('\n挂点名含 flower 的外观行', cnt, '其中该挂点 only_for_reborn=1 的', both)
