# -*- coding: utf-8 -*-
"""反编译weapon_skin_data.nxs并解码编码字符"""
import sys, os, struct, marshal, json, dis, re

skin_path = r'E:\提取成果\拆包产物\_nxs配置\weapon_skin_data.nxs'

with open(skin_path, 'rb') as f:
    raw = f.read()

print('=== 1. 提取marshal数据 ===')
# 前35字节是头部，后面是marshal数据
marshal_data = raw[35:]
print(f'marshal数据大小: {len(marshal_data):,} bytes')

# 尝试加载marshal对象
try:
    root_obj = marshal.loads(marshal_data)
    print(f'根对象类型: {type(root_obj).__name__}')
    print(f'根对象值: {root_obj}')
except Exception as e:
    print(f'加载marshal失败: {e}')

print()

# 递归遍历所有对象，查找code对象
print('=== 2. 递归查找code对象 ===')
def find_code_objects(obj, path='root', depth=0):
    code_objects = []
    if depth > 10:
        return code_objects
    
    obj_type = type(obj).__name__
    
    if obj_type == 'code':
        code_objects.append((path, obj))
        print(f'  找到code对象: {path}')
        print(f'    文件名: {obj.co_filename}')
        print(f'    函数名: {obj.co_name}')
        print(f'    指令数: {len(obj.co_code)}')
        print(f'    常量数: {len(obj.co_consts)}')
        print(f'    变量数: {len(obj.co_varnames)}')
        print(f'    名字数: {len(obj.co_names)}')
    elif obj_type == 'tuple':
        for i, item in enumerate(obj):
            code_objects.extend(find_code_objects(item, f'{path}[{i}]', depth+1))
    elif obj_type == 'list':
        for i, item in enumerate(obj):
            code_objects.extend(find_code_objects(item, f'{path}[{i}]', depth+1))
    elif obj_type == 'dict':
        for k, v in obj.items():
            code_objects.extend(find_code_objects(v, f'{path}[{k}]', depth+1))
    elif hasattr(obj, '__dict__'):
        for k, v in obj.__dict__.items():
            code_objects.extend(find_code_objects(v, f'{path}.{k}', depth+1))
    
    return code_objects

try:
    code_objects = find_code_objects(root_obj)
    print(f'总共找到 {len(code_objects)} 个code对象')
except Exception as e:
    print(f'遍历失败: {e}')

print()

# 尝试逐个加载marshal对象（可能有多个对象）
print('=== 3. 逐个加载marshal对象 ===')
offset = 0
objects = []
while offset < len(marshal_data):
    try:
        obj = marshal.loads(marshal_data[offset:])
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

print(f'找到 {len(objects)} 个marshal对象')
for i, (off, typ, obj, length) in enumerate(objects[:20]):
    val_str = str(obj)[:80]
    print(f'  [{i:2d}] 偏移{off:5d} 长度{length:4d} {typ:10s} = {val_str}')

# 检查是否有code对象
code_objs = [(i, off, obj) for i, (off, typ, obj, length) in enumerate(objects) if typ == 'code']
print(f'\n其中code对象: {len(code_objs)}')
for i, off, obj in code_objs:
    print(f'  [{i}] 偏移{off}: {obj.co_name} in {obj.co_filename}')

print()

# 尝试反汇编code对象
print('=== 4. 反汇编code对象 ===')
for i, off, obj in code_objs[:3]:
    print(f'\n--- code对象[{i}] {obj.co_name} ---')
    print(f'文件名: {obj.co_filename}')
    print(f'指令数: {len(obj.co_code)}')
    print(f'常量: {obj.co_consts}')
    print(f'名字: {obj.co_names}')
    print(f'变量: {obj.co_varnames}')
    print('\n反汇编:')
    try:
        dis.dis(obj)
    except Exception as e:
        print(f'反汇编失败: {e}')

print()

# 用字母表字符串解码编码字符
print('=== 5. 用字母表解码编码字符 ===')

# 提取字母表字符串
alphabet_strings = []
for i, (off, typ, obj, length) in enumerate(objects):
    if typ == 'str' and len(obj) > 3 and obj.isalpha():
        alphabet_strings.append((i, off, obj))
        print(f'  字母表[{i}] 偏移{off}: {repr(obj)}')

