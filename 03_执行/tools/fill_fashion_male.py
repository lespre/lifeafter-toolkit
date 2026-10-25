# -*- coding: utf-8 -*-
r"""给时装板补齐男角色图（**只用 PE 源**，禁止回落 PC）。

用法：
  python fill_fashion_male.py --limit 50          # 试样
  python fill_fashion_male.py --all               # 全量
  python fill_fashion_male.py --all --batch 200   # 指定批大小

要点（踩过的坑）：
  * 图标路径必须带 `ui/item_icon/` 前缀，且必须带 `_b`/`_s` 后缀才会被 resolve 命中。
  * 男女成对命名两套：`icon_<n>_1`(男)/`icon_<n>_2`(女)；`icon_b_m_<n>`/`icon_b_f_<n>`
    （另有 hat/bag/light/suit 四种家族前缀）。
  * 包缓存：整包只读一次，按 row 直接定位载荷，避免每张图重新 iter_entries。
"""
from __future__ import annotations

import argparse
import io
import json
import pathlib
import re
import shutil
import sqlite3
import sys
import time

PROJ = pathlib.Path(r"E:/la拆包项目")
CORE = PROJ / "00_规范与工具/工具/工具库/00_共享核心"
sys.path.insert(0, str(CORE))

from toolkit_core import android_gpk as AG  # noqa: E402
from toolkit_core.path_fid import fid_of  # noqa: E402

IDX = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
PACKS = PROJ / "01_索引与产物/源包/pe_gres_android"
WARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
OUTDIR = PROJ / "02_wiki/web/assets/fashion_posters"
REPDIR = PROJ / "01_索引与产物/30_分析/子代理产出_20261022"

EXTS = (".ktx", ".dds", ".png", ".bc7")
SIZE_SUF = ("_b", "_s", "")


def hx(v) -> str:
    return v if isinstance(v, str) else "%016X" % (v & 0xFFFFFFFFFFFFFFFF)


# ---------------------------------------------------------------- 索引
class Index:
    def __init__(self):
        self.c = sqlite3.connect("file:%s?mode=ro" % str(IDX).replace("\\", "/"), uri=True, timeout=30)
        self.n = 0

    def lookup(self, stem: str):
        """stem 如 ui/item_icon/icon_h_m_1 ；自动试扩展名与 _b/_s 互换。"""
        self.n += 1
        stems = [stem]
        if stem.endswith("_b"):
            stems.append(stem[:-2] + "_s")
        elif stem.endswith("_s"):
            stems.append(stem[:-2] + "_b")
        for st in stems:
            for e in EXTS:
                p = st + e
                r = self.c.execute("select pack,row from rows where fid=? limit 1",
                                   (hx(fid_of(p)),)).fetchone()
                if r:
                    return p, r[0], r[1]
        return None


# ---------------------------------------------------------------- 包缓存
class PackReader:
    def __init__(self):
        self._blob, self._spans, self._rows = {}, {}, {}
        self._img = {}

    def _load(self, pack):
        if pack in self._blob:
            return
        p = PACKS / pack
        if not p.is_file():
            self._blob[pack] = None
            return
        _rec, spans, factory = AG.open_blocks(str(p))
        self._blob[pack] = p.read_bytes()
        self._spans[pack] = spans
        self._rows[pack] = {r[0]: r for r in factory()}

    def get_png(self, pack, row):
        key = (pack, row)
        if key in self._img:
            return self._img[key]
        self._load(pack)
        blob = self._blob.get(pack)
        if blob is None:
            self._img[key] = ("包文件不存在", None)
            return self._img[key]
        ent = self._rows[pack].get(row)
        if ent is None:
            self._img[key] = ("包内无此行", None)
            return self._img[key]
        _row, fid, off, packed, decoded, flag = ent
        h = AG._base_of(self._spans[pack], row) + off
        pay = blob[h + 20: h + 20 + packed]
        data = AG.decompress(pay, flag, decoded)
        if data is None:
            self._img[key] = ("解压失败 flag=%d" % flag, None)
            return self._img[key]
        try:
            rr = {"row": row, "fid": fid, "data": data, "flag": flag,
                  "kind": AG.content_kind(data, flag)}
            if data[:4] == b"\xabKTX":
                rr["info"] = AG.parse_ktx(data)
            rgba = AG.decode_image(rr)
            from PIL import Image
            buf = io.BytesIO()
            Image.fromarray(rgba, "RGBA").save(buf, "PNG")
            self._img[key] = (None, buf.getvalue())
        except Exception as ex:
            self._img[key] = ("解码失败: %s %s" % (type(ex).__name__, str(ex)[:60]), None)
        return self._img[key]


