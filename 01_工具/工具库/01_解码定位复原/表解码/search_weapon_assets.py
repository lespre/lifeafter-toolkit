# -*- coding: utf-8 -*-
"""用拼音/英文名在 gpk 包里搜索武器皮肤的贴图和模型。"""
from __future__ import annotations
import struct, sys, os, re
from pathlib import Path
from Crypto.Cipher import AES

KEY = bytes.fromhex('606308D8A32C782013D26C2F226F686D')
GPK_DIR = Path(r'E:/mrzh/res')

# 武器皮肤关键词（拼音/英文名/缩写）
KEYWORDS = [
    # 铠甲勇士联动
    b'dihuang', b'caijue', b'zhanshen', b'liehuo', b'jiguang',
    b'jiying', b'xingtian', b'feiying', b'dihuangxia',
    # 其他武器皮肤
    b'jifu', b'lingtai', b'zhongli', b'zhendong', b'alaye',
    b'hongtailang', b'huise', b'yunshang', b'shengdanshu',
    b'qiandie', b'jixian', b'liujin',
    # 通用武器皮肤关键词
    b'weapon_skin', b'wpn_skin', b'skin_', b'weapon_',
    b'wpn_', b'firearm', b'rifle', b'sniper', b'pistol',
]

def aes_ecb(data):
    pad = (16 - len(data) % 16) % 16
    return AES.new(KEY, AES.MODE_ECB).decrypt(data + b'\x00' * pad)[:len(data)]

def search_in_gpk(gpk_path, keywords):
    hits = {kw: [] for kw in keywords}
    with open(gpk_path, 'rb') as f:
        head = aes_ecb(f.read(32))
        if head[8:12] != b'NXPK':
            return hits
        entry_count = struct.unpack_from('<I', head, 20)[0]
        table_offset = struct.unpack_from('<I', head, 16)[0]
        f.seek(table_offset)
        table = aes_ecb(f.read(entry_count * 32))
        for i in range(entry_count):
            off, comp, decomp, crc1, crc2, flag = struct.unpack_from('<IIIIII', table, i * 32)
            if comp > 20 * 1024 * 1024:
                continue
            f.seek(off + 36)
            data = f.read(comp)
            try:
                if flag == 2:
                    import lz4.block
                    raw = lz4.block.decompress(data, uncompressed_size=decomp)
                elif flag == 12:
                    import zstandard
                    raw = zstandard.ZstdDecompressor().decompress(data, max_output_size=decomp + 1024)
                else:
                    raw = data
            except:
                continue
            # 搜索关键词
            for kw in keywords:
                if kw in raw:
                    # 找上下文
                    idx = raw.find(kw)
                    context = raw[max(0, idx-30):idx+len(kw)+50]
                    # 尝试提取路径/文件名
                    path_match = re.search(rb'[A-Za-z0-9_/\\.]{5,}\.(?:png|dds|jpg|mesh|mat|anim|json|bin)', context)
                    hits[kw].append({
                        'entry': i,
                        'size': decomp,
                        'context': context.decode('ascii', errors='replace')[:80],
                        'path': path_match.group(0).decode('ascii', errors='replace') if path_match else None
                    })
                    if len(hits[kw]) >= 3:  # 每个关键词最多3条
                        break
    return hits

print(f'=== 在 gpk 包里搜索武器皮肤关键词 ===')
print(f'关键词数: {len(KEYWORDS)}')
print()

gpk_files = sorted(GPK_DIR.glob('*.gpk'))
# 优先搜索 weapon/model/textures/ui 相关的包
priority_pkgs = [p for p in gpk_files if any(k in p.name.lower() for k in ['weapon', 'model', 'texture', 'ui', 'character'])]
other_pkgs = [p for p in gpk_files if p not in priority_pkgs]
search_pkgs = priority_pkgs + other_pkgs[:10]  # 只搜前20个包

print(f'搜索包数: {len(search_pkgs)} (优先: {len(priority_pkgs)}, 其他: {len(search_pkgs)-len(priority_pkgs)})')
print()

total_hits = 0
for gpk in search_pkgs:
    hits = search_in_gpk(gpk, KEYWORDS)
    pkg_hits = {kw: v for kw, v in hits.items() if v}
    if pkg_hits:
        print(f'--- {gpk.name} ---')
        for kw, entries in pkg_hits.items():
            print(f'  {kw.decode()}: {len(entries)} 条')
            for e in entries[:2]:
                print(f'    entry[{e["entry"]}] size={e["size"]} path={e["path"]}')
                print(f'    上下文: {e["context"]}')
            total_hits += len(entries)
        print()

print(f'=== 总计: {total_hits} 条命中 ===')
