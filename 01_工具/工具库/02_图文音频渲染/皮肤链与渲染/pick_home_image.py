"""首页截图 → docs/images/web-home.png（压缩 ✓）"""
from pathlib import Path

from PIL import Image

SRC = Path(r'E:\la拆包项目\03_执行\90_临时\web_home.png')
DST = Path(r'E:\la拆包项目\docs\images\web-home.png')

im = Image.open(SRC).convert('RGB')
print('  原图 %dx%d  %.0f KB' % (im.width, im.height, SRC.stat().st_size / 1024))
maxw = 1500
if im.width > maxw:
    im = im.resize((maxw, int(im.height * maxw / im.width)), Image.LANCZOS)
im.save(DST, optimize=True, quality=80)
kb = DST.stat().st_size / 1024
if kb > 450:
    im2 = im.resize((int(im.width * 0.8), int(im.height * 0.8)), Image.LANCZOS)
    im2.save(DST, optimize=True, quality=76)
    kb = DST.stat().st_size / 1024
print('  ➜ %s  %dx%d  %.0f KB' % (DST, im.width, im.height, kb))