# ---------------------------------------------------------------- base 分类
FAM_RX = [
    ("bag", re.compile(r"^icon_bag_([fm])_(\d+)((?:_\d+)?)$")),
    ("b", re.compile(r"^icon_b_([fm])_(\d+)((?:_\d+)?)$")),
    ("hat", re.compile(r"^icon_h_([fm])_(\d+)((?:_\d+)?)$")),
    ("suit", re.compile(r"^icon_suit_([fm])_(\d+)((?:_\d+)?)$")),
    ("light", re.compile(r"^icon_light_([fm])_(\d+)((?:_\d+)?)$")),
    ("cloth", re.compile(r"^icon_cloth_c_(\d+)_(\d+)$")),
    ("num", re.compile(r"^icon_(\d+)_([12])$")),
    ("plain", re.compile(r"^icon_(\d+)$")),
]

FAM_PREFIX = {"bag": "icon_bag_", "b": "icon_b_", "hat": "icon_h_",
              "suit": "icon_suit_", "light": "icon_light_"}


def strip_base(base: str) -> str:
    b = (base or "").strip().replace("\\", "/").rsplit("/", 1)[-1]
    b = re.sub(r"\.(ktx|dds|png|bc7)$", "", b, flags=re.I)
    return re.sub(r"_[bs]$", "", b)


def classify(base: str):
    """→ (fam, gender|None, id, full_stem)"""
    s = strip_base(base)
    for fam, rx in FAM_RX:
        m = rx.match(s)
        if not m:
            continue
        if fam == "cloth":
            return "cloth", None, m.group(1), s
        if fam == "num":
            return "num", ("m" if m.group(2) == "1" else "f"), m.group(1), s
        if fam == "plain":
            return "plain", None, m.group(1), s
        return fam, m.group(1), m.group(2), s
    return "other", None, s, s


def male_candidates(base: str):
    """由一条 base 推男图候选 stem。→ (fam, gender_of_base, [stems])"""
    fam, g, iid, full = classify(base)
    if fam in FAM_PREFIX:
        if g != "f":
            return fam, g, []
        m = re.match(re.escape(FAM_PREFIX[fam]) + r"[fm]_(\d+)((?:_\d+)?)$", full)
        if not m:
            return fam, g, []
        return fam, g, [FAM_PREFIX[fam] + "m_" + m.group(1) + m.group(2)]
    if fam == "num":
        return fam, g, (["icon_%s_1" % iid] if g == "f" else [])
    if fam == "cloth":
        return fam, g, []
    if fam == "plain":
        return fam, g, ["icon_%s_1" % iid, "icon_b_m_%s" % iid, "icon_h_m_%s" % iid,
                        "icon_bag_m_%s" % iid, "icon_light_m_%s" % iid]
    return fam, g, []


