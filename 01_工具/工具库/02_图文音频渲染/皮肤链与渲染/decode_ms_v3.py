"""行体 = 偏移索引结构 ⇒ 用模块的 decode_table_rows（base_body=rest, pool=池串）"""
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
rest = body[52 + pl:]

# 池按 NUL 或长度切？先把池整体当一个"字符串"，再试 parse_chs_pool 的变体
pool_u = []
for m in re.finditer(rb'[\x20-\x7E]{2,200}', pool_blob):
    pool_u.append(m.group(0).decode('ascii', 'replace'))
print('  池串 %d 条' % len(pool_u))

# index_rows = 从 rest 里抽 (key, off) 对
idx = []
for i in range(0, len(rest) - 8, 4):
    a, b = struct.unpack_from('<II', rest, i)
    if a < len(body) and b < len(body):
        idx.append((a, b))
print('  候选 (key,off) 对 %d' % len(idx))

for label, bb, plist, irows in (
        ('rest+池串+index', rest, pool_u, idx),
        ('rest+池串', rest, pool_u, None),
        ('body+池串+index', body, pool_u, idx),
        ('body+池串', body, pool_u, None),
):
    for rj in (False, True):
        try:
            rows, junk = BT.decode_table_rows(bb, plist, irows, rj)
            if rows:
                print('  ✓ [%s] rj=%s rows=%d' % (label, rj, len(rows)))
                print('     键: %s' % list(rows[0].keys())[:30])
                for r in rows[:3]:
                    print('     %s' % str(r)[:400])
                raise SystemExit(0)
            else:
                print('  · [%s] rj=%s rows=0 junk=%d' % (label, rj, len(junk)))
        except SystemExit:
            raise
        except Exception as e:
            print('  ✗ [%s] rj=%s %r' % (label, rj, repr(e)[:110]))
print()
print('  ⇒ 模块解不出 ⇒ 我手解：按 rest 的 4B 对齐读 (off, val) 并解析池')
# 手解：rest 每 8 字节 = (off u32, val u32)？
n = len(rest) // 8
print('  rest/8 = %d 组' % n)
for i in range(0, min(6, n)):
    off, val = struct.unpack_from('<II', rest, i * 8)
    s = ''
    if 0 <= off < len(pool_blob):
        s = ''.join(chr(c) if 32 <= c < 127 else '.' for c in pool_blob[off:off + 40])
    print('   [%d] off=0x%06X val=0x%08X(%d)  池@off: %s' % (i, off, val, val, s))
