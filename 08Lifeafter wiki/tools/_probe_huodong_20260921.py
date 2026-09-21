# -*- coding: utf-8 -*-
import sys, os, json, importlib.util, re
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
BASE='F394516378015E27'; CHS='DACF87AE00F14120'   # huodong_conf ykxq 全量主表（skill 记载）
for role,fid in (('huodong_base',BASE),('huodong_chs',CHS)):
    print(role, fid, '→', '在包内 ✓' if fid in entries else '✗ 不在包内')
try:
    b,_ = RWS.read_payload(reader, pkg, entries, BASE, 'hb')
    c,_ = RWS.read_payload(reader, pkg, entries, CHS, 'hc')
    rows, unbound = RWS.table_rows(b, c)
    print('huodong_conf 行数:', len(rows), '| unbound:', len(unbound))
    # 收集文本值（0x05 CHS 文本）
    texts=[]
    for r in rows:
        vs = r.get('values') or {}
        for k,v in vs.items():
            s = v[1] if isinstance(v,(list,tuple)) and len(v)>1 and isinstance(v[1],str) else (v if isinstance(v,str) else None)
            if s and re.search(r'[\u4e00-\u9fff]', s):
                texts.append((r.get('key'), k, s))
    print('中文文本条数:', len(texts))
    kws=['中秋','无人机','信号','猎手','斩神','打铁花','月','团圆','坠','新']
    hit=[t for t in texts if any(k in t[2] for k in ['中秋','无人机','信号猎手','斩神','打铁花','月亮','月饼'])]
    print('\n★ 主题命中（中秋/无人机/斩神/打铁花）:', len(hit))
    for h in hit[:40]: print('   key=%-8s %-14s %s' % (h[0], h[1], h[2][:70]))
except Exception as e:
    print('解码失败:', repr(e)[:200])
