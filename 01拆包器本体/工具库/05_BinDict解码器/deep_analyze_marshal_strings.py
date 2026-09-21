# -*- coding: utf-8 -*-
"""深度分析weapon_skin_data.nxs的marshal字符串对象"""
import sys, os, struct, marshal, json

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

print(f'总对象数: {len(objects)}')
print()

# 分析所有字符串对象
print('=== 字符串对象详细分析 ===')
str_objects = [(i, off, val) for i, (off, typ, val, length) in enumerate(objects) if typ == 'str']

for idx, (i, off, val) in enumerate(str_objects):
    print(f'\n--- 字符串[{i}] 偏移{off} 长度{len(val)} ---')
    
    # 转换为字节
    try:
        raw_bytes = val.encode('latin-1')
    except:
        raw_bytes = val.encode('utf-8', errors='replace')
    
    print(f'  十六进制（前64字节）: {raw_bytes[:64].hex()}')
    
    # 尝试解析浮点数
    if len(raw_bytes) >= 4:
        floats = []
        for p in range(0, len(raw_bytes) - 4, 4):
            try:
                f = struct.unpack_from('<f', raw_bytes, p)[0]
                if -1000 < f < 10000 and f != 0.0:
                    floats.append((p, f))
            except:
                pass
        if floats:
            print(f'  浮点数（前20个）:')
            for p, f in floats[:20]:
                print(f'    偏移{p}: {f}')
    
    # 尝试解析双精度浮点数
    if len(raw_bytes) >= 8:
        doubles = []
        for p in range(0, len(raw_bytes) - 8, 8):
            try:
                d = struct.unpack_from('<d', raw_bytes, p)[0]
                if -1000 < d < 10000 and d != 0.0:
                    doubles.append((p, d))
            except:
                pass
        if doubles:
            print(f'  双精度浮点数（前10个）:')
            for p, d in doubles[:10]:
                print(f'    偏移{p}: {d}')
    
    # 查找可读ASCII字符串
    import re
    ascii_strings = re.findall(rb'[a-zA-Z_][a-zA-Z0-9_/\\.]{2,}', raw_bytes)
    if ascii_strings:
        print(f'  ASCII字符串: {[s.decode() for s in ascii_strings[:10]]}')
    
    # 查找中文字符（UTF-8）
    try:
        decoded = raw_bytes.decode('utf-8', errors='ignore')
        chinese = re.findall(r'[\u4e00-\u9fff]{2,}', decoded)
        if chinese:
            print(f'  中文字符: {chinese[:10]}')
    except:
        pass

# 分析所有int对象
print()
print('=== int对象分析 ===')
int_objects = [(i, off, val) for i, (off, typ, val, length) in enumerate(objects) if typ == 'int']
print(f'int对象总数: {len(int_objects)}')
for i, off, val in int_objects[:20]:
    print(f'  [{i}] 偏移{off}: {val} (hex: {val & 0xFFFFFFFFFFFFFFFF:016X})')

# 分析所有float对象
print()
print('=== float对象分析 ===')
float_objects = [(i, off, val) for i, (off, typ, val, length) in enumerate(objects) if typ == 'float']
print(f'float对象总数: {len(float_objects)}')
for i, off, val in float_objects[:20]:
    print(f'  [{i}] 偏移{off}: {val}')

# 分析所有complex对象
print()
print('=== complex对象分析 ===')
complex_objects = [(i, off, val) for i, (off, typ, val, length) in enumerate(objects) if typ == 'complex']
print(f'complex对象总数: {len(complex_objects)}')
for i, off, val in complex_objects[:5]:
    print(f'  [{i}] 偏移{off}: {val}')

# 分析对象序列结构
print()
print('=== 对象序列结构（前50个）===')
for i, (off, typ, val, length) in enumerate(objects[:50]):
    val_str = str(val)[:50]
    print(f'  [{i:2d}] 偏移{off:5d} 长度{length:4d} {typ:10s} = {val_str}')
