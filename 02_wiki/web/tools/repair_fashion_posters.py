# -*- coding: utf-8 -*-
r"""修时装板「男女角色取图不完整」：卡面引用的 png 已经不在磁盘上（断链）。

现象（2026-10-29 实测）：
  · 372 张卡各有一条 `_media.images` 指向 `assets/fashion_posters/<id>_m.png`，
    但该文件不存在 —— 浏览器 img 404，卡面只剩女装一张，看起来"男女取图不完整"。
  · 同一张男图往往另有落盘文件（`<id>.png` / `<id>_1.png`，或被 refs 收录），
    只是 JSON 里的路径漂了（fill_fashion_male 写 `_m.png`，重建按序号写 `_1.png`）。

修法（按优先级，全部只动数据，不删已有好图）：
  1) 自身已有同 base 的落盘文件（images 其它条目 / icons_all.png）→ 直接改指向
  2) assets/fashion_icon_refs/<base>{,_b,_s,_max}.png → 复制到 fashion_posters
  3) PE 包实导（缓存整包，按 row 取）→ PC 包实导
  4) 都拿不到 → 从 images 移除，记进 _media.missing（带性别），不再留断链

顺带：
  · label 归一到「男 / 女」（按文件名判性别，判不出的留「图示N」）
  · 同 base 去重（_b / _s 只算尺寸档），女前男后
  · 回写 icon_count / _media.total / icon_state，并同步 .js（页面读的是 .js）

用法：
  python repair_fashion_posters.py --dry       # 只报数
  python repair_fashion_posters.py             # 落盘
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import sys
import time
from collections import Counter

PROJ = pathlib.Path("E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
BOARDS = WEB / "data/boards"
BOARD_JSON = BOARDS / "fashion_wardrobe.json"
BOARD_JS = BOARDS / "fashion_wardrobe.js"
POSTERS = WEB / "assets/fashion_posters"
REFS = WEB / "assets/fashion_icon_refs"
#: item_icon 全量扁平导出库（文件名 = 完整路径把 / 换成 _）。
#: 2026-10-29 发现：这里早就有图，但取图链路只查 REFS，导致「图在磁盘上却标缺图」。
FULL = WEB / "assets/item_icons_full"

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))

SIZE = re.compile(r"_(b|s|max|mid|max2|sq_b|sq_s)$", re.I)
EXT = re.compile(r"\.(ktx|dds|png|bc7|jpg)$", re.I)
G_PATH = re.compile(r"^icon_(?:b|h|bag|light|suit)_([fm])_")
G_NUM = re.compile(r"^icon_\d+_([12])(?:_|$)")


def nb(base: str) -> str:
    """归一 base：去目录/扩展名/尺寸档。"""
    b = str(base or "").split("/")[-1]
    b = EXT.sub("", b)
    return SIZE.sub("", b)


def gender_of(base: str) -> str:
    """按图标名判性别（部位+性别式 / 编号式 两套命名）。"""
    b = nb(base)
    m = G_PATH.match(b)
    if m:
        return "男" if m.group(1) == "m" else "女"
    m = G_NUM.match(b)
    if m:
        return "男" if m.group(1) == "1" else "女"
    return ""


def refs_hit(base: str):
    stem = nb(base)
    for suf in ("_b", "_s", "", "_max"):
        p = REFS / (stem + suf + ".png")
        if p.is_file() and p.stat().st_size > 512:
            return p
    return None


def flat_name(path: str) -> str:
    """item_icons_full 的落盘名：完整路径的分隔符换成 _（如 ui_item_icon_icon_h_f_3733001.png）。

    注意不能用 nb()：那个函数会把目录一起砍掉，只留文件名。
    """
    p = str(path or "").replace("\\", "/")
    p = EXT.sub("", p)
    p = SIZE.sub("", p)
    return p.replace("/", "_") + ".png"


def local_hit(path: str):
    """本地已有同一张图：先 item_icons_full（按完整路径），再 refs（按文件名）。

    两张库都只认「>512 字节」的真图，避免把空壳/占位当成功。
    只给了文件名（老卡数据 base 是短名）时，补 ui/item_icon/ 前缀再查一遍。
    """
    raw = str(path or "").replace("\\", "/")
    cands = [flat_name(raw)]
    if "/" not in raw:
        cands.insert(0, flat_name("ui/item_icon/" + raw))
    for c in cands:
        p = FULL / c
        if p.is_file() and p.stat().st_size > 512:
            return p
    return refs_hit(path)


def _cache_pc_csv() -> None:
    """pc_fetch.load_csv 每次 resolve 未命中都要把 CSV 重解析一遍（几千万行级），
    批量补图会被拖死 —— 这里在进程内缓存一次（不改共享库）。"""
    try:
        import pc_fetch
    except Exception:
        return
    if getattr(pc_fetch, "_csv_memo_on", False):
        return
    orig = pc_fetch.load_csv
    memo: dict = {}

    def wrapped():
        if "v" not in memo:
            memo["v"] = orig()
        return memo["v"]

    pc_fetch.load_csv = wrapped
    pc_fetch._csv_memo_on = True


class PackExporter:
    """PE → PC 实导（不缓存整包：单张导出够快，缓存整包反而吃内存）。"""

    def __init__(self):
        self._pe = None
        self._pc = None
        _cache_pc_csv()

    def _mods(self):
        if self._pe is None:
            try:
                import pe_fetch
                self._pe = pe_fetch
            except Exception:
                self._pe = False
        if self._pc is None:
            try:
                import pc_fetch
                self._pc = pc_fetch
            except Exception:
                self._pc = False
        return self._pe, self._pc

    def export(self, path: str, dst: pathlib.Path) -> str:
        """按「完整图标路径」实导。

        2026-10-29 修：原来把 base 用 nb() 砍成纯文件名再调 pe_fetch.export，
        而 pe_fetch.resolve 是拿 fid_of(完整路径) 查索引的 —— 短名算出的 fid 永远
        对不上，于是「包里明明有图」也被判成缺图（星紫迷踪/炽翼使徒 等 6 张卡）。
        现在保留目录，并补 _b/_s/无后缀 三档。
        """
        p = str(path or "").replace("\\", "/").strip()
        if not p:
            return ""
        p = EXT.sub("", p)
        p = SIZE.sub("", p)
        if "/" not in p:
            # 只给了文件名（卡面旧数据里只有 base）→ 补 UI 图标目录
            p = "ui/item_icon/" + p
        pe, pc = self._mods()
        for suf in ("_b", "_s", ""):
            for name, mod in (("PE", pe), ("PC", pc)):
                if not mod:
                    continue
                try:
                    if mod.export(p + suf, dst) and dst.is_file() and dst.stat().st_size > 512:
                        return name
                except Exception:
                    pass
                if dst.exists():
                    dst.unlink()
        return ""


def fill_missing_slots(it: dict, exp: "PackExporter", dry: bool, stat: Counter) -> None:
    """把 icons_all 里登记了、但卡上没有图的槽位补上；补不到的记进 _media.missing。"""
    media = it.setdefault("_media", {})
    imgs = [x for x in (media.get("images") or []) if isinstance(x, dict)]
    have = {nb(x.get("base")) for x in imgs}
    gaps = [g for g in (media.get("missing") or []) if isinstance(g, dict)]
    cid = it["id"]
    for ic in (it.get("icons_all") or []):
        key = nb(ic.get("path"))
        if not key or key in have:
            continue
        g = gender_of(key) or str(ic.get("gender") or "")
        rp = local_hit(ic.get("path") or key)
        dst = POSTERS / ("%s_%s.png" % (cid, "m" if g == "男" else "f"))
        n = 2
        while dst.exists():
            dst = POSTERS / ("%s_%s%d.png" % (cid, "m" if g == "男" else "f", n))
            n += 1
        src = ""
        if rp:
            if not dry:
                POSTERS.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(rp, dst)
            src = rp.parent.name if rp.parent in (REFS, FULL) else "本地图库"
        elif not dry:
            src = exp.export(ic.get("path") or key, dst)
        if src:
            imgs.append({"png": str(dst.relative_to(WEB)).replace("\\", "/"),
                         "base": key + ("_b" if src.startswith("PE") or src == "PC" else ""),
                         "label": g or "图示%d" % (len(imgs) + 1),
                         "source": "性别补图（%s）· %s" % (src, key)})
            have.add(key)
            stat["槽位补图"] += 1
        else:
            if dst.exists():
                dst.unlink()
            gaps.append({"base": key, "gender": g, "why": "PE/PC/refs 均无此图"})
            stat["槽位仍缺"] += 1
    imgs.sort(key=lambda x: 0 if x.get("label") == "女" else (1 if x.get("label") == "男" else 2))
    media["images"] = imgs
    media["total"] = len(imgs)
    it["icon_count"] = len(imgs)
    if imgs:
        it["icon_state"] = "有图"
    gaps = dedup_gaps(gaps)
    if gaps:
        media["missing"] = gaps
        it["gender_icon_state"] = "缺%s图" % ("/".join(sorted({g["gender"] for g in gaps if g["gender"]})) or "图")


def load_board():
    return json.loads(BOARD_JSON.read_text(encoding="utf-8"))


def save_board(d: dict) -> None:
    BOARD_JSON.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    BOARD_JS.write_text("window.WIKI_BOARD_fashion_wardrobe = "
                        + json.dumps(d, ensure_ascii=False, indent=1) + ";\n",
                        encoding="utf-8")


UNISEX_FAM = ("bag", "light", "suit")   # 板上口径：背包/光源/整套 同一模型男女通用


FAM_RX = re.compile(r"^icon_([a-z]+)_([fm])_(\d+)")


def fam_of(base: str):
    """→ (族, 性别, 编号)；命名不是「部位+性别」式时返回 ("", "", "")。"""
    m = FAM_RX.match(nb(base))
    return m.groups() if m else ("", "", "")


def reuse_unisex(it: dict, dry: bool, stat: Counter) -> None:
    """缺的性别槽属于「男女通用」族（背包/光源/整套）时，直接复用同模型的另一性别图。

    板 meta 里的口径：背包/挂件不分性别（同一模型男女通用），不追男图属正常。
    这类槽位标成「缺图」是噪音 —— 复用它有的那张，label 上照性别写。
    """
    media = it.get("_media") or {}
    gaps = [g for g in (media.get("missing") or []) if isinstance(g, dict)]
    if not gaps:
        return
    imgs = [x for x in (media.get("images") or []) if isinstance(x, dict)]
    if not imgs:
        return
    before = len(imgs)
    rest = []
    for g in gaps:
        fam, _g, num = fam_of(g.get("base") or "")
        mate = None
        if fam in UNISEX_FAM and num:
            for im in imgs:
                f2, _g2, n2 = fam_of(im.get("base") or "")
                if f2 == fam and n2 == num and im.get("png"):
                    mate = im
                    break
        if not mate:
            rest.append(g)
            continue
        imgs.append({"png": mate["png"], "base": g.get("base"),
                     "label": g.get("gender") or "图示",
                     "source": "男女通用（%s）→ 复用同模型另一性别图" % fam,
                     "unisex_from": mate.get("base")})
        stat["通用族复用"] += 1
    if len(imgs) > before and not dry:
        imgs.sort(key=lambda x: 0 if x.get("label") == "女" else (1 if x.get("label") == "男" else 2))
        media["images"] = imgs
        media["total"] = len(imgs)
        it["icon_count"] = len(imgs)
        it["icon_state"] = "有图"
        it["_media"] = media
    if rest:
        media["missing"] = rest
        if not dry:
            it["gender_icon_state"] = "缺%s图" % ("/".join(
                sorted({g["gender"] for g in rest if g["gender"]})) or "图")
    else:
        media.pop("missing", None)
        if not dry:
            it.pop("gender_icon_state", None)


def mark_gender_gaps(it: dict, dry: bool, stat: Counter) -> None:
    """表里标了「女/男」，卡上却只取到一种性别的图 —— 把缺口标出来，别让卡面假装完整。

    这类卡的 icons_all 往往只登记了存在的那一条路径，所以前面几段扫不出来。
    """
    g = str(it.get("gender") or "")
    if "男" not in g or "女" not in g:
        return
    media = it.get("_media") or {}
    imgs = [x for x in (media.get("images") or []) if isinstance(x, dict)]
    if not imgs:
        return
    have = {gender_of(x.get("base")) for x in imgs}
    have.discard("")
    if not have or len(have) >= 2:
        return
    miss = [x for x in ("女", "男") if x not in have]
    gaps = [x for x in (media.get("missing") or []) if isinstance(x, dict)]
    known = {(x.get("gender"), x.get("base")) for x in gaps}
    for mg in miss:
        if (mg, None) in known:
            continue
        gaps.append({"base": None, "gender": mg,
                     "why": "表里标%s款，但 PE/PC/refs 都没有这张图标" % mg})
        stat["性别缺口标记"] += 1
    if not dry:
        media["missing"] = gaps
        it["_media"] = media
        it["gender_icon_state"] = "缺%s图" % ("/".join(
            sorted({x["gender"] for x in gaps if x.get("gender")})) or "图")


def dedup_gaps(gaps):
    """缺口去重：同一 (icon base, 性别) 只留一条。

    repair 脚本是反复可跑的，旧版缺失列表是 append 的 —— 每跑一次就翻倍
    （2026-10-29 实测 742 → 1487），卡面角标也会变成「缺女图 · 2」。
    """
    out, seen = [], set()
    for g in gaps:
        key = (nb(g.get("base") or ""), str(g.get("gender") or ""))
        if key in seen:
            continue
        seen.add(key)
        out.append(g)
    return out


def prune_gaps(it: dict, dry: bool) -> None:
    """图片已经补上了对应性别 → 把残留的缺口标记删掉。

    fill_missing_slots / mark_gender_gaps 只负责「加」，不负责「减」；
    补图成功后旧的 `{base: null, gender: 女}` 还留着，卡面就一直显示「缺女图」。
    """
    media = it.get("_media") or {}
    gaps = [g for g in (media.get("missing") or []) if isinstance(g, dict)]
    if not gaps:
        return
    imgs = [x for x in (media.get("images") or []) if isinstance(x, dict)]
    have_bases = {nb(x.get("base")) for x in imgs if x.get("base")}
    have_gender = set()
    for x in imgs:
        g = gender_of(x.get("base")) or str(x.get("label") or "")
        if g in ("女", "男"):
            have_gender.add(g)
    keep = []
    for g in gaps:
        b = nb(g.get("base") or "")
        if b and b in have_bases:
            continue
        if not b and str(g.get("gender") or "") in have_gender:
            continue
        keep.append(g)
    # 具体槽优先：某性别已经有具体图标名的缺槽时，删掉同性别 base=null 的泛化记录，
    # 否则一张卡会同时挂着「缺女图（泛化）」和「icon_xxx 缺（具体）」两条，重复计数。
    with_base = {str(g.get("gender") or "") for g in keep if g.get("base")}
    keep = [g for g in keep if g.get("base") or str(g.get("gender") or "") not in with_base]
    keep = dedup_gaps(keep)
    if len(keep) == len(gaps):
        return
    if not dry:
        if keep:
            media["missing"] = keep
            it["gender_icon_state"] = "缺%s图" % ("/".join(
                sorted({x["gender"] for x in keep if x.get("gender")})) or "图")
        else:
            media.pop("missing", None)
            it.pop("gender_icon_state", None)
        it["_media"] = media


PART_FAM = {"头饰": "h", "衣服": "b", "背包": "bag", "整套": "suit", "光源": "light"}
AP_RX = re.compile(r"appearance_icons/(\d+)_([男女])\.png$")


def fix_appearance_icons(it: dict, dry: bool, stat: Counter) -> None:
    """外观合并卡（merged_from=appearance_extra）的图标是按 model 出的「整套外观图」，
    把同一张衣服图同时挂到了头饰卡上 —— 按部位纠正成对应图标，并补另一性别。

    例：云兔衔光-头饰 原本显示 3732001_女.png（衣服图），纠正为 icon_h_f_3732001。
    """
    media = it.get("_media") or {}
    imgs = [x for x in (media.get("images") or []) if isinstance(x, dict)]
    if not imgs:
        return
    fam = PART_FAM.get(((it.get("part_bucket") or [""])[0]))
    if not fam:
        return
    out, hit_any, model = [], False, None
    for im in imgs:
        m = AP_RX.search(str(im.get("png") or ""))
        if not m:
            out.append(im)
            continue
        model, g = m.group(1), m.group(2)
        stem = "icon_%s_%s_%s" % (fam, "f" if g == "女" else "m", model)
        rp = refs_hit(stem)
        if not rp:
            out.append(im)
            continue
        dst = POSTERS / ("%s_%s.png" % (it["id"], "f" if g == "女" else "m"))
        if not dry:
            POSTERS.mkdir(parents=True, exist_ok=True)
            if not dst.is_file():
                shutil.copyfile(rp, dst)
        out.append({"png": str(dst.relative_to(WEB)).replace("\\", "/"), "base": stem,
                    "label": g, "source": "按部位纠正（%s）· refs %s" % (fam, rp.name)})
        hit_any = True
        stat["外观卡部位纠正"] += 1
    # 补另一性别
    if hit_any and model:
        have = {x.get("label") for x in out if x.get("base")}
        for g, code in (("女", "f"), ("男", "m")):
            if g in have:
                continue
            stem = "icon_%s_%s_%s" % (fam, code, model)
            rp = refs_hit(stem)
            if not rp:
                continue
            dst = POSTERS / ("%s_%s.png" % (it["id"], code))
            if not dry:
                if not dst.is_file():
                    shutil.copyfile(rp, dst)
            out.append({"png": str(dst.relative_to(WEB)).replace("\\", "/"), "base": stem,
                        "label": g, "source": "按部位补另一性别 · refs %s" % rp.name})
            stat["外观卡补另一性别"] += 1
    if hit_any:
        out.sort(key=lambda x: 0 if x.get("label") == "女" else (1 if x.get("label") == "男" else 2))
        if not dry:
            media["images"] = out
            media["total"] = len(out)
            it["icon_count"] = len(out)
            it["icon_state"] = "有图"
            it["_media"] = media


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--no-export", action="store_true", help="只做本地文件/refs 修复，不实导")
    ap.add_argument("--no-slots", action="store_true", help="不补「icons_all 登记了但没取到」的性别槽")
    ap.add_argument("--no-reuse", action="store_true", help="不做男女通用族（背包/光源/整套）复用")
    a = ap.parse_args()

    d = load_board()
    stat = Counter()
    exp = PackExporter()
    t0 = time.time()
    touched = 0

    for idx, it in enumerate(d["items"], 1):
        if idx % 200 == 0:
            print("  [%d/%d] %.0fs 补图 %d 仍缺 %d" % (
                idx, len(d["items"]), time.time() - t0,
                stat["refs 回填"] + stat["实导回填"] + stat["槽位补图"], stat["槽位仍缺"]), flush=True)
        media = it.get("_media") or {}
        imgs = [x for x in (media.get("images") or []) if isinstance(x, dict)]
        cid = it["id"]

        if imgs:
            # 本卡可用的落盘图（其它条目 + icons_all.png），按归一 base 索引
            avail = {}
            for im in imgs:
                p = im.get("png") or ""
                if p and (WEB / p).is_file():
                    avail.setdefault(nb(im.get("base")), p)
            for ic in (it.get("icons_all") or []):
                p = ic.get("png") or ""
                if p and (WEB / p).is_file():
                    avail.setdefault(nb(ic.get("path")), p)

            # 保留此前标记的缺槽（否则每次重跑都会把 mark_gender_gaps 的结果冲掉）
            fixed, gaps = [], [g for g in (media.get("missing") or []) if isinstance(g, dict)]
            for im in imgs:
                png = str(im.get("png") or "")
                if png and (WEB / png).is_file():
                    fixed.append(im)
                    stat["原样可用"] += 1
                    continue
                key = nb(im.get("base"))
                g = gender_of(im.get("base")) or str(im.get("label") or "").replace("装", "")[:1]
                # 1) 本卡已有同 base 的落盘文件 → 改指向，不复制
                if key in avail:
                    im = dict(im)
                    im["png"] = avail[key]
                    im["repair"] = "同 base 已有文件"
                    fixed.append(im)
                    stat["改指向本卡已有文件"] += 1
                    continue
                # 2) 本地图库（item_icons_full / refs）→ 复制一份到 fashion_posters
                rp = local_hit(im.get("base"))
                dst = POSTERS / ("%s_%s.png" % (cid, "m" if g == "男" else "f"))
                n = 2
                while dst.exists():
                    dst = POSTERS / ("%s_%s%d.png" % (cid, "m" if g == "男" else "f", n))
                    n += 1
                if rp:
                    if not a.dry:
                        POSTERS.mkdir(parents=True, exist_ok=True)
                        shutil.copyfile(rp, dst)
                    im = dict(im)
                    im["png"] = str(dst.relative_to(WEB)).replace("\\", "/")
                    im["repair"] = "refs:%s" % rp.name
                    im["bytes"] = rp.stat().st_size
                    fixed.append(im)
                    stat["refs 回填"] += 1
                    continue
                # 3) 实导
                if a.no_export:
                    gaps.append({"base": key, "gender": g, "why": "未实导"})
                    stat["缺图(跳过实导)"] += 1
                    continue
                src = "" if a.dry else exp.export(key, dst)
                if src:
                    im = dict(im)
                    im["png"] = str(dst.relative_to(WEB)).replace("\\", "/")
                    im["repair"] = "实导:%s" % src
                    im["bytes"] = dst.stat().st_size
                    fixed.append(im)
                    stat["实导回填"] += 1
                else:
                    if dst.exists():
                        dst.unlink()
                    gaps.append({"base": key, "gender": g, "why": "PE/PC 均未命中"})
                    stat["仍缺图"] += 1

            # 去重（同归一 base 只留一张，优先 _b）+ label 归一
            groups = {}
            for im in fixed:
                groups.setdefault(nb(im.get("base")), []).append(im)
            kept = []
            for _k, g in groups.items():
                g.sort(key=lambda x: 0 if str(x.get("base")).endswith("_b") else
                       (2 if str(x.get("base")).endswith("_s") else 1))
                keep = dict(g[0])
                gl = gender_of(keep.get("base"))
                if gl:
                    keep["label"] = gl
                kept.append(keep)
                stat["去重合并"] += len(g) - 1
            kept.sort(key=lambda x: 0 if x.get("label") == "女" else (1 if x.get("label") == "男" else 2))
            n = 0
            for x in kept:
                if x.get("label") not in ("男", "女"):
                    n += 1
                    x["label"] = "图示%d" % n

            if len(kept) != len(imgs) or any(x.get("repair") for x in kept):
                touched += 1
            media["images"] = kept
            media["total"] = len(kept)
            if gaps:
                media["missing"] = gaps
                it["gender_icon_state"] = "缺%s图" % ("/".join(
                    sorted({g["gender"] for g in gaps if g["gender"]})) or "图")
            else:
                media.pop("missing", None)
                it.pop("gender_icon_state", None)
            it["icon_count"] = len(kept)
            if kept:
                it["icon_state"] = "有图"
            it["_media"] = media

            # icons_all 的 png 指向补齐（溯源用）
            bykey = {nb(x.get("base")): x.get("png") for x in kept}
            for ic in (it.get("icons_all") or []):
                k = nb(ic.get("path"))
                if k in bykey:
                    ic["png"] = bykey[k]

        # 第二段：icons_all 登记了、卡上却没图的性别槽，尽量补上
        if not a.no_slots and (it.get("icons_all") or []):
            before = len((it.get("_media") or {}).get("images") or [])
            fill_missing_slots(it, exp, a.dry, stat)
            if len((it.get("_media") or {}).get("images") or []) != before:
                touched += 1
                media = it["_media"]
                media.pop("placeholder", None)

        # 第三段：男女通用族（背包/光源/整套）的缺槽 → 复用另一性别那张图
        if not a.no_reuse:
            fix_appearance_icons(it, a.dry, stat)
            mark_gender_gaps(it, a.dry, stat)
        if not a.no_reuse and (it.get("_media") or {}).get("missing"):
            before = len((it.get("_media") or {}).get("images") or [])
            reuse_unisex(it, a.dry, stat)
            if len((it.get("_media") or {}).get("images") or []) != before:
                touched += 1

        # 收尾：图已补齐的性别，缺口标记要撤掉（否则卡面永远显示缺图）
        prune_gaps(it, a.dry)

    print("=== 修图结果（%.1fs）===" % (time.time() - t0))
    for k, v in stat.most_common():
        print("  %-22s %5d" % (k, v))
    print("  受影响卡 %d" % touched)
    if not a.dry:
        save_board(d)
        print("已写回", BOARD_JSON.name, "与", BOARD_JS.name)
    else:
        print("（dry-run，未写盘）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
