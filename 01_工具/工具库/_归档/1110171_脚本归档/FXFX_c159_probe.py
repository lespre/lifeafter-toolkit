# -*- coding: utf-8 -*-
"""FXFX_c159_probe.py — c159-FxGroup 容器结构探查（第一轮，最小样本 _idle_part_01 2111B / 18 名）。
目标：搞清 header + 名字表 + 载荷编码（tag id / 属性键 id / 值类型），为解码器定型。
"""
import os, struct, json, re, collections

EX = r'E:\la拆包项目\03拆包产物\_target_1110171\FXSRC_exact'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
files = ['sibling_fx_skin_1012_009_idle_part_01.sfx', 'sibling_fx_skin_1012_009_di_low.sfx',
         'sibling_fx_skin_1012_009_idle_01.sfx', 'sibling_fx_skin_1006_004_zishen.sfx']
rep = {}
for fn in files:
    p = os.path.join(EX, fn)
    b = open(p, 'rb').read()
    magic = b[:4].hex()
    size = struct.unpack_from('<I', b, 4)[0]
    zero = struct.unpack_from('<I', b, 8)[0]
    ncount = b[12]
    # 名字表
    pos = 13
    names = []
    for i in range(ncount):
        k = b.find(b'\x00', pos)
        names.append(b[pos:k].decode('latin1', 'replace'))
        pos = k + 1
    payload = b[pos:]
    rep[fn] = {'bytes': len(b), 'magic': magic, 'size_field': size, 'zero_field': zero,
               'name_count': ncount, 'names': names, 'table_end': pos, 'payload_bytes': len(payload),
               'payload_head_hex': payload[:160].hex(),
               'entry_magic_01000113': [m.start() for m in re.finditer(re.escape(b'\x01\x00\x01\x13'), payload)][:10],
               'entry_magic_0100010f': [m.start() for m in re.finditer(re.escape(b'\x01\x00\x01\x0f'), payload)][:10]}
    print('== %s  %dB  magic=%s size=%d zero=%d names=%d table_end=%d payload=%d' % (
        fn, len(b), magic, size, zero, ncount, pos, len(payload)))
    print('   名字表:', names)
    print('   payload head hex:', payload[:160].hex())
    print('   payload head ascii:', re.sub(rb'[^\x20-\x7e]', b'.', payload[:120]))
    print('   \\x01\\x00\\x01\\x13 出现:', rep[fn]['entry_magic_01000113'])
    print('   \\x01\\x00\\x01\\x0f 出现:', rep[fn]['entry_magic_0100010f'])
json.dump(rep, open(os.path.join(OUT, 'FXFX_c159_probe.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\njson ->', os.path.join(OUT, 'FXFX_c159_probe.json'))
