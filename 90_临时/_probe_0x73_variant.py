# -*- coding: utf-8 -*-
"""0x73 变体格式：head(0x73) + UTF16 串区 + 0x76 索引尾 + 载荷
appear_id_2_equip_id.py 用的就是这个（x{ 在 263，cnt=0，说明不是 legacy x{ 容器）"""
import pathlib, struct, collections, sys
PROJ=pathlib.Path('E:/la拆包项目')
CD=PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
raw=(CD/'appear_id_2_equip_id.py').read_bytes()
# 找 0x76 01 01（索引尾）
i=raw.find(b'\x76\x01\x01')
print('0x76 01 01 at', i)
# 载荷起点：0x73 头之后的表头区
# 观察：bytes 0..0x1F 是头，0x20 起是 UTF-16 串区
print('head:', raw[:0x20].hex())
# 试：0x73 头后 4 字节是 count，再 4 字节是长度
cnt=struct.unpack_from('<I',raw,0x0C)[0]
ln=struct.unpack_from('<I',raw,0x10)[0]
print('cnt@0x0C',cnt,'len@0x10',ln)
str_start=0x20
print('str区结束 =', str_start+ln, '→ hex', raw[str_start+ln-8:str_start+ln].hex())
print('该处往后:', raw[str_start+ln:str_start+ln+32].hex())
