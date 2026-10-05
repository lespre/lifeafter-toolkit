# -*- coding: utf-8 -*-
"""FX152_scan_gpk.py — 在 effect_*.gpk 帧中按内容找 skin_1012_009（1110152 灵态诱导）的特效源。

路线同 scan_gpk_fx010.py：复用 toolkit_core.fpk_frames.iter_fpk_frames 逐帧扫描，
needle = skin_1012_009 / fx_skin_1012 / 1012_009；命中帧落盘到本目录（FX152_ 前缀），绝不写 _sfx_010。
"""
import os, sys, json, time, hashlib
from pathlib import Path

sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\10_应用核心')
from toolkit_core.fpk_frames import iter_fpk_frames

OUT = Path(r'E:\la拆包项目\03拆包产物\_target_1110171')
NEEDLES = [b'skin_1012_009', b'fx_skin_1012', b'1012_009', b'lingtai', b'1012']
targets = [r'E:\mrzh\res\effect_01.gpk', r'E:\mrzh\res\effect_02.gpk', r'E:\mrzh\res\effect_cache.gpk']

hits = []
for t in targets:
    if not os.path.exists(t):
        print('MISS', t, flush=True)
        continue
    t0 = time.time(); n = 0; h = 0
    for fr, payload in iter_fpk_frames(t):
        n += 1
        if any(nd in payload for nd in NEEDLES[:3]):      # 严格 needle（不含 1012/lingtai 泛匹配）
            hh = hashlib.sha256(payload).hexdigest()[:16]
            name = 'FX152_gpk_%s_f%d_%s.bin' % (os.path.basename(t).replace('.gpk', ''), fr.index, hh)
            (OUT / name).write_bytes(payload)
            hits.append(dict(gpk=os.path.basename(t), frame=fr.index, offset=fr.offset, size=len(payload),
                             magic=fr.output_magic, saved=name, sha16=hh,
                             head_ascii=payload[:120].decode('utf-8', 'replace'),
                             is_fxgroup=b'FxGroup' in payload[:200],
                             matching=[nd.decode() for nd in NEEDLES[:3] if nd in payload]))
            h += 1
            print('HIT %s f%d %s %dB -> %s' % (os.path.basename(t), fr.index, fr.output_magic, len(payload), name), flush=True)
    print('%s frames=%d hits=%d %.0fs' % (os.path.basename(t), n, h, time.time() - t0), flush=True)

json.dump({'needles': [n.decode() for n in NEEDLES], 'hits': hits},
          open(OUT / 'FX152_scan_gpk.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('DONE hits=%d' % len(hits), flush=True)
