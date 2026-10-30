# -*- coding: utf-8 -*-
"""裁剪改为「背景框优先」：有背景槽（bg）的骨架，按背景矩形出图，与游戏内头像框一致。

实测依据（da_450002 可乐大亨）：
  按内容 bbox 裁 → 角色与金币分处两角、主体缩成小块；
  按背景槽矩形裁 → 角色撑满蓝框，与官方静态立绘比例一致（游戏内就是被头像框裁掉的）。
"""
from __future__ import annotations

import pathlib

P = pathlib.Path("E:/la拆包项目/02_wiki/web/tools/spine_render_fix.py")

HELPER = '''

def _bg_rect(skel, regions, world, scale, off, canvas):
    """找背景槽（bone 名 bg / 附件 region 面积最大且接近正方），返回其画布矩形或 None。"""
    best = None
    best_area = 0.0
    for slot in skel.get("slots", []):
        att = slot.get("attachment")
        if not att:
            continue
        reg = regions.get(att) or regions.get(slot.get("name"))
        if not reg:
            continue
        w, h = float(reg.get("w") or 0), float(reg.get("h") or 0)
        if w <= 0 or h <= 0:
            continue
        area = w * h
        is_bg = str(slot.get("bone")) == "bg" or str(slot.get("name")) == "23"
        if not is_bg and not (0.8 <= w / h <= 1.25 and area >= 6000):
            continue
        m = world.get(slot.get("bone"))
        if not m:
            continue
        sx = math.hypot(m[0][0], m[1][0]) or 1.0
        sy = math.hypot(m[0][1], m[1][1]) or 1.0
        pw, ph = w * scale * sx, h * scale * sy
        cx = m[0][2] * scale + off[0]
        cy = -m[1][2] * scale + off[1]
        if pw * ph > best_area:
            best_area = pw * ph
            best = (int(cx - pw / 2), int(cy - ph / 2), int(cx + pw / 2), int(cy + ph / 2))
    if not best:
        return None
    x0, y0, x1, y1 = best
    if x1 - x0 < 32 or y1 - y0 < 32:
        return None
    return (max(0, x0), max(0, y0), min(canvas - 1, x1), min(canvas - 1, y1))
'''


def main() -> int:
    s = P.read_text(encoding="utf-8")
    if "_bg_rect" in s:
        print("已存在，跳过")
        return 0
    anchor = "\ndef render_frames("
    s = s.replace(anchor, HELPER + anchor, 1)

    # 在裁剪计算之后、留边之前插入「背景框优先」
    old = "    # 留 4px 边"
    new = """    # ★ 背景框优先：有 bg 槽的骨架，游戏里是被头像框裁切显示的，
    #   按内容 bbox 裁会把框外的装饰（金币/光效）算进画幅 → 主体缩成小块。
    try:
        w0 = bone_world(skel, anim, 0.0)
        brect = _bg_rect(skel, regions, w0, scale, off, canvas)
        if brect and (brect[2] - brect[0]) * (brect[3] - brect[1]) >= 0.6 * (maxx - minx) * (maxy - miny):
            minx, miny, maxx, maxy = brect
    except Exception:                                   # noqa: BLE001
        pass
    # 留 4px 边"""
    if old not in s:
        raise SystemExit("裁剪锚点未命中")
    s = s.replace(old, new, 1)
    P.write_text(s, encoding="utf-8")
    print("已加：背景框优先裁剪")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
