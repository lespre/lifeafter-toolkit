# -*- coding: utf-8 -*-
import os, re

base = r'E:\提取成果\明日之后拆包工具'

print('=== 脚本硬编码路径检查 ===')
for f in sorted(os.listdir(base)):
    if not f.endswith('.py'):
        continue
    full = os.path.join(base, f)
    content = open(full, 'r', encoding='utf-8', errors='ignore').read()
    
    # 找硬编码路径
    paths = re.findall(r'[A-Z]:[\\/][^\s\"\']+', content)
    if paths:
        unique_paths = list(set(paths))
        print(f'\n{f}:')
        for p in unique_paths[:5]:
            exists = os.path.exists(p)
            status = 'OK' if exists else 'MISSING'
            print(f'  [{status}] {p}')
        if len(unique_paths) > 5:
            print(f'  ... 还有 {len(unique_paths)-5} 个路径')

print('\n=== 检查完成 ===')
