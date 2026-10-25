# -*- coding: utf-8 -*-
"""同 model + 同部位 的卡之间复用已导出的图（参照款 → 缺图款）。

用于「耀·」这类同款不同品级的卡：资源名带自己的前缀，但图在库里可能只发过一份。
复制的是已存在且已按卡名部位校验过的 PNG，不改名不猜路径。
"""
from __future__ import annotations

import json
import pathlib
import re
import shutil

ROOT = pathlib.Path("E:/la拆包项目")
WEB = ROOT / "02_wiki/web"
BOARD = WEB / "data/boards/fashion_wardrobe.json"
WANT = {"衣服": "icon_b", "头饰": "icon_h", "背包": "icon_bag", "光源": "icon_light", "整套": "icon_suit"}
NAME_PART = re.compile(r"[-·](衣服|头饰|背包|光源|整套)$")


def fam(base: str) -> str:
    for f in ("icon_bag", "icon_light", "icon_suit", "icon_h", "icon_b"):
        if base.startswith(f + "_"):
            return f
    return ""


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]
    # 参照池：部位与图族一致、且图文件确实存在
    pool: dict[tuple[str, str], list[dict]] = {}
    for it in items:
        m = NAME_PART.search(str(it["name"]))
        if not m:
            continue
        f = WANT[m.group(1)]
        imgs = [x for x in ((it.get("_media") or {}).get("images") or []) if isinstance(x, dict)]
        good = [x for x in imgs if fam(str(x.get("base") or "")) == f
                and (WEB / str(x.get("png") or "")).is_file()]
        if good:
            pool.setdefault((str(it.get("model_id") or ""), f), good)

    fixed = 0
    for it in items:
        m = NAME_PART.search(str(it["name"]))
        if not m:
            continue
        f = WANT[m.group(1)]
        imgs = [x for x in ((it.get("_media") or {}).get("images") or []) if isinstance(x, dict)]
        good = [x for x in imgs if fam(str(x.get("base") or "")) == f
                and (WEB / str(x.get("png") or "")).is_file()]
        src = pool.get((str(it.get("model_id") or ""), f))
        if good or not src:
            continue
        new = []
        for i, s in enumerate(src):
            suffix = "" if i == 0 else "_%d" % i
            dst_rel = "assets/fashion_posters/%s%s.png" % (it["id"], suffix)
            shutil.copyfile(WEB / s["png"], WEB / dst_rel)
            gender = "女" if "_f_" in str(s.get("base")) else "男" if "_m_" in str(s.get("base")) else "图示"
            new.append({"png": dst_rel, "base": s.get("base"),
                        "label": "女装" if gender == "女" else "男装" if gender == "男" else "图示",
                        "source": "同款同部位参照（%s 已发布图）" % s.get("base")})
        it["_media"] = {"images": new, "total": len(new)}
        it["media_reuse"] = "同 model 同部位参照，非本卡独立导出"
        it.pop("gender_male_state", None)
        fixed += 1

    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("复用参照图修复 %d 卡" % fixed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
