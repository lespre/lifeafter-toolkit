# -*- coding: utf-8 -*-
"""从all_equips和其他配置表查找武器皮肤的model_path和物品ID"""
import sys, os, re, json, runpy, struct

sys.path.insert(0, r'E:\提取成果\明日拆包\工具库\05_BinDict解码器')

# 加载all_equips解码器
_LIB = r'E:\提取成果\明日拆包\工具库\05_BinDict解码器\bindict_lib\decode_current_all_equips_D6_scalar_006.py'
M = runpy.run_path(str(_LIB), run_name='search')
ver, n, src = M['unpack_members']()
slots = M['strings'](src[M['CHS']]['body'])

print('=== 1. 在all_equips字符串池中搜索武器皮肤相关 ===')
skin_keywords = ['skin', '皮肤', 'weapon_skin', 'wpn_skin', '极光', '帝皇', '战神', '疾影', '刑天', '飞影']
for i, s in enumerate(slots):
    if any(kw in s.lower() for kw in skin_keywords):
        if len(s) < 200:
            print(f'  slot[{i}] = {s}')

# 搜索包含weapon路径的字符串
print()
print('=== 2. 搜索包含weapon路径的字符串（前30个）===')
weapon_paths = []
for i, s in enumerate(slots):
    if 'weapon/' in s.lower() and ('.gim' in s.lower() or '.mesh' in s.lower()):
        weapon_paths.append((i, s))
        if len(weapon_paths) <= 30:
            print(f'  slot[{i}] = {s}')
print(f'总计: {len(weapon_paths)}个weapon路径')

# 搜索包含skin的路径
print()
print('=== 3. 搜索包含skin的路径 ===')
skin_paths = []
for i, s in enumerate(slots):
    if 'skin' in s.lower():
        skin_paths.append((i, s))
        print(f'  slot[{i}] = {s}')
print(f'总计: {len(skin_paths)}个skin相关字符串')

# 查看gift_data中的物品ID
print()
print('=== 4. 从gift_data提取武器皮肤的物品ID ===')
gift_path = r'E:\提取成果\拆包产物\_nxs配置\gift_data_kj1_900KB.py'
with open(gift_path, 'r', encoding='utf-8', errors='ignore') as f:
    gift_content = f.read()

# 找武器皮肤名称附近的数字ID
armor_skins = ['帝皇裁决', '战神烈火剑', '极光剑', '极光盾', '疾影枪']
for skin in armor_skins:
    positions = [m.start() for m in re.finditer(re.escape(skin), gift_content)]
    if positions:
        # 在第一个出现位置前后找数字ID
        pos = positions[0]
        region = gift_content[max(0,pos-1000):pos+500]
        # 找5-6位数字
        ids = re.findall(r'\b(\d{5,6})\b', region)
        print(f'  {skin}: 附近数字ID = {list(set(ids))[:10]}')

# 搜索nxs配置目录中的其他配置表
print()
print('=== 5. 搜索nxs配置目录中的武器皮肤相关文件 ===')
nxs_dir = r'E:\提取成果\拆包产物\_nxs配置'
if os.path.exists(nxs_dir):
    for f in sorted(os.listdir(nxs_dir)):
        if any(kw in f.lower() for kw in ['skin', 'weapon', 'item', 'equip', 'gift']):
            fpath = os.path.join(nxs_dir, f)
            size = os.path.getsize(fpath)
            print(f'  {f} ({size:,} bytes)')

# 搜索所有nxs文件中包含"武器皮肤"的
print()
print('=== 6. 搜索所有nxs/py文件中包含"武器皮肤"的 ===')
for f in sorted(os.listdir(nxs_dir)):
    fpath = os.path.join(nxs_dir, f)
    if os.path.isfile(fpath) and f.endswith(('.nxs', '.py')):
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as fh:
                content = fh.read()
            if '武器皮肤' in content:
                count = content.count('武器皮肤')
                print(f'  {f}: {count}次"武器皮肤"')
        except:
            pass
