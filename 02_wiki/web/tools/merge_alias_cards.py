# -*- coding: utf-8 -*-
r"""同名同款不同写法（开发名/占位名）的时装卡合并。

起因（2026-10-29 用户反馈）：
  砂海遗珠-衣服 与 沙漠珍珠裁切-衣服 是同一件衣服，板上出了两张卡。
  查表：两条记录 model_id 都是 3659、部位 cloth、品级 5、魅力 1100，
  区别只在 name（沙漠珍珠裁切 = 开发/占位名）与 desc（占位占位 vs 官方描述）。

判定条件（全中才合，宁可少合不可错合）：
  ① 同一 model_id + 同一部位
  ② 组内恰好一张「正式卡」（desc 有真实文案）与一张「占位卡」（desc 为 占位占位/占位/空）
  ③ 两卡品级相同（都取得到时）、魅力值相同（都取得到时）
  ④ 占位卡名字不是正式卡名字的前缀/变体（已由 merge_version_cards 处理的那类不重复处理）

合并后：
  · 正式卡新增 alias_merge：别名 / 被并卡 id / 行键 / 占位描述 / 说明
  · 行键、表内变体名、model_ids、时限档、图标登记表合并去重
  · 被并卡存进顶层 merged_away（kind=alias），可回滚
  · 卡面显示「别名 · XXX」小标，技术详情列「同款别名」「别名行键」

用法：
  python merge_alias_cards.py --dry
  python merge_alias_cards.py
"""
from __future__ import annotations
import sys

import argparse
import json
import pathlib
from collections import Counter, defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

WEB = PROJ / "02_wiki/web"
BOARDS = WEB / "data/boards"
BOARD_JSON = BOARDS / "fashion_wardrobe.json"
BOARD_JS = BOARDS / "fashion_wardrobe.js"

PLACEHOLDER_DESC = {"占位占位", "占位", ""}


def load_board() -> dict:
    return json.loads(BOARD_JSON.read_text(encoding="utf-8"))


def save_board(d: dict) -> None:
    BOARD_JSON.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    BOARD_JS.write_text("window.WIKI_BOARD_fashion_wardrobe = "
                        + json.dumps(d, ensure_ascii=False, indent=1) + ";\n",
                        encoding="utf-8")


def is_placeholder(it: dict) -> bool:
    return (it.get("desc") or "").strip() in PLACEHOLDER_DESC


def mini_name(name: str, part: str) -> str:
    """'沙漠珍珠裁切-衣服' → '沙漠珍珠裁切'（去掉部位后缀，卡面小标用）"""
    if part and name.endswith("-" + part):
        return name[: -len(part) - 1]
    return name


