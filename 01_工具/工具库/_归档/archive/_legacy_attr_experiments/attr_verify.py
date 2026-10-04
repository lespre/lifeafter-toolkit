# -*- coding: utf-8 -*-
"""验证属性名列表，找出缺少的属性名"""
import json
from pathlib import Path

attrs = json.loads(Path(r'E:\提取成果\attribute_data\attr_sorted_index.json').read_text(encoding='utf-8'))

fp = Path(r'E:\提取成果\attribute_data\attribute_data_chs_4D97783A1FC8AFEC.bin')
data = fp.read_bytes()

str_start = 15557
str_end = 29356

# 验证每个属性名在文件中的位置
cumulative = 0
mismatches = 0
for i, name in enumerate(attrs):
    actual_pos = str_start + cumulative
    expected = name.encode('ascii')
    if data[actual_pos:actual_pos+len(expected)] != expected:
        mismatches += 1
        if mismatches <= 5:
            actual = data[actual_pos:actual_pos+len(expected)+10].decode('ascii', errors='replace')
            print(f'  不匹配 index {i}: 期望 {name}, 实际 {actual}')
    cumulative += len(name)

print(f'总属性名: {len(attrs)}, 不匹配: {mismatches}')
print(f'累积总长度: {cumulative}, 表实际长度: {str_end-str_start}')

# 找出未覆盖区域
covered = bytearray(str_end - str_start)
cumulative = 0
for name in attrs:
    nb = name.encode('ascii')
    for j in range(len(nb)):
        if cumulative + j < len(covered):
            covered[cumulative + j] = 1
    cumulative += len(nb)

gaps = []
in_gap = False
gap_start = 0
for i in range(len(covered)):
    if covered[i] == 0 and not in_gap:
        gap_start = i
        in_gap = True
    elif covered[i] == 1 and in_gap:
        gaps.append((gap_start, i))
        in_gap = False
if in_gap:
    gaps.append((gap_start, len(covered)))

print(f'\n发现 {len(gaps)} 个未覆盖区域:')
for start, end in gaps[:30]:
    content = data[str_start+start:str_start+end+30].decode('ascii', errors='replace')
    print(f'  偏移 {start}-{end} (长度{end-start}): {content[:80]}')

# 用未覆盖区域的内容补全属性名列表
print('\n=== 补全后的完整属性名列表 ===')
# 重建：按偏移顺序，把属性名和gap内容合并
full_attrs = []
cumulative = 0
attr_idx = 0
gap_idx = 0
pos = 0
while pos < str_end - str_start:
    if attr_idx < len(attrs):
        name = attrs[attr_idx]
        name_start = 0
        # 计算这个属性名的累积偏移
        temp = 0
        for k in range(attr_idx):
            temp += len(attrs[k])
        name_start = temp
        if pos == name_start:
            full_attrs.append(name)
            pos += len(name)
            attr_idx += 1
            continue
    # 检查是否在gap中
    in_gap_now = False
    for gs, ge in gaps:
        if gs <= pos < ge:
            # 读取gap内容直到下一个属性名或gap结束
            gap_content = data[str_start+pos:str_start+ge].decode('ascii', errors='replace')
            if gap_content.strip():
                full_attrs.append(f'[GAP]{gap_content}')
            pos = ge
            in_gap_now = True
            break
    if not in_gap_now:
        pos += 1

print(f'完整列表共 {len(full_attrs)} 项')
for i, name in enumerate(full_attrs):
    marker = ' <-- AUG(148)' if i == 148 else (' <-- SCAR(161)' if i == 161 else '')
    print(f'  {i:3d}: {name}{marker}')
