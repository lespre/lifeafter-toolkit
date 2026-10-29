# -*- coding: utf-8 -*-
"""头像 / 头像框 / 名片框 板的媒体补齐与动态头像（Spine）预渲染。

三件事，各自独立可跑、可续跑（已落盘的产物直接跳过）：

  A. 挂图修正 —— 已落盘但没挂到 _media 的 PNG 补挂（assets/img_cache/avatar_catalog、
     assets/avatar_frames、assets/avatar_icons；顺序即优先级）
  B. 缺图补抓 —— 仍无图的条目，按 image_path → resource_path → detail_bg（各试 _b 变体）
     依次实拍，只写真命中的图，不猜、不用别名图兜底
  C. 动态头像预渲染 —— spine_path 指向的 Spine 资源（atlas/json/贴图页）抓到
     assets/spine_live/ 后，逐帧渲染成 APNG，落 assets/avatar_anim/<id>.png；
     卡面默认显示游戏内静态图，悬停 / 打开详情时播放动图

C 的抓取是批式的（按包聚合、每个包只枚举一次），否则 400 套资源要跑 40 分钟。

用法：
    python build_avatar_media.py --step bind
    python build_avatar_media.py --step fetch
    python build_avatar_media.py --step anim [--kind 头像] [--size 168] [--frames 24]
    python build_avatar_media.py --step anim --dry    # 只报覆盖度，不落盘
"""
from __future__ import annotations

import argparse
import io
import json
import pathlib
import sqlite3
import struct
import sys
import time
from collections import Counter, defaultdict

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
TOOLS = WEB / "tools"
BOARD = "avatar_catalog"
BOARD_JSON = WEB / "data/boards" / (BOARD + ".json")
BOARD_JS = WEB / "data/boards" / (BOARD + ".js")
CACHE = WEB / "assets/img_cache/avatar_catalog"
FRAMES_DIR = WEB / "assets/avatar_frames"
ICONS_DIR = WEB / "assets/avatar_icons"
ANIM_DIR = WEB / "assets/avatar_anim"
SPINE_DIR = WEB / "assets/spine_live"

GAME = pathlib.Path(r"E:/mrzh")
PKGDIR = PROJ / "01_索引与产物/源包/pe_gres_android"
NAMES_IDX = PROJ / "01_索引与产物/10_索引/names/fid_to_path_v2.jsonl"
PE_IDX = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"

sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))

FPS_FALLBACK = 10
MIN_BYTES = 1024


def log(s):
    print(s, flush=True)


def load_board():
    return json.loads(BOARD_JSON.read_text(encoding="utf-8"))


def save_board(d):
    BOARD_JSON.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    BOARD_JS.write_text("window.WIKI_BOARD_%s = %s;\n" % (BOARD, json.dumps(d, ensure_ascii=False)),
                        encoding="utf-8")


def has_img(it):
    return bool(((it.get("_media") or {}).get("images") or []))


def set_img(it, rel, label, note=None):
    m = it.setdefault("_media", {})
    m["images"] = [{"png": rel, "label": label}] + \
        [x for x in (m.get("images") or []) if x.get("png") != rel]
    m["total"] = len(m["images"])
    if note:
        m["note"] = note


# ---------------------------------------------------------------- A 挂图
def step_bind(d):
    hit = Counter()
    for it in d["items"]:
        if has_img(it):
            continue
        iid, ikey = it["id"], it.get("item_id", "")
        for f, rel, label in (
            (CACHE / (iid + ".png"), "assets/img_cache/avatar_catalog/%s.png" % iid, it.get("kind", "图标")),
            (FRAMES_DIR / (iid + ".png"), "assets/avatar_frames/%s.png" % iid, "名片框"),
            (ICONS_DIR / (ikey + ".png"), "assets/avatar_icons/%s.png" % ikey, "图标"),
        ):
            if f.is_file() and f.stat().st_size > 512:
                set_img(it, rel, label)
                hit[it.get("kind")] += 1
                break
    log("挂图补齐 %d 条 ｜ %s" % (sum(hit.values()), dict(hit)))
    return sum(hit.values())


