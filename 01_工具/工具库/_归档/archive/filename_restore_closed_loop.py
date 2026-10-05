# -*- coding: utf-8 -*-
"""文件名还原闭环：从 NPK 脚本内容提取 import 路径 → 计算 path_id → 匹配条目表。

思路：
1. 读取 NPK 条目表
2. 逐个解包条目到内存（不写文件）
3. 从解包后的内容中提取 import 路径（Python import 语句 / 字符串中的逻辑路径）
4. 计算 path_id（双 Murmur3），匹配条目表
5. 输出匹配结果，扩大路径字典

只读源，不写解包产物。
"""
from __future__ import annotations
import hashlib, importlib.util, json, re, struct, sys
from pathlib import Path

PKG = Path(r'E:\mrzh\Documents\script.py314.lc.npk')
READER = Path(r'E:\提取成果\明日之后拆包工具\npk_reader.py')
OUT = Path(r'E:\提取成果\filename_restore_output')

# import 路径提取模式
IMPORT_PATTERNS = [
    re.compile(rb'from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import'),
    re.compile(rb'import\s+([a-zA-Z_][a-zA-Z0-9_.]*)'),
    re.compile(rb'__import__\s*\(\s*[\'"]([a-zA-Z_][a-zA-Z0-9_.]*)[\'"]'),
]
# 字符串中的逻辑路径（com\xxx\yyy 或 com/xxx/yyy）
LOGICAL_PATH_PATTERN = re.compile(rb'([a-zA-Z_][a-zA-Z0-9_]*(?:[\\/][a-zA-Z_][a-zA-Z0-9_]*)+)')


def murmur3_x86_32(data: bytes, seed: int) -> int:
    """MurmurHash3 x86 32-bit."""
    c1 = 0xcc9e2d51
    c2 = 0x1b873593
    length = len(data)
    h1 = seed & 0xffffffff
    rounded_end = (length & ~0x3)
    for i in range(0, rounded_end, 4):
        k1 = (data[i] | (data[i+1] << 8) | (data[i+2] << 16) | (data[i+3] << 24)) & 0xffffffff
        k1 = (k1 * c1) & 0xffffffff
        k1 = ((k1 << 15) | (k1 >> 17)) & 0xffffffff
        k1 = (k1 * c2) & 0xffffffff
        h1 ^= k1
        h1 = ((h1 << 13) | (h1 >> 19)) & 0xffffffff
        h1 = (h1 * 5 + 0xe6546b64) & 0xffffffff
    k1 = 0
    tail_index = rounded_end
    tail_size = length & 0x3
    if tail_size >= 3:
        k1 ^= data[tail_index + 2] << 16
    if tail_size >= 2:
        k1 ^= data[tail_index + 1] << 8
    if tail_size >= 1:
        k1 ^= data[tail_index]
        k1 = (k1 * c1) & 0xffffffff
        k1 = ((k1 << 15) | (k1 >> 17)) & 0xffffffff
        k1 = (k1 * c2) & 0xffffffff
        h1 ^= k1
    h1 ^= length
    h1 ^= h1 >> 16
    h1 = (h1 * 0x85ebca6b) & 0xffffffff
    h1 ^= h1 >> 13
    h1 = (h1 * 0xc2b2ae35) & 0xffffffff
    h1 ^= h1 >> 16
    return h1 & 0xffffffff


def path_id(logical_path: str) -> int:
    """逻辑路径 → 64位 file_id（双 Murmur3 x86_32）。"""
    data = logical_path.encode('utf-8')
    high = murmur3_x86_32(data, 0x77777777)
    low = murmur3_x86_32(data, 0x66666666)
    return (high << 32) | low


