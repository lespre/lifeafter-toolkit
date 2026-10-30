# -*- coding: utf-8 -*-
"""头像板动态头像（Spine → APNG）构建：统一解析器三路回源版。

★ 与旧版 build_avatar_media.py --step anim 的差别
  旧版只查 PE（安卓测试服）索引，于是：
    · 422 条有 spine_path 的条目里，PE 缺 atlas/json/page 的 68 条直接放弃
      （其中 26 条名片框、29 条头像、15 条头像框 —— 这些在 **PC 包**里是齐的）
    · 页贴图找不到时用主贴图页顶替 → 渲染出的是别的图（"乱七八糟"的一部分）
  新版按 **PE 索引 → PC 索引 → PC 校准表** 三路回源，
  页贴图按「atlas 声明的页名 → 同名 .bc7/.ktx/.png」两条规则解析，
  拿不到就**如实放弃**（不做任何顶替）。

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
from PIL import Image                              # noqa: E402

CAT = WEB / "data/boards/avatar_catalog.json"
SPINE_DIR = WEB / "assets/spine_live"
ANIM_DIR = WEB / "assets/avatar_anim"
FPS_FALLBACK = 10
MIN_BYTES = 1024


def log(msg):
    print("[anim] %s" % msg, flush=True)


def page_candidates(base: str, atlas_text: str):
    """页贴图的候选逻辑路径（按优先级）。"""
    out = []
    d0 = base.rsplit("/", 1)[0] if "/" in base else ""
    # 1) atlas 声明的页名（Spine atlas 第一行就是页图文件名）
    for line in atlas_text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.lower().endswith((".png", ".jpg")):
            out.append((d0 + "/" + s) if d0 else s)
            break
    # 2) 与 atlas 同名的贴图页（PC 侧常以 .bc7 存）
    for e in (".bc7", ".ktx", ".png"):
        out.append(base + e)
    return out


def grab_page(res: Resolver, base: str, atlas_text: str, dst: pathlib.Path):
    """把页贴图落到本地（png）；返回 True/False。"""
    if dst.is_file() and dst.stat().st_size > MIN_BYTES:
        return True
    for logical in page_candidates(base, atlas_text):
        if res.fetch_png(logical, dst):
            return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", default="", help="逗号分隔；空=全部")
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

    SPINE_DIR.mkdir(parents=True, exist_ok=True)
    ANIM_DIR.mkdir(parents=True, exist_ok=True)

    targets = []
    for it in items:
        sp = (it.get("spine_path") or "").strip()
        if not sp:
            continue
        if kinds and it.get("kind") not in kinds:
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
        # 页贴图
        pg_f = SPINE_DIR / (base + ".png")
        if not grab_page(res, base, atlas_text, pg_f):
            fail += 1
            fails.append((iid, base, "贴图页取不到"))
            continue
        try:
            skel, pages, regions = FX.load_atlas(at_f)
        except Exception as ex:                            # noqa: BLE001
            fail += 1
            fails.append((iid, base, "解析失败 " + str(ex)[:50]))
            continue
        img_of = {}
        for pg in pages:
            src = pg_f if (pg_f.is_file() and not "/" in pg) else (SPINE_DIR / (base.rsplit("/", 1)[0] + "/" + pg if "/" in base else pg))
            if not src.is_file():
                cand = pg_f
                if cand.is_file():
                    src = cand
                else:
                    continue
            try:
                img_of[pg] = Image.open(src).convert("RGBA")
            except Exception:                              # noqa: BLE001
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
        CAT.write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding="utf-8")
        log("已写回 %s" % CAT.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
