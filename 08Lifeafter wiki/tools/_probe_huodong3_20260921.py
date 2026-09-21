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
NOW = 1789920000  # 2026-09-21
def val(r,f):
    vs=r.get('values') or {}; v=vs.get(f)
    if isinstance(v,(list,tuple)) and len(v)>1: return v[1]
    return v
out=[]
for r in rows:
    vs=r.get('values') or {}
    name=str(val(r,'name') or ''); sub=str(val(r,'sub_title') or ''); ht=str(val(r,'hd_type') or '')
    end=val(r,'end_ts')
    try: endi=int(end)
    except Exception: endi=0
    if endi >= NOW and (name or sub):
        out.append({'key':r.get('key'),'name':name[:40],'sub':sub[:40],'type':ht[:30],
                    'end':datetime.datetime.fromtimestamp(endi).strftime('%Y-%m-%d') if endi else '?',
                    'cls':str(val(r,'hd_class') or '')[:28]})
out.sort(key=lambda x:x['end'])
print('=== end_ts ≥ 2026-09-21 的活动：%d 条 ===' % len(out))
for o in out[:60]:
    print('  %-6s %-14s %-16s %-22s 到 %s  [%s]' % (o['key'],o['name'],o['sub'],o['type'],o['end'],o['cls']))
json.dump(out, open(r'E:\la拆包项目\03拆包产物\_known_loop\huodong_future_20260921.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('→ huodong_future_20260921.json ✓')
