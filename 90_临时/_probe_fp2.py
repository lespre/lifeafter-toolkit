# -*- coding: utf-8 -*-
import sys, pathlib, collections, struct
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
            elif k==0x05: out.append(pool[e] if e<len(pool) else None)
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
        except Exception: return None
    return one
F,fb,fp=load('fashion_data'); fo=mk(fb,fp)
v=lambda x: x[1] if isinstance(x,tuple) else x
def vals(r,f):
    x=fo(r,f); return x if isinstance(x,list) else ([] if x in (None,'') else [x])
nm=lambda r: str(fo(r,'name') or '')

PR,pb,pp=load('player_fashion_preview_data'); po=mk(pb,pp)
grp={}
for r in PR:
    g=v(r['values'].get('group_id'))
    if g is None: continue
    grp.setdefault(int(g), []).append({
        'key': r['key'],
        'tag': v(r['values'].get('tag_name')),
        'anim': v(r['values'].get('preview_idle_anim')),
        'title_img': v(r['values'].get('title_img_path')),
        'img': v(r['values'].get('img_path')),
        'cam': (v(r['values'].get('camera_pos_nan')), v(r['values'].get('camera_pos_nv'))),
    })

fpid=sorted({int(vals(r,'preview_id')[0]) for r in F if vals(r,'preview_id')})
print('preview_id 取值', len(fpid), '个；能命中 preview 表 group_id 的:', len([x for x in fpid if x in grp]))
print('preview 表 group_id 全集', sorted(grp))
for gid in fpid[:14]:
    ent=grp.get(gid) or []
    tags=sorted({str(e['tag']) for e in ent if e['tag']})
    anims=sorted({str(e['anim']) for e in ent if e['anim']})
    # 该组包含哪些款
    names=[]
    for r in F:
        pv=vals(r,'preview_id')
        if pv and int(pv[0])==gid:
            n=nm(r)
            if not any(n.endswith(f'-{d}天') for d in (1,3,5,7,14,30)) and n not in names: names.append(n)
    print(f'  组 {gid:3d} 标签={tags} 动画={anims} 款数={len(names)} 例:{"、".join(names[:3])}')

print('\n=== friendliness 的极端例子（低魅力但高好感 / 高魅力但低好感）===')
rows_f=[r for r in F if vals(r,'friendliness') and v(r['values'].get('charm_value')) is not None]
pairs=[]
for r in rows_f:
    fv=int(vals(r,'friendliness')[0]); cv=int(v(r['values'].get('charm_value')))
    pairs.append((fv-cv, fv, cv, nm(r), str(fo(r,'part_type')), v(r['values'].get('level')), str(v(r['values'].get('desc')) or '')[:22]))
pairs.sort()
print(' 差值最小（好感≈魅力×10 量级）:')
for x in pairs[:4]: print('   ', x)
print(' 差值最大（魅力低但好感高）:')
for x in pairs[-6:]: print('   ', x)
