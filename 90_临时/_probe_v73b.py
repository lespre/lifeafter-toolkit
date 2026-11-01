# -*- coding: utf-8 -*-
"""appear_id_2_equip_id：0x73 头 + UTF16串区 + 载荷(78 7b) + 0x76索引尾"""
import pathlib, struct, collections, sys
PROJ=pathlib.Path('E:/la拆包项目')
sys.path.insert(0,str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_73 as B73
CD=PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
raw=(CD/'appear_id_2_equip_id.py').read_bytes()
# 找 78 7b 载荷标记
for i in range(len(raw)-6):
    if raw[i]==0x78 and raw[i+1]==0x7b:
        ln=struct.unpack_from('<I',raw,i+2)[0]
        print(f'载荷标记 78 7b @ {i}, len={ln} (文件剩 {len(raw)-i-6})')
        if i+6+ln<=len(raw):
            print('  载荷 head:', raw[i+6:i+6+24].hex())
            print('  载荷尾后:', raw[i+6+ln:i+6+ln+24].hex())
