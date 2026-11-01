# -*- coding: utf-8 -*-
"""Spine 2.1.27 绘制内核（头像 / 头像框 / 名片框 动图预渲染专用，重写版）。

相对旧版修掉的关键错误：

  A. 【最严重】mesh / skinnedmesh 附件整块丢失。
     旧版用 `page_of.get(att.get("name"))` 取贴图页，但 page_of 的键是**页名**
     （如 touxiang_ani_02.png），而 att.get("name") 是**附件名**（如 left_leg），
     永远取不到 → 整条肢体被 `continue` 掉。
     新版：每个 mesh 附件按同名 atlas region 裁出**该附件自己的位图** att_img，
     mesh 的 uv（0..1）直接映射到 att_img，彻底绕开页内 rotate/偏移换算。

  B. 内容被裁切 / 飞出画布。旧版画布按 skeleton 声明的 width/height 定，
     但头像框 / 名片框的装饰远大于这个框。新版：在超大全画布上以原点为中心渲染，
     最后对所有帧取**并集透明包围盒**做紧裁，不裁内容、居中、且动画不抖。

  C. IK 约束未解（13 个骨架，主要是角色手脚链）。新增 1/2 段 IK 求解，
     否则手脚停在 setup 姿势、不会随动画摆动。

  D. 附件切换时间线（Spine 2.x 逐帧动画做法）与 slot 颜色时间线（发光/淡入淡出）
     均按增量处理。

验证口径：touxiang_ani_02（蜜蜜甜粽）渲染后四肢齐全、与游戏内静态图姿态一致。
"""
from __future__ import annotations

import json
import math
import pathlib
import re

import numpy as np
from PIL import Image

from spine_render import mat_mul, mat_trs, parse_atlas, sample  # noqa: F401

IDENT = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]

_HEX = re.compile(r"^([0-9a-fA-F]{8}|[0-9a-fA-F]{6})$")


def parse_color(s):
    if not s:
        return None
    h = str(s).lstrip("#")
    if not _HEX.match(h):
        return None
    n = lambda i: int(h[i:i + 2], 16)  # noqa: E731
    if len(h) == 6:
        return (n(0), n(2), n(4), 255)
    return (n(0), n(2), n(4), n(6))


# ---------------------------------------------------------------- 骨骼
def bone_world(skel, anim, t):
    """骨骼世界矩阵（增量动画）。返回 {name: 2x3}。

    ★ inheritRotation / inheritScale：Spine 允许骨骼「不继承父级旋转/缩放」，
      此时世界旋转/缩放只取自身值，但**位置仍由父级矩阵变换**。
      450002 的头部骨骼 9 就是 inheritRotation:false —— 旧版一律继承父级，
      让头在父链上多转 ~99°，于是「头方向反了」。
    """
    bones = skel["bones"]
    anim_bones = (anim or {}).get("bones", {})
    world = {}
    rot_of = {}
    scl_of = {}
    for b in bones:
        name = b["name"]
        x, y = b.get("x", 0.0), b.get("y", 0.0)
        rot = b.get("rotation", 0.0)
        sx, sy = b.get("scaleX", 1.0), b.get("scaleY", 1.0)
        tl = anim_bones.get(name, {})
        if "translate" in tl:
            dx, dy = sample(tl["translate"], t, (("x", 0.0), ("y", 0.0)))
            x, y = x + dx, y + dy
        if "rotate" in tl:
            (dr,) = sample(tl["rotate"], t, (("angle", 0.0),))
            rot = rot + dr
        if "scale" in tl:
            mx, my = sample(tl["scale"], t, (("x", 1.0), ("y", 1.0)))
            sx, sy = sx * mx, sy * my
        parent = b.get("parent")
        pm = world.get(parent)
        if pm is None:
            rot_of[name], scl_of[name] = rot, (sx, sy)
            world[name] = mat_trs(x, y, rot, sx, sy)
            continue
        wr = rot + (rot_of[parent] if b.get("inheritRotation", True) else 0.0)
        ps = scl_of[parent] if b.get("inheritScale", True) else (1.0, 1.0)
        wsx, wsy = sx * ps[0], sy * ps[1]
        # 位置：本地 (x,y) 经父级矩阵变换（即使不继承旋转/缩放也照样跟随）
        wx = pm[0][0] * x + pm[0][1] * y + pm[0][2]
        wy = pm[1][0] * x + pm[1][1] * y + pm[1][2]
        r = math.radians(wr)
        c, s = math.cos(r), math.sin(r)
        world[name] = [[c * wsx, -s * wsy, wx], [s * wsx, c * wsy, wy]]
        rot_of[name], scl_of[name] = wr, (wsx, wsy)
    return world


# ---------------------------------------------------------------- IK 求解
def _world_to_local(bone, world):
    """从世界矩阵反解 (x,y,rotation_deg,scaleX,scaleY)。"""
    m = world[bone["name"]]
    c, s = m[0][0], m[1][0]
    sx = math.hypot(c, s)
    sy = math.hypot(m[0][1], m[1][1])
    rot = math.degrees(math.atan2(s, c))
    return m[0][2], m[1][2], rot, sx, sy


