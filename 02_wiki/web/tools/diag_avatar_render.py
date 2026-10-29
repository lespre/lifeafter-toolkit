# -*- coding: utf-8 -*-
"""头像板动图渲染全量诊断：逐条走真实链路，抓出精确失败原因。

与 build_avatar_anim.py 的区别：
  · 不做产物缓存短路（--force 语义），每条都真跑
  · 记录**每一级**的细节（atlas/json/页贴图/解析/动画名/渲染/产出校验）
  · 对已产出文件额外做质量体检（帧数、全透明、帧间差）
  · 输出 JSON + Markdown 报告
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
import traceback

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ                                        # noqa: E402
WEB = PROJ / "02_wiki/web"
sys.path.insert(0, str(WEB / "tools"))
from avatar_resolve import Resolver                              # noqa: E402
import spine_render_fix as FX                                    # noqa: E402
from PIL import Image                                            # noqa: E402

CAT = WEB / "data/boards/avatar_catalog.json"
SPINE_DIR = WEB / "assets/spine_live"
ANIM_DIR = WEB / "assets/avatar_anim"
REPORT_DIR = PROJ / "01_索引与产物/30_分析"
MIN_BYTES = 1024


def resolve_pages(base, atlas_text, pages, res):
    """解析页贴图：严格按 atlas 声明的页名，不做顶替。
    顺序：本地同名页 → 目录相对页 → base+.png → 回源 fetch_png。"""
    out, missing = {}, []
    d0 = base.rsplit("/", 1)[0] if "/" in base else ""
    for pg in pages:
        cands = []
        if d0:
            cands.append(SPINE_DIR / (d0 + "/" + pg))
        cands.append(SPINE_DIR / pg)
        cands.append(SPINE_DIR / (base + ".png"))
        found = None
        for c in cands:
            if c.is_file():
                found = c
                break
        if found is None:
            # 回源：把页贴图落到 spine_live 缓存
            cache = SPINE_DIR / (d0 + "/" + pg if d0 else pg)
            try:
                cache.parent.mkdir(parents=True, exist_ok=True)
                if res.fetch_png((d0 + "/" + pg if d0 else pg), cache):
                    found = cache
            except Exception:                                    # noqa: BLE001
                pass
        if found is None:
            missing.append(pg)
            continue
        try:
            out[pg] = Image.open(found).convert("RGBA")
        except Exception:                                        # noqa: BLE001
            missing.append(pg + "(解码失败)")
    return out, missing


def diag_one(it, res, do_render=True):
    """返回 dict：id/kind/name/base/ok/stage/detail/耗时"""
    iid = it["id"]
    base = (it.get("spine_path") or "").strip().replace("\\", "/").rstrip("/")
    rec = {"id": iid, "kind": it.get("kind"), "name": it.get("name"),
           "base": base, "ok": False, "stage": "", "detail": "",
           "t": 0.0}
    t0 = time.time()
    at_f = SPINE_DIR / (base + ".atlas")
    js_f = SPINE_DIR / (base + ".json")

    # 1) atlas
    atlas_text = None
    if at_f.is_file():
        atlas_text = at_f.read_text(encoding="utf-8", errors="ignore")
        rec["stage"] = "atlas本地"
    else:
        try:
            atlas_text = res.fetch_text(base + ".atlas")
            rec["stage"] = "atlas回源"
            if atlas_text is not None:
                at_f.parent.mkdir(parents=True, exist_ok=True)
                at_f.write_text(atlas_text, encoding="utf-8")
        except Exception as ex:                                  # noqa: BLE001
            rec["stage"], rec["detail"] = "atlas", "回源异常 " + str(ex)[:160]
            rec["t"] = time.time() - t0
            return rec
        if atlas_text is None:
            rec["stage"] = "atlas"
            rec["detail"] = "PE/PC/校准表三路均未收录"
            rec["t"] = time.time() - t0
            return rec

    # 2) json
    if not js_f.is_file():
        try:
            t = res.fetch_text(base + ".json")
            if t is not None:
                js_f.parent.mkdir(parents=True, exist_ok=True)
                js_f.write_text(t, encoding="utf-8")
        except Exception:                                       # noqa: BLE001
            pass
    if not js_f.is_file():
        rec["stage"], rec["detail"] = "json", "骨架 json 三路均未收录"
        rec["t"] = time.time() - t0
        return rec

    # 3) 解析
    try:
        skel, pages, regions = FX.load_atlas(at_f)
    except Exception as ex:                                      # noqa: BLE001
        rec["stage"] = "解析"
        rec["detail"] = "%s: %s" % (type(ex).__name__, str(ex)[:160])
        rec["t"] = time.time() - t0
        return rec
    if not pages:
        rec["stage"], rec["detail"] = "解析", "atlas 未解析出任何页"
        rec["t"] = time.time() - t0
        return rec
    if not regions:
        rec["stage"], rec["detail"] = "解析", "atlas 未解析出任何 region"
        rec["t"] = time.time() - t0
        return rec

    # 4) 页贴图（同时记录回源能力）
    img_of, missing = resolve_pages(base, atlas_text, pages, res)
    if not img_of:
        rec["stage"] = "贴图页"
        rec["detail"] = "atlas 声明页 %s 全部取不到" % ",".join(pages)
        rec["t"] = time.time() - t0
        return rec
    if missing:
        rec["warn"] = "部分页缺失: %s" % ",".join(missing)

    # 5) 动画名
    aname = FX.anim_name(skel)
    if not aname:
        rec["stage"], rec["detail"] = "动画", "骨架里无任何动画"
        rec["t"] = time.time() - t0
        return rec

    # 6) 渲染
    if not do_render:
        rec["ok"] = True
        rec["stage"] = "可渲染"
        rec["t"] = time.time() - t0
        return rec
    dur = FX.anim_duration(skel, aname) or 1.0
    cnt = max(6, min(24, int(round(dur * 10))))
    try:
        frs, meta = FX.render_frames(at_f, img_of, box=168, cnt=cnt, aname=aname)
    except Exception as ex:                                      # noqa: BLE001
        rec["stage"] = "渲染"
        rec["detail"] = "%s: %s" % (type(ex).__name__, str(ex)[:160])
        rec["t"] = time.time() - t0
        return rec
    if not frs:
        rec["stage"], rec["detail"] = "渲染", "render_frames 返回空帧列表"
        rec["t"] = time.time() - t0
        return rec

    # 7) 产出质量校验
    import numpy as np
    a0 = np.asarray(frs[0])
    cover = float((a0[:, :, 3] > 4).mean())
    if cover < 0.001:
        rec["stage"] = "产出"
        rec["detail"] = "首帧全透明（覆盖率 %.5f）—— 渲染画不出内容" % cover
        rec["t"] = time.time() - t0
        return rec
    if cover > 0.985:
        rec["warn"] = "首帧几乎满幅（%.3f），疑似整幅场景图而非边框/角色" % cover
    rec["ok"] = True
    rec["stage"] = "OK"
    rec["frames"] = len(frs)
    rec["cover"] = round(cover, 4)
    rec["anim"] = aname
    rec["t"] = time.time() - t0
    return rec


def audit_existing():
    """对已产出文件做质量体检。"""
    import numpy as np
    from PIL import ImageSequence
    out = []
    for p in sorted(ANIM_DIR.glob("*.png")):
        if p.stem.endswith("_f0"):
            continue
        try:
            im = Image.open(p)
        except Exception as ex:                                  # noqa: BLE001
            out.append({"id": p.stem, "err": "打不开: %s" % str(ex)[:80]})
            continue
        frames = [f.convert("RGBA") for f in ImageSequence.Iterator(im)]
        n = len(frames)
        a0 = np.asarray(frames[0])
        cover = float((a0[:, :, 3] > 4).mean())
        diffs = []
        for i in range(1, min(n, 12)):
            d = np.abs(np.asarray(frames[i - 1], dtype=np.int16)
                       - np.asarray(frames[i], dtype=np.int16)).mean()
            diffs.append(round(float(d), 2))
        out.append({
            "id": p.stem, "mode": im.mode, "frames": n,
            "size": "%dx%d" % im.size, "cover": round(cover, 4),
            "maxdiff": max(diffs) if diffs else 0,
            "bytes": p.stat().st_size,
            "quantized": im.mode == "P",
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(REPORT_DIR / "avatar_anim_render_report.json"))
    ap.add_argument("--md", default=str(REPORT_DIR / "avatar_anim_render_report.md"))
    ap.add_argument("--no-render", action="store_true", help="只查资源链路，不真渲染")
    a = ap.parse_args()

    res = Resolver()
    cat = json.loads(CAT.read_text(encoding="utf-8"))
    items = cat["items"]
    t0 = time.time()
    recs = []
    for n, it in enumerate(items, 1):
        if not (it.get("spine_path") or "").strip():
            continue
        recs.append(diag_one(it, res, do_render=not a.no_render))
        if n % 20 == 0:
            print("  diag %d/%d  %.0fs" % (n, len(items), time.time() - t0), flush=True)

    stages = {}
    for r in recs:
        k = r["stage"] if not r["ok"] else "OK"
        stages[k] = stages.get(k, 0) + 1
    existing = audit_existing()

    payload = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_items": len(items),
        "with_spine": len(recs),
        "ok": sum(1 for r in recs if r["ok"]),
        "failed": sum(1 for r in recs if not r["ok"]),
        "stage_breakdown": stages,
        "records": recs,
        "existing_products": existing,
    }
    pathlib.Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(a.out).write_text(json.dumps(payload, ensure_ascii=False, indent=1),
                                   encoding="utf-8")
    print(json.dumps({k: v for k, v in payload.items()
                      if k not in ("records", "existing_products")},
                     ensure_ascii=False, indent=1))
    print("已写 %s" % a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
