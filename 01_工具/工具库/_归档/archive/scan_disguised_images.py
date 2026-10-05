# -*- coding: utf-8 -*-
"""快速扫描 GPK 包，找伪装的 JPG/PNG 图片（文件头异常但内容含图片标记）。

思路：
1. 读取 GPK 条目表
2. 逐个解压条目到内存（不写文件）
3. 检查文件头：如果不是标准格式（DDS/PNG/JPG/GIF/BMP）
4. 但内容包含 JPG 标记（FF D8 FF / JFIF / Exif）或 PNG 标记
5. 输出候选文件

只读源，不写解包产物。
"""
from __future__ import annotations
import struct, sys
from pathlib import Path

try:
    from Crypto.Cipher import AES
except ImportError:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    AES = None

import lz4.block
import zstandard as zstd

KEY = bytes.fromhex('606308D8A32C782013D26C2F226F686D')

def aes_ecb_decrypt(data: bytes) -> bytes:
    if AES:
        cipher = AES.new(KEY, AES.MODE_ECB)
        return cipher.decrypt(data)
    else:
        dec = Cipher(algorithms.AES(KEY), modes.ECB()).decryptor()
        return dec.update(data) + dec.finalize()

def is_standard_image(data: bytes) -> bool:
    """检查是否是标准图片格式。"""
    if len(data) < 4:
        return False
    if data[:4] == b'DDS ':
        return True
    if data[:8] == b'\x89PNG\r\n\x1a\n':
        return True
    if data[:3] == b'\xff\xd8\xff':
        return True
    if data[:6] in (b'GIF87a', b'GIF89a'):
        return True
    if data[:2] == b'BM':
        return True
    return False

def has_jpg_markers(data: bytes) -> list:
    """检查内容是否包含 JPG 标记（可能在文件中间）。"""
    markers = []
    # JFIF 标记
    if b'JFIF' in data:
        markers.append('JFIF')
    # Exif 标记
    if b'Exif' in data:
        markers.append('Exif')
    # JPG SOI 标记（可能在偏移处）
    for offset in range(0, min(256, len(data) - 2)):
        if data[offset:offset+3] == b'\xff\xd8\xff':
            markers.append(f'SOI@{offset}')
            break
    # Photoshop / Adobe 标记
    if b'Adobe' in data[:1024]:
        markers.append('Adobe')
    return markers

def has_png_markers(data: bytes) -> list:
    """检查内容是否包含 PNG 标记。"""
    markers = []
    if b'PNG' in data[:1024]:
        markers.append('PNG_signature')
    if b'IHDR' in data[:1024]:
        markers.append('IHDR')
    if b'IDAT' in data[:1024]:
        markers.append('IDAT')
    return markers

def scan_gpk(gpk_path: Path, max_entries: int = None):
    """扫描单个 GPK 包。"""
    print(f'\n=== 扫描: {gpk_path.name} ({gpk_path.stat().st_size // 1024 // 1024}MB) ===')

    with gpk_path.open('rb') as f:
        # 解密头部（32字节倍数）
        head_enc = f.read(32)
        head = aes_ecb_decrypt(head_enc)

        # 解析头部
        magic = struct.unpack_from('<I', head, 0)[0]
        entry_count = struct.unpack_from('<I', head, 20)[0]
        print(f'  条目数: {entry_count}')

        # 读取条目表（每条32字节，紧跟在头部后）
        table_size = entry_count * 32
        # 条目表可能需要解密（按16字节倍数）
        table_enc_size = (table_size + 15) // 16 * 16
        table_enc = f.read(table_enc_size)
        table = aes_ecb_decrypt(table_enc)[:table_size]

        candidates = []
        dctx = zstd.ZstdDecompressor()

        for i in range(entry_count):
            if max_entries and i >= max_entries:
                break

            entry = table[i*32:(i+1)*32]
            offset, comp, decomp, crc1, crc2, flag = struct.unpack('<IIIIII', entry)

            # 只检查合理大小的条目（1KB-2MB）
            if decomp < 1024 or decomp > 2 * 1024 * 1024:
                continue

            try:
                f.seek(offset + 36)  # 数据从 offset+36 开始
                packed = f.read(comp)
                if len(packed) != comp:
                    continue

                if flag == 0:
                    raw = packed
                elif flag == 2:
                    raw = lz4.block.decompress(packed, uncompressed_size=decomp)
                elif flag == 12:
                    raw = dctx.decompress(packed, max_output_size=decomp)
                else:
                    continue

                # 检查是否是伪装图片
                if not is_standard_image(raw):
                    jpg_markers = has_jpg_markers(raw)
                    png_markers = has_png_markers(raw)

                    if jpg_markers or png_markers:
                        candidates.append({
                            'index': i,
                            'offset': offset,
                            'packed': comp,
                            'decomp': decomp,
                            'flag': flag,
                            'head_hex': raw[:16].hex(),
                            'jpg_markers': jpg_markers,
                            'png_markers': png_markers,
                        })

            except Exception:
                continue

            if (i + 1) % 10000 == 0:
                print(f'  进度: {i+1}/{entry_count}, 候选: {len(candidates)}')

    print(f'  扫描完成: {len(candidates)} 个候选伪装图片')
    for c in candidates[:20]:
        print(f"    [{c['index']:6d}] {c['decomp']:>8}B flag={c['flag']} head={c['head_hex'][:24]} jpg={c['jpg_markers']} png={c['png_markers']}")

    return candidates


def main():
    if len(sys.argv) < 2:
        print('用法: python scan_disguised_images.py <gpk_file> [max_entries]')
        sys.exit(1)

    gpk_path = Path(sys.argv[1])
    max_entries = int(sys.argv[2]) if len(sys.argv) > 2 else None

    if not gpk_path.exists():
        print(f'文件不存在: {gpk_path}')
        sys.exit(1)

    candidates = scan_gpk(gpk_path, max_entries)

    # 保存结果
    import json
    out = Path(r'E:\提取成果\filename_restore_output') / f'disguised_images_{gpk_path.stem}.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({'source': str(gpk_path), 'candidates': candidates}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'\n结果已保存: {out}')


if __name__ == '__main__':
    main()
