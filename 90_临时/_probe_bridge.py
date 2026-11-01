# -*- coding: utf-8 -*-
"""appear_id_2_equip_id：自包含表（UTF16串区在文件内）。0x76 01 01 索引尾"""
import pathlib, struct, collections, sys
PROJ=pathlib.Path('E:/la拆包项目')
sys.path.insert(0,str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_73 as B73
CD=PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
raw=(CD/'appear_id_2_equip_id.py').read_bytes()
# x{ at 263, len 7792
payload=raw[269:269+7792]
print('payload[0:16]', payload[:16].hex())
# legacy 解析：cnt=u32@0, offsets cnt*4, 然后 blob
cnt=struct.unpack_from('<I',payload,0)[0]
print('cnt', cnt)
if cnt:
    offs=[struct.unpack_from('<I',payload,4+4*i)[0] for i in range(cnt)]
    print('offsets[:8]', offs[:8])
    blob=payload[4+4*cnt:]
    print('blob[0:16]', blob[:16].hex(), 'len', len(blob))
    # schema 在 blob 里
    # 试试 bindict_table 的 read_27_group / schema 解析
    import toolkit_core.bindict_table as BT
    # 字符串池：文件里的 UTF-16 串区
    # 0x20 起是 UTF-16；cnt@0x0C=1280 → 行数
    print('文件头 cnt@0x0C', struct.unpack_from('<I',raw,0x0C)[0])
