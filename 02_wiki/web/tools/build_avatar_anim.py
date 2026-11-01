# -*- coding: utf-8 -*-
"""头像板动态头像（Spine → APNG）构建：还原树优先 + 三路回源。

★ 2026-11-01 重做页贴图解析（针对「渲染乱七八糟」的根因）
  旧版把**整个 atlas 的所有页**都映射到同一个 `base + ".png"`：
  19 个多页 atlas（如 img_biankuang41 有 img_biankuang41.png +
  img_biankuang412.png）的第二、三页被第一页顶替 → 贴图串图。
  现在按 atlas 声明的**每个页名**单独取图，优先级：
      1) 新还原树（41_还原树/pe/资源）里同名资源（.ktx/.png/.bc7 均可）
      2) 本地单页缓存（spine_live/<目录>/<页名>.png）
      3) PE 索引 → PC 索引 → PC 校准表 回源
  任何一页取不到就**如实记失败**，绝不拿别的页顶替。

渲染内核见 tools/spine_render_fix.py（已支持 skinnedmesh/mesh/IK/附件切换）。

用法：
    python build_avatar_anim.py                 # 渲染所有没有动图的条目
    python build_avatar_anim.py --force         # 全部重渲
    python build_avatar_anim.py --kind 名片框    # 只做某一类
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import time


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
WEB = PROJ / "02_wiki/web"
sys.path.insert(0, str(WEB / "tools"))
from avatar_resolve import Resolver                # noqa: E402
import spine_render_fix as FX                      # noqa: E402
import numpy as np                                 # noqa: E402
from PIL import Image                              # noqa: E402

CAT = WEB / "data/boards/avatar_catalog.json"
SPINE_DIR = WEB / "assets/spine_live"
ANIM_DIR = WEB / "assets/avatar_anim"
FPS_FALLBACK = 10
MIN_BYTES = 1024


def log(msg):
    print("[anim] %s" % msg, flush=True)


def _atomic_save_image(img, path):
    """原子落盘（写临时文件再 replace）。

    ★ 并行渲染时同一骨架的多条头像可能同时取到同一张页贴图/同一份 atlas，
      直接写会互相覆盖出半截文件；原子替换可避免读到残缺产物。
    """
    tmp = path.with_name(path.name + ".%d.tmp" % os.getpid())
    img.save(tmp, format="PNG")
    os.replace(tmp, path)


def _atomic_write_text(path, text):
    tmp = path.with_name(path.name + ".%d.tmp" % os.getpid())
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def page_logical(base: str, page_name: str):
    """atlas 页名 → 客户端逻辑路径（页名自带目录时直接使用）。"""
    name = page_name.replace("\\", "/").strip()
    if "/" in name:
        return name
    d0 = base.rsplit("/", 1)[0] if "/" in base else ""
    return (d0 + "/" + name) if d0 else name


def page_cache_path(base: str, page_name: str):
    """页贴图的本地缓存文件（与 atlas 同目录、沿用页名）。"""
    name = page_name.replace("\\", "/").strip()
    if "/" in name:
        return SPINE_DIR / name
    d0 = base.rsplit("/", 1)[0] if "/" in base else ""
    return SPINE_DIR / ((d0 + "/" + name) if d0 else name)


def page_declared_sizes(atlas_text: str):
    """从 atlas 头解析每页声明的尺寸 → {页名: (w, h)}。"""
    sizes = {}
    cur = None
    for raw in atlas_text.splitlines():
        s = raw.strip()
        if not s:
            continue
        indented = raw.startswith((" ", "\t"))
        if not indented and s.lower().endswith((".png", ".jpg")):
            cur = s
            continue
        if cur and not indented and s.startswith("size:"):
            try:
                w, h = [int(x) for x in s[5:].split(",")]
                sizes[cur] = (w, h)
            except ValueError:
                pass
    return sizes


def _page_fingerprint(img):
    """页图的廉价指纹（64×64 缩略图），用于识别「多页被同一张图顶替」。"""
    small = np.asarray(img.convert("RGBA").resize((64, 64), Image.BILINEAR))
    return hash(small.tobytes())


def load_pages(res: Resolver, base: str, pages, sizes):
    """逐页解析页贴图 → ({页名: RGBA}, 缺失页名列表)。

    ★ 多页 atlas 必须每页单独取图。旧版把全部页映射到 base+".png"，
      导致 19 个多页骨架的后续页全部串成第一页（画面"乱七八糟"）。
    ★ 两条硬校验（2026-11-01）：
      · 页图尺寸必须与 atlas 头声明的 size 一致（尺寸不符 = 取到了别的图）
      · 同一 atlas 内不能出现两张完全相同的页图（= 该页从未单独解出，
        旧管线把第一页复制成了后续页）
      任一校验不过就记为缺失，绝不顶替。
    """
    img_of = {}
    missing = []
    fps = {}
    for pg in pages:
        logical = page_logical(base, pg)
        cache = page_cache_path(base, pg)
        img = None
        # 1) 新还原树（权威本地资源层：文件名即客户端逻辑路径）
        img = res.tree_image(logical)
        if img is not None:
            img = img.convert("RGBA")
            # 顺手落一份 png 缓存，便于离线复核与其它工具复用
            if not (cache.is_file() and cache.stat().st_size > MIN_BYTES):
                try:
                    cache.parent.mkdir(parents=True, exist_ok=True)
                    _atomic_save_image(img, cache)
                except Exception:                          # noqa: BLE001
                    pass
        # 2) 本地缓存（含旧版遗留的单页 base+".png"）
        if img is None and cache.is_file() and cache.stat().st_size > MIN_BYTES:
            try:
                img = Image.open(cache).convert("RGBA")
            except Exception:                              # noqa: BLE001
                img = None
        # 3) PE 索引 → PC 索引 → PC 校准表
        if img is None and res.fetch_png(logical, cache):
            try:
                img = Image.open(cache).convert("RGBA")
            except Exception:                              # noqa: BLE001
                img = None
        if img is None:
            missing.append(pg)
            continue
        declared = sizes.get(pg)
        if declared and img.size != declared:
            missing.append(pg)
            continue
        fp = _page_fingerprint(img)
        if fp in fps:
            # 与本 atlas 的某一页完全同图 → 该页实际没解出来
            missing.append(pg)
            continue
        fps[fp] = pg
        img_of[pg] = img
    return img_of, missing


_WORKER_RES = None


def _worker_res():
    """worker 进程内复用同一个 Resolver（每条任务都新建会重复扫索引）。"""
    global _WORKER_RES
    if _WORKER_RES is None:
        _WORKER_RES = Resolver()
    return _WORKER_RES


def _render_item(job):
    """渲染单条（可在子进程里跑）。只返回结果，不做任何全局写回。

    ★ 并行安全：每条只写自己的 assets/avatar_anim/<id>.png，文件名互不冲突；
      avatar_catalog.json 只由主进程最后统一写一次，worker 绝不碰。
    """
    it, size, frames, fmt = job
    iid = it["id"]
    base = it["spine_path"].strip().replace("\\", "/").rstrip("/")
    at_f = SPINE_DIR / (base + ".atlas")
    js_f = SPINE_DIR / (base + ".json")
    res = _worker_res()

    def bad(why):
        return {"ok": False, "id": iid, "base": base, "why": why}

    # 文本资源：优先本地缓存，否则回源
    atlas_text = None
    if at_f.is_file():
        atlas_text = at_f.read_text(encoding="utf-8", errors="ignore")
    else:
        t = res.fetch_text(base + ".atlas")
        if t is not None:
            at_f.parent.mkdir(parents=True, exist_ok=True)
            _atomic_write_text(at_f, t)
            atlas_text = t
    if atlas_text is None:
        return bad("atlas 取不到")
    if not js_f.is_file():
        t = res.fetch_text(base + ".json")
        if t is not None:
            js_f.parent.mkdir(parents=True, exist_ok=True)
            _atomic_write_text(js_f, t)
    if not js_f.is_file():
        return bad("json 取不到")
    # 页贴图：按 atlas 声明的每个页名逐页解析（还原树优先）
    try:
        skel, pages, _regions = FX.load_atlas(at_f)
    except Exception as ex:                            # noqa: BLE001
        return bad("解析失败 " + str(ex)[:50])
    img_of, missing = load_pages(res, base, pages, page_declared_sizes(atlas_text))
    if missing:
        return bad("页贴图缺失 " + ",".join(missing[:3]))
    if not img_of:
        return bad("贴图页读不出")
    aname = FX.anim_name(skel)
    if not aname:
        return bad("无动画")
    dur = FX.anim_duration(skel, aname) or 1.0
    cnt = max(6, min(frames, int(round(dur * FPS_FALLBACK))))
    try:
        # 名片框按画板裁（火焰溢出属正常），头像/头像框按覆盖率紧裁
        crop = "artboard" if it.get("kind") == "名片框" else "coverage"
        # ★ internal 必须跟着 size 一起提：render_frames 先在内部画布上把主体
        #   渲染到 internal 像素再缩到 box，默认 internal=420 —— 只调 box 的话
        #   输出长边永远卡在 ~429，放大看还是糊。
        frs, _meta = FX.render_frames(at_f, img_of, box=size, cnt=cnt,
                                      internal=max(420, size), aname=aname, crop=crop)
    except Exception as ex:                            # noqa: BLE001
        return bad("渲染失败 " + str(ex)[:50])
    if not frs:
        return bad("无帧")
    anim_rel = "assets/avatar_anim/%s.png" % iid
    if fmt == "webp":
        # ★ 2026-11-01：动图改 WebP（q90）。实测同分辨率体积只有 APNG 的 1/2.3，
        #   于是名片框才能从 384 提到 768 重渲（详情卡面约 614px，384 放大 1.6 倍
        #   就是用户说的"糊得离谱"），总体积反而不涨。
        #   首帧另存 PNG：没有静态边框的卡面主图仍用它，动图只负责悬停/详情播放。
        frs[0].save(ANIM_DIR / (iid + ".webp"), format="WEBP", save_all=True,
                    append_images=frs[1:], duration=int(round(dur * 1000 / cnt)),
                    loop=0, quality=90, method=4)
        frs[0].save(ANIM_DIR / (iid + ".png"), format="PNG")
        anim_rel = "assets/avatar_anim/%s.webp" % iid
    else:
        # ★ 绝不能量化：Pillow 的 quantize() 会破坏 APNG 多帧的透明通道与调色板，
        #   导致第 2~N 帧出现色块/反转（实测帧间差 75~120，视觉即"乱码"）。
        #   直接保存 RGBA 帧，重编码后帧间差为 0.0，画面完全正确。
        frs[0].save(ANIM_DIR / (iid + ".png"), format="PNG", save_all=True,
                    append_images=frs[1:], duration=int(round(dur * 1000 / cnt)),
                    loop=0, default_image=True)
    return {"ok": True, "id": iid, "base": base,
            "anim": anim_rel,
            "meta": {"spine": (skel.get("skeleton") or {}).get("spine"),
                     "anim": aname, "frames": cnt,
                     "duration": round(dur, 3), "source": base + ".atlas"}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", default="", help="逗号分隔；空=全部")
    ap.add_argument("--ids", default="", help="只渲染指定 id（逗号分隔，用于抽样核对）")
    ap.add_argument("--size", type=int, default=168)
    ap.add_argument("--format", choices=["png", "webp"], default="png",
                    help="动图容器：png=APNG（默认）；webp=动图 WebP（同分辨率约 1/2.3 体积）")
    ap.add_argument("--frames", type=int, default=24)
    ap.add_argument("--budget", type=float, default=5400.0)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--jobs", type=int, default=0,
                    help="并行进程数；0=按 CPU 自动（上限 24）")
    a = ap.parse_args()

    t0 = time.time()
    cat = json.loads(CAT.read_text(encoding="utf-8"))
    items = cat["items"]
    kinds = [k for k in a.kind.split(",") if k]
    want_ids = {x for x in a.ids.split(",") if x}

    SPINE_DIR.mkdir(parents=True, exist_ok=True)
    ANIM_DIR.mkdir(parents=True, exist_ok=True)

    targets = []
    for it in items:
        sp = (it.get("spine_path") or "").strip()
        if not sp:
            continue
        if kinds and it.get("kind") not in kinds:
            continue
        if want_ids and it["id"] not in want_ids:
            continue
        out = ANIM_DIR / (it["id"] + (".webp" if a.format == "webp" else ".png"))
        if not a.force and out.is_file() and out.stat().st_size > MIN_BYTES:
            continue
        targets.append(it)

    log("待渲染 %d 条（总条目 %d）" % (len(targets), len(items)))
    jobs = a.jobs or min(24, max(1, (os.cpu_count() or 4) // 2))
    done = fail = 0
    fails = []
    media = {}
    results = []

    def collect(r):
        nonlocal done, fail
        results.append(r)
        if r["ok"]:
            done += 1
            media[r["id"]] = (r["anim"], r["meta"])
        else:
            fail += 1
            fails.append((r["id"], r["base"], r["why"]))
        n = done + fail
        if n % 25 == 0:
            log("  %d/%d ｜ 成功 %d ｜ 失败 %d ｜ %.0fs"
                % (n, len(targets), done, fail, time.time() - t0))

    if jobs > 1 and len(targets) > 1:
        from concurrent.futures import ProcessPoolExecutor, as_completed
        log("并行 %d 进程（共 %s 逻辑核）" % (jobs, os.cpu_count()))
        pool = ProcessPoolExecutor(max_workers=jobs)
        try:
            futs = {pool.submit(_render_item, (it, a.size, a.frames, a.format)): it["id"]
                    for it in targets}
            for fut in as_completed(futs):
                collect(fut.result())
                if time.time() > t0 + a.budget:
                    log("到预算，取消剩余任务")
                    for f2 in futs:
                        f2.cancel()
                    break
        finally:
            pool.shutdown(wait=True, cancel_futures=True)
    else:
        for it in targets:
            if time.time() > t0 + a.budget:
                log("到预算，停在第 %d 条" % len(results))
                break
            collect(_render_item((it, a.size, a.frames, a.format)))
    log("完成：成功 %d ｜ 失败 %d ｜ %.0fs" % (done, fail, time.time() - t0))
    for f in fails[:15]:
        log("  失败 %s ｜ %s ｜ %s" % f)
    (PROJ / "01_索引与产物/30_分析/avatar_anim_fail_rescue.json").write_text(
        json.dumps(fails, ensure_ascii=False, indent=1), encoding="utf-8")
    if not a.dry:
        fail_ids = {f[0] for f in fails}
        for it in items:
            iid = it["id"]
            if iid in media:
                m = it.setdefault("_media", {})
                m["anim"], m["anim_meta"] = media[iid]
            elif iid in fail_ids:
                # ★ 失败条目不能继续挂着旧动图（旧产物大量残缺/串图）。
                #   清引用 + 删旧文件 → 看板回落静态图，且下次不带 --force 也会重试。
                m = it.get("_media") or {}
                m.pop("anim", None)
                m.pop("anim_meta", None)
                for ext in (".png", ".webp"):
                    p = ANIM_DIR / (iid + ext)
                    if p.is_file():
                        p.unlink()
        CAT.write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding="utf-8")
        log("已写回 %s" % CAT.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
