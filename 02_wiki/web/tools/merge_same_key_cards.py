# -*- coding: utf-8 -*-
r"""同名同部位同 model 的多张卡收敛为一张（拆卡后的收尾）。

起因：拆「同套多部位」合并卡时，表里还有一组「name 不带部位后缀」的行
（如 367285「星宿万象·冥」，正式行是「星宿万象·冥-头饰」），拆完就与正式卡撞名：
    星宿万象·冥-头饰  charm 200  行 462960-462966   ← 正式行
    星宿万象·冥-头饰  charm —    行 367285          ← 外观/旧版行（拆出来的）
两张同 model 3223、同图，属于同一件。

规则（三条全中才合）：
  ① name 完全相同
  ② part 完全相同
  ③ model_id 相同

主卡选信息更全的那张（charm 非空 > 图片多 > 行键多），其余并入并记进 merged_away。

用法：
  python merge_same_key_cards.py --dry
  python merge_same_key_cards.py
"""
from __future__ import annotations

import argparse
import json
import pathlib
from collections import Counter, defaultdict

PROJ = pathlib.Path("E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
BOARDS = WEB / "data/boards"
BOARD_JSON = BOARDS / "fashion_wardrobe.json"
BOARD_JS = BOARDS / "fashion_wardrobe.js"


def rank(it: dict):
    imgs = (it.get("_media") or {}).get("images") or []
    return (1 if it.get("charm_value") not in (None, 0) else 0, len(imgs), len(it.get("row_keys") or []))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    d = json.loads(BOARD_JSON.read_text(encoding="utf-8"))
    items = d["items"]
    groups = defaultdict(list)
    for it in items:
        groups[(str(it.get("name") or ""), str(it.get("part") or ""), it.get("model_id"))].append(it)

    stat = Counter()
    drop = set()
    for key, lst in groups.items():
        if len(lst) < 2:
            continue
        lst.sort(key=rank, reverse=True)
        host, rest = lst[0], lst[1:]
        print("%-26s %-4s model %-5s  %d 张 → 保留 %s（魅力 %s）" % (
            host["name"], host.get("part"), host.get("model_id"), len(lst), host["id"], host.get("charm_value")))
        for it in rest:
            print("      并入 %s（魅力 %s，行 %s）" % (it["id"], it.get("charm_value"), len(it.get("row_keys") or [])))
            stat["被并卡"] += 1
            drop.add(it["id"])
            if a.dry:
                continue
            host["row_keys"] = sorted(set((host.get("row_keys") or []) + (it.get("row_keys") or [])))
            hi = (host.setdefault("_media", {}).setdefault("images", []))
            have = {str(x.get("base") or "") for x in hi}
            for im in ((it.get("_media") or {}).get("images") or []):
                if im.get("base") not in have:
                    hi.append(im)
                    have.add(im.get("base"))
            host["_media"]["total"] = len(hi)
            host["icon_count"] = len(hi)
            if hi:
                host["icon_state"] = "有图"
            for f in ("charm_value", "grade_level", "desc", "gender"):
                if host.get(f) in (None, "", 0) and it.get(f) not in (None, "", 0):
                    host[f] = it[f]
            variants = sorted(set((host.get("name_variants") or []) + (it.get("name_variants") or [])))
            if variants:
                host["name_variants"] = variants
            if it.get("_media", {}).get("missing") and not host["_media"].get("missing"):
                host["_media"]["missing"] = it["_media"]["missing"]

    if drop and not a.dry:
        by_id = {it["id"]: it for it in items}
        ma = d.get("merged_away") or []
        for did in drop:
            src = by_id[did]
            host = next(x for x in items if x["id"] not in drop and x["name"] == src["name"]
                        and x.get("part") == src.get("part") and x.get("model_id") == src.get("model_id"))
            ma.append({"id": did, "name": src["name"], "part": src.get("part"),
                       "model_ids": src.get("model_ids"), "provenance": src.get("provenance"),
                       "into": host["id"], "kind": "same_key"})
        d["merged_away"] = ma
        d["meta"]["merged_cards"] = len(ma)
        d["items"] = [x for x in items if x["id"] not in drop]
        st = d["meta"].get("state_summary") or {}
        st["有图"] = sum(1 for x in d["items"] if x.get("icon_state") == "有图")
        st["无图"] = len(d["items"]) - st["有图"]
        d["meta"]["state_summary"] = st
        if isinstance(d["meta"].get("rebuild"), dict):
            d["meta"]["rebuild"]["cards"] = len(d["items"])
        d["meta"]["notes"] = (d["meta"].get("notes") or "") + (
            "\n【同名同部位同 model 收敛（2026-10-29）】拆卡后撞名的 %d 组已并回信息更全的那张。\n" % len(drop))
        BOARD_JSON.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        BOARD_JS.write_text("window.WIKI_BOARD_fashion_wardrobe = "
                            + json.dumps(d, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")

    print("=== 结果 ===")
    for k, v in stat.most_common():
        print("  %-10s %4d" % (k, v))
    print("  cards %d → %d" % (len(items), len(items) - len(drop)))
    print("（dry-run，未写盘）" if a.dry else "已写回 json + js")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
