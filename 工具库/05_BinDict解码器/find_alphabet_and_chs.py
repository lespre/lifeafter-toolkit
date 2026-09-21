# -*- coding: utf-8 -*-
"""直接在原始字节中查找字母表，检查配套CHS文件"""
import sys, os, struct, re, glob

skin_path = r'E:\提取成果\拆包产物\_nxs配置\weapon_skin_data.nxs'
nxs_dir = r'E:\提取成果\拆包产物\_nxs配置'

with open(skin_path, 'rb') as f:
    raw = f.read()

print('=== 1. 直接在原始字节中查找字母表字符串 ===')
# 查找连续的字母序列（至少5个）
patterns = [
    rb'[a-z]{5,}',
    rb'[A-Z]{5,}',
    rb'[a-zA-Z]{5,}',
]

for pattern in patterns:
    matches = re.findall(pattern, raw)
    if matches:
        print(f'模式 {pattern}:')
        for m in matches[:20]:
            print(f'  {m.decode()}')

print()

# 查找特定的字母表
print('=== 2. 查找特定字母表 ===')
specific_alphabets = [
    b'hijklmnopqr',
    b'ABCDEF',
    b'GHIJK',
    b'LMNPQRSTUVWXYZ',
    b'abcdefghijklmnopqrstuvwxyz',
    b'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
]

for alpha in specific_alphabets:
    pos = raw.find(alpha)
    if pos >= 0:
        print(f'找到 {alpha.decode()} at 偏移{pos}')
        # 查看上下文
        context = raw[max(0,pos-10):pos+len(alpha)+20]
        print(f'  上下文: {context}')
    else:
        print(f'未找到 {alpha.decode()}')

print()

# 查找所有可读字符串（长度>=4）
print('=== 3. 所有可读ASCII字符串（长度>=4）===')
all_strings = re.findall(rb'[a-zA-Z_][a-zA-Z0-9_/\\.]{3,}', raw)
print(f'找到 {len(all_strings)} 个字符串')
for s in all_strings:
    print(f'  {s.decode()}')

print()

# 检查配套CHS文件
print('=== 4. 检查配套CHS文件 ===')
nxs_files = glob.glob(os.path.join(nxs_dir, '*.nxs'))
print(f'nxs目录下文件数: {len(nxs_files)}')
for f in nxs_files:
    size = os.path.getsize(f)
    print(f'  {os.path.basename(f)}: {size:,} bytes')

# 特别查找weapon_skin相关文件
print('\n查找weapon_skin相关文件:')
weapon_files = [f for f in nxs_files if 'weapon_skin' in os.path.basename(f).lower()]
for f in weapon_files:
    size = os.path.getsize(f)
    print(f'  {os.path.basename(f)}: {size:,} bytes')

print()

# 分析301个编码字符的结构
print('=== 5. 分析301个编码字符结构 ===')
encoded_chars = []
for i in range(len(raw) - 6):
    if raw[i] == 0x27 and raw[i+1] == 0x01 and raw[i+2] == 0x01:
        char_bytes = raw[i+3:i+6]
        encoded_chars.append((i, char_bytes))

print(f'编码字符数: {len(encoded_chars)}')

# 按位置排序
encoded_chars.sort(key=lambda x: x[0])

# 检查位置是否连续
print('\n位置分布:')
positions = [pos for pos, cb in encoded_chars]
print(f'  最小位置: {positions[0]}')
print(f'  最大位置: {positions[-1]}')
print(f'  位置范围: {positions[-1] - positions[0]}')

# 检查间隔
gaps = []
for i in range(1, len(positions)):
    gap = positions[i] - positions[i-1]
    gaps.append(gap)
print(f'  平均间隔: {sum(gaps)/len(gaps):.1f}')
print(f'  最小间隔: {min(gaps)}')
print(f'  最大间隔: {max(gaps)}')

# 检查是否有6字节连续的编码字符
print('\n检查连续编码字符（间隔=6）:')
consecutive = 0
max_consecutive = 0
for i in range(1, len(positions)):
    if positions[i] - positions[i-1] == 6:
        consecutive += 1
        max_consecutive = max(max_consecutive, consecutive)
    else:
        consecutive = 0
print(f'  最大连续编码字符数: {max_consecutive + 1}')

print()

# 分析编码字符的字节值分布
print('=== 6. 编码字符字节值分布 ===')
# 第1字节
b0_values = [cb[0] for pos, cb in encoded_chars]
b0_unique = sorted(set(b0_values))
print(f'第1字节唯一值数: {len(b0_unique)}')
print(f'第1字节范围: 0x{b0_unique[0]:02X} - 0x{b0_unique[-1]:02X}')
# 统计主要范围
ranges = [(0x00, 0x1F), (0x20, 0x3F), (0x40, 0x5F), (0x60, 0x7F), 
          (0x80, 0x9F), (0xA0, 0xBF), (0xC0, 0xDF), (0xE0, 0xFF)]
for start, end in ranges:
    count = sum(1 for v in b0_values if start <= v <= end)
    if count > 0:
        print(f'  0x{start:02X}-0x{end:02X}: {count}个')

# 第2字节
b1_values = [cb[1] for pos, cb in encoded_chars]
b1_unique = sorted(set(b1_values))
print(f'\n第2字节唯一值数: {len(b1_unique)}')
for v in b1_unique:
    count = b1_values.count(v)
    print(f'  0x{v:02X} ({chr(v) if 32<=v<127 else "?"}): {count}个')

# 第3字节
b2_values = [cb[2] for pos, cb in encoded_chars]
b2_unique = sorted(set(b2_values))
print(f'\n第3字节唯一值数: {len(b2_unique)}')
for v in b2_unique:
    count = b2_values.count(v)
    print(f'  0x{v:02X} ({chr(v) if 32<=v<127 else "?"}): {count}个')

print()

# 尝试将3字节作为小端整数
print('=== 7. 3字节作为小端整数 ===')
int_values = []
for pos, cb in encoded_chars:
    val = cb[0] | (cb[1] << 8) | (cb[2] << 16)
    int_values.append((pos, val))

print(f'整数值范围: {min(v for _,v in int_values):,} - {max(v for _,v in int_values):,}')
print(f'前20个整数值:')
for pos, val in int_values[:20]:
    print(f'  偏移{pos}: {val:,} (0x{val:06X})')

# 检查是否是递增的
print('\n检查是否递增:')
is_increasing = all(int_values[i][1] < int_values[i+1][1] for i in range(len(int_values)-1))
print(f'  完全递增: {is_increasing}')

# 检查是否有排序
sorted_vals = sorted(v for _, v in int_values)
is_sorted = sorted_vals == [v for _, v in int_values]
print(f'  已排序: {is_sorted}')
