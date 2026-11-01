# -*- coding: utf-8 -*-
import sys, struct, pathlib, collections
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
F,fb,fp = load('fashion_data'); A,ab,ap = load('player_appear_data')
def ev(blob, g, depth=0):
    kind, els = g
    out=[]
    for e in els:
        if kind==0x0b:
            g2=BT.read_27_group(blob,e)
            out += ev(blob,g2,depth+1) if g2 else []
        elif kind==0x05:
            out.append(fp[e] if e < len(fp) else f'<oob{e}>')
        else:
            out.append(e)
    return out
def vals(blob,row,f,pool):
    got=row['values'].get(f)
    if not got: return []
    tag,v=got
    if tag=='0x0b':
        off=int(str(v).split(':')[1])
        g=BT.read_27_group(blob,off)
        return ev(blob,g) if g else []
    return [v]
hits=[r for r in F if '白月魁' in str(vals(fb,r,'name',fp)) or '白月魁' in str(r['values'].get('show_name'))]
print('白月魁 rows', len(hits))
am={a['key']:a for a in A}
for r in hits:
    print('key',r['key'],'name',vals(fb,r,'name',fp),'model',vals(fb,r,'model_id',fp),'part',r['values'].get('part_type'))
    print('   icons', vals(fb,r,'icons',fp))
    print('   appear', vals(fb,r,'appear_ids',fp), 'force_gender', r['values'].get('force_gender'),'uncap',r['values'].get('uncap_appear_gender'))
    for aid in vals(fb,r,'appear_ids',fp):
        a=am.get(aid)
        print('    ->',aid, (vals(ab,a,'name',ap), a['values'].get('part'), a['values'].get('gender'), vals(ab,a,'model_name',ap)[:1]) if a else 'MISSING')
