# -*- coding: utf-8 -*-
"""提取极光剑在配置表里的完整上下文，找活动名/海报路径。"""
from __future__ import annotations
import re, json
from pathlib import Path

CONFIG_PATH = Path(r'E:/提取成果/明日拆包/工具库/05_BinDict解码器/output/weapon_search/config_1B249D5C9984E1B4_script.py314.lc.bin')
OUT_DIR = Path(r'E:/提取成果/明日拆包/工具库/05_BinDict解码器/output/weapon_search')

raw = CONFIG_PATH.read_bytes()
text = raw.decode('utf-8', errors='ignore')

print(f'=== 配置表大小: {len(raw)} 字节 ===')
print(f'=== 提取"极光剑"完整上下文 ===\n')

positions = [m.start() for m in re.finditer('极光剑', text)]
print(f'"极光剑"出现次数: {len(positions)}')
print()

for i, pos in enumerate(positions):
    print(f'--- 第{i+1}次出现 (offset={pos}) ---')
    # 扩大上下文到前后1000字节
    start = max(0, pos - 1000)
    end = min(len(text), pos + 1000)
    context = text[start:end]
    
    # 找活动名/关键词
    keywords = ['活动', '抽奖', '宝箱', '礼盒', '交易盒', '海报', 'banner', '活动图', '宣传', '铠甲', '勇士', '联动', '限定', '典藏']
    found_kw = [kw for kw in keywords if kw in context]
    
    # 找UI路径
    ui_paths = re.findall(r'ui/[A-Za-z0-9_/\.]+', context)
    # 找图片路径
    img_paths = re.findall(r'[A-Za-z0-9_/\.]+\.(?:png|jpg|dds)', context)
    # 找数字ID
    ids = re.findall(r'\b(\d{6,})\b', context)
    
    print(f'  关键词: {found_kw}')
    print(f'  UI路径: {list(set(ui_paths))[:5]}')
    print(f'  图片路径: {list(set(img_paths))[:5]}')
    print(f'  数字ID: {list(set(ids))[:10]}')
    print(f'  上下文预览 (前300字):')
    print(f'    {context[:300].replace(chr(10), " ")}')
    print()

# 搜索"铠甲勇士"相关活动
print(f'\n=== 搜索"铠甲勇士"/"勇士商店"相关活动 ===')
for kw in ['铠甲勇士', '勇士商店', '铠甲合体', '帝皇铠甲', '刑天', '飞影']:
    positions_kw = [m.start() for m in re.finditer(kw, text)]
    if positions_kw:
        print(f'  "{kw}" 出现 {len(positions_kw)} 次')
        # 显示第一次出现的上下文
        pos = positions_kw[0]
        start = max(0, pos - 200)
        end = min(len(text), pos + 300)
        context = text[start:end]
        print(f'    上下文: ...{context[:200].replace(chr(10), " ")}...')
        print()

# 保存完整上下文
out_path = OUT_DIR / '极光剑完整上下文.txt'
with open(out_path, 'w', encoding='utf-8') as f:
    for i, pos in enumerate(positions):
        f.write(f'=== 第{i+1}次出现 (offset={pos}) ===\n')
        start = max(0, pos - 2000)
        end = min(len(text), pos + 2000)
        f.write(text[start:end])
        f.write('\n\n' + '='*80 + '\n\n')
print(f'已保存完整上下文: {out_path}')
