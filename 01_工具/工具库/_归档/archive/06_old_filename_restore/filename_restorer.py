#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
明日之后 NPK 文件名还原工具
原理：双 Murmur3 x86_32 计算 path_id，与 NPK 条目表匹配
路径字典来源：脚本 import 语句、已知逻辑路径、FPK manifest
"""
import os, sys, struct, re, json
from pathlib import Path
from Crypto.Cipher import AES

KEY = bytes.fromhex('606308D8A32C782013D26C2F226F686D')

def aes_ecb(data: bytes) -> bytes:
    usable = len(data) // 16 * 16
    if not usable:
        return data
    cipher = AES.new(KEY, AES.MODE_ECB)
    return cipher.decrypt(data[:usable]) + data[usable:]

def murmur3_x86_32(data: bytes, seed: int) -> int:
    c1, c2 = 0xCC9E2D51, 0x1B873593
    value = seed & 0xFFFFFFFF
    end = len(data) & ~3
    for offset in range(0, end, 4):
        block = int.from_bytes(data[offset:offset + 4], 'little')
        block = (block * c1) & 0xFFFFFFFF
        block = ((block << 15) | (block >> 17)) & 0xFFFFFFFF
        block = (block * c2) & 0xFFFFFFFF
        value ^= block
        value = ((value << 13) | (value >> 19)) & 0xFFFFFFFF
        value = (value * 5 + 0xE6546B64) & 0xFFFFFFFF
    tail = data[end:]
    block = 0
    if len(tail) >= 3:
        block ^= tail[2] << 16
    if len(tail) >= 2:
        block ^= tail[1] << 8
    if tail:
        block ^= tail[0]
        block = (block * c1) & 0xFFFFFFFF
        block = ((block << 15) | (block >> 17)) & 0xFFFFFFFF
        block = (block * c2) & 0xFFFFFFFF
        value ^= block
    value ^= len(data)
    value ^= value >> 16
    value = (value * 0x85EBCA6B) & 0xFFFFFFFF
    value ^= value >> 13
    value = (value * 0xC2B2AE35) & 0xFFFFFFFF
    value ^= value >> 16
    return value & 0xFFFFFFFF

def path_id(logical_path: str) -> int:
    encoded = logical_path.encode('utf-8')
    return (murmur3_x86_32(encoded, 0x77777777) << 32) | murmur3_x86_32(encoded, 0x66666666)

def parse_npk_entry_table(npk_path: str) -> dict:
    """读取 NPK 条目表，返回 {file_id: (entry_index, offset, packed_size, flag)}"""
    npk_path = Path(npk_path)
    with open(npk_path, 'rb') as f:
        header = aes_ecb(f.read(32))
        _reserved, magic, version, table_offset, entry_count = struct.unpack_from('<QIIII', header)
        if magic != 0x4B50584E:
            raise ValueError(f'不是 NXPK 包: magic=0x{magic:08x}')
        f.seek(table_offset)
        table = aes_ecb(f.read(entry_count * 48))
        index = {}
        for i in range(entry_count):
            fid, off, ps, ds, ca, cb, flag = struct.unpack_from('<QIIIIIi', table, i * 48)
            index[fid] = (i, off, ps, ds, flag)
    return index

def collect_paths_from_scripts(script_dir: str) -> set:
    """从脚本文件的 import 语句中收集逻辑路径"""
    paths = set()
    script_dir = Path(script_dir)
    if not script_dir.exists():
        return paths
    import_pattern = re.compile(r'(?:from|import)\s+([a-zA-Z_][a-zA-Z0-9_.]*)')
    for root, dirs, files in os.walk(script_dir):
        for f in files:
            if f.endswith(('.py', '.txt', '.json')):
                try:
                    content = Path(root, f).read_text(encoding='utf-8', errors='ignore')
                except:
                    continue
                for match in import_pattern.finditer(content):
                    module = match.group(1)
                    # com.utils.xxx -> com\xxx\xxx.nxs
                    parts = module.split('.')
                    if len(parts) >= 2 and parts[0] in ('com', 'game', 'ui', 'config'):
                        logical = '\\'.join(parts) + '.nxs'
                        paths.add(logical)
                        logical_py = '\\'.join(parts) + '.py'
                        paths.add(logical_py)
    return paths

def build_known_paths() -> set:
    """已知的逻辑路径列表（从之前的提取中验证过的）"""
    paths = set()
    # 已验证的配置表
    known = [
        r'com\cdata\attribute_data.nxs',
        r'com\cdata\attribute_data_chs.nxs',
        r'com\cdata\attribute_data_kj1.nxs',
        r'com\cdata\attribute_data_yk.nxs',
        r'com\utils\AttributeHelper.nxs',
        r'com\utils\GmCmdParser.nxs',
        r'com\equip\Equip.nxs',
        r'com\utils\SocItemHelpers.nxs',
        r'com\components\avatar\EquipComp.nxs',
        r'com\cdata\advanced_recipe_consume_conf_auto_oversea_data_kj1.nxs',
        r'com\cdata\advanced_recipe_consume_conf_auto_oversea_data.nxs',
        r'com\cdata\common_item_data.nxs',
        r'com\cdata\common_item_data_chs.nxs',
        r'com\cdata\all_equips.nxs',
        r'com\cdata\all_equips_chs.nxs',
        r'com\cdata\all_equips_base.nxs',
    ]
    paths.update(known)
    # 生成常见前缀组合
    prefixes = ['com', 'game', 'ui', 'config', 'data']
    modules = ['cdata', 'utils', 'equip', 'components', 'ui', 'config', 'game', 'scene', 'entity', 'manager', 'helper', 'model', 'view', 'controller']
    for p in prefixes:
        for m in modules:
            for ext in ['.nxs', '.py']:
                paths.add(f'{p}\\{m}{ext}')
    return paths

def restore_filenames(npk_path: str, path_dict: set, output_dir: str = None):
    """主函数：批量计算 path_id 并匹配 NPK 条目表"""
    print(f'=== 文件名还原: {npk_path} ===')

    # 读取 NPK 条目表
    index = parse_npk_entry_table(npk_path)
    print(f'NPK 条目数: {len(index)}')

    # 批量计算 path_id
    path_to_id = {}
    id_to_path = {}
    for p in path_dict:
        fid = path_id(p)
        path_to_id[p] = fid
        if fid in id_to_path:
            id_to_path[fid].append(p)
        else:
            id_to_path[fid] = [p]

    print(f'路径字典大小: {len(path_dict)}')

    # 匹配
    matched = []
    unmatched_ids = set(index.keys())
    for fid, paths in id_to_path.items():
        if fid in index:
            entry_idx, off, ps, ds, flag = index[fid]
            for p in paths:
                matched.append({
                    'logical_path': p,
                    'file_id': f'{fid:016X}',
                    'entry_index': entry_idx,
                    'offset': off,
                    'packed_size': ps,
                    'declared_size': ds,
                    'flag': flag,
                })
            unmatched_ids.discard(fid)

    print(f'匹配成功: {len(matched)}')
    print(f'未匹配: {len(unmatched_ids)}')
    print(f'还原率: {len(matched)/len(index)*100:.1f}%')

    # 输出
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        report = {
            'npk_path': str(npk_path),
            'total_entries': len(index),
            'path_dict_size': len(path_dict),
            'matched_count': len(matched),
            'unmatched_count': len(unmatched_ids),
            'restore_rate': f'{len(matched)/len(index)*100:.1f}%',
            'matched': sorted(matched, key=lambda x: x['entry_index']),
        }
        report_path = output_dir / f'filename_restore_{Path(npk_path).stem}.json'
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'报告已保存: {report_path}')

        # 保存未匹配的 file_id 供后续分析
        unmatched_path = output_dir / f'unmatched_ids_{Path(npk_path).stem}.txt'
        with open(unmatched_path, 'w', encoding='utf-8') as f:
            for fid in sorted(unmatched_ids):
                entry_idx, off, ps, ds, flag = index[fid]
                f.write(f'{fid:016X}\tentry={entry_idx}\toff={off}\tsize={ps}\tflag={flag}\n')
        print(f'未匹配 ID 列表: {unmatched_path}')

    return matched, unmatched_ids

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法:')
        print('  python filename_restorer.py <npk_path> [script_dir] [output_dir]')
        print('示例:')
        print('  python filename_restorer.py E:\\mrzh\\Documents\\script.py3.npk E:\\mrzh\\gpk_unpacked E:\\restore_out')
        print('  python filename_restorer.py E:\\mrzh\\Documents\\script.npk')
        sys.exit(1)

    npk_path = sys.argv[1]
    script_dir = sys.argv[2] if len(sys.argv) > 2 else None
    output_dir = sys.argv[3] if len(sys.argv) > 3 else 'filename_restore_output'

    # 构建路径字典
    path_dict = build_known_paths()
    print(f'已知路径: {len(path_dict)}')

    if script_dir:
        script_paths = collect_paths_from_scripts(script_dir)
        path_dict.update(script_paths)
        print(f'从脚本收集: {len(script_paths)}')

    print(f'路径字典总计: {len(path_dict)}')

    # 还原
    matched, unmatched = restore_filenames(npk_path, path_dict, output_dir)

    # 打印前 20 个匹配结果
    print('\n=== 匹配结果（前20条）===')
    for m in sorted(matched, key=lambda x: x['entry_index'])[:20]:
        print(f"  [{m['entry_index']:5d}] {m['logical_path']:50s} flag={m['flag']} size={m['packed_size']}")
