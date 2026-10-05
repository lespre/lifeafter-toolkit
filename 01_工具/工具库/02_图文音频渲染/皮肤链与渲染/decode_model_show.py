"""用 toolkit_core.bindict_table 直接解 common_model_show_conf（找表体标记 ✓）"""
import sys
from pathlib import Path

sys.path.insert(0, r'E:\la拆包项目\01_工具\工具库\00_共享核心')
from toolkit_core import bindict_table as BT   # noqa: E402

P = Path(r'E:\la拆包项目\03_执行\41_还原树\Documents\script.py314.lc.npk\com\cdata\common_model_show_conf.py')
raw = P.read_bytes()
print('  文件 %d B' % len(raw))
print('  接口: %s' % [n for n in dir(BT) if not n.startswith('_')][:24])

# ① 找 'x{' 表体标记
for marker in (b'x{', b'\x78\x7b', b'x{'):
    i = raw.find(marker)
    print('  find %r -> %s' % (marker, i))

# ② 试各种入口
for fn in ('parse', 'load', 'read', 'decode', 'table_of', 'rows_of', 'columns_of'):
    if hasattr(BT, fn):
        f = getattr(BT, fn)
        try:
            r = f(str(P))
            print('  ✓ %s(str) -> %s %s' % (fn, type(r).__name__,
                                            (str(r)[:300] if not isinstance(r, (list, dict)) else
                                             ('len=%d' % len(r)))))
            if isinstance(r, dict):
                print('     keys: %s' % list(r.keys())[:20])
                for k in list(r.keys())[:6]:
                    v = r[k]
                    print('       %s = %s' % (k, str(v)[:160]))
            elif isinstance(r, list) and r:
                print('     [0]: %s' % str(r[0])[:300])
        except Exception as e:
            print('  ✗ %s -> %r' % (fn, e))

# ③ 用 bytes 入口
for fn in ('parse', 'load', 'decode', 'parse_table'):
    if hasattr(BT, fn):
        try:
            r = getattr(BT, fn)(raw)
            print('  ✓ %s(bytes) -> %s' % (fn, str(r)[:300]))
        except Exception:
            pass
