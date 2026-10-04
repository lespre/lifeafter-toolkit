"""选图 + 压缩 ⇒ docs/images/（网页友好 ✓ 每张 <500KB ✓）"""
from pathlib import Path

from PIL import Image

SRC = Path(r'E:\la拆包项目\03_执行\90_临时')
DST = Path(r'E:\la拆包项目\docs\images')
DST.mkdir(parents=True, exist_ok=True)

# (源文件, 输出名, 最大宽, 说明)
PICK = [
    ('v2_realtex.png',            'preview-page.png',  1400, '武器皮肤预览页（真贴图 + 官方相机 + 22:00 天气）'),
    ('SKIN_1003_010_TEXTURES.png', 'skin-textures.png', 1600, '皮肤 7 张贴图（基色/参数/法线/表面 + 细节/单通道）'),
    ('CHANNEL_COMPARE.png',       'channel-ident.png', 1400, '通道统计判身份（法线 / 参数 / 单通道 / 基色）'),
    ('FINAL_1110171_full.png',    'render-chain.png',  1400, '渲染链出图（材质分层 → 成品）'),
    ('full_chain_4way.png',       'chain-4way.png',    1400, '全链四路对比'),
    ('LOOSE_WEAPON_TEX.png',      'loose-textures.png', 1400, '散文件层解出的武器贴图'),
]

made = []
for src, dst, maxw, desc in PICK:
    p = SRC / src
    if not p.is_file():
        print('  · 缺 %s' % src)
        continue
    im = Image.open(p).convert('RGB')
    if im.width > maxw:
        h = int(im.height * maxw / im.width)
        im = im.resize((maxw, h), Image.LANCZOS)
    o = DST / dst
    im.save(o, optimize=True, quality=82)
    kb = o.stat().st_size / 1024
    # 若还太大 ⇒ 再缩
    if kb > 500:
        im2 = im.resize((int(im.width * 0.75), int(im.height * 0.75)), Image.LANCZOS)
        im2.save(o, optimize=True, quality=78)
        kb = o.stat().st_size / 1024
    made.append((dst, im.size, kb, desc))
    print('  ✓ %-22s %sx%s  %.0f KB  %s' % (dst, im.width, im.height, kb, desc))

print()
print('  ➜ %s  （共 %d 张）' % (DST, len(made)))
for d, sz, kb, desc in made:
    print('     ![%s](docs/images/%s)' % (desc, d))
