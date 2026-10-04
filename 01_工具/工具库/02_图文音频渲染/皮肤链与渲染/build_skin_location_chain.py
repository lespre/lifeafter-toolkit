# -*- coding: utf-8 -*-
"""
解析Python字节码文件的字符串池
提取完整的时装和武器皮肤配置
构建皮肤定位链条
"""
import marshal
import struct
import re
from pathlib import Path
from collections import defaultdict

raw_dir = Path(r'E:\提取成果\配置数据\_script_raw\_raw')
out_dir = Path(r'E:\提取成果\配置数据\皮肤定位链条')
out_dir.mkdir(parents=True, exist_ok=True)

def extract_all_strings(content):
    """提取文件中所有可读字符串"""
    strings = []
    current = []
    positions = []
    
    for i, b in enumerate(content):
        if 32 <= b < 127 or b in (0x09, 0x0a, 0x0d):
            current.append(chr(b))
        else:
            if len(current) >= 4:
                strings.append(''.join(current))
                positions.append(i - len(current))
            current = []
    
    if len(current) >= 4:
        strings.append(''.join(current))
        positions.append(len(content) - len(current))
    
    return list(zip(positions, strings))

def parse_string_pool(content):
    """解析字符串池"""
    # 查找string_pool标记
    string_pool_pos = content.find(b'string_pool')
    if string_pool_pos < 0:
        return None
    
    print(f'  找到string_pool标记，位置: {string_pool_pos}')
    print(f'  标记附近数据: {content[string_pool_pos:string_pool_pos+64].hex()}')
    
    # string_pool后面可能有长度字段
    # 尝试解析
    offset = string_pool_pos + len(b'string_pool')
    
    # 跳过可能的填充字节
    while offset < len(content) and content[offset] == 0:
        offset += 1
    
    print(f'  字符串池数据起始: {offset}')
    print(f'  起始16字节: {content[offset:offset+16].hex()}')
    
    return offset

def extract_image_paths(strings):
    """从字符串中提取图片路径"""
    image_paths = []
    image_pattern = re.compile(r'[\w/]+\.(png|jpg|jpeg|dds|tga)', re.IGNORECASE)
    
    for pos, s in strings:
        # 查找所有图片路径
        matches = image_pattern.findall(s)
        if matches:
            # 提取完整路径
            paths = re.findall(r'[\w/]+\.(?:png|jpg|jpeg|dds|tga)', s, re.IGNORECASE)
            for p in paths:
                image_paths.append({'position': pos, 'path': p})
    
    return image_paths

def extract_fashion_info(content, strings):
    """提取时装信息"""
    fashion_info = []
    
    # 查找时装ID模式（数字ID）
    # 从图片路径中提取ID
    image_paths = extract_image_paths(strings)
    
    fashion_ids = set()
    for ip in image_paths:
        path = ip['path']
        # 查找类似 _3466_ 的ID
        match = re.search(r'_(\d{4,})_', path)
        if match:
            fashion_ids.add(int(match.group(1)))
    
    # 查找时装名称（中文）
    chinese_strings = []
    for pos, s in strings:
        # 检查是否包含中文字符
        if any('\u4e00' <= c <= '\u9fff' for c in s):
            chinese_strings.append({'position': pos, 'text': s})
    
    return {
        'fashion_ids': sorted(list(fashion_ids)),
        'image_paths': image_paths,
        'chinese_strings': chinese_strings,
    }

def analyze_file(filepath):
    """分析单个文件"""
    content = filepath.read_bytes()
    print(f'\n{"="*80}')
    print(f'文件: {filepath.name} ({len(content)}字节)')
    
    # 提取所有字符串
    strings = extract_all_strings(content)
    print(f'  提取到{len(strings)}个字符串')
    
    # 解析字符串池
    string_pool_offset = parse_string_pool(content)
    
    # 提取图片路径
    image_paths = extract_image_paths(strings)
    print(f'  找到{len(image_paths)}个图片路径')
    
    # 提取时装信息
    fashion_info = extract_fashion_info(content, strings)
    print(f'  时装ID: {fashion_info["fashion_ids"]}')
    print(f'  中文字符串: {len(fashion_info["chinese_strings"])}个')
    
    # 输出图片路径
    if image_paths:
        print(f'\n  图片路径列表:')
        for ip in image_paths[:30]:
            print(f'    [{ip["position"]}] {ip["path"]}')
    
    # 输出中文字符串
    if fashion_info['chinese_strings']:
        print(f'\n  中文字符串:')
        for cs in fashion_info['chinese_strings'][:20]:
            print(f'    [{cs["position"]}] {cs["text"][:100]}')
    
    return {
        'file': filepath.name,
        'size': len(content),
        'strings_count': len(strings),
        'image_paths': image_paths,
        'fashion_info': fashion_info,
        'string_pool_offset': string_pool_offset,
    }

