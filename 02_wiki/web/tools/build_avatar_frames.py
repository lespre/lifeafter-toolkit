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


def hole_geom(path: pathlib.Path):
    """量边框的「内孔」几何：返回 {"bbox":[l,t,w,h], "clip":[[x,y],...]}（0~1）；量不到 None。

    为什么不只用 bbox：内孔不是矩形（框边常是斜的/带角饰），矩形背景按 bbox 铺会从
    斜边处露到框外。所以同时给一条沿透明内孔轮廓简化出来的多边形（clip），
    前端把背景按 bbox 铺进去、再用 polygon 裁掉多余部分，才是「框完全包住背景」。
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
    mask = (a <= 8).astype(np.uint8)
    _n, labels, stats, _cent = cv2.connectedComponentsWithStats(mask, 4)
    lab = int(labels[cy, cx])
    x, y, bw, bh, area = stats[lab]
    if area > 0 and x > 0 and y > 0 and x + bw < w and y + bh < h:
        bbox = [x / w, y / h, bw / w, bh / h]
        clip = None
        # 轮廓简化：epsilon 取长边的 0.6%，既能贴边又不让点太多
        sub = (labels[y:y + bh, x:x + bw] == lab).astype(np.uint8)
        cnts, _ = cv2.findContours(sub, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if cnts:
            c = max(cnts, key=cv2.contourArea)
            eps = 0.006 * max(bw, bh)
            poly = cv2.approxPolyDP(c, eps, True).reshape(-1, 2)
            if 3 <= len(poly) <= 120:
                clip = [[round((x + px) / w, 4), round((y + py) / h, 4)]
                        for px, py in poly]
        return {"bbox": bbox, "clip": clip}
    # 内孔与画布外侧连通（框有缺口）→ 退回中心行列法
    return _hole_fallback(a)


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


def hole_bbox(path: pathlib.Path):
    """兼容旧调用：只要 bbox。"""
    g = hole_geom(path)
    return g["bbox"] if g else None


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
            "背景图": 0, "背景图缺失": 0, "场景图降级": 0, "场景图被替换": 0}
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
            hole = hole_bbox(dst)
            if hole:
                main_img["hole"] = [round(v, 4) for v in hole]
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
        if main_img is not None and "hole" not in main_img:
            src = WEB / main_img["png"]
            g = hole_geom(src) if src.is_file() else None
            if g:
                main_img["hole"] = [round(v, 4) for v in g["bbox"]]
                # 非矩形内孔：额外交一条多边形轮廓，前端裁掉溢出框外的部分
                if g.get("clip"):
                    main_img["clip"] = g["clip"]
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
        _bg_png = (bg or {}).get("png")
        others = [x for x in imgs
                  if x is not cur and (not _bg_png or x.get("png") != _bg_png)]
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