def build_candidates(it):
    """→ [(stem, why)] 去重保序"""
    imgs = ((it.get("_media") or {}).get("images") or [])
    cands = []
    for im in imgs:
        _f, _g, cs = male_candidates(im.get("base", ""))
        for x in cs:
            cands.append((x, "base:%s" % im.get("base")))
    for c in (it.get("icons_all") or []):
        p = c.get("path") or ""
        _f, g, _i, full = classify(p)
        if g == "m":
            cands.append((full, "icons_all男"))
        else:
            _f2, _g2, cs = male_candidates(p)
            for x in cs:
                cands.append((x, "icons_all:%s" % strip_base(p)))
    seen, uniq = set(), []
    for s_, why in cands:
        s_ = strip_base(s_)
        if s_ and s_ not in seen:
            seen.add(s_)
            uniq.append((s_, why))
    return uniq


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--batch", type=int, default=200)
    ap.add_argument("--offset", type=int, default=0)
    a = ap.parse_args()

    board = json.loads(WARD.read_text(encoding="utf-8"))
    items = board["items"]

    bak = WARD.with_name(WARD.name + ".bak_20261025_premale")
    if not bak.exists():
        shutil.copy2(WARD, bak)
        print("已备份 →", bak.name)

    idx = Index()
    pr = PackReader()
    OUTDIR.mkdir(parents=True, exist_ok=True)

    todo = []
    for it in items:
        imgs = ((it.get("_media") or {}).get("images") or [])
        if any(classify(im.get("base", ""))[1] == "m" for im in imgs):
            continue
        todo.append(it)
    print("缺男图卡数: %d / 总 %d" % (len(todo), len(items)))
    if a.limit:
        todo = todo[a.offset: a.offset + a.limit]
        print("本次试样:", len(todo))
    else:
        todo = todo[a.offset:]
    if not todo:
        return

    t0 = time.time()
    hit = miss = 0
    reasons, samples = {}, {}
    dirty = False
    since_save = 0

    for n, it in enumerate(todo, 1):
        imgs = ((it.get("_media") or {}).get("images") or [])
        uniq = build_candidates(it)

        got = None
        for stem, why in uniq:
            for suf in SIZE_SUF:
                r = idx.lookup("ui/item_icon/" + stem + suf)
                if r:
                    got = (r, stem + suf, why)
                    break
            if got:
                break

        if not got:
            miss += 1
            if not uniq:
                fam0, g0 = (classify(imgs[0].get("base", ""))[:2] if imgs else ("none", None))
                key = "无候选(fam=%s,g=%s)" % (fam0, g0)
            else:
                key = "索引无(候选%d个全未命中)" % len(uniq)
            reasons[key] = reasons.get(key, 0) + 1
            samples.setdefault(key, []).append(it.get("id"))
            continue

        (path_hit, pack, row), used, why = got
        err, png = pr.get_png(pack, row)
        if png is None:
            miss += 1
            key = "包内取图失败"
            reasons[key] = reasons.get(key, 0) + 1
            samples.setdefault(key, []).append("%s(%s)" % (it.get("id"), err))
            continue

        (OUTDIR / ("%s_m.png" % it["id"])).write_bytes(png)
        imgs.append({
            "png": "assets/fashion_posters/%s_m.png" % it["id"],
            "base": used,
            "label": "男装",
            "source": "PE %s · 行 %s（%s）" % (pack, row, path_hit.rsplit("/", 1)[-1]),
        })
        it.setdefault("_media", {})["images"] = imgs
        it["_media"]["total"] = len(imgs)
        hit += 1
        dirty = True
        since_save += 1

        if since_save >= 100:
            WARD.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
            since_save = 0
            print("  …落盘 %d 张（%.1fs）" % (hit, time.time() - t0))
        if n % a.batch == 0:
            print("批 %d：命中 %d 未命中 %d（%.1fs）" % (n, hit, miss, time.time() - t0))

    if dirty:
        WARD.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")

    print("\n=== 结果 ===")
    print("处理 %d 卡  命中 %d  未命中 %d  命中率 %.1f%%  %.1fs  查索引 %d 次"
          % (len(todo), hit, miss, hit * 100.0 / max(len(todo), 1), time.time() - t0, idx.n))
    for k, v in sorted(reasons.items(), key=lambda x: -x[1]):
        print("  %-34s %4d  例: %s" % (k, v, ", ".join(str(x) for x in samples.get(k, [])[:3])))

    REPDIR.mkdir(parents=True, exist_ok=True)
    (REPDIR / "_male_fill_last.json").write_text(json.dumps(
        {"n": len(todo), "hit": hit, "miss": miss, "reasons": reasons,
         "samples": {k: v[:8] for k, v in samples.items()}}, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
