# -*- coding: utf-8 -*-
"""解码weapon_skin_data.nxs中的编码字符串"""
import sys, os, struct, marshal, json, re

skin_path = r'E:\提取成果\拆包产物\_nxs配置\weapon_skin_data.nxs'

with open(skin_path, 'rb') as f:
    raw = f.read()

# 加载所有marshal对象
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

# 提取所有字符串对象
str_objects = [(i, off, val) for i, (off, typ, val, length) in enumerate(objects) if typ == 'str']

print('=== 1. 提取所有编码字符串模式 ===')
# 模式: 27 01 01 XX YY ZZ (3字节UTF-8字符)
encoded_strings = []
for idx, (i, off, val) in enumerate(str_objects):
    raw_bytes = val.encode('latin-1')
    # 查找 27 01 01 模式
    pos = 0
    while pos < len(raw_bytes) - 5:
        if raw_bytes[pos] == 0x27 and raw_bytes[pos+1] == 0x01 and raw_bytes[pos+2] == 0x01:
            # 读取后面的3字节
            char_bytes = raw_bytes[pos+3:pos+6]
            try:
                char = char_bytes.decode('utf-8')
                encoded_strings.append({
                    'obj_index': i,
                    'obj_offset': off,
                    'pos': pos,
                    'char_bytes': char_bytes.hex(),
                    'char': char,
                    'char_codepoint': ord(char)
                })
            except:
                pass
            pos += 6
        else:
            pos += 1

print(f'找到 {len(encoded_strings)} 个编码字符')
print()

# 分析字符分布
print('=== 2. 字符分布分析 ===')
char_counts = {}
for es in encoded_strings:
    c = es['char']
    char_counts[c] = char_counts.get(c, 0) + 1

# 按频率排序
sorted_chars = sorted(char_counts.items(), key=lambda x: -x[1])
print(f'唯一字符数: {len(sorted_chars)}')
print('前30个高频字符:')
for c, count in sorted_chars[:30]:
    print(f'  {repr(c)} (U+{ord(c):04X}): {count}次')

print()

# 分析字符的码点范围
print('=== 3. 码点范围分析 ===')
codepoints = [ord(c) for c, _ in sorted_chars]
print(f'最小码点: U+{min(codepoints):04X} ({chr(min(codepoints))})')
print(f'最大码点: U+{max(codepoints):04X} ({chr(max(codepoints))})')
print(f'码点范围: {max(codepoints) - min(codepoints)}')

# 检查是否是连续范围
ranges = []
current_start = codepoints[0]
current_end = codepoints[0]
for cp in sorted(codepoints)[1:]:
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

# 尝试解码方法1: 简单偏移
print('=== 4. 尝试解码方法 ===')
print('方法1: 简单偏移 (codepoint - base)')
base = min(codepoints)
decoded_method1 = []
for es in encoded_strings:
    idx = ord(es['char']) - base
    decoded_method1.append(idx)
print(f'  偏移基数: U+{base:04X}')
print(f'  解码后索引范围: {min(decoded_method1)} - {max(decoded_method1)}')
print(f'  前50个索引: {decoded_method1[:50]}')

print()

# 尝试解码方法2: XOR
print('方法2: XOR 0x80')
decoded_method2 = []
for es in encoded_strings:
    cp = ord(es['char'])
    decoded = cp ^ 0x80
    decoded_method2.append(decoded)
print(f'  解码后范围: {min(decoded_method2)} - {max(decoded_method2)}')
# 尝试作为ASCII
ascii_chars = []
for d in decoded_method2[:100]:
    if 32 <= d < 127:
        ascii_chars.append(chr(d))
    else:
        ascii_chars.append(f'[{d}]')
print(f'  前100个ASCII: {"".join(ascii_chars)}')

print()

