# -*- coding: utf-8 -*-
"""直接分析weapon_skin_data.nxs原始字节，解码编码字符串"""
import sys, os, struct, json, re

skin_path = r'E:\提取成果\拆包产物\_nxs配置\weapon_skin_data.nxs'

with open(skin_path, 'rb') as f:
    raw = f.read()

print(f'文件大小: {len(raw):,} bytes')
print()

# 直接在原始字节中查找 27 01 01 模式
print('=== 1. 查找 27 01 01 模式 ===')
pattern_positions = []
for i in range(len(raw) - 6):
    if raw[i] == 0x27 and raw[i+1] == 0x01 and raw[i+2] == 0x01:
        char_bytes = raw[i+3:i+6]
        pattern_positions.append((i, char_bytes))

print(f'找到 {len(pattern_positions)} 个 27 01 01 模式')
print()

# 分析字符字节
print('=== 2. 字符字节分析 ===')
char_bytes_list = [cb for _, cb in pattern_positions]
char_counts = {}
for cb in char_bytes_list:
    key = cb.hex()
    char_counts[key] = char_counts.get(key, 0) + 1

sorted_chars = sorted(char_counts.items(), key=lambda x: -x[1])
print(f'唯一字符字节数: {len(sorted_chars)}')
print('前30个高频字符:')
for cb_hex, count in sorted_chars[:30]:
    cb = bytes.fromhex(cb_hex)
    try:
        c = cb.decode('utf-8')
        cp = ord(c)
        print(f'  {cb_hex} = {repr(c)} (U+{cp:04X}): {count}次')
    except:
        print(f'  {cb_hex} (无法解码): {count}次')

print()

# 分析码点范围
print('=== 3. 码点范围分析 ===')
codepoints = []
for cb_hex, count in sorted_chars:
    cb = bytes.fromhex(cb_hex)
    try:
        c = cb.decode('utf-8')
        codepoints.append(ord(c))
    except:
        pass

if codepoints:
    print(f'最小码点: U+{min(codepoints):04X}')
    print(f'最大码点: U+{max(codepoints):04X}')
    print(f'码点范围: {max(codepoints) - min(codepoints)}')
    
    # 检查连续范围
    ranges = []
    sorted_cps = sorted(codepoints)
    current_start = sorted_cps[0]
    current_end = sorted_cps[0]
    for cp in sorted_cps[1:]:
        if cp == current_end + 1:
            current_end = cp
        else:
            ranges.append((current_start, current_end))
            current_start = cp
            current_end = cp
    ranges.append((current_start, current_end))
    print(f'连续范围数: {len(ranges)}')
    for start, end in ranges:
        print(f'  U+{start:04X} - U+{end:04X} ({end-start+1}个字符)')

print()

# 尝试解码方法
print('=== 4. 尝试解码方法 ===')

# 方法1: 简单偏移
if codepoints:
    base = min(codepoints)
    print(f'方法1: 偏移解码 (base=U+{base:04X})')
    decoded = [cp - base for cp in codepoints]
    print(f'  解码后索引范围: {min(decoded)} - {max(decoded)}')
    print(f'  所有索引: {sorted(decoded)}')

print()

# 方法2: 分析字节结构
print('方法2: 分析3字节结构')
for cb_hex, count in sorted_chars[:10]:
    cb = bytes.fromhex(cb_hex)
    b0, b1, b2 = cb[0], cb[1], cb[2]
    print(f'  {cb_hex}: b0=0x{b0:02X}, b1=0x{b1:02X}, b2=0x{b2:02X}')
    print(f'    b0低4位={b0&0x0F}, b1低4位={b1&0x0F}, b2低4位={b2&0x0F}')
    print(f'    b0-0xC0={b0-0xC0}, b1-0x80={b1-0x80}, b2-0x40={b2-0x40}')

print()

# 方法3: UTF-8编码分析
print('方法3: UTF-8编码分析')
# 3字节UTF-8: 1110xxxx 10xxxxxx 10xxxxxx
# 码点 = ((b0 & 0x0F) << 12) | ((b1 & 0x3F) << 6) | (b2 & 0x3F)
for cb_hex, count in sorted_chars[:5]:
    cb = bytes.fromhex(cb_hex)
    b0, b1, b2 = cb[0], cb[1], cb[2]
    cp = ((b0 & 0x0F) << 12) | ((b1 & 0x3F) << 6) | (b2 & 0x3F)
    print(f'  {cb_hex}: 码点=U+{cp:04X}, 字符={chr(cp) if cp < 0x110000 else "?"}')
    # 提取各部分
    part1 = (b0 & 0x0F)
    part2 = (b1 & 0x3F)
    part3 = (b2 & 0x3F)
    print(f'    part1={part1} (0x{part1:02X}), part2={part2} (0x{part2:02X}), part3={part3} (0x{part3:02X})')

print()

# 提取完整的编码序列
print('=== 5. 提取完整编码序列 ===')
# 按位置排序
pattern_positions.sort(key=lambda x: x[0])

# 提取前200个编码字符
print('前200个编码字符序列:')
sequence = []
for i, (pos, cb) in enumerate(pattern_positions[:200]):
    try:
        c = cb.decode('utf-8')
        sequence.append(c)
        if i % 20 == 0:
            print()
            print(f'  [{i:3d}] ', end='')
        print(f'{c}', end=' ')
    except:
        sequence.append('?')
        if i % 20 == 0:
            print()
            print(f'  [{i:3d}] ', end='')
        print('?', end=' ')

print()
print()

# 分析序列中的重复模式
print('=== 6. 序列重复模式分析 ===')
if len(sequence) > 10:
    # 查找重复的2字符模式
    patterns_2 = {}
    for i in range(len(sequence) - 1):
        pat = (sequence[i], sequence[i+1])
        patterns_2[pat] = patterns_2.get(pat, 0) + 1
    common_2 = sorted(patterns_2.items(), key=lambda x: -x[1])[:10]
    print('常见2字符模式:')
    for pat, count in common_2:
        print(f'  {pat}: {count}次')
    
    print()
    # 查找重复的4字符模式
    patterns_4 = {}
    for i in range(len(sequence) - 3):
        pat = tuple(sequence[i:i+4])
        patterns_4[pat] = patterns_4.get(pat, 0) + 1
    common_4 = sorted(patterns_4.items(), key=lambda x: -x[1])[:10]
    print('常见4字符模式:')
    for pat, count in common_4:
        if count > 1:
            print(f'  {pat}: {count}次')

print()

# 分析上下文（编码字符前后的字节）
print('=== 7. 编码字符上下文分析 ===')
for i, (pos, cb) in enumerate(pattern_positions[:5]):
    context_start = max(0, pos - 10)
    context_end = min(len(raw), pos + 16)
    context = raw[context_start:context_end]
    print(f'位置{pos}: 上下文{context.hex()}')
    print(f'  前10字节: {raw[context_start:pos].hex()}')
    print(f'  编码字符: {cb.hex()}')
    print(f'  后10字节: {raw[pos+6:pos+16].hex()}')
    print()