# ---------------------------------------------------------------- B 补抓
def _variants(base: str):
    base = (base or "").strip().replace("\\", "/").lstrip("/")
    if not base:
        return []
    stem = base.rsplit(".", 1)[0] if "." in base.rsplit("/", 1)[-1] else base
    out = []
    for s in ([stem, "ui/" + stem] if not stem.lower().startswith("ui/") else [stem]):
        out.append(s)
        out.append(s + "_b")
    return list(dict.fromkeys(out))


def step_fetch(d, budget=900.0, apply=True):
    from toolkit_core import img_fetch
    t0 = time.time()
    pend = [it for it in d["items"] if not has_img(it)]
    log("待补图 %d 条" % len(pend))
    if not apply:
        return 0
    CACHE.mkdir(parents=True, exist_ok=True)
    ok, bad = 0, []
    for it in pend:
        if time.time() > t0 + budget:
            log("到预算，剩 %d 条下次再跑" % (len(pend) - ok - len(bad)))
            break
        dst = CACHE / (it["id"] + ".png")
        got = None
        for field in ("image_path", "resource_path", "detail_bg"):
            for v in _variants(it.get(field) or ""):
                try:
                    if img_fetch.export(v, dst):
                        got = (field, v)
                        break
                except Exception:                        # noqa: BLE001
                    continue
            if got:
                break
        if got and dst.is_file() and dst.stat().st_size > 512:
            set_img(it, "assets/img_cache/avatar_catalog/%s.png" % it["id"], it.get("kind", "图标"),
                    "来源 %s（%s 档）" % (got[0], got[1].rsplit("_", 1)[-1]))
            ok += 1
        else:
            bad.append((it["id"], it.get("image_path"), it.get("resource_path"), it.get("detail_bg")))
            if dst.is_file():
                dst.unlink()
    log("补到图 %d ｜ 仍未命中 %d" % (ok, len(bad)))
    (PROJ / "01_索引与产物/30_分析/avatar_media_fetch_fail.json").write_text(
        json.dumps(bad, ensure_ascii=False, indent=1), encoding="utf-8")
    return ok


# ---------------------------------------------------------------- B2 名片框归一
def _namecard_frame_src(it):
    """名片框正确边框源 = image_path（img_biankuang_*.png，真·中空边框）。
    resource_path 指向 img_biankuang_b_*.png（场景底图，不是边框）、detail_bg 是
    img_mingpian（场景）—— 二者都曾在线上被误挂成主图，导致「名片框=风景照」的 bug。"""
    ip = (it.get("image_path") or "").strip().replace("\\", "/").lstrip("/")
    if ip:
        return ip
    rp = (it.get("resource_path") or "").strip().replace("\\", "/").lstrip("/")
    if rp:
        # 兜底：把 _b_ 变体还原成边框名（img_biankuang_b_06_01 → img_biankuang_06_01）
        return rp.replace("_b_", "_") if "_b_" in rp else rp
    return ""


def step_namecard(d, budget=900.0):
    """名片框主图统一为「边框图」(image_path → img_biankuang_*.png)，
    覆盖历史误挂的场景底图（resource_path/detail_bg）。"""
    from toolkit_core import img_fetch
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    nc = [it for it in d["items"] if it.get("kind") == "名片框"]
    log("名片框 %d 张，开始以边框图(image_path)归一主图" % len(nc))
    done = fetched = fb = 0
    for it in nc:
        if time.time() > t0 + budget:
            log("到预算，剩 %d 张下次再跑" % (len(nc) - done - fb))
            break
        iid = it["id"]
        m = it.setdefault("_media", {})
        src = _namecard_frame_src(it)
        cand = FRAMES_DIR / (iid + ".png")
        cur_base = (((m.get("images") or [{}])[0] or {}).get("base")) if m.get("images") else None
        # 强制重取：文件缺失，或当前主图来源不是边框图（仍是误挂的场景底图）
        need = (not (cand.is_file() and cand.stat().st_size > 512)) or (cur_base != src)
        if need and src:
            try:
                img_fetch.export(src, cand)
            except Exception:                      # noqa: BLE001
                pass
            if cand.is_file() and cand.stat().st_size > 512:
                fetched += 1
        if cand.is_file() and cand.stat().st_size > 512:
            m["images"] = [{"png": "assets/avatar_frames/%s.png" % iid,
                            "label": "名片框", "base": src}]
            m["total"] = 1
            done += 1
        else:
            m.pop("images", None)
            m["total"] = 0
    log("名片框主图：边框 %d（新取 %d）" % (done, fetched))
    return done


