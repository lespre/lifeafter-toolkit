"""斩神专题截图 → docs/images/web-zhanshen.png；删 web-lottery.png"""
from pathlib import Path

from PIL import Image

T = Path(r'E:\la拆包项目\03_执行\90_临时')
D = Path(r'E:\la拆包项目\docs\images')

src = T / 'web_zhanshen.png'
im = Image.open(src).convert('RGB')
print('  原图 %dx%d %.0f KB' % (im.width, im.height, src.stat().st_size / 1024))
dst = D / 'web-zhanshen.png'
for w, q in ((1400, 82), (1280, 78), (1150, 75)):
    t = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
    t.save(dst, optimize=True, quality=q)
    kb = dst.stat().st_size / 1024
    print('  %dx%d q=%d → %.0f KB' % (t.width, t.height, q, kb))
    if kb <= 420:
        break
print('  ➜ %s  %.0f KB' % (dst.name, dst.stat().st_size / 1024))

bad = D / 'web-lottery.png'
if bad.is_file():
    bad.unlink()
    print('  ✗ 已删 web-lottery.png（按用户要求换斩神渲染图）')

print()
for f in sorted(D.glob('*.png')):
    print('   %-22s %7.0f KB' % (f.name, f.stat().st_size / 1024))
