# -*- coding: utf-8 -*-
"""头像板「边框类」卡面主图归位（名片框 / 头像框）。

★ 修的到底是什么（2026-10-30）
  名片框的卡面此前把 `resource_path`（= `img_biankuang_b_NN`，**整幅场景底图**）
  当成「边框图」挂上去，于是 217 张名片框里有 49 张显示的是风景/场景截图，
  一眼看去就是「一堆 bug」。真实口径是：
    · 边框图 = `img_biankuang_NN`（1292×810，**中空**，中间透出内容）
    · `img_biankuang_b_NN` = 场景底图（432×252）—— 是背景，不是边框
    · Spine 家族的名片框没有静态边框图，边框画在 Spine 图集里

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
ICONS = WEB / "assets/avatar_icons"
ANIM = WEB / "assets/avatar_anim"

# 中心区域不透明像素占比超过此值 → 判定为「实心场景图」，不是边框
SOLID_MAX = 0.25
KINDS = ("名片框", "头像框")


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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="真正写回 json（默认只报告）")
    ap.add_argument("--budget", type=float, default=1800.0)
    a = ap.parse_args()

    t0 = time.time()
    res = Resolver()
    cat = json.loads(CAT.read_text(encoding="utf-8"))
    items = cat["items"]

    stat = {"静态边框": 0, "Spine首帧": 0, "沿用原图": 0, "无边框图": 0, "场景图被替换": 0}
    details = []
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

        # 4) 场景底图降级成次图（保留信息，但不再冒充边框）
        sec = [x for x in imgs if x is not cur]
        scene = None
        for x in sec:
            if x.get("role") == "background":
                scene = x
        for x in imgs:
            if x is not cur and x.get("role") != "background":
                # 旧的次图（可能是背景也可能是图标）→ 统一标成 background
                x["role"] = "background"
        if cur is not None and cur_solid is not None and cur_solid >= SOLID_MAX:
            # 当前主图其实是场景底图 → 降级
            scene = {"png": cur["png"], "label": "名片背景", "role": "background",
                     "base": cur.get("base") or it.get("resource_path")}
            stat["场景图被替换"] += 1

        if main_img is None:
            stat["无边框图"] += 1
            it["image_status"] = "无边框图"
            it["image_note"] = ("当前 PE/PC 包快照里该名片框的边框资源不可得"
                                "（静态图未收录且 Spine 贴图页缺失）")
            m["frame_status"] = "missing"
            new_imgs = ([scene] if scene else []) + [x for x in imgs
                                                    if x is not cur and x is not scene]
        else:
            if cur is not None and cur_solid is not None and cur_solid >= SOLID_MAX:
                stat["场景图被替换"] += 0      # 已计数
            else:
                stat["沿用原图"] += 1
            it.pop("image_status", None)
            it.pop("image_note", None)
            m["frame_status"] = "ok"
            new_imgs = [main_img] + ([scene] if scene else []) + \
                       [x for x in imgs if x is not cur and x is not scene]

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
    if a.apply:
        CAT.write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding="utf-8")
        print("已写回 %s（用时 %.0fs）" % (CAT.name, time.time() - t0))
    else:
        print("试运行，未写回（加 --apply 生效）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
