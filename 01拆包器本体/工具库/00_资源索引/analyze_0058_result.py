# -*- coding: utf-8 -*-
from pathlib import Path
from collections import defaultdict

out_dir = Path(r'E:\提取成果\拆包产物\gres_0058')

print('=== 0058.gpk 解包结果统计 ===')
print()

file_types = defaultdict(list)
total_size = 0
total_files = 0

for f in out_dir.rglob('*'):
    if f.is_file():
        total_files += 1
        size = f.stat().st_size
        total_size += size
        
        ext = f.suffix.lower()
        if not ext:
            try:
                with open(f, 'rb') as fh:
                    header = fh.read(8)
                ext = '无扩展名(' + header[:4].hex() + ')'
            except:
                ext = '无扩展名'
        
        file_types[ext].append({
            'name': f.name,
            'path': str(f.relative_to(out_dir)),
            'size': size,
        })

print('总文件数:', total_files)
print('总大小:', round(total_size / 1024 / 1024, 2), 'MB')
print()

print('文件类型统计:')
print('-' * 60)
for ext, files in sorted(file_types.items(), key=lambda x: len(x[1]), reverse=True):
    size_mb = sum(f['size'] for f in files) / 1024 / 1024
    print('  ' + ext + ': ' + str(len(files)) + '个文件, ' + str(round(size_mb, 2)) + ' MB')

print()
print('前50个最大的文件:')
print('-' * 60)
all_files = []
for ext, files in file_types.items():
    all_files.extend(files)

for f in sorted(all_files, key=lambda x: x['size'], reverse=True)[:50]:
    size_mb = f['size'] / 1024 / 1024
    print('  ' + f['path'] + ': ' + str(round(size_mb, 2)) + ' MB')
