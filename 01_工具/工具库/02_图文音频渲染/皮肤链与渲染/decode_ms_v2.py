"""按真实布局解：
   [count u32][48B 保留][u32 池长][池][行体]
   ⇒ 池 = body[56 : 52+poollen] ；行体 = body[52+poollen:]
"""
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, r'E:\la拆包项目\01_工具\工具库\00_共享核心')
from toolkit_core import bindict_table as BT   # noqa: E402

P = Path(r'E:\la拆包项目\03_执行\41_还原树\Documents\script.py314.lc.npk\com\cdata\common_model_show_conf.py')
raw = P.read_bytes()
x = raw.find(b'x{')
ln = struct.unpack_from('<I', raw, x + 2)[0]
body = raw[x + 6: x + 6 + ln]

cnt = struct.unpack_from('<I', body, 0)[0]
pool_len = struct.unpack_from('<I', body, 52)[0]
POOL_OFF = 56
pool_blob = body[POOL_OFF: 52 + pool_len]
rest = body[52 + pool_len:]
print('  count=%d  pool_len=%d  pool=%d B  rest=%d B' % (cnt, pool_len, len(pool_blob), len(rest)))
print()

# 池里抽可读串（这就是"列名/值"的来源 ✓）
u = []
for m in re.finditer(rb'[\x20-\x7E]{2,120}', pool_blob):
    s = m.group(0).decode('ascii', 'replace')
    if s not in u:
        u.append(s)
print('  ★ 池可读串 %d 条（前 60）:' % len(u))
for s in u[:60]:
    print('     %s' % s)

print()
print('  ★ 含语义关键词的:')
KEY = ('camera', 'model', 'light', 'color', 'zoom', 'env', 'weather', 'scene',
       'skin', 'weapon', 'pos', 'rot', 'angle', 'fov', 'dist', 'intensity', 'conf')
for s in u:
    if any(k in s.lower() for k in KEY):
        print('     %s' % s)

print()
print('  ════ rest 头 128B ════')
for i in range(0, min(128, len(rest)), 16):
    seg = rest[i:i + 16]
    print('   %04X  %-47s  %s' % (i, ' '.join('%02x' % b for b in seg),
                                  ''.join(chr(c) if 32 <= c < 127 else '.' for c in seg)))
