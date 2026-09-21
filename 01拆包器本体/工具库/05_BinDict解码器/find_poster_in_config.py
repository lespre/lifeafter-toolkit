# -*- coding: utf-8 -*-
"""从配置表里搜索海报/活动图的资源路径或file_id。"""
from __future__ import annotations
import re, json
from pathlib import Path

CONFIG_PATH = Path(r'E:/提取成果/明日拆包/工具库/05_BinDict解码器/output/weapon_search/config_1B249D5C9984E1B4_script.py314.lc.bin')

raw = CONFIG_PATH.read_bytes()
text = raw.decode('utf-8', errors='ignore')

print(f'=== 配置表大小: {len(raw)} 字节 ===')
print()

# 搜索图片路径
print('=== 搜索图片路径 ===')
img_patterns = [
    r'ui/[A-Za-z0-9_/]+\.(?:png|jpg|dds)',
    r'[A-Za-z0-9_/]+\.(?:png|jpg|dds)',
    r'icon_[A-Za-z0-9_]+',
    r'banner[A-Za-z0-9_]*',
    r'poster[A-Za-z0-9_]*',
    r'activity[A-Za-z0-9_/]*',
]
for pat in img_patterns:
    matches = re.findall(pat, text)
    if matches:
        print(f'  模式 {pat}: {len(matches)} 条')
        for m in list(set(matches))[:10]:
            print(f'    {m}')
        print()

# 搜索"海报"/"活动图"/"banner"等关键词
print('=== 搜索海报相关关键词 ===')
keywords = ['海报', '活动图', 'banner', '宣传图', '主视觉', 'kv', '封面', '背景图', 'loading', '加载图']
for kw in keywords:
    positions = [m.start() for m in re.finditer(kw, text, re.IGNORECASE)]
    if positions:
        print(f'  "{kw}": {len(positions)} 次')
        for pos in positions[:3]:
            start = max(0, pos - 100)
            end = min(len(text), pos + 100)
            context = text[start:end].replace('\n', '\\n')
            print(f'    [{pos}] ...{context}...')
        print()

# 搜索铠甲勇士相关的图片引用
print('=== 搜索铠甲勇士相关的图片引用 ===')
armor_keywords = ['铠甲', '勇士', '刑天', '飞影', '帝皇', '极光', '战神', '疾影']
for kw in armor_keywords:
    # 找关键词附近的图片路径
    for match in re.finditer(kw, text):
        pos = match.start()
        start = max(0, pos - 200)
        end = min(len(text), pos + 200)
        context = text[start:end]
        # 找附近的图片路径
        imgs = re.findall(r'[A-Za-z0-9_/]+\.(?:png|jpg|dds)', context)
        icons = re.findall(r'icon_[A-Za-z0-9_]+', context)
        if imgs or icons:
            print(f'  "{kw}" at [{pos}]:')
            if imgs:
                print(f'    图片: {list(set(imgs))}')
            if icons:
                print(f'    图标: {list(set(icons))}')
            print(f'    上下文: ...{context[:150].replace(chr(10), " ")}...')
            print()
            break  # 每个关键词只显示第一个

# 搜索数字file_id（16位十六进制）
print('=== 搜索16位十六进制file_id ===')
fid_pattern = r'[0-9A-Fa-f]{16}'
fids = re.findall(fid_pattern, text)
if fids:
    print(f'  找到 {len(fids)} 个16位hex')
    print(f'  前10个: {list(set(fids))[:10]}')