def _recompute_subtree(skel, world, bone_name):
    """以 bone_name 的新世界矩阵为根，级联重算其所有后代的世界矩阵。"""
    # 先确保 bone_name 自身已就位（调用方已写好），这里只重算后代
    by_name = {b["name"]: b for b in skel["bones"]}
    children = {}
    for b in skel["bones"]:
        p = b.get("parent")
        if p:
            children.setdefault(p, []).append(b["name"])
    stack = list(children.get(bone_name, []))
    while stack:
        nm = stack.pop()
        b = by_name[nm]
        # 用其“当前”局部 transform 重算世界 = 父世界 * TRS(局部)
        # 但局部 transform 一直没变，只是父的世界变了 → 直接 mat_mul 即可
        parent = b.get("parent")
        x, y = b.get("x", 0.0), b.get("y", 0.0)
        rot = b.get("rotation", 0.0)
        sx, sy = b.get("scaleX", 1.0), b.get("scaleY", 1.0)
        local = mat_trs(x, y, rot, sx, sy)
        world[nm] = mat_mul(world[parent], local)
        stack.extend(children.get(nm, []))


def apply_ik(skel, world, anim, t):
    """对 skel["ik"] 逐条求解，就地修正 world 矩阵。"""
    iks = skel.get("ik")
    if not iks:
        return
    by_name = {b["name"]: b for b in skel["bones"]}
    for ik in iks:
        bones = ik.get("bones", [])
        target = ik.get("target")
        if len(bones) < 1 or target not in world:
            continue
        bend = bool(ik.get("bendPositive", True))
        mix = float(ik.get("mix", 1.0))
        # 动画里 IK 自身的覆盖
        ik_tl = (anim or {}).get("ik", {}).get(ik.get("name"), {})
        if "bendPositive" in ik_tl:
            bend = bool(int(sample(ik_tl["bendPositive"], t, ((0, 1),))[0]))
        if "mix" in ik_tl:
            (mix,) = sample(ik_tl["mix"], t, ((0, mix),))
        if len(bones) == 1:
            _ik_one(world, by_name, bones[0], target, bend, mix)
        else:
            _ik_two(world, by_name, bones[0], bones[1], target, bend, mix)


def _bone_world_xy(w):
    return w[0][2], w[1][2]


def _ik_one(world, by_name, bone_name, target, bend_pos, mix):
    """单段 IK：让 bone 的末端指向 target（绕父旋转）。"""
    if bone_name not in world or target not in world:
        return
    b = by_name[bone_name]
    parent = b.get("parent")
    if parent not in world:
        return
    pw = world[parent]
    px, py = _bone_world_xy(pw)
    ax, ay = _bone_world_xy(world[bone_name])
    tx, ty = _bone_world_xy(world[target])
    # 当前角度与目标角度（相对父）
    cur = math.degrees(math.atan2(ay - py, ax - px))
    want = math.degrees(math.atan2(ty - py, tx - px))
    # 父世界旋转
    pr = math.degrees(math.atan2(pw[1][0], pw[0][0]))
    # bone 局部 rotation 应 = want - pr （spine 中 rotation 是相对父）
    new_local_rot = want - pr
    old_local_rot = b.get("rotation", 0.0)
    # 取当前世界旋转
    cur_world_rot = math.degrees(math.atan2(world[bone_name][1][0], world[bone_name][0][0]))
    # 目标世界旋转
    target_world_rot = pr + new_local_rot
    # 混合
    final_world_rot = cur_world_rot + (target_world_rot - cur_world_rot) * mix
    # 由 final_world_rot 反解局部 rotation
    new_local = final_world_rot - pr
    # 写回 world[bone_name]
    sx = world[bone_name][0][0]; _ = sx
    # 重新构造世界矩阵：保持位置/缩放，仅改旋转
    scale_x = math.hypot(world[bone_name][0][0], world[bone_name][1][0])
    scale_y = math.hypot(world[bone_name][0][1], world[bone_name][1][1])
    r = math.radians(final_world_rot)
    c, s = math.cos(r), math.sin(r)
    world[bone_name] = [[c * scale_x, -s * scale_y, ax], [s * scale_x, c * scale_y, ay]]
    _recompute_subtree(skel_dummy(by_name), world, bone_name)


