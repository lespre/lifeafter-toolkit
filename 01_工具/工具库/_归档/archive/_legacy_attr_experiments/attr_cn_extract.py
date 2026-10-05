# -*- coding: utf-8 -*-
"""从 attribute_data_chs.nxs 第一个数据块提取 243 个中文名，建立索引"""
import struct, json
from pathlib import Path

fp = Path(r'E:\提取成果\attribute_data\attribute_data_chs_4D97783A1FC8AFEC.bin')
data = fp.read_bytes()

# @48 开始是 243 个数据块偏移表
# 第一个数据块 @2304 是中文名偏移表
# 每个条目 4 字节：1字节标记 + 3字节小端偏移

print("=== 第一个数据块 @2304 的前 30 个偏移及指向内容 ===")
cn_names = []
for i in range(243):
    entry_off = 2304 + i * 4
    # 3字节小端（第2-4字节）
    off3 = data[entry_off+1] | (data[entry_off+2] << 8) | (data[entry_off+3] << 16)
    if off3 > 0 and off3 < len(data):
        # 看看指向的前 30 字节
        content = data[off3:off3+30]
        # 尝试找到有效的 UTF-8 中文起始位置
        start = off3
        for j in range(8):
            if off3+j+2 < len(data):
                b = data[off3+j]
                if 0xE0 <= b <= 0xEF:  # UTF-8 中文首字节
                    start = off3 + j
                    break
        # 读取到下一个偏移或 0 结尾
        next_entry = 2304 + (i+1) * 4
        next_off = data[next_entry+1] | (data[next_entry+2] << 8) | (data[next_entry+3] << 16) if i < 242 else len(data)
        length = next_off - start if next_off > start else 200
        s = data[start:start+length].decode('utf-8', errors='replace').rstrip('\x00')
        cn_names.append(s)
        if i < 30:
            print(f"  [{i:3d}] off={off3:5d} start={start:5d} len={len(s):3d} : {s[:40]}")

print(f"\n中文名总数: {len(cn_names)}")

# 看看 140-170
print("\n=== index 140-170 ===")
for i in range(140, min(170, len(cn_names))):
    marker = " <-- AUG field23=148" if i == 148 else (" <-- SCAR field23=161" if i == 161 else "")
    print(f"  {i:3d}: {cn_names[i]}{marker}")

# 搜索关键属性
print("\n=== 关键属性索引（按中文名搜索）===")
for kw in ["攻击", "伤害", "射速", "暴击", "耐久", "护甲", "穿透", "弹匣", "换弹", "散布", "稳定", "射程", "重量", "火力", "精准"]:
    for i, name in enumerate(cn_names):
        if kw in name:
            print(f"  {kw:6s} = index {i:3d} ({name})")
            break

# 保存
out = Path(r"E:\提取成果\attribute_data\attr_cn_names.json")
out.write_text(json.dumps(cn_names, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n已保存到 {out}")
