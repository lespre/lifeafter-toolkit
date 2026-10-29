# -*- coding: utf-8 -*-
r"""时装部位纠偏：以 fashion_data.part_type 为准，只改「名字完全对得上」的冲突项。

规则：
  · 名字去掉 -头饰/-衣服/-背包… 后缀后与板内名一致，才算同一个东西；
  · 板上是「整套」的跳过——整套本来就是 hat+cloth+bag 多行聚合，不算错；
  · 其余冲突按源表 part_type 改写 part/part_bucket，并记录 part_source。
"""
from __future__ import annotations

import json
import pathlib
import re
import struct
import sys


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
WEB = PROJ / "02_wiki/web"
BASE = PROJ / "01_索引与产物/41_还原树/Documents/script.py314.lc.npk/com/cdata"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
import toolkit_core.bindict_table as BT  # noqa: E402

PART_CN = {"hat": "头饰", "cloth": "衣服", "bag": "背包", "pendant": "挂饰",
           "suit": "整套", "light": "光源", "face": "面饰", "hair": "发饰",
           "projection": "投影", "gloves": "手套", "shoes": "鞋", "pants": "裤子"}
SUFFIXES = ["-头饰", "-衣服", "-背包", "-挂饰", "-整套", "-光源", "-面饰", "-发饰", "-投影"]


def load_rows():
    p = BASE / "fashion_data.py"
    c = BASE / "fashion_data_chs.py"
    raw = p.read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + L]
    pool = BT.parse_legacy_chs_pool(c.read_bytes())
    rows, _ = BT.decode_table_rows(body, pool, resolve_jumps=True)
    return [(r["key"], {k: (v[1] if isinstance(v, tuple) and len(v) == 2 else v)
                        for k, v in r["values"].items()}) for r in rows]


def base_name(nm: str) -> str:
    """统一写法：去掉部位后缀、括号内容，把 · / ・ / 全角空格 归一成半角空格。"""
    s = nm.strip()
    for suf in SUFFIXES:
        if s.endswith(suf):
            s = s[: -len(suf)]
            break
    s = re.sub(r"[（(][^）)]*[）)]", "", s)
    s = s.replace("·", " ").replace("・", " ").replace("　", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def main() -> int:
    apply = "--apply" in sys.argv
    by_name: dict[str, set] = {}
    for _k, f in load_rows():
        nm = str(f.get("name") or "")
        pt = str(f.get("part_type") or "")
        if nm and pt:
            by_name.setdefault(base_name(nm), set()).add(PART_CN.get(pt, pt))

    p = WEB / "data/boards/fashion_wardrobe.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    fixed, skipped, miss = 0, 0, 0
    for it in d["items"]:
        nm = (it.get("name") or "").strip()
        want = by_name.get(base_name(nm))
        if not want:
            miss += 1
            continue
        cur = set(it.get("part_bucket") or [])
        if cur == {"整套"}:
            skipped += 1
            continue
        if want & cur:
            continue
        if apply:
            it["part_bucket"] = sorted(want)
            it["part"] = sorted(want)[0]
            it["part_source"] = "fashion_data.part_type"
        print("   %-14s %-22s %s → %s" % (it.get("id"), nm, sorted(cur), sorted(want)))
        fixed += 1

    print("\n纠偏 %d 件（整套跳过 %d，名字未匹配 %d，共 %d）"
          % (fixed, skipped, miss, len(d["items"])))
    if apply and fixed:
        p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        (WEB / "data/boards/fashion_wardrobe.js").write_text(
            "window.WIKI_BOARD_fashion_wardrobe = "
            + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
        print("已写回")
    elif fixed:
        print("（加 --apply 才会写回）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
