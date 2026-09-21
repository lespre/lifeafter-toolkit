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

gres_dir = Path(r'E:\mrzh\Documents\gres')

print('=== GRES包快速扫描（0053~0057） ===')
print()

for i in range(53, 58):
    fname = f'{i:04d}.gpk'
    f = gres_dir / fname
    if not f.exists():
        print(f'{fname}: 不存在')
        continue
    
    size_mb = round(f.stat().st_size / 1024 / 1024, 2)
    mtime = f.stat().st_mtime
    
    with open(f, 'rb') as fh:
        header = fh.read(256)
    
    decrypted = aes_ecb_decrypt(header)
    
    # 检查magic
    magics = []
    for offset in range(0, 64, 4):
        magic = decrypted[offset:offset+4]
        try:
            magic_str = magic.decode('ascii')
            if magic_str.isalpha() and len(magic_str) == 4:
                magics.append(f'偏移{offset}:{magic_str}')
        except:
            pass
    
    # 尝试解析条目数（不同偏移）
    entry_counts = []
    for offset in [16, 20, 24, 28, 32, 36, 40, 44, 48]:
        try:
            val = struct.unpack_from('<I', decrypted, offset)[0]
            if 100 < val < 100000:
                entry_counts.append(f'偏移{offset}:{val}')
        except:
            pass
    
    print(f'{fname}: {size_mb} MB, 修改时间:{mtime}')
    print(f'  Magic: {", ".join(magics)}')
    print(f'  可能条目数: {", ".join(entry_counts)}')
    print()

print('=== 对比：res目录下的GPK包 ===')
print()

res_dir = Path(r'E:\mrzh\res')
for fname in ['ui_01.gpk', 'weapon.gpk', 'character_05.gpk']:
    f = res_dir / fname
    if not f.exists():
        continue
    
    size_mb = round(f.stat().st_size / 1024 / 1024, 2)
    
    with open(f, 'rb') as fh:
        header = fh.read(256)
    
    decrypted = aes_ecb_decrypt(header)
    
    magics = []
    for offset in range(0, 64, 4):
        magic = decrypted[offset:offset+4]
        try:
            magic_str = magic.decode('ascii')
            if magic_str.isalpha() and len(magic_str) == 4:
                magics.append(f'偏移{offset}:{magic_str}')
        except:
            pass
    
    entry_counts = []
    for offset in [16, 20, 24, 28, 32]:
        try:
            val = struct.unpack_from('<I', decrypted, offset)[0]
            if 100 < val < 1000000:
                entry_counts.append(f'偏移{offset}:{val}')
        except:
            pass
    
    print(f'{fname}: {size_mb} MB')
    print(f'  Magic: {", ".join(magics)}')
    print(f'  条目数: {", ".join(entry_counts)}')
    print()
