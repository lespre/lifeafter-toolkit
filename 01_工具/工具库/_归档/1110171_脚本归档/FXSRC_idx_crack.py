# -*- coding: utf-8 -*-
"""FXSRC_idx_crack.py — 用已知对（fx_skin_1003_010_zs_02.sfx ↔ effect_01.gpk frame14761 offset 22173392 size 83327）
反推 effect.idx 的 16 字节 idx_hash 哈希函数；成功后即可精确算出 1012_009 / 1006_004 的 fx 帧位置。
只读源；输出写 _target_1110171\\FXSRC_idx_crack.json
"""
import os, re, json, struct, hashlib, glob, itertools

PACK = r'E:\la拆包项目\03拆包产物'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
IDX = sorted(glob.glob(os.path.join(PACK, 'source_snapshots', '*', '**', 'effect.idx'), recursive=True))
IDX = max(IDX, key=os.path.getmtime)
d = open(IDX, 'rb').read()
rep = {'idx': IDX, 'bytes': len(d)}
print('== effect.idx %s %dB' % (IDX, len(d)))
print('   head:', d[:64].hex())

# ---- 在 idx 里找已知的 offset/size ----
KNOWN = {'path': 'effect\\fx\\weapon\\skin\\skin_1003_010\\fx_skin_1003_010_zs_02.sfx',
         'frame': 14761, 'offset': 22173392, 'size': 83327}
pats = {'offset_u32': struct.pack('<I', KNOWN['offset']), 'size_u32': struct.pack('<I', KNOWN['size']),
        'size_u32b': struct.pack('<I', KNOWN['size'] + 4), 'offset_u32b': struct.pack('<I', KNOWN['offset'])}
found = {}
for k, p in pats.items():
    pos = []
    i = d.find(p)
    while i >= 0 and len(pos) < 8:
        pos.append(i)
        i = d.find(p, i + 1)
    found[k] = pos
rep['known_pattern_hits'] = found
print('   已知 offset/size 在 idx 中的位置:', json.dumps(found))

# ---- 解析 idx 条目（magic SKPW + ...）----
rep['entries_parsed'] = None
cand_hashes = []
# 先按 16 字节哈希 + 后续字段的启发式扫描：寻找 32 hex 长度模式
hexpat = re.compile(rb'[0-9a-f]{32}')
allh = [m.group().decode() for m in hexpat.finditer(d)]
rep['hex32_count_in_idx'] = len(allh)
print('   idx 中 32-hex 串数量:', len(allh))

# 若 offset 命中，取其前 16 字节（或附近）作为该条目的哈希
near = []
for k, pos in found.items():
    for p in pos:
        for back in (16, 20, 24, 28, 32):
            if p - back >= 0:
                h = d[p - back:p - back + 16]
                near.append({'pattern': k, 'pos': p, 'back': back, 'hash_hex': h.hex()})
rep['near_hashes'] = near
print('   邻近 16 字节哈希候选:', json.dumps(near[:8], ensure_ascii=False))

# ---- 尝试哈希函数 × 路径变体 ----
path = KNOWN['path']
variants = set()
for sep in ('\\', '/'):
    q = path.replace('\\', sep)
    for case in (q, q.lower(), q.upper()):
        variants.add(case)
        variants.add(os.path.splitext(case)[0])
        variants.add(case + '\x00')
        variants.add('res/' + case.replace('\\', '/'))
        variants.add('Documents/res/' + case.replace('\\', '/'))
        variants.add('effect/' + os.path.basename(case))
hexset = set(allh)
rep['hash_attempts'] = 0
rep['hash_match'] = None
algs = ['md5', 'sha1', 'sha256', 'sha512', 'blake2b', 'blake2s', 'sha3_256']
for v in sorted(variants):
    for enc in ('utf-8', 'utf-16-le', 'gbk', 'latin1'):
        try:
            bb = v.encode(enc)
        except Exception:
            continue
        for alg in algs:
            try:
                h = hashlib.new(alg, bb).hexdigest()
            except Exception:
                continue
            rep['hash_attempts'] += 1
            if h[:32] in hexset:
                rep['hash_match'] = {'variant': v, 'enc': enc, 'alg': alg, 'hash': h[:32]}
                print('   ★★ 命中: %s (%s/%s) -> %s' % (v, enc, alg, h[:32]))
                break
        if rep['hash_match']:
            break
    if rep['hash_match']:
        break
if not rep['hash_match']:
    print('   × 未命中：%d 次尝试（%d 变体 × 4 编码 × 7 算法）' % (rep['hash_attempts'], len(variants)))
    # 打印该文件里的哈希样例，便于人工比对
    print('   idx 中样例哈希:', allh[:5])
    import hashlib as H
    print('   对已知路径的常见哈希:')
    for alg in ('md5', 'sha1', 'sha256'):
        print('      %-7s utf8     %s' % (alg, H.new(alg, path.encode()).hexdigest()[:32]))
        print('      %-7s lower    %s' % (alg, H.new(alg, path.lower().encode()).hexdigest()[:32]))
        print('      %-7s slash    %s' % (alg, H.new(alg, path.replace('\\', '/').encode()).hexdigest()[:32]))
    # 反向：已知路径的 md5 是否出现在 idx 任何位置
    for alg in ('md5', 'sha1'):
        for name, bb in (('utf8', path.encode()), ('lower', path.lower().encode()),
                         ('slash', path.replace('\\', '/').encode()), ('basename', os.path.basename(path).encode())):
            hh = H.new(alg, bb).hexdigest()
            print('      in-idx? %s %s = %s' % (alg, name, d.find(hh.encode()) >= 0 or d.find(bytes.fromhex(hh)) >= 0))
json.dump(rep, open(os.path.join(OUT, 'FXSRC_idx_crack.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('json ->', os.path.join(OUT, 'FXSRC_idx_crack.json'))
