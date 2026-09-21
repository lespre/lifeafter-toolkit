# -*- coding: utf-8 -*-
"""从配置表提取武器皮肤对应的 item_id，然后解包 weapon.gpk 查看。"""
from __future__ import annotations
import re, json, struct, os
from pathlib import Path
from Crypto.Cipher import AES

KEY = bytes.fromhex('606308D8A32C782013D26C2F226F686D')
CONFIG_PATH = Path(r'E:/提取成果/明日拆包/工具库/05_BinDict解码器/output/weapon_search/config_1B249D5C9984E1B4_script.py314.lc.bin')
OUT_DIR = Path(r'E:/提取成果/明日拆包/工具库/05_BinDict解码器/output/weapon_search')

WEAPON_NAMES = [
    '帝皇裁决', '战神烈火剑', '极光剑', '极光盾', '疾影枪',
    '极狐终结刃', '灵态诱导', '重力震爆', '阿赖耶识',
]

raw = CONFIG_PATH.read_bytes()
text = raw.decode('utf-8', errors='ignore')

print(f'=== 配置表大小: {len(raw)} 字节 ===')
print(f'=== 提取武器皮肤 item_id ===\n')

results = []
for name in WEAPON_NAMES:
    print(f'--- {name} ---')
    positions = [m.start() for m in re.finditer(re.escape(name), text)]
    
    weapon_info = {'name': name, 'item_ids': [], 'icon_ids': [], 'contexts': []}
    
    for pos in positions[:3]:
        # 扩大上下文范围，找附近的数字ID
        start = max(0, pos - 500)
        end = min(len(text), pos + len(name) + 500)
        context = text[start:end]
        
        # 找 item_id (6-7位数字，可能是武器皮肤ID)
        all_ids = re.findall(r'\b(\d{6,7})\b', context)
        # 找图标ID (icon_xxxxxx)
        icon_ids = re.findall(r'icon_(\d+)', context)
        # 找 ui/ 路径
        ui_paths = re.findall(r'ui/[A-Za-z0-9_/\.]+', context)
        
        weapon_info['item_ids'].extend(all_ids)
        weapon_info['icon_ids'].extend(icon_ids)
        weapon_info['contexts'].append({
            'position': pos,
            'ids': list(set(all_ids))[:10],
            'icons': list(set(icon_ids))[:5],
            'ui_paths': list(set(ui_paths))[:5],
            'preview': context[:200].replace('\n', '\\n')
        })
        
        print(f'  [{pos}] 数字ID: {list(set(all_ids))[:8]}')
        print(f'         图标ID: {list(set(icon_ids))[:5]}')
        print(f'         UI路径: {list(set(ui_paths))[:3]}')
    
    # 去重
    weapon_info['item_ids'] = list(set(weapon_info['item_ids']))
    weapon_info['icon_ids'] = list(set(weapon_info['icon_ids']))
    results.append(weapon_info)
    print()

# 保存结果
out_path = OUT_DIR / '武器皮肤item_id提取.json'
out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'已保存: {out_path}')

# 汇总所有可能的武器皮肤ID
all_ids = set()
for r in results:
    all_ids.update(r['item_ids'])
print(f'\n=== 所有相关数字ID ({len(all_ids)}个) ===')
print(sorted(all_ids)[:30])

# 现在解包 weapon.gpk，看看里面有什么
print(f'\n=== 解包 weapon.gpk 查看内容 ===')
def aes_ecb(data):
    pad = (16 - len(data) % 16) % 16
    return AES.new(KEY, AES.MODE_ECB).decrypt(data + b'\x00' * pad)[:len(data)]

gpk_path = Path(r'E:/mrzh/res/weapon.gpk')
if gpk_path.exists():
    with open(gpk_path, 'rb') as f:
        head = aes_ecb(f.read(32))
        entry_count = struct.unpack_from('<I', head, 20)[0]
        table_offset = struct.unpack_from('<I', head, 16)[0]
        print(f'weapon.gpk: {entry_count} 个条目')
        f.seek(table_offset)
        table = aes_ecb(f.read(entry_count * 32))
        
        # 统计文件类型
        types = {}
        sample_names = []
        for i in range(min(entry_count, 50)):  # 只看前50个
            off, comp, decomp, crc1, crc2, flag = struct.unpack_from('<IIIIII', table, i * 32)
            f.seek(off + 36)
            data = f.read(min(comp, 1024))
            try:
                if flag == 12:
                    import zstandard
                    raw_data = zstandard.ZstdDecompressor().decompress(data, max_output_size=decomp + 1024)
                elif flag == 2:
                    import lz4.block
                    raw_data = lz4.block.decompress(data, uncompressed_size=decomp)
                else:
                    raw_data = data
            except:
                raw_data = data
            
            # 判断类型
            if raw_data[:4] == b'DDS ':
                ext = '.dds'
            elif raw_data[:8] == b'\x89PNG\r\n\x1a\n':
                ext = '.png'
            elif raw_data[:4] == b'RGIS':
                ext = '.rgis (模型)'
            elif raw_data[:4] == b'\xc1\x59\x41\x0d':
                ext = '.neox_anim'
            elif raw_data[:4] == b'\x34\x80\xc8\xbb':
                ext = '.neox_skeleton'
            else:
                ext = '.bin'
            
            types[ext] = types.get(ext, 0) + 1
            if i < 10:
                sample_names.append(f'entry[{i}] {ext} size={decomp}')
        
        print(f'文件类型统计 (前50个): {types}')
        print(f'前10个样本:')
        for s in sample_names:
            print(f'  {s}')
else:
    print('weapon.gpk 不存在')