def load_reader():
    spec = importlib.util.spec_from_file_location('npk_reader', READER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def extract_import_paths(content: bytes) -> set:
    """从脚本内容中提取 import 路径，返回逻辑路径集合。"""
    paths = set()
    # 1. Python import 语句
    for pat in IMPORT_PATTERNS:
        for m in pat.finditer(content):
            module = m.group(1).decode('ascii', errors='ignore')
            parts = module.split('.')
            if len(parts) >= 2 and parts[0] in ('com', 'game', 'ui', 'config', 'data', 'scene', 'entity'):
                logical = '\\'.join(parts) + '.nxs'
                paths.add(logical)
                logical_py = '\\'.join(parts) + '.py'
                paths.add(logical_py)
    # 2. 字符串中的逻辑路径
    for m in LOGICAL_PATH_PATTERN.finditer(content):
        raw = m.group(1)
        try:
            s = raw.decode('ascii', errors='ignore')
        except:
            continue
        # 规范化分隔符
        s = s.replace('/', '\\')
        parts = s.split('\\')
        if len(parts) >= 2 and parts[0] in ('com', 'game', 'ui', 'config', 'data', 'scene', 'entity'):
            if not s.endswith(('.nxs', '.py', '.json', '.xml', '.cfg')):
                s += '.nxs'
            paths.add(s)
    return paths


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    reader = load_reader()

    # 1. 读取 NPK 条目表
    with PKG.open('rb') as f:
        _r, magic, version, table_offset, entry_count = struct.unpack_from('<QIIII', reader.aes_ecb(f.read(32)))
        if magic != 0x4b50584e:
            raise ValueError(f'NXPK magic mismatch: {magic:#x}')
        print(f'NPK: version={version}, entries={entry_count}, table_offset={table_offset}')

        f.seek(table_offset)
        table = reader.aes_ecb(f.read(entry_count * 48))

    entries = []
    id_to_entry = {}
    for i in range(entry_count):
        fid, off, ps, ds, a, b, flag = struct.unpack_from('<QIIIIIi', table, i * 48)
        entries.append({'index': i, 'file_id': fid, 'offset': off, 'packed': ps, 'decoded': ds, 'flag': flag})
        id_to_entry[fid] = i

    print(f'条目表读取完成: {len(entries)} 条')

    # 2. 逐个解包条目，提取 import 路径
    all_paths = set()
    extracted_count = 0
    fail_count = 0

    with PKG.open('rb') as f:
        for i, entry in enumerate(entries):
            try:
                f.seek(entry['offset'])
                packed = f.read(entry['packed'])
                if len(packed) != entry['packed']:
                    continue
                raw = reader.unpack_entry(packed, entry['decoded'], entry['flag'])
                paths = extract_import_paths(raw)
                if paths:
                    all_paths.update(paths)
                    extracted_count += 1
            except Exception:
                fail_count += 1
                continue

            if (i + 1) % 5000 == 0:
                print(f'  进度: {i+1}/{entry_count}, 提取到路径的条目: {extracted_count}, 唯一路径: {len(all_paths)}')

    print(f'\n解包完成: 成功提取 {extracted_count} 个条目的 import, 失败 {fail_count} 个')
    print(f'唯一逻辑路径: {len(all_paths)}')

    # 3. 计算 path_id，匹配条目表
    matched = []
    unmatched_paths = []
    for logical in sorted(all_paths):
        fid = path_id(logical)
        if fid in id_to_entry:
            entry_idx = id_to_entry[fid]
            matched.append({'logical_path': logical, 'file_id': f'{fid:016X}', 'entry_index': entry_idx})
        else:
            unmatched_paths.append(logical)

    print(f'\n匹配结果: 成功 {len(matched)}, 未匹配 {len(unmatched_paths)}')

    # 4. 保存结果
    report = {
        'source': str(PKG),
        'entry_count': entry_count,
        'extracted_entries': extracted_count,
        'unique_paths': len(all_paths),
        'matched': len(matched),
        'unmatched_paths': len(unmatched_paths),
        'matched_entries': matched,
    }
    report_path = OUT / 'filename_restore_closed_loop.json'
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    # 保存扩大的路径字典
    dict_path = OUT / 'path_dictionary_closed_loop.txt'
    with dict_path.open('w', encoding='utf-8') as f:
        for p in sorted(all_paths):
            f.write(p + '\n')

    print(f'\n报告已保存: {report_path}')
    print(f'路径字典已保存: {dict_path}')

    # 打印前30个匹配
    print('\n=== 匹配结果（前30条）===')
    for m in matched[:30]:
        print(f"  [{m['entry_index']:5d}] {m['logical_path']}")


if __name__ == '__main__':
    main()
