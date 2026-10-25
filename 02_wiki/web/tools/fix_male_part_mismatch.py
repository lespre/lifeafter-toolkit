# -*- coding: utf-8 -*-
"""修正「男图取成男衣服」的问题：男装图必须与卡部位同族，否则按女图换性别重取。

规则：
  女图 icon_h_f_X  → 男图应 icon_h_m_X（不是 icon_b_m_X）
  女图 icon_b_f_X  → 男图应 icon_b_m_X
  女图 icon_bag_f_X→ 男图应 icon_bag_m_X
  编号式 icon_N_2   → 男图 icon_N_1
重取失败则删掉错误的男图，标记 gender_male_state=未下发。
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

PROJ = pathlib.Path("E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
import pe_fetch  # noqa: E402
from PIL import Image  # noqa: E402

BOARD = WEB / "data/boards/fashion_wardrobe.json"
OUT = WEB / "assets/fashion_posters"
FAM = ("icon_bag", "icon_light", "icon_suit", "icon_h", "icon_b")
SUF = ("_b", "_s", "")


def family(base: str) -> str:
    for f in FAM:
        if base.startswith(f + "_"):
            return f
    return ""


def sibling_male(female_base: str) -> list[str]:
    b = female_base
    out = []
    if "_f_" in b:
        out.append(b.replace("_f_", "_m_"))
    m = re.match(r"^(icon_\d+)_2(_\d+)?$", b)
    if m:
        out.append(m.group(1) + "_1" + (m.group(2) or ""))
    m = re.match(r"^(icon_\d+)_2(_\d+)?(_[a-z]+)?$", b)
    if m:
        out.append(m.group(1) + "_1" + (m.group(2) or "") + (m.group(3) or ""))
    return list(dict.fromkeys(out))


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
    fixed = dropped = 0
    for it in d["items"]:
        imgs = [x for x in ((it.get("_media") or {}).get("images") or []) if isinstance(x, dict)]
        male = [x for x in imgs if "男" in str(x.get("label", ""))]
        female = [x for x in imgs if "男" not in str(x.get("label", ""))]
        if not male or not female:
            continue
        parts = [p for p in (it.get("part_bucket") or [])]
        want = {"衣服": "icon_b", "头饰": "icon_h", "背包": "icon_bag",
                "光源": "icon_light", "整套": "icon_suit"}
        fams = {want[p] for p in parts if p in want}
        bad = [m for m in male if fams and family(str(m.get("base") or "")) not in fams]
        if not bad:
            continue
        # 用女图换性别重取
        new_imgs = [x for x in imgs if x not in bad]
        for fb in [str(f.get("base") or "") for f in female]:
            for cand in sibling_male(fb):
                dst = OUT / ("%s_m.png" % it["id"])
                hit = try_export(cand, dst)
                if hit:
                    new_imgs.append({"png": "assets/fashion_posters/%s_m.png" % it["id"],
                                     "base": hit.split("/")[-1], "label": "男装",
                                     "source": "PE · %s（按女图换性别重取）" % hit})
                    fixed += 1
                    break
            else:
                continue
            break
        else:
            dropped += 1
            it["gender_male_state"] = "未下发（原男图部位不符，已剔除）"
        new_imgs.sort(key=lambda x: (1 if "男" in str(x.get("label", "")) else 0))
        for i, im in enumerate(new_imgs, 1):
            if "男" not in str(im.get("label", "")):
                im["label"] = "图示%d" % i
        it["_media"] = {"images": new_imgs, "total": len(new_imgs)}

    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("按女图换性别重取成功 %d 张 ｜ 剔除错误男图 %d 张" % (fixed, dropped))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
