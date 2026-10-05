# -*- coding: utf-8 -*-
"""FXSRC_hash_probe.py — ① c159 里 1.4462 是否出现（anchor 溯源）② 路径→idx_hash 哈希函数验证（贴图精确化）
只读。"""
import os, re, json, struct, hashlib, collections

PACK = r'E:\la拆包项目\03拆包产物'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
C159 = os.path.join(PACK, 'weapon', '001209.c159')
rep = {}

# ---------- ① c159：所有可解释的 float，找 1.4462 ----------
b = open(C159, 'rb').read()
targets = [1.4462, 1.446, 2.4424, 2.0263, 1.8291, 0.447, 3.2]
found = collections.defaultdict(list)
for off in range(0, len(b) - 4):
    v = struct.unpack_from('<f', b, off)[0]
    if v != v or abs(v) > 1e4:
        continue
    for t in targets:
        if abs(v - t) < 0.002:
            found[t].append((off, round(v, 6)))
rep['c159_float_hits'] = {str(k): v[:8] for k, v in found.items()}
print('== c159 中目标浮点出现位置（±0.002）==')
for t in targets:
    print('   %-8s %s' % (t, found.get(t, [])[:8]))
# 每个具名 socket 后的 16 float
names = [{'off': m.start(), 'name': m.group().decode('latin1')}
         for m in re.finditer(rb'[\x20-\x7e]{3,}', b)]
named = []
for nm in names:
    if re.fullmatch(r'(fx_|bag|hongwai|sound|muzzle_fire|pifuguashi|rotation)[\w]*', nm['name']):
        st = nm['off'] + len(nm['name'])
        # 跳过 0x00 与 4-8 字节头，找第一个 16-float 合法块
        for s in range(st, min(st + 24, len(b) - 64)):
            v = list(struct.unpack_from('<16f', b, s))
            if all(abs(x) < 1e4 and x == x for x in v) and any(abs(x - 1.0) < 1e-6 for x in v):
                named.append({'name': nm['name'], 'name_off': nm['off'], 'mat_off': s,
                              'matrix': [round(float(x), 5) for x in v],
                              'translation_rowmajor_4th_col': [round(v[3], 5), round(v[7], 5), round(v[11], 5)],
                              'translation_last3': [round(v[12], 5), round(v[13], 5), round(v[14], 5)]})
                break
rep['c159_named_transforms'] = named
print('== c159 具名 socket 的 4x4 ==')
for n in named:
    print('   %-14s @%4d  平移(4th col)=%s  平移(v12-14)=%s' % (n['name'], n['name_off'], n['translation_rowmajor_4th_col'], n['translation_last3']))

# ---------- ② 路径 → idx_hash 哈希函数验证 ----------
idx = json.load(open(os.path.join(PACK, 'render_1003_010', '_sfx_010', 'effect_texture_pool.json'), encoding='utf-8'))
hashes = set(e['idx_hash'] for e in idx['entries'])
rep['idx_hash_count'] = len(hashes)
print('\n== idx_hash 集合 %d 个（effect.idx）' % len(hashes))
tex_paths = [
    'effect\\textures\\glow\\glow_01.tga', 'effect\\textures\\lightning\\lightning07_cs.spr',
    'effect\\textures\\lightning\\lightning1_rzx_djs.spr', 'effect\\textures\\glow\\ray_01_sk.tga',
    'effect\\textures\\glow\\glow_16_yh_djs.tga', 'effect\\textures\\glow\\glow_26_tp37.tga',
    'effect\\textures\\glow\\dian_12.tga', 'effect\\textures\\glow\\glow_02_sk2.tga',
    'effect\\textures\\glow\\glow10_d.tga', 'effect\\textures\\glow\\glow_tp25_08.tga',
    'effect\\textures\\glow\\tex_glow_xr_03_cc.tga',
]
variants = []
for p in tex_paths:
    cand = set()
    for sep in ('\\', '/'):
        q = p.replace('\\', sep)
        for case in (q, q.lower(), q.upper()):
            cand.add(case)
            cand.add('res/' + case.replace('\\', '/'))
            cand.add(os.path.splitext(case)[0])
            cand.add(os.path.basename(case))
            cand.add(os.path.basename(os.path.splitext(case)[0]))
    variants.append((p, sorted(cand)))
hits = {}
tested = 0
for p, cand in variants:
    for c in cand:
        for enc in ('utf-8', 'utf-16-le', 'latin1'):
            try:
                bb = c.encode(enc)
            except Exception:
                continue
            for alg in ('md5', 'sha1', 'sha256', 'sha512'):
                h = hashlib.new(alg, bb).hexdigest()
                tested += 1
                if h in hashes or h[:32] in hashes:
                    hits.setdefault(p, []).append({'variant': c, 'alg': alg, 'enc': enc, 'hash': h[:32]})
                # 常见变体：末尾加 \0
                h2 = hashlib.new(alg, bb + b'\x00').hexdigest()
                tested += 1
                if h2 in hashes or h2[:32] in hashes:
                    hits.setdefault(p, []).append({'variant': c + '\\0', 'alg': alg, 'enc': enc, 'hash': h2[:32]})
rep['hash_probe'] = {'tested': tested, 'hits': hits, 'texture_paths': tex_paths}
print('   哈希尝试次数 %d，命中 %d' % (tested, len(hits)))
for p, hh in hits.items():
    print('   HIT %s -> %s' % (p, hh[:3]))
if not hits:
    print('   ⇒ 无命中：路径→idx_hash 的哈希函数在 md5/sha1/sha256/sha512 × utf-8/utf-16/latin1 × 斜杠/大小写/扩展名 变体下均未验证成功')
# 反向：idx_hash 是否像 md5（16 字节）——长度/分布
print('   idx_hash 长度分布:', collections.Counter(len(h) for h in hashes))
json.dump(rep, open(os.path.join(OUT, 'FXSRC_hash_probe.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('json ->', os.path.join(OUT, 'FXSRC_hash_probe.json'))
