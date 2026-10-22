#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
明日之后 PC 端 1DPW/WPK 解密器
格式：1DPW 头 + AC/PC/XC 前缀加密 + ENON/DTSZ 包装 + Zstd
来源：接力包验证通过的实现，ui.idx 第0条 → ui3.wpk → DDS 45748B
依赖：pip install zstandard cryptography
"""
import os, sys, struct, hashlib, json
from pathlib import Path
import zstandard
from Crypto.Cipher import AES

def derive_key(length: int, t: int) -> bytes:
    """派生 AES key（16字节）"""
    v10 = (t + (length & 0xffffffff)) & 0xff
    v28 = (0x7C2E6B6A00000000 |
           (((length & 0xffffffff) << 8) & 0xffff0000) |
           (v10 << 8) |
           (length % 0xfd))
    v29 = (0x5C74656E00003630 |
           (((v10 ^ 0x33) << 16) & 0xffffffff00ffffff) |
           ((v10 | 0x2e) << 24))
    return struct.pack('<QQ', v28 & 0xffffffffffffffff, v29 & 0xffffffffffffffff)

def stage1(payload: bytes, key_delta: int = 0):
    """
    AC/PC/XC 前缀解密
    返回: (解密后数据, tag, p, t, key)
    """
    if len(payload) < 8:
        raise ValueError('short AC wrapper')
    tag = int.from_bytes(payload[:2], 'little')
    p = payload[2]
    t = (payload[3] + key_delta) & 0xff
    body = bytearray(payload[8:])
    plen = min(len(body), 128 << (p - 1)) if body and p else 0

    if tag in (0x4341, 0x4350):  # AC / PC
        done = (plen // 16) * 16
        if done:
            key = derive_key(len(body), t)
            cipher = AES.new(key, AES.MODE_ECB)
            body[:done] = cipher.decrypt(bytes(body[:done]))
        seed = (t + len(body)) & 0xffffffff
        for i in range(plen - done):
            at = done + i
            body[at] ^= ((seed + i) + (body[i] if i < done else 0)) & 0xff
    elif tag == 0x4358:  # XC
        seed = (t + len(body)) & 0xffffffff
        for i in range(plen):
            body[i] ^= (seed + i) & 0xff
    else:
        raise ValueError(f'unsupported AC tag {tag:#x}')

    # 前64字节反转 + XOR 0x5a
    n = min(64, len(body))
    body[:n] = bytes(x ^ 0x5a for x in body[:n][::-1])
    return bytes(body), tag, p, t, derive_key(len(body), t)

def unwrap(d: bytes):
    """ENON/DTSZ 解包，返回 (最终数据, 层列表)"""
    layers = []
    for _ in range(16):
        if d.startswith(b'ENON'):
            d = d[4:]
            layers.append('ENON')
            continue
        if d.startswith(b'DTSZ'):
            if d[4:8] != bytes.fromhex('28b52ffd'):
                raise ValueError('DTSZ magic mismatch')
            d = zstandard.ZstdDecompressor().decompress(d[4:])
            layers.append('DTSZ/ZSTD')
            continue
        break
    return d, layers

def detect_kind(d: bytes) -> str:
    """识别文件类型"""
    for magic, name in [
        (b'DDS ', 'dds'),
        (b'\x89PNG\r\n\x1a\n', 'png'),
        (b'\xff\xd8\xff', 'jpg'),
        (b'RIFF', 'riff'),
        (b'\x13\xab\xa1\x5c', 'astc'),
        (b'PK\x03\x04', 'zip'),
    ]:
        if d.startswith(magic):
            return name
    return 'bin'

def decrypt_1dpw_entry(raw: bytes):
    """
    解密一个 1DPW 条目（包含 1DPW 头）
    返回: (最终数据, 元信息dict)
    """
    if raw[:4] != b'1DPW':
        raise ValueError('not 1DPW')
    # 头部：前 hsz 字节，hsz 在偏移 0x1c？根据验证代码 hsz = hf & 0xffff
    # 这里简化：payload 从某个偏移开始，由调用方传入
    # 实际使用时，从 idx 读取 hsz/psz，然后 raw[hsz:hsz+psz] 是 payload
    # 这个函数接受完整 raw，假设头部大小已知
    raise NotImplementedError('use decrypt_payload with header size')

def decrypt_payload(payload: bytes):
    """解密 AC payload（不含 1DPW 头）"""
    dec, tag, p, t, key = stage1(payload)
    final, layers = unwrap(dec)
    kind = detect_kind(final)
    return final, {
        'ac_tag': f'{tag:04x}',
        'p': p, 't': t,
        'derived_key': key.hex(),
        'layers': layers,
        'type': kind,
        'size': len(final),
    }

def parse_idx(idx_path: str):
    """解析 ui.idx（SKPW 格式），返回条目列表"""
    idx = Path(idx_path).read_bytes()
    if idx[:4] != b'SKPW':
        raise ValueError('not SKPW idx')
    # 头部 0x20 字节，然后每条 0x24 字节
    # 每条: hash(16) + ???(4) + pkg(4) + offset(4) + psz(4) + hf(4)
    count = (len(idx) - 0x20 - 4) // 0x24
    entries = []
    for i in range(count):
        rec = idx[0x20 + i * 0x24 : 0x20 + (i + 1) * 0x24]
        entry_hash = rec[:16].hex()
        pkg_raw = struct.unpack_from('<I', rec, 20)[0]
        pkg = pkg_raw & 0xff
        off, psz, hf = struct.unpack_from('<III', rec, 24)
        hsz = hf & 0xffff
        entries.append({
            'index': i, 'hash': entry_hash, 'pkg': pkg,
            'offset': off, 'payload_size': psz, 'header_size': hsz,
        })
    return entries

def batch_decrypt_wpk(res_dir: str, output_dir: str, pkg_filter=None, max_count=0):
    """
    批量解密 WPK 条目
    res_dir: 包含 ui.idx 和 ui3.wpk/ui4.wpk 的目录
    pkg_filter: 只解密指定 pkg（如 [3,4]），None 为全部
    """
    res_dir = Path(res_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ★ 通用化：扫全部 *.idx（原来写死 ui.idx，导致其它家族读不到）
    idx_files = sorted(res_dir.glob('*.idx'))
    if not idx_files:
        print(f'没有找到任何 .idx（{res_dir}）')
        return 0, 0
    entries = []
    for idx in idx_files:
        try:
            fam = idx.stem
            got = parse_idx(str(idx))
        except Exception as ex:
            print(f'  {idx.name} 解析失败：{str(ex)[:70]}')
            continue
        for e in got:
            e['family'] = fam
        entries.extend(got)
        print(f'  {idx.name:24s} {len(got):4d} 条')
    print(f'idx 共 {len(entries)} 条（{len(idx_files)} 个家族）')

    if pkg_filter:
        entries = [e for e in entries if e['pkg'] in pkg_filter]
        print(f'过滤 pkg {pkg_filter} 后 {len(entries)} 条')

    if max_count > 0:
        entries = entries[:max_count]

    success = 0
    failed = 0
    results = []

    for e in entries:
        # ★★ 2026-09-30 修（真 bug，会让全量扫描静默丢 8%）：
        #   `pkg=255` 是哨兵值，表示**该条目不在任何 .wpk 补丁层里**，而是以
        #   客户端【内容寻址散文件】的形式存放：`<res_dir>/<family>/<hash>`
        #   （文件名 = 条目 hash 的 32 位十六进制）。
        #   原实现直接拼 `<family><pkg>.wpk`（= `model255.wpk`）⇒ 文件不存在 ⇒
        #   `failed += 1; continue` ⇒ 实测 5,588 条里 464 条（12%）被静默丢弃，
        #   且集中在 model 226 / character 157 / building 69。
        #   铁证：`res/building/5359e8fdb411e8c15b9f09689cf41928` 1,051,645 B
        #         == header_size 48 + payload_size 1,051,597（完全对上）。
        raw = None
        if e['pkg'] == 255:
            direct = res_dir / str(e.get('family', 'ui')) / str(e['hash'])
            if not direct.is_file():                      # 大写/小写都试一次
                direct = res_dir / str(e.get('family', 'ui')) / str(e['hash']).upper()
            if direct.is_file():
                raw = direct.read_bytes()
                if len(raw) != e['header_size'] + e['payload_size']:
                    raw = None                            # 长度不符 ⇒ 不当命中
        else:
            wpk_path = res_dir / f'{e.get("family", "ui")}{e["pkg"]}.wpk'
            if wpk_path.exists():
                with open(wpk_path, 'rb') as f:
                    f.seek(e['offset'])
                    raw = f.read(e['header_size'] + e['payload_size'])
        if raw is None or len(raw) != e['header_size'] + e['payload_size'] \
                or raw[:4] != b'1DPW':
            failed += 1
            continue

        payload = raw[e['header_size']:e['header_size'] + e['payload_size']]
        try:
            final, meta = decrypt_payload(payload)
            ext = meta['type']
            out_name = f'{e.get("family", "ui")}_{e["index"]:05d}_{e["hash"][:16]}.{ext}'
            out_path = output_dir / out_name
            out_path.write_bytes(final)
            meta['output'] = str(out_path)
            meta['entry'] = e
            results.append(meta)
            success += 1
        except Exception as ex:
            failed += 1
            if failed <= 5:
                print(f'  失败 #{e["index"]}: {str(ex)[:80]}')

    print(f'\n完成：成功 {success}，失败 {failed}')

    # 保存 manifest
    manifest_path = output_dir / '_manifest.json'
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'Manifest: {manifest_path}')
    return success, failed

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('用法:')
        print('  python wpk_1dpw_decryptor.py <res_dir> <output_dir> [pkg_filter] [max_count]')
        print('示例: python wpk_1dpw_decryptor.py E:\\mrzh\\Documents\\res E:\\wpk_out "3,4" 100')
        sys.exit(1)

    res_dir = sys.argv[1]
    output_dir = sys.argv[2]
    pkg_filter = [int(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else None
    max_count = int(sys.argv[4]) if len(sys.argv) > 4 else 0

    batch_decrypt_wpk(res_dir, output_dir, pkg_filter, max_count)