# 合并所有字母
all_letters = ''
for i, off, s in alphabet_strings:
    all_letters += s
print(f'\n所有字母: {all_letters}')
print(f'字母总数: {len(all_letters)}')

# 提取编码字符
print('\n提取编码字符序列:')
encoded_chars = []
for i in range(len(raw) - 6):
    if raw[i] == 0x27 and raw[i+1] == 0x01 and raw[i+2] == 0x01:
        char_bytes = raw[i+3:i+6]
        # 作为3个独立的Latin-1字符
        c0 = chr(char_bytes[0])
        c1 = chr(char_bytes[1])
        c2 = chr(char_bytes[2])
        encoded_chars.append((i, c0, c1, c2, char_bytes))

print(f'找到 {len(encoded_chars)} 个编码字符')

# 尝试解码方法1: 第1字符低4位作为字母表索引
print('\n方法1: 第1字符低4位作为索引')
if all_letters:
    decoded1 = []
    for pos, c0, c1, c2, cb in encoded_chars[:50]:
        idx = ord(c0) & 0x0F
        if idx < len(all_letters):
            decoded1.append(all_letters[idx])
        else:
            decoded1.append('?')
    print(f'  解码结果: {"".join(decoded1)}')

# 尝试解码方法2: 第1字符码点-0xC0作为索引
print('\n方法2: 第1字符码点-0xC0作为索引')
if all_letters:
    decoded2 = []
    for pos, c0, c1, c2, cb in encoded_chars[:50]:
        idx = ord(c0) - 0xC0
        if 0 <= idx < len(all_letters):
            decoded2.append(all_letters[idx])
        else:
            decoded2.append('?')
    print(f'  解码结果: {"".join(decoded2)}')

# 尝试解码方法3: 第1字符和第2字符组合作为16位索引
print('\n方法3: 第1+第2字符作为16位索引（低8位）')
if all_letters:
    decoded3 = []
    for pos, c0, c1, c2, cb in encoded_chars[:50]:
        idx = (ord(c0) + ord(c1)) % len(all_letters)
        decoded3.append(all_letters[idx])
    print(f'  解码结果: {"".join(decoded3)}')

# 尝试解码方法4: 直接用第1字符作为替换密码
print('\n方法4: 第1字符替换（Latin-1扩展 -> ASCII）')
latin1_to_ascii = {}
# 建立映射: 0xE0-0xF4 -> a-z, A-Z
ascii_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
for i, cp in enumerate(range(0xE0, 0xE0+len(ascii_chars))):
    if cp <= 0xFF:
        latin1_to_ascii[cp] = ascii_chars[i]

decoded4 = []
for pos, c0, c1, c2, cb in encoded_chars[:50]:
    cp = ord(c0)
    if cp in latin1_to_ascii:
        decoded4.append(latin1_to_ascii[cp])
    else:
        decoded4.append('?')
print(f'  解码结果: {"".join(decoded4)}')

print()

# 分析编码字符的第1字符分布
print('=== 6. 编码字符第1字符分布 ===')
c0_counts = {}
for pos, c0, c1, c2, cb in encoded_chars:
    c0_counts[c0] = c0_counts.get(c0, 0) + 1

sorted_c0 = sorted(c0_counts.items(), key=lambda x: -x[1])
print(f'唯一第1字符数: {len(sorted_c0)}')
for c, count in sorted_c0[:20]:
    cp = ord(c)
    print(f'  {repr(c)} (U+{cp:04X}, 0x{cp:02X}): {count}次, 低4位={cp&0x0F}, -0xC0={cp-0xC0}')

print()

# 分析编码字符的第2字符分布
print('=== 7. 编码字符第2字符分布 ===')
c1_counts = {}
for pos, c0, c1, c2, cb in encoded_chars:
    c1_counts[c1] = c1_counts.get(c1, 0) + 1

sorted_c1 = sorted(c1_counts.items(), key=lambda x: -x[1])
print(f'唯一第2字符数: {len(sorted_c1)}')
for c, count in sorted_c1[:10]:
    cp = ord(c)
    print(f'  {repr(c)} (U+{cp:04X}, 0x{cp:02X}): {count}次')
