# -*- coding: utf-8 -*-
"""Spine 2.1 精简渲染器（region 附件）→ GIF。

支持：bones 层级、translate/rotate/scale 关键帧（线性插值）、slot 顺序、region 附件、
atlas 旋转区域。mesh / skinnedmesh 跳过（会在报告里给出跳过数量）。

用法：
  python spine_render.py <atlas路径> <输出.gif> [尺寸=256] [fps=15] [圈数=2]
"""
from __future__ import annotations

import json
import math
import pathlib
import re
import sys

from PIL import Image

# ---------------- atlas ----------------
xy_rx = re.compile(r"^\s*xy:\s*(-?\d+)\s*,\s*(-?\d+)")
sz_rx = re.compile(r"^\s*size:\s*(\d+)\s*,\s*(\d+)")
orig_rx = re.compile(r"^\s*orig:\s*(\d+)\s*,\s*(\d+)")
off_rx = re.compile(r"^\s*offset:\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)")
rot_rx = re.compile(r"^\s*rotate:\s*(\w+)")


def parse_atlas(path: pathlib.Path):
    pages, regions = [], {}
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    cur_page = None
    cur = None
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if line[:1] not in (" ", "\t") and s.lower().endswith((".png", ".jpg", ".webp")):
            cur_page = s
            pages.append(s)
            cur = None
            continue
        if line[:1] not in (" ", "\t"):
            cur = {"name": s, "page": cur_page}
            regions[s] = cur
            continue
        if cur is None:
            continue
        m = xy_rx.match(line)
        if m:
            cur["x"], cur["y"] = int(m.group(1)), int(m.group(2))
            continue
        m = sz_rx.match(line)
        if m:
            cur["w"], cur["h"] = int(m.group(1)), int(m.group(2))
            continue
        m = orig_rx.match(line)
        if m:
            cur["ow"], cur["oh"] = int(m.group(1)), int(m.group(2))
            continue
        m = off_rx.match(line)
        if m:
            cur["offx"], cur["offy"] = float(m.group(1)), float(m.group(2))
            continue
        m = rot_rx.match(line)
        if m:
            cur["rot"] = m.group(1).lower() == "true"
    return pages, regions


# ---------------- 矩阵 ----------------
def mat_mul(a, b):
    return [[a[0][0] * b[0][0] + a[0][1] * b[1][0], a[0][0] * b[0][1] + a[0][1] * b[1][1], a[0][0] * b[0][2] + a[0][1] * b[1][2] + a[0][2]],
            [a[1][0] * b[0][0] + a[1][1] * b[1][0], a[1][0] * b[0][1] + a[1][1] * b[1][1], a[1][0] * b[0][2] + a[1][1] * b[1][2] + a[1][2]]]


def mat_trs(x, y, rot_deg, sx, sy):
    r = math.radians(rot_deg)
    c, s = math.cos(r), math.sin(r)
    return [[c * sx, -s * sy, x], [s * sx, c * sy, y]]


IDENT = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]


# ---------------- 动画采样 ----------------
def sample(keys, t, default):
    if not keys:
        return default
    if t <= keys[0].get("time", 0):
        k = keys[0]
        return tuple(k.get(f, d) for f, d in default)
    for i in range(len(keys) - 1):
        k0, k1 = keys[i], keys[i + 1]
        t0, t1 = k0.get("time", 0), k1.get("time", 0)
        if t0 <= t <= t1:
            u = 0 if t1 == t0 else (t - t0) / (t1 - t0)
            return tuple(k0.get(f, d) + (k1.get(f, d) - k0.get(f, d)) * u
                         for f, d in default)
    k = keys[-1]
    return tuple(k.get(f, d) for f, d in default)


def bone_world(skel, anim, t):
    bones = skel["bones"]
    anim_bones = (anim or {}).get("bones", {})
    world = {}
    for b in bones:
        name = b["name"]
        x, y = b.get("x", 0.0), b.get("y", 0.0)
        rot, sx, sy = b.get("rotation", 0.0), b.get("scaleX", 1.0), b.get("scaleY", 1.0)
        tl = anim_bones.get(name, {})
        if "translate" in tl:
            x, y = sample(tl["translate"], t, (("x", 0.0), ("y", 0.0)))
        if "rotate" in tl:
            (rot,) = sample(tl["rotate"], t, (("angle", 0.0),))
        if "scale" in tl:
            sx, sy = sample(tl["scale"], t, (("x", 1.0), ("y", 1.0)))
        local = mat_trs(x, y, rot, sx, sy)
        parent = b.get("parent")
        world[name] = mat_mul(world[parent], local) if parent in world else local
    return world


