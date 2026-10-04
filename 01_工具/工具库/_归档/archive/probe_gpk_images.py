# -*- coding: utf-8 -*-
"""探测 GPK 头部和条目表结构，并扫描伪装图片。"""
import struct, sys, json
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import lz4.block
import zstandard as zstd

KEY = bytes.fromhex('606308D8A32C782013D26C2F226F686D')

def aes_ecb_decrypt(data):
    dec = Cipher(algorithms.AES(KEY), modes.ECB()).decryptor()
    return dec.update(data) + dec.finalize()

def is_standard_image(data):
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

def has_image_markers(data):
    markers = []
    if b'JFIF' in data[:4096]:
        markers.append('JFIF')
    if b'Exif' in data[:4096]:
        markers.append('Exif')
    if b'IHDR' in data[:4096]:
        markers.append('IHDR')
    if b'IDAT' in data[:4096]:
        markers.append('IDAT')
    # 检查文件偏移处是否有 JPG SOI
    for off in range(0, min(512, len(data) - 2)):
        if data[off:off+3] == b'\xff\xd8\xff':
            markers.append(f'JPG_SOI@{off}')
            break
    return markers

def probe_gpk(gpk_path):
    print(f'=== 探测: {gpk_path.name} ({gpk_path.stat().st_size // 1024 // 1024}MB) ===')

    with gpk_path.open('rb') as f:
        raw_head = f.read(32)
        head = aes_ecb_decrypt(raw_head)

        print(f'头部 hex: {head.hex()}')
        for i in range(0, 32, 4):
            val = struct.unpack_from('<I', head, i)[0]
            print(f'  @{i:2d}: {val:>12} ({val:#010x})')

        entry_count = struct.unpack_from('<I', head, 20)[0]
        print(f'\n假设条目数 @20 = {entry_count}')

        # 读取条目表（假设紧跟头部后，每条32字节）
        table_size = entry_count * 32
        table_enc_size = (table_size + 15) // 16 * 16
        f.seek(32)
        table_enc = f.read(table_enc_size)
        table = aes_ecb_decrypt(table_enc)[:table_size]

        print(f'\n前5条条目（每条32字节）:')
        for i in range(min(5, entry_count)):
            entry = table[i*32:(i+1)*32]
            vals = struct.unpack('<IIIIIIII', entry)
            print(f'  [{i}] offset={vals[0]:>10} comp={vals[1]:>8} decomp={vals[2]:>8} '
                  f'crc1={vals[3]:#010x} crc2={vals[4]:#010x} flag={vals[5]} res={vals[6]},{vals[7]}')

        # 扫描伪装图片
        print(f'\n开始扫描伪装图片（1KB-2MB）...')
        candidates = []
        dctx = zstd.ZstdDecompressor()

        for i in range(entry_count):
            entry = table[i*32:(i+1)*32]
            offset, comp, decomp, crc1, crc2, flag, r1, r2 = struct.unpack('<IIIIIIII', entry)

            if decomp < 1024 or decomp > 2 * 1024 * 1024:
                continue

            try:
                f.seek(offset + 36)
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

                # 检查 1DPW 头
                is_1dpw = raw[:4] == b'1DPW'

                if not is_standard_image(raw):
                    markers = has_image_markers(raw)
                    if markers or is_1dpw:
                        candidates.append({
                            'index': i,
                            'offset': offset,
                            'packed': comp,
                            'decomp': decomp,
                            'flag': flag,
                            'head_hex': raw[:16].hex(),
                            'is_1dpw': is_1dpw,
                            'markers': markers,
                        })

            except Exception:
                continue

            if (i + 1) % 5000 == 0:
                print(f'  进度: {i+1}/{entry_count}, 候选: {len(candidates)}')

    print(f'\n扫描完成: {len(candidates)} 个候选')
    for c in candidates[:30]:
        print(f"  [{c['index']:6d}] {c['decomp']:>8}B flag={c['flag']} "
              f"1DPW={c['is_1dpw']} markers={c['markers']} head={c['head_hex'][:24]}")

    # 保存结果
    out = Path(r'E:\提取成果\filename_restore_output') / f'disguised_{gpk_path.stem}.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({'source': str(gpk_path), 'candidates': candidates},
                               ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'\n结果已保存: {out}')
    return candidates

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: python probe_gpk_images.py <gpk_file>')
        sys.exit(1)
    probe_gpk(Path(sys.argv[1]))
