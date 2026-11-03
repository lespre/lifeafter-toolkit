#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
明日之后 安卓版 .ktx 纹理批量转 PNG
格式：伪装 KTX 头 + 属性列表 + ASTC 8x8 mipmap 链
依赖：astcenc-avx2.exe（同目录或 PATH）
"""
import os, sys, struct, subprocess, tempfile, shutil
from concurrent.futures import ProcessPoolExecutor, as_completed

ASTCENC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'astcenc-avx2.exe')
if not os.path.exists(ASTCENC):
    ASTCENC = shutil.which('astcenc-avx2.exe') or 'astcenc-avx2.exe'

def parse_ktx(filepath):
    """解析 .ktx 文件，返回 (width, height, astc_data)"""
    with open(filepath, 'rb') as f:
        data = f.read()
    
    if len(data) < 64:
        return None
    
    # 从偏移64开始解析 level 列表
    offset = 64
    real_w = real_h = 0
    texture_offset = None
    
    while offset + 4 <= len(data):
        img_size = struct.unpack_from('<I', data, offset)[0]
        data_start = offset + 4
        
        if img_size > 1000:
            # 真正的纹理数据
            texture_offset = data_start
            break
        
        # 尝试解析属性
        if img_size > 0 and img_size < 64:
            level_data = data[data_start:data_start+img_size]
            null_pos = level_data.find(b'\x00')
            if 0 < null_pos < 32:
                try:
                    name = level_data[:null_pos].decode('ascii')
                    if name.isalpha() and null_pos + 1 + 4 <= len(level_data):
                        value = struct.unpack_from('<I', level_data, null_pos + 1)[0]
                        if name == 'RealWidth':
                            real_w = value
                        elif name == 'RealHeight':
                            real_h = value
                except:
                    pass
        
        offset = (data_start + img_size + 3) & ~3
    
    if texture_offset is None or real_w == 0 or real_h == 0:
        return None
    
    # 提取第一个 mipmap（最大尺寸）
    blocks_x = (real_w + 7) // 8
    blocks_y = (real_h + 7) // 8
    mip0_size = blocks_x * blocks_y * 16
    
    if texture_offset + mip0_size > len(data):
        return None
    
    astc_data = data[texture_offset:texture_offset + mip0_size]
    return (real_w, real_h, astc_data)

# ══════════════════════════════════════════════════════════════════════
# 真 KTX 1.1（角色/时装侧）：ETC2/EAC 像素格式，非伪装 ASTC
#
# 武器侧 .ktx 是"伪装 KTX 头 + 属性列表 + ASTC 8x8"，走上面的 astcenc 路径；
# 角色/时装侧 .ktx（players/players2021/players2025）是**标准 KTX 1.1**：
#   identifier «KTX 11», glInternalFormat=0x9278(GL_COMPRESSED_RGBA8_ETC2_EAC),
#   1 级 → 1024x1024，11 级 mip，mip0 imageSize=1048576（4bpp）。
# 实测 b_f_3715001a.ktx 1398236B：64 头 + 4B imageSize + 1048576+262144+…（mip 链）。
# 老解析器从 offset64 起按"属性列表"扫，会把 mip0 的 1048576B 当成属性而返回 None
# （实测报 parse failed）。故这里按 KTX 1.1 头逐字段解析，用 texture2ddecoder 解码。
# ══════════════════════════════════════════════════════════════════════
KTX11_ID = b'\xabKTX 11\xbb\r\n\x1a\n'
# glInternalFormat → (解码函数名, 是否有 alpha)
ETC2_FORMATS = {
    0x9274: ('decode_etc2', False),      # RGB8_ETC2
    0x9275: ('decode_etc2', False),      # SRGB8_ETC2
    0x9276: ('decode_etc2a1', True),     # RGB8_PUNCHTHROUGH_ALPHA1
    0x9277: ('decode_etc2a1', True),     # SRGB8_PUNCHTHROUGH_ALPHA1
    0x9278: ('decode_etc2a8', True),     # RGBA8_ETC2_EAC
    0x9279: ('decode_etc2a8', True),     # SRGB8_ALPHA8_ETC2_EAC
    0x9270: ('decode_eacr', False),      # R11_EAC
    0x9271: ('decode_eacr_signed', False),
    0x9272: ('decode_eacrg', False),     # RG11_EAC
    0x9273: ('decode_eacrg_signed', False),
}


def parse_ktx11(filepath):
    """解析标准 KTX 1.1 头，返回 (w, h, fmt, mip0_bytes) 或 None。"""
    with open(filepath, 'rb') as f:
        head = f.read(64)
        if len(head) < 64 or not head.startswith(KTX11_ID):
            return None
        fmt = struct.unpack_from('<I', head, 0x1C)[0]
        w = struct.unpack_from('<I', head, 0x24)[0]
        h = struct.unpack_from('<I', head, 0x28)[0]
        kv = struct.unpack_from('<I', head, 0x3C)[0]
        f.seek(64 + kv)
        img_size = struct.unpack_from('<I', f.read(4), 0)[0]
        data = f.read(img_size)
    if w == 0 or h == 0 or len(data) < img_size:
        return None
    return w, h, fmt, data


def ktx11_to_png(ktx_path, png_path):
    """标准 KTX 1.1（ETC2/EAC）→ PNG。返回 (ok, msg)。"""
    try:
        from PIL import Image
        import texture2ddecoder as t2d
    except Exception as exc:      # 依赖缺失：明确报错而不是静默失败
        return False, '依赖缺失(Pillow/texture2ddecoder): %r' % (exc,)
    got = parse_ktx11(ktx_path)
    if got is None:
        return False, 'KTX1.1 头解析失败'
    w, h, fmt, data = got
    dec = ETC2_FORMATS.get(fmt)
    if dec is None:
        return False, '未支持的 glInternalFormat=0x%04x' % fmt
    fn_name, has_alpha = dec
    out = getattr(t2d, fn_name)(data, w, h)
    mode = 'RGBA' if has_alpha else 'RGB'
    if not has_alpha:
        # 无 alpha 的解码器返回 3 通道；不足时按 4 通道兜底
        if len(out) == w * h * 4:
            mode = 'RGBA'
        elif len(out) == w * h * 3:
            mode = 'RGB'
        else:
            return False, '解码输出长度异常 %d' % len(out)
    os.makedirs(os.path.dirname(png_path), exist_ok=True)
    Image.frombytes(mode, (w, h), out).save(png_path)
    return True, '%dx%d fmt=0x%04x' % (w, h, fmt)


def ktx_to_png(ktx_path, png_path, astcenc=ASTCENC):
    """单个 .ktx 转 .png（自动判族：标准 KTX1.1 ETC2 / 伪装 ASTC）"""
    try:
        with open(ktx_path, 'rb') as _f:
            if _f.read(12) == KTX11_ID:
                return ktx11_to_png(ktx_path, png_path)
        result = parse_ktx(ktx_path)
        if result is None:
            return False, "parse failed"
        
        w, h, astc_data = result
        
        # 生成 ASTC 容器文件
        magic = struct.pack('<I', 0x5CA1AB13)
        astc_header = (magic + bytes([8, 8, 1]) + 
                       struct.pack('<I', w)[:3] + 
                       struct.pack('<I', h)[:3] + 
                       struct.pack('<I', 1)[:3])
        
        # 用临时文件
        tmp_dir = tempfile.mkdtemp()
        try:
            astc_tmp = os.path.join(tmp_dir, 'tex.astc')
            with open(astc_tmp, 'wb') as f:
                f.write(astc_header + astc_data)
            
            png_tmp = os.path.join(tmp_dir, 'tex.png')
            proc = subprocess.run(
                [astcenc, '-dl', astc_tmp, png_tmp],
                capture_output=True, timeout=30
            )
            
            if os.path.exists(png_tmp):
                os.makedirs(os.path.dirname(png_path), exist_ok=True)
                shutil.copy2(png_tmp, png_path)
                return True, f"{w}x{h}"
            else:
                return False, proc.stderr.decode('utf-8', errors='replace')[:200]
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)
    except Exception as e:
        return False, str(e)[:200]

def batch_convert(input_dir, output_dir, workers=8, min_size=0, max_count=0):
    """批量转换目录下所有 .ktx"""
    ktx_files = []
    for root, dirs, files in os.walk(input_dir):
        for fn in files:
            if fn.lower().endswith('.ktx'):
                fp = os.path.join(root, fn)
                if min_size > 0 and os.path.getsize(fp) < min_size:
                    continue
                ktx_files.append(fp)
    
    if max_count > 0:
        ktx_files = ktx_files[:max_count]
    
    print(f"找到 {len(ktx_files)} 个 .ktx 文件，{workers} 线程转换...")
    
    success = 0
    failed = 0
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {}
        for ktx_path in ktx_files:
            rel = os.path.relpath(ktx_path, input_dir)
            png_path = os.path.join(output_dir, os.path.splitext(rel)[0] + '.png')
            fut = executor.submit(ktx_to_png, ktx_path, png_path)
            futures[fut] = ktx_path
        
        for i, fut in enumerate(as_completed(futures), 1):
            ktx_path = futures[fut]
            ok, msg = fut.result()
            if ok:
                success += 1
            else:
                failed += 1
            if i % 100 == 0 or i == len(ktx_files):
                print(f"  [{i}/{len(ktx_files)}] 成功={success} 失败={failed}")
    
    print(f"\n完成：成功 {success}，失败 {failed}")
    return success, failed

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: python ktx_to_png.py <输入目录> <输出目录> [线程数] [最小文件大小KB] [最大数量]")
        print("示例: python ktx_to_png.py E:\\提取成果\\apk_unpacked\\ui E:\\提取成果\\ktx_png 10 100 500")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    min_size = int(sys.argv[4]) * 1024 if len(sys.argv) > 4 else 0
    max_count = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    
    batch_convert(input_dir, output_dir, workers, min_size, max_count)
