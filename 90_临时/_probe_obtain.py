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
F,fb,fp=load('fashion_data'); fo=mk(fb,fp)
R,rb,rp=load('fashion_obtain_res_data'); ro=mk(rb,rp)
rmap={r['key']:r for r in R}
fk={r['key'] for r in F}
print('fashion_obtain_res_data 行', len(R), '| 主键与 fashion_data 交集', len(set(rmap) & fk))
ov=collections.Counter()
for r in R:
    if r['key'] in fk: ov[ro(r,'obtain_res')]+=1
print('  途径分布 top', ov.most_common(12))
print('  主键范围', min(rmap), '~', max(rmap))
for k in (467480, 468880, 166000):
    r=rmap.get(k)
    print('  ', k, (ro(r,'fashion_name'), ro(r,'obtain_res')) if r else 'MISS')

print('\n### handbook 主题')
H,hb,hp=load('fashion_obtain_handbook_data'); ho=mk(hb,hp)
themes={}
for r in H:
    t=ho(r,'theme_name')
    ids=ho(r,'fashion_ids') or []
    for i in (ids if isinstance(ids,list) else []):
        themes.setdefault(int(i), []).append((t, r['key']))
print('  handbook 行', len(H), '覆盖 fashion_id', len(themes))
# theme_codes=yh 的行能否落到主题
yh=[r for r in F if (fo(r,'theme_codes') or [])==['yh']]
hit=0; miss=[]
for r in yh:
    ids=themes.get(r['key'])
    if ids: hit+=1
    else: miss.append(fo(r,'name'))
print('  theme_codes=yh 行', len(yh), '能查到主题', hit, '查不到', len(miss), miss[:6])
ex=[(r['key'], ho(r,'theme_name'), ho(r,'fashion_ids')[:3]) for r in H[:3]]
print('  样例', ex)
# 覆盖率：全表有多少 fashion_data 行能查到主题
tot=sum(1 for r in F if r['key'] in themes)
print('  fashion_data 行能查到主题', tot, '/', len(F))
