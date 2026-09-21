# -*- coding: utf-8 -*-
"""根据 file_id 从 script.npk / script.py3.npk 提取配置表并搜索武器皮肤。"""
from __future__ import annotations
import importlib.util, struct, sys, json, re
from pathlib import Path

TARGET_FID = int(sys.argv[1], 16) if len(sys.argv) > 1 else 0x1B249D5c9984E1B4
KEYWORD = sys.argv[2] if len(sys.argv) > 2 else '武器皮肤'

NPK_READER = Path(r'E:/提取成果/明日拆包/工具库/01_核心解包器/npk_reader.py')
PKGS = [
    Path(r'E:/mrzh/Documents/script.npk'),
    Path(r'E:/mrzh/Documents/script.py3.npk'),
    Path(r'E:/mrzh/Documents/script.py314.lc.npk'),
]

# 加载 npk_reader
spec = importlib.util.spec_from_file_location('npkr', NPK_READER)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

print(f'=== 目标 file_id: {TARGET_FID:016X} ===')
print(f'关键词: {KEYWORD}')
print()

for pkg in PKGS:
    if not pkg.exists():
        print(f'跳过（不存在）: {pkg.name}')
        continue
    print(f'--- 搜索 {pkg.name} ---')
    with pkg.open('rb') as f:
        h = m.aes_ecb(f.read(32))
        _r, magic, ver, to, n = struct.unpack_from('<QIIII', h)
        if magic != 0x4b50584e:
            print(f'  不是 NXPK（magic={magic:#x}）')
            continue
        print(f'  版本: {ver}, 条目数: {n}')
        f.seek(to)
        tab = m.aes_ecb(f.read(n * 48))
        # 查找目标 file_id
        found = None
        for i in range(n):
            fid = struct.unpack_from('<Q', tab, i * 48)[0]
            if fid == TARGET_FID:
                off, ps, ds, a, b, flag = struct.unpack_from('<IIIIIi', tab, i * 48 + 8)
                found = (i, off, ps, ds, flag)
                break
        if not found:
            print(f'  未找到 file_id {TARGET_FID:016X}')
            continue
        i, off, ps, ds, flag = found
        print(f'  找到! entry[{i}] offset={off} packed={ps} decomp={ds} flag={flag}')
        f.seek(off)
        raw = m.unpack_entry(f.read(ps), ds, flag)
        print(f'  解压后大小: {len(raw)}')
        # 保存原始数据
        out_dir = Path(r'E:/提取成果/明日拆包/工具库/05_BinDict解码器/output/weapon_search')
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f'config_{TARGET_FID:016X}_{pkg.stem}.bin'
        out_path.write_bytes(raw)
        print(f'  已保存: {out_path}')
        # 多编码搜索关键词
        print(f'\n  --- 搜索关键词: {KEYWORD} ---')
        for enc_name, enc in [('UTF-8', 'utf-8'), ('GBK', 'gbk'), ('UTF-16LE', 'utf-16-le'), ('UTF-16BE', 'utf-16-be')]:
            try:
                text = raw.decode(enc, errors='ignore')
                count = text.count(KEYWORD)
                if count > 0:
                    print(f'  {enc_name}: {count} 次命中')
                    # 显示上下文
                    idx = 0
                    shown = 0
                    while shown < 10:
                        idx = text.find(KEYWORD, idx)
                        if idx < 0:
                            break
                        start = max(0, idx - 30)
                        end = min(len(text), idx + len(KEYWORD) + 50)
                        context = text[start:end].replace('\n', '\\n').replace('\r', '\\r')
                        print(f'    [{idx}] ...{context}...')
                        idx += len(KEYWORD)
                        shown += 1
            except Exception as e:
                print(f'  {enc_name}: 解码失败 {e}')
        # 搜索所有"武器皮肤:xxx"模式
        print(f'\n  --- 所有武器皮肤列表 ---')
        try:
            text = raw.decode('utf-8', errors='ignore')
            # 匹配"武器皮肤:xxx"或"武器皮肤：xxx"
            patterns = [
                r'武器皮肤[:：]\s*([^\s\n\r,，、;；]+)',
                r'获得武器皮肤[:：]\s*([^\s\n\r,，、;；]+)',
            ]
            weapons = set()
            for pat in patterns:
                for match in re.finditer(pat, text):
                    weapons.add(match.group(1))
            for w in sorted(weapons):
                print(f'    - {w}')
            print(f'  共 {len(weapons)} 种武器皮肤')
            # 保存武器皮肤列表
            weapons_path = out_dir / f'weapon_skins_{TARGET_FID:016X}.json'
            weapons_path.write_text(json.dumps(sorted(weapons), ensure_ascii=False, indent=2), encoding='utf-8')
            print(f'  已保存: {weapons_path}')
        except Exception as e:
            print(f'  提取失败: {e}')
    print()

print('搜索完成')
