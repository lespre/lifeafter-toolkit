# -*- coding: utf-8 -*-
"""头像板「边框类」卡面主图归位（名片框 / 头像框）。

★ 修的到底是什么（2026-10-30）
  名片框的卡面此前把 `resource_path`（= `img_biankuang_b_NN`，**整幅场景底图**）
  当成「边框图」挂上去，于是 217 张名片框里有 49 张显示的是风景/场景截图，
  一眼看去就是「一堆 bug」。真实口径是：
    · 边框图 = `img_biankuang_NN`（1292×810，**中空**，中间透出内容）
    · `img_biankuang_b_NN` = 场景底图（432×252）—— 是背景，不是边框
    · Spine 家族的名片框没有静态边框图，边框画在 Spine 图集里

★ 2026-11-01 补：名片框的**背景图**（场景底图）也要找出来
  背景图 = `resource_path`（`img_biankuang_b_NN.png`），是**实心的整幅场景**，
  和「中空边框」正好互补：边框叠在背景上才是完整的游戏内名片。
  以前脚本只在「主图被误挂成场景图」时把它降级成次图，从不主动去找 ——
  于是 217 张名片框里绝大多数只有一层中空边线，背景层整片缺失。
  现在按 `resource_path` 主动回源（还原树 → 索引/校准表），落盘到
  `assets/avatar_frames_bg/<id>.png`，挂为 `role:"background"` 次图。
  校验三道（任一不过就**如实不挂**，绝不拿边框/图标顶替）：
      1) 路径必须含 `_b_`（背景命名约定）；
      2) 中心不透明占比 ≥ 25%（中空图是边框，不是背景）；
      3) 横版名片比例 1.45~2.0、短边 ≥ 200px（防止串到碎屑图/图标）。

本脚本按下列优先级给每张边框卡定主图：
  1) 静态高清边框：`image_path` 经统一解析器（PE → PC 索引 → PC 校准表）取图，
     并用「中心不透明像素占比 < 25%」校验它确实是**中空边框**，不是场景；
  2) Spine 渲染首帧（`assets/avatar_anim/<id>_f0.png`）—— 真边框，且可悬停播放；
  3) 都没有 → **主图置空**，明确标注「边框图缺失（当前包快照无该资源）」，
     场景底图降级为标注清楚的次图「名片背景」，绝不冒充边框。

用法：python build_avatar_frames.py [--apply] [--budget 1800]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
from avatar_resolve import Resolver                # noqa: E402
from PIL import Image                              # noqa: E402
import numpy as np                                 # noqa: E402

WEB = PROJ / "02_wiki/web"
CAT = WEB / "data/boards/avatar_catalog.json"
FRAMES = WEB / "assets/avatar_frames"
FRAMES_BG = WEB / "assets/avatar_frames_bg"
ICONS = WEB / "assets/avatar_icons"
ANIM = WEB / "assets/avatar_anim"

# 中心区域不透明像素占比超过此值 → 判定为「实心场景图」，不是边框
SOLID_MAX = 0.25
KINDS = ("名片框", "头像框")

# 名片背景（场景底图）的形态约束：横版整卡、实心
BG_AR_MIN, BG_AR_MAX = 1.45, 2.0
BG_MIN_W, BG_MIN_H = 360, 200


def solid_ratio(path: pathlib.Path):
    """中心 50%×50% 区域的不透明像素占比；读不出返回 None。"""
    try:
        with Image.open(path) as im:
            a = np.asarray(im.convert("RGBA"))[:, :, 3]
    except Exception:                                   # noqa: BLE001
        return None
    if a.size == 0:
        return None
    h, w = a.shape
    cy, cx = h // 4, w // 4
    c = a[cy:cy + h // 2, cx:cx + w // 2]
    return float((c > 8).mean())


def fetch_frame(res: Resolver, logical: str, dst: pathlib.Path):
    """取静态边框图并落盘；返回 'hollow' / 'solid' / None。"""
    if not logical:
        return None
    logical = logical.replace("\\", "/").lstrip("/")
    stem = logical.rsplit(".", 1)[0]
    # 已知历史坑：`img_biankuang_b_NN` 是场景底图，绝不能当边框
    if "_b_" in stem:
        return None
    if not res.fetch_png(stem + ".png", dst):
        return None
    r = solid_ratio(dst)
    if r is None:
        dst.unlink(missing_ok=True)
        return None
    return "hollow" if r < SOLID_MAX else "solid"


def fetch_background(res: Resolver, logical: str, dst: pathlib.Path):
    """取名片背景（场景底图）并落盘；不合形态就删掉返回 False。

    ★ 三道校验见文件头：必须是 `_b_` 命名、实心、横版整卡尺寸。
      任何一道不过都如实返回 False —— 宁可缺背景层，也不拿边框/图标冒充。
    """
    if not logical:
        return False
    logical = logical.replace("\\", "/").lstrip("/")
    if "_b_" not in logical.rsplit(".", 1)[0]:
        return False
    # 还原树优先（文件名即逻辑路径），取不到再走索引/校准表
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = res.tree_image(logical)
    if im is not None:
        im.save(dst)
    elif not res.fetch_png(logical, dst):
        return False
    try:
        with Image.open(dst) as im2:
            w, h = im2.size
    except Exception:                                   # noqa: BLE001
        dst.unlink(missing_ok=True)
        return False
    if w < BG_MIN_W or h < BG_MIN_H or not (BG_AR_MIN <= w / h <= BG_AR_MAX):
        dst.unlink(missing_ok=True)
        return False
    r = solid_ratio(dst)
    if r is None or r < SOLID_MAX:
        dst.unlink(missing_ok=True)
        return False
    return True


def _interior_mask(cv2, a):
    """找出「被边框围住」的透明内孔 → 二值 mask；找不到返回 None。

    ★ 2026-11-01 修正：旧法直接取中心透明像素的连通域，遇到装饰件之间有小缺口
      （内孔与画布外连通）就量不到，只能退回中心行列法，背景于是按一个大矩形铺，
      在斜边/角饰处露出一块方角。新法先把不透明区做闭运算封住细缝，再从画布四边
      找「外部」，剩下没被外部连到的透明区就是内孔；从细核到粗核逐级尝试，
      封不住才算真开口（如实退回兜底，不硬猜）。
    """
    h, w = a.shape
    opaque = (a > 8).astype(np.uint8)
    base_k = max(3, int(round(0.006 * min(h, w))) | 1)
    for k in (base_k, base_k * 2 | 1, base_k * 4 | 1):
        ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
        closed = cv2.morphologyEx(opaque, cv2.MORPH_CLOSE, ker)
        free = (closed == 0).astype(np.uint8)
        n, lab, st, _c = cv2.connectedComponentsWithStats(free, 4)
        outside = np.zeros(n, bool)
        for i in range(1, n):
            x, y, bw, bh, _area = st[i]
            if x == 0 or y == 0 or x + bw >= w or y + bh >= h:
                outside[i] = True                 # 触到画布边 = 与外界连通
        best_i, best_d = -1, float("inf")
        for i in range(1, n):
            if outside[i] or st[i][4] * 50 < w * h:   # 太小的碎片不是内孔
                continue
            d = ((st[i][0] + st[i][2] / 2 - w / 2) ** 2
                 + (st[i][1] + st[i][3] / 2 - h / 2) ** 2)
            if d < best_d:
                best_d, best_i = d, i
        if best_i >= 0:
            return (lab == best_i).astype(np.uint8)
    return None


def _silhouette_mask(cv2, a):
    """框的「整体轮廓」：返回被框围住的整块区域（含框体+框内），找不到返回 None。

    ★ 2026-11-01 二次修正（用户反馈「背景和名片框还是不适配」）：
      上一版把 clip 取成「透明内孔的轮廓」—— 框上的花枝/藤蔓往孔里探进来时，
      内孔轮廓就会绕着这些装饰啃出一圈缺口，背景因此被切掉一块块，
      合成后表现为框内沿边一圈锯齿状暗斑。实际正确的口子只要「不露到框外」，
      框内被装饰压住的地方背景本来就该继续铺着（装饰画在上面会盖住）。
      所以 clip 改取**外轮廓**：框内所有位置都允许背景，只有框外才裁掉。
      阈值用 alpha>=96（只认明确的框体），柔光/抗锯齿算透明，避免光效把轮廓撑歪。
    """
    h, w = a.shape
    base = max(3, int(round(0.004 * min(h, w))) | 1)
    for th in (96, 64, 40):
        solid = (a >= th).astype(np.uint8)
        for mul in (1, 2, 4):
            k = base * mul | 1
            ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
            closed = cv2.morphologyEx(solid, cv2.MORPH_CLOSE, ker)
            free = (closed == 0).astype(np.uint8)
            n, lab, st, _c = cv2.connectedComponentsWithStats(free, 4)
            outside = np.zeros(n, bool)
            for i in range(1, n):
                x, y, bw, bh, _area = st[i]
                if x == 0 or y == 0 or x + bw >= w or y + bh >= h:
                    outside[i] = True             # 触到画布边 = 与框外连通
            leak = np.zeros((h, w), bool)
            for i in range(1, n):
                if outside[i]:
                    leak |= (lab == i)
            inside = ~leak
            # 面积过小说明框有真开口、外部灌进来了 —— 这一档不可信，继续加粗封缝
            if inside.sum() >= 0.25 * w * h:
                return inside.astype(np.uint8)
    return None


def _interior_union(cv2, a, sil, main, w, h):
    """外轮廓内「明确透明」且与主内孔相邻的碎片并集 —— 补齐被装饰切开的薄片。

    ★ 为什么不直接取「轮廓内所有透明像素」：框体本身（花边/丝带之间）也有透明缝隙，
      全并进来会把 bbox 撑到整张卡，背景铺到底会从半透明的边框里透出来，反而更假。
      这里以主内孔（离中心最近的最大透光块）为种子，只收「bbox 与种子 bbox 相交
      （外扩 0.8% 长边）」的碎片，一条丝带切出来的贴边薄片都会被收进来，
      而边框环上的独立缝隙不会被牵连。
    ★ 外扩量从 2% 收到 0.8%（2026-11-02 灯箱实测 bc_580219）：框右侧挂饰（灯笼/花枝）
      之间那道缝离内孔右沿只有 ~24px，2%（26px）恰好把它收进来，背景于是铺到
      外轮廓边界、从缝里透出一大块蓝色场景。0.8%（10px）只够接住被丝带切开的
      内孔薄片，接不到外侧挂饰的缝。
    """
    hole = ((sil > 0) & (a < 96)).astype(np.uint8)
    n, lab, st, _c = cv2.connectedComponentsWithStats(hole, 4)
    if n <= 1:
        return main
    # 种子：主内孔所在的连通块（_interior_mask 给的 mask 与 hole 的交集里面积最大的）
    seed_i, seed_n = -1, 0
    for i in range(1, n):
        overlap = int(np.count_nonzero((lab == i) & (main > 0)))
        if overlap > seed_n:
            seed_i, seed_n = i, overlap
    if seed_i < 0:
        return main
    pad = max(4, int(round(0.008 * max(w, h))))
    min_area = max(16, int(0.0015 * w * h))
    keep = np.zeros((h, w), bool)
    x0, y0, bw, bh, _ar = st[seed_i]
    cx0, cy0 = x0 - pad, y0 - pad
    cx1, cy1 = x0 + bw + pad, y0 + bh + pad
    for i in range(1, n):
        x, y, bw2, bh2, area = st[i]
        if i == seed_i:
            keep |= (lab == i)
            continue
        if area < min_area:
            continue
        if x > cx1 or y > cy1 or x + bw2 < cx0 or y + bh2 < cy0:
            continue
        keep |= (lab == i)
    return keep.astype(np.uint8) if keep.any() else main


def _polygon_of(cv2, mask, w, h, eps_ratio, max_pts=600):
    """取 mask 的最大外轮廓 → 归一化多边形点列；取不到返回 None。"""
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return None
    c = max(cnts, key=cv2.contourArea)
    if cv2.contourArea(c) < 0.02 * w * h:
        return None
    eps = max(1.0, eps_ratio * max(w, h))
    poly = cv2.approxPolyDP(c, eps, True).reshape(-1, 2)
    while len(poly) > max_pts:
        eps *= 1.5
        poly = cv2.approxPolyDP(c, eps, True).reshape(-1, 2)
    if len(poly) < 3:
        return None
    return [[round(px / w, 5), round(py / h, 5)] for px, py in poly]


def hole_geom(path: pathlib.Path):
    """量边框的「内孔」几何：返回 {"bbox":[l,t,w,h], "clip":[[x,y],...]}（0~1）；量不到 None。

    bbox = 背景照片摆放位置（内孔外接框，外扩 2~4px 压进框底）；
    clip = 允许背景显示的多边形。★ 取「框的外轮廓」而不是内孔轮廓：
      内孔轮廓会被探进孔里的花枝/藤蔓啃出缺口，背景沿边出现锯齿状暗斑；
      外轮廓只在框外裁切，框内被装饰压住的地方背景照常铺，边缘才自然闭合。
      外轮廓实在取不到（框真有开口）时，退回内孔轮廓。
    """
    try:
        with Image.open(path) as im:
            a = np.asarray(im.convert("RGBA"))[:, :, 3]
    except Exception:                                   # noqa: BLE001
        return None
    h, w = a.shape
    if h < 8 or w < 8:
        return None
    cy, cx = h // 2, w // 2
    if a[cy, cx] > 8:                                   # 中心不透明 → 不是中空框
        return None
    try:
        import cv2
    except Exception:                                   # noqa: BLE001
        return _hole_fallback(a)
    inner = _interior_mask(cv2, a)
    if inner is None:
        # 内孔确实与画布外连通（框有真开口）→ 退回中心行列法，如实不裁轮廓
        return _hole_fallback(a)
    # ★ 2026-11-02 三次修正（用户二次反馈「背景图和名片框还是不太适配」）：
    #   旧 bbox 只取「离中心最近的那一块透明连通域」，可框里的花枝/丝带会横穿内孔，
    #   把整块内孔切成一堆碎片 —— 贴在边上的薄片被丢掉，背景就缩在最大那块里，
    #   框内侧于是露出一圈细长暗缝（截图实测 bc_580219 右侧、bc_580220 底边）。
    #   新口径：内孔 = 外轮廓范围内所有明确透明的像素（含被装饰切开的碎片），
    #   只按面积过滤掉零星碎点，再整体外扩 2~4px 压进框底。
    sil = _silhouette_mask(cv2, a)
    body = inner
    if sil is not None:
        body = _interior_union(cv2, a, sil, inner, w, h)
    # 外扩：背景压进框边 2~4px，消除抗锯齿造成的接缝暗边
    d = max(2, int(round(0.004 * min(h, w))))
    ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (d * 2 + 1, d * 2 + 1))
    grown = cv2.dilate(body, ker)
    ys, xs = np.nonzero(grown)
    if len(xs) == 0:
        return _hole_fallback(a)
    x0, x1 = int(xs.min()), int(xs.max())
    y0, y1 = int(ys.min()), int(ys.max())
    bw, bh = x1 - x0 + 1, y1 - y0 + 1
    # clip：优先取框的外轮廓（框内全允许背景，只有框外裁掉，不会被装饰啃出缺口）；
    # 外轮廓不可信时退回内孔轮廓，epsilon 取长边 0.12%（至少 1px）
    clip = None
    if sil is not None:
        clip = _polygon_of(cv2, sil, w, h, 0.0012)
    if not clip:
        clip = _polygon_of(cv2, grown, w, h, 0.0012)
    return {"bbox": [round(x0 / w, 5), round(y0 / h, 5),
                     round(bw / w, 5), round(bh / h, 5)], "clip": clip}


def _hole_fallback(a):
    """中心行 / 中心列的连续透明段交集（内孔与外界连通时的兜底），返回 bbox 形态。"""
    h, w = a.shape
    cy, cx = h // 2, w // 2
    if a[cy, cx] > 8:
        return None
    row = a[cy] > 8
    left = np.where(row[:cx])[0]
    right = np.where(row[cx + 1:])[0]
    x0 = int(left.max()) + 1 if len(left) else 0
    x1 = cx + int(right.min()) if len(right) else w - 1
    col = a[:, cx] > 8
    up = np.where(col[:cy])[0]
    down = np.where(col[cy + 1:])[0]
    y0 = int(up.max()) + 1 if len(up) else 0
    y1 = cy + int(down.min()) if len(down) else h - 1
    ys, xs = np.where(a > 8)                             # 夹到不透明内容外接框内
    if len(xs):
        x0, x1 = max(x0, int(xs.min())), min(x1, int(xs.max()))
        y0, y1 = max(y0, int(ys.min())), min(y1, int(ys.max()))
    if x1 <= x0 or y1 <= y0:
        return None
    return {"bbox": [x0 / w, y0 / h, (x1 - x0 + 1) / w, (y1 - y0 + 1) / h],
            "clip": None}


def _visible_mask(cv2, a):
    """背景「只在内孔里显形」的遮罩：内孔=1，框体与框外=0，边缘羽化 1~2px。"""
    h, w = a.shape
    inner = _interior_mask(cv2, a)
    if inner is None:
        return None
    sil = _silhouette_mask(cv2, a)
    body = _interior_union(cv2, a, sil, inner, w, h) if sil is not None else inner
    d = max(2, int(round(0.004 * min(h, w))))
    ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (d * 2 + 1, d * 2 + 1))
    body = cv2.dilate(body.astype(np.uint8), ker)
    m = cv2.GaussianBlur(body.astype(np.float32), (0, 0), 1.2)
    return np.clip(m, 0.0, 1.0)


def bake_background(frame_path: pathlib.Path, bg_path: pathlib.Path,
                    out_path: pathlib.Path, bbox) -> bool:
    """把场景底图按内孔 bbox 裁好，并把「只在内孔里显形」写进 alpha 通道。

    ★ 为什么弃用前端 clip-path（2026-11-02 用户二次反馈「背景图和名片框还是不太适配」）：
      CSS clip-path 只能吃**一个单连通多边形**，而框外挂饰（灯笼/花枝）之间的透明缝隙
      虽然落在外轮廓里，却不是内孔 —— 背景铺满就会从缝里透出来（灯箱实测 bc_580219
      右侧漏出一条蓝色场景，边界还是多边形折线）。多边形带不了洞，只能改用 alpha
      通道逐像素表达：孔里实心、孔外全透明。
    ★ 产物与边框图**同尺寸**（整卡图层）：前端 inset:0 铺满，靠 alpha 决定哪里显形。
      这样没有裁切框、没有多边形，位置对齐不会差半分。
    """
    try:
        with Image.open(frame_path) as fim:
            a = np.asarray(fim.convert("RGBA"))[:, :, 3]
    except Exception:                                   # noqa: BLE001
        return False
    h, w = a.shape
    if h < 8 or w < 8 or bbox is None:
        return False
    try:
        import cv2
    except Exception:                                   # noqa: BLE001
        return False
    mask = _visible_mask(cv2, a)
    if mask is None:
        return False
    px, py = int(round(0.0035 * w)), int(round(0.0035 * h))
    l, t, bw, bh = bbox
    x0 = max(0, int(round(l * w)) - px)
    y0 = max(0, int(round(t * h)) - py)
    x1 = min(w, int(round((l + bw) * w)) + px)
    y1 = min(h, int(round((t + bh) * h)) + py)
    cw, ch = x1 - x0, y1 - y0
    if cw < 16 or ch < 16:
        return False
    # ★ Spine 首帧只有 384~640 宽，照画布坐标烘焙会把 1080 的场景缩成小图，
    #   灯箱里再放大就发虚。整卡图层等比放大（宽高同比），让场景保持 ~1100px 量级。
    k = min(2.2, 1100.0 / cw) if cw < 1000 else 1.0
    tw, th = int(round(w * k)), int(round(h * k))
    sx, sy = int(round(x0 * k)), int(round(y0 * k))
    sw, sh = int(round(cw * k)), int(round(ch * k))
    sx = max(0, min(tw - sw, sx))
    sy = max(0, min(th - sh, sy))
    try:
        with Image.open(bg_path) as bim:
            scene = bim.convert("RGB")
            s = max(sw / scene.width, sh / scene.height)   # cover：铺满内孔框，多出的居中裁掉
            nw, nh = max(sw, int(round(scene.width * s))), max(sh, int(round(scene.height * s)))
            scene = scene.resize((nw, nh), Image.LANCZOS)
            ox, oy = (nw - sw) // 2, (nh - sh) // 2
            scene = scene.crop((ox, oy, ox + sw, oy + sh))
    except Exception:                                   # noqa: BLE001
        return False
    canvas = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    canvas.paste(scene, (sx, sy))
    alpha = mask[y0:y1, x0:x1] * 255.0
    alpha = np.asarray(Image.fromarray(alpha.round().astype(np.uint8))
                       .resize((sw, sh), Image.LANCZOS))
    full = Image.new("L", (tw, th), 0)
    full.paste(Image.fromarray(alpha), (sx, sy))
    canvas.putalpha(full)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        canvas.save(out_path, format="WEBP", quality=90, method=4)
    except Exception:                                   # noqa: BLE001
        out_path.unlink(missing_ok=True)
        return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="真正写回 json（默认只报告）")
    ap.add_argument("--budget", type=float, default=1800.0)
    a = ap.parse_args()

    t0 = time.time()
    res = Resolver()
    cat = json.loads(CAT.read_text(encoding="utf-8"))
    items = cat["items"]

    stat = {"静态边框": 0, "Spine首帧": 0, "无边框图": 0,
            "背景图": 0, "背景图缺失": 0, "背景烘焙": 0,
            "场景图降级": 0, "场景图被替换": 0}
    details = []
    bg_missing = []
    dirty = False

    for it in items:
        kind = it.get("kind")
        if kind not in KINDS:
            continue
        iid = it["id"]
        m = it.setdefault("_media", {})
        imgs = list(m.get("images") or [])
        cur = imgs[0] if imgs else None
        cur_path = (WEB / cur["png"]) if cur else None

        # 1) 现状判定
        cur_solid = None
        if cur_path and cur_path.is_file():
            cur_solid = solid_ratio(cur_path)

        # 2) 找真边框
        main_img = None
        note = ""
        dst = FRAMES / (iid + ".png")
        got = fetch_frame(res, it.get("image_path") or "", dst)
        if got == "hollow":
            main_img = {"png": "assets/avatar_frames/%s.png" % iid,
                        "label": "边框图", "role": "frame",
                        "base": it.get("image_path")}
            note = "静态高清边框（image_path）"
            stat["静态边框"] += 1
        elif got == "solid":
            dst.unlink(missing_ok=True)
            note = "image_path 解析到的是实心图（非边框），已弃用"
        # 3) 退化到 Spine 首帧
        if main_img is None:
            f0 = ANIM / (iid + "_f0.png")
            apng = ANIM / (iid + ".png")
            if f0.is_file():
                main_img = {"png": "assets/avatar_anim/%s_f0.png" % iid,
                            "label": "边框图(Spine首帧)", "role": "frame",
                            "base": it.get("spine_path")}
                note = "Spine 渲染首帧（image_path 无静态边框）"
                stat["Spine首帧"] += 1
            elif apng.is_file():
                main_img = {"png": "assets/avatar_anim/%s.png" % iid,
                            "label": "边框图(Spine)", "role": "frame",
                            "base": it.get("spine_path")}
                note = "Spine 动画（无独立首帧文件）"
                stat["Spine首帧"] += 1
        # Spine 边框同样量内孔：它也是「中空边框 + 场景底图」的同一套画法，
        # 只是贴图页缺失、只能拿到渲染图。量到了前端照样能叠（框在外、背景在孔内）。
        # ★ 每次都重量（不沿用旧值）：Spine 首帧分辨率会变（168→384），
        #   旧的内孔百分比是新图上错的位置，背景会整块错位。
        if main_img is not None:
            src = WEB / main_img["png"]
            g = hole_geom(src) if src.is_file() else None
            if g:
                main_img["hole"] = [round(v, 4) for v in g["bbox"]]
                # 非矩形内孔：额外交一条多边形轮廓，前端裁掉溢出框外的部分
                if g.get("clip"):
                    main_img["clip"] = g["clip"]
                else:
                    main_img.pop("clip", None)
        # 边框图原始宽高：前端要靠它固定卡面比例，悬停换成 Spine 动图时才不会跳尺寸
        if main_img is not None:
            src = WEB / main_img["png"]
            try:
                with Image.open(src) as _im:
                    main_img["w"], main_img["h"] = _im.width, _im.height
            except Exception:
                pass

        # 4) 背景图：主动按 resource_path 找名片场景底图（_b_ 命名）
        bg = None
        if kind == "名片框":
            if fetch_background(res, it.get("resource_path") or "",
                                FRAMES_BG / (iid + ".png")):
                bg = {"png": "assets/avatar_frames_bg/%s.png" % iid,
                      "label": "名片背景", "role": "background",
                      "base": it.get("resource_path")}
                stat["背景图"] += 1
            else:
                stat["背景图缺失"] += 1
        # 旧主图本身若是场景底图 → 它是背景，绝不能当边框
        cur_is_scene = (cur is not None and cur_solid is not None
                        and cur_solid >= SOLID_MAX)
        if cur_is_scene:
            if bg is None:
                # 头像框没有「名片背景」这个概念，实心原图如实叫「实心原图」，不串词
                bg = {"png": cur["png"],
                      "label": "名片背景" if kind == "名片框" else "实心原图",
                      "role": "background",
                      "base": cur.get("base") or it.get("resource_path")}
                stat["场景图降级"] += 1
            else:
                stat["场景图被替换"] += 1
        # ★ 2026-11-02：名片背景改「烘焙成带 alpha 的图」——场景按内孔裁好、孔外全透明。
        # 前端照旧按 --hl/--hw 摆图，但不再需要（也不再吃）clip-path 多边形。
        if (kind == "名片框" and bg is not None and main_img is not None
                and bg["png"].startswith("assets/avatar_frames_bg/")
                and main_img.get("hole")):
            _frame = WEB / main_img["png"]
            _raw = WEB / bg["png"]
            _out = FRAMES_BG / (iid + ".webp")
            if _frame.is_file() and _raw.is_file() and bake_background(
                    _frame, _raw, _out, main_img["hole"]):
                _raw.unlink(missing_ok=True)             # 原始场景底图已烘进 webp，不再留盘
                bg["png"] = "assets/avatar_frames_bg/%s.webp" % iid
                bg["fit"] = "frame"                      # 前端按整卡铺满（同边框尺寸的透明图层）
                main_img.pop("clip", None)               # alpha 已精确表达内孔，多边形无用
                stat["背景烘焙"] += 1
        # 其余次图（旧背景 / 图标）不再占主图位
        for x in imgs:
            if x.get("role") == "fixture":
                continue
            if x is not cur and not x.get("role"):
                x["role"] = "background"
            # 历史误标：头像框的次图曾被写成「名片背景」，这里按类型纠回
            if kind != "名片框" and x.get("label") == "名片背景":
                x["label"] = "实心原图"

        # 按 png 去重：脚本可重复跑，背景层不能每跑一次多挂一份
        # ★ 2026-11-02：背景改成烘焙 webp 后，旧版本留下的 `avatar_frames_bg/<id>.png`
        #   文件名不同、躲过了按 png 去重，会和新 webp 一起挂成两张「名片背景」
        #   （实测 47 张）。这里按目录前缀一并清掉旧背景。
        _bg_png = (bg or {}).get("png")
        _bg_prefix = "assets/avatar_frames_bg/%s." % iid
        others = [x for x in imgs
                  if x is not cur and x.get("png") != _bg_png
                  and not str(x.get("png") or "").startswith(_bg_prefix)]
        if kind == "名片框" and bg is None:
            bg_missing.append((iid, it.get("name")))
        if main_img is None:
            stat["无边框图"] += 1
            it["image_status"] = "无边框图"
            it["image_note"] = ("当前 PE/PC 包快照里该名片框的边框资源不可得"
                                "（静态图未收录且 Spine 贴图页缺失）"
                                + ("；背景图同样缺失" if bg is None else ""))
            m["frame_status"] = "missing"
            new_imgs = ([bg] if bg else []) + others
        else:
            it.pop("image_status", None)
            it.pop("image_note", None)
            m["frame_status"] = "ok"
            new_imgs = [main_img] + ([bg] if bg else []) + others

        if new_imgs != imgs:
            dirty = True
        m["images"] = new_imgs
        m["total"] = len(new_imgs)
        if note:
            m["frame_note"] = note
        details.append((iid, it.get("name"), kind, note or "沿用",
                        (main_img or {}).get("png")))

    print("统计：", stat)
    miss = [d for d in details if d[4] is None]
    print("无边框图 %d 张：%s" % (len(miss), [(d[0], d[1]) for d in miss[:12]]))
    print("背景图缺失 %d 张：%s" % (len(bg_missing), bg_missing[:12]))
    bg_cnt = sum(1 for it in items if it.get("kind") == "名片框"
                 and any(x.get("role") == "background"
                         and x.get("label") == "名片背景"
                         and "/avatar_frames_bg/" in x.get("png", "")
                         for x in ((it.get("_media") or {}).get("images") or [])))
    print("名片背景（新回源）%d 张" % bg_cnt)
    if a.apply:
        CAT.write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding="utf-8")
        # 看板走的是 .js（file:// 直开也要能读到），必须与 json 同步
        (WEB / "data/boards/avatar_catalog.js").write_text(
            "window.WIKI_BOARD_avatar_catalog = " + json.dumps(cat, ensure_ascii=False) + ";\n",
            encoding="utf-8")
        print("已写回 %s / %s.js（用时 %.0fs）" % (CAT.name, CAT.stem, time.time() - t0))
    else:
        print("试运行，未写回（加 --apply 生效）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
