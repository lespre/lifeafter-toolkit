# -*- coding: utf-8 -*-
"""APNG 质检：逐个检查 avatar_anim 里的动图
   1) 帧数 / 时长
   2) 帧间差异（是否真的在动）——比较相邻帧的像素差
   3) 裁切检测——非透明像素是否贴到画布边缘（贴边=内容被切）
   4) 宽高比 vs 同 id 的静态图（是否被拉伸变形）
输出：疑似问题清单 + 统计
"""
import json, pathlib, sys, collections
from PIL import Image, ImageSequence
import numpy as np

WEB = pathlib.Path(__file__).resolve().parents[1]
ANIM = WEB / "assets/avatar_anim"
STATIC = WEB / "assets/img_cache/avatar_catalog"

def alpha_bbox(arr):
    ys, xs = np.where(arr[:, :, 3] > 4)
    if len(xs) == 0:
        return None
    return xs.min(), ys.min(), xs.max(), ys.max()

def analyze(p):
    try:
        im = Image.open(p)
    except Exception as e:
        return {"err": "open: %s" % e}
    frames = [f.convert("RGBA") for f in ImageSequence.Iterator(im)]
    if not frames:
        return {"err": "no frames"}
    n = len(frames)
    w, h = frames[0].size
    durs = []
    try:
        durs = list(im.info.get("duration", []))
    except Exception:
        pass
    # 帧间差异
    diffs = []
    for i in range(1, n):
        a = np.asarray(frames[i - 1], dtype=np.int16)
        b = np.asarray(frames[i], dtype=np.int16)
        d = np.abs(a - b)
        diffs.append(float(d.mean()))
    # 边缘裁切检测
    touch = 0
    for f in frames:
        arr = np.asarray(f)
        bb = alpha_bbox(arr)
        if bb is None:
            touch += 1
            continue
        x0, y0, x1, y1 = bb
        if x0 <= 0 or y0 <= 0 or x1 >= w - 1 or y1 >= h - 1:
            touch += 1
    return {
        "frames": n, "w": w, "h": h,
        "duration_ms": sum(d for d in durs if isinstance(d, (int, float))) or None,
        "max_diff": max(diffs) if diffs else 0.0,
        "mean_diff": (sum(diffs) / len(diffs)) if diffs else 0.0,
        "touch_frames": touch,
        "has_alpha": bool(np.asarray(frames[0])[:, :, 3].min() < 250),
    }

def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    d = json.load(open(WEB / "data/boards/avatar_catalog.json", encoding="utf-8"))
    meta = {}
    for it in d["items"]:
        a = (it.get("_media") or {}).get("anim")
        if a:
            meta[pathlib.Path(a).stem] = it
    files = sorted(ANIM.glob("*.png"))
    if limit:
        files = files[:limit]
    print("APNG 总数:", len(files))
    rows = []
    kinds = collections.Counter()
    issues = []
    for p in files:
        r = analyze(p)
        if "err" in r:
            issues.append((p.stem, "ERR", r["err"]))
            continue
        it = meta.get(p.stem)
        kind = (it or {}).get("kind") or "?"
        kinds[kind] += 1
        if r["max_diff"] < 0.8:
            issues.append((p.stem, "静止", "maxdiff=%.2f frames=%d %s" % (r["max_diff"], r["frames"], (it or {}).get("name", ""))))
        if r["touch_frames"] > r["frames"] * 0.5:
            issues.append((p.stem, "贴边", "touch=%d/%d" % (r["touch_frames"], r["frames"])))
        # 宽高比与静态图比较
        sp = STATIC / (p.stem + ".png")
        if sp.is_file():
            try:
                sw, sh = Image.open(sp).size
                if sw and sh:
                    ar_a = r["w"] / r["h"]
                    ar_s = sw / sh
                    if abs(ar_a / ar_s - 1) > 0.35 and abs(ar_a / ar_s - 1) / (ar_s and 1) > 0.35:
                        issues.append((p.stem, "比例", "anim %.2f vs static %.2f (%s)" % (ar_a, ar_s, (it or {}).get("name", ""))))
            except Exception:
                pass
        rows.append((p.stem, kind, r))
    print("按类型:", dict(kinds))
    print("帧数分布:", dict(collections.Counter(r[2]["frames"] for r in rows)))
    print("尺寸分布(前10):", dict(collections.Counter((r[2]["w"], r[2]["h"]) for r in rows).most_common(10)))
    print("\n=== 可疑清单 (%d) ===" % len(issues))
    c = collections.Counter(t for _, t, _ in issues)
    print("分类统计:", dict(c))
    for stem, typ, msg in issues[:60]:
        print("  [%s] %s  %s" % (typ, stem, msg))
    json.dump([{"id": s, "type": t, "msg": m} for s, t, m in issues],
              open("/tmp/qa_issues.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
