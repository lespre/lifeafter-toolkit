# -*- coding: utf-8 -*-
"""用第二个数据块（中文描述偏移表）反推属性索引"""
from pathlib import Path

fp = Path(r'E:\提取成果\attribute_data\attribute_data_chs_4D97783A1FC8AFEC.bin')
data = fp.read_bytes()

# 搜索 attack_point 等
print("=== 搜索攻击力相关属性名 ===")
for kw in [b'attack_point', b'e_attack_p', b'attack_power', b'base_attack',
           b'weapon_attack', b'gun_attack', b'attack_value', b'atk']:
    pos = data.find(kw)
    if pos >= 0:
        context = data[max(0,pos-15):pos+len(kw)+25].decode('ascii', errors='replace')
        print(f"  {kw.decode():20s} @{pos}: ...{context}...")
    else:
        print(f"  {kw.decode():20s}: 未找到")

# 第二个数据块 @5120，243 个偏移指向中文描述
print()
print("=== 第二个数据块前 15 个描述 ===")
for i in range(15):
    entry_off = 5120 + i * 4
    off3 = data[entry_off+1] | (data[entry_off+2] << 8) | (data[entry_off+3] << 16)
    if off3 > 0 and off3 < len(data):
        end = off3
        while end < len(data) and end - off3 < 300:
            b = data[end]
            if b == 0:
                break
            if 0xE0 <= b <= 0xEF:
                end += 3
            elif 0x20 <= b <= 0x7E:
                end += 1
            elif b in (0x23, 0x7B, 0x7D, 0x0A, 0x0D, 0x2C, 0x2E, 0x3A):
                end += 1
            else:
                break
        desc = data[off3:end].decode('utf-8', errors='replace')
        print(f"  [{i:2d}] @{off3:5d}: {desc[:100]}")

# 搜索包含"攻击"的描述
print()
print("=== 包含'攻击'的描述（前 20 个）===")
count = 0
for i in range(243):
    entry_off = 5120 + i * 4
    off3 = data[entry_off+1] | (data[entry_off+2] << 8) | (data[entry_off+3] << 16)
    if off3 > 0 and off3 < len(data):
        end = off3
        while end < len(data) and end - off3 < 300:
            b = data[end]
            if b == 0:
                break
            if 0xE0 <= b <= 0xEF:
                end += 3
            elif 0x20 <= b <= 0x7E:
                end += 1
            elif b in (0x23, 0x7B, 0x7D, 0x0A, 0x0D, 0x2C, 0x2E, 0x3A):
                end += 1
            else:
                break
        desc = data[off3:end].decode('utf-8', errors='replace')
        if '攻击' in desc:
            print(f"  [{i:3d}] @{off3:5d}: {desc[:120]}")
            count += 1
            if count >= 20:
                break

# 搜索包含"火力"的描述
print()
print("=== 包含'火力'的描述 ===")
for i in range(243):
    entry_off = 5120 + i * 4
    off3 = data[entry_off+1] | (data[entry_off+2] << 8) | (data[entry_off+3] << 16)
    if off3 > 0 and off3 < len(data):
        end = off3
        while end < len(data) and end - off3 < 300:
            b = data[end]
            if b == 0:
                break
            if 0xE0 <= b <= 0xEF:
                end += 3
            elif 0x20 <= b <= 0x7E:
                end += 1
            elif b in (0x23, 0x7B, 0x7D, 0x0A, 0x0D, 0x2C, 0x2E, 0x3A):
                end += 1
            else:
                break
        desc = data[off3:end].decode('utf-8', errors='replace')
        if '火力' in desc:
            print(f"  [{i:3d}] @{off3:5d}: {desc[:120]}")
