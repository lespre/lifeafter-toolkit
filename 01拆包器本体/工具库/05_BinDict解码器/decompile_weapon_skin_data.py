# -*- coding: utf-8 -*-
"""反编译weapon_skin_data.nxs的Python字节码"""
import sys, os, struct, marshal, dis, re

skin_path = r'E:\提取成果\拆包产物\_nxs配置\weapon_skin_data.nxs'

with open(skin_path, 'rb') as f:
    raw = f.read()

print(f'文件大小: {len(raw):,} bytes')
print()

# 分析文件结构
print('=== 文件结构分析 ===')
# 前4字节
print(f'偏移0-3: {raw[:4].hex()}')
# 找路径字符串结束位置
path_end = raw.find(b'.py') + 3
print(f'路径字符串: {raw[6:path_end]}')
print(f'路径结束偏移: {path_end}')

# 路径后面的字节
print(f'路径后16字节: {raw[path_end:path_end+16].hex()}')

# 尝试找Python code object的魔数
# Python 3.11的magic number是 0xA70D (3.11) 或 0xCB0D (3.11a)
# Python 3.10是 0x6F0D
# Python 3.9是 0x610D
print()
print('=== 搜索Python magic number ===')
for offset in range(0, min(100, len(raw))):
    magic = struct.unpack_from('<H', raw, offset)[0]
    if magic in (0xA70D, 0xCB0D, 0x6F0D, 0x610D, 0x550D, 0x4F0D):
        print(f'  偏移{offset}: magic=0x{magic:04X} (可能是Python字节码)')

# 尝试用不同偏移量marshal加载
print()
print('=== 尝试marshal加载 ===')
for offset in [0, 4, 6, path_end, path_end+1, path_end+4, path_end+5, path_end+8, path_end+12]:
    if offset >= len(raw):
        continue
    try:
        code = marshal.loads(raw[offset:])
        print(f'  偏移{offset}: 成功! 类型={type(code).__name__}')
        if hasattr(code, 'co_consts'):
            print(f'    co_consts数量: {len(code.co_consts)}')
            print(f'    co_names数量: {len(code.co_names)}')
            print(f'    co_names: {code.co_names[:20]}')
            # 打印常量
            for i, c in enumerate(code.co_consts[:20]):
                if isinstance(c, str) and len(c) < 100:
                    print(f'    const[{i}]: {c}')
                elif isinstance(c, (int, float)):
                    print(f'    const[{i}]: {c}')
                elif hasattr(c, 'co_consts'):
                    print(f'    const[{i}]: <code object {c.co_name}>')
        break
    except Exception as e:
        pass

# 如果marshal失败，尝试直接反汇编原始字节
print()
print('=== 直接字节码分析（从路径结束后开始）===')
# 找LOAD_CONST操作码后面的字符串常量
bytecode_start = path_end + 5  # 跳过路径和一些头部
print(f'从偏移{bytecode_start}开始分析')
code_bytes = raw[bytecode_start:]

# 尝试找字符串常量（在Python字节码中，字符串前面通常有长度前缀）
print()
print('=== 搜索字符串常量 ===')
strings_found = []
i = 0
while i < len(code_bytes) - 4:
    # 尝试小端uint32作为长度
    length = struct.unpack_from('<I', code_bytes, i)[0]
    if 1 < length < 200 and i + 4 + length <= len(code_bytes):
        potential_str = code_bytes[i+4:i+4+length]
        try:
            s = potential_str.decode('utf-8')
            if all(32 <= ord(c) < 127 or 0x4e00 <= ord(c) <= 0x9fff for c in s):
                if len(s) > 2:
                    strings_found.append((bytecode_start + i, length, s))
        except:
            pass
    i += 1

print(f'找到 {len(strings_found)} 个可能的字符串常量:')
for offset, length, s in strings_found[:50]:
    print(f'  偏移{offset} (长度{length}): {s[:80]}')

# 搜索中文
print()
print('=== 搜索中文字符串 ===')
chinese_strings = re.findall(rb'[\xe4-\xe9][\x80-\xbf][\x80-\xbf]{2,}', raw)
print(f'找到 {len(chinese_strings)} 个中文字符串片段')
for s in list(set(chinese_strings))[:30]:
    try:
        print(f'  {s.decode("utf-8")}')
    except:
        pass
