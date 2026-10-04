"""扫【已入库文件】里的敏感信息（只扫 tracked ✓ 不扫工作区噪声）
   类别：密钥/token · AES 密钥样式 · 用户名/绝对路径 · 邮箱 · 私钥 · IP"""
import re
import subprocess
from pathlib import Path

ROOT = Path(r'E:\la拆包项目')

# 取 tracked 文件清单（相对路径 ✓）
out = subprocess.run(['git', 'ls-files'], cwd=str(ROOT), capture_output=True, text=True,
                     encoding='utf-8', errors='replace').stdout
files = [f for f in out.splitlines() if f.strip()]
print('  tracked 文件 %d 个' % len(files))

PATTERNS = [
    ('私钥', re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----')),
    ('GitHub token', re.compile(r'\b(gh[pousr]_[A-Za-z0-9]{20,})\b')),
    ('OpenAI key', re.compile(r'\bsk-[A-Za-z0-9]{20,}\b')),
    ('AWS key', re.compile(r'\bAKIA[0-9A-Z]{16}\b')),
    ('通用 bearer', re.compile(r'(?i)bearer\s+[A-Za-z0-9\-_.]{20,}')),
    ('账号密码字段', re.compile(r'(?i)(password|passwd|pwd|secret|api_?key)\s*[:=]\s*["\'][^"\']{6,}["\']')),
    ('AES 密钥样式(32/64 hex)', re.compile(r'\b[0-9A-Fa-f]{32,64}\b')),
    ('Windows 用户名路径', re.compile(r'C:\\+Users\\+[A-Za-z0-9_.\-]+')),
    ('邮箱', re.compile(r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b')),
    ('手机号', re.compile(r'\b1[3-9]\d{9}\b')),
    ('身份证', re.compile(r'\b\d{17}[\dXx]\b')),
    ('内网 IP', re.compile(r'\b192\.168\.\d{1,3}\.\d{1,3}\b')),
    ('实名/账号词', re.compile(r'(?i)(网易账号|通行证|实名|身份证号|手机绑定)')),
]

# 允许白名单（不是敏感）
ALLOW = re.compile(
    r'^(?:[0-9a-f]{32})$'      # 纯 32 hex 可能是哈希 fid（项目里大量）—— 单独判断
)

hits = {}
for rel in files:
    p = ROOT / rel
    if not p.is_file():
        continue
    suf = p.suffix.lower()
    if suf in ('.png', '.jpg', '.jpeg', '.gif', '.ico', '.woff', '.woff2', '.ttf', '.zip', '.exe', '.dll'):
        continue
    try:
        txt = p.read_text('utf-8', errors='ignore')
    except Exception:
        continue
    for name, rgx in PATTERNS:
        for m in rgx.finditer(txt):
            s = m.group(0)
            # 32~64 hex 太常见（fid/hash）⇒ 只在疑似密钥上下文才报
            if name.startswith('AES'):
                ctx = txt[max(0, m.start() - 40):m.end() + 40].lower()
                if not any(k in ctx for k in ('key', 'aes', 'secret', 'iv', '密钥')):
                    continue
            key = (name, s if len(s) < 70 else s[:60] + '…')
            hits.setdefault(key, []).append(rel)

if not hits:
    print()
    print('  ✅ 未检出敏感信息')
else:
    print()
    print('  ⚠️ 命中 %d 类：' % len(hits))
    for (name, s), fs in sorted(hits.items()):
        print('   [%s] %r' % (name, s))
        for f in fs[:4]:
            print('        %s' % f)
        if len(fs) > 4:
            print('        … 共 %d 个文件' % len(fs))
