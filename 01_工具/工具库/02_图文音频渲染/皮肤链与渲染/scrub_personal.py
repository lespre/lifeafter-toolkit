"""清个人信息（用户名路径 / 内网 IP）—— ★ 处理 git 的引号转义路径 ✓
   密钥按用户要求【保留】✓"""
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(r'E:\la拆包项目')

PATTERNS = [
    (re.compile(re.escape(r'C:\Users\Administrator')), r'C:\Users\<user>'),
    (re.compile(re.escape(r'C:\\Users\\Administrator')), r'C:\\Users\\<user>'),
    (re.compile(re.escape('C:/Users/Administrator')), 'C:/Users/<user>'),
    (re.compile(re.escape('Users/Administrator')), 'Users/<user>'),
    (re.compile(re.escape(r'C:\Users\Administrator')), r'C:\Users\<user>'),
    (re.compile(r'192\.168\.31\.\d{1,3}'), '192.168.1.100'),
    (re.compile(re.escape('Administrator')), '<user>') if False else (None, None),
]
PATTERNS = [p for p in PATTERNS if p[0] is not None]


def unquote_git_path(s: str) -> str:
    """git 输出的中文路径可能带双引号与 \\ 转义 ⇒ 还原成真实路径"""
    s = s.strip()
    if s.startswith('"') and s.endswith('"'):
        s = s[1:-1]
        # git 的八进制转义 \345\261\261 形式
        s = re.sub(r'\\(\d{3})', lambda m: chr(int(m.group(1), 8)), s)
        s = s.replace('\\"', '"').replace('\\\\', '\\')
    return s


# 用 grep 找含用户名路径 / 内网 IP 的 tracked 文件（-z 避免转义 ✓）
def tracked_hits(pattern: str):
    r = subprocess.run(['git', 'grep', '-z', '-l', '-I', '-E', pattern],
                       cwd=str(ROOT), capture_output=True)
    out = r.stdout or b''
    return [x.decode('utf-8', 'replace') for x in out.split(b'\x00') if x]


hits = set()
for pat in (r'Users.Administrator', r'192\.168\.31\.'):
    hits.update(tracked_hits(pat))

print('  命中 tracked 文件 %d 个：' % len(hits))
for h in sorted(hits):
    print('   %s' % h)

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
        print('   · 非 utf-8（跳过）%s' % rel)
        continue
    orig = txt
    for rgx, rep in PATTERNS:
        txt = rgx.sub(rep, txt)
    if txt != orig:
        p.write_bytes(txt.encode('utf-8'))
        changed.append(rel)

print()
print('  已清 %d / %d 个文件' % (len(changed), len(hits)))
for c in changed:
    print('   ✓ %s' % c)

print()
print('  ════ 复查 ════')
for pat in (r'Users.Administrator', r'192\.168\.31\.'):
    n = len(tracked_hits(pat))
    print('   %-24s %s' % (pat, '✓ 已清' if n == 0 else '✗ 仍 %d 个文件' % n))
