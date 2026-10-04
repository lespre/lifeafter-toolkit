"""按 table_export 的实测布局切 body ⇒ parse_chs_pool ⇒ decode_table_rows ✓"""
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
print('  x=%d ln=%d body=%d B（文件 %d B）' % (x, ln, len(body), len(raw)))
print('  body 头 16B: %s' % body[:16].hex(' '))

pool = BT.parse_chs_pool(body)
print('  ✓ pool %d 条' % len(pool))
print('     前 40: %s' % pool[:40])

# 去掉池那一段，取行体
# parse_chs_pool 内部：[count][reserved][ends...][strings] ⇒ 行体在池之后
cnt, res = struct.unpack_from('<II', body, 0)
tail = 8 + 4 * cnt
last_end = struct.unpack_from('<I', body, 8 + 4 * (cnt - 1))[0]
rest = body[tail + last_end:]
print('  count=%d 池体结束于 %d ⇒ 行体 %d B' % (cnt, tail + last_end, len(rest)))
print('  行体头 32B: %s' % rest[:32].hex(' '))

print()
for name, blob in (('rest', rest), ('body', body)):
    for idx_rows in (None,):
        for rj in (False, True):
            try:
                rows, junk = BT.decode_table_rows(blob, pool, idx_rows, rj)
                print('  ✓ [%s] resolve_jumps=%s rows=%d junk=%d' % (name, rj, len(rows), len(junk)))
                if rows:
                    print('     键: %s' % list(rows[0].keys())[:30])
                    for r in rows[:4]:
                        print('     %s' % str(r)[:420])
                    raise SystemExit(0)
            except SystemExit:
                raise
            except Exception as e:
                print('  ✗ [%s] rj=%s %r' % (name, rj, repr(e)[:130]))
