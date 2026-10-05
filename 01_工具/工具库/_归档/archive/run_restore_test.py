# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'E:\提取成果\明日之后拆包工具')
from filename_restorer import path_id, parse_npk_entry_table, restore_filenames, build_known_paths

# 读取路径字典
paths = set()
with open(r'E:\提取成果\filename_restore_output\path_dictionary.txt', 'r', encoding='utf-8') as f:
    for line in f:
        p = line.strip()
        if p:
            paths.add(p)

paths.update(build_known_paths())
print(f'路径字典总计: {len(paths)}')

# 还原 script.py3.npk
matched, unmatched = restore_filenames(
    r'E:\mrzh\Documents\script.py3.npk',
    paths,
    r'E:\提取成果\filename_restore_output'
)

print()
print('=== 匹配结果（前50条）===')
for m in sorted(matched, key=lambda x: x['entry_index'])[:50]:
    print(f"  [{m['entry_index']:5d}] {m['logical_path']:55s} flag={m['flag']} size={m['packed_size']}")
