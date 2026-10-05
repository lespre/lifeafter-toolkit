"""完整读 fashion_bg_data_chs.py 的 weaponskin 行（44 列 ✓ 有列名 ✓ 正主 ✓）"""
import re
from pathlib import Path

P = Path(r'E:\la拆包项目\03_执行\41_还原树\Documents\script.py314.lc.npk\com\cdata\fashion_bg_data_chs.py')
raw = P.read_bytes()
print('  %s  %d B' % (P.name, len(raw)))

# ① 全部可读串
u = []
for m in re.finditer(rb'[\x20-\x7E]{2,200}', raw):
    s = m.group(0).decode('ascii', 'replace')
    if s not in u:
        u.append(s)
print('  可读串 %d' % len(u))
print()
print('  ════ 全部可读串（按顺序 ✓ 列名在前 ✓）════')
for i, s in enumerate(u):
    print('   [%3d] %s' % (i, s))

# ② 中文
print()
zh = []
for m in re.finditer(rb'[\xc0-\xef][\x80-\xbf]{1,2}(?:[\xc0-\xef][\x80-\xbf]{1,2})+', raw):
    try:
        s = m.group(0).decode('utf-8')
        if s not in zh:
            zh.append(s)
    except Exception:
        pass
print('  中文串 %d: %s' % (len(zh), zh[:40]))

# ③ 头字节
print()
print('  ════ 头 128B ════')
for i in range(0, min(128, len(raw)), 16):
    seg = raw[i:i + 16]
    print('   %04X  %-47s  %s' % (i, ' '.join('%02x' % b for b in seg),
                                  ''.join(chr(c) if 32 <= c < 127 else '.' for c in seg)))
