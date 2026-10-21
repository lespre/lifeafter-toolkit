# -*- coding: utf-8 -*-
r"""PC 取图器：路径 → PC 落点，带三级兜底，并统计真实覆盖率。

兜底顺序：
  ① 精确：<base><suffix>.bc7 → hit_table
  ② 换扩展：.png / .jpg / .ktx
  ③ 同名兜底：hit_table 里同 basename 的任意路径（解决 _skill 这类换目录改名）
"""
from __future__ import annotations

import csv
import json
import pathlib
import sys

def _project_root() -> pathlib.Path:
    """自动定位项目根：环境变量 LA_ROOT → 向上找 00_治理 与 01_工具。"""
    import os
    env = os.environ.get("LA_ROOT")
    if env:
        return pathlib.Path(env).expanduser().resolve()
    here = pathlib.Path(__file__).resolve()
    for up in here.parents:
        if (up / "00_治理").is_dir() and (up / "01_工具").is_dir():
            return up
    return here.parents[3]



PROJ = _project_root()
WEB = PROJ / "04_站点/web"
CAL = PROJ / "03_执行/30_分析/热更检测/pc_fid_calib/hit_table.csv"
EXTRA = PROJ / "03_执行/30_分析/热更检测/pc_fid_calib/hit_table_extra.csv"


def load() -> tuple[dict, dict]:
    exact, by_name = {}, {}
    for src in (CAL, EXTRA):
        if not src.is_file():
            continue
        with src.open(encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                p = r["path"]
                exact[p] = (r["pkg"], int(r["row"]), r.get("kind"), r.get("dw"), r.get("dh"))
                name = p.rsplit("/", 1)[-1]
                by_name.setdefault(name, []).append(p)
    return exact, by_name


def join_path(base: str, suffix: str) -> str:
    s = suffix or ""
    s = s if s.startswith("_") else ("_" + s if s else "")
    return base if (s and base.endswith(s)) else base + s


def resolve(base: str, suffix: str, exact: dict, by_name: dict) -> tuple[str, str] | None:
    stem = join_path(base, suffix)
    for ext in (".bc7", ".png", ".jpg", ".dds", ".ktx"):
        p = stem + ext
        if p in exact:
            return p, "精确"
    # 档位兜底：只有 _s 没有 _b 时用 _s 顶（PC 常只下发小图）
    alt = None
    if stem.endswith("_b"):
        alt = stem[:-2] + "_s"
    elif stem.endswith("_s"):
        alt = stem[:-2] + "_b"
    if alt:
        for ext in (".bc7", ".png", ".jpg", ".dds", ".ktx"):
            if alt + ext in exact:
                return alt + ext, "档位兜底"
    # 同名兜底
    name = stem.rsplit("/", 1)[-1]
    for ext in (".bc7", ".png", ".jpg"):
        cands = by_name.get(name + ext) or []
        if cands:
            return cands[0], "同名兜底"
    return None


def main() -> int:
    exact, by_name = load()
    print("PC 路径表 %d 条 ｜ basename 索引 %d" % (len(exact), len(by_name)))

    total = hit_exact = hit_fuzzy = miss = 0
    miss_list = []
    for bid in ("fashion_wardrobe", "vehicle_full", "tactical_chip_full", "mutation_core_full"):
        p = WEB / "data/boards" / (bid + ".json")
        if not p.is_file():
            continue
        for it in json.loads(p.read_text(encoding="utf-8"))["items"]:
            for im in ((it.get("_media") or {}).get("images") or []):
                b = im.get("base")
                if not b:
                    continue
                total += 1
                r = resolve(b, im.get("suffix") or "", exact, by_name)
                if r and r[1] == "精确":
                    hit_exact += 1
                elif r:
                    hit_fuzzy += 1
                else:
                    miss += 1
                    miss_list.append(b + ("" if not im.get("suffix") else "_" + str(im.get("suffix")).lstrip("_")))
    print("图鉴图 %d 张 ｜ 精确 %d ｜ 同名兜底 %d ｜ 缺 %d ｜ 覆盖 %.2f%%"
          % (total, hit_exact, hit_fuzzy, miss, (hit_exact + hit_fuzzy) * 100.0 / max(total, 1)))
    print("仍缺样例:", miss_list[:6])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
