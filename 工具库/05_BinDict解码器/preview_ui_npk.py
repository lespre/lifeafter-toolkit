# -*- coding: utf-8 -*-
"""解包 ui.npk，查看里面的内容，找活动海报。"""
from __future__ import annotations
import importlib.util, struct, os
from pathlib import Path

NPK_READER = Path(r'E:/提取成果/明日拆包/工具库/01_核心解包器/npk_reader.py')
UI_NPK = Path(r'E:/mrzh/res/ui.npk')
OUT_DIR = Path(r'E:/提取成果/明日拆包/工具库/05_BinDict解码器/output/ui_npk_preview')

# 加载 npk_reader
spec = importlib.util.spec_from_file_location('npkr', NPK_READER)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

OUT_DIR.mkdir(parents=True, exist_ok=True)

print(f'=== 解包 {UI_NPK} ===')
print(f'文件大小: {UI_NPK.stat().st_size} 字节')
print()

with open(UI_NPK, 'rb') as f:
    h = m.aes_ecb(f.read(32))
    _r, magic, ver, to, n = struct.unpack_from('<QIIII', h)
    print(f'NXPK magic: {magic:#x}, version: {ver}, entries: {n}')
    print(f'table_offset: {to}')
    print()
    
    f.seek(to)
    table = m.aes_ecb(f.read(n * 48))
    
    # 统计文件类型
    types = {}
    samples = []
    
    # 只解包前100个条目看看
    preview_count = min(100, n)
    print(f'解包前 {preview_count} 个条目预览...')
    print()
    
    for i in range(preview_count):
        fid, off, ps, ds, a, b, flag = struct.unpack_from('<QIIIIIi', table, i * 48)
        f.seek(off)
        raw = m.unpack_entry(f.read(ps), ds, flag)
        
        # 判断类型
        if raw[:4] == b'DDS ':
            ext = '.dds'
            # 提取DDS尺寸
            if len(raw) >= 20:
                h_dds = struct.unpack_from('<I', raw, 12)[0]
                w_dds = struct.unpack_from('<I', raw, 16)[0]
                size_info = f'{w_dds}x{h_dds}'
            else:
                size_info = '?'
        elif raw[:8] == b'\x89PNG\r\n\x1a\n':
            ext = '.png'
            size_info = 'PNG'
        elif raw[:4] == b'RIFF':
            ext = '.riff'
            size_info = 'RIFF'
        elif raw[:4] == b'FSB5':
            ext = '.fsb'
            size_info = 'FSB5音频'
        elif len(raw) > 0 and raw[0] == 0x1b:
            ext = '.lua'
            size_info = 'Lua字节码'
        else:
            ext = '.bin'
            size_info = f'head={raw[:8].hex()}'
        
        types[ext] = types.get(ext, 0) + 1
        
        if i < 20:
            samples.append(f'entry[{i}] fid={fid:016X} {ext} ({size_info}) size={ds} flag={flag}')
        
        # 保存DDS预览（前10个）
        if ext == '.dds' and i < 10:
            out_path = OUT_DIR / f'ui_npk_entry_{i:04d}_{fid:016X}.dds'
            out_path.write_bytes(raw)
    
    print(f'文件类型统计 (前{preview_count}个): {types}')
    print()
    print(f'前20个样本:')
    for s in samples:
        print(f'  {s}')
    
    # 搜索大尺寸DDS（可能是海报）
    print()
    print(f'=== 搜索大尺寸DDS（可能是海报）===')
    big_dds = []
    for i in range(min(500, n)):
        fid, off, ps, ds, a, b, flag = struct.unpack_from('<QIIIIIi', table, i * 48)
        if ds < 100 * 1024:  # 小于100KB的跳过
            continue
        f.seek(off)
        raw = m.unpack_entry(f.read(ps), ds, flag)
        if raw[:4] == b'DDS ' and len(raw) >= 20:
            h_dds = struct.unpack_from('<I', raw, 12)[0]
            w_dds = struct.unpack_from('<I', raw, 16)[0]
            if w_dds >= 512 or h_dds >= 512:  # 大尺寸
                big_dds.append((i, fid, w_dds, h_dds, ds))
                # 保存
                out_path = OUT_DIR / f'big_dds_entry_{i:04d}_{w_dds}x{h_dds}_{fid:016X}.dds'
                out_path.write_bytes(raw)
                if len(big_dds) <= 10:
                    print(f'  entry[{i}] {w_dds}x{h_dds} size={ds} fid={fid:016X}')
    
    print(f'共找到 {len(big_dds)} 个大尺寸DDS')
    print(f'已保存到: {OUT_DIR}')
