"""最终：首页截图压缩 → docs/images/web-home.png（首图 ✓）"""
from pathlib import Path

from PIL import Image

SRC = Path(r'E:\la拆包项目\03_执行\90_临时\web_home_final.png')
DST = Path(r'E:\la拆包项目\docs\images\web-home.png')

im = Image.open(SRC).convert('RGB')
print('  原图 %dx%d %.0f KB' % (im.width, im.height, SRC.stat().st_size / 1024))
for w, q in ((1400, 80), (1280, 76), (1150, 72)):
    t = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
    t.save(DST, optimize=True, quality=q)
    kb = DST.stat().st_size / 1024
    print('  %dx%d q=%d → %.0f KB' % (t.width, t.height, q, kb))
    if kb <= 420:
        break
print('  ➜ %s  %.0f KB' % (DST.name, DST.stat().st_size / 1024))