# 尝试解码方法3: 查表 (Latin-1扩展区 -> ASCII)
print('方法3: Latin-1字符 -> ASCII映射')
# 观察: à=0xE0, â=0xE2, ð=0xF0, é=0xE9, á=0xE1, è=0xE8
# 这些字符的低4位可能是索引
latin1_to_ascii = {}
for c, count in sorted_chars:
    cp = ord(c)
    # 尝试多种映射
    low_nibble = cp & 0x0F
    high_nibble = (cp >> 4) & 0x0F
    latin1_to_ascii[c] = {
        'cp': cp,
        'low_nibble': low_nibble,
        'high_nibble': high_nibble,
        'cp_minus_0xC0': cp - 0xC0,
        'cp_minus_0xE0': cp - 0xE0,
    }

print('  字符映射表（前20个）:')
for c, count in sorted_chars[:20]:
    info = latin1_to_ascii[c]
    print(f'    {repr(c)} (U+{info["cp"]:04X}): low={info["low_nibble"]}, high={info["high_nibble"]}, -0xC0={info["cp_minus_0xC0"]}, -0xE0={info["cp_minus_0xE0"]}')

print()

# 尝试按对象分组解码
print('=== 5. 按对象分组解码 ===')
for idx, (i, off, val) in enumerate(str_objects):
    raw_bytes = val.encode('latin-1')
    # 提取该对象中的所有编码字符
    chars_in_obj = [es for es in encoded_strings if es['obj_index'] == i]
    if not chars_in_obj:
        continue
    
    print(f'\n--- 对象[{i}] 偏移{off} 长度{len(val)} ({len(chars_in_obj)}个编码字符) ---')
    
    # 方法1: 偏移解码
    base = min(ord(es['char']) for es in chars_in_obj)
    decoded = [ord(es['char']) - base for es in chars_in_obj]
    print(f'  偏移解码(base=U+{base:04X}): {decoded[:50]}')
    
    # 方法2: 尝试作为字符索引
    # 检查是否有重复模式
    if len(decoded) > 10:
        # 查找重复的4字节模式
        patterns = {}
        for j in range(len(decoded) - 3):
            pat = tuple(decoded[j:j+4])
            patterns[pat] = patterns.get(pat, 0) + 1
        common_patterns = sorted(patterns.items(), key=lambda x: -x[1])[:5]
        if common_patterns[0][1] > 1:
            print(f'  常见4元组: {common_patterns}')

print()

# 分析完整的字节结构（不仅仅是编码字符）
print('=== 6. 完整字节结构分析 ===')
for idx, (i, off, val) in enumerate(str_objects):
    if len(val) < 50:
        continue
    raw_bytes = val.encode('latin-1')
    print(f'\n--- 对象[{i}] 偏移{off} 长度{len(val)} ---')
    print(f'  前100字节hex: {raw_bytes[:100].hex()}')
    print(f'  前100字节repr: {repr(raw_bytes[:100])}')
    
    # 查找非编码字符部分
    # 编码字符模式是 27 01 01 XX YY ZZ
    # 其他部分可能是控制字节或数据
    pos = 0
    segments = []
    current_segment = b''
    while pos < len(raw_bytes):
        if pos + 5 < len(raw_bytes) and raw_bytes[pos] == 0x27 and raw_bytes[pos+1] == 0x01 and raw_bytes[pos+2] == 0x01:
            if current_segment:
                segments.append(('data', current_segment))
                current_segment = b''
            char_bytes = raw_bytes[pos:pos+6]
            segments.append(('encoded_char', char_bytes))
            pos += 6
        else:
            current_segment += bytes([raw_bytes[pos]])
            pos += 1
    if current_segment:
        segments.append(('data', current_segment))
    
    print(f'  段数: {len(segments)}')
    print(f'  前10段:')
    for seg_type, seg_data in segments[:10]:
        if seg_type == 'encoded_char':
            try:
                c = seg_data[3:6].decode('utf-8')
                print(f'    [编码字符] {repr(c)} (U+{ord(c):04X})')
            except:
                print(f'    [编码字符] {seg_data.hex()}')
        else:
            print(f'    [数据] {len(seg_data)}字节: {seg_data[:20].hex()}')
