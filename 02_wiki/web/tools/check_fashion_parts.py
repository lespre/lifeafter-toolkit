# -*- coding: utf-8 -*-
r"""核对时装板的部位归类：以 fashion_data 的 part_type 为准，列出不一致的条目。

用法：python check_fashion_parts.py [--apply]
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys
from collections import Counter


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
    out = []
    for r in rows:
        f = {k: (v[1] if isinstance(v, tuple) and len(v) == 2 else v) for k, v in r["values"].items()}
        out.append((r["key"], f))
    return out


def main() -> int:
    apply = "--apply" in sys.argv
    rows = load_rows()
    by_name: dict[str, list] = {}
    for key, f in rows:
        nm = str(f.get("name") or "")
        pt = str(f.get("part_type") or "")
        if not nm or not pt:
            continue
        base = nm
        for s in SUFFIXES:
            if base.endswith(s):
                base = base[: -len(s)]
                break
        by_name.setdefault(base, []).append((key, nm, pt, f.get("model_id")))

    by_model: dict[int, set] = {}
    for _k, _n, pt, mid in [(k, n, pt, m) for k, n, pt, m in
                            [(k2, n2, pt2, m2) for k2, n2, pt2, m2 in
                             [(k3, n3, pt3, m3) for k3, n3, pt3, m3 in
                              [(x[0], x[1], x[2], x[3]) for lst in by_name.values() for x in lst]]]]:
        if mid is not None:
            by_model.setdefault(int(mid), set()).add(PART_CN.get(pt, pt))

    board_p = WEB / "data/boards/fashion_wardrobe.json"
    d = json.loads(board_p.read_text(encoding="utf-8"))
    items = d["items"]

    mism, fixed, nohit = [], 0, 0
    for it in items:
        nm = (it.get("name") or "").strip()
        cands = by_name.get(nm) or []
        if cands:
            want = {PART_CN.get(pt, pt) for _k, _n, pt, _m in cands}
        else:
            mid = it.get("model_id")
            want = by_model.get(int(mid)) if mid is not None else None
            if not want:
                nohit += 1
                continue
        cur = set(it.get("part_bucket") or [])
        if want and not (want & cur):
            _src = "源名=" + (cands[0][1] if cands else "model_id=%s" % it.get("model_id"))
            mism.append((it.get("id"), nm, sorted(cur), sorted(want), _src))
            if apply:
                it["part_bucket"] = sorted(want)
                it["part"] = sorted(want)[0]
                it["part_source"] = "fashion_data.part_type"
                fixed += 1

    print("板内 %d 件 ｜ 名字对得上源表 %d ｜ 对不上 %d" % (len(items), len(items) - nohit, nohit))
    print("部位与源表冲突 %d 件%s" % (len(mism), "（已修正）" if apply else ""))
    for m in mism[:12]:
        print("   %-14s %-20s 板上=%-8s 源表=%-10s %s" % m)

    if apply and fixed:
        board_p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        (WEB / "data/boards/fashion_wardrobe.js").write_text(
            "window.WIKI_BOARD_fashion_wardrobe = "
            + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
        print("已写回", board_p.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
