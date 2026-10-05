# -*- coding: utf-8 -*-
"""
解析Python字节码文件的字符串池
提取完整的时装和武器皮肤配置数据
字符串池格式：0xd3/0xf3/0xda/0xfa + 长度 + 字符串内容
"""
import struct
from pathlib import Path
from collections import defaultdict

raw_dir = Path(r'E:\提取成果\配置数据\_script_raw\_raw')
out_dir = Path(r'E:\提取成果\配置数据\皮肤定位链条')
out_dir.mkdir(parents=True, exist_ok=True)

def parse_string_pool(content, start_offset):
    """解析字符串池"""
    strings = []
    offset = start_offset
    
    # 跳过可能的头部
    # 查找第一个字符串标记
    while offset < len(content):
        tag = content[offset]
        
        # 字符串类型标记
        if tag in (0xd3, 0xf3, 0xda, 0xfa, 0xd4, 0xf4):
            # 读取长度
            if offset + 1 >= len(content):
                break
            
            length = content[offset + 1]
            
            # 对于长字符串，可能需要读取更多字节
            if length == 0xff:
                # 长字符串，读取4字节长度
                if offset + 5 >= len(content):
                    break
                length = struct.unpack_from('<I', content, offset + 2)[0]
                string_start = offset + 6
            else:
                string_start = offset + 2
            
            # 读取字符串
            if string_start + length > len(content):
                break
            
            string_data = content[string_start:string_start + length]
            
            try:
                # 尝试用不同编码解码
                if tag in (0xda, 0xfa):
                    # Unicode字符串
                    string_value = string_data.decode('utf-8', errors='replace')
                else:
                    # ASCII字符串
                    string_value = string_data.decode('ascii', errors='replace')
                
                strings.append({
                    'offset': offset,
                    'tag': f'0x{tag:02x}',
                    'length': length,
                    'value': string_value,
                })
            except:
                pass
            
            offset = string_start + length
        else:
            # 不是字符串标记，继续前进
            offset += 1
    
    return strings

def find_string_pool_start(content):
    """查找字符串池起始位置"""
    # 查找string_pool标记
    string_pool_pos = content.find(b'string_pool')
    if string_pool_pos < 0:
        return None
    
    # string_pool后面是数据
    # 跳过标记和可能的填充
    offset = string_pool_pos + len(b'string_pool')
    
    # 跳过0字节
    while offset < len(content) and content[offset] == 0:
        offset += 1
    
    return offset

def analyze_file(filepath):
    """分析单个文件"""
    content = filepath.read_bytes()
    print(f'\n{"="*80}')
    print(f'文件: {filepath.name} ({len(content)}字节)')
    
    # 查找字符串池
    pool_start = find_string_pool_start(content)
    if pool_start:
        print(f'  字符串池起始: {pool_start}')
        
        # 解析字符串池
        strings = parse_string_pool(content, pool_start)
        print(f'  解析到{len(strings)}个字符串')
        
        # 输出字符串
        for i, s in enumerate(strings[:30]):
            print(f'    [{i}] [{s["tag"]}] @{s["offset"]}: {s["value"][:100]}')
        
        return strings
    else:
        print('  未找到字符串池')
        return []

# 重点分析的文件
target_files = [
    '000004.bin',  # 时装获取手册
    '000549.bin',  # 美服时装数据
    '000552.bin',  # 简单时装数据
    '000169.bin',  # 武器皮肤挂件
    '000274.bin',  # 武器类型到皮肤
    '000607.bin',  # 武器类型到皮肤2
    '000287.bin',  # 冷兵器到皮肤
    '000035.bin',  # 通用抽奖
]

print('开始解析字符串池...')
print('=' * 80)

all_strings = {}
for filename in target_files:
    filepath = raw_dir / filename
    if filepath.exists():
        strings = analyze_file(filepath)
        all_strings[filename] = strings

# 汇总所有字符串
print('\n' + '=' * 80)
print('汇总所有字符串')
print('=' * 80)

total_strings = sum(len(s) for s in all_strings.values())
print(f'共解析到{total_strings}个字符串')

# 搜索关键词
print('\n' + '=' * 80)
print('搜索关键词')
print('=' * 80)

keywords = ['fashion', 'weapon', 'skin', 'poster', 'img_path', 'xuanchuan', 
            'shizhuang', '极光', '帝皇', '刑天', '飞影', '铠甲', 'aug', 'AUG',
            'theme_name', 'new_poster', 'poster_bg', 'poster_txt']

for kw in keywords:
    hits = []
    for filename, strings in all_strings.items():
        for s in strings:
            if kw.lower() in s['value'].lower():
                hits.append({'file': filename, 'string': s})
    
    if hits:
        print(f'\n【{kw}】{len(hits)}个命中')
        for hit in hits[:10]:
            s = hit['string']
            print(f'  [{hit["file"]}] @{s["offset"]}: {s["value"][:100]}')

# 保存结果
import json
with open(out_dir / '字符串池解析结果.json', 'w', encoding='utf-8') as f:
    json.dump({
        filename: [{'offset': s['offset'], 'tag': s['tag'], 'length': s['length'], 'value': s['value']} for s in strings]
        for filename, strings in all_strings.items()
    }, f, ensure_ascii=False, indent=2)

print()
print(f'结果已保存到: {out_dir / "字符串池解析结果.json"}')
