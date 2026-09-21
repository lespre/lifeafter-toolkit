# -*- coding: utf-8 -*-
"""提取1B249D5C9984E1B4.nxs中的武器皮肤完整记录"""
import sys, os, struct, re, json

nxs_path = r'E:\提取成果\拆包产物\_nxs配置\1B249D5C9984E1B4.nxs'

with open(nxs_path, 'rb') as f:
    raw = f.read()

print(f'文件大小: {len(raw):,} bytes')
print()

# 1. 提取所有中文字符串及其位置
print('=== 1. 提取所有中文字符串 ===')
# 使用UTF-8解码，提取连续的中文字符串
chinese_strings = []
try:
    decoded = raw.decode('utf-8', errors='ignore')
    # 查找中文字符串（包含中文和标点）
    for m in re.finditer(r'[\u4e00-\u9fff][\u4e00-\u9fff\w\s\-\*\+\#\.\,\，\。\：\:\(\)（）\[\]【】\/\\]{1,200}', decoded):
        chinese_strings.append({
            'text': m.group(),
            'start': m.start(),
            'end': m.end()
        })
except Exception as e:
    print(f'解码失败: {e}')

print(f'找到 {len(chinese_strings)} 个中文字符串')

print()

# 2. 查找武器皮肤相关的完整记录
print('=== 2. 武器皮肤相关完整记录 ===')
weapon_skin_keywords = ['武器皮肤', '极光剑', '战神烈火剑', '帝皇裁决', '铠甲勇士', '刑天', '飞影', '帝皇侠', '帝皇驹']

weapon_skin_records = []
for kw in weapon_skin_keywords:
    print(f'\n--- 关键词: {kw} ---')
    positions = []
    pos = 0
    kw_bytes = kw.encode('utf-8')
    while True:
        pos = raw.find(kw_bytes, pos)
        if pos < 0:
            break
        positions.append(pos)
        pos += 1
    
    print(f'找到 {len(positions)} 处')
    
    # 提取每个位置的上下文（前后200字节）
    for p in positions[:10]:
        context_start = max(0, p - 100)
        context_end = min(len(raw), p + len(kw_bytes) + 200)
        context_bytes = raw[context_start:context_end]
        try:
            context_text = context_bytes.decode('utf-8', errors='ignore')
            # 清理非打印字符
            context_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', context_text)
            context_text = re.sub(r'\s+', ' ', context_text).strip()
            print(f'  偏移{p}: {context_text[:300]}')
            
            weapon_skin_records.append({
                'keyword': kw,
                'offset': p,
                'context': context_text[:500]
            })
        except:
            pass

print()

# 3. 查找"打开可以获得武器皮肤"的完整列表
print('=== 3. "打开可以获得武器皮肤"完整列表 ===')
pattern = '打开可以获得武器皮肤[:：]'.encode('utf-8')
pos = 0
weapon_skin_list = []
while True:
    pos = raw.find(pattern, pos)
    if pos < 0:
        break
    # 提取后面的内容
    context_start = pos
    context_end = min(len(raw), pos + 500)
    context_bytes = raw[context_start:context_end]
    try:
        context_text = context_bytes.decode('utf-8', errors='ignore')
        # 提取武器皮肤名称
        match = re.search(r'打开可以获得武器皮肤[:：]([^*#\s]+)', context_text)
        if match:
            skin_name = match.group(1)
            print(f'  偏移{pos}: {skin_name}')
            weapon_skin_list.append({
                'name': skin_name,
                'offset': pos,
                'context': context_text[:200]
            })
    except:
        pass
    pos += 1

print(f'\n共找到 {len(weapon_skin_list)} 个武器皮肤')
print('武器皮肤列表:')
for item in weapon_skin_list:
    print(f'  - {item["name"]}')

print()

# 4. 查找铠甲勇士联动相关的完整内容
print('=== 4. 铠甲勇士联动完整内容 ===')
armor_keywords = ['铠甲勇士', '刑天', '飞影', '帝皇侠', '帝皇驹', '帝皇裁决', '极光剑', '战神烈火剑']
armor_records = []

for kw in armor_keywords:
    kw_bytes = kw.encode('utf-8')
    pos = 0
    while True:
        pos = raw.find(kw_bytes, pos)
        if pos < 0:
            break
        # 提取较大的上下文
        context_start = max(0, pos - 200)
        context_end = min(len(raw), pos + len(kw_bytes) + 300)
        context_bytes = raw[context_start:context_end]
        try:
            context_text = context_bytes.decode('utf-8', errors='ignore')
            context_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', context_text)
            context_text = re.sub(r'\s+', ' ', context_text).strip()
            # 只保留有意义的记录（包含多个关键词或较长文本）
            if len(context_text) > 20:
                armor_records.append({
                    'keyword': kw,
                    'offset': pos,
                    'context': context_text[:500]
                })
        except:
            pass
        pos += 1

# 去重
unique_contexts = []
seen = set()
for record in armor_records:
    ctx = record['context'][:100]
    if ctx not in seen:
        seen.add(ctx)
        unique_contexts.append(record)

print(f'找到 {len(unique_contexts)} 条独特记录')
print('前20条:')
for i, record in enumerate(unique_contexts[:20]):
    print(f'\n[{i+1}] {record["keyword"]} @ 偏移{record["offset"]}:')
    print(f'    {record["context"][:300]}')

print()

# 5. 保存结果
print('=== 5. 保存结果 ===')
output_data = {
    'weapon_skin_list': weapon_skin_list,
    'weapon_skin_records': weapon_skin_records,
    'armor_records': unique_contexts[:50],
}

output_path = r'E:\提取成果\明日拆包\工具库\05_BinDict解码器\weapon_skin_extracted.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)
print(f'已保存到: {output_path}')

# 保存武器皮肤列表为文本
txt_path = r'E:\提取成果\明日拆包\工具库\05_BinDict解码器\武器皮肤列表.txt'
with open(txt_path, 'w', encoding='utf-8') as f:
    f.write('=== 武器皮肤列表 ===\n\n')
    for item in weapon_skin_list:
        f.write(f'- {item["name"]}\n')
    f.write(f'\n共 {len(weapon_skin_list)} 个武器皮肤\n')
print(f'武器皮肤列表已保存到: {txt_path}')
