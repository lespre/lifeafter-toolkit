# -*- coding: utf-8 -*-
"""通过.mesh模型文件大小和头部特征区分武器类型"""
import sys, os, struct, json

weapon_dir = r'E:\提取成果\拆包产物\weapon'

# 获取所有.mesh文件
mesh_files = []
for f in os.listdir(weapon_dir):
    if f.endswith('.mesh'):
        fpath = os.path.join(weapon_dir, f)
        size = os.path.getsize(fpath)
        mesh_files.append((f, size, fpath))

print(f'=== weapon.gpk中.mesh文件总数: {len(mesh_files)} ===')

# 按大小分组
print()
print('=== .mesh文件大小分布 ===')
size_groups = {}
for f, size, fpath in mesh_files:
    group = size // (10 * 1024)  # 按10KB分组
    if group not in size_groups:
        size_groups[group] = []
    size_groups[group].append((f, size))

for group in sorted(size_groups.keys()):
    files = size_groups[group]
    print(f'  {group*10}KB~{(group+1)*10}KB: {len(files)}个')

# 分析小mesh文件（可能是武器模型）
print()
print('=== 小于100KB的.mesh文件（可能是武器模型）===')
small_meshes = [(f, size, fpath) for f, size, fpath in mesh_files if size < 100 * 1024]
small_meshes.sort(key=lambda x: x[1])
print(f'总数: {len(small_meshes)}个')
for f, size, fpath in small_meshes[:30]:
    # 读取头部
    with open(fpath, 'rb') as fh:
        header = fh.read(64)
    # 检查魔数
    magic = header[:4].hex()
    print(f'  {f} ({size:,} bytes) magic={magic}')

# 分析中等大小mesh文件（50-200KB，可能是武器模型）
print()
print('=== 50-200KB的.mesh文件（可能是武器模型）===')
medium_meshes = [(f, size, fpath) for f, size, fpath in mesh_files if 50 * 1024 <= size < 200 * 1024]
medium_meshes.sort(key=lambda x: x[1])
print(f'总数: {len(medium_meshes)}个')
for f, size, fpath in medium_meshes[:30]:
    with open(fpath, 'rb') as fh:
        header = fh.read(64)
    magic = header[:4].hex()
    print(f'  {f} ({size:,} bytes) magic={magic}')

# 分析mesh文件头部魔数
print()
print('=== .mesh文件头部魔数统计 ===')
magic_count = {}
for f, size, fpath in mesh_files[:1000]:  # 只统计前1000个
    with open(fpath, 'rb') as fh:
        header = fh.read(4)
    magic = header.hex()
    magic_count[magic] = magic_count.get(magic, 0) + 1

for magic, count in sorted(magic_count.items(), key=lambda x: -x[1]):
    print(f'  {magic}: {count}个')

# 查找与纹理编号对应的mesh文件
# 纹理编号在019750-019789区间，看看附近的mesh文件
print()
print('=== 019700-019800区间的.mesh文件 ===')
for f, size, fpath in mesh_files:
    idx = int(f.replace('.mesh', ''))
    if 19700 <= idx <= 19800:
        with open(fpath, 'rb') as fh:
            header = fh.read(64)
        magic = header[:4].hex()
        print(f'  {f} ({size:,} bytes) magic={magic}')

# 查找与纹理编号对应的mesh文件（004100-004120区间）
print()
print('=== 004100-004120区间的.mesh文件 ===')
for f, size, fpath in mesh_files:
    idx = int(f.replace('.mesh', ''))
    if 4100 <= idx <= 4120:
        with open(fpath, 'rb') as fh:
            header = fh.read(64)
        magic = header[:4].hex()
        print(f'  {f} ({size:,} bytes) magic={magic}')
