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

A,ab,ap=load('player_appear_data'); ao=mk(ab,ap)
am={r['key']:r for r in A}
M,mb,mp=load('player_module_appear_data'); mo=mk(mb,mp)
mm={r['key']:r for r in M}

board=json.loads(pathlib.Path('02_wiki/web/data/boards/fashion_wardrobe.json').read_text(encoding='utf-8'))
def pb(it): return (it.get('part_bucket') or ['?'])[0]

print('=== ① 补充卡的 row_keys 是不是直接的外观行键？ ===')
sup=[it for it in board['items'] if it.get('source','').startswith('player_appear_data')]
print('  「其他外观并入」卡数:', len(sup))
# 这些卡的 row_keys 在 player_appear_data 命中率
hit=sum(1 for it in sup for k in (it.get('row_keys') or []) if int(k) in am)
tot=sum(len(it.get('row_keys') or []) for it in sup)
print(f'  row_keys 总数 {tot} | 在 player_appear_data 命中 {hit}')
# 分桶
print('  按桶:', collections.Counter(pb(it) for it in sup).most_common())
# 这些卡有 model_paths 吗
print('  有 model_paths:', sum(1 for it in sup if it.get('model_paths')))
print('  样例:')
for it in sup[:4]:
    ks=[int(k) for k in (it.get('row_keys') or [])]
    print('   ', it.get('name'), '| bucket', pb(it), '| keys', ks, '| model_paths', json.dumps(it.get('model_paths'), ensure_ascii=False)[:110])

print()
print('=== ② 挂饰卡：row_keys 指向 module 表吗 ===')
pin=[it for it in board['items'] if pb(it)=='挂饰']
inc=0; incm=0
for it in pin:
    ks=[int(k) for k in (it.get('row_keys') or []) if str(k).isdigit()]
    if any(k in am for k in ks): inc+=1
    if any(k in mm for k in ks): incm+=1
print(f'  挂饰卡 {len(pin)} | row_keys 命中 player_appear_data {inc} | 命中 player_module_appear_data {incm}')
for it in pin[:5]:
    ks=[int(k) for k in (it.get('row_keys') or []) if str(k).isdigit()]
    print('   ', it.get('name'), '| keys', ks, '| in A', [k in am for k in ks], '| in M', [k in mm for k in ks])

print()
print('=== ③ module 表的 charm/model 能不能补挂饰 ===')
# module 表里 face 部件 1174 行，有 model_paths 1200、charm 1153
print('  module 表: model_paths 非空 1200/1200, charm 非空 1153/1200, part_type face 1174')
# 板上面饰 56 + 挂饰 147 = 203
print('  板上面饰+挂饰 =', sum(1 for it in board['items'] if pb(it) in ('面饰','挂饰')))

print()
print('=== ④ 半感染者花苞 11 张 ===')
for it in board['items']:
    if pb(it)=='半感染者花苞':
        ks=[int(k) for k in (it.get('row_keys') or []) if str(k).isdigit()]
        print('   ', it.get('name'), '| keys', ks, '| in A', [k in am for k in ks])
