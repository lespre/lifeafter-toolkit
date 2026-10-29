# -*- coding: utf-8 -*-
r"""把「前缀版本卡」并入本体卡 —— 同一套时装在 fashion_data 里有多条记录。

起因（2026-10-29 用户反馈）：
  炽海天姿 在板上出现 4 张卡（头饰×2、衣服×2）：
    炽海天姿-头饰      model 5001  魅力 400   图标 icon_h_*_5001001
    耀·炽海天姿-头饰   model 5001  魅力 —     图标 icon_h_*_5001003（资源未下发，挂的是 001 的图）
  两两同名（只差「耀·」前缀）、同 model、同部位、同品级、同描述 —— 就是一套，被当成两张输出。

判定条件（四条全中才合，避免误并「堂前问鼎·守护」这类真不同的款）：
  ① 名字形如「<前缀>·<本体名>」
  ② 本体卡存在（同名同部位）
  ③ model_id 相同
  ④ grade_level 相同（都取得到时）

合并后：
  · 本体卡新增 version_merge：别名 / 被并卡 id / 行键 / 登记但未下发的图标路径
  · 图片不重复搬（耀版实际挂的就是本体的图）
  · 被并卡存进顶层 merged_away，可回滚
  · 卡面显示「含X·版」小标，详情列同套版本

用法：
  python merge_version_cards.py --dry
  python merge_version_cards.py
"""
from __future__ import annotations

import argparse
import json
import pathlib
from collections import Counter

PROJ = pathlib.Path("E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
BOARDS = WEB / "data/boards"
BOARD_JSON = BOARDS / "fashion_wardrobe.json"
BOARD_JS = BOARDS / "fashion_wardrobe.js"


def load_board() -> dict:
    return json.loads(BOARD_JSON.read_text(encoding="utf-8"))


def save_board(d: dict) -> None:
    BOARD_JSON.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    BOARD_JS.write_text("window.WIKI_BOARD_fashion_wardrobe = "
                        + json.dumps(d, ensure_ascii=False, indent=1) + ";\n",
                        encoding="utf-8")


def split_prefix(name: str):
    """'耀·炽海天姿-头饰' → ('耀', '炽海天姿-头饰')；没有前缀返回 ('', 原名)。"""
    if "·" not in name:
        return "", name
    p, rest = name.split("·", 1)
    return (p, rest) if rest else ("", name)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    d = load_board()
    items = d["items"]
    idx = {}
    for it in items:
        idx.setdefault((it["name"], it.get("part")), it)

    stat = Counter()
    pairs = []          # (本体卡, 版本卡, 前缀)
    for it in items:
        p, base = split_prefix(it["name"])
        if not p:
            continue
        host = idx.get((base, it.get("part")))
        if host is None or host is it:
            stat["无本体卡"] += 1
            continue
        if host.get("model_id") != it.get("model_id"):
            stat["model 不同"] += 1
            continue
        if (host.get("grade_level") is not None and it.get("grade_level") is not None
                and host["grade_level"] != it["grade_level"]):
            stat["品级不同"] += 1
            continue
        pairs.append((host, it, p))

    for host, it, p in pairs:
        print("%-14s %-12s ← 并入 %s（model %s，魅力 %s → %s，图标 %s）" % (
            host["name"], host["id"], it["name"], it.get("model_id"),
            host.get("charm_value"), it.get("charm_value"),
            ",".join(x.get("path", "").split("/")[-1] for x in (it.get("icons_all") or [])) or "—"))
        if a.dry:
            continue
        vm = host.get("version_merge") or {"aliases": [], "ids": [], "row_keys": [], "icon_paths": []}
        vm["aliases"].append(it["name"])
        vm["ids"].append(it["id"])
        for rk in (it.get("row_keys") or []):
            if rk not in vm["row_keys"]:
                vm["row_keys"].append(rk)
        for ic in (it.get("icons_all") or []):
            pth = ic.get("path")
            if pth and pth not in vm["icon_paths"]:
                vm["icon_paths"].append(pth)
        vm["prefixes"] = sorted(set((vm.get("prefixes") or []) + [p]))
        vm["charm_value"] = it.get("charm_value")
        vm["note"] = ("同 model 的另一条记录（前缀「%s」），图标 %s 在 PE/PC 未下发，"
                      "故沿用本体图" % (p, "、".join(x.split("/")[-1] for x in vm["icon_paths"])))
        host["version_merge"] = vm
        # 版本卡若登记了缺口（图标没取到），本体也记一笔，别假装图是全的
        if (it.get("_media") or {}).get("missing") and not (host.get("_media") or {}).get("missing"):
            host.setdefault("_media", {})["missing"] = it["_media"]["missing"]
        stat["合并版本卡"] += 1

    gone = {it["id"] for _h, it, _p in pairs}
    if gone and not a.dry:
        by_id = {it["id"]: it for it in items}
        d["items"] = [x for x in items if x["id"] not in gone]
        ma = d.get("merged_away") or []
        for hid in gone:
            src = by_id[hid]
            ma.append({
                "id": hid, "name": src["name"], "part": src.get("part"),
                "model_ids": src.get("model_ids"), "provenance": src.get("provenance"),
                "into": next(h["id"] for h, it, _p in pairs if it["id"] == hid),
                "kind": "version",
            })
        d["merged_away"] = ma
        d["meta"]["merged_cards"] = len(ma)
        st = d["meta"].get("state_summary") or {}
        st["有图"] = sum(1 for x in d["items"] if x.get("icon_state") == "有图")
        st["无图"] = len(d["items"]) - st["有图"]
        d["meta"]["state_summary"] = st
        if isinstance(d["meta"].get("rebuild"), dict):
            d["meta"]["rebuild"]["cards"] = len(d["items"])
        d["meta"]["notes"] = (d["meta"].get("notes") or "") + (
            "\n\n【同套版本卡合并（2026-10-29）】\n"
            "「<前缀>·<本体名>」且同 model、同部位、同品级的独立记录并入本体卡，共 %d 张：%s。\n"
            "本体卡 version_merge 保留别名/行键/登记图标；卡面标「含X·版」；"
            "耀版图标（如 icon_h_*_5001003）在 PE/PC 未下发，图沿用本体 001。\n" % (
                len(gone), "、".join(sorted({it["name"] for _h, it, _p in pairs}))))

    print("=== 结果 ===")
    for k, v in stat.most_common():
        print("  %-12s %4d" % (k, v))
    print("  cards %d → %d" % (len(items), len(items) - len(gone)))
    if a.dry:
        print("（dry-run，未写盘）")
    else:
        save_board(d)
        print("已写回", BOARD_JSON.name, "与", BOARD_JS.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
