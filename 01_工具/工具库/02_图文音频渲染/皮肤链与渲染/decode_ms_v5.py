"""解 jump 链 ⇒ 看一层引用后的真实值（f32/f64/颜色 ✓）"""
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
bykey = {r['key']: r for r in rows if 'key' in r}
print('  行 %d  bykey %d' % (len(rows), len(bykey)))


def read_at(off, n=8):
    """把 body[off:] 解成有意义的标量序列（按 tag ✓）"""
    out = []
    p = off
    for _ in range(n):
        if p >= len(body):
            break
        t = body[p]
        if t == 0x12 and p + 5 <= len(body):
            v = struct.unpack_from('<f', body, p + 1)[0]
            out.append(('f32', round(v, 5)))
            p += 5
        elif t == 0x22 and p + 9 <= len(body):
            v = struct.unpack_from('<d', body, p + 1)[0]
            out.append(('f64', round(v, 5)))
            p += 9
        elif t in (0x0b,):
            # 也许是 uleb / 引用
            out.append(('0x0b', body[p:p + 6].hex(' ')))
            p += 1
        else:
            out.append(('tag%02X' % t, body[p:p + 5].hex(' ')))
            p += 1
        if len(out) >= n:
            break
    return out


for k in (1, 4, 5, 100, 500, 1000, 1602):
    r = bykey.get(k)
    if not r:
        continue
    print()
    print('  ── key=%s start=%s ──' % (k, r.get('start')))
    for vk, vv in (r.get('values') or {}).items():
        print('      %s = %s' % (vk[:16], vv))
        if isinstance(vv, tuple) and vv[0] == '0x0b' and str(vv[1]).startswith('jump:'):
            tgt = int(str(vv[1]).split(':')[1])
            print('         ⇒ @%d 解: %s' % (tgt, read_at(tgt, 6)))
