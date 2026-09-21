# -*- coding: utf-8 -*-
"""分析AUG涂装 vs 武器皮肤系统"""
import sys, os, re, json

# === 1. weapon.gpk文件类型统计 ===
weapon_dir = r'E:\提取成果\拆包产物\weapon'
print('=== weapon.gpk文件类型统计 ===')
ext_count = {}
for f in os.listdir(weapon_dir):
    ext = os.path.splitext(f)[1].lower()
    ext_count[ext] = ext_count.get(ext, 0) + 1
for ext, count in sorted(ext_count.items(), key=lambda x: -x[1]):
    print(f'  {ext}: {count}个')

# 找大文件（可能是武器模型/纹理）
print()
print('=== weapon.gpk中最大的20个文件 ===')
files_with_size = []
for f in os.listdir(weapon_dir):
    fpath = os.path.join(weapon_dir, f)
    size = os.path.getsize(fpath)
    files_with_size.append((f, size))
files_with_size.sort(key=lambda x: -x[1])
for f, size in files_with_size[:20]:
    print(f'  {f} ({size:,} bytes = {size/1024/1024:.1f} MB)')

# === 2. gift_data中武器皮肤清单 ===
print()
print('=== gift_data中武器皮肤清单 ===')
gift_path = r'E:\提取成果\拆包产物\_nxs配置\gift_data_kj1_900KB.py'
with open(gift_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# 找所有"武器皮肤:"后面的内容
skin_pattern = r'武器皮肤[:：]\s*([^\n\r"\\]+)'
skin_matches = re.findall(skin_pattern, content)
print(f'找到 {len(skin_matches)} 个武器皮肤引用:')
seen = set()
for i, skin in enumerate(skin_matches):
    skin = skin.strip()
    if skin not in seen:
        seen.add(skin)
        print(f'  {len(seen)}. {skin}')

# === 3. 铠甲勇士相关上下文 ===
print()
print('=== gift_data中铠甲勇士相关内容 ===')
keywords = ['铠甲勇士', '刑天', '飞影', '帝皇', '极光剑', '战神烈火剑', '帝皇裁决', '沙海月鸣']
for kw in keywords:
    positions = [m.start() for m in re.finditer(re.escape(kw), content)]
    if positions:
        print(f'  "{kw}": {len(positions)}次出现')
        # 显示前2个上下文
        for idx, pos in enumerate(positions[:2]):
            context = content[max(0,pos-80):pos+120].replace('\\n', ' ').replace('\\r', '').replace('\\t', ' ')
            print(f'    上下文{idx+1}: ...{context}...')

# === 4. 查看weapon_skin_data.nxs ===
print()
print('=== weapon_skin_data.nxs内容预览 ===')
skin_path = r'E:\提取成果\拆包产物\_nxs配置\weapon_skin_data.nxs'
if os.path.exists(skin_path):
    with open(skin_path, 'rb') as f:
        raw = f.read()
    print(f'  文件大小: {len(raw):,} bytes')
    print(f'  头部16字节: {raw[:16].hex()}')
    # 尝试找可读字符串
    try:
        text = raw.decode('utf-8', errors='ignore')
        # 找中文
        chinese = re.findall(r'[\u4e00-\u9fff]{2,}', text)
        if chinese:
            print(f'  中文字符串（前20个）:')
            for c in list(set(chinese))[:20]:
                print(f'    {c}')
    except:
        pass
else:
    print(f'  文件不存在: {skin_path}')

# === 5. 搜索all_equips中是否有武器皮肤相关字段 ===
print()
print('=== all_equips字符串池中武器皮肤相关字段 ===')
_LIB = r'E:\提取成果\明日拆包\工具库\05_BinDict解码器\bindict_lib\decode_current_all_equips_D6_scalar_006.py'
import runpy
M = runpy.run_path(str(_LIB), run_name='search')
ver, n, src = M['unpack_members']()
slots = M['strings'](src[M['CHS']]['body'])

skin_keywords = ['skin', '皮肤', '涂装', 'fashion', '外观']
for i, s in enumerate(slots):
    if any(kw in s.lower() for kw in skin_keywords):
        if len(s) < 150:
            print(f'  slot[{i}] = {s}')
