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
v=lambda x: x[1] if isinstance(x,tuple) else x

print('=== ① 挂饰源表 player_module_appear_data 的 model_paths / v2_socket_model_path ===')
M,mb,mp=load('player_module_appear_data'); mo=mk(mb,mp)
mm={r['key']:r for r in M}
for k in (260000, 1372501):
    r=mm.get(k)
    if not r: continue
    print(' ==', k, v(r['values'].get('name')))
    for f in ('model_paths','v2_socket_model_path','v2_socket_names','model_id','model_socket','charm_value','icon','female_icon','part','part_type','level','valid_days'):
        print('    ', f, '=', mo(r,f))
# 分布
c=collections.Counter(); ch=collections.Counter(); pt=collections.Counter()
for r in M:
    c['model_paths' if mo(r,'model_paths') else '-']+=1
    ch['charm' if mo(r,'charm_value') else '-']+=1
    pt[str(mo(r,'part_type'))]+=1
print('  model_paths 非空', c['model_paths'], '/', len(M), '| charm 非空', ch['charm'])
print('  part_type 分布', pt.most_common())

print()
print('=== ② 戒指：player_appear_data 的 60001/160001 行 ===')
A,ab,ap=load('player_appear_data'); ao=mk(ab,ap)
am={r['key']:r for r in A}
for k in (60001,160001,60007,160007):
    r=am.get(k)
    if not r: print(' ==',k,'MISSING'); continue
    print(' ==', k, ao(r,'name'), '| part', ao(r,'part'), '| part_type', ao(r,'part_type'), '| gender', ao(r,'gender'))
    for f in ('model_name','high_model_name','human_body_model_name','charm_value','icon','icons','desc','level','socket_models'):
        print('    ', f, '=', ao(r,f))

print()
print('=== ③ 戒指/挂饰 在 player_appear_data 里的 part 分布 ===')
pc=collections.Counter()
for r in A:
    pc[str(mo(r,'part') if False else ao(r,'part'))]+=1
print('  part 分布:', pc.most_common(10))
# part=2 的行数与样例
p2=[r for r in A if ao(r,'part')==2]
print('  part=2 行数', len(p2))
for r in p2[:4]:
    print('    ', r['key'], ao(r,'name'), '| part_type', ao(r,'part_type'), '| model_name', ao(r,'model_name'), '| charm', ao(r,'charm_value'), '| icons', ao(r,'icons'))
