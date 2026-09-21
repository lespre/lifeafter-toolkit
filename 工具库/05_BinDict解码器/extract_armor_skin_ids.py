# -*- coding: utf-8 -*-
"""从gift_data提取铠甲勇士武器皮肤的物品ID和详细信息"""
import sys, os, re, json

gift_path = r'E:\提取成果\拆包产物\_nxs配置\gift_data_kj1_900KB.py'

with open(gift_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

print('=== 1. 提取所有"武器皮肤：XXX"的完整上下文 ===')
# 找所有武器皮肤引用
skin_pattern = r'武器皮肤[:：]\s*([^\n\r"\\*]+)'
skin_matches = list(re.finditer(skin_pattern, content))
print(f'找到 {len(skin_matches)} 个武器皮肤引用')

# 去重
skin_names = set()
for m in skin_matches:
    name = m.group(1).strip()
    if name and len(name) < 50:
        skin_names.add(name)

print(f'去重后 {len(skin_names)} 个武器皮肤:')
for i, name in enumerate(sorted(skin_names)):
    print(f'  {i+1}. {name}')

# 提取每个武器皮肤的完整物品描述
print()
print('=== 2. 铠甲勇士武器皮肤的完整物品描述 ===')
armor_skins = ['帝皇裁决', '战神烈火剑', '极光剑', '极光盾', '疾影枪', 
                '极狐终结刃', '灵态诱导', '重力震爆', '阿赖耶识']

for skin in armor_skins:
    # 找包含这个皮肤名称的所有位置
    positions = [m.start() for m in re.finditer(re.escape(skin), content)]
    if positions:
        print(f'\n--- {skin} ({len(positions)}次出现) ---')
        # 显示第一个出现的完整上下文
        pos = positions[0]
        # 向前找物品名称（通常在"打开可以获得"前面）
        start = max(0, pos - 300)
        end = min(len(content), pos + 200)
        context = content[start:end].replace('\\n', ' | ').replace('\\r', '').replace('#r', '').replace('#n', '')
        # 清理颜色代码
        context = re.sub(r'#c[0-9a-fA-F]{6}', '', context)
        context = re.sub(r'#c[0-9a-fA-F]{8}', '', context)
        print(f'  上下文: ...{context[:400]}...')

# 3. 搜索武器皮肤的物品ID（通常是数字ID）
print()
print('=== 3. 搜索武器皮肤相关的物品ID ===')
# 在gift_data中找"武器皮肤"附近的数字ID
for skin in armor_skins[:3]:  # 只看前3个
    positions = [m.start() for m in re.finditer(re.escape(skin), content)]
    for pos in positions[:1]:
        # 在前后500字节内找数字ID
        region = content[max(0,pos-500):pos+500]
        # 找可能的物品ID（5-6位数字）
        ids = re.findall(r'\b(\d{5,6})\b', region)
        if ids:
            print(f'  {skin} 附近的数字ID: {list(set(ids))[:10]}')

# 4. 查看gift_data的结构，找物品定义
print()
print('=== 4. gift_data文件结构预览 ===')
# 找前1000字符的结构
preview = content[:2000].replace('\\n', '\n').replace('\\r', '')
print(preview[:1500])