def _ik_two(world, by_name, boneA_name, boneB_name, target, bend_pos, mix):
    """两段 IK（spine 经典算法，世界系）。"""
    if boneA_name not in world or boneB_name not in world or target not in world:
        return
    bA = by_name[boneA_name]
    parentA = bA.get("parent")
    if parentA not in world:
        return
    pw = world[parentA]
    px, py = _bone_world_xy(pw)
    ax, ay = _bone_world_xy(world[boneA_name])
    bx, by = _bone_world_xy(world[boneB_name])
    tx, ty = _bone_world_xy(world[target])

    # 计算两段骨长（用当前世界距离近似）
    L1 = math.hypot(ax - px, ay - py)
    L2 = math.hypot(bx - ax, by - ay)
    # target 相对 parent 的距离
    dx, dy = tx - px, ty - py
    D = math.hypot(dx, dy)
    if L1 < 1e-6 or L2 < 1e-6:
        return
    D = min(D, L1 + L2 - 1e-4)
    # 余弦定理求 parent->A->B 夹角
    a = math.atan2(dy, dx)
    # A 处内角
    cosA = (L1 * L1 + D * D - L2 * L2) / (2 * L1 * D)
    cosA = max(-1.0, min(1.0, cosA))
    Aang = math.acos(cosA)
    # B 处内角
    cosB = (L1 * L1 + L2 * L2 - D * D) / (2 * L1 * L2)
    cosB = max(-1.0, min(1.0, cosB))
    Bang = math.acos(cosB)
    # 弯曲方向
    bend_sign = 1.0 if bend_pos else -1.0
    # A 骨骼世界旋转（指向 target 方向 ± Aang）
    aA_world = math.degrees(a + bend_sign * Aang)
    # B 骨骼世界旋转：相对 A 转 -(180 - Bang)（同侧弯曲）
    aB_world = aA_world + bend_sign * (180.0 - math.degrees(Bang))
    # 父世界旋转
    pr = math.degrees(math.atan2(pw[1][0], pw[0][0]))
    # 写回 A 世界矩阵（保留位置、缩放）
    def set_world(name, world_rot_deg, wx, wy):
        w = world[name]
        sx = math.hypot(w[0][0], w[1][0])
        sy = math.hypot(w[0][1], w[1][1])
        r = math.radians(world_rot_deg)
        c, s = math.cos(r), math.sin(r)
        world[name] = [[c * sx, -s * sy, wx], [s * sx, c * sy, wy]]
    # 混合（spine mix）
    curA = math.degrees(math.atan2(world[boneA_name][1][0], world[boneA_name][0][0]))
    curB = math.degrees(math.atan2(world[boneB_name][1][0], world[boneB_name][0][0]))
    finA = curA + (aA_world - curA) * mix
    finB = curB + (aB_world - curB) * mix
    set_world(boneA_name, finA, ax, ay)
    # 重算 B 世界位置（基于新 A）+ 写 B 旋转
    # B 的世界 = 新 A 世界 * B 局部(未变)  → 但我们要直接设 B 位置为 A + L2*(finB 方向)
    # 用新 A 位置 + 方向求 B 端点
    bx2 = ax + L2 * math.cos(math.radians(finB))
    by2 = ay + L2 * math.sin(math.radians(finB))
    set_world(boneB_name, finB, bx2, by2)
    # 级联重算 A、B 的后代
    _recompute_subtree(skel_dummy(by_name), world, boneA_name)
    _recompute_subtree(skel_dummy(by_name), world, boneB_name)


def skel_dummy(by_name):
    """给 _recompute_subtree 用的极简骨架（只需 bones 列表含 parent）。"""
    return {"bones": [{"name": n, "parent": b.get("parent"),
                       "x": b.get("x", 0.0), "y": b.get("y", 0.0),
                       "rotation": b.get("rotation", 0.0),
                       "scaleX": b.get("scaleX", 1.0), "scaleY": b.get("scaleY", 1.0)}
                      for n, b in by_name.items()]}


# ---------------------------------------------------------------- 时间线取值
def _key_at(tl, t):
    pick = None
    for k in tl:
        if float(k.get("time", 0)) <= t + 1e-6:
            pick = k
        else:
            break
    return pick or tl[0]


def slot_attachment(skel, slot, anim_slots, t):
    tl = (anim_slots or {}).get(slot["name"], {}).get("attachment")
    if not tl:
        return slot.get("attachment")
    k = _key_at(tl, t)
    return k.get("name") if k else None


def slot_color(skel, slot, anim_slots, t):
    tl = (anim_slots or {}).get(slot["name"], {}).get("color")
    if not tl:
        return parse_color(slot.get("color"))
    k = _key_at(tl, t)
    return parse_color(k.get("color")) if k else None


def anim_duration(skel, aname):
    anim = (skel.get("animations") or {}).get(aname) or {}
    dur = 0.0
    for group in anim.values():
        if not isinstance(group, dict):
            continue
        for who in group.values():
            if not isinstance(who, dict):
                continue
            for tl in who.values():
                if isinstance(tl, list):
                    for k in tl:
                        if isinstance(k, dict):
                            dur = max(dur, float(k.get("time", 0)))
    return dur


def anim_name(skel):
    anims = skel.get("animations") or {}
    if not anims:
        return None
    for pref in ("loop", "idle", "stand", "animation"):
        for k in anims:
            if k.lower() == pref:
                return k
    for k in anims:
        if any(w in k.lower() for w in ("loop", "idle", "stand")):
            return k
    return next(iter(anims))


def draw_order(skel, anim, t):
    """返回该时刻的 slot 绘制顺序（列表 of slot name）。无 drawOrder 时间线则返回 setup 顺序。"""
    setup = [s["name"] for s in skel.get("slots", [])]
    tl = (anim or {}).get("drawOrder")
    if not tl:
        return setup
    k = _key_at(tl, t)
    offs = k.get("offsets") if k else None
    if not offs:
        return setup
    # offsets: [{slot, offset}]，offset 是相对 setup 的偏移
    order = list(setup)
    for o in offs:
        sn = o.get("slot")
        if sn in order:
            order.remove(sn)
            idx = o.get("offset", 0)
            order.insert(max(0, min(len(order), idx)), sn)
    return order