# 重点分析的文件
target_files = {
    'fashion_handbook': '000004.bin',  # 时装获取手册
    'fashion_data_us': '000549.bin',   # 美服时装数据
    'fashion_simple': '000552.bin',     # 简单时装数据
    'fashion_data_hmt': '000444.bin',   # 时装数据hmt
    'weapon_skin_pendant': '000169.bin', # 武器皮肤挂件
    'weapon_kind_to_skin': '000274.bin', # 武器类型到皮肤
    'weapon_kind_to_skin2': '000607.bin', # 武器类型到皮肤2
    'coldarm_to_skin': '000287.bin',    # 冷兵器到皮肤
    'common_lottery': '000035.bin',      # 通用抽奖
    'box_data': '000044.bin',            # 宝箱数据
}

print('开始分析配置文件...')
print('=' * 80)

all_results = {}
for category, filename in target_files.items():
    filepath = raw_dir / filename
    if filepath.exists():
        result = analyze_file(filepath)
        all_results[category] = result

# 汇总所有图片路径
print('\n' + '=' * 80)
print('汇总所有图片路径')
print('=' * 80)

all_image_paths = []
for category, result in all_results.items():
    for ip in result['image_paths']:
        ip['category'] = category
        ip['file'] = result['file']
        all_image_paths.append(ip)

# 去重
unique_paths = {}
for ip in all_image_paths:
    if ip['path'] not in unique_paths:
        unique_paths[ip['path']] = ip

print(f'共找到{len(all_image_paths)}个图片路径，去重后{len(unique_paths)}个')
print()

# 按类型分类
path_categories = defaultdict(list)
for path, ip in unique_paths.items():
    if 'shizhuang' in path.lower() or 'fashion' in path.lower():
        path_categories['fashion'].append(ip)
    elif 'weapon' in path.lower() or 'wpn' in path.lower():
        path_categories['weapon'].append(ip)
    elif 'xuanchuan' in path.lower() or 'poster' in path.lower():
        path_categories['poster'].append(ip)
    elif 'shoucang' in path.lower() or 'tujian' in path.lower():
        path_categories['collection'].append(ip)
    else:
        path_categories['other'].append(ip)

for cat, paths in path_categories.items():
    print(f'\n【{cat}】{len(paths)}个')
    for ip in paths[:20]:
        print(f'  {ip["path"]}')

# 汇总所有时装ID
print('\n' + '=' * 80)
print('汇总所有时装ID')
print('=' * 80)

all_fashion_ids = set()
for category, result in all_results.items():
    for fid in result['fashion_info']['fashion_ids']:
        all_fashion_ids.add(fid)

print(f'时装ID: {sorted(list(all_fashion_ids))}')

# 汇总所有中文字符串
print('\n' + '=' * 80)
print('汇总所有中文字符串（可能是时装/武器名称）')
print('=' * 80)

all_chinese = []
for category, result in all_results.items():
    for cs in result['fashion_info']['chinese_strings']:
        cs['category'] = category
        cs['file'] = result['file']
        all_chinese.append(cs)

# 去重
unique_chinese = {}
for cs in all_chinese:
    if cs['text'] not in unique_chinese:
        unique_chinese[cs['text']] = cs

print(f'共找到{len(all_chinese)}个中文字符串，去重后{len(unique_chinese)}个')
print()
for text, cs in list(unique_chinese.items())[:30]:
    print(f'  [{cs["category"]}] {text[:100]}')

# 保存结果
import json
with open(out_dir / '皮肤定位链条_初步结果.json', 'w', encoding='utf-8') as f:
    json.dump({
        'all_image_paths': [{'path': ip['path'], 'category': ip.get('category'), 'file': ip.get('file')} for ip in all_image_paths],
        'unique_image_paths': [{'path': ip['path'], 'category': ip.get('category'), 'file': ip.get('file')} for ip in unique_paths.values()],
        'all_fashion_ids': sorted(list(all_fashion_ids)),
        'all_chinese_strings': [{'text': cs['text'], 'category': cs.get('category'), 'file': cs.get('file')} for cs in unique_chinese.values()],
        'path_categories': {cat: [{'path': ip['path'], 'file': ip.get('file')} for ip in paths] for cat, paths in path_categories.items()},
    }, f, ensure_ascii=False, indent=2)

print()
print(f'结果已保存到: {out_dir / "皮肤定位链条_初步结果.json"}')
