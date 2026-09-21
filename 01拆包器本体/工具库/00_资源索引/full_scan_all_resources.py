# -*- coding: utf-8 -*-
"""
全量扫描 E:\mrzh 所有目录和文件
包括：res/、Documents/、bin/、根目录文件
识别文件类型，统计大小和修改时间，生成完整索引表
"""
from pathlib import Path
import struct
import json
from datetime import datetime
from collections import defaultdict
from Crypto.Cipher import AES

mrzh_dir = Path(r'E:\mrzh')
out_dir = Path(r'E:\提取成果\明日拆包\文档索引')
out_dir.mkdir(parents=True, exist_ok=True)

AES_KEY = bytes.fromhex('606308D8A32C782013D26C2F226F686D')

def aes_ecb_decrypt(data):
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    padded_len = (len(data) // 16) * 16
    if padded_len == 0:
        return data
    return cipher.decrypt(data[:padded_len])

def get_header(filepath, num_bytes=256):
    try:
        with open(filepath, 'rb') as f:
            return f.read(num_bytes)
    except:
        return b''

def ascii_str(data):
    return ''.join(chr(b) if 32 <= b < 127 else '.' for b in data)

def identify_file(filepath):
    """识别文件类型和信息"""
    try:
        stat = filepath.stat()
    except:
        return None
    
    ext = filepath.suffix.lower()
    name = filepath.name
    size = stat.st_size
    size_mb = round(size / 1024 / 1024, 2)
    mtime = datetime.fromtimestamp(stat.st_mtime)
    
    info = {
        'name': name,
        'path': str(filepath),
        'relative_path': str(filepath.relative_to(mrzh_dir)),
        'extension': ext,
        'size': size,
        'size_mb': size_mb,
        'mtime': mtime.strftime('%Y-%m-%d %H:%M:%S'),
        'is_recent': mtime >= datetime(2026, 7, 29),
    }
    
    # 获取头部
    header = get_header(filepath, 64)
    if header:
        info['header_hex'] = header[:32].hex()
        info['header_ascii'] = ascii_str(header[:32])
    
    # 识别文件类型
    file_type = '未知'
    description = ''
    
    # 按扩展名识别
    if ext == '.gpk':
        file_type = 'GPK资源包'
        description = '游戏资源包，AES-ECB加密头部'
        # 尝试解密头部获取条目数
        if header:
            try:
                decrypted = aes_ecb_decrypt(header)
                magic = decrypted[4:8]
                if magic in (b'HPGF', b'FPGH'):
                    info['magic'] = magic.decode('ascii', errors='replace')
                    entry_count = struct.unpack_from('<I', decrypted, 20)[0]
                    if entry_count < 10000000:
                        info['entry_count'] = entry_count
            except:
                pass
    
    elif ext == '.fpk':
        file_type = 'FPK资源包'
        description = 'NXPK格式资源包，AES加密'
        if header:
            try:
                decrypted = aes_ecb_decrypt(header)
                entry_count = struct.unpack_from('<I', decrypted, 20)[0]
                if entry_count < 10000000:
                    info['entry_count'] = entry_count
            except:
                pass
    
    elif ext == '.npk':
        file_type = 'NPK资源包'
        description = 'NPK格式资源包'
    
    elif ext == '.nxs':
        file_type = 'NXS配置文件'
        description = 'BinDict/xbrace加密配置'
    
    elif ext == '.wpk':
        file_type = 'WPK资源包'
        description = '武器纹理包，1DPW加密'
    
    elif ext == '.idx':
        file_type = 'IDX索引文件'
        description = 'WPK包索引文件'
    
    elif ext == '.thx':
        file_type = 'THX纹理引用'
        description = '纹理引用哈希文件'
    
    elif ext == '.thh':
        file_type = 'THH文件'
        description = 'THFB相关文件'
    
    elif ext == '.gres':
        file_type = 'GRES资源包'
        description = 'RPGF/CPGF/KPGF分卷结构'
    
    elif ext == '.dds':
        file_type = 'DDS纹理'
        description = 'DirectDraw Surface纹理'
    
    elif ext == '.png':
        file_type = 'PNG图片'
        description = 'PNG格式图片'
    
    elif ext == '.jpg' or ext == '.jpeg':
        file_type = 'JPG图片'
        description = 'JPEG格式图片'
    
    elif ext == '.bin':
        file_type = 'BIN二进制'
        description = '二进制文件'
    
    elif ext == '.json':
        file_type = 'JSON配置'
        description = 'JSON格式配置'
    
    elif ext == '.txt':
        file_type = '文本文件'
        description = '纯文本文件'
    
    elif ext == '.exe':
        file_type = '可执行文件'
        description = 'Windows可执行程序'
    
    elif ext == '.dll':
        file_type = '动态链接库'
        description = 'Windows DLL'
    
    elif ext == '.py':
        file_type = 'Python脚本'
        description = 'Python源代码'
    
    elif ext == '.pyc':
        file_type = 'Python字节码'
        description = 'Python编译字节码'
    
    elif ext == '.lc':
        file_type = 'Lua字节码'
        description = 'Lua编译字节码'
    
    elif ext == '.ini':
        file_type = 'INI配置'
        description = 'INI配置文件'
    
    elif ext == '.log':
        file_type = '日志文件'
        description = '日志文件'
    
    elif ext == '.lnk':
        file_type = '快捷方式'
        description = 'Windows快捷方式'
    
    elif not ext:
        # 无扩展名文件，检查头部
        if header:
            magic = header[:4]
            if magic == b'PK\x03\x04':
                file_type = 'ZIP压缩包'
                description = 'ZIP格式压缩包'
            elif magic[:2] == b'MZ':
                file_type = 'PE可执行文件'
                description = 'Windows PE格式（无扩展名）'
            else:
                file_type = '无扩展名二进制'
                description = f'无扩展名，头部: {ascii_str(magic)}'
    
    info['file_type'] = file_type
    info['description'] = description
    
    return info

# 扫描所有目录
print('=== 全量扫描 E:\mrzh ===')
print()

all_files = []
dir_stats = defaultdict(lambda: {'file_count': 0, 'total_size': 0})

# 要扫描的目录
scan_dirs = [
    mrzh_dir / 'res',
    mrzh_dir / 'Documents',
    mrzh_dir / 'bin',
]

# 扫描根目录文件（不递归）
print('扫描根目录文件...')
for item in sorted(mrzh_dir.iterdir()):
    if item.is_file():
        info = identify_file(item)
        if info:
            all_files.append(info)
            dir_stats['根目录']['file_count'] += 1
            dir_stats['根目录']['total_size'] += info['size']
            print(f'  {info["name"]}: {info["file_type"]} ({info["size_mb"]} MB)')

# 扫描各个目录
for scan_dir in scan_dirs:
    if not scan_dir.exists():
        continue
    
    dir_name = scan_dir.name
    print()
    print(f'扫描 {dir_name}/ ...')
    
    for item in scan_dir.rglob('*'):
        if item.is_file():
            info = identify_file(item)
            if info:
                all_files.append(info)
                dir_stats[dir_name]['file_count'] += 1
                dir_stats[dir_name]['total_size'] += info['size']
                
                # 只打印大文件（>10MB）
                if info['size_mb'] > 10:
                    print(f'  {info["relative_path"]}: {info["file_type"]} ({info["size_mb"]} MB)')

print()
print('=' * 80)
print('扫描完成')
print('=' * 80)
print(f'总文件数: {len(all_files)}')
total_size = sum(f['size'] for f in all_files)
print(f'总大小: {total_size / 1024 / 1024 / 1024:.2f} GB')

print()
print('各目录统计:')
for dir_name, stats in dir_stats.items():
    size_gb = stats['total_size'] / 1024 / 1024 / 1024
    print(f'  {dir_name}: {stats["file_count"]}个文件, {size_gb:.2f} GB')

# 按文件类型统计
print()
print('文件类型统计:')
type_stats = defaultdict(lambda: {'count': 0, 'size': 0})
for f in all_files:
    ftype = f['file_type']
    type_stats[ftype]['count'] += 1
    type_stats[ftype]['size'] += f['size']

for ftype, stats in sorted(type_stats.items(), key=lambda x: x[1]['size'], reverse=True):
    size_mb = stats['size'] / 1024 / 1024
    print(f'  {ftype}: {stats["count"]}个, {size_mb:.2f} MB')

# 近一个月更新的文件
print()
print('近一个月更新的大文件 (>100MB):')
recent_files = [f for f in all_files if f['is_recent'] and f['size_mb'] > 100]
for f in sorted(recent_files, key=lambda x: x['size'], reverse=True)[:50]:
    print(f'  {f["relative_path"]}: {f["size_mb"]} MB ({f["mtime"]})')

# 保存完整索引
print()
print('保存完整索引表...')

result = {
    'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'root_dir': str(mrzh_dir),
    'total_files': len(all_files),
    'total_size_gb': round(total_size / 1024 / 1024 / 1024, 2),
    'dir_stats': {
        k: {
            'file_count': v['file_count'],
            'total_size_gb': round(v['total_size'] / 1024 / 1024 / 1024, 2),
        }
        for k, v in dir_stats.items()
    },
    'type_stats': {
        k: {
            'count': v['count'],
            'total_size_mb': round(v['size'] / 1024 / 1024, 2),
        }
        for k, v in type_stats.items()
    },
    'files': all_files,
}

with open(out_dir / '明日之后体验服全量资源索引表.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f'完整索引表已保存到: {out_dir / "明日之后体验服全量资源索引表.json"}')

# 生成Markdown摘要
print()
print('生成Markdown摘要...')

md = '# 明日之后体验服全量资源索引表\n\n'
md += f'> 扫描时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
md += f'> 根目录：`{mrzh_dir}`\n'
md += f'> 总文件数：{len(all_files)}\n'
md += f'> 总大小：{result["total_size_gb"]} GB\n\n'

md += '---\n\n'
md += '## 一、各目录统计\n\n'
md += '| 目录 | 文件数 | 总大小(GB) |\n'
md += '|---|---|---|\n'
for dir_name, stats in sorted(dir_stats.items(), key=lambda x: x[1]['total_size'], reverse=True):
    size_gb = round(stats['total_size'] / 1024 / 1024 / 1024, 2)
    md += f'| {dir_name} | {stats["file_count"]} | {size_gb} |\n'

md += '\n---\n\n'
md += '## 二、文件类型统计\n\n'
md += '| 文件类型 | 数量 | 总大小(MB) | 说明 |\n'
md += '|---|---|---|---|\n'
for ftype, stats in sorted(type_stats.items(), key=lambda x: x[1]['size'], reverse=True):
    size_mb = round(stats['size'] / 1024 / 1024, 2)
    # 获取描述
    desc = ''
    for f in all_files:
        if f['file_type'] == ftype:
            desc = f.get('description', '')
            break
    md += f'| {ftype} | {stats["count"]} | {size_mb} | {desc} |\n'

md += '\n---\n\n'
md += '## 三、高价值资源包（>100MB）\n\n'
md += '| 路径 | 类型 | 大小(MB) | 条目数 | 修改时间 |\n'
md += '|---|---|---|---|---|\n'

large_files = [f for f in all_files if f['size_mb'] > 100]
for f in sorted(large_files, key=lambda x: x['size'], reverse=True)[:100]:
    entries = f.get('entry_count', '-')
    md += f"| {f['relative_path']} | {f['file_type']} | {f['size_mb']} | {entries} | {f['mtime']} |\n"

md += '\n---\n\n'
md += '## 四、近一个月更新的大文件（>100MB）\n\n'
md += '| 路径 | 类型 | 大小(MB) | 修改时间 |\n'
md += '|---|---|---|---|\n'

recent_large = [f for f in all_files if f['is_recent'] and f['size_mb'] > 100]
for f in sorted(recent_large, key=lambda x: x['size'], reverse=True)[:50]:
    md += f"| {f['relative_path']} | {f['file_type']} | {f['size_mb']} | {f['mtime']} |\n"

with open(out_dir / '明日之后体验服全量资源索引表.md', 'w', encoding='utf-8') as f:
    f.write(md)

print(f'Markdown摘要已保存到: {out_dir / "明日之后体验服全量资源索引表.md"}')