# ---------------------------------------------------------------- 绘制
def tint(im, col):
    """对**小图**（region sprite）着色。不再对整张画布做转换 —— 那是性能灾难。"""
    if not col:
        return im
    r, g, b, a = col
    if r >= 255 and g >= 255 and b >= 255 and a >= 255:
        return im
    arr = np.asarray(im.convert("RGBA"), dtype=np.float32)
    if (r, g, b) != (255, 255, 255):
        arr[..., 0] *= r / 255.0
        arr[..., 1] *= g / 255.0
        arr[..., 2] *= b / 255.0
    if a < 255:
        arr[..., 3] *= a / 255.0
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")


def _crop_region(page_img, region):
    """从页图裁出 region 位图（处理 rotate）。"""
    rx, ry, rw, rh = region["x"], region["y"], region["w"], region["h"]
    if region.get("rotate"):
        crop = page_img.crop((rx, ry, rx + rh, ry + rw))
        crop = crop.transpose(Image.ROTATE_270)
    else:
        crop = page_img.crop((rx, ry, rx + rw, ry + rh))
    return crop


_REGION_CACHE = {}


def _region_cache(page_img, region):
    """region 裁切缓存。key=(page 图 id, x, y, w, h, rotate)。"""
    key = (id(page_img), region["x"], region["y"], region["w"], region["h"],
           bool(region.get("rotate")))
    hit = _REGION_CACHE.get(key)
    if hit is not None:
        return hit
    rx, ry, rw, rh = region["x"], region["y"], region["w"], region["h"]
    if region.get("rotate"):
        crop = page_img.crop((rx, ry, rx + rh, ry + rw)).transpose(Image.ROTATE_270)
    else:
        crop = page_img.crop((rx, ry, rx + rw, ry + rh))
    _REGION_CACHE[key] = crop
    return crop


def _composite_clipped(canvas, sprite, x, y):
    """把 sprite 贴到 canvas；越界部分裁剪（PIL 的 alpha_composite 不允许负坐标）。"""
    bx0, by0 = max(0, x), max(0, y)
    bx1 = min(canvas.width, x + sprite.width)
    by1 = min(canvas.height, y + sprite.height)
    if bx1 <= bx0 or by1 <= by0:
        return False
    piece = sprite.crop((bx0 - x, by0 - y, bx1 - x, by1 - y))
    canvas.alpha_composite(piece, (bx0, by0))
    return True


def draw_region(canvas, page_img, region, att, world_mat, scale, off):
    """region 附件：按骨骼世界矩阵贴图。

    ★ 性能：贴图页的 region 裁切结果做**全局缓存**（同一页同 region 尺寸不变），
      否则 500+ slot 的骨架每帧要重复 crop 上千次。
    """
    w = float(att.get("width", region.get("w", 0)))
    h = float(att.get("height", region.get("h", 0)))
    if w <= 0 or h <= 0:
        return False
    local = mat_trs(float(att.get("x", 0)), float(att.get("y", 0)),
                    float(att.get("rotation", 0)), 1.0, 1.0)
    m = mat_mul(world_mat, local)
    rx, ry, rw, rh = region["x"], region["y"], region["w"], region["h"]
    crop = _region_cache(page_img, region)
    if crop is None:
        return False
    # 目标尺寸：附件尺寸 × 全局缩放（骨骼缩放已含在 world_mat 的行列式里）
    sx = math.hypot(m[0][0], m[1][0])
    sy = math.hypot(m[0][1], m[1][1])
    dw = max(1, int(round(w * scale * sx)))
    dh = max(1, int(round(h * scale * sy)))
    # ★ 骨架里 scale=0 的插槽（粒子从 0 放大）缩放后只剩 1px，
    #   会变成画布上的杂点并撑大包围盒 —— 直接不画。
    if dw < 2 or dh < 2:
        return False
    sprite = crop.resize((dw, dh), Image.BILINEAR)
    ang = math.degrees(math.atan2(m[1][0], m[0][0]))
    if abs(ang) > 1e-3:
        sprite = sprite.rotate(ang, expand=True, resample=Image.BILINEAR)
    px = m[0][2] * scale + off[0]
    py = -m[1][2] * scale + off[1]
    return _composite_clipped(canvas, sprite,
                              int(round(px - sprite.width / 2)),
                              int(round(py - sprite.height / 2)))


def _sample_vertices(att, bones_mat, slotmat, scale, off):
    verts = att.get("vertices") or []
    if att.get("type") == "skinnedmesh":
        pts = []
        i = 0
        while i < len(verts):
            n = int(verts[i]); i += 1
            sx = sy = 0.0
            for _ in range(n):
                bidx = int(verts[i]); vx = float(verts[i + 1]); vy = float(verts[i + 2]); wgt = float(verts[i + 3])
                i += 4
                if bidx < len(bones_mat):
                    m = bones_mat[bidx]
                    sx += (m[0][0] * vx + m[0][1] * vy + m[0][2]) * wgt
                    sy += (m[1][0] * vx + m[1][1] * vy + m[1][2]) * wgt
            pts.append((sx * scale + off[0], -sy * scale + off[1]))
        return pts
    m = slotmat
    pts = []
    for i in range(0, len(verts), 2):
        vx, vy = float(verts[i]), float(verts[i + 1])
        wx = m[0][0] * vx + m[0][1] * vy + m[0][2]
        wy = m[1][0] * vx + m[1][1] * vy + m[1][2]
        pts.append((wx * scale + off[0], -wy * scale + off[1]))
    return pts


