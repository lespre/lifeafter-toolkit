# -*- coding: utf-8 -*-
import sys, pathlib, struct, collections
PROJ = pathlib.Path('E:/la拆包项目')
sys.path.insert(0, str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
from toolkit_core import cdata_nxs
CD = PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
def load(n):
    raw=(CD/f'{n}.py').read_bytes(); at=raw.find(b'x{')
    if at<0: return None
    L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
    pool=BT.parse_legacy_chs_pool((CD/f'{n}_chs.py').read_bytes())
    return BT.decode_table_rows(body,pool,resolve_jumps=False,lenient=True)[0]
v=lambda x: x[1] if isinstance(x,tuple) else x

print('=== 1) follow_charm_conf_data（跟随/伙伴魅力）===')
try:
    t=cdata_nxs.load_table('follow_charm_conf_data', CD)
    print(' kind',t.kind,'rows',len(t.rows))
    for r in t.rows[:5]: print('  ', r['key'], str(r['fields'])[:200])
except Exception as e: print(' fail', e)

print('\n=== 2) zss_zombie_friend_data（僵尸好友）===')
for name in ('zss_zombie_friend_data',):
    r=load(name)
    if not r: print(' ',name,'无 legacy'); continue
    print(' rows',len(r))
    for x in r[:5]: print('  ', x['key'], {k:str(v(val))[:46] for k,val in x['values'].items()})

print('\n=== 3) 全库搜：字段值/主键落在 680/1280/1960 的表 ===')
TARGET={680,1280,1960,700,1500,3000}
hits=collections.defaultdict(list)
files=[p for p in CD.glob('*.py') if not p.name.endswith('_chs.py')]
for p in files:
    try: rows=load(p.stem)
    except Exception: continue
    if not rows: continue
    for r in rows[:400]:
        for k,val in r['values'].items():
            vv = v(val)
            if isinstance(vv,int) and vv in TARGET and k in ('level','need','min','max','limit','score','value','threshold','friendliness','charm_value','add_friendliness','max_friendliness_score'):
                hits[p.stem].append((r['key'],k,vv))
                break
    if len(hits)>40: break
for t in list(hits)[:25]:
    print('  ', t, hits[t][:3])
