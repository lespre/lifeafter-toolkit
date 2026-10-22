"""清敏感：① AES 密钥 ② 内网 IP ③ Windows 用户名路径（只改 tracked 文件 ✓）
   ★ 用 Python 直读写（emoji/反斜杠用 patch 易误判 ✗）"""
import re
import subprocess
from pathlib import Path

ROOT = Path(r'E:\la拆包项目')

out = subprocess.run(['git', 'ls-files'], cwd=str(ROOT), capture_output=True,
                     text=True, encoding='utf-8', errors='replace').stdout
files = [f for f in out.splitlines() if f.strip()]

# ① 精确串替换（安全 ✓）
EXACT = [
    # ★ NPK AES 密钥 → 脱敏（必须保留"这里曾有个 key"的语义 ✓）
    ('"aes_key": "606308d8a32c782013d26c2f226f686d"', '"aes_key": "[REDACTED]"'),
    ('606308d8a32c782013d26c2f226f686d', '[REDACTED]'),
    # ② 内网 IP → 通用占位
    ('192.168.31.52', '192.168.1.100'),
    ('192.168.31.', '192.168.1.'),
    # ③ Windows 用户名路径 → 占位（保留可读性 ✓）
    (r'C:\Users\Administrator', r'C:\Users\<你的用户名>'),
    (r'C:\\Users\\Administrator', r'C:\\Users\\<你的用户名>'),
    ('Users/Administrator', 'Users/<你的用户名>'),
    ('C:/Users/Administrator', 'C:/Users/<你的用户名>'),
    # ④ 备份仓库名（我改名的 ✓ 不该入库）
    ('.git.bak_repo', '.git.bak'),
]

changed = {}
for rel in files:
    p = ROOT / rel
    if not p.is_file():
        continue
    if p.suffix.lower() in ('.png', '.jpg', '.jpeg', '.gif', '.ico', '.woff', '.woff2',
                            '.ttf', '.zip', '.exe', '.dll', '.so', '.pack', '.idx'):
        continue
    try:
        raw = p.read_bytes()
    except Exception:
        continue
    try:
        txt = raw.decode('utf-8')
    except UnicodeDecodeError:
        continue
    orig = txt
    hits = []
    for old, new in EXACT:
        if old in txt:
            c = txt.count(old)
            txt = txt.replace(old, new)
            hits.append('%s→%s ×%d' % (old[:34], new[:22], c))
    if txt != orig:
        p.write_bytes(txt.encode('utf-8'))
        changed[rel] = hits

print('  改动文件 %d 个：' % len(changed))
for rel, hs in changed.items():
    print('   %s' % rel)
    for h in hs:
        print('      %s' % h)
