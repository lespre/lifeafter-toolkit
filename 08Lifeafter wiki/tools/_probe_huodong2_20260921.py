# -*- coding: utf-8 -*-
import sys, os, json, importlib.util, re, datetime
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
by = {r.get('key'): r for r in rows}

def val(r, fname):
    vs = r.get('values') or {}
    v = vs.get(fname)
    if isinstance(v,(list,tuple)) and len(v)>1: return v[1]
    return v

def ts(v):
    try:
        n=int(v)
        if n>1e9: return datetime.datetime.fromtimestamp(n).strftime('%Y-%m-%d %H:%M')
    except Exception: pass
    return str(v)[:24]

keys=[2664,2724,2726,2731,3074,3232,3343,3418,3420,3466,3513,3516,3587,3597]
print('=== 活动表命中行的完整字段 ===')
for k in keys:
    r = by.get(k)
    if not r: print('  key=%s ✗ 不存在' % k); continue
    vs = r.get('values') or {}
    names = {fn for fn in vs}
    show = {}
    for fn in ('name','sub_title','hd_type','tab_name','begin_time','end_time','start_time','end_ts','exp','priority','hd_class','ui_short_name_es_key'):
        if fn in vs: show[fn] = (ts(val(r,fn)) if 'time' in fn or fn in ('exp','end_ts') else str(val(r,fn))[:60])
    print('  key=%-6s %s' % (k, json.dumps(show, ensure_ascii=False)))
    # 全部数值型字段（可能含时间）
    nums = {fn: val(r,fn) for fn in vs if fn not in show}
    long_nums = {fn:v for fn,v in nums.items() if isinstance(v,int) and v>1.7e9 and v<2.2e9}
    if long_nums:
        print('        疑似时间戳字段:', {fn: ts(v) for fn,v in list(long_nums.items())[:8]})
