"""wiki / lottery 截图 → docs/images/（压缩 ✓）并删除弃用的 web-home"""
from pathlib import Path

from PIL import Image

T = Path(r'E:\la拆包项目\03_执行\90_临时')
D = Path(r'E:\la拆包项目\docs\images')

for src, dst in (('web_wiki.png', 'web-wiki.png'), ('web_lottery.png', 'web-lottery.png')):
    p = T / src
    if not p.is_file():
        print('  · 缺 %s' % src)
        continue
    im = Image.open(p).convert('RGB')
    if im.width > 1500:
        im = im.resize((1500, int(im.height * 1500 / im.width)), Image.LANCZOS)
    o = D / dst
    im.save(o, optimize=True, quality=82)
    print('  ✓ %-18s %dx%d  %.0f KB' % (dst, im.width, im.height, o.stat().st_size / 1024))

# 弃用：状态看板（含"半吊子/缺"字样 ✗ 不适合对外）
bad = D / 'web-home.png'
if bad.is_file():
    bad.unlink()
    print('  ✗ 已删 web-home.png（状态看板，含内部进度字样）')

print()
for f in sorted(D.glob('*.png')):
    print('   %-20s %7.0f KB' % (f.name, f.stat().st_size / 1024))
