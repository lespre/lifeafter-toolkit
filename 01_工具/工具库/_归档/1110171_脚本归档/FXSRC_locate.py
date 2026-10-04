# -*- coding: utf-8 -*-
"""FXSRC_locate.py — 用 c159 明文路径路线定位 1110152(skin_1012_009) / 1110024(skin_1006_004) 的特效源。
只读。在每个已解包容器的 *.c159 里按字节搜 skin id，并抽出其中的 `effect\fx\...\*.sfx` 明文路径与 socket 名。
"""
import os, re, json, glob

PACK = r'E:\la拆包项目\03拆包产物'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
TARGETS = {'1110152': b'skin_1012_009', '1110024': b'skin_1006_004'}
DIRS = ['weapon', 'effect_01', 'character_01', 'character_02', 'character_03', 'model_01', 'model_02', 'big_res']
rep = {}
for sid, needle in TARGETS.items():
    hits = []
    for d in DIRS:
        base = os.path.join(PACK, d)
        if not os.path.isdir(base):
            continue
        files = glob.glob(os.path.join(base, '*.c159'))
        for p in files:
            try:
                b = open(p, 'rb').read()
            except Exception:
                continue
            if needle in b:
                fx = re.findall(rb'[\x20-\x7e]*effect\\fx\\[\x20-\x7e]*\.sfx', b)
                gim = re.findall(rb'[\x20-\x7e]*weapon\\skin\\[\x20-\x7e]*\.gim', b)
                names = [m.group().decode('latin1') for m in re.finditer(rb'[\x20-\x7e]{3,}', b)]
                hits.append({'file': p, 'dir': d, 'bytes': len(b),
                             'fx_paths': sorted(set(x.decode('latin1') for x in fx)),
                             'gim_paths': sorted(set(x.decode('latin1') for x in gim))[:6],
                             'names_sample': names[:30]})
                if len(hits) >= 6:
                    break
        if len(hits) >= 6:
            break
    rep[sid] = {'needle': needle.decode(), 'hits': hits, 'hit_count': len(hits)}
    print('=== %s (%s) 命中 %d 个 c159 ===' % (sid, needle.decode(), len(hits)))
    for h in hits:
        print('   %s  %dB' % (h['file'], h['bytes']))
        print('      fx 路径: %s' % h['fx_paths'])
        print('      gim 路径: %s' % h['gim_paths'])
        print('      名字表前 30: %s' % h['names_sample'])
json.dump(rep, open(os.path.join(OUT, 'FXSRC_locate.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('json ->', os.path.join(OUT, 'FXSRC_locate.json'))
