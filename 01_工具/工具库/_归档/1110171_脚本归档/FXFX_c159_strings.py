# -*- coding: utf-8 -*-
"""FXFX_c159_strings.py — 判定 c159-FxGroup 内值是否为明文串（决定解码路径），并用已知项交叉验证身份。
核查项：贴图逻辑名、SfxName 值、节点名（如 L_空特效）、PosOffset 等。
"""
import os, re, json, struct

EX = r'E:\la拆包项目\03拆包产物\_target_1110171\FXSRC_exact'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
CANDS = {
    'sibling_fx_skin_1012_009_idle_01.sfx': [b'idle_part_01', b'idle_part_02', b'glow25', b'tex_ring_keji',
                                             b'heitiane_04', b'skin_1012_009', b'L_', b'FxGroup', b'MyFx'],
    'sibling_fx_skin_1006_004_zishen.sfx': [b'skin_1006_004', b'glow', b'FxGroup', b'MyFx'],
}
rep = {}
for fn, needles in CANDS.items():
    b = open(os.path.join(EX, fn), 'rb').read()
    print('== %s %dB' % (fn, len(b)))
    hits = {}
    for nd in needles:
        pos = [m.start() for m in re.finditer(re.escape(nd), b)][:5]
        hits[nd.decode()] = pos
        if pos:
            print('   %-16s @ %s' % (nd.decode(), pos))
            print('        上下文: %s' % re.sub(rb'[^\x20-\x7e]', b'.', b[max(0, pos[0] - 24):pos[0] + 40]))
    # 全部可打印串（>=4）统计
    strs = [m.group().decode('latin1') for m in re.finditer(rb'[\x20-\x7e]{4,}', b)]
    print('   可打印串(>=4) 总数 %d，样例 %s' % (len(strs), strs[:14]))
    # 是否有 UTF-16LE 明文（中文字节对）
    u16 = re.findall((b'(?:[\x20-\x7e]\x00){4,}'), b)
    print('   UTF-16LE 串样例:', [x[:40] for x in u16[:4]])
    rep[fn] = {'bytes': len(b), 'hits': hits, 'n_ascii_strings': len(strs), 'ascii_sample': strs[:20],
               'utf16_sample': [x.decode('utf-16-le', 'replace') for x in u16[:6]]}
json.dump(rep, open(os.path.join(OUT, 'FXFX_c159_strings.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('json ->', os.path.join(OUT, 'FXFX_c159_strings.json'))
