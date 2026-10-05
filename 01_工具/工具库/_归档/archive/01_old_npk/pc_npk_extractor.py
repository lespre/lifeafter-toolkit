#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
明日之后 PC 端 script*.npk 定点提取器
格式：NXPK（AES-ECB 加密头/表 + 48字节条目 + flag 0/2/12 解压）
path_id：双 Murmur3 x86_32（高 seed 0x77777777，低 seed 0x66666666）
依赖：pip install pycryptodome lz4 zstandard
"""
import os, sys, struct, hashlib, json, zlib
from pathlib import Path
from Crypto.Cipher import AES
import lz4.block as lz4block
import zstandard

KEY = bytes.fromhex('606308D8A32C782013D26C2F226F686D')

def aes_ecb(data: bytes) -> bytes:
    """AES-ECB 解密（按16字节对齐，尾部原样保留）"""
    usable = len(data) // 16 * 16
    if not usable:
        return data
    cipher = AES.new(KEY, AES.MODE_ECB)
    return cipher.decrypt(data[:usable]) + data[usable:]

def murmur3_x86_32(data: bytes, seed: int) -> int:
    """Murmur3 x86 32位"""
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
    """双 Murmur3 计算文件 ID"""
    encoded = logical_path.encode('utf-8')
    return (murmur3_x86_32(encoded, 0x77777777) << 32) | murmur3_x86_32(encoded, 0x66666666)

def unpack_entry(packed: bytes, expected_size: int, flag: int) -> bytes:
    """根据 flag 解压条目"""
    if flag == 2:
        return lz4block.decompress(packed, uncompressed_size=expected_size)
    if flag == 12:
        return zstandard.ZstdDecompressor().decompress(packed, max_output_size=expected_size)
    if flag == 0:
        decrypted = aes_ecb(packed) if len(packed) >= 16 else packed
        # flag=0 的条目可能是 AES+zlib 包装：前18字节头，之后 zlib
        if len(decrypted) >= 18 and struct.unpack_from('<Q', decrypted, 0)[0] == 1:
            if decrypted[16:18] in (b'\x78\x9c', b'\x78\xda', b'\x78\x01'):
                try:
                    return zlib.decompress(decrypted[18:])
                except zlib.error:
                    return zlib.decompress(decrypted[18:], -15)
        return packed
    return packed

def parse_npk(npk_path: str):
    """解析 NXPK 包，返回 (header_info, entry_index)"""
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
            index[fid] = (i, fid, off, ps, ds, ca, cb, flag)

    return {
        'path': str(npk_path),
        'size': npk_path.stat().st_size,
        'version': version,
        'entry_count': entry_count,
        'table_offset': table_offset,
    }, index

def extract_by_path(npk_path: str, logical_paths: list, output_dir: str):
    """按逻辑路径提取文件"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    header, index = parse_npk(npk_path)
    print(f'包: {header["path"]} ({header["size"]//1024//1024} MB, {header["entry_count"]} 条目)')

    results = []
    with open(npk_path, 'rb') as f:
        for logical in logical_paths:
            fid = path_id(logical)
            if fid not in index:
                print(f'  未找到: {logical} (fid={fid:016X})')
                results.append({'path': logical, 'status': 'not_found', 'file_id': f'{fid:016X}'})
                continue

            i, entry_fid, off, ps, ds, ca, cb, flag = index[fid]
            f.seek(off)
            packed = f.read(ps)
            raw = unpack_entry(packed, ds, flag)

            out_name = f'{Path(logical).stem}_{fid:016X}.bin'
            out_path = output_dir / out_name
            out_path.write_bytes(raw)

            results.append({
                'path': logical,
                'status': 'extracted',
                'file_id': f'{fid:016X}',
                'entry_index': i,
                'offset': off,
                'packed_size': ps,
                'declared_size': ds,
                'flag': flag,
                'raw_size': len(raw),
                'raw_sha256': hashlib.sha256(raw).hexdigest(),
                'output': str(out_path),
            })
            print(f'  提取: {logical} → {out_name} ({len(raw)} bytes, flag={flag})')

    report_path = output_dir / '_extract_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({'source': header, 'results': results}, f, ensure_ascii=False, indent=2)

    return results

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('用法:')
        print('  python pc_npk_extractor.py <npk_path> <output_dir> <logical_path1> [logical_path2] ...')
        print('示例:')
        print('  python pc_npk_extractor.py E:\\mrzh\\Documents\\script.py3.npk E:\\attr_out com\\cdata\\attribute_data.nxs com\\cdata\\attribute_data_chs.nxs')
        sys.exit(1)

    npk_path = sys.argv[1]
    output_dir = sys.argv[2]
    logical_paths = sys.argv[3:]
    extract_by_path(npk_path, logical_paths, output_dir)
