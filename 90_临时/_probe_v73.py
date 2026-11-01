# -*- coding: utf-8 -*-
"""0x73 新变体解析：head + UTF16串区 + 0x76索引尾
appear_id_2_equip_id.py 8505 字节，0x76 01 01 在 281"""
import pathlib, struct, collections, sys
PROJ=pathlib.Path('E:/la拆包项目')
sys.path.insert(0,str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_73 as B73
CD=PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
raw=(CD/'appear_id_2_equip_id.py').read_bytes()
# 0x76 01 01 at 281；其前 4 字节应是 blob 长度（de）
de=281
blob_len=struct.unpack_from('<I',raw,de-4)[0]
print('de',de,'blob_len',blob_len)
# blob 起点？ 0x76 索引尾前的 u32 就是 de
# 试：blob = raw[? : de]，de 是 blob 长度
for cand in (de, len(raw)-de):
    pass
# 从头找：0x73 头 0x20 后是 UTF16 串区（cnt@0x0C=1280 行）
# 串区长度：从 0x20 起直到遇到 0x76 前
# 先看 0x76 前的字节
print('before 0x76:', raw[de-24:de].hex())
print('0x76+:', raw[de:de+40].hex())
# 试 parse_index_73 需要 data[de]==0x76 且 data[0:4] 是 u32 长度
# 构造：blob = 载荷(从某处到 de+索引尾)
# 先猜载荷起点：0x20 + str区长度。找 str 区结束：UTF16 串以 0000 0000 结尾
# 从 de 往前找连续的 0000
i=de-4
zeros=0
while i>0 and raw[i]==0 and raw[i-1]==0:
    zeros+=2; i-=2
print('0x76 前连续零字节数', zeros)
str_end=de-4-zeros
print('推测 str 区结束 @', str_end)
# 载荷起点 = str_end + 4（一个 u32）
payload_start=str_end+4
print('payload_start', payload_start, 'payload_len', de-payload_start)
print('payload head:', raw[payload_start:payload_start+32].hex())
