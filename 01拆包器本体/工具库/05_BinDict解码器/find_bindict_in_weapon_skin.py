# -*- coding: utf-8 -*-
"""在weapon_skin_data.nxs中查找BinDict特征标记"""
import sys, os, struct, zlib, json

skin_path = r'E:\提取成果\拆包产物\_nxs配置\weapon_skin_data.nxs'

with open(skin_path, 'rb') as f:
    raw = f.read()

print(f'文件大小: {len(raw):,} bytes')
print()

# 1. 查找x{标记
print('=== 1. 查找x{标记 ===')
x_positions = []
for i in range(len(raw) - 2):
    if raw[i] == 0x78 and raw[i+1] == 0x7B:  # x{
        x_positions.append(i)
print(f'找到 {len(x_positions)} 个x{{标记')
for pos in x_positions[:10]:
    # 读取后面的长度
    if pos + 6 <= len(raw):
        length = struct.unpack_from('<I', raw, pos+2)[0]
        print(f'  偏移{pos}: 声明长度={length},  fits={pos+6+length <= len(raw)}')
        print(f'    后续16字节: {raw[pos:pos+22].hex()}')

# 2. 查找CHS字符串池特征（<II>头 + 递增偏移量表）
print()
print('=== 2. 查找CHS字符串池特征 ===')
for offset in range(0, min(200, len(raw))):
    if offset + 8 > len(raw):
        break
    count, reserved = struct.unpack_from('<II', raw, offset)
    if reserved != 0 or count == 0 or count > 10000:
        continue
    table_end = offset + 8 + count * 4
    if table_end > len(raw):
        continue
    offsets = struct.unpack_from(f'<{count}I', raw, offset+8)
    # 检查偏移量是否递增且合理
    if offsets[0] <= 0 or offsets[-1] > len(raw) - table_end:
        continue
    valid = True
    for i in range(1, count):
        if offsets[i] <= offsets[i-1]:
            valid = False
            break
    if not valid:
        continue
    # 检查最后一个偏移是否等于数据区大小
    data_size = len(raw) - table_end
    if offsets[-1] != data_size:
        continue
    # 尝试解码字符串
    try:
        strings = []
        last = 0
        for off in offsets:
            s = raw[table_end+last:table_end+off].decode('utf-8', strict=True)
            strings.append(s)
            last = off
        print(f'  偏移{offset}: 找到CHS字符串池! count={count}')
        print(f'    前10个字符串: {strings[:10]}')
        print(f'    后10个字符串: {strings[-10:]}')
        break
    except:
        continue

# 3. 尝试zlib解压（从不同偏移量）
print()
print('=== 3. 尝试zlib解压 ===')
for offset in range(0, min(200, len(raw))):
    try:
        decompressed = zlib.decompress(raw[offset:])
        print(f'  偏移{offset}: zlib解压成功! 大小={len(decompressed)}')
        print(f'    头部64字节: {decompressed[:64].hex()}')
        # 查找可读字符串
        import re
        ascii_strings = re.findall(rb'[a-zA-Z_][a-zA-Z0-9_/\\.]{3,}', decompressed)
        if ascii_strings:
            print(f'    ASCII字符串（前10）: {[s.decode() for s in ascii_strings[:10]]}')
        break
    except:
        pass

# 4. 尝试AES解密（使用gpk相同的KEY）
print()
print('=== 4. 尝试AES解密 ===')
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
KEY = bytes([0x60,0x63,0x08,0xD8,0xA3,0x2C,0x78,0x20,0x13,0xD2,0x6C,0x2F,0x22,0x6F,0x68,0x6D])

for offset in [0, 6, 35, 36]:
    if offset + 16 > len(raw):
        continue
    data = raw[offset:]
    pad = (16 - len(data) % 16) % 16
    padded = data + b'\x00' * pad
    try:
        dec = Cipher(algorithms.AES(KEY), modes.ECB()).decryptor()
        decrypted = dec.update(padded) + dec.finalize()
        # 检查是否有可读内容
        if b'x{' in decrypted or b'bindict' in decrypted.lower() or b'weapon' in decrypted.lower():
            print(f'  偏移{offset}: AES解密后找到特征!')
            print(f'    头部64字节: {decrypted[:64].hex()}')
            # 查找x{
            x_pos = decrypted.find(b'x{')
            if x_pos >= 0:
                print(f'    x{{位置: {x_pos}')
            break
    except:
        pass

# 5. 分析marshal对象中的字符串，尝试提取BinDict数据
print()
print('=== 5. 分析marshal字符串对象中的BinDict特征 ===')
import marshal
offset = 35
objects = []
while offset < len(raw):
    try:
        obj = marshal.loads(raw[offset:])
        try:
            serialized = marshal.dumps(obj)
            obj_len = len(serialized)
        except:
            obj_len = 0
        objects.append((offset, type(obj).__name__, obj, obj_len))
        if obj_len > 0:
            offset += obj_len
        else:
            offset += 1
    except:
        offset += 1

# 查找包含x{或BinDict特征的字符串对象
for i, (off, typ, val, length) in enumerate(objects):
    if typ == 'str' and len(val) > 10:
        # 检查是否包含x{标记
        if 'x{' in val or 'bindict' in val.lower() or 'weapon' in val.lower():
            print(f'  对象[{i}] 偏移{off}: 找到特征! 长度={len(val)}')
            print(f'    前100字符: {repr(val[:100])}')
        # 检查是否是UTF-8编码的BinDict数据
        try:
            raw_bytes = val.encode('latin-1')
            if b'x{' in raw_bytes:
                x_pos = raw_bytes.find(b'x{')
                print(f'  对象[{i}] 偏移{off}: latin-1编码后找到x{{! 位置={x_pos}')
                print(f'    后续32字节: {raw_bytes[x_pos:x_pos+32].hex()}')
        except:
            pass

# 6. 查看所有字符串对象的长度分布
print()
print('=== 6. 字符串对象长度分布 ===')
str_objects = [(i, off, val) for i, (off, typ, val, length) in enumerate(objects) if typ == 'str']
print(f'字符串对象总数: {len(str_objects)}')
for i, off, val in str_objects:
    print(f'  [{i}] 偏移{off}: 长度={len(val)}, 前20字节={repr(val[:20])}')
