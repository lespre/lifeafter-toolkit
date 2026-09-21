# -*- coding: utf-8 -*-
import sys, os, json, importlib.util, datetime
W = r'E:\la拆包项目\08Lifeafter wiki'
sys.path.insert(0, os.path.join(W,'tools'))
spec = importlib.util.spec_from_file_location('rws', os.path.join(W,'tools','rebuild_weapon_skin_catalog_current.py'))
RWS = importlib.util.module_from_spec(spec)
try: spec.loader.exec_module(RWS)
except SystemExit: pass
reg = RWS.load_current_source()
pkg = __import__('pathlib').Path(reg['path'])
reader = RWS.LiveNpkReader(pkg, str(reg.get('server_branch') or 'x'))
entries = {f'{e.file_id:016X}': e for e in reader._entries}
b,_ = RWS.read_payload(reader, pkg, entries, 'F394516378015E27', 'hb')
c,_ = RWS.read_payload(reader, pkg, entries, 'DACF87AE00F14120', 'hc')
rows, _ = RWS.table_rows(b, c)
NOW = 1789920000
def val(r,f):
    vs=r.get('values') or {}; v=vs.get(f)
    if isinstance(v,(list,tuple)) and len(v)>1: return v[1]
    return v
# 先看有哪些"时间类"字段名
allf=set()
for r in rows[:200]: allf |= set((r.get('values') or {}).keys())
tfields=[f for f in sorted(allf) if any(k in f.lower() for k in ('ts','time','begin','start','end','date','open'))]
print('时间类字段名:', tfields)
fut=[]
for r in rows:
    vs=r.get('values') or {}
    name=str(val(r,'name') or ''); sub=str(val(r,'sub_title') or '')
    def g(f):
        v=val(r,f)
        try: return int(v)
        except Exception: return 0
    begins=[g(f) for f in vs if f.lower() in ('begin_ts','start_ts','begin_time','start_time','open_ts','begin')]
    begins=[x for x in begins if x>1e9]
    end=g('end_ts')
    beg=min(begins) if begins else 0
    if beg and beg > NOW and end >= beg:
        fut.append({'key':r.get('key'),'name':name[:40],'sub':sub[:40],
                    'type':str(val(r,'hd_type') or '')[:28],
                    'begin':datetime.datetime.fromtimestamp(beg).strftime('%Y-%m-%d'),
                    'end':datetime.datetime.fromtimestamp(end).strftime('%Y-%m-%d') if end>1e9 else '?',
                    'cls':str(val(r,'hd_class') or '')[:30]})
fut.sort(key=lambda x:x['begin'])
print('\n=== 开始时间 > 今天 的活动（= 还没开的新活动）：%d 条 ===' % len(fut))
for o in fut[:60]:
    print('  %-6s %-14s %-16s %-20s %s ~ %s  [%s]' % (o['key'],o['name'],o['sub'],o['type'],o['begin'],o['end'],o['cls']))
json.dump(fut, open(r'E:\la拆包项目\03拆包产物\_known_loop\huodong_notyet_20260921.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('→ huodong_notyet_20260921.json ✓')
