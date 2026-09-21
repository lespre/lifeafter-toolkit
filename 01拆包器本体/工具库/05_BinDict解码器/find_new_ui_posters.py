# -*- coding: utf-8 -*-
"""对比体验服和正式服的ui.npk，找体验服独有的大尺寸PNG（新活动海报）。"""
from __future__ import annotations
import importlib.util, struct, os
from pathlib import Path
from PIL import Image
import io

NPK_READER = Path(r'E:/提取成果/明日拆包/工具库/01_核心解包器/npk_reader.py')
TEST_UI_NPK = Path(r'E:/mrzh/res/ui.npk')
LIVE_UI_NPK = Path(r'E:/lifeafter/res/ui.npk')
OUT_DIR = Path(r'E:/提取成果/明日拆包/工具库/05_BinDict解码器/output/ui_npk_new_posters')

# 加载 npk_reader
spec = importlib.util.spec_from_file_location('npkr', NPK_READER)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

OUT_DIR.mkdir(parents=True, exist_ok=True)

def get_all_fids(npk_path):
    """获取npk里所有条目的file_id集合。"""
    with open(npk_path, 'rb') as f:
        h = m.aes_ecb(f.read(32))
        _r, magic, ver, to, n = struct.unpack_from('<QIIII', h)
        f.seek(to)
        table = m.aes_ecb(f.read(n * 48))
        fids = set()
        for i in range(n):
            fid = struct.unpack_from('<Q', table, i * 48)[0]
            fids.add(fid)
        return fids, n, table

print(f'=== 对比体验服和正式服 ui.npk ===')
print()

# 读取正式服
if LIVE_UI_NPK.exists():
    print(f'正式服 ui.npk: {LIVE_UI_NPK.stat().st_size} 字节')
    live_fids, live_n, live_table = get_all_fids(LIVE_UI_NPK)
    print(f'正式服条目数: {live_n}')
else:
    print(f'正式服 ui.npk 不存在: {LIVE_UI_NPK}')
    live_fids = set()
    live_n = 0

print()

# 读取体验服
print(f'体验服 ui.npk: {TEST_UI_NPK.stat().st_size} 字节')
test_fids, test_n, test_table = get_all_fids(TEST_UI_NPK)
print(f'体验服条目数: {test_n}')
print()

# 找体验服独有
new_fids = test_fids - live_fids
print(f'体验服独有条目数: {len(new_fids)}')
print()

# 解包体验服独有的大尺寸PNG
print(f'=== 解包体验服独有的大尺寸PNG ===')
big_pngs = []
with open(TEST_UI_NPK, 'rb') as f:
    for i in range(test_n):
        fid, off, ps, ds, a, b, flag = struct.unpack_from('<QIIIIIi', test_table, i * 48)
        if fid not in new_fids:
            continue
        if ds < 50 * 1024:  # 小于50KB的跳过
            continue
        f.seek(off)
        raw = m.unpack_entry(f.read(ps), ds, flag)
        if raw[:8] == b'\x89PNG\r\n\x1a\n':
            try:
                img = Image.open(io.BytesIO(raw))
                w, h_img = img.size
                if w >= 256 or h_img >= 256:  # 中等以上尺寸
                    big_pngs.append((i, fid, w, h_img, ds, raw))
                    print(f'  entry[{i}] {w}x{h_img} size={ds} fid={fid:016X}')
                    # 保存
                    out_path = OUT_DIR / f'new_poster_entry_{i:04d}_{w}x{h_img}_{fid:016X}.png'
                    out_path.write_bytes(raw)
                    if len(big_pngs) >= 50:  # 最多保存50个
                        break
            except Exception as e:
                pass

print()
print(f'共找到 {len(big_pngs)} 个体验服独有的大尺寸PNG')
print(f'已保存到: {OUT_DIR}')
print()

# 列出所有保存的文件
print('=== 保存的文件列表 ===')
for f in sorted(OUT_DIR.glob('*.png')):
    print(f'  {f.name} ({f.stat().st_size} 字节)')
