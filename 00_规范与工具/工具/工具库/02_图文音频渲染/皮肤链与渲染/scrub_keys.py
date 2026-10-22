"""彻底清密钥：用 git grep -l 精确找命中文件 ⇒ 替换 ⇒ 不依赖 git ls-files 的编码问题"""
import re
import subprocess
from pathlib import Path

ROOT = Path(r'E:\la拆包项目')
KEYS = ['606308d8a32c782013d26c2f226f686d', '118aad79bf2a9b17d899d63be05e7cb3']

# ① 用 git grep -l 找所有含密钥的【已入库】文件
hits = set()
for k in KEYS:
    r = subprocess.run(['git', 'grep', '-l', k], cwd=str(ROOT),
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    for line in (r.stdout or '').splitlines():
        line = line.strip()
        if line:
            hits.add(line)
print('  含密钥的 tracked 文件 %d 个：' % len(hits))
for h in sorted(hits):
    print('   %s' % h)

# ② 逐个替换
changed = []
for rel in sorted(hits):
    p = ROOT / rel
    if not p.is_file():
        print('   ✗ 打不开 %s' % rel)
        continue
    raw = p.read_bytes()
    try:
        txt = raw.decode('utf-8')
    except UnicodeDecodeError:
        print('   ✗ 非 utf-8: %s' % rel)
        continue
    orig = txt
    for k in KEYS:
        if k in txt:
            txt = txt.replace(k, '[REDACTED]')
        # 大写形式
        if k.upper() in txt:
            txt = txt.replace(k.upper(), '[REDACTED]')
    if txt != orig:
        p.write_bytes(txt.encode('utf-8'))
        changed.append(rel)
        print('   ✓ 已清 %s' % rel)

print()
print('  实际改动 %d / %d 个文件' % (len(changed), len(hits)))

# ③ 复查
print()
print('  ════ 复查（git grep ✓）════')
left = 0
for k in KEYS:
    r = subprocess.run(['git', 'grep', '-c', k], cwd=str(ROOT),
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    out = (r.stdout or '').strip()
    if out:
        left += 1
        print('   ✗ 仍在: %s' % out[:200])
    else:
        print('   ✓ 已无: %s…' % k[:16])
print('  %s' % ('✅ 工作区已清 ✓（但 git 历史仍需处理 ✗）' if left == 0 else '✗ 仍有残留'))