def draw_mesh(canvas, att_img, att, bones_mat, slotmat, scale, off, col=None):
    """mesh / skinnedmesh：uv 直接映射到 att_img（已裁好的该附件位图）。

    ★ 性能：先算出所有三角形的整体像素包围盒，**只在该范围内**做 numpy 运算，
      避免每帧为每个 mesh 拷贝整张 1400×1400 画布。
    ★ col：slot 颜色。region 路径会用 tint 上色，mesh 路径原来**漏了** ——
      于是 setup 里 alpha=0 的隐藏 slot（Spine 常用「淡入」做显隐）也会被画出来。
    """
    tris = att.get("triangles") or []
    uvs = att.get("uvs") or []
    if not tris or not uvs:
        return False
    pts = _sample_vertices(att, bones_mat, slotmat, scale, off)
    W, H = canvas.width, canvas.height
    # 1) 整体像素包围盒
    xs_all = [p[0] for p in pts]
    ys_all = [p[1] for p in pts]
    if not xs_all:
        return False
    minx = int(max(0, math.floor(min(xs_all))))
    maxx = int(min(W - 1, math.ceil(max(xs_all))))
    miny = int(max(0, math.floor(min(ys_all))))
    maxy = int(min(H - 1, math.ceil(max(ys_all))))
    if maxx <= minx or maxy <= miny:
        return False
    # 2) 只取该区域
    bw, bh = maxx - minx + 1, maxy - miny + 1
    base = np.asarray(canvas, dtype=np.float32)[miny:maxy + 1, minx:maxx + 1]
    out = base.copy()
    tex = np.asarray(att_img.convert("RGBA"), dtype=np.float32)
    th, tw = tex.shape[:2]
    # slot 颜色：RGB 相乘、alpha 相乘
    cr = cg = cb = 1.0
    ca = 1.0
    if col:
        cr, cg, cb, ca = (col[0] / 255.0, col[1] / 255.0, col[2] / 255.0,
                          col[3] / 255.0)
        if ca <= 0.002:
            return False          # 完全透明 → 不画
    drew = False
    for t in range(0, len(tris) - 2, 3):
        i0, i1, i2 = int(tris[t]), int(tris[t + 1]), int(tris[t + 2])
        if max(i0, i1, i2) >= len(pts) or 2 * max(i0, i1, i2) + 1 >= len(uvs):
            continue
        x0, y0 = pts[i0]; x1, y1 = pts[i1]; x2, y2 = pts[i2]
        u0, v0 = uvs[2 * i0], uvs[2 * i0 + 1]
        u1, v1 = uvs[2 * i1], uvs[2 * i1 + 1]
        u2, v2 = uvs[2 * i2], uvs[2 * i2 + 1]
        # 三角形自身的像素包围盒（相对 out 的偏移）
        lx0 = int(max(0, math.floor(min(x0, x1, x2)) - minx))
        lx1 = int(min(bw - 1, math.ceil(max(x0, x1, x2)) - minx))
        ly0 = int(max(0, math.floor(min(y0, y1, y2)) - miny))
        ly1 = int(min(bh - 1, math.ceil(max(y0, y1, y2)) - miny))
        if lx1 <= lx0 or ly1 <= ly0:
            continue
        den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(den) < 1e-9:
            continue
        ys, xs = np.mgrid[ly0:ly1 + 1, lx0:lx1 + 1]
        # ★ 关键：xs/ys 是**相对 out 的局部坐标**（从 0 起），而 x0/y0…是**画布绝对坐标**。
        #   重心坐标必须在同一坐标系里算，否则 inside 恒为 False → 主体整块不绘制。
        px = xs + minx + 0.5
        py = ys + miny + 0.5
        w0 = ((y1 - y2) * (px - x2) + (x2 - x1) * (py - y2)) / den
        w1 = ((y2 - y0) * (px - x2) + (x0 - x2) * (py - y2)) / den
        w2 = 1.0 - w0 - w1
        inside = (w0 >= -0.002) & (w1 >= -0.002) & (w2 >= -0.002)
        if not inside.any():
            continue
        u = (w0 * u0 + w1 * u1 + w2 * u2) * (tw - 1)
        v = (w0 * v0 + w1 * v1 + w2 * v2) * (th - 1)
        ui = np.clip(u.astype(np.int32), 0, tw - 1)
        vi = np.clip(v.astype(np.int32), 0, th - 1)
        src = tex[vi, ui]
        a = (src[..., 3:4] / 255.0) * inside[..., None] * ca
        rgb = src[..., :3] * np.array([cr, cg, cb], dtype=np.float32)
        sub = out[ly0:ly1 + 1, lx0:lx1 + 1]
        sub[..., :3] = rgb * a + sub[..., :3] * (1 - a)
        sub[..., 3:4] = (a * 255 + sub[..., 3:4] * (1 - a))
        out[ly0:ly1 + 1, lx0:lx1 + 1] = sub
        drew = True
    if drew:
        full = np.asarray(canvas, dtype=np.float32)
        full[miny:maxy + 1, minx:maxx + 1] = out
        canvas.paste(Image.fromarray(np.clip(full, 0, 255).astype(np.uint8), "RGBA"))
    return drew


