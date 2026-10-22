# -*- coding: utf-8 -*-
"""直接在 gpk 包里搜索关键词（不需要全量解包）。"""
from __future__ import annotations
import struct, sys, os
from pathlib import Path
from Crypto.Cipher import AES

KEY = bytes.fromhex('606308D8A32C782013D26C2F226F686D')
GPK_DIR = Path(r'E:/mrzh/res')
KEYWORD = sys.argv[1] if len(sys.argv) > 1 else '战神烈火剑'

def aes_ecb(data):
    pad = (16 - len(data) % 16) % 16
    return AES.new(KEY, AES.MODE_ECB).decrypt(data + b'\x00' * pad)[:len(data)]

def search_in_gpk(gpk_path, keyword):
    keyword_bytes = keyword.encode('utf-8')
    keyword_gbk = keyword.encode('gbk', errors='ignore')
    hits = []
    with open(gpk_path, 'rb') as f:
        # 解密头部
        head = aes_ecb(f.read(32))
        if head[8:12] != b'NXPK':
            return hits
        entry_count = struct.unpack_from('<I', head, 20)[0]
        table_offset = struct.unpack_from('<I', head, 16)[0]
        # 解密条目表
        f.seek(table_offset)
        table = aes_ecb(f.read(entry_count * 32))
        # 遍历每个条目
        for i in range(entry_count):
            off, comp, decomp, crc1, crc2, flag = struct.unpack_from('<IIIIII', table, i * 32)
            if comp > 50 * 1024 * 1024:  # 跳过太大的
                continue
            f.seek(off + 36)
            data = f.read(comp)
            # 尝试解压
            try:
                if flag == 2:  # lz4
                    import lz4.block
                    raw = lz4.block.decompress(data, uncompressed_size=decomp)
                elif flag == 12:  # zstd
                    import zstandard
                    raw = zstandard.ZstdDecompressor().decompress(data, max_output_size=decomp + 1024)
                else:
                    raw = data
            except:
                continue
            # 搜索关键词
            if keyword_bytes in raw or keyword_gbk in raw:
                # 找到上下文
                idx = raw.find(keyword_bytes)
                if idx < 0:
                    idx = raw.find(keyword_gbk)
                context = raw[max(0, idx - 50):idx + len(keyword_bytes) + 50]
                hits.append({
                    'entry': i,
                    'offset': off + 36,
                    'size': decomp,
                    'flag': flag,
                    'context': context.decode('utf-8', errors='replace')
                })
    return hits

print(f'=== 在 gpk 包里搜索: {KEYWORD} ===')
print(f'搜索目录: {GPK_DIR}')
print()

gpk_files = sorted(GPK_DIR.glob('*.gpk'))
print(f'共 {len(gpk_files)} 个 gpk 文件')
print()

total_hits = 0
for gpk in gpk_files:
    hits = search_in_gpk(gpk, KEYWORD)
    if hits:
        print(f'--- {gpk.name}: {len(hits)} 条命中 ---')
        for h in hits[:5]:
            print(f'  entry[{h["entry"]}] size={h["size"]} flag={h["flag"]}')
            print(f'    上下文: ...{h["context"]}...')
        total_hits += len(hits)
    else:
        print(f'  {gpk.name}: 0 命中')

print()
print(f'=== 总计: {total_hits} 条命中 ===')
