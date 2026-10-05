# -*- coding: utf-8 -*-
"""FXSRC_anchor_tex.py — (a) 从 weapon/001209.c159 读出 fx_idle_01 的 16 float 挂点
                        (b) 解析 effect.idx 路径表 → 精确解析 .sfx 的 Texture 逻辑路径（替代候选）
只读；输出写 03拆包产物\\_target_1110171\\FXSRC_*。
"""
import os, re, struct, json, glob, collections

PACK = r'E:\la拆包项目\03拆包产物'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
C159 = os.path.join(PACK, 'weapon', '001209.c159')
rep = {}

# ---------------- (a) c159 ----------------
b = open(C159, 'rb').read()
rep['c159'] = {'path': C159, 'bytes': len(b)}
print('== c159 %s %dB' % (C159, len(b)))
print('   hex head  :', b[:180].hex())
print('   ascii 串  :', re.findall(rb'[\x20-\x7e]{4,}', b)[:20])
i = b.find(b'fx_idle_01')
print('   fx_idle_01 @ %d' % i)
if i >= 0:
    seg = b[i:i + 140]
    print('   该处原始 hex:', seg.hex())
    print('   该处 ascii  :', re.sub(rb'[^\x20-\x7e]', b'.', seg))
    # 找 16 连续 float（值域合理：|v|<1000，非 NaN）
    best = None
    for start in range(i + 10, min(i + 120, len(b) - 64) + 1):
        try:
            v = list(struct.unpack_from('<16f', b, start))
        except Exception:
            continue
        if all(abs(x) < 1000 and x == x for x in v):
            best = (start, v)
            break
    if best:
        st, v = best
        rep['c159']['f32x16'] = {'offset': st, 'values': [round(float(x), 5) for x in v]}
        print('   ★ 16 float @ %d（marker+%d）:' % (st, st - i))
        for r in range(4):
            print('      [%s]' % '  '.join('%12.5f' % v[r * 4 + c] for c in range(4)))
        print('      平移分量 (row-major 第4列) = [%.5f, %.5f, %.5f]' % (v[3], v[7], v[11]))
        print('      平移分量 (column-major 第13-15) = [%.5f, %.5f, %.5f]' % (v[12], v[13], v[14]))
    else:
        # 退而求其次：4 float
        for start in range(i + 10, min(i + 120, len(b) - 16) + 1):
            v = list(struct.unpack_from('<4f', b, start))
            if all(abs(x) < 1000 and x == x for x in v):
                rep['c159']['f32x4'] = {'offset': start, 'values': [round(float(x), 5) for x in v]}
                print('   ★ 4 float @ %d（marker+%d）: %s' % (start, start - i, [round(x, 4) for x in v]))
                break
# 全文件所有字符串 + 位置
rep['c159']['strings'] = [{'off': m.start(), 's': m.group().decode('latin1')} for m in re.finditer(rb'[\x20-\x7e]{3,}', b)]
print('   全部可打印串:'); 
for s in rep['c159']['strings']:
    print('      %5d  %s' % (s['off'], s['s']))

# ---------------- (b) effect.idx ----------------
idxs = sorted(glob.glob(os.path.join(PACK, 'source_snapshots', '*', '**', 'effect.idx'), recursive=True))
rep['effect_idx_candidates'] = idxs
print('\n== effect.idx 候选 %d 个' % len(idxs))
if idxs:
    p = max(idxs, key=os.path.getmtime)
    d = open(p, 'rb').read()
    rep['effect_idx'] = {'path': p, 'bytes': len(d)}
    print('   %s  %dB  mtime=%s' % (p, len(d), os.path.getmtime(p)))
    print('   head hex:', d[:96].hex())
    for needle in (b'glow_01.tga', b'effect\\textures', b'fx_skin_1003_010', b'1003_010'):
        j = d.find(needle)
        print('   needle %-20s @ %s' % (needle, j))
    strs = [{'off': m.start(), 's': m.group().decode('latin1')} for m in re.finditer(rb'[\x20-\x7e]{4,}', d)]
    rep['effect_idx']['n_strings'] = len(strs)
    rep['effect_idx']['strings_sample'] = strs[:40]
    print('   可打印串数量:', len(strs))
    for s in strs[:25]:
        print('      %7d  %s' % (s['off'], s['s'][:100]))
    hit = [s for s in strs if 'glow_01' in s['s'] or 'textures' in s['s'].lower()]
    print('   含 texture/glow_01 的串:', len(hit))
    for s in hit[:15]:
        print('      %7d  %s' % (s['off'], s['s'][:120]))
    rep['effect_idx']['texture_strings'] = hit[:40]
json.dump(rep, open(os.path.join(OUT, 'FXSRC_anchor_tex.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\njson ->', os.path.join(OUT, 'FXSRC_anchor_tex.json'))