def render_frame(skel, regions, page_imgs, anim, anim_slots, t, scale, off,
                 canvas_wh, att_cache, bone_order=None, slot_map=None):
    """渲染一帧 RGBA。canvas_wh=(w,h)，所有内容以 off 为原点（spine 原点）居中。"""
    canvas = Image.new("RGBA", canvas_wh, (0, 0, 0, 0))
    world = bone_world(skel, anim, t)
    apply_ik(skel, world, anim, t)
    bones_mat = [world.get(b["name"], IDENT) for b in skel["bones"]]
    skin = skel.get("skins", {})
    if isinstance(skin, list):
        default = {}
        for s in skin:
            if isinstance(s, dict) and s.get("name") == "default":
                default = s.get("attachments", {})
    else:
        default = skin.get("default", {}) or {}
    atts = {}
    for slot in skel.get("slots", []):
        for n, a in (default.get(slot["name"]) or {}).items():
            atts.setdefault(n, a)
    # 绘制顺序
    order = bone_order or [s["name"] for s in skel.get("slots", [])]
    smap = slot_map if slot_map is not None else {s["name"]: s for s in skel.get("slots", [])}
    for sname in order:
        slot = smap.get(sname)
        if slot is None:
            continue
        name = slot_attachment(skel, slot, anim_slots, t)
        if not name:
            continue
        att = (default.get(slot["name"]) or {}).get(name) or atts.get(name)
        if not att:
            continue
        col = slot_color(skel, slot, anim_slots, t)
        bm = world.get(slot["bone"], IDENT)
        atype = att.get("type") or ("mesh" if (att.get("uvs") and att.get("triangles")) else "region")
        if atype in ("mesh", "skinnedmesh"):
            key = att.get("name") or name
            att_img = att_cache.get(key)
            if att_img is None:
                reg = regions.get(key)
                if not reg:
                    continue
                pg = reg.get("page")
                page_img = page_imgs.get(pg)
                if page_img is None:
                    continue
                att_img = _region_cache(page_img, reg)
                att_cache[key] = att_img
            draw_mesh(canvas, att_img, att, bones_mat, bm, scale, off, col)
            continue
        if atype != "region":
            continue
        reg = regions.get(att.get("name") or name)
        if not reg:
            continue
        page_img = page_imgs.get(reg.get("page"))
        if page_img is None:
            continue
        if col is not None:
            # ★ 只对 region 小图着色，再贴到画布（旧版对整张 1400×1400 画布做
            #   float32 转换，每个 slot 一次 → 551 slot 的骨架单帧要十几秒）
            # ★ off 必须传进去：曾漏传导致着色插槽贴在 (0,0) 左上角，
            #   这些杂点会把包围盒撑大，主体被缩成一小块。
            sprite = _region_sprite(page_img, reg, att, bm, scale, off)
            if sprite is None:
                continue
            canvas.alpha_composite(tint(sprite[0], col), sprite[1])
        else:
            draw_region(canvas, page_img, reg, att, bm, scale, off)
    return canvas


def _region_sprite(page_img, region, att, world_mat, scale, off=(0, 0)):
    """region 附件 → (RGBA sprite, 贴图左上角坐标)。

    off 必须是画布原点（画布中心）。漏传会把着色插槽贴到 (0,0)。
    """
    w = float(att.get("width", region.get("w", 0)))
    h = float(att.get("height", region.get("h", 0)))
    if w <= 0 or h <= 0:
        return None
    local = mat_trs(float(att.get("x", 0)), float(att.get("y", 0)),
                    float(att.get("rotation", 0)), 1.0, 1.0)
    m = mat_mul(world_mat, local)
    crop = _region_cache(page_img, region)
    if crop is None:
        return None
    sx = math.hypot(m[0][0], m[1][0])
    sy = math.hypot(m[0][1], m[1][1])
    dw = max(1, int(round(w * scale * sx)))
    dh = max(1, int(round(h * scale * sy)))
    if dw < 2 or dh < 2:
        return None
    sprite = crop.resize((dw, dh), Image.BILINEAR)
    ang = math.degrees(math.atan2(m[1][0], m[0][0]))
    if abs(ang) > 1e-3:
        sprite = sprite.rotate(ang, expand=True, resample=Image.BILINEAR)
    px = m[0][2] * scale + off[0]
    py = -m[1][2] * scale + off[1]
    pos = (int(round(px - sprite.width / 2)), int(round(py - sprite.height / 2)))
    return (sprite, pos)