# ---------------------------------------------------------------- 批式取包
class Packs:
    """按包聚合的随机读取：每个包只枚举一次行数表，之后按 row 直接取 payload。"""

    def __init__(self):
        try:
            from toolkit_core import android_gpk as AG
        except Exception:                                # noqa: BLE001
            import android_gpk as AG                     # type: ignore
        self.AG = AG
        self._opened = {}

    def _open(self, path: pathlib.Path):
        key = str(path)
        if key in self._opened:
            return self._opened[key]
        blob = path.read_bytes()
        _rec, spans, factory = self.AG.open_blocks(str(path))
        meta = {}
        for row, _fid, off, packed, decoded, flag in factory():
            meta[row] = (off, packed, decoded, flag)
        self._opened[key] = (blob, spans, meta)
        return self._opened[key]

    def payload(self, path: pathlib.Path, row: int):
        try:
            blob, spans, meta = self._open(path)
        except Exception:                                # noqa: BLE001
            return None
        m = meta.get(row)
        if not m:
            return None
        off, packed, decoded, flag = m
        h = self.AG._base_of(spans, row) + off
        if h + 20 > len(blob):
            return None
        hp, hd, _c1, _c2, hf = struct.unpack_from("<5I", blob, h)
        if (hp, hd, hf) != (packed, decoded, flag):
            return None
        try:
            return self.AG.decompress(blob[h + 20: h + 20 + packed], flag, decoded)
        except Exception:                                # noqa: BLE001
            return None

    def image(self, path: pathlib.Path, row: int):
        """取贴图行 → RGBA 数组；失败返回 None。"""
        data = self.payload(path, row)
        if not data:
            return None
        AG = self.AG
        try:
            if data.startswith(b"\xabKTX"):
                info = AG.parse_ktx(data)
                if not info:
                    return None
                return AG.decode_image({"kind": "ktx", "data": data, "info": info})
            if data.startswith(b"DDS "):
                return AG.decode_image({"kind": "dds", "data": data})
            if data.startswith(b"\x89PNG"):
                from PIL import Image
                return Image.open(io.BytesIO(data)).convert("RGBA")
        except Exception:                                # noqa: BLE001
            return None
        return None


