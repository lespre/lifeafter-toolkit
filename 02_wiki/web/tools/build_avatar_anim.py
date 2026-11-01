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
                    img.save(cache)
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", default="", help="逗号分隔；空=全部")
    ap.add_argument("--ids", default="", help="只渲染指定 id（逗号分隔，用于抽样核对）")
    ap.add_argument("--size", type=int, default=168)
    ap.add_argument("--frames", type=int, default=24)
    ap.add_argument("--budget", type=float, default=5400.0)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    t0 = time.time()
    res = Resolver()
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
        out = ANIM_DIR / (it["id"] + ".png")
        if not a.force and out.is_file() and out.stat().st_size > MIN_BYTES:
            continue
        targets.append(it)

    log("待渲染 %d 条（总条目 %d）" % (len(targets), len(items)))
    done = fail = 0
    fails = []
    for n, it in enumerate(targets, 1):
        if time.time() > t0 + a.budget:
            log("到预算，停在第 %d 条" % n)
            break
        iid = it["id"]
        base = it["spine_path"].strip().replace("\\", "/").rstrip("/")
        at_f = SPINE_DIR / (base + ".atlas")
        js_f = SPINE_DIR / (base + ".json")
        # 文本资源：优先本地缓存，否则回源
        atlas_text = None
        if at_f.is_file():
            atlas_text = at_f.read_text(encoding="utf-8", errors="ignore")
        else:
            t = res.fetch_text(base + ".atlas")
            if t is not None:
                at_f.parent.mkdir(parents=True, exist_ok=True)
                at_f.write_text(t, encoding="utf-8")
                atlas_text = t
        if atlas_text is None:
            fail += 1
            fails.append((iid, base, "atlas 取不到"))
            continue
        if not js_f.is_file():
            t = res.fetch_text(base + ".json")
            if t is not None:
                js_f.parent.mkdir(parents=True, exist_ok=True)
                js_f.write_text(t, encoding="utf-8")
        if not js_f.is_file():
            fail += 1
            fails.append((iid, base, "json 取不到"))
            continue
        # 页贴图：按 atlas 声明的每个页名逐页解析（还原树优先）
        try:
            skel, pages, regions = FX.load_atlas(at_f)
        except Exception as ex:                            # noqa: BLE001
            fail += 1
            fails.append((iid, base, "解析失败 " + str(ex)[:50]))
            continue
        img_of, missing = load_pages(res, base, pages, page_declared_sizes(atlas_text))
        if missing:
            fail += 1
            fails.append((iid, base, "页贴图缺失 " + ",".join(missing[:3])))
            continue
        if not img_of:
            fail += 1
            fails.append((iid, base, "贴图页读不出"))
            continue
        aname = FX.anim_name(skel)
        if not aname:
            fail += 1
            fails.append((iid, base, "无动画"))
            continue
        dur = FX.anim_duration(skel, aname) or 1.0
        cnt = max(6, min(a.frames, int(round(dur * FPS_FALLBACK))))
        try:
            frs, meta = FX.render_frames(at_f, img_of, box=a.size, cnt=cnt, aname=aname)
        except Exception as ex:                            # noqa: BLE001
            fail += 1
            fails.append((iid, base, "渲染失败 " + str(ex)[:50]))
            continue
        if not frs:
            fail += 1
            fails.append((iid, base, "无帧"))
            continue
        out = ANIM_DIR / (iid + ".png")
        # ★ 绝不能量化：Pillow 的 quantize() 会破坏 APNG 多帧的透明通道与调色板，
        #   导致第 2~N 帧出现色块/反转（实测帧间差 75~120，视觉即"乱码"）。
        #   直接保存 RGBA 帧，重编码后帧间差为 0.0，画面完全正确。
        frs[0].save(out, format="PNG", save_all=True, append_images=frs[1:],
                    duration=int(round(dur * 1000 / cnt)), loop=0, default_image=True)
        m = it.setdefault("_media", {})
        m["anim"] = "assets/avatar_anim/%s.png" % iid
        m["anim_meta"] = {"spine": (skel.get("skeleton") or {}).get("spine"),
                          "anim": aname, "frames": cnt,
                          "duration": round(dur, 3), "source": base + ".atlas"}
        done += 1
        if n % 25 == 0:
            log("  %d/%d ｜ 成功 %d ｜ 失败 %d ｜ %.0fs" % (n, len(targets), done, fail, time.time() - t0))

    log("完成：成功 %d ｜ 失败 %d ｜ %.0fs" % (done, fail, time.time() - t0))
    for f in fails[:15]:
        log("  失败 %s ｜ %s ｜ %s" % f)
    (PROJ / "01_索引与产物/30_分析/avatar_anim_fail_rescue.json").write_text(
        json.dumps(fails, ensure_ascii=False, indent=1), encoding="utf-8")
    if not a.dry:
        # ★ 失败条目不能继续挂着旧动图（旧产物大量残缺/串图）。
        #   清引用 + 删旧文件 → 看板回落静态图，且下次不带 --force 也会重试。
        for it in items:
            if it["id"] not in {f[0] for f in fails}:
                continue
            m = it.get("_media") or {}
            m.pop("anim", None)
            m.pop("anim_meta", None)
            p = ANIM_DIR / (it["id"] + ".png")
            if p.is_file():
                p.unlink()
        CAT.write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding="utf-8")
        log("已写回 %s" % CAT.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
