# -*- coding: utf-8 -*-
"""
明日之后皮肤定位链 - IDX→WPK→DDS解密
解析IDX索引，从WPK中提取1DPW加密条目并解密为DDS
"""
import struct
import hashlib
import json
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import zstandard

# 配置
RES_DIR = Path(r'E:\mrzh\Documents\res')
OUT_DIR = Path(r'E:\提取成果\明日拆包\工具库\06_皮肤定位链\extracted')

def derive_key(length: int, t: int) -> bytes:
    """1DPW派生key算法"""
    v10 = (t + (length & 0xffffffff)) & 0xff
    v28 = 0x7C2E6B6A00000000 | (((length & 0xffffffff) << 8) & 0xffff0000) | (v10 << 8) | (length % 0xfd)
    v29 = 0x5C74656E00003630 | (((v10 ^ 0x33) << 16) & 0xffffffff00ffffff) | ((v10 | 0x2e) << 24)
    return struct.pack('<QQ', v28 & 0xffffffffffffffff, v29 & 0xffffffffffffffff)

def stage1(payload: bytes, key_delta: int = 0):
    """1DPW第一阶段解密：AC/PC/XC前缀加密"""
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
            dec = Cipher(algorithms.AES(derive_key(len(body), t)), modes.ECB()).decryptor()
            body[:done] = dec.update(bytes(body[:done])) + dec.finalize()
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
    
    n = min(64, len(body))
    body[:n] = bytes(x ^ 0x5a for x in body[:n][::-1])
    
    return bytes(body), tag, p, payload[3], derive_key(len(body), t)

def unwrap(d: bytes):
    """解包ENON/DTSZ层"""
    layers = []
    for _ in range(16):
        if d.startswith(b'ENON'):
            d = d[4:]
            layers.append('ENON')
            continue
        if d.startswith(b'DTSZ'):
            if d[4:8] != bytes.fromhex('28b52ffd'):
                raise ValueError('DTSZ magic')
            d = zstandard.ZstdDecompressor().decompress(d[4:])
            layers.append('DTSZ/ZSTD')
            continue
        break
    return d, layers

def kind(d: bytes):
    """判断文件类型"""
    for m, n in ((b'DDS ', 'dds'), (b'\x89PNG\r\n\x1a\n', 'png'), 
                 (b'\xff\xd8\xff', 'jpg'), (b'RIFF', 'riff'),
                 (b'\x13\xab\xa1\x5c', 'astc')):
        if d.startswith(m):
            return n
    return 'bin'

def parse_idx(idx_path: Path):
    """解析IDX索引文件"""
    data = idx_path.read_bytes()
    
    if data[:4] != b'SKPW':
        raise ValueError(f'不是SKPW格式: {idx_path}')
    
    # 头部32字节，然后条目每个36字节，最后4字节校验
    entry_count = (len(data) - 32 - 4) // 36
    entries = []
    
    for i in range(entry_count):
        offset = 32 + i * 36  # 32头部后直接是条目
        if offset + 36 > len(data):
            break
        
        rec = data[offset:offset+36]
        hash_val = rec[:16].hex()
        pkg_raw = struct.unpack_from('<I', rec, 20)[0]
        pkg = pkg_raw & 0xff
        off, psz, hf = struct.unpack_from('<III', rec, 24)
        hsz = hf & 0xffff
        
        entries.append({
            'index': i,
            'hash': hash_val,
            'pkg': pkg,
            'offset': off,
            'payload_size': psz,
            'header_size': hsz,
        })
    
    return entries

def extract_dds_from_wpk(wpk_path: Path, offset: int, header_size: int, payload_size: int):
    """从WPK中提取并解密一个1DPW条目"""
    with wpk_path.open('rb') as f:
        f.seek(offset)
        raw = f.read(header_size + payload_size)
    
    if len(raw) != header_size + payload_size:
        raise ValueError(f'读取不完整: 期望{header_size+payload_size}, 实际{len(raw)}')
    
    if raw[:4] != b'1DPW':
        raise ValueError(f'不是1DPW格式: {raw[:4]}')
    
    payload = raw[header_size:header_size+payload_size]
    
    # 解密
    dec, tag, p, t, key = stage1(payload)
    final, layers = unwrap(dec)
    typ = kind(final)
    
    return final, typ, layers, tag, p, t

def extract_by_hash(idx_path: Path, wpk_dir: Path, target_hash: str, out_dir: Path):
    """通过hash提取一个DDS文件"""
    entries = parse_idx(idx_path)
    
    target = None
    for e in entries:
        if e['hash'] == target_hash.lower():
            target = e
            break
    
    if not target:
        print(f'未找到hash: {target_hash}')
        return None
    
    wpk_path = wpk_dir / f'{idx_path.stem}{target["pkg"]}.wpk'
    if not wpk_path.exists():
        # 尝试其他命名方式
        wpk_path = wpk_dir / f'{idx_path.stem.replace(".idx", "")}{target["pkg"]}.wpk'
    
    if not wpk_path.exists():
        print(f'WPK文件不存在: {wpk_path}')
        return None
    
    print(f'找到条目: hash={target["hash"]}, pkg={target["pkg"]}, offset={target["offset"]}, size={target["payload_size"]}')
    print(f'WPK文件: {wpk_path}')
    
    try:
        final, typ, layers, tag, p, t = extract_dds_from_wpk(
            wpk_path, target['offset'], target['header_size'], target['payload_size']
        )
        
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f'{target_hash}.{typ}'
        out_path.write_bytes(final)
        
        print(f'解密成功: 类型={typ}, 大小={len(final)}, 层数={layers}')
        print(f'输出: {out_path}')
        
        return str(out_path)
    except Exception as e:
        print(f'解密失败: {e}')
        return None

def list_all_hashes(idx_path: Path, limit: int = 20):
    """列出IDX中的所有hash"""
    entries = parse_idx(idx_path)
    print(f'\n=== {idx_path.name} 条目列表 (共{len(entries)}个) ===')
    for e in entries[:limit]:
        print(f'  [{e["index"]:4d}] hash={e["hash"]} pkg={e["pkg"]} off={e["offset"]:10d} size={e["payload_size"]:6d} hsz={e["header_size"]}')
    if len(entries) > limit:
        print(f'  ... 还有{len(entries)-limit}个')
    return entries

def main():
    print("=" * 60)
    print("明日之后皮肤定位链 - IDX→WPK→DDS解密")
    print("=" * 60)
    
    # 列出weapon.idx的条目
    weapon_idx = RES_DIR / 'weapon.idx'
    if weapon_idx.exists():
        weapon_entries = list_all_hashes(weapon_idx, limit=50)
    
    # 列出ui.idx的条目
    ui_idx = RES_DIR / 'ui.idx'
    if ui_idx.exists():
        ui_entries = list_all_hashes(ui_idx, limit=20)
    
    # 保存hash列表
    out_dir = OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    
    if weapon_idx.exists():
        with open(out_dir / 'weapon_idx_hashes.json', 'w', encoding='utf-8') as f:
            json.dump(weapon_entries, f, indent=2, ensure_ascii=False)
        print(f'\nweapon.idx hash列表已保存: {out_dir / "weapon_idx_hashes.json"}')
    
    print("\n" + "=" * 60)
    print("使用方法:")
    print("  extract_by_hash(weapon_idx, RES_DIR, '目标hash', out_dir)")
    print("=" * 60)

if __name__ == '__main__':
    main()
