# -*- coding: utf-8 -*-
"""从配置表提取武器皮肤详细信息（item_id、图标路径、描述），然后搜索贴图模型。"""
from __future__ import annotations
import re, json, struct, sys
from pathlib import Path

CONFIG_PATH = Path(r'E:/提取成果/明日拆包/工具库/05_BinDict解码器/output/weapon_search/config_1B249D5C9984E1B4_script.py314.lc.bin')
OUT_DIR = Path(r'E:/提取成果/明日拆包/工具库/05_BinDict解码器/output/weapon_search')

WEAPON_NAMES = [
    '帝皇裁决', '战神烈火剑', '极光剑', '极光盾', '疾影枪',
    '极狐终结刃', '灵态诱导', '重力震爆', '阿赖耶识',
    '红太狼之怒', '灰色协议', '云上铃', '一支圣诞树',
    '千蝶一梦', '极限节拍', '鎏金锐魄',
]

raw = CONFIG_PATH.read_bytes()
text = raw.decode('utf-8', errors='ignore')

print(f'=== 配置表大小: {len(raw)} 字节 ===')
print(f'=== 提取武器皮肤详细信息 ===\n')

results = []
for name in WEAPON_NAMES:
    print(f'--- {name} ---')
    # 找所有出现位置
    positions = [m.start() for m in re.finditer(re.escape(name), text)]
    print(f'  出现次数: {len(positions)}')
    
    weapon_info = {'name': name, 'occurrences': len(positions), 'contexts': []}
    
    for pos in positions[:5]:  # 只看前5个
        start = max(0, pos - 200)
        end = min(len(text), pos + len(name) + 300)
        context = text[start:end]
        
        # 提取图标路径 (ui/item_icon/icon_xxxxxx)
        icon_matches = re.findall(r'ui/item_icon/icon_(\d+)', context)
        # 提取 item_id (数字ID)
        id_matches = re.findall(r'\b(\d{6,})\b', context)
        # 提取武器类型 (突击步枪/狙击枪/冷兵器等)
        type_matches = re.findall(r'(突击步枪|狙击枪|冷兵器|冲锋枪|霰弹枪|手枪|弓箭|榴弹炮)', context)
        
        info = {
            'position': pos,
            'icons': list(set(icon_matches)),
            'ids': list(set(id_matches))[:10],
            'types': list(set(type_matches)),
            'context_preview': context[:150].replace('\n', '\\n')
        }
        weapon_info['contexts'].append(info)
        
        print(f'  [{pos}] 图标: {icon_matches[:3]} 类型: {type_matches[:2]}')
        print(f'    上下文: ...{context[:100].replace(chr(10), " ")}...')
    
    results.append(weapon_info)
    print()

# 保存结果
out_path = OUT_DIR / '武器皮肤详细信息.json'
out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'已保存: {out_path}')

# 汇总所有图标ID
all_icons = set()
for r in results:
    for ctx in r['contexts']:
        all_icons.update(ctx['icons'])
print(f'\n=== 所有相关图标ID ({len(all_icons)}个) ===')
print(sorted(all_icons))

# 保存图标ID列表
icons_path = OUT_DIR / '武器皮肤图标ID列表.txt'
icons_path.write_text('\n'.join(sorted(all_icons)), encoding='utf-8')
print(f'已保存: {icons_path}')
