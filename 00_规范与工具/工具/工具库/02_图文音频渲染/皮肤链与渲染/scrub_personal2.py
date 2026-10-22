"""清个人信息 v2 —— 纯字符串替换（无正则 ✓ 不踩 \\U 转义 ✗）
   密钥按用户要求保留 ✓"""
import subprocess
from pathlib import Path

ROOT = Path(r'E:\la拆包项目')

# 纯字符串替换（顺序重要：长的先 ✓）
PAIRS = [
    ('C:\\Users\\Administrator', 'C:\\Users\\<user>'),   # 双反斜杠形式（代码里常见）
    (r'C:\Users\Administrator', r'C:\Users\<user>'),     # 单反斜杠
    ('C:/Users/Administrator', 'C:/Users/<user>'),
    ('Users/Administrator', 'Users/<user>'),
    ('192.168.31.52', '192.168.1.100'),
]


def hits_of(pat: str):
    r = subprocess.run(['git', 'grep', '-z', '-l', '-I', '-F', pat],
                       cwd=str(ROOT), capture_output=True)
    return [x.decode('utf-8', 'replace') for x in (r.stdout or b'').split(b'\x00') if x]


files = set()
for a, _ in PAIRS:
    files.update(hits_of(a))
print('  命中 tracked 文件 %d 个' % len(files))

changed = 0
failed = []
for rel in sorted(files):
    p = ROOT / rel
    if not p.is_file():
        failed.append(rel)
        continue
    raw = p.read_bytes()
    try:
        txt = raw.decode('utf-8')
    except UnicodeDecodeError:
        failed.append(rel + ' (非utf-8)')
        continue
    orig = txt
    for a, b in PAIRS:
        if a in txt:
            txt = txt.replace(a, b)
    if txt != orig:
        p.write_bytes(txt.encode('utf-8'))
        changed += 1

print('  已清 %d 个文件；跳过 %d 个' % (changed, len(failed)))
for f in failed[:8]:
    print('   · %s' % f)

print()
print('  ════ 复查 ════')
for a, _ in PAIRS:
    n = len(hits_of(a))
    print('   %-28s %s' % (a, '✓ 已清' if n == 0 else '✗ 仍 %d 个' % n))
