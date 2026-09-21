# -*- coding: utf-8 -*-
"""查看lifeafter_unpacker_full.py中的gpk和nxs解析函数"""
import re

with open(r'E:\提取成果\明日拆包\工具库\01_核心解包器\lifeafter_unpacker_full.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找所有函数定义
print('=== 所有函数定义 ===')
for match in re.finditer(r'def (\w+)\(', content):
    name = match.group(1)
    if any(kw in name.lower() for kw in ['gpk', 'nxs', 'decrypt', 'bindict', 'extract', 'parse']):
        start = match.start()
        line_start = content.rfind('\n', 0, start) + 1
        line_end = content.find('\n', start)
        print(f'  {content[line_start:line_end].strip()}')

# 找gpk魔数相关
print()
print('=== gpk魔数/格式相关 ===')
for kw in ['FPGH', 'NXPK', 'FPGK', 'gpk', 'GPK', 'magic']:
    positions = [m.start() for m in re.finditer(re.escape(kw), content)]
    if positions:
        print(f'  "{kw}": {len(positions)}次出现')
        for pos in positions[:2]:
            line_start = content.rfind('\n', 0, pos) + 1
            line_end = content.find('\n', pos)
            line = content[line_start:line_end].strip()
            if len(line) > 120:
                line = line[:120] + '...'
            print(f'    {line}')

# 找extract_gpk函数的完整内容
print()
print('=== extract_gpk函数内容（前50行）===')
match = re.search(r'def extract_gpk\(', content)
if match:
    start = match.start()
    # 找到函数结束（下一个def或类定义）
    next_def = content.find('\ndef ', start + 10)
    if next_def == -1:
        next_def = content.find('\nclass ', start + 10)
    func_content = content[start:next_def if next_def > 0 else start + 2000]
    lines = func_content.split('\n')[:50]
    for i, line in enumerate(lines):
        print(f'  {i+1}: {line}')
