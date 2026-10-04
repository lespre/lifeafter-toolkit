"""行体的 values 已解出 ✓ ⇒ 看若干行的 11 列值（即使无列名，值也可用 ✓）"""
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
pl = struct.unpack_from('<I', body, 52)[0]
pool_blob = body[56: 52 + pl]

pool_u = [m.group(0).decode('ascii', 'replace')
          for m in re.finditer(rb'[\x20-\x7E]{2,200}', pool_blob)]
rows, junk = BT.decode_table_rows(body, pool_u, None, False)
print('  rows=%d' % len(rows))
print()

keys = [r.get('key') for r in rows]
print('  key 范围 %s … %s（共 %d 个不同）' % (keys[0], keys[-1], len(set(keys))))
print()

for r in rows[:6]:
    print('  ── key=%s start=%s schema=%s bitmap=%s ──' % (
        r.get('key'), r.get('start'), r.get('schema'), r.get('bitmap')))
    for k, v in r.get('values', {}).items():
        print('      %-14s %s' % (k[:14], v))
    for g in r.get('inline_groups', []):
        print('      [group %s n=%s] %s' % (g.get('kind'), g.get('count'), g.get('elements')))
    print()

# 统计：每行多少列
import collections
c = collections.Counter(len(r.get('values', {})) for r in rows)
print('  每行列数分布: %s' % dict(c))