def parse_atlas_fixed(atlas: pathlib.Path):
    """正确的 Spine atlas 解析（覆盖旧模块的 buggy 版本）。

    ★ 旧实现的 bug：atlas 里页属性行（size:/format:/filter:/repeat:）是**不缩进**的，
      与 region 名同层级。旧解析器把它们当成 region 名，于是 regions 里混进
      "size: 256,128" 这类条目，页归属判定也随之错乱。

    正确规则：
      · 页名行 = 不缩进、非 key:value 形式（如 `touxiang_ani_39.png`）
      · 页属性行 = 不缩进、key:value 形式（size/format/filter/repeat）→ 只影响当前页
      · region 名 = 不缩进、非 key:value，且其后紧跟缩进属性行
      · region 属性行 = 缩进（xy/size/orig/offset/rotate/index）
    """
    txt = atlas.read_text(encoding="utf-8", errors="ignore")
    pages = []
    regions = {}
    cur_page = None
    pending = None          # 等待缩进属性确认的 region 名
    cur = None              # 正在收集属性的 region
    for raw in txt.splitlines():
        if not raw.strip():
            continue
        indented = raw.startswith((" ", "\t"))
        s = raw.strip()
        if not indented:
            # 页名行
            if s.lower().endswith((".png", ".jpg")):
                cur_page = s
                if s not in pages:
                    pages.append(s)
                pending = None
                cur = None
                continue
            # 页属性行：只改当前页的元信息，不生成 region
            if ":" in s:
                pending = None
                cur = None
                continue
            # 候选 region 名
            pending = {"name": s, "page": cur_page}
            cur = None
            continue
        # 缩进行：属性
        if pending is not None and cur is None:
            cur = pending
            regions.setdefault(pending["name"], cur)
        if cur is None:
            continue
        if s.startswith("xy:"):
            p = s[3:].split(",")
            cur["x"], cur["y"] = int(p[0]), int(p[1])
        elif s.startswith("size:"):
            p = s[5:].split(",")
            cur["w"], cur["h"] = int(p[0]), int(p[1])
        elif s.startswith("orig:"):
            p = s[5:].split(",")
            cur["ow"], cur["oh"] = int(p[0]), int(p[1])
        elif s.startswith("offset:"):
            p = s[7:].split(",")
            cur["ox"], cur["oy"] = int(p[0]), int(p[1])
        elif s.startswith("rotate:"):
            cur["rotate"] = s.split(":", 1)[1].strip().lower() == "true"
        elif s.startswith("index:"):
            cur["index"] = s.split(":", 1)[1].strip()
    # 只保留尺寸完整的 region
    regions = {k: v for k, v in regions.items()
               if v.get("w") is not None and v.get("h") is not None}
    return pages, regions


def load_atlas(atlas: pathlib.Path):
    skel = json.loads(atlas.with_suffix(".json").read_text(encoding="utf-8"))
    pages, regions = parse_atlas_fixed(atlas)
    return skel, pages, regions



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

def _render_all(skel, regions, page_imgs, anim, anim_slots, dur, cnt, scale, off,
                canvas_wh, order_tl, slot_map, static_order):
    """按给定 scale 渲染 cnt 帧。"""
    att_cache = {}
    frs = []
    for i in range(cnt):
        t = dur * i / cnt
        order = draw_order(skel, anim, t) if order_tl else static_order
        frs.append(render_frame(skel, regions, page_imgs, anim, anim_slots, t,
                                scale, off, canvas_wh, att_cache, order, slot_map))
    return frs


def _coverage_bbox(frs, canvas):
    """按「覆盖率」求包围盒（排除只在少数帧出现的飞散粒子/特效）。

    返回 (minx, miny, maxx, maxy)；无内容时返回整张画布。
    """
    acc = None
    for f in frs:
        a = (np.asarray(f)[:, :, 3] > 4)
        acc = a.astype(np.int16) if acc is None else (acc + a)
    if acc is None:
        return 0, 0, canvas - 1, canvas - 1
    thr = max(1, int(round(len(frs) * 0.25)))
    ys, xs = np.nonzero(acc >= thr)
    if xs.size == 0:
        ys, xs = np.nonzero(acc >= 1)
    if xs.size == 0:
        return 0, 0, canvas - 1, canvas - 1
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def _persistent_bbox(frs, canvas, ratio=0.85):
    """「持久核心」包围盒：只统计在 ≥ratio 帧里都出现的像素。

    飞过画面的云/粒子只在某几帧覆盖同一位置，会被排除；主体（背景+角色）
    每帧都在，因此保留。用于识别「越界溢出的动态特效」并把取景收回到主体。
    """
    acc = None
    for f in frs:
        a = (np.asarray(f)[:, :, 3] > 4)
        acc = a.astype(np.int16) if acc is None else (acc + a)
    if acc is None:
        return None
    thr = max(1, int(math.ceil(len(frs) * ratio)))
    ys, xs = np.nonzero(acc >= thr)
    if xs.size == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def _pick_rect(frs, canvas, crop):
    """取景矩形。

    coverage：按逐帧覆盖率包围盒紧裁；但若**持久核心**明显更小（长边/面积差
      1.6/1.8 倍以上），说明有特效横向飞出画面（450006 的云把画面拉成 3.2:1
      长条，主体场景只剩一小块），此时改按持久核心取景、裁掉溢出特效。
    """
    minx, miny, maxx, maxy = _coverage_bbox(frs, canvas)
    if crop == "coverage":
        core = _persistent_bbox(frs, canvas)
        if core:
            w_cov, h_cov = maxx - minx + 1, maxy - miny + 1
            w_cor, h_cor = core[2] - core[0] + 1, core[3] - core[1] + 1
            if ((w_cov / w_cor >= 1.6 or h_cov / h_cor >= 1.6)
                    and (w_cov * h_cov) / float(w_cor * h_cor) >= 1.8):
                pad = int(round(max(w_cor, h_cor) * 0.06))
                return (core[0] - pad, core[1] - pad, core[2] + pad, core[3] + pad)
    return (minx, miny, maxx, maxy)


