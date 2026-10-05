"""找 body 起点 → parse_chs_pool → decode_table_rows（试多起点 ✓）"""
import sys
from pathlib import Path

sys.path.insert(0, r'E:\la拆包项目\01_工具\工具库\00_共享核心')
from toolkit_core import bindict_table as BT   # noqa: E402

P = Path(r'E:\la拆包项目\03_执行\41_还原树\Documents\script.py314.lc.npk\com\cdata\common_model_show_conf.py')
raw = P.read_bytes()
x = raw.find(b'x{')
print('  x{ @%d  文件 %d B' % (x, len(raw)))
print('  x{ 后 32B: %s' % raw[x:x + 32].hex(' '))
print()

for skip in (2, 4, 6, 8, 10, 12, 16, 20, 24, 28, 32, 36, 48, 64):
    body = raw[x + skip:]
    try:
        pool = BT.parse_chs_pool(body)
        if not pool:
            continue
        rows, junk = BT.decode_table_rows(body, pool)
        print('  skip=%-3d ✓ pool=%-5d rows=%-5d junk=%-4d' % (skip, len(pool), len(rows), len(junk)))
        if rows:
            print('     首行键: %s' % list(rows[0].keys())[:30])
            print('     首行: %s' % str(rows[0])[:500])
            break
    except Exception as e:
        print('  skip=%-3d ✗ %r' % (skip, repr(e)[:80]))
