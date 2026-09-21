# -*- coding: utf-8 -*-
from pathlib import Path
import struct
from Crypto.Cipher import AES

AES_KEY = bytes.fromhex('606308D8A32C782013D26C2F226F686D')

def aes_ecb_decrypt(data):
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    padded_len = (len(data) // 16) * 16
    if padded_len == 0:
        return data
    return cipher.decrypt(data[:padded_len])

def ascii_str(data):
    return ''.join(chr(b) if 32 <= b < 127 else '.' for b in data)

f = Path(r'E:\mrzh\Documents\gres\0058.gpk')
print('文件:', f.name)
print('大小:', round(f.stat().st_size / 1024 / 1024, 2), 'MB')

with open(f, 'rb') as fh:
    header = fh.read(256)

print()
print('原始头部(前64字节):')
print('  HEX:', header[:64].hex())
print('  ASCII:', ascii_str(header[:64]))

# 尝试解密
decrypted = aes_ecb_decrypt(header)
print()
print('解密后头部(前64字节):')
print('  HEX:', decrypted[:64].hex())
print('  ASCII:', ascii_str(decrypted[:64]))

# 检查各种magic
print()
print('Magic检查:')
for offset in range(0, 32, 4):
    magic = decrypted[offset:offset+4]
    print('  偏移', offset, ':', magic.hex(), '=', magic)

# 尝试解析条目数
print()
print('尝试解析条目数:')
for offset in [16, 20, 24, 28, 32, 36, 40]:
    try:
        val = struct.unpack_from('<I', decrypted, offset)[0]
        print('  偏移', offset, ':', val)
    except:
        pass

# 检查原始头部的magic（不解密）
print()
print('原始头部Magic检查:')
for offset in range(0, 32, 4):
    magic = header[offset:offset+4]
    print('  偏移', offset, ':', magic.hex(), '=', magic)
