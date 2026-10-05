"""解 common_model_show_conf_chs.py（同布局 ✓）⇒ 拿列名/中文"""
import re
import struct
from pathlib import Path

CANDS = [
    r'E:\la拆包项目\03_执行\41_还原树\script.py314.lc.npk\com\cdata\common_model_show_conf_chs.py',
    r'E:\la拆包项目\03_执行\41_还原树\script.py314.lc.npk\com\cdata\common_model_show_conf.py',
    r'E:\la拆包项目\03_执行\41_还原树\Documents\script.py314.lc.npk\com\cdata\fashion_bg_data_chs.py',
]
for path in CANDS:
    p = Path(path)
    if not p.is_file():
        print('  · 无 %s' % p.name)
        continue
    raw = p.read_bytes()
    x = raw.find(b'x{')
    print()
    print('█' * 66)
    print('██ %s  (%d B)  x{@%s' % (p.name, len(raw), x))
    print('█' * 66)
    if x < 0:
        print('   ✗ 无 x{')
        continue
    ln = struct.unpack_from('<I', raw, x + 2)[0]
    body = raw[x + 6: x + 6 + ln]
    if len(body) < 56:
        print('   ✗ body 太短 %d' % len(body))
        continue
    cnt = struct.unpack_from('<I', body, 0)[0]
    pl = struct.unpack_from('<I', body, 52)[0]
    print('   count=%s pool_len=%s rows=%s' % (cnt, pl, len(body) - 52 - pl))
    pool = body[56: 52 + pl]
    # 池里的可读串（列名如果是字符串 ✓ 就在这）
    u = []
    for m in re.finditer(rb'[\x20-\x7E]{3,160}', pool):
        s = m.group(0).decode('ascii', 'replace')
        if s not in u:
            u.append(s)
    print('   池可读串 %d 条' % len(u))
    KEY = ('camera', 'model', 'light', 'color', 'zoom', 'env', 'weather', 'scene',
           'skin', 'weapon', 'pos', 'rot', 'angle', 'fov', 'dist', 'intensity',
           'conf', 'bg', 'ssr', 'ibl', 'fog', 'sun', 'amb', 'dir', 'spec', 'emis')
    hit = [s for s in u if any(k in s.lower() for k in KEY)]
    print('   ★ 语义串 %d:' % len(hit))
    for s in hit[:70]:
        print('      %s' % s)
    if not hit:
        for s in u[:40]:
            print('      %s' % s)
    # 中文
    try:
        zh = []
        for m in re.finditer(rb'[\xc0-\xef][\x80-\xbf]{1,2}(?:[\xc0-\xef][\x80-\xbf]{1,2})+', raw):
            try:
                s = m.group(0).decode('utf-8')
                if s not in zh:
                    zh.append(s)
            except Exception:
                pass
        print('   中文串 %d: %s' % (len(zh), zh[:30]))
    except Exception:
        pass
