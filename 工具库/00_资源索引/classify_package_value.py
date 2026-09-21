# -*- coding: utf-8 -*-
"""
资源包价值分类
- 场景、建筑、PVE相关：低价值（不拆）
- 近一个月内更新：高价值
- 其他：中价值
"""
from pathlib import Path
import struct
import json
from datetime import datetime, timedelta
from Crypto.Cipher import AES

res_dir = Path(r'E:\mrzh\res')
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
    with open(filepath, 'rb') as f:
        return f.read(num_bytes)

# 近一个月的时间阈值（2026年7月29日）
threshold_date = datetime(2026, 7, 29)

# 低价值关键词（场景、建筑、PVE）
low_value_keywords = [
    'scene_', 'building_', 'scene_bw_',
    'utility_scene', 'textures_bw',
]

# PVE相关关键词
pve_keywords = [
    'pve', '副本', '战役', '闯关',
]

print('=== 资源包价值分类 ===')
print(f'近一个月阈值: {threshold_date.strftime("%Y-%m-%d")}')
print()

all_packages = []

for f in sorted(res_dir.iterdir()):
    if not f.is_file():
        continue
    
    # 获取修改时间
    mtime = datetime.fromtimestamp(f.stat().st_mtime)
    is_recent = mtime >= threshold_date
    
    # 获取文件信息
    ext = f.suffix.lower()
    name = f.name
    size = f.stat().st_size
    size_mb = round(size / 1024 / 1024, 2)
    
    # 解析条目数
    entry_count = None
    if ext in ('.gpk', '.fpk'):
        try:
            header = get_header(f, 256)
            decrypted = aes_ecb_decrypt(header)
            entry_count = struct.unpack_from('<I', decrypted, 20)[0]
            if entry_count > 10000000:
                entry_count = None
        except:
            pass
    
    # 判断价值等级
    value_level = '中价值'
    value_reason = []
    
    # 检查低价值关键词
    for kw in low_value_keywords:
        if kw in name.lower():
            value_level = '低价值'
            value_reason.append(f'包含关键词: {kw}')
            break
    
    # 检查PVE关键词
    for kw in pve_keywords:
        if kw in name.lower():
            value_level = '低价值'
            value_reason.append(f'PVE相关: {kw}')
            break
    
    # 近一个月更新 -> 高价值（覆盖低价值判断）
    if is_recent:
        if value_level == '低价值':
            value_level = '中价值'
            value_reason.append('近一个月更新，提升为中价值')
        else:
            value_level = '高价值'
            value_reason.append('近一个月更新')
    
    # 特定高价值包
    high_value_packages = [
        'ui_01.gpk', 'ui_02.gpk', 'ui_03.gpk', 'ui_04.gpk', 'ui_05.gpk',
        'weapon.gpk', 'character_01.gpk', 'character_02.gpk', 'character_03.gpk',
        'character_04.gpk', 'character_05.gpk', 'character_06.gpk', 'character_07.gpk',
        'character_08.gpk', 'character_09.gpk', 'sound.gpk', 'ui.npk',
    ]
    
    if name in high_value_packages and value_level != '高价值':
        if not is_recent:
            value_level = '中价值'
            value_reason.append('核心资源包')
    
    # 体验服独有FPK标记
    is_exclusive = False
    if ext == '.fpk':
        # 提取编号
        try:
            num = int(name.replace('.fpk', ''))
            if (2 <= num <= 14) or (23 <= num <= 64):
                is_exclusive = True
                if value_level == '低价值':
                    value_level = '中价值'
                    value_reason.append('体验服独有FPK')
        except:
            pass
    
    pkg_info = {
        'name': name,
        'extension': ext,
        'size': size,
        'size_mb': size_mb,
        'mtime': mtime.strftime('%Y-%m-%d %H:%M:%S'),
        'is_recent': is_recent,
        'entry_count': entry_count,
        'value_level': value_level,
        'value_reason': value_reason,
        'is_exclusive_fpk': is_exclusive,
    }
    
    all_packages.append(pkg_info)
    
    # 打印
    level_icon = {'高价值': '🔴', '中价值': '🟡', '低价值': '⚪'}
    icon = level_icon.get(value_level, '⚪')
    recent_mark = ' [近一月]' if is_recent else ''
    exclusive_mark = ' [体验服独有]' if is_exclusive else ''
    entries = f', {entry_count}条目' if entry_count else ''
    reason = f' ({", ".join(value_reason)})' if value_reason else ''
    
    print(f'{icon} {name}: {size_mb} MB{entries}{recent_mark}{exclusive_mark} -> {value_level}{reason}')

