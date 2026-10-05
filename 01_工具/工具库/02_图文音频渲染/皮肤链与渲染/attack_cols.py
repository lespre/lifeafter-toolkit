"""攻列名：① common_model_show_conf_chs 的字段 ② 引擎 schema 注册表 ③ 对比同名表的其他副本"""
import re
import struct
import sys
from pathlib import Path

ROOT = Path(r'E:\la拆包项目')
S = ROOT / '03_执行/41_还原树/Documents/script.py314.lc.npk'
sys.path.insert(0, str(ROOT / '01_工具/工具库/00_共享核心'))

FIND = [
    'com/cdata/common_model_show_conf.py',
    'com/cdata/common_model_show_conf_chs.py',
    'com/cdata/oversea/common_model_show_conf_chs.py',
]
for rel in FIND:
    p = S / rel
    if not p.is_file():
        print('  · 无 %s' % rel)
        continue
    raw = p.read_bytes()
    x = raw.find(b'x{')
    print()
    print('  ── %s (%d B)  x{@%s ──' % (rel, len(raw), x))
    if x >= 0:
        ln = struct.unpack_from('<I', raw, x + 2)[0]
        body = raw[x + 6: x + 6 + ln]
        cnt = struct.unpack_from('<I', body, 0)[0]
        pl = struct.unpack_from('<I', body, 52)[0]
        print('     count=%s pool_len=%s rows=%s' % (cnt, pl, len(body) - 52 - pl))
    # 该文件里的可读中文/标识串（列名可能在这 ✓）
    u = []
    for m in re.finditer(rb'[\x20-\x7E]{4,120}', raw):
        s = m.group(0).decode('ascii', 'replace')
        if s not in u:
            u.append(s)
    ident = [s for s in u if re.fullmatch(r'[a-z_][a-z0-9_]*', s)]
    print('     标识符样式串 %d: %s' % (len(ident), ident[:40]))
    # 中文（UTF-8）
    try:
        txt = raw.decode('utf-8', 'ignore')
        zh = re.findall(r'[\u4e00-\u9fff]{2,20}', txt)
        seen = []
        for z in zh:
            if z not in seen:
                seen.append(z)
        print('     中文串 %d: %s' % (len(seen), seen[:30]))
    except Exception as e:
        print('     中文抽取失败 %r' % e)

# 引擎 schema：AttributeHelper / schema 注册表
print()
print('  ════ 引擎侧 schema 表 ════')
for pat in ('*schema*', '*Schema*', '*AttributeHelper*', '*bin_schema*', '*bin_dict*'):
    for f in S.rglob(pat):
        if f.is_file():
            print('   %8d  %s' % (f.stat().st_size, str(f.relative_to(S))[:90]))
