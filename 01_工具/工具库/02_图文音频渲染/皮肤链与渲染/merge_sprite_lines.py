# -*- coding: utf-8 -*-
"""merge_sprite_lines.py — 复现 NeoX/cocos2d `MergeSprite` + `BinPackAlgorithm_Lines` 的 512 页打包。

引擎侧证据（libclient.so @0x0093113a / 0x0095d2c4）:
    <cocosui SharedTextureSize="512">
      <MergeSprite Enabled="True">
        <Group Algorithm="Lines" Format_PC="RGBA" Name="Icon"
               PackingTextureLimit="4" Regex="ui/item_icon/.*_s.png" TextureSize="512" />
      </MergeSprite>
    </cocosui>
    类符号: cocos2d::BinPackAlgorithm_Base / _Lines / _LinesForIcon / _LinesGeneric / _MaxRects
    描述符规范 (libclient.so @0x00ac0b07 render.create_atlas):
        INFO.x/y : (0,0) 在左上角, x 左→右, y 上→下   ← **左上原点**
        INFO.w/h : 必须等于子图真实尺寸

本模块复现「Lines」语义（有据部分 ✓）与推断参数（未定证 ⚠，见 README/报告）：
    ✓ 左上原点、y 向下
    ✓ 行内 x 递增；行放不下则换行；行高 = 该行最高子图
    ⚠ margin=2 / pad=2   —— 同引擎族打包器实测值（4639 个 .atlas：行内 gap=2 占 131614/134000+；行首 x0=2 占 25838）
    ⚠ 插入顺序 = 加载顺序（未被任何产物证实）
    ✓ TextureSize=512、PackingTextureLimit=4（来自引擎配置原文）

用法:
    from merge_sprite_lines import pack_lines, pack_report
    pages = pack_lines([("a",64,64),("b",120,48)], page=512, limit=4)
"""
from __future__ import annotations

MARGIN = 2   # ⚠ 推断
PAD = 2      # ⚠ 推断


def pack_lines(rects, page=512, margin=MARGIN, pad=PAD, limit=4, order='input'):
    """Lines 打包。rects=[(name,w,h)]。返回 pages=[ [ (name,x,y,w,h), ... ], ... ]；
    超过 limit 页则返回 None（对齐引擎 PackingTextureLimit 语义：超限不合并）。"""
    items = list(rects)
    if order == 'height_desc':
        items.sort(key=lambda t: -t[2])
    elif order == 'area_desc':
        items.sort(key=lambda t: -(t[1] * t[2]))
    pages = []
    cur = []
    x = y = margin
    row_h = 0
    for name, w, h in items:
        if w + 2 * margin > page or h + 2 * margin > page:
            raise ValueError('subtexture %s (%dx%d) larger than page %d (引擎会报 '
                             '"image is larger than texture size")' % (name, w, h, page))
        if x + w > page - margin:              # 换行
            x = margin
            y += row_h + pad
            row_h = 0
        if y + h > page - margin:              # 本页满 → 开新页
            pages.append(cur)
            if len(pages) >= limit:
                return None
            cur = []
            x = y = margin
            row_h = 0
        cur.append((name, x, y, w, h))
        x += w + pad
        row_h = max(row_h, h)
    if cur:
        pages.append(cur)
    if len(pages) > limit:
        return None
    return pages


def check_pages(pages, page=512):
    """不变量自检：越界 / 重叠。返回 (ok, errs)"""
    errs = []
    for pi, pg in enumerate(pages):
        occ = []
        for name, x, y, w, h in pg:
            if x < 0 or y < 0 or x + w > page or y + h > page:
                errs.append('page%d %s out of bounds' % (pi, name))
            occ.append((x, y, w, h, name))
        for i in range(len(occ)):
            for j in range(i + 1, len(occ)):
                a, b = occ[i], occ[j]
                if a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]:
                    errs.append('page%d overlap %s/%s' % (pi, a[4], b[4]))
    return (not errs), errs


def pack_report(rects, page=512, limit=4, order='input'):
    r = pack_lines(rects, page=page, limit=limit, order=order)
    if r is None:
        return dict(ok=False, reason='exceeds PackingTextureLimit=%d' % limit)
    ok, errs = check_pages(r, page)
    used = sum(1 for pg in r for _ in pg)
    return dict(ok=ok, pages=len(r), sprites=used, errs=errs[:5])


if __name__ == '__main__':
    import sys
    demo = [('icon_%02d' % i, 64, 64) for i in range(40)]
    print('40 个 64x64 →', pack_report(demo))
    print('Lines 每行上限 = (512-2-2+2)//(64+2) =', (512 - 2 - 2 + 2) // (64 + 2))
