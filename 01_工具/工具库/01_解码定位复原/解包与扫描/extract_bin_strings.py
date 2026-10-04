# -*- coding: utf-8 -*-
"""
bin文件字符串提取器：从bin文件中提取可读字符串（UTF-8/GBK/UTF-16LE），保存为txt。
用法: python extract_bin_strings.py <bin文件路径> [输出txt路径]
"""
from __future__ import annotations
import sys, re, os
from pathlib import Path

def extract_strings(data, min_len=4):
    """从二进制数据中提取可读字符串。"""
    results = []
    
    # UTF-8字符串
    try:
        text = data.decode('utf-8', errors='ignore')
        # 提取连续的可读字符（中文+英文+数字+标点）
        matches = re.findall(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\w\s\.\,\;\:\!\?\(\)\[\]\{\}\<\>\/\\\|\-\+\=\*\&\%\$\#\@\!\~]{4,}', text)
        for m in matches:
            m = m.strip()
            if len(m) >= min_len and any('\u4e00' <= c <= '\u9fff' for c in m):
                results.append(('utf-8', m))
    except:
        pass
    
    # GBK字符串
    try:
        text = data.decode('gbk', errors='ignore')
        matches = re.findall(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\w\s\.\,\;\:\!\?\(\)\[\]\{\}\<\>\/\\\|\-\+\=\*\&\%\$\#\@\!\~]{4,}', text)
        for m in matches:
            m = m.strip()
            if len(m) >= min_len and any('\u4e00' <= c <= '\u9fff' for c in m):
                results.append(('gbk', m))
    except:
        pass
    
    # UTF-16LE字符串
    try:
        text = data.decode('utf-16-le', errors='ignore')
        matches = re.findall(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\w\s\.\,\;\:\!\?\(\)\[\]\{\}\<\>\/\\\|\-\+\=\*\&\%\$\#\@\!\~]{4,}', text)
        for m in matches:
            m = m.strip()
            if len(m) >= min_len and any('\u4e00' <= c <= '\u9fff' for c in m):
                results.append(('utf-16-le', m))
    except:
        pass
    
    # 去重（保留顺序）
    seen = set()
    unique = []
    for enc, s in results:
        if s not in seen:
            seen.add(s)
            unique.append((enc, s))
    
    return unique

def main():
    if len(sys.argv) < 2:
        print('用法: python extract_bin_strings.py <bin文件路径> [输出txt路径]')
        return
    
    bin_path = Path(sys.argv[1])
    if not bin_path.exists():
        print(f'文件不存在: {bin_path}')
        return
    
    if len(sys.argv) >= 3:
        out_path = Path(sys.argv[2])
    else:
        out_path = bin_path.with_suffix('.txt')
    
    print(f'读取: {bin_path} ({bin_path.stat().st_size} 字节)')
    data = bin_path.read_bytes()
    
    print(f'提取可读字符串...')
    strings = extract_strings(data)
    
    print(f'找到 {len(strings)} 条可读字符串')
    print()
    
    # 保存到txt
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f'# 从 {bin_path.name} 提取的可读字符串\n')
        f.write(f'# 原始大小: {bin_path.stat().st_size} 字节\n')
        f.write(f'# 提取数量: {len(strings)} 条\n')
        f.write(f'# 生成时间: {__import__("datetime").datetime.now()}\n')
        f.write('\n')
        
        for i, (enc, s) in enumerate(strings):
            f.write(f'[{i:04d}] [{enc}] {s}\n')
    
    print(f'已保存到: {out_path}')
    print()
    
    # 打印前50条
    print('=== 前50条 ===')
    for i, (enc, s) in enumerate(strings[:50]):
        print(f'[{i:04d}] [{enc}] {s[:100]}')

if __name__ == '__main__':
    main()
