# -*- coding: utf-8 -*-
"""补充卡能拿到的字段汇总 + 投影的 model/charm 源 + 捏脸全量性核对"""
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

print('=== ① 捏脸：源表全量 vs 板上的 190 张 ===')
for t in ('fashion_preset_do_face_config_data','do_face_v4_preset_data','do_face_v4_preview_data','do_face_config_data','do_face_config_v2_data','sub_do_face_ui_v4_data','sub_do_face_ui_data','fashion_preset_do_face_makeup_data'):
    r,_,_=load(t)
    if not r: print(f'  {t}: 无'); continue
    print(f'  {t}: {len(r)} 行')

print()
print('=== ② 捏脸 preset 的主键形态 ===')
R,rb,rp=load('fashion_preset_do_face_config_data'); ro=mk(rb,rp)
fs=collections.Counter()
for r in R:
    for f in r['values']: fs[f]+=1
print('  fashion_preset_do_face_config_data 字段:', sorted(fs))
for r in R[:4]:
    print('   ', r['key'], {k:str(ro(r,k))[:44] for k in sorted(r['values'])[:9]})

print()
print('=== ③ 板上捏脸卡的 row_variants / time_limited_variants ===')
board=json.loads(pathlib.Path('02_wiki/web/data/boards/fashion_wardrobe.json').read_text(encoding='utf-8'))
face=[it for it in board['items'] if it['id'].startswith('face_')]
print('  捏脸卡', len(face))
print('  part_source 分布:', collections.Counter(it.get('part_source') for it in face).most_common())
print('  样例:', json.dumps({k:v for k,v in face[0].items() if k not in ('provenance',)}, ensure_ascii=False)[:800])
