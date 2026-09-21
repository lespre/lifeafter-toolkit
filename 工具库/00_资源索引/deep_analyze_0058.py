# -*- coding: utf-8 -*-
from pathlib import Path
import json

out_dir = Path(r'E:\提取成果\拆包产物\gres_0058')

print('=== 0058.gpk 内容深入分析 ===')
print()

# 1. 查看JSON文件
print('--- JSON文件 ---')
for f in out_dir.glob('*.json'):
    print('文件:', f.name)
    try:
        with open(f, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        print('内容:')
        print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])
    except Exception as e:
        print('读取失败:', e)
        # 尝试二进制读取
        with open(f, 'rb') as fh:
            print('头部:', fh.read(100).hex())

print()

# 2. 搜索bin文件中的文本关键词
print('--- BIN文件关键词搜索 ---')
keywords = [
    '铠甲', '刑天', '飞影', '帝皇', '极光', '战神', '裁决',
    '武器皮肤', '时装', 'AUG', '改造', '转移',
    'xingtian', 'feiying', 'dihuang', 'armor', 'weapon', 'skin',
    'aug', 'fashion',
]

# 搜索所有bin文件
hits = {}
for f in out_dir.glob('*.bin'):
    try:
        with open(f, 'rb') as fh:
            data = fh.read()
        
        file_hits = []
        for kw in keywords:
            # 尝试多种编码
            for encoding in ['utf-8', 'gbk', 'utf-16-le']:
                try:
                    encoded = kw.encode(encoding)
                    if encoded in data:
                        file_hits.append(kw + '(' + encoding + ')')
                        break
                except:
                    pass
        
        if file_hits:
            hits[f.name] = file_hits
    except:
        pass

if hits:
    print('命中文件:')
    for fname, kws in sorted(hits.items()):
        print('  ' + fname + ': ' + ', '.join(kws))
else:
    print('未命中关键词')

print()

# 3. 查看FSB音频文件
print('--- FSB音频文件 ---')
for f in sorted(out_dir.glob('*.fsb')):
    print('  ' + f.name + ': ' + str(round(f.stat().st_size / 1024, 2)) + ' KB')
    # 查看头部
    with open(f, 'rb') as fh:
        header = fh.read(64)
    print('    头部:', header[:32].hex())
    # 尝试提取采样名
    try:
        # FSB5格式，采样名在头部后面
        if header[:4] == b'FSB5':
            # 简单搜索可打印字符串
            text = ''
            for b in header:
                if 32 <= b < 127:
                    text += chr(b)
                else:
                    if len(text) > 3:
                        print('    字符串:', text)
                    text = ''
            if len(text) > 3:
                print('    字符串:', text)
    except:
        pass

print()

# 4. 查看C159模型文件
print('--- C159模型文件（前10个） ---')
c159_files = sorted(out_dir.glob('*.c159'))
for f in c159_files[:10]:
    print('  ' + f.name + ': ' + str(round(f.stat().st_size / 1024, 2)) + ' KB')

print('  ... 共', len(c159_files), '个C159文件')

print()

# 5. 查看DDS纹理文件统计
print('--- DDS纹理文件统计 ---')
dds_files = sorted(out_dir.glob('*.dds'))
print('  共', len(dds_files), '个DDS文件')
print('  总大小:', round(sum(f.stat().st_size for f in dds_files) / 1024 / 1024, 2), 'MB')

# 按大小分组
large_dds = [f for f in dds_files if f.stat().st_size > 1024*1024]
medium_dds = [f for f in dds_files if 100*1024 < f.stat().st_size <= 1024*1024]
small_dds = [f for f in dds_files if f.stat().st_size <= 100*1024]

print('  大纹理(>1MB):', len(large_dds), '个')
print('  中纹理(100KB-1MB):', len(medium_dds), '个')
print('  小纹理(<100KB):', len(small_dds), '个')
