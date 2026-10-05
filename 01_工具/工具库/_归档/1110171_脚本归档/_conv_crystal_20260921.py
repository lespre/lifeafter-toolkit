# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\06_皮肤定位链')
D = r'E:\la拆包项目\03拆包产物\_target_1110171\crystal_tex_located_20260921'
from PIL import Image
for f in ['crystal_bump_n_uvva.tga','crystal_caustic_uvva.tga','crystal_reflection_uvva.tga']:
    im = Image.open(os.path.join(D,f))
    print(f, im.mode, im.size, '→', os.path.join(D, f.replace('.tga','.png')))
    im.convert('RGBA').save(os.path.join(D, f.replace('.tga','.png')))
# DDS：用工具库的规范解码器（BC 系列禁 convert('RGB')）
try:
    import dds_rgba_canonical as DDS
    print('已加载 dds_rgba_canonical')
    res = DDS.decode_file(os.path.join(D,'refraction_envmap_3.dds')) if hasattr(DDS,'decode_file') else None
    print('decode_file:', type(res).__name__ if res is not None else '无 decode_file 接口')
except Exception as e:
    print('dds_rgba_canonical 直接调用失败:', repr(e)[:200]); res=None
    # 回退：PIL 试读
    try:
        im = Image.open(os.path.join(D,'refraction_envmap_3.dds'))
        print('PIL 读 DDS:', im.mode, im.size)
        im.convert('RGBA').save(os.path.join(D,'refraction_envmap_3.png'))
    except Exception as e2:
        print('PIL 也失败:', repr(e2)[:200])
