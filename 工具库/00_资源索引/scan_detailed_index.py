# -*- coding: utf-8 -*-
from pathlib import Path
import struct
import json
from collections import defaultdict

res_dir = Path(r'E:\mrzh\res')
out_dir = Path(r'E:\提取成果\明日拆包\文档索引')
out_dir.mkdir(parents=True, exist_ok=True)

def get_header(filepath, num_bytes=64):
    with open(filepath, 'rb') as f:
        return f.read(num_bytes)

def ascii_str(data):
    return ''.join(chr(b) if 32 <= b < 127 else '.' for b in data)

# 检查GPK文件头部
print('=== GPK文件头部检查 ===')
gpk_info = {}
for f in sorted(res_dir.glob('*.gpk')):
    header = get_header(f, 64)
    info = {
        'name': f.name,
        'size': f.stat().st_size,
        'size_mb': round(f.stat().st_size / 1024 / 1024, 2),
        'header_hex': header[:32].hex(),
        'header_ascii': ascii_str(header[:32]),
    }
    
    # 检查不同偏移的magic
    for offset in [0, 4, 8, 12, 16]:
        magic = header[offset:offset+4]
        if magic in (b'HPGF', b'FPGH', b'GPKF', b'FPGK'):
            info['magic_offset'] = offset
            info['magic'] = magic.decode('ascii', errors='replace')
    
    # 解析条目数（偏移20）
    try:
        entry_count = struct.unpack_from('<I', header, 20)[0]
        info['entry_count'] = entry_count
    except:
        pass
    
    # 解析条目表偏移（偏移16）
    try:
        table_offset = struct.unpack_from('<I', header, 16)[0]
        info['table_offset'] = table_offset
    except:
        pass
    
    gpk_info[f.name] = info
    print(f"  {f.name}: {info['size_mb']} MB, magic={info.get('magic', 'unknown')}, entries={info.get('entry_count', '?')}")

print()
print('=== FPK文件头部检查 ===')
fpk_info = {}
for f in sorted(res_dir.glob('*.fpk')):
    header = get_header(f, 64)
    info = {
        'name': f.name,
        'size': f.stat().st_size,
        'size_mb': round(f.stat().st_size / 1024 / 1024, 2),
        'header_hex': header[:32].hex(),
        'header_ascii': ascii_str(header[:32]),
    }
    
    # 检查magic
    magic = header[:4]
    info['magic'] = magic.decode('ascii', errors='replace')
    
    # 解析版本（偏移4）
    try:
        version = struct.unpack_from('<I', header, 4)[0]
        info['version'] = version
    except:
        pass
    
    fpk_info[f.name] = info
    print(f"  {f.name}: {info['size_mb']} MB, magic={info['magic']}, version={info.get('version', '?')}")

print()
print('=== NPK文件头部检查 ===')
npk_info = {}
for f in sorted(res_dir.glob('*.npk')):
    header = get_header(f, 64)
    info = {
        'name': f.name,
        'size': f.stat().st_size,
        'size_mb': round(f.stat().st_size / 1024 / 1024, 2),
        'header_hex': header[:32].hex(),
        'header_ascii': ascii_str(header[:32]),
    }
    magic = header[:4]
    info['magic'] = magic.decode('ascii', errors='replace')
    npk_info[f.name] = info
    print(f"  {f.name}: {info['size_mb']} MB, magic={info['magic']}")

# 保存详细索引
print()
print('保存详细索引表...')

index_data = {
    'scan_time': '2026-08-29',
    'resource_dir': str(res_dir),
    'total_files': len(gpk_info) + len(fpk_info) + len(npk_info),
    'total_size_gb': round(sum(f['size'] for f in gpk_info.values()) / 1024 / 1024 / 1024 + 
                           sum(f['size'] for f in fpk_info.values()) / 1024 / 1024 / 1024 +
                           sum(f['size'] for f in npk_info.values()) / 1024 / 1024 / 1024, 2),
    'gpk_files': gpk_info,
    'fpk_files': fpk_info,
    'npk_files': npk_info,
}

with open(out_dir / '体验服资源详细索引表.json', 'w', encoding='utf-8') as f:
    json.dump(index_data, f, ensure_ascii=False, indent=2)

print(f'详细索引表已保存到: {out_dir / "体验服资源详细索引表.json"}')
