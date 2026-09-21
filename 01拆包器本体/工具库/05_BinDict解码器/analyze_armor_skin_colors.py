# -*- coding: utf-8 -*-
"""转换019750-019789区间的纹理，并分析颜色特征"""
import sys, os, struct, json
from PIL import Image
import numpy as np

sys.path.insert(0, r'E:\提取成果\明日拆包\工具库\01_核心解包器')
import lifeafter_unpacker_full as unpacker

weapon_dir = r'E:\提取成果\拆包产物\weapon'
preview_dir = r'E:\提取成果\拆包产物\_武器纹理预览\铠甲勇士武器皮肤集'
os.makedirs(preview_dir, exist_ok=True)

# 转换019750-019789区间的纹理
print('=== 转换019750-019789区间纹理 ===')
converted = []
for i in range(19750, 19790):
    dds_file = f'{i:06d}.dds'
    dds_path = os.path.join(weapon_dir, dds_file)
    if os.path.exists(dds_path):
        png_file = f'{i:06d}.png'
        png_path = os.path.join(preview_dir, png_file)
        try:
            unpacker.dds2png(dds_path, png_path)
            converted.append(png_file)
            print(f'  转换成功: {dds_file}')
        except Exception as e:
            print(f'  转换失败: {dds_file} - {e}')

print(f'\n成功转换 {len(converted)} 个纹理')

# 分析每个纹理的主色调
print()
print('=== 纹理颜色特征分析 ===')
color_analysis = []
for png_file in sorted(os.listdir(preview_dir)):
    if not png_file.endswith('.png'):
        continue
    png_path = os.path.join(preview_dir, png_file)
    try:
        img = Image.open(png_path)
        img = img.convert('RGB')
        img = img.resize((256, 256))  # 缩小以加速分析
        arr = np.array(img)
        
        # 计算主色调
        avg_color = arr.mean(axis=(0, 1))
        r, g, b = avg_color
        
        # 计算颜色分布
        # 红色调（战神烈火剑）
        red_mask = (arr[:,:,0] > 150) & (arr[:,:,1] < 100) & (arr[:,:,2] < 100)
        red_ratio = red_mask.sum() / (256*256)
        
        # 蓝色调（极光剑）
        blue_mask = (arr[:,:,2] > 150) & (arr[:,:,0] < 100) & (arr[:,:,1] < 150)
        blue_ratio = blue_mask.sum() / (256*256)
        
        # 金色调（帝皇裁决）
        gold_mask = (arr[:,:,0] > 180) & (arr[:,:,1] > 140) & (arr[:,:,2] < 100)
        gold_ratio = gold_mask.sum() / (256*256)
        
        # 绿色调（法线贴图/ORM）
        green_mask = (arr[:,:,1] > 150) & (arr[:,:,0] < 150) & (arr[:,:,2] < 150)
        green_ratio = green_mask.sum() / (256*256)
        
        # 判断纹理类型
        texture_type = '未知'
        if green_ratio > 0.3:
            texture_type = '法线/ORM贴图'
        elif gold_ratio > 0.1:
            texture_type = '金色武器皮肤（可能帝皇裁决）'
        elif red_ratio > 0.1:
            texture_type = '红色武器皮肤（可能战神烈火剑）'
        elif blue_ratio > 0.1:
            texture_type = '蓝色武器皮肤（可能极光剑）'
        elif r > 100 and g > 100 and b > 100:
            texture_type = '颜色贴图（亮色）'
        else:
            texture_type = '颜色贴图（暗色）'
        
        analysis = {
            'file': png_file,
            'avg_color': [int(r), int(g), int(b)],
            'red_ratio': float(red_ratio),
            'blue_ratio': float(blue_ratio),
            'gold_ratio': float(gold_ratio),
            'green_ratio': float(green_ratio),
            'type': texture_type,
        }
        color_analysis.append(analysis)
        
        print(f'  {png_file}: RGB=({int(r)},{int(g)},{int(b)}), 红={red_ratio:.1%}, 蓝={blue_ratio:.1%}, 金={gold_ratio:.1%}, 绿={green_ratio:.1%} -> {texture_type}')
    except Exception as e:
        print(f'  {png_file}: 分析失败 - {e}')

# 保存颜色分析结果
analysis_path = os.path.join(preview_dir, '颜色特征分析.json')
with open(analysis_path, 'w', encoding='utf-8') as f:
    json.dump(color_analysis, f, ensure_ascii=False, indent=2)
print(f'\n颜色分析结果已保存: {analysis_path}')

# 汇总
print()
print('=== 武器皮肤纹理汇总 ===')
armor_skins = [a for a in color_analysis if '武器皮肤' in a['type']]
normal_maps = [a for a in color_analysis if '法线' in a['type']]
print(f'疑似铠甲勇士武器皮肤颜色贴图: {len(armor_skins)}个')
for a in armor_skins:
    print(f'  {a["file"]}: {a["type"]}')
print(f'法线/ORM贴图: {len(normal_maps)}个')
