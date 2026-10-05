# -*- coding: utf-8 -*-
"""FXSRC_find_fxgroup.py — 在已扫出的命中帧里挑出目标皮肤的 FxGroup XML（只读 + 写本目录 FXSRC_*）。
用法: python FXSRC_find_fxgroup.py <needle 例如 1012_009>
"""
import glob, os, re, sys, json

OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
needle = (sys.argv[1] if len(sys.argv) > 1 else '1012_009').encode()
rep = {'needle': needle.decode(), 'candidates': []}
for p in sorted(glob.glob(os.path.join(OUT, 'FX152_gpk_*.bin'))):
    b = open(p, 'rb').read()
    if b'<FxGroup' not in b[:400]:
        continue
    txt = b.decode('gbk', 'replace')
    if needle.decode() not in txt:
        continue
    nodes = re.findall(r'<(Sprite|ParticleSystem|Dummy|Model|ParticleRes|Trail)\b[^>]*Name\s*=\s*"([^"]*)"', txt)
    tex = sorted(set(re.findall(r'Texture\s*=\s*"([^"]+)"', txt)))
    gim = sorted(set(re.findall(r'ModelName\s*=\s*"([^"]+)"', txt)))
    fxpath = sorted(set(re.findall(r'effect\\fx\\[\w\\]*\.sfx', txt)))
    rep['candidates'].append({'file': os.path.basename(p), 'bytes': len(b),
                              'node_count': len(nodes),
                              'tags': {t: sum(1 for x, _ in nodes if x == t) for t in set(x for x, _ in nodes)},
                              'names': [n for _, n in nodes],
                              'textures': tex, 'model_meshes': gim, 'fx_paths_in_xml': fxpath,
                              'needle_hits': txt.count(needle.decode())})
    print('== %s  %dB  节点 %d  %s' % (os.path.basename(p), len(b), len(nodes),
                                       json.dumps({t: sum(1 for x, _ in nodes if x == t) for t in set(x for x, _ in nodes)}, ensure_ascii=False)))
    print('   节点名:', [n for _, n in nodes])
    print('   贴图引用:', tex)
    print('   Model mesh:', gim[:4])
    print('   XML 内 fx 路径:', fxpath)
    print('   目标串出现次数:', txt.count(needle.decode()))
json.dump(rep, open(os.path.join(OUT, 'FXSRC_fxgroup_%s.json' % needle.decode().replace('\\', '_')), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n候选 %d 个 → %s' % (len(rep['candidates']), os.path.join(OUT, 'FXSRC_fxgroup_%s.json' % needle.decode())))
