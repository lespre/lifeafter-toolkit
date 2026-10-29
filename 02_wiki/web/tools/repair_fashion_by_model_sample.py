# -*- coding: utf-8 -*-
"""按「同 model + 同部位」的正确图样本，修复错部位/缺性别的时装卡。

样本来源：所有「卡名部位 == 图族」的卡；
修复对象：卡名部位与图族不符、或缺少某性别的卡。
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from collections import Counter, defaultdict


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
WEB = PROJ / "02_wiki/web"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
import pe_fetch  # noqa: E402
from PIL import Image  # noqa: E402

BOARD = WEB / "data/boards/fashion_wardrobe.json"
OUT = WEB / "assets/fashion_posters"
WANT = {"衣服": "icon_b", "头饰": "icon_h", "背包": "icon_bag", "光源": "icon_light", "整套": "icon_suit"}
SUF = ("_b", "_s", "")
NAME_PART = re.compile(r"[-·](衣服|头饰|背包|光源|整套)$")
NUM = re.compile(r"^icon_\d+")


def family(base: str) -> str:
    for f in ("icon_bag", "icon_light", "icon_suit", "icon_h", "icon_b"):
        if base.startswith(f + "_"):
            return f
    return ""


def gender_of(base: str) -> str:
    if "_m_" in base:
        return "m"
    if "_f_" in base:
        return "f"
    if re.match(r"^icon_\d+_1", base):
        return "m"
    if re.match(r"^icon_\d+_2", base):
        return "f"
    return ""


def try_export(base: str, dst: pathlib.Path) -> str:
    for s in SUF:
        try:
            if pe_fetch.export(base + s, dst) and dst.is_file() and dst.stat().st_size > 512:
                w, h = Image.open(dst).size
                if w >= 64 and h >= 64:
                    return base + s
        except Exception:  # noqa: BLE001
            continue
    if dst.exists():
        dst.unlink()
    return ""


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]

    # 1) 采样：卡名部位与图族一致的图
    pool: dict[tuple[str, str], Counter] = defaultdict(Counter)
    for it in items:
        m = NAME_PART.search(str(it["name"]))
        if not m:
            continue
        fam = WANT[m.group(1)]
        model = str(it.get("model_id") or "")
        for im in ((it.get("_media") or {}).get("images") or []):
            if not isinstance(im, dict):
                continue
            base = str(im.get("base") or "")
            if family(base) != fam:
                continue
            g = gender_of(base)
            if g:
                pool[(model, fam)][(g, base)] += 1

    print("可复用的样本组 %d" % len(pool))

    # 2) 修复
    fixed = 0
    for it in items:
        m = NAME_PART.search(str(it["name"]))
        if not m:
            continue
        fam = WANT[m.group(1)]
        model = str(it.get("model_id") or "")
        imgs = [x for x in ((it.get("_media") or {}).get("images") or []) if isinstance(x, dict)]
        keep = [x for x in imgs if family(str(x.get("base") or "")) == fam]
        have = {gender_of(str(x.get("base") or "")) for x in keep}
        cands = pool.get((model, fam), Counter())
        if not cands:
            continue
        best = {}
        for (g, base), _ in cands.most_common():
            best.setdefault(g, base)
        changed = False
        for g, label in (("f", "女装"), ("m", "男装")):
            if g in have or g not in best:
                continue
            dst = OUT / ("%s_%s.png" % (it["id"], g))
            hit = try_export(best[g], dst)
            if not hit:
                continue
            keep.append({"png": "assets/fashion_posters/%s_%s.png" % (it["id"], g),
                         "base": hit.split("/")[-1], "label": label,
                         "source": "PE · %s（同款同部位参照）" % hit})
            changed = True
        if not changed and len(keep) == len(imgs):
            continue
        for i, im in enumerate(keep, 1):
            if "男" not in str(im.get("label", "")) and "女" not in str(im.get("label", "")):
                im["label"] = "图示%d" % i
        it["_media"] = {"images": keep, "total": len(keep)}
        if len(keep) >= 2:
            it.pop("gender_male_state", None)
        fixed += 1

    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("修复卡 %d 张" % fixed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
