# -*- coding: utf-8 -*-
from pathlib import Path
import struct

out_dir = Path(r'E:\提取成果\拆包产物\gres_0058')

print('=== 深入分析 000097.bin (armor/weapon) ===')
print()

f = out_dir / '000097.bin'
print('文件:', f.name)
print('大小:', f.stat().st_size, 'bytes')
print()

with open(f, 'rb') as fh:
    data = fh.read()

# 打印头部
print('头部(256字节):')
print('  HEX:', data[:256].hex())
print('  ASCII:', ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[:256]))
print()

# 搜索所有可打印字符串
print('可打印字符串(长度>4):')
strings = []
current = ''
for i, b in enumerate(data):
    if 32 <= b < 127:
        current += chr(b)
    else:
        if len(current) > 4:
            strings.append((i - len(current), current))
        current = ''
if len(current) > 4:
    strings.append((len(data) - len(current), current))

for offset, s in strings:
    print('  偏移', offset, ':', s)

print()
print('共找到', len(strings), '个字符串')

print()
print('=== 分析其他大的bin文件 ===')
print()

# 分析前10个最大的bin文件
bin_files = sorted(out_dir.glob('*.bin'), key=lambda x: x.stat().st_size, reverse=True)
for f in bin_files[:10]:
    print('文件:', f.name, '大小:', f.stat().st_size, 'bytes')
    with open(f, 'rb') as fh:
        data = fh.read()
    
    # 搜索字符串
    strings = []
    current = ''
    for b in data:
        if 32 <= b < 127:
            current += chr(b)
        else:
            if len(current) > 4:
                strings.append(current)
            current = ''
    if len(current) > 4:
        strings.append(current)
    
    if strings:
        print('  字符串:', strings[:10])
    print()
