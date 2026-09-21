# -*- coding: utf-8 -*-
"""检查weapon_skin_data.nxs是否包含BinDict子组件"""
import sys, os, struct, json, zlib, re

skin_path = r'E:\提取成果\拆包产物\_nxs配置\weapon_skin_data.nxs'

with open(skin_path, 'rb') as f:
    raw = f.read()

print(f'文件大小: {len(raw):,} bytes')
print()

# 1. 查找CHS字符串池特征（<II>头 + 递增偏移量表）
print('=== 1. 查找CHS字符串池 ===')
chs_pools = []
for offset in range(0, len(raw) - 8):
    count, reserved = struct.unpack_from('<II', raw, offset)
    if reserved != 0 or count == 0 or count > 5000:
        continue
    table_end = offset + 8 + count * 4
    if table_end > len(raw):
        continue
    offsets = struct.unpack_from(f'<{count}I', raw, offset+8)
    # 检查偏移量是否递增
    if offsets[0] <= 0:
        continue
    valid = True
    for i in range(1, count):
        if offsets[i] <= offsets[i-1]:
            valid = False
            break
    if not valid:
        continue
    # 检查最后一个偏移是否等于数据区大小
    data_size = len(raw) - table_end
    if offsets[-1] != data_size:
        continue
    # 尝试解码字符串
    try:
        strings = []
        last = 0
        for off in offsets:
            s = raw[table_end+last:table_end+off].decode('utf-8', strict=True)
            strings.append(s)
            last = off
        chs_pools.append({
            'offset': offset,
            'count': count,
            'strings': strings
        })
        print(f'  偏移{offset}: 找到CHS字符串池! count={count}')
        print(f'    前10个: {strings[:10]}')
        print(f'    后10个: {strings[-10:]}')
    except:
        pass

if not chs_pools:
    print('  未找到标准CHS字符串池')

print()

# 2. 查找D6记录标记
print('=== 2. 查找D6记录标记 ===')
d6_positions = []
for i in range(len(raw)):
    if raw[i] == 0xD6:
        # 检查后面是否有合理的ULEB
        d6_positions.append(i)

print(f'找到 {len(d6_positions)} 个0xD6字节')
if d6_positions:
    print('前10个位置的上下文:')
    for pos in d6_positions[:10]:
        context = raw[max(0,pos-4):pos+20]
        print(f'  偏移{pos}: {context.hex()}')

print()

# 3. 查找x{标记（即使之前没找到，再确认一次）
print('=== 3. 查找x{标记 ===')
x_positions = []
for i in range(len(raw) - 2):
    if raw[i] == 0x78 and raw[i+1] == 0x7B:
        x_positions.append(i)
print(f'找到 {len(x_positions)} 个x{{标记')

print()

# 4. 查找其他BinDict相关标记
print('=== 4. 查找其他BinDict标记 ===')
# 常见标记: 0x07 (异构容器), 0x27 (数组), 0x0B (引用)
markers = {0x07: '0x07异构容器', 0x27: '0x27数组', 0x0B: '0x0B引用', 0x0C: '0x0C'}
for marker, name in markers.items():
    count = raw.count(bytes([marker]))
    print(f'  {name}: {count}次')

print()

# 5. 尝试在marshal数据后查找BinDict结构
print('=== 5. 分析marshal数据后的区域 ===')
# 前35字节是头部，后面是marshal数据
# 尝试找到marshal数据的结束位置
import marshal
offset = 35
marshal_end = 35
while offset < len(raw):
    try:
        obj = marshal.loads(raw[offset:])
        try:
            serialized = marshal.dumps(obj)
            obj_len = len(serialized)
        except:
            obj_len = 0
        if obj_len > 0:
            offset += obj_len
            marshal_end = offset
        else:
            offset += 1
    except:
        offset += 1

print(f'marshal数据结束位置: {marshal_end}')
print(f'marshal后剩余字节: {len(raw) - marshal_end}')

if marshal_end < len(raw):
    remaining = raw[marshal_end:]
    print(f'剩余数据前100字节: {remaining[:100].hex()}')
    print(f'剩余数据repr: {repr(remaining[:100])}')
    
    # 在剩余数据中查找BinDict特征
    print()
    print('在剩余数据中查找BinDict特征:')
    # 查找x{
    x_in_remaining = []
    for i in range(len(remaining) - 2):
        if remaining[i] == 0x78 and remaining[i+1] == 0x7B:
            x_in_remaining.append(marshal_end + i)
    print(f'  x{{标记: {len(x_in_remaining)}个')
    
    # 查找CHS字符串池
    for offset2 in range(0, len(remaining) - 8):
        count, reserved = struct.unpack_from('<II', remaining, offset2)
        if reserved != 0 or count == 0 or count > 1000:
            continue
        table_end = offset2 + 8 + count * 4
        if table_end > len(remaining):
            continue
        offsets = struct.unpack_from(f'<{count}I', remaining, offset2+8)
        if offsets[0] <= 0 or offsets[-1] != len(remaining) - table_end:
            continue
        valid = all(offsets[i] > offsets[i-1] for i in range(1, count))
        if not valid:
            continue
        try:
            strings = []
            last = 0
            for off in offsets:
                s = remaining[table_end+last:table_end+off].decode('utf-8', strict=True)
                strings.append(s)
                last = off
            print(f'  找到CHS字符串池! 偏移{marshal_end+offset2}, count={count}')
            print(f'    前10个: {strings[:10]}')
        except:
            pass

print()

# 6. 分析整个文件的结构（分段）
print('=== 6. 文件结构分段分析 ===')
# 头部
print(f'头部 (0-35): {raw[:35].hex()}')
print(f'  魔数: {raw[:4].hex()}')
print(f'  路径: {raw[6:35]}')

# 查找所有可读字符串
print()
print('=== 7. 查找所有可读ASCII字符串 ===')
ascii_strings = re.findall(rb'[a-zA-Z_][a-zA-Z0-9_/\\.]{3,}', raw)
print(f'找到 {len(ascii_strings)} 个ASCII字符串')
for s in ascii_strings[:30]:
    print(f'  {s.decode()}')

print()

# 8. 查找中文字符（UTF-8）
print('=== 8. 查找中文字符 ===')
try:
    decoded = raw.decode('utf-8', errors='ignore')
    chinese = re.findall(r'[\u4e00-\u9fff]{2,}', decoded)
    print(f'找到 {len(chinese)} 个中文字符串')
    for s in chinese[:20]:
        print(f'  {s}')
except:
    print('  无法解码')

print()

# 9. 尝试zlib解压不同区域
print('=== 9. 尝试zlib解压各区域 ===')
for start in [35, 100, 500, 1000, marshal_end]:
    if start >= len(raw):
        continue
    try:
        decompressed = zlib.decompress(raw[start:])
        print(f'  偏移{start}: zlib解压成功! 大小={len(decompressed)}')
        print(f'    头部: {decompressed[:64].hex()}')
        # 查找字符串
        ascii_in_decomp = re.findall(rb'[a-zA-Z_][a-zA-Z0-9_/\\.]{3,}', decompressed)
        if ascii_in_decomp:
            print(f'    ASCII字符串（前10）: {[s.decode() for s in ascii_in_decomp[:10]]}')
        break
    except:
        pass
else:
    print('  所有区域zlib解压失败')