# ---------------- 绘制 ----------------
def draw_region(canvas, page_img, region, att, world_mat, scale, off):
    w = float(att.get("width", region.get("w", 0)))
    h = float(att.get("height", region.get("h", 0)))
    if w <= 0 or h <= 0:
        return False
    local = mat_trs(float(att.get("x", 0)), float(att.get("y", 0)),
                    float(att.get("rotation", 0)), 1.0, 1.0)
    m = mat_mul(world_mat, local)

    # 源图裁切（atlas 可能旋转 90°）
    rx, ry, rw, rh = region["x"], region["y"], region["w"], region["h"]
    crop = page_img.crop((rx, ry, rx + rw, ry + rh))
    if region.get("rot"):
        crop = crop.transpose(Image.ROTATE_90)

    # 目标尺寸（按 spine 单位 × 全局缩放）
    dw, dh = abs(w * scale), abs(h * scale)
    if dw < 1 or dh < 1:
        return False
    sprite = crop.resize((max(1, int(round(dw))), max(1, int(round(dh)))), Image.BILINEAR)

    # 合成变换：世界矩阵 → 像素坐标（中心对齐 + 翻转 y）
    # 位置 = m 作用于 (0,0)
    px = m[0][2] * scale + off[0]
    py = -m[1][2] * scale + off[1]
    # 旋转 / 缩放（忽略非均匀剪切）
    a, b = m[0][0], -m[1][0]
    ang = math.degrees(math.atan2(-b, a))
    canvas.alpha_composite(sprite.rotate(ang, expand=True, resample=Image.BICUBIC),
                           (int(px - sprite.width / 2), int(py - sprite.height / 2)))
    return True




def _sample_vertices(att, world, scale, off):
    """返回顶点屏幕坐标 [(x,y)...]（y 已翻转为图像坐标）。"""
    import numpy as np

    verts = att.get("vertices") or []
    if att.get("type") == "skinnedmesh":
        pts = []
        i = 0
        while i < len(verts):
            n = int(verts[i])
            i += 1
            sx = sy = 0.0
            for _ in range(n):
                bidx, vx, vy, w = int(verts[i]), float(verts[i + 1]), float(verts[i + 2]), float(verts[i + 3])
                i += 4
                m = world.get("__bones__", [])[bidx] if bidx < len(world.get("__bones__", [])) else IDENT
                sx += (m[0][0] * vx + m[0][1] * vy + m[0][2]) * w
                sy += (m[1][0] * vx + m[1][1] * vy + m[1][2]) * w
            pts.append((sx * scale + off[0], -sy * scale + off[1]))
        return pts

    m = world.get("__slotmat__", IDENT)
    pts = []
    for i in range(0, len(verts), 2):
        vx, vy = float(verts[i]), float(verts[i + 1])
        wx = m[0][0] * vx + m[0][1] * vy + m[0][2]
        wy = m[1][0] * vx + m[1][1] * vy + m[1][2]
        pts.append((wx * scale + off[0], -wy * scale + off[1]))
    return pts


