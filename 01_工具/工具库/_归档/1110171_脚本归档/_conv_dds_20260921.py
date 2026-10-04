# -*- coding: utf-8 -*-
import os, sys, json
sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\06_皮肤定位链')
D = r'E:\la拆包项目\03拆包产物\_target_1110171\crystal_tex_located_20260921'
import dds_rgba_canonical as DD
from PIL import Image
p = os.path.join(D,'refraction_envmap_3.dds')
u8, meta = None, None
try:
    r = DD.decode_dds_rgba_u8(p, verify_oiio=False)
    print('返回类型:', type(r).__name__, '长度:' , len(r) if hasattr(r,'__len__') else '?')
    if isinstance(r, tuple):
        u8, meta = r[0], (r[1] if len(r)>1 else None)
    else:
        u8 = r
except Exception as e:
    print('decode_dds_rgba_u8 失败:', repr(e)[:250])
    u8 = None
if u8 is not None:
    try:
        hdr = DD.parse_header(open(p,'rb').read(160)) if hasattr(DD,'parse_header') else None
        print('头信息:', hdr)
        import numpy as np
        a = np.frombuffer(bytes(u8), dtype=np.uint8)
        # 尝试推断尺寸：从 meta 或头
        w = h = None
        if isinstance(meta, dict):
            w, h = meta.get('width') or meta.get('w'), meta.get('height') or meta.get('h')
        if (w is None or h is None) and isinstance(hdr, dict):
            w, h = hdr.get('width'), hdr.get('height')
        print('尺寸推断:', w, h, '| 元素数:', a.size)
        if w and h and a.size == w*h*4:
            img = Image.fromarray(a.reshape(h, w, 4), 'RGBA')
        else:
            # 16x16 启发：先按正方形试
            import math
            n = a.size // 4; s = int(math.isqrt(n))
            img = Image.fromarray(a[:s*s*4].reshape(s, s, 4), 'RGBA') if s*s*4 == a.size else None
            print('按正方形回退:', s if img else '失败')
        if img:
            out = os.path.join(D, 'refraction_envmap_3.png')
            img.save(out)
            print('★ 已保存:', out, img.size, img.mode)
    except Exception as e:
        print('转换失败:', repr(e)[:250])
