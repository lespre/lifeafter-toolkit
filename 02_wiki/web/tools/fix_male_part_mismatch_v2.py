# -*- coding: utf-8 -*-
"""修正「男图取成男衣服」：只处理「已知部位族且不匹配」的男图。

判定收窄（上一版误删 580 张的教训）：
  ① 男图是编号式（icon_<num>_1 / icon_<num>_1_b）→ 无法判部位，跳过，不改
  ② 男图部位族为空（如 icon_140030_b）→ 跳过
  ③ 只有当男图族 ∈ 已知族 且 不在卡部位族集合 且 卡部位族集合非空 → 才判错
修正：用同卡女图换性别重取；取不到就删掉该男图并标记「未下发」。
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
FAM = ("icon_bag", "icon_light", "icon_suit", "icon_h", "icon_b")
WANT = {"衣服": "icon_b", "头饰": "icon_h", "背包": "icon_bag", "光源": "icon_light", "整套": "icon_suit"}
SUF = ("_b", "_s", "")
NUM = re.compile(r"^icon_\d+_\d")


def family(base: str) -> str:
    for f in FAM:
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
    fixed = dropped = 0
    for it in d["items"]:
        imgs = [x for x in ((it.get("_media") or {}).get("images") or []) if isinstance(x, dict)]
        male = [x for x in imgs if "男" in str(x.get("label", ""))]
        female = [x for x in imgs if "男" not in str(x.get("label", ""))]
        parts = [p for p in (it.get("part_bucket") or []) if p in WANT]
        if not male or not female or not parts:
            continue
        fams = {WANT[p] for p in parts}
        bad = []
        for m in male:
            base = str(m.get("base") or "")
            fam = family(base)
            if not fam or NUM.match(base):
                continue          # 编号式 / 无族 → 不动
            if fam not in fams:
                bad.append(m)
        if not bad:
            continue
        rest = [x for x in imgs if x not in bad]
        got = ""
        for fb in [str(f.get("base") or "") for f in female]:
            if NUM.match(fb):
                continue
            for cand in siblings(fb):
                if family(cand) not in fams:
                    continue
                dst = OUT / ("%s_m.png" % it["id"])
                hit = try_export(cand, dst)
                if hit:
                    got = hit
                    rest.append({"png": "assets/fashion_posters/%s_m.png" % it["id"],
                                 "base": hit.split("/")[-1], "label": "男装",
                                 "source": "PE · %s（按同卡女图换性别重取）" % hit})
                    break
            if got:
                break
        if got:
            fixed += 1
        else:
            dropped += 1
            it["gender_male_state"] = "未下发（原男图部位不符，已剔除）"
        for i, im in enumerate(rest, 1):
            if "男" not in str(im.get("label", "")):
                im["label"] = "图示%d" % i
        it["_media"] = {"images": rest, "total": len(rest)}

    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("换性别重取成功 %d 张 ｜ 剔除并标未下发 %d 张" % (fixed, dropped))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