# 统计
print()
print('=' * 80)
print('统计汇总')
print('=' * 80)

high_value = [p for p in all_packages if p['value_level'] == '高价值']
mid_value = [p for p in all_packages if p['value_level'] == '中价值']
low_value = [p for p in all_packages if p['value_level'] == '低价值']

print(f'高价值: {len(high_value)}个, {sum(p["size_mb"] for p in high_value):.2f} MB')
print(f'中价值: {len(mid_value)}个, {sum(p["size_mb"] for p in mid_value):.2f} MB')
print(f'低价值: {len(low_value)}个, {sum(p["size_mb"] for p in low_value):.2f} MB')

print()
print('近一个月更新的文件:')
for p in all_packages:
    if p['is_recent']:
        print(f'  {p["name"]}: {p["mtime"]} ({p["value_level"]})')

# 保存
print()
print('保存价值分类索引表...')

result = {
    'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'threshold_date': threshold_date.strftime('%Y-%m-%d'),
    'total_packages': len(all_packages),
    'high_value_count': len(high_value),
    'mid_value_count': len(mid_value),
    'low_value_count': len(low_value),
    'packages': all_packages,
}

with open(out_dir / '资源包价值分类索引表.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f'已保存到: {out_dir / "资源包价值分类索引表.json"}')

# 生成Markdown
md = '# 明日之后体验服资源包价值分类索引表\n\n'
md += f'> 生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
md += f'> 近一个月阈值：{threshold_date.strftime("%Y-%m-%d")}\n'
md += f'> 总资源包数：{len(all_packages)}\n\n'

md += '---\n\n'
md += '## 统计汇总\n\n'
md += '| 价值等级 | 数量 | 总大小(MB) | 说明 |\n'
md += '|---|---|---|---|\n'
md += f'| 🔴 高价值 | {len(high_value)} | {sum(p["size_mb"] for p in high_value):.2f} | 近一个月更新，优先拆包 |\n'
md += f'| 🟡 中价值 | {len(mid_value)} | {sum(p["size_mb"] for p in mid_value):.2f} | 核心资源或体验服独有 |\n'
md += f'| ⚪ 低价值 | {len(low_value)} | {sum(p["size_mb"] for p in low_value):.2f} | 场景/建筑/PVE，暂不拆 |\n'

md += '\n---\n\n'
md += '## 🔴 高价值资源包（近一个月更新，优先拆包）\n\n'
md += '| 文件名 | 大小(MB) | 条目数 | 修改时间 | 说明 |\n'
md += '|---|---|---|---|---|\n'
for p in sorted(high_value, key=lambda x: x['size'], reverse=True):
    entries = p['entry_count'] if p['entry_count'] else '-'
    reason = ', '.join(p['value_reason'])
    md += f"| {p['name']} | {p['size_mb']} | {entries} | {p['mtime']} | {reason} |\n"

md += '\n---\n\n'
md += '## 🟡 中价值资源包（核心资源或体验服独有）\n\n'
md += '| 文件名 | 大小(MB) | 条目数 | 修改时间 | 说明 |\n'
md += '|---|---|---|---|---|\n'
for p in sorted(mid_value, key=lambda x: x['size'], reverse=True):
    entries = p['entry_count'] if p['entry_count'] else '-'
    reason = ', '.join(p['value_reason'])
    md += f"| {p['name']} | {p['size_mb']} | {entries} | {p['mtime']} | {reason} |\n"

md += '\n---\n\n'
md += '## ⚪ 低价值资源包（场景/建筑/PVE，暂不拆）\n\n'
md += '| 文件名 | 大小(MB) | 条目数 | 修改时间 | 说明 |\n'
md += '|---|---|---|---|---|\n'
for p in sorted(low_value, key=lambda x: x['size'], reverse=True):
    entries = p['entry_count'] if p['entry_count'] else '-'
    reason = ', '.join(p['value_reason'])
    md += f"| {p['name']} | {p['size_mb']} | {entries} | {p['mtime']} | {reason} |\n"

with open(out_dir / '资源包价值分类索引表.md', 'w', encoding='utf-8') as f:
    f.write(md)

print(f'Markdown已保存到: {out_dir / "资源包价值分类索引表.md"}')
