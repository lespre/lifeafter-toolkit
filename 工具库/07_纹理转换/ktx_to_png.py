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

def ktx_to_png(ktx_path, png_path, astcenc=ASTCENC):
    """单个 .ktx 转 .png"""
    try:
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
