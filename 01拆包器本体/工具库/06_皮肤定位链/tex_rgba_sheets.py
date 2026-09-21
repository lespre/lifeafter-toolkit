# -*- coding: utf-8 -*-
"""tex_rgba_sheets.py — 贴图 RGBA 通道证据图 (候选矩阵交付用)
输出: 每个文件一张 4 通道图 (R/G/B/A 灰度四联 + RGB 原图), 以及总矩阵拼版。
用法: python tex_rgba_sheets.py <out_dir> <file1.dds> <file2.dds> ...
"""
import sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from raw_anchor import decode_dds_bc7

F = ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc', 22)

def chan_img(a, ch):
    g = (a[..., ch] * 255).astype(np.uint8)
    return Image.fromarray(g).convert('RGB')

def main():
    out = sys.argv[1]
    files = sys.argv[2:]
    os.makedirs(out, exist_ok=True)
    thumbs = []
    for f in files:
        fid = os.path.splitext(os.path.basename(f))[0]
        a = decode_dds_bc7(f).astype(np.float32) / 255.0
        TH = 256
        rgb = Image.fromarray((a[..., :3] * 255).astype(np.uint8)).resize((TH, TH), Image.LANCZOS)
        channels = [rgb] + [chan_img(a, c).resize((TH, TH), Image.LANCZOS) for c in (0, 1, 2, 3)]
        labels = ['RGB原图', 'R通道', 'G通道', 'B通道', 'A通道']
        cv = Image.new('RGB', (TH * 5 + 6 * 6, TH + 34), (14, 16, 20))
        d = ImageDraw.Draw(cv)
        for i, (im, lb) in enumerate(zip(channels, labels)):
            x = 6 + i * (TH + 6)
            cv.paste(im, (x, 6))
            d.text((x + 4, TH + 10), lb, font=F, fill=(230, 233, 240))
        d.text((6, -20), '', font=F, fill=(230, 230, 230))
        save_p = os.path.join(out, 'rgba_%s.png' % fid)
        cv.save(save_p)
        thumbs.append((fid, channels))
        print('saved', save_p)
    # 总矩阵 (每文件一行)
    TH2 = 150
    cols = 6  # 文件+5通道
    rows = len(thumbs)
    mcv = Image.new('RGB', (TH2 * cols + 8 * (cols + 1) + 130, (TH2 + 8) * rows + 8), (14, 16, 20))
    dm = ImageDraw.Draw(mcv)
    for r, (fid, channels) in enumerate(thumbs):
        y = 8 + r * (TH2 + 8)
        dm.text((8, y + TH2 // 2 - 10), fid, font=F, fill=(235, 238, 245))
        for c, im in enumerate(channels):
            mcv.paste(im.resize((TH2, TH2), Image.LANCZOS), (130 + 8 + c * (TH2 + 8), y))
    # 表头
    for c, lb in enumerate(['RGB', 'R', 'G', 'B', 'A']):
        dm.text((130 + 8 + c * (TH2 + 8) + 4, 8), lb, font=F, fill=(200, 210, 230))
    sp = os.path.join(out, 'matrix_sheet.png')
    mcv.save(sp)
    print('saved', sp, mcv.size)

if __name__ == '__main__':
    main()
