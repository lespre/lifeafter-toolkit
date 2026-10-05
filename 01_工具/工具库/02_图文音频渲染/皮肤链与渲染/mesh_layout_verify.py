# -*- coding: utf-8 -*-
"""验证打补丁后的 mesh_parse2：全语料统计 + 关键样本对比"""
import sys, os, glob, struct, importlib
sys.path.insert(0, r"E:\la拆包项目\01_工具\工具库\02_图文音频渲染\皮肤链与渲染")
import mesh_parse2 as M
importlib.reload(M)
from collections import Counter

pats = sys.argv[1:]
files = []
for p in pats: files += glob.glob(p)
c = Counter(); bad = []
n = 0
for p in files:
    try:
        d = open(p, 'rb').read()
        if d[:4] != b'\x34\x80\xc8\xbb': continue
        n += 1
        P, uv, idx, meta = M.parse_mesh2(p)
        c['eng_ok' if meta['eng_ok'] else 'eng_BAD'] += 1
        c['state=%s' % meta['extra_streams_state']] += 1
        c['pos=%s' % meta['eng']['pos_mode']] += 1
        c['typ=%d' % meta['typ']] += 1
        c['ver=%s' % hex(meta['ver24'])] += 1
        if not meta['eng_ok']:
            bad.append((os.path.basename(p), meta['eng']['footer'], meta['footer_bytes'],
                        meta['typ'], len(meta['subs']), meta['tv'], meta['tf'],
                        [hex(u) for u in meta['flags']]))
        # 一致性：idx 全 < tv?（非平凡判据：要求 max>0）
        if idx.size and idx.max() >= meta['tv']:
            c['idx_oob'] += 1
    except Exception as e:
        c['EXC:%s' % type(e).__name__] += 1
print("files", n)
for k, v in sorted(c.items(), key=lambda kv: -kv[1]):
    print("  %-28s %d" % (k, v))
print("BAD sample:")
for b in bad[:15]:
    print("   ", b)