def load_names_subset(suffixes):
    """names 索引里只抽指定后缀的 path → (container, row)。"""
    out = {}
    with NAMES_IDX.open("r", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            if not line:
                continue
            i = line.find('"path": "')
            if i < 0 or not any(s in line for s in suffixes):
                continue
            try:
                r = json.loads(line)
            except Exception:                            # noqa: BLE001
                continue
            p = (r.get("path") or "").replace("\\", "/").lstrip("/")
            if not p.endswith(suffixes):
                continue
            if r.get("row") is None:
                continue
            out.setdefault(p, (r.get("container") or "", int(r["row"])))
    return out


# ---------------------------------------------------------------- C 动画
def _resolve_page(con, base, page_name, primary):
    """贴图页逻辑路径 → (pack,row)；找不到时回退到主贴图页。"""
    from toolkit_core.path_fid import fid_of
    stem = page_name.rsplit(".", 1)[0]
    if "/" in base and "/" not in stem:
        logical = base.rsplit("/", 1)[0] + "/" + stem
    else:
        logical = stem
    if logical == base:
        return primary
    fid = "%016X" % fid_of(logical + ".ktx")
    row = con.execute("select pack,row from rows where fid=? limit 1", (fid,)).fetchone()
    return (PKGDIR / row[0], int(row[1])) if row else primary


def step_anim(d, kinds=None, size=168, frames=24, budget=5400.0, dry=False, force=False):
    from toolkit_core.path_fid import fid_of
    import spine_render_fix as FX
    from PIL import Image
    import numpy as np

    t0 = time.time()
    targets = [it for it in d["items"]
               if (it.get("spine_path") or "").strip()
               and (not kinds or it.get("kind") in kinds)]
    log("有 spine_path 的条目 %d 条（本次范围）" % len(targets))

    name_map = load_names_subset((".atlas", ".json"))
    log("names 索引载入 .atlas/.json 条目 %d" % len(name_map))
    con = sqlite3.connect("file:%s?mode=ro" % str(PE_IDX).replace("\\", "/"), uri=True)
    plan, nopage, noatlas = [], Counter(), Counter()
    for it in targets:
        base = it["spine_path"].strip().replace("\\", "/").rstrip("/")
        a = name_map.get(base + ".atlas")
        j = name_map.get(base + ".json")
        if not (a and j):
            noatlas[it.get("kind")] += 1
            continue
        fid = "%016X" % fid_of(base + ".ktx")
        row = con.execute("select pack,row from rows where fid=? limit 1", (fid,)).fetchone()
        if not row:
            nopage[it.get("kind")] += 1
            continue
        plan.append({
            "it": it, "base": base,
            "atlas": (GAME / a[0].replace("\\", "/").lstrip("/"), a[1]) if a[0] else None,
            "json": (GAME / j[0].replace("\\", "/").lstrip("/"), j[1]) if j[0] else None,
            "page": (PKGDIR / row[0], int(row[1])),
        })
    log("可渲染 %d 条 ｜ 索引无 atlas/json %s ｜ 索引无主贴图页 %s"
        % (len(plan), dict(noatlas), dict(nopage)))
    if dry:
        return 0

    packs = Packs()
    SPINE_DIR.mkdir(parents=True, exist_ok=True)
    ANIM_DIR.mkdir(parents=True, exist_ok=True)
    done, skip, fail = 0, 0, []

    def grab_text(job):
        for key, fname in (("atlas", ".atlas"), ("json", ".json")):
            dst = SPINE_DIR / (job["base"] + fname)
            if dst.is_file():
                continue
            src = job[key]
            if not src:
                continue
            b = packs.payload(*src)
            if b:
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(b.lstrip(b"\x00") if b[:1] in (b"\n", b"{") else b)

    def grab_page(job, page_name):
        """返回落盘路径或 None。"""
        if "/" in page_name:
            logical = page_name.rsplit(".", 1)[0]
        elif "/" in job["base"]:
            logical = job["base"].rsplit("/", 1)[0] + "/" + page_name.rsplit(".", 1)[0]
        else:
            logical = page_name.rsplit(".", 1)[0]
        dst = SPINE_DIR / (logical + ".png")
        if dst.is_file() and dst.stat().st_size > MIN_BYTES:
            return dst
        row = job["page"] if logical == job["base"] else _resolve_page(
            con, job["base"], page_name, job["page"])
        arr = packs.image(*row)
        if arr is None:
            return None
        dst.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(np.asarray(arr, dtype=np.uint8), "RGBA").save(dst)
        return dst

    for n, job in enumerate(plan, 1):
        if time.time() > t0 + budget:
            log("到预算（%d/%d），剩下的下次续跑" % (n - 1, len(plan)))
            break
        it, base = job["it"], job["base"]
        iid = it["id"]
        out = ANIM_DIR / (iid + ".png")
        grab_text(job)
        at_f, js_f = SPINE_DIR / (base + ".atlas"), SPINE_DIR / (base + ".json")
        if not (at_f.is_file() and js_f.is_file()):
            fail.append((iid, base, "atlas/json 取不到"))
            continue
        try:
            skel, pages, regions = FX.load_atlas(at_f)
        except Exception as ex:                            # noqa: BLE001
            fail.append((iid, base, "解析失败 " + str(ex)[:60]))
            continue
        img_of = {}
        for pg in pages:
            p = grab_page(job, pg)
            if p is None:
                continue
            try:
                img_of[pg] = Image.open(p).convert("RGBA")
            except Exception:                              # noqa: BLE001
                continue
        if not img_of:
            fail.append((iid, base, "贴图页取不到"))
            continue
        aname = FX.anim_name(skel)
        if not aname:
            fail.append((iid, base, "无动画"))
            continue
        dur = FX.anim_duration(skel, aname) or 1.0
        cnt = max(6, min(frames, int(round(dur * FPS_FALLBACK))))
        if (not force) and out.is_file() and out.stat().st_size > MIN_BYTES:
            skip += 1
        else:
            frs, _meta = FX.render_frames(at_f, img_of, box=size, cnt=cnt, aname=aname)
            if not frs:
                fail.append((iid, base, "无帧"))
                continue
            q = [f.quantize(colors=180, method=Image.FASTOCTREE) for f in frs]
            q[0].save(out, format="PNG", save_all=True, append_images=q[1:],
                      duration=int(round(dur * 1000 / cnt)), loop=0, default_image=True)
            done += 1
        m = it.setdefault("_media", {})
        m["anim"] = "assets/avatar_anim/%s.png" % iid
        m["anim_meta"] = {"spine": (skel.get("skeleton") or {}).get("spine"),
                          "anim": aname, "frames": cnt,
                          "duration": round(dur, 3), "source": base + ".atlas"}
        if not (m.get("images") or []):
            f0 = ANIM_DIR / (iid + "_f0.png")
            if not f0.is_file():
                Image.open(out).convert("RGBA").save(f0)
            set_img(it, "assets/avatar_anim/%s_f0.png" % iid, it.get("kind", "动图首帧"),
                    "静态图缺失，显示动图首帧")
        if n % 50 == 0:
            log("  %d/%d ｜ 新渲染 %d ｜ 复用 %d ｜ %.0fs"
                % (n, len(plan), done, skip, time.time() - t0))
    log("动画：新渲染 %d ｜ 复用 %d ｜ 失败 %d ｜ %.0fs"
        % (done, skip, len(fail), time.time() - t0))
    for f in fail[:10]:
        log("  失败 %s ｜ %s ｜ %s" % f)
    (PROJ / "01_索引与产物/30_分析/avatar_anim_fail.json").write_text(
        json.dumps(fail, ensure_ascii=False, indent=1), encoding="utf-8")
    return done


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", default="bind", choices=["bind", "fetch", "anim", "namecard", "all"])
    ap.add_argument("--kind", default="")
    ap.add_argument("--size", type=int, default=168)
    ap.add_argument("--frames", type=int, default=24)
    ap.add_argument("--budget", type=float, default=5400.0)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--force", action="store_true",
                   help="强制重渲染（忽略已存在的 avatar_anim/<id>.png）")
    a = ap.parse_args()

    d = load_board()
    before = sum(1 for x in d["items"] if has_img(x))
    kinds = [k for k in a.kind.split(",") if k] or None

    if a.step in ("bind", "all"):
        step_bind(d)
    if a.step in ("fetch", "all"):
        step_fetch(d, budget=a.budget, apply=not a.dry)
    if a.step in ("namecard", "all"):
        step_namecard(d, budget=a.budget)
    if a.step in ("anim", "all"):
        step_anim(d, kinds=kinds, size=a.size, frames=a.frames, budget=a.budget,
                  dry=a.dry, force=a.force)

    after = sum(1 for x in d["items"] if has_img(x))
    nanim = sum(1 for x in d["items"] if (x.get("_media") or {}).get("anim"))
    d["meta"].setdefault("state_summary", {}).update(
        {"有图": after, "缺图": len(d["items"]) - after, "有动画": nanim})
    if nanim:
        d["meta"]["note"] = (d["meta"].get("note", "").split("｜")[0].strip()
                             + " ｜ 动态头像由 spine_path 的 Spine 资源预渲染为 APNG"
                               "（卡面默认游戏内静态图，悬停/开详情播放）；"
                               "贴图页在包索引里无名的条目不出动图")
    save_board(d)
    log("卡片有图 %d/%d（前 %d）｜ 有动画 %d" % (after, len(d["items"]), before, nanim))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
