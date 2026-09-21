# -*- coding: utf-8 -*-
"""用lifeafter_unpacker_full.py中的函数解析weapon_skin_data.nxs"""
import sys, os, json, struct

sys.path.insert(0, r'E:\提取成果\明日拆包\工具库\01_核心解包器')
import lifeafter_unpacker_full as unpacker

skin_path = r'E:\提取成果\拆包产物\_nxs配置\weapon_skin_data.nxs'

print('=== 1. 读取weapon_skin_data.nxs原始内容 ===')
with open(skin_path, 'rb') as f:
    raw = f.read()
print(f'文件大小: {len(raw):,} bytes')
print(f'头部128字节: {raw[:128].hex()}')

# 尝试找可读字符串
print()
print('=== 2. 提取可读字符串 ===')
import re
# ASCII字符串
ascii_strings = re.findall(rb'[a-zA-Z_][a-zA-Z0-9_/\\.]{3,}', raw)
print(f'ASCII字符串: {len(ascii_strings)}个')
for s in list(set(ascii_strings))[:30]:
    print(f'  {s.decode("ascii", errors="ignore")}')

# 尝试用decrypt_nxs
print()
print('=== 3. 尝试decrypt_nxs ===')
try:
    decrypted = unpacker.decrypt_nxs(skin_path)
    print(f'解密后大小: {len(decrypted):,} bytes')
    print(f'解密后头部64字节: {decrypted[:64].hex()}')
    # 尝试找可读字符串
    ascii_strings2 = re.findall(rb'[a-zA-Z_][a-zA-Z0-9_/\\.]{3,}', decrypted)
    print(f'解密后ASCII字符串: {len(ascii_strings2)}个')
    for s in list(set(ascii_strings2))[:20]:
        print(f'  {s.decode("ascii", errors="ignore")}')
except Exception as e:
    print(f'decrypt_nxs失败: {e}')

# 尝试用parse_bindict_chs
print()
print('=== 4. 尝试parse_bindict_chs ===')
try:
    result = unpacker.parse_bindict_chs(raw)
    print(f'解析结果类型: {type(result).__name__}')
    if isinstance(result, dict):
        print(f'键: {list(result.keys())[:20]}')
    elif isinstance(result, list):
        print(f'长度: {len(result)}')
        if result:
            print(f'第一个元素: {str(result[0])[:200]}')
    else:
        print(f'结果: {str(result)[:500]}')
except Exception as e:
    print(f'parse_bindict_chs失败: {e}')
    import traceback
    traceback.print_exc()

# 尝试用parse_bindict_xbrace
print()
print('=== 5. 尝试parse_bindict_xbrace ===')
try:
    result = unpacker.parse_bindict_xbrace(raw)
    print(f'解析结果类型: {type(result).__name__}')
    if isinstance(result, dict):
        print(f'键: {list(result.keys())[:20]}')
    elif isinstance(result, list):
        print(f'长度: {len(result)}')
        if result:
            print(f'第一个元素: {str(result[0])[:200]}')
    else:
        print(f'结果: {str(result)[:500]}')
except Exception as e:
    print(f'parse_bindict_xbrace失败: {e}')

# 尝试用extract_nxs_text
print()
print('=== 6. 尝试extract_nxs_text ===')
try:
    text = unpacker.extract_nxs_text(skin_path)
    print(f'提取文本长度: {len(text)}')
    print(f'文本前500字符: {text[:500]}')
except Exception as e:
    print(f'extract_nxs_text失败: {e}')

# 直接分析文件格式
print()
print('=== 7. 直接分析文件格式 ===')
# 前4字节可能是魔数
magic = raw[:4]
print(f'前4字节: {magic.hex()} = {magic}')
# 接下来4字节可能是长度
if len(raw) >= 8:
    size1 = struct.unpack_from('<I', raw, 4)[0]
    size2 = struct.unpack_from('>I', raw, 4)[0]
    print(f'偏移4小端uint32: {size1}')
    print(f'偏移4大端uint32: {size2}')
# 找路径字符串的位置
path_pos = raw.find(b'com\\cdata\\weapon_skin_data')
print(f'路径字符串位置: {path_pos}')
if path_pos >= 0:
    print(f'路径字符串前16字节: {raw[path_pos-16:path_pos].hex()}')
    print(f'路径字符串: {raw[path_pos:path_pos+50]}')
