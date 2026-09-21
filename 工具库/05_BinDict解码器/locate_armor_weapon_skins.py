# -*- coding: utf-8 -*-
"""定位铠甲勇士武器皮肤的模型和纹理"""
import sys, os, re, json, struct

# === 1. 详细分析weapon_skin_data.nxs ===
print('=== 1. weapon_skin_data.nxs详细分析 ===')
skin_path = r'E:\提取成果\拆包产物\_nxs配置\weapon_skin_data.nxs'
with open(skin_path, 'rb') as f:
    raw = f.read()
print(f'文件大小: {len(raw):,} bytes')
print(f'头部32字节: {raw[:32].hex()}')

# 尝试多种编码找可读字符串
for enc in ['utf-8', 'gbk', 'utf-16-le', 'utf-16-be']:
    try:
        text = raw.decode(enc, errors='ignore')
        chinese = re.findall(r'[\u4e00-\u9fff]{2,}', text)
        ascii_strings = re.findall(r'[a-zA-Z_][a-zA-Z0-9_/\\.]{3,}', text)
        if chinese or ascii_strings:
            print(f'  {enc}: 中文={len(chinese)}个, ASCII字符串={len(ascii_strings)}个')
            if chinese:
                print(f'    中文（前10）: {list(set(chinese))[:10]}')
            if ascii_strings:
                print(f'    ASCII（前10）: {list(set(ascii_strings))[:10]}')
    except:
        pass

# === 2. 搜索所有nxs配置中武器皮肤相关的模型路径 ===
print()
print('=== 2. 搜索nxs配置中武器皮肤模型路径 ===')
nxs_dir = r'E:\提取成果\拆包产物\_nxs配置'
if os.path.exists(nxs_dir):
    for f in os.listdir(nxs_dir):
        fpath = os.path.join(nxs_dir, f)
        if os.path.isfile(fpath) and f.endswith(('.nxs', '.py')):
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as fh:
                    content = fh.read()
                # 搜索武器皮肤关键词
                skin_kw = ['武器皮肤', 'weapon_skin', 'skin_id', '皮肤']
                hits = [kw for kw in skin_kw if kw in content]
                if hits:
                    print(f'  {f}: 命中{hits}')
                    # 显示上下文
                    for kw in hits[:1]:
                        pos = content.find(kw)
                        context = content[max(0,pos-100):pos+200].replace('\\n', ' ').replace('\\r', '')
                        print(f'    上下文: ...{context[:300]}...')
            except:
                pass

# === 3. 分析weapon.gpk中.mesh文件的大小分布 ===
print()
print('=== 3. weapon.gpk中.mesh文件大小分布 ===')
weapon_dir = r'E:\提取成果\拆包产物\weapon'
mesh_files = []
dds_files = []
for f in os.listdir(weapon_dir):
    fpath = os.path.join(weapon_dir, f)
    if f.endswith('.mesh'):
        mesh_files.append((f, os.path.getsize(fpath)))
    elif f.endswith('.dds'):
        dds_files.append((f, os.path.getsize(fpath)))

mesh_files.sort(key=lambda x: -x[1])
print(f'.mesh文件总数: {len(mesh_files)}')
print(f'最大的20个.mesh文件:')
for f, size in mesh_files[:20]:
    print(f'  {f} ({size:,} bytes = {size/1024:.1f} KB)')

# === 4. 分析.dds文件大小分布 ===
print()
print(f'.dds文件总数: {len(dds_files)}')
# 按大小分组
size_groups = {}
for f, size in dds_files:
    group = size // (1024*1024)  # 按MB分组
    size_groups[group] = size_groups.get(group, 0) + 1
print(f'.dds文件大小分布（MB分组）:')
for group in sorted(size_groups.keys(), reverse=True):
    print(f'  {group}MB~{group+1}MB: {size_groups[group]}个')

# 5.3MB的dds文件列表
big_dds = [(f, s) for f, s in dds_files if s > 5*1024*1024]
print(f'大于5MB的.dds文件: {len(big_dds)}个')
print(f'  编号范围: {big_dds[0][0]} ~ {big_dds[-1][0]}')

# === 5. 查看几个大mesh文件的头部，判断是否是武器模型 ===
print()
print('=== 5. 大mesh文件头部分析 ===')
for f, size in mesh_files[:5]:
    fpath = os.path.join(weapon_dir, f)
    with open(fpath, 'rb') as fh:
        header = fh.read(64)
    print(f'  {f} ({size:,} bytes):')
    print(f'    头部64字节: {header.hex()}')
    # 尝试找可读字符串
    try:
        text = header.decode('ascii', errors='ignore')
        readable = re.findall(r'[a-zA-Z0-9_]{3,}', text)
        if readable:
            print(f'    可读字符串: {readable}')
    except:
        pass
