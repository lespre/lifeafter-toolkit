# -*- coding: utf-8 -*-
"""按「卡名部位」校正男图：名字写 -头饰 就必须是 icon_h_m，-衣服 必须 icon_b_m。

part_bucket 常是多部位合一（['衣服','头饰']），拿它判族会把「头饰卡配到男衣服」放过。
卡名后缀才是这张卡的身份。
"""
from __future__ import annotations

import json
import pathlib
import re
import sys


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


def siblings(female_base: str) -> list[str]:
    b = female_base
    out = []
    if "_f_" in b:
        out.append(b.replace("_f_", "_m_"))
    m = re.match(r"^(icon_\d+)_2(.*)$", b)
    if m:
        out.append(m.group(1) + "_1" + m.group(2))
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
    fixed = dropped = added = 0
    for it in d["items"]:
        m = NAME_PART.search(str(it.get("name") or ""))
        if not m:
            continue                      # 名字不带部位的卡不在这里处理
        target = WANT[m.group(1)]
        imgs = [x for x in ((it.get("_media") or {}).get("images") or []) if isinstance(x, dict)]
        female = [x for x in imgs if "男" not in str(x.get("label", ""))]
        male = [x for x in imgs if "男" in str(x.get("label", ""))]
        if not female:
            continue

        bad = [x for x in male if family(str(x.get("base") or "")) not in ("", target)]
        ok_male = [x for x in male if x not in bad]
        if ok_male:
            continue                      # 已有正确男图

        rest = [x for x in imgs if x not in bad]
        hit = ""
        for fb in [str(f.get("base") or "") for f in female]:
            for cand in siblings(fb):
                if family(cand) != target and not NUM.match(cand):
                    continue
                dst = OUT / ("%s_m.png" % it["id"])
                hit = try_export(cand, dst)
                if hit:
                    rest.append({"png": "assets/fashion_posters/%s_m.png" % it["id"],
                                 "base": hit.split("/")[-1], "label": "男装",
                                 "source": "PE · %s（按卡名部位换性别重取）" % hit})
                    break
            if hit:
                break

        if hit:
            if bad:
                fixed += 1
            else:
                added += 1
        else:
            if bad:
                dropped += 1
                it["gender_male_state"] = "未下发（男图部位不符且无替代）"
            else:
                it["gender_male_state"] = "未下发（男图缺失）"
        for i, im in enumerate(rest, 1):
            if "男" not in str(im.get("label", "")):
                im["label"] = "图示%d" % i
        it["_media"] = {"images": rest, "total": len(rest)}

    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("替换错误男图 %d 张 ｜ 新补男图 %d 张 ｜ 剔除并标未下发 %d 张" % (fixed, added, dropped))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
