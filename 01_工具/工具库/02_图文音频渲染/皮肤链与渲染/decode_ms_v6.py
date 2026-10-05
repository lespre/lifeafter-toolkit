"""修正 jump 基准：试 pool_blob / body 三种基址 ⇒ 找到能解出连续合理值的那个 ✓"""
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

TAGS = {0x12: 5, 0x22: 9}   # tag -> total size


def scan_values(buf, off, limit=12):
    """从 off 起按 tag 步进解值（f32/f64/整数/jump）"""
    out = []
    p = off
    while len(out) < limit and p < len(buf):
        t = buf[p]
        if t == 0x12 and p + 5 <= len(buf):
            v = struct.unpack_from('<f', buf, p + 1)[0]
            out.append(('f32', round(v, 4)))
            p += 5
        elif t == 0x22 and p + 9 <= len(buf):
            v = struct.unpack_from('<d', buf, p + 1)[0]
            out.append(('f64', round(v, 4)))
            p += 9
        elif t == 0x03 and p + 2 <= len(buf):
            out.append(('bool', buf[p + 1] != 0))
            p += 2
        elif t == 0x0b and p + 2 <= len(buf):
            # uleb 引用
            q, sh = 0, 0
            k = p + 1
            while k < len(buf) and buf[k] & 0x80:
                q |= (buf[k] & 0x7F) << sh
                sh += 7
                k += 1
            q |= (buf[k] & 0x7F) << sh if k < len(buf) else 0
            out.append(('ref', q))
            p = k + 1
        else:
            out.append(('tag%02X' % t, buf[p + 1:p + 5].hex(' ')))
            p += 1
    return out


# 先看一个已知行 key=1000：hD = jump:2882
r = None
pool_u = [m.group(0).decode('ascii', 'replace')
          for m in re.finditer(rb'[\x20-\x7E]{2,200}', pool_blob)]
rows, junk = BT.decode_table_rows(body, pool_u, None, False)
bykey = {q['key']: q for q in rows if 'key' in q}
r = bykey.get(1000)
print('  key=1000 的 values:')
for k, v in (r.get('values') or {}).items():
    print('     %-16s %s' % (k[:16], v))

print()
bases = {
    'pool_blob': pool_blob,
    'body': body,
    'body[56:]': body[56:],
    'rest': body[52 + pl:],
}
for name, buf in bases.items():
    print('  ── 基准 %s (%d B) ──' % (name, len(buf)))
    for tgt in (2882, 7534, 1401, 931, 50, 168):
        if tgt < len(buf):
            print('     @%-6d %s' % (tgt, scan_values(buf, tgt, 8)))
    print()
