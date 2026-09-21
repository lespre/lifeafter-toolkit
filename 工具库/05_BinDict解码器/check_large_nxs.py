# -*- coding: utf-8 -*-
"""检查1B249D5C9984E1B4.nxs，查找实际字符串数据"""
import sys, os, struct, re, zlib, marshal

nxs_path = r'E:\提取成果\拆包产物\_nxs配置\1B249D5C9984E1B4.nxs'

with open(nxs_path, 'rb') as f:
    raw = f.read()

print(f'文件大小: {len(raw):,} bytes')
print()

# 1. 检查文件头部
print('=== 1. 文件头部 ===')
print(f'前64字节: {raw[:64].hex()}')
print(f'前64字节repr: {repr(raw[:64])}')

# 检查是否有路径字符串
path_match = re.search(rb'[a-zA-Z_\\]{5,}\.[a-zA-Z]{1,5}', raw[:200])
if path_match:
    print(f'路径字符串: {path_match.group().decode()}')

print()

# 2. 查找可读字符串
print('=== 2. 查找可读ASCII字符串（长度>=4）===')
all_strings = re.findall(rb'[a-zA-Z_][a-zA-Z0-9_/\\.]{3,}', raw)
print(f'找到 {len(all_strings)} 个字符串')
print('前50个:')
for s in all_strings[:50]:
    print(f'  {s.decode()}')

print()

# 3. 查找中文字符（UTF-8）
print('=== 3. 查找中文字符 ===')
try:
    decoded = raw.decode('utf-8', errors='ignore')
    chinese = re.findall(r'[\u4e00-\u9fff]{2,}', decoded)
    print(f'找到 {len(chinese)} 个中文字符串')
    print('前30个:')
    for s in chinese[:30]:
        print(f'  {s}')
except Exception as e:
    print(f'解码失败: {e}')

print()

# 4. 查找武器皮肤相关关键词
print('=== 4. 查找武器皮肤相关关键词 ===')
keywords = [
    'weapon_skin', '武器皮肤', '极光剑', '战神烈火剑', '帝皇裁决',
    '铠甲勇士', '刑天', '飞影', '帝皇侠', 'AUG',
    'skin', 'weapon', '涂装', '皮肤'
]

for kw in keywords:
    if isinstance(kw, str):
        kw_bytes = kw.encode('utf-8')
    else:
        kw_bytes = kw
    count = raw.count(kw_bytes)
    if count > 0:
        print(f'  {kw}: {count}次')
        # 查找位置
        pos = 0
        positions = []
        while True:
            pos = raw.find(kw_bytes, pos)
            if pos < 0:
                break
            positions.append(pos)
            pos += 1
            if len(positions) >= 5:
                break
        print(f'    位置: {positions}')
        # 查看上下文
        for p in positions[:3]:
            context = raw[max(0,p-20):p+len(kw_bytes)+30]
            print(f'    上下文: {repr(context)}')

print()

# 5. 检查是否有marshal数据
print('=== 5. 检查marshal数据 ===')
# 尝试从不同偏移加载marshal
for offset in [0, 35, 100, 1000]:
    if offset >= len(raw):
        continue
    try:
        obj = marshal.loads(raw[offset:])
        print(f'偏移{offset}: marshal加载成功! 类型={type(obj).__name__}')
        if isinstance(obj, (int, float, str, bool)):
            print(f'  值: {obj}')
        elif isinstance(obj, (list, tuple)):
            print(f'  长度: {len(obj)}')
            print(f'  前5个: {obj[:5]}')
        elif isinstance(obj, dict):
            print(f'  键数: {len(obj)}')
            print(f'  前5个键: {list(obj.keys())[:5]}')
        break
    except Exception as e:
        pass
else:
    print('  所有偏移marshal加载失败')

print()

# 6. 尝试zlib解压
print('=== 6. 尝试zlib解压 ===')
for offset in [0, 35, 100, 1000, 10000]:
    if offset >= len(raw):
        continue
    try:
        decompressed = zlib.decompress(raw[offset:])
        print(f'偏移{offset}: zlib解压成功! 大小={len(decompressed):,}')
        print(f'  头部: {decompressed[:64].hex()}')
        # 查找字符串
        strings = re.findall(rb'[a-zA-Z_][a-zA-Z0-9_/\\.]{3,}', decompressed)
        if strings:
            print(f'  字符串（前10）: {[s.decode() for s in strings[:10]]}')
        # 查找中文
        try:
            dec = decompressed.decode('utf-8', errors='ignore')
            chinese = re.findall(r'[\u4e00-\u9fff]{2,}', dec)
            if chinese:
                print(f'  中文（前10）: {chinese[:10]}')
        except:
            pass
        break
    except:
        pass
else:
    print('  所有偏移zlib解压失败')

print()

# 7. 查找BinDict特征
print('=== 7. 查找BinDict特征 ===')
# x{标记
x_count = raw.count(b'x{')
print(f'x{{标记: {x_count}个')

# D6标记
d6_count = raw.count(b'\xd6')
print(f'0xD6标记: {d6_count}个')

# CHS字符串池特征
print('查找CHS字符串池...')
for offset in range(0, min(1000, len(raw))):
    if offset + 8 > len(raw):
        break
    count, reserved = struct.unpack_from('<II', raw, offset)
    if reserved != 0 or count < 10 or count > 10000:
        continue
    table_end = offset + 8 + count * 4
    if table_end > len(raw):
        continue
    offsets = struct.unpack_from(f'<{count}I', raw, offset+8)
    if offsets[0] <= 0 or offsets[-1] != len(raw) - table_end:
        continue
    valid = all(offsets[i] > offsets[i-1] for i in range(1, count))
    if not valid:
        continue
    try:
        strings = []
        last = 0
        for off in offsets:
            s = raw[table_end+last:table_end+off].decode('utf-8', strict=True)
            strings.append(s)
            last = off
        print(f'  找到CHS字符串池! 偏移{offset}, count={count}')
        print(f'  前10个: {strings[:10]}')
        print(f'  后10个: {strings[-10:]}')
        break
    except:
        pass
else:
    print('  未找到标准CHS字符串池')

print()

# 8. 分析文件结构（分段）
print('=== 8. 文件结构分段分析 ===')
# 查找所有可读字符串的位置
string_positions = []
for m in re.finditer(rb'[a-zA-Z_][a-zA-Z0-9_/\\.]{3,}', raw):
    string_positions.append((m.start(), m.group().decode()))

print(f'字符串位置分布:')
if string_positions:
    print(f'  第一个字符串位置: {string_positions[0][0]}')
    print(f'  最后一个字符串位置: {string_positions[-1][0]}')
    # 按位置分段
    segments = {}
    for pos, s in string_positions:
        segment = pos // 100000
        segments[segment] = segments.get(segment, 0) + 1
    print(f'  分段统计（每100KB）:')
    for seg in sorted(segments.keys()):
        print(f'    {seg*100000}-{seg*100000+99999}: {segments[seg]}个字符串')
