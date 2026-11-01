# -*- coding: utf-8 -*-
import sys, struct, pathlib, collections, re, json
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
base=lambda s: re.sub(r'-\d+天$','',str(s))
def vals(r,f):
    x=fo(r,f); return x if isinstance(x,list) else ([] if x in (None,'') else [x])

board=json.loads(pathlib.Path('02_wiki/web/data/boards/fashion_wardrobe.json').read_text(encoding='utf-8'))
owner={}
for it in board['items']:
    for k in (it.get('row_keys') or []):
        try: owner[int(k)]=it['id']
        except Exception: pass
cards=set(owner.values())

def cover(pred):
    rows=[r for r in F if pred(r)]
    cs={owner.get(r['key']) for r in rows}
    cs.discard(None)
    return len(rows), len(cs)

R,rb,rp=load('fashion_obtain_res_data'); ro=mk(rb,rp)
rmap={r['key']:r for r in R}
print('获取途径(按行键直接命中) 行/卡', cover(lambda r: r['key'] in rmap and ro(rmap[r['key']],'obtain_res')))
# 按名字兜底
name2res={str(ro(r,'fashion_name') or ''): ro(r,'obtain_res') for r in R}
def res_by_name(r):
    nm=str(fo(r,'name') or '')
    return name2res.get(nm)
print('获取途径(按名字兜底)   行/卡', cover(lambda r: bool(res_by_name(r))))
print('  途径文本分布', collections.Counter(str(res_by_name(r)) for r in F if res_by_name(r)).most_common(8))

H,hb,hp=load('fashion_obtain_handbook_data'); ho=mk(hb,hp)
themes={}
for r in H:
    t=ho(r,'theme_name')
    ids=ho(r,'fashion_ids') or []
    for i in (ids if isinstance(ids,list) else []):
        themes.setdefault(base(fo([x for x in F if x['key']==int(i)][0],'name')) if any(x['key']==int(i) for x in F) else int(i), []).append((t, r['key']))
# 更稳：按 fashion_ids 直接记 id→主题
id2theme={}
for r in H:
    t=ho(r,'theme_name')
    for i in (ho(r,'fashion_ids') or []):
        id2theme.setdefault(int(i), []).append((t, r['key']))
print('套装主题 行/卡', cover(lambda r: r['key'] in id2theme))
yh=[r for r in F if (vals(r,'theme_codes') or [])==['yh']]
hit=sum(1 for r in yh if r['key'] in id2theme)
print('  theme_codes=yh 行', len(yh), '命中主题', hit)
# 时限变体：同名的其它变体
basehit=0
for r in yh:
    if r['key'] in id2theme: basehit+=1; continue
    nm=base(fo(r,'name'))
    sib=[x for x in F if base(fo(x,'name'))==nm and x['key'] in id2theme]
    if sib: basehit+=1
print('  yh 按同名兜底命中', basehit, '/', len(yh))
print('  主题名 top', collections.Counter(t for r in H for t in [ho(r,'theme_name')]).most_common(10))