def render_frames(atlas: pathlib.Path, page_imgs: dict, box=220, cnt=24, aname=None,
                  internal=420, canvas=1400, crop="coverage"):
    """→ (frames[RGBA], meta)。

    box：最终输出最长边（px）。internal：主体在内部画布上应占的最长边。
    canvas：内部全画布边长（要足够大以容纳超出 skeleton 声明边界的装饰）。
    crop：
      · "coverage"（默认，头像/头像框）：按逐帧覆盖率包围盒紧裁 ——
        主体刚好占满，不受飞散粒子影响；若有特效横向飞出（持久核心远小于
        覆盖率包围盒），自动收回到持久核心，避免画面被拉成长条。
      · "artboard"（名片框）：按 skeleton 声明的 width/height 裁剪 ——
        名片框的火焰特效会横向溢出画板，用覆盖率会把画面裁成一条长条，
        按画板裁则与游戏内显示区域一致（溢出部分裁掉）。

    ★ 两遍渲染（2026-11-01）：不同骨架声明的 width/height 与实际内容尺寸
      差异极大（3.8 素材常见声明 520×1025 而主体只有 ~110 单位），
      一层 scale 会让部分条目渲成 40px 的小图。第一遍渲染后量**实测覆盖率
      包围盒**，若明显小于 internal 则按实测值重算 scale 再渲一遍。
    """
    skel, pages, regions = load_atlas(atlas)
    aname = aname or anim_name(skel)
    if not aname:
        return [], {}
    dur = anim_duration(skel, aname) or 1.0
    sk = skel.get("skeleton") or {}
    W = max(float(sk.get("width") or 128), 1.0)
    H = max(float(sk.get("height") or 128), 1.0)
    anim = (skel.get("animations") or {}).get(aname) or {}
    # ★ 骨架声明的 width/height 不含根部缩放（Spine 3.8 的 GUI 素材常见
    #   root scale=0.14 这类写法）。只按 W/H 定 scale 会让主体只占几十像素，
    #   之后再放大 → 又糊又小。这里把根部缩放并进去，让主体稳定占满 internal。
    try:
        root_w = bone_world(skel, anim, 0.0)[skel["bones"][0]["name"]]
        root_scale = math.hypot(root_w[0][0], root_w[1][0])
    except Exception:                                   # noqa: BLE001
        root_scale = 1.0
    root_scale = min(max(root_scale, 0.02), 4.0)
    scale = internal / (max(W, H) * root_scale)
    scale = min(max(scale, 0.02), 16.0)
    canvas_wh = (canvas, canvas)
    off = (canvas / 2, canvas / 2)
    anim_slots = anim.get("slots") or {}
    order_tl = anim.get("drawOrder")
    slot_map = {s["name"]: s for s in skel.get("slots", [])}
    # 静态绘制顺序（无 drawOrder 时间线时复用，避免每帧重建）
    static_order = [s["name"] for s in skel.get("slots", [])]

    frs = _render_all(skel, regions, page_imgs, anim, anim_slots, dur, cnt, scale,
                      off, canvas_wh, order_tl, slot_map, static_order)
    minx, miny, maxx, maxy = _pick_rect(frs, canvas, crop)
    long = max(maxx - minx + 1, maxy - miny + 1)
    # 主体远小于内部画布 → 按实测包围盒放大 scale 再渲一遍（最多一次）
    if long > 0 and long < internal * 0.9:
        factor = min(internal / float(long), 20.0)
        scale = min(scale * factor, 16.0)
        frs = _render_all(skel, regions, page_imgs, anim, anim_slots, dur, cnt, scale,
                          off, canvas_wh, order_tl, slot_map, static_order)
        minx, miny, maxx, maxy = _pick_rect(frs, canvas, crop)
    # ★ 不再用 _bg_rect 猜背景框：它会把面积大的方形装饰（烟花/粒子）
    #   当成背景框，裁出的画面里主体只剩一小点 —— 这正是「乱七八糟」的来源。
    if crop == "artboard":
        # 名片框：按 skeleton 声明的画板裁（火焰特效横向溢出画板属正常，
        # 用覆盖率包围盒会把画面裁成 2.5:1 的长条）
        half_w = W * scale / 2.0
        half_h = H * scale / 2.0
        minx = int(max(0, math.floor(off[0] - half_w)))
        maxx = int(min(canvas - 1, math.ceil(off[0] + half_w)))
        miny = int(max(0, math.floor(off[1] - half_h)))
        maxy = int(min(canvas - 1, math.ceil(off[1] + half_h)))
    # 留 4px 边
    minx = max(0, minx - 4); miny = max(0, miny - 4)
    maxx = min(canvas - 1, maxx + 4); maxy = min(canvas - 1, maxy + 4)
    cw, ch = maxx - minx + 1, maxy - miny + 1
    frs = [f.crop((minx, miny, maxx + 1, maxy + 1)) for f in frs]

    # 等比缩到 box（保持宽高比）
    long = max(cw, ch)
    if long > box:
        r = box / long
        nw, nh = max(1, int(round(cw * r))), max(1, int(round(ch * r)))
        frs = [f.resize((nw, nh), Image.LANCZOS) for f in frs]

    meta = {"anim": aname, "duration": dur, "frames": len(frs),
            "canvas": (cw, ch), "spine": sk.get("spine"), "ik": bool(skel.get("ik"))}
    return frs, meta
