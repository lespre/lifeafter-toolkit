# -*- coding: utf-8 -*-
"""
深入解析体验服资源包
先解密GPK/FPK头部，再解析条目信息
"""
from pathlib import Path
import struct
import json
from collections import defaultdict
from Crypto.Cipher import AES

res_dir = Path(r'E:\mrzh\res')
out_dir = Path(r'E:\提取成果\明日拆包\文档索引')
out_dir.mkdir(parents=True, exist_ok=True)

# AES密钥
AES_KEY = bytes.fromhex('606308D8A32C782013D26C2F226F686D')

def aes_ecb_decrypt(data):
    """AES-ECB解密"""
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    # 按16字节倍数补齐
    padded_len = (len(data) // 16) * 16
    if padded_len == 0:
        return data
    return cipher.decrypt(data[:padded_len])

def get_header(filepath, num_bytes=256):
    with open(filepath, 'rb') as f:
        return f.read(num_bytes)

def ascii_str(data):
    return ''.join(chr(b) if 32 <= b < 127 else '.' for b in data)

# 解析GPK文件
print('=== GPK文件深入解析 ===')
gpk_info = {}
for f in sorted(res_dir.glob('*.gpk')):
    header = get_header(f, 256)
    
    # 解密头部（前256字节）
    decrypted = aes_ecb_decrypt(header)
    
    info = {
        'name': f.name,
        'size': f.stat().st_size,
        'size_mb': round(f.stat().st_size / 1024 / 1024, 2),
        'raw_header_hex': header[:64].hex(),
        'decrypted_header_hex': decrypted[:64].hex(),
        'decrypted_header_ascii': ascii_str(decrypted[:64]),
    }
    
    # 检查解密后的magic
    for offset in [0, 4, 8, 12, 16]:
        magic = decrypted[offset:offset+4]
        if magic in (b'HPGF', b'FPGH', b'GPKF', b'FPGK', b'NXPK'):
            info['magic_offset'] = offset
            info['magic'] = magic.decode('ascii', errors='replace')
    
    # 解析条目数（偏移20）
    try:
        entry_count = struct.unpack_from('<I', decrypted, 20)[0]
        if entry_count < 10000000:  # 合理范围
            info['entry_count'] = entry_count
    except:
        pass
    
    # 解析条目表偏移（偏移16）
    try:
        table_offset = struct.unpack_from('<I', decrypted, 16)[0]
        info['table_offset'] = table_offset
    except:
        pass
    
    gpk_info[f.name] = info
    print(f"  {f.name}: {info['size_mb']} MB, magic={info.get('magic', 'unknown')}, entries={info.get('entry_count', '?')}")

print()
print('=== FPK文件深入解析 ===')
fpk_info = {}
for f in sorted(res_dir.glob('*.fpk')):
    header = get_header(f, 256)
    
    # 解密头部
    decrypted = aes_ecb_decrypt(header)
    
    info = {
        'name': f.name,
        'size': f.stat().st_size,
        'size_mb': round(f.stat().st_size / 1024 / 1024, 2),
        'raw_header_hex': header[:64].hex(),
        'decrypted_header_hex': decrypted[:64].hex(),
        'decrypted_header_ascii': ascii_str(decrypted[:64]),
    }
    
    # 检查magic
    magic = decrypted[:4]
    info['magic'] = magic.decode('ascii', errors='replace')
    
    # 解析版本（偏移4）
    try:
        version = struct.unpack_from('<I', decrypted, 4)[0]
        info['version'] = version
    except:
        pass
    
    # 解析条目数（偏移20）
    try:
        entry_count = struct.unpack_from('<I', decrypted, 20)[0]
        if entry_count < 10000000:
            info['entry_count'] = entry_count
    except:
        pass
    
    fpk_info[f.name] = info
    print(f"  {f.name}: {info['size_mb']} MB, magic={info['magic']}, version={info.get('version', '?')}, entries={info.get('entry_count', '?')}")

print()
print('=== NPK文件深入解析 ===')
npk_info = {}
for f in sorted(res_dir.glob('*.npk')):
    header = get_header(f, 256)
    decrypted = aes_ecb_decrypt(header)
    
    info = {
        'name': f.name,
        'size': f.stat().st_size,
        'size_mb': round(f.stat().st_size / 1024 / 1024, 2),
        'raw_header_hex': header[:64].hex(),
        'decrypted_header_hex': decrypted[:64].hex(),
        'decrypted_header_ascii': ascii_str(decrypted[:64]),
    }
    magic = decrypted[:4]
    info['magic'] = magic.decode('ascii', errors='replace')
    npk_info[f.name] = info
    print(f"  {f.name}: {info['size_mb']} MB, magic={info['magic']}")

# 保存详细索引
print()
print('保存深入解析索引表...')

index_data = {
    'scan_time': '2026-08-29',
    'resource_dir': str(res_dir),
    'aes_key': AES_KEY.hex(),
    'total_files': len(gpk_info) + len(fpk_info) + len(npk_info),
    'total_size_gb': round(
        sum(f['size'] for f in gpk_info.values()) / 1024 / 1024 / 1024 + 
        sum(f['size'] for f in fpk_info.values()) / 1024 / 1024 / 1024 +
        sum(f['size'] for f in npk_info.values()) / 1024 / 1024 / 1024, 2
    ),
    'gpk_files': gpk_info,
    'fpk_files': fpk_info,
    'npk_files': npk_info,
}

with open(out_dir / '体验服资源深入解析索引表.json', 'w', encoding='utf-8') as f:
    json.dump(index_data, f, ensure_ascii=False, indent=2)

print(f'深入解析索引表已保存到: {out_dir / "体验服资源深入解析索引表.json"}')

# 生成Markdown摘要
print()
print('生成Markdown摘要...')

md = '# 明日之后体验服资源深入解析索引表\n\n'
md += '> 扫描时间：2026-08-29\n'
md += f'> 总文件数：{len(gpk_info) + len(fpk_info) + len(npk_info)}\n'
md += f'> 总大小：{index_data["total_size_gb"]} GB\n\n'

md += '---\n\n'
md += '## 一、GPK资源包（55个）\n\n'
md += '| 文件名 | 大小(MB) | Magic | 条目数 | 说明 |\n'
md += '|---|---|---|---|---|\n'

# 按类别分组
categories = {
    '人物角色': [f for f in gpk_info if f.startswith('character_')],
    '建筑': [f for f in gpk_info if f.startswith('building_')],
    '场景': [f for f in gpk_info if f.startswith('scene_')],
    '模型': [f for f in gpk_info if f.startswith('model_')],
    'UI': [f for f in gpk_info if f.startswith('ui_')],
    '武器': [f for f in gpk_info if f.startswith('weapon')],
    '特效': [f for f in gpk_info if f.startswith('effect')],
    '纹理': [f for f in gpk_info if f.startswith('texture')],
    '音频': [f for f in gpk_info if f.startswith('sound')],
    '视频': [f for f in gpk_info if f.startswith('video')],
    '工具': [f for f in gpk_info if f.startswith('utility')],
}

for cat, files in categories.items():
    if files:
        md += f'\n### {cat}（{len(files)}个）\n\n'
        for fname in sorted(files):
            f = gpk_info[fname]
            md += f"| {f['name']} | {f['size_mb']} | {f.get('magic', '?')} | {f.get('entry_count', '?')} | |\n"

md += '\n---\n\n'
md += '## 二、FPK资源包（64个）\n\n'
md += '| 文件名 | 大小(MB) | Magic | 版本 | 条目数 | 说明 |\n'
md += '|---|---|---|---|---|---|\n'
for fname in sorted(fpk_info.keys()):
    f = fpk_info[fname]
    md += f"| {f['name']} | {f['size_mb']} | {f['magic']} | {f.get('version', '?')} | {f.get('entry_count', '?')} | |\n"

md += '\n---\n\n'
md += '## 三、NPK资源包（1个）\n\n'
md += '| 文件名 | 大小(MB) | Magic | 说明 |\n'
md += '|---|---|---|---|\n'
for fname in sorted(npk_info.keys()):
    f = npk_info[fname]
    md += f"| {f['name']} | {f['size_mb']} | {f['magic']} | |\n"

with open(out_dir / '体验服资源深入解析索引表.md', 'w', encoding='utf-8') as f:
    f.write(md)

print(f'Markdown摘要已保存到: {out_dir / "体验服资源深入解析索引表.md"}')
