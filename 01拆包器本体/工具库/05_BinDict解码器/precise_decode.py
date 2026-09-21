# -*- coding: utf-8 -*-
"""精确解码weapon_skin_data.nxs的编码字符"""
import sys, os, struct, marshal, json, re

skin_path = r'E:\提取成果\拆包产物\_nxs配置\weapon_skin_data.nxs'

with open(skin_path, 'rb') as f:
    raw = f.read()

# 提取所有marshal字符串对象
print('=== 1. 提取所有字符串对象 ===')
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

str_objects = [(i, off, val) for i, (off, typ, val, length) in enumerate(objects) if typ == 'str']
print(f'字符串对象数: {len(str_objects)}')

# 查找字母表字符串（包含连续字母的）
print('\n=== 2. 查找字母表字符串 ===')
alphabet_strings = []
for i, off, val in str_objects:
    # 检查是否包含连续的字母序列
    if len(val) >= 3:
        # 检查是否主要由字母组成
        letter_count = sum(1 for c in val if c.isalpha())
        if letter_count >= len(val) * 0.8:
            alphabet_strings.append((i, off, val))
            print(f'  [{i}] 偏移{off}: {repr(val)} (长度{len(val)})')

# 合并字母表
all_letters = ''
for i, off, s in alphabet_strings:
    all_letters += s
print(f'\n合并字母表: {all_letters}')
print(f'字母总数: {len(all_letters)}')
print(f'唯一字母数: {len(set(all_letters))}')

# 提取编码字符
print('\n=== 3. 提取编码字符 ===')
encoded_chars = []
for i in range(len(raw) - 6):
    if raw[i] == 0x27 and raw[i+1] == 0x01 and raw[i+2] == 0x01:
        char_bytes = raw[i+3:i+6]
        c0 = char_bytes[0]
        c1 = char_bytes[1]
        c2 = char_bytes[2]
        encoded_chars.append((i, c0, c1, c2, char_bytes))

print(f'编码字符数: {len(encoded_chars)}')

# 分析第1字符范围
c0_values = sorted(set(ec[1] for ec in encoded_chars))
print(f'第1字符唯一值数: {len(c0_values)}')
print(f'第1字符范围: 0x{c0_values[0]:02X} - 0x{c0_values[-1]:02X}')
print(f'第1字符值: {[f"0x{v:02X}" for v in c0_values]}')

# 分析第2字符范围
c1_values = sorted(set(ec[2] for ec in encoded_chars))
print(f'\n第2字符唯一值数: {len(c1_values)}')
print(f'第2字符值: {[f"0x{v:02X}" for v in c1_values]}')

print()

# 解码方法1: 第1字符 - 最小值 = 字母表索引
print('=== 4. 解码方法1: c0 - min(c0) = 索引 ===')
if all_letters:
    min_c0 = min(c0_values)
    decoded1 = []
    for pos, c0, c1, c2, cb in encoded_chars:
        idx = c0 - min_c0
        if 0 <= idx < len(all_letters):
            decoded1.append(all_letters[idx])
        else:
            decoded1.append('?')
    result1 = ''.join(decoded1)
    print(f'  解码结果: {result1}')
    # 查找可读单词
    words = re.findall(r'[a-zA-Z]{3,}', result1)
    if words:
        print(f'  可读单词: {words}')

print()

# 解码方法2: 第1字符低6位 = 索引
print('=== 5. 解码方法2: c0 & 0x3F = 索引 ===')
if all_letters:
    decoded2 = []
    for pos, c0, c1, c2, cb in encoded_chars:
        idx = c0 & 0x3F
        if 0 <= idx < len(all_letters):
            decoded2.append(all_letters[idx])
        else:
            decoded2.append('?')
    result2 = ''.join(decoded2)
    print(f'  解码结果: {result2}')
    words = re.findall(r'[a-zA-Z]{3,}', result2)
    if words:
        print(f'  可读单词: {words}')

print()

# 解码方法3: 第1字符 - 0x87 = 索引
print('=== 6. 解码方法3: c0 - 0x87 = 索引 ===')
if all_letters:
    decoded3 = []
    for pos, c0, c1, c2, cb in encoded_chars:
        idx = c0 - 0x87
        if 0 <= idx < len(all_letters):
            decoded3.append(all_letters[idx])
        else:
            decoded3.append('?')
    result3 = ''.join(decoded3)
    print(f'  解码结果: {result3}')
    words = re.findall(r'[a-zA-Z]{3,}', result3)
    if words:
        print(f'  可读单词: {words}')

print()

# 解码方法4: 第1字符和第2字符组合 = 索引
print('=== 7. 解码方法4: (c0 - min) * 3 + c1_group = 索引 ===')
if all_letters:
    min_c0 = min(c0_values)
    # c1分组: 0xAE=0, 0xAF=1, 0xB0=2
    c1_group_map = {0xAE: 0, 0xAF: 1, 0xB0: 2}
    decoded4 = []
    for pos, c0, c1, c2, cb in encoded_chars:
        c0_idx = c0 - min_c0
        c1_group = c1_group_map.get(c1, 0)
        idx = c0_idx * 3 + c1_group
        if 0 <= idx < len(all_letters):
            decoded4.append(all_letters[idx])
        else:
            decoded4.append('?')
    result4 = ''.join(decoded4)
    print(f'  解码结果: {result4}')
    words = re.findall(r'[a-zA-Z]{3,}', result4)
    if words:
        print(f'  可读单词: {words}')

print()

# 解码方法5: 直接建立映射表（基于频率分析）
print('=== 8. 解码方法5: 频率分析映射 ===')
# 统计编码字符频率
c0_c1_counts = {}
for pos, c0, c1, c2, cb in encoded_chars:
    key = (c0, c1)
    c0_c1_counts[key] = c0_c1_counts.get(key, 0) + 1

sorted_pairs = sorted(c0_c1_counts.items(), key=lambda x: -x[1])
print(f'唯一(c0,c1)组合数: {len(sorted_pairs)}')
print('前20个高频组合:')
for (c0, c1), count in sorted_pairs[:20]:
    print(f'  (0x{c0:02X}, 0x{c1:02X}): {count}次')

# 英文字母频率（从高到低）
english_freq = 'etaoinshrdlcumwfgypbvkjxqz'
print(f'\n英文字母频率: {english_freq}')

# 建立映射
if len(sorted_pairs) >= 26:
    freq_map = {}
    for i, ((c0, c1), count) in enumerate(sorted_pairs[:26]):
        freq_map[(c0, c1)] = english_freq[i]
    
    decoded5 = []
    for pos, c0, c1, c2, cb in encoded_chars:
        key = (c0, c1)
        if key in freq_map:
            decoded5.append(freq_map[key])
        else:
            decoded5.append('?')
    result5 = ''.join(decoded5)
    print(f'\n频率分析解码结果: {result5}')
    words = re.findall(r'[a-zA-Z]{3,}', result5)
    if words:
        print(f'可读单词: {words}')

print()

# 保存编码字符序列供后续分析
print('=== 9. 保存编码字符序列 ===')
output_data = {
    'alphabet': all_letters,
    'encoded_chars': [
        {'pos': pos, 'c0': c0, 'c1': c1, 'c2': c2, 'hex': cb.hex()}
        for pos, c0, c1, c2, cb in encoded_chars
    ],
    'c0_values': c0_values,
    'c1_values': c1_values,
}

output_path = r'E:\提取成果\明日拆包\工具库\05_BinDict解码器\encoded_chars_analysis.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)
print(f'已保存到: {output_path}')
