# -*- coding: utf-8 -*-
"""提取第一个数据块全部 704 个条目，找出属性索引规律"""
import struct, json
from pathlib import Path

fp = Path(r'E:\提取成果\attribute_data\attribute_data_chs_4D97783A1FC8AFEC.bin')
data = fp.read_bytes()

# 第一个数据块 @2304，大小 = 5120-2304 = 2816 字节，704 个条目
# 704 / 243 ≈ 2.9，可能每个属性 3 个字符串

print("=== 第一个数据块全部 704 个条目（每 3 个一组）===")
entries = []
for i in range(704):
    entry_off = 2304 + i * 4
    off3 = data[entry_off+1] | (data[entry_off+2] << 8) | (data[entry_off+3] << 16)
    if off3 > 0 and off3 < len(data):
        # 找 UTF-8 起始
        start = off3
        for j in range(8):
            if off3+j < len(data):
                b = data[off3+j]
                if 0xE0 <= b <= 0xEF or 0x20 <= b <= 0x7E:
                    start = off3 + j
                    break
        # 读取到下一个非字符串字符
        end = start
        while end < len(data):
            b = data[end]
            if 0xE0 <= b <= 0xEF:  # UTF-8 中文
                end += 3
            elif 0x20 <= b <= 0x7E:  # ASCII 可打印
                end += 1
            elif b == 0x00:
                break
            else:
                break
        s = data[start:end].decode('utf-8', errors='replace').rstrip('\x00')
        entries.append({'idx': i, 'off': off3, 'start': start, 'len': len(s), 'text': s[:60]})
    else:
        entries.append({'idx': i, 'off': off3, 'start': 0, 'len': 0, 'text': ''})

# 每 3 个一组打印前 80 组
for group in range(80):
    base = group * 3
    if base + 2 >= len(entries):
        break
    e0 = entries[base]
    e1 = entries[base+1]
    e2 = entries[base+2]
    print(f"  属性{group:3d}: [{e0['text']:30s}] [{e1['text']:30s}] [{e2['text']:30s}]")

# 看看属性 48-55（AUG/SCAR 附近）
print("\n=== 属性 48-55（AUG/SCAR 附近）===")
for group in range(48, 56):
    base = group * 3
    if base + 2 >= len(entries):
        break
    e0 = entries[base]
    e1 = entries[base+1]
    e2 = entries[base+2]
    print(f"  属性{group:3d}: [{e0['text']:40s}] [{e1['text']:40s}] [{e2['text']:40s}]")

# 保存
out = Path(r"E:\提取成果\attribute_data\attr_all_entries.json")
out.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n共 {len(entries)} 个条目，已保存到 {out}")
