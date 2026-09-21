# -*- coding: utf-8 -*-
"""搜索 ui.npk 里的大尺寸PNG（可能是活动海报）。"""
from __future__ import annotations
import importlib.util, struct, os
from pathlib import Path
from PIL import Image
import io

NPK_READER = Path(r'E:/提取成果/明日拆包/工具库/01_核心解包器/npk_reader.py')
UI_NPK = Path(r'E:/mrzh/res/ui.npk')
OUT_DIR = Path(r'E:/提取成果/明日拆包/工具库/05_BinDict解码器/output/ui_npk_posters')

# 加载 npk_reader
spec = importlib.util.spec_from_file_location('npkr', NPK_READER)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

OUT_DIR.mkdir(parents=True, exist_ok=True)

print(f'=== 搜索 {UI_NPK} 里的大尺寸PNG ===')
print()

with open(UI_NPK, 'rb') as f:
    h = m.aes_ecb(f.read(32))
    _r, magic, ver, to, n = struct.unpack_from('<QIIII', h)
    print(f'总条目数: {n}')
    print()
    
    f.seek(to)
    table = m.aes_ecb(f.read(n * 48))
    
    # 搜索大尺寸PNG
    big_pngs = []
    scan_count = min(2000, n)  # 先扫前2000个
    print(f'扫描前 {scan_count} 个条目...')
    
    for i in range(scan_count):
        fid, off, ps, ds, a, b, flag = struct.unpack_from('<QIIIIIi', table, i * 48)
        if ds < 50 * 1024:  # 小于50KB的跳过
            continue
        f.seek(off)
        raw = m.unpack_entry(f.read(ps), ds, flag)
        if raw[:8] == b'\x89PNG\r\n\x1a\n':
            try:
                img = Image.open(io.BytesIO(raw))
                w, h_img = img.size
                if w >= 512 or h_img >= 512:  # 大尺寸
                    big_pngs.append((i, fid, w, h_img, ds, raw))
                    if len(big_pngs) <= 20:
                        print(f'  entry[{i}] {w}x{h_img} size={ds} fid={fid:016X}')
                    # 保存
                    out_path = OUT_DIR / f'poster_entry_{i:04d}_{w}x{h_img}_{fid:016X}.png'
                    out_path.write_bytes(raw)
                    if len(big_pngs) >= 30:  # 最多保存30个
                        break
            except Exception as e:
                pass
    
    print()
    print(f'共找到 {len(big_pngs)} 个大尺寸PNG')
    print(f'已保存到: {OUT_DIR}')
    print()
    
    # 列出所有保存的文件
    print('=== 保存的文件列表 ===')
    for f in sorted(OUT_DIR.glob('*.png')):
        print(f'  {f.name} ({f.stat().st_size} 字节)')