def union(a, b):
    out = list(a or [])
    for x in (b or []):
        if x not in out:
            out.append(x)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    d = load_board()
    items = d["items"]

    groups = defaultdict(list)
    for it in items:
        if it.get("model_id") and it.get("part"):
            groups[(it["model_id"], it["part"])].append(it)

    stat = Counter()
    pairs = []          # (正式卡, 占位卡)
    for key, g in groups.items():
        if len(g) < 2:
            continue
        ph = [x for x in g if is_placeholder(x)]
        real = [x for x in g if not is_placeholder(x)]
        if not ph or not real:
            stat["无占位/无正式对"] += 1
            continue
        if len(real) != 1:
            stat["正式卡不唯一"] += 1
            continue
        # 组内多张占位卡 = 同模不同人的套装（如 model 3047 的 敲钟者/王子/经理/舞者
        # 与「考究时光-衣服」同 model 但各有自己的图标与行键），不能并成一张
        if len(ph) > 1:
            stat["组内多张占位卡（同模不同款）"] += 1
            print("  跳过 %s：组内 %d 张占位卡 —— %s" % (
                real[0]["name"], len(ph), "、".join(x["name"] for x in ph)))
            continue
        host = real[0]
        for it in ph:
            if (host.get("grade_level") is not None and it.get("grade_level") is not None
                    and host["grade_level"] != it["grade_level"]):
                stat["品级不同"] += 1
                continue
            if (host.get("charm_value") is not None and it.get("charm_value") is not None
                    and host["charm_value"] != it["charm_value"]):
                stat["魅力不同"] += 1
                continue
            if host["name"].startswith(it["name"].split("-")[0]):
                stat["名字是前缀（另一类）"] += 1
                continue
            pairs.append((host, it))

    for host, it in pairs:
        print("%-16s %-22s ← 并占位卡 %-22s（model %s，魅力 %s，行键 %s）" % (
            host["name"], host["id"], it["name"], it.get("model_id"),
            host.get("charm_value"), ",".join(str(x) for x in (it.get("row_keys") or []))[:40]))
        if a.dry:
            continue

        am = host.get("alias_merge") or {"aliases": [], "ids": [], "row_keys": [], "icon_paths": []}
        am["aliases"] = union(am.get("aliases"), [it["name"]])
        am["ids"] = union(am.get("ids"), [it["id"]])
        am["row_keys"] = union(am.get("row_keys"), it.get("row_keys") or [])
        am["desc"] = union(am.get("desc"), [it.get("desc") or "（空）"])
        paths = [x.get("path") for x in (it.get("icons_all") or []) if x.get("path")]
        am["icon_paths"] = union(am.get("icon_paths"), paths)
        am["note"] = ("表里同 model 同部位的另一条记录，名字是开发/占位名、描述为「%s」，"
                      "已按同一件时装并入本卡" % (it.get("desc") or "空"))
        host["alias_merge"] = am

        # 行键 / 变体名 / model / 时限档 / 图标登记 合并去重
        host["row_keys"] = union(host.get("row_keys"), it.get("row_keys") or [])
        host["name_variants"] = union(host.get("name_variants"), it.get("name_variants") or [])
        host["model_ids"] = union(host.get("model_ids") or host.get("model_id"),
                                  it.get("model_ids") or it.get("model_id"))
        host["durations"] = sorted(set(host.get("durations") or []) | set(it.get("durations") or []))
        host["time_limited_variants"] = sorted(
            set(host.get("time_limited_variants") or []) | set(it.get("time_limited_variants") or []))
        known = {x.get("path") for x in (host.get("icons_all") or [])}
        for ic in (it.get("icons_all") or []):
            if ic.get("path") not in known:
                host.setdefault("icons_all", []).append({"path": ic.get("path"),
                                                        "gender": ic.get("gender"),
                                                        "png": ic.get("png")})
        if host.get("provenance") and it.get("provenance"):
            host["provenance"]["row_keys"] = union(
                host["provenance"].get("row_keys"), it["provenance"].get("row_keys") or [])

        # 占位卡若登记了缺图槽，正式卡也记一笔，别假装图是齐的
        gaps = (it.get("_media") or {}).get("missing") or []
        if gaps:
            hg = host.setdefault("_media", {}).setdefault("missing", [])
            for g in gaps:
                if g not in hg:
                    hg.append(g)
        stat["合并占位卡"] += 1

    gone = {it["id"] for _h, it in pairs}
    if gone and not a.dry:
        by_id = {it["id"]: it for it in items}
        d["items"] = [x for x in items if x["id"] not in gone]
        ma = d.get("merged_away") or []
        for hid in gone:
            src = by_id[hid]
            ma.append({
                "id": hid, "name": src.get("name"), "part": src.get("part"),
                "model_ids": src.get("model_ids"), "provenance": src.get("provenance"),
                "into": next(h["id"] for h, it in pairs if it["id"] == hid),
                "kind": "alias",
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
            "\n\n【同款别名（开发名/占位名）卡合并（2026-10-29）】\n"
            "同 model、同部位、同品级同魅力，且一方描述为「占位占位」开发名时并入正式卡，共 %d 张：%s。\n"
            "正式卡 alias_merge 保留别名/行键/占位描述；卡面标「别名 · XXX」。\n" % (
                len(gone), "、".join(sorted(it["name"] for _h, it in pairs))))

    print("=== 结果 ===")
    for k, v in stat.most_common():
        print("  %-18s %4d" % (k, v))
    print("  cards %d → %d" % (len(items), len(items) - len(gone)))
    if a.dry:
        print("（dry-run，未写盘）")
    else:
        save_board(d)
        print("已写回", BOARD_JSON.name, "与", BOARD_JS.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
