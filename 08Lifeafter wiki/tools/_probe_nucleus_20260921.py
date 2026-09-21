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
b,_ = RWS.read_payload(reader, pkg, entries, 'F394516378015E27', 'b')
c,_ = RWS.read_payload(reader, pkg, entries, 'DACF87AE00F14120', 'c')
rows, _u = RWS.table_rows(b, c)
by = {r.get('key'): r for r in rows}
def val(r,f):
    vs=r.get('values') or {}; v=vs.get(f)
    if isinstance(v,(list,tuple)) and len(v)>1: return v[1]
    return v
def ts(v):
    try:
        n=int(v)
        if n>1e9: return datetime.datetime.fromtimestamp(n).strftime('%Y-%m-%d')
    except Exception: pass
    return str(v)[:12]
for k in (2871,3440,3343,3587,3595):
    r=by.get(k)
    if not r: print('key=%s ✗' % k); continue
    vs=r.get('values') or {}
    show={fn:(ts(val(r,fn)) if fn in ('start_ts','end_ts') else str(val(r,fn))[:56]) for fn in ('name','sub_title','hd_type','hd_class','start_ts','end_ts') if fn in vs}
    print('key=%-5s %s' % (k, json.dumps(show, ensure_ascii=False)))
# 所有含「核芯」或「无人机」的行（近两年）
print('\n=== 含「核芯」/「无人机」的行（按结束时间）===')
out=[]
for r in rows:
    vs=r.get('values') or {}
    nm=str(val(r,'name') or ''); st=str(val(r,'sub_title') or ''); ht=str(val(r,'hd_type') or '')
    if any(k in nm+st+ht for k in ('核芯','无人机')):
        e=val(r,'end_ts')
        try: e=int(e)
        except Exception: e=0
        out.append((e, r.get('key'), nm[:22], st[:26], ht[:20], str(val(r,'hd_class') or '')[:24]))
out.sort(reverse=True)
for e,k,nm,st,ht,cls in out[:22]:
    print('  %-6s %-13s %-16s %-9s %s  [%s]' % (k, nm, st, ht, datetime.datetime.fromtimestamp(e).strftime('%Y-%m-%d') if e>1e9 else '?', cls))