def draw_mesh(canvas, page_img, att, world, scale, off):
    """三角形光栅化 + 仿射纹理映射；返回是否画出了像素。"""
    import numpy as np

    tris = att.get("triangles") or []
    uvs = att.get("uvs") or []
    if not tris or not uvs:
        return False
    pts = _sample_vertices(att, world, scale, off)
    tex = np.asarray(page_img.convert("RGBA"), dtype=np.float32)
    th, tw = tex.shape[:2]
    out = np.asarray(canvas, dtype=np.float32).copy()
    drew = False

    for t in range(0, len(tris) - 2, 3):
        i0, i1, i2 = int(tris[t]), int(tris[t + 1]), int(tris[t + 2])
        if max(i0, i1, i2) >= len(pts) or 2 * max(i0, i1, i2) + 1 >= len(uvs):
            continue
        x0, y0 = pts[i0]; x1, y1 = pts[i1]; x2, y2 = pts[i2]
        u0, v0 = uvs[2 * i0], uvs[2 * i0 + 1]
        u1, v1 = uvs[2 * i1], uvs[2 * i1 + 1]
        u2, v2 = uvs[2 * i2], uvs[2 * i2 + 1]

        minx, maxx = int(max(0, np.floor(min(x0, x1, x2)))), int(min(canvas.width - 1, np.ceil(max(x0, x1, x2))))
        miny, maxy = int(max(0, np.floor(min(y0, y1, y2)))), int(min(canvas.height - 1, np.ceil(max(y0, y1, y2))))
        if maxx <= minx or maxy <= miny:
            continue
        den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(den) < 1e-9:
            continue

        ys, xs = np.mgrid[miny:maxy + 1, minx:maxx + 1]
        px = xs + 0.5
        py = ys + 0.5
        w0 = ((y1 - y2) * (px - x2) + (x2 - x1) * (py - y2)) / den
        w1 = ((y2 - y0) * (px - x2) + (x0 - x2) * (py - y2)) / den
        w2 = 1.0 - w0 - w1
        inside = (w0 >= -0.002) & (w1 >= -0.002) & (w2 >= -0.002)
        if not inside.any():
            continue

        u = (w0 * u0 + w1 * u1 + w2 * u2) * (tw - 1)
        v = (1.0 - (w0 * v0 + w1 * v1 + w2 * v2)) * (th - 1)
        ui = np.clip(u.astype(np.int32), 0, tw - 1)
        vi = np.clip(v.astype(np.int32), 0, th - 1)
        src = tex[vi, ui]
        a = (src[..., 3:4] / 255.0) * inside[..., None]
        sub = out[miny:maxy + 1, minx:maxx + 1]
        sub[..., :3] = src[..., :3] * a + sub[..., :3] * (1 - a)
        sub[..., 3:4] = (a * 255 + sub[..., 3:4] * (1 - a))
        out[miny:maxy + 1, minx:maxx + 1] = sub
        drew = True

    if drew:
        canvas.paste(Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA"))
    return drew


def main() -> int:
    atlas = pathlib.Path(sys.argv[1])
    out = pathlib.Path(sys.argv[2])
    size = int(sys.argv[3]) if len(sys.argv) > 3 else 256
    fps = int(sys.argv[4]) if len(sys.argv) > 4 else 15
    loops = float(sys.argv[5]) if len(sys.argv) > 5 else 2

    skel = json.loads(atlas.with_suffix(".json").read_text(encoding="utf-8"))
    pages, regions = parse_atlas(atlas)
    page_img = None
    for pg in pages:
        p = atlas.parent / pg
        if p.is_file():
            page_img = Image.open(p).convert("RGBA")
            break
    if page_img is None:
        print("没有贴图页，无法渲染")
        return 1

    W, H = skel["skeleton"].get("width", 128), skel["skeleton"].get("height", 128)
    scale = min(size / max(W, 1), size / max(H, 1))
    off = (size / 2, size / 2)

    anims = skel.get("animations") or {}
    if not anims:
        print("没有动画")
        return 1
    aname = next(iter(anims))
    anim = anims[aname]
    duration = 0.0
    for group in anim.values():
        if not isinstance(group, dict):
            continue
        for bone in group.values():
            if not isinstance(bone, dict):
                continue
            for tl in bone.values():
                if not isinstance(tl, list):
                    continue
                for k in tl:
                    if isinstance(k, dict):
                        duration = max(duration, float(k.get("time", 0)))

    slots = skel.get("slots", [])
    skins = skel.get("skins", {}).get("default", {})
    bones_mat = []
    frames = []
    drawn_mesh = 0
    total = max(1, int(duration * fps * loops))
    skipped = 0
    for i in range(total):
        t = (i / fps) % max(duration, 0.001)
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        world = bone_world(skel, anim, t)
        bones_mat = [world.get(b["name"], IDENT) for b in skel["bones"]]
        for slot in slots:
            sname = slot["name"]
            att_name = slot.get("attachment")
            if not att_name:
                continue
            att = (skins.get(sname) or {}).get(att_name)
            if not att:
                continue
            atype = att.get("type", "region")
            bm = world.get(slot["bone"], IDENT)
            if atype in ("mesh", "skinnedmesh"):
                world["__bones__"] = bones_mat
                world["__slotmat__"] = bm
                if draw_mesh(canvas, page_img, att, world, scale, off):
                    drawn_mesh += 1
                else:
                    skipped += 1
                continue
            if atype != "region":
                skipped += 1
                continue
            reg = regions.get(att.get("name") or att_name)
            if not reg:
                continue
            draw_region(canvas, page_img, reg, att, bm, scale, off)
        frames.append(canvas)

    out.parent.mkdir(parents=True, exist_ok=True)
    # GIF 需要不透明帧：铺到深色底上再转 P
    bg = Image.new("RGBA", (size, size), (12, 12, 14, 255))
    flat = []
    for f in frames:
        c = bg.copy()
        c.alpha_composite(f)
        flat.append(c.convert("P", palette=Image.ADAPTIVE, colors=256))
    flat[0].save(out, save_all=True, append_images=flat[1:], duration=int(1000 / fps),
                 loop=0, optimize=False)
    print("动画 %s ｜ 时长 %.2fs ｜ 帧 %d ｜ 尺寸 %d ｜ mesh 绘制 %d 次 ｜ 跳过 %d 次"
          % (aname, duration, len(frames), size, drawn_mesh, skipped))
    print("输出", out, out.stat().st_size // 1024, "KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
