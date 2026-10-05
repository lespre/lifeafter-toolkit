# -*- coding: utf-8 -*-
"""FXSRC_scan_gpk2.py <输出前缀> <needle1> [needle2 ...] — 在 effect_*.gpk 帧中按内容找目标皮肤特效源。只写本目录。"""
import os, sys, json, time, hashlib
from pathlib import Path
sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\10_应用核心')
from toolkit_core.fpk_frames import iter_fpk_frames

OUT = Path(r'E:\la拆包项目\03拆包产物\_target_1110171')
prefix = sys.argv[1]
needles = [a.encode() for a in sys.argv[2:]] or [b'1012_009']
targets = [r'E:\mrzh\res\effect_01.gpk', r'E:\mrzh\res\effect_02.gpk', r'E:\mrzh\res\effect_cache.gpk']
hits = []
for t in targets:
    if not os.path.exists(t):
        print('MISS', t, flush=True)
        continue
    t0 = time.time(); n = 0; h = 0
    for fr, payload in iter_fpk_frames(t):
        n += 1
        if b'<FxGroup' in payload[:400] and any(nd in payload for nd in needles):
            hh = hashlib.sha256(payload).hexdigest()[:16]
            name = '%s_gpk_%s_f%d_%s.bin' % (prefix, os.path.basename(t).replace('.gpk', ''), fr.index, hh)
            (OUT / name).write_bytes(payload)
            hits.append(dict(gpk=os.path.basename(t), frame=fr.index, offset=fr.offset, size=len(payload),
                             sha16=hh, saved=name, matching=[nd.decode() for nd in needles if nd in payload]))
            h += 1
            print('HIT %s f%d %dB -> %s' % (os.path.basename(t), fr.index, len(payload), name), flush=True)
    print('%s frames=%d hits=%d %.0fs' % (os.path.basename(t), n, h, time.time() - t0), flush=True)
json.dump({'prefix': prefix, 'needles': [n.decode() for n in needles], 'hits': hits},
          open(OUT / (prefix + '_scan.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('DONE hits=%d' % len(hits), flush=True)
