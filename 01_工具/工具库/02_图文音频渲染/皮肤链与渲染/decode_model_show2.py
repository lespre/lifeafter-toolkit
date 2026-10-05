"""用 bindict_table 的正确入口解 common_model_show_conf。"""
import inspect
import sys
from pathlib import Path

sys.path.insert(0, r'E:\la拆包项目\01_工具\工具库\00_共享核心')
from toolkit_core import bindict_table as BT   # noqa: E402

for fn in ('parse_index', 'decode_table_rows', 'parse_chs_pool', 'parse_legacy_chs_pool',
           'decode_86_row', 'read_27_group', 'resolve_row_jumps'):
    f = getattr(BT, fn, None)
    if f:
        try:
            print('  %-22s %s' % (fn, inspect.signature(f)))
        except Exception as e:
            print('  %-22s %r' % (fn, e))
print()
print('  常量：MAPPING_MARKER=%r ROW_MARKERS=%r' % (
    getattr(BT, 'MAPPING_MARKER', None), getattr(BT, 'ROW_MARKERS', None)))
print()

P = Path(r'E:\la拆包项目\03_执行\41_还原树\Documents\script.py314.lc.npk\com\cdata\common_model_show_conf.py')
raw = P.read_bytes()
print('  文件 %d B  x{@%d' % (len(raw), raw.find(b'x{')))

# 试 parse_index
try:
    idx = BT.parse_index(raw)
    print('  ✓ parse_index -> %s' % type(idx).__name__)
    print('     %s' % str(idx)[:600])
except Exception as e:
    print('  ✗ parse_index: %r' % e)

# 试 decode_table_rows（签名可能带 index ✓）
try:
    sig = inspect.signature(BT.decode_table_rows)
    n = len(sig.parameters)
    if n == 1:
        rows = BT.decode_table_rows(raw)
    elif n == 2:
        rows = BT.decode_table_rows(raw, idx)
    else:
        rows = BT.decode_table_rows(raw, 0, len(raw))
    rows = list(rows) if hasattr(rows, '__iter__') else rows
    print('  ✓ decode_table_rows -> %d 行' % len(rows))
    for r in rows[:5]:
        print('     %s' % str(r)[:400])
except Exception as e:
    print('  ✗ decode_table_rows: %r' % e)
