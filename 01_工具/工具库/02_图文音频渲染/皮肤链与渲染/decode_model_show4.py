"""全文件扫：找出 [count][reserved=0][递增 ends][utf8串] 的合法 body 起点 ✓"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, r'E:\la拆包项目\01_工具\工具库\00_共享核心')
from toolkit_core import bindict_table as BT   # noqa: E402

P = Path(r'E:\la拆包项目\03_执行\41_还原树\Documents\script.py314.lc.npk\com\cdata\common_model_show_conf.py')
raw = P.read_bytes()
print('  文件 %d B' % len(raw))

found = []
for off in range(0, min(len(raw), 4096)):
    if off + 8 > len(raw):
        break
    cnt, res = struct.unpack_from('<II', raw, off)
    if res != 0 or not (0 < cnt < 200000):
        continue
    if 8 + 4 * cnt > len(raw) - off:
        continue
    try:
        ends = struct.unpack_from('<%dI' % cnt, raw, off + 8)
        if not all(a < b for a, b in zip(ends, ends[1:])):
            continue
        pool = BT.parse_chs_pool(raw[off:])
        if pool:
            found.append((off, cnt, len(pool), pool[:6]))
    except Exception:
        continue

print('  合法起点 %d 个:' % len(found))
for off, cnt, n, head in found[:8]:
    print('   @%-7d count=%-7d pool=%-6d  头: %s' % (off, cnt, n, head))

if found:
    off = found[0][0]
    body = raw[off:]
    print()
    print('  ════ 用 @%d 解表 ════' % off)
    pool = BT.parse_chs_pool(body)
    ok = 0
    for kw in (False, True):
        try:
            rows, junk = BT.decode_table_rows(body, pool, None, kw)
            print('  resolve_jumps=%s ⇒ rows=%d junk=%d' % (kw, len(rows), len(junk)))
            if rows:
                ok += 1
                print('     键: %s' % list(rows[0].keys())[:30])
                for r in rows[:3]:
                    print('     %s' % str(r)[:400])
                break
        except Exception as e:
            print('  resolve_jumps=%s ✗ %r' % (kw, repr(e)[:120]))
