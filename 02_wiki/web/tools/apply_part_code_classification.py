# -*- coding: utf-8 -*-
r"""分类写死：一切按「部位码」判定，不按名字、不按旧字段。

部位码 → 桶（本轮用三张表的实测取值定死）：

  fashion_data.part_type（与其 new_fashion_id_str 前缀互斥，取其一）
      cloth→衣服  hat→头发  bag→背包  light→荧光棒  suit→整套

  player_appear_data.part（数字码）+ part_type 细化
      1→头发  2→捏脸  3→衣服/整套(part_type=suit)  4→背包
      5→荧光棒(light)/挂饰(pendant)/挂饰(其他)  6→戒指  7→半感染者花苞

  player_module_appear_data.part
      1→头发  2→头饰  20001→面饰

匹配顺序：row_keys 命中 fashion_data → player_appear_data → 按名字命中挂件表 → 保持原样并标 part_unresolved。
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys

PROJ = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
import add_fashion_style_fields as A  # noqa: E402
from board_io import write_board_pair  # noqa: E402

BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"

FASHION_MAP = {"cloth": "衣服", "hat": "头发", "bag": "背包", "light": "荧光棒", "suit": "整套"}
APPEAR_NUM = {"1": "头发", "2": "捏脸", "3": "衣服", "4": "背包", "6": "戒指", "7": "半感染者花苞"}
MODULE_MAP = {"1": "头发", "2": "头饰", "20001": "面饰"}


def sv(x):
    return x[1] if isinstance(x, tuple) else x


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    fash, _, _ = A.load("fashion_data")
    by_fk = {}
    for r in fash:
        v = r["values"]
        pt = str(sv(v.get("part_type")) or "") or str(sv(v.get("new_fashion_id_str")) or "").split("_")[0]
        part = FASHION_MAP.get(pt)
        if part:
            by_fk[int(r["key"])] = part

    app, _, _ = A.load("player_appear_data")
    by_ak = {}
    for r in app:
        v = r["values"]
        code = str(sv(v.get("part")) or "")
        pt = str(sv(v.get("part_type")) or "")
        part = APPEAR_NUM.get(code)
        if code == "3" and pt == "suit":
            part = "整套"
        if code == "5":
            part = "荧光棒" if pt == "light" else "挂饰"
        if part:
            by_ak[int(r["key"])] = part

    mod, _, _ = A.load("player_module_appear_data")
    by_mod = {}
    for r in mod:
        v = r["values"]
        nm = str(sv(v.get("name")) or "").strip()
        part = MODULE_MAP.get(str(sv(v.get("part")) or ""))
        if nm and part:
            by_mod.setdefault(nm, part)

    print(f"号码表：fashion {len(by_fk)} ｜ appear {len(by_ak)} ｜ module {len(by_mod)}")

    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]
    trans = collections.Counter()
    unresolved = 0
    for it in items:
        want, src = None, None
        for k in (it.get("row_keys") or []):
            if int(k) in by_fk:
                want, src = by_fk[int(k)], "fashion_data.part_type（部位码写死）"
                break
        if want is None:
            for k in (it.get("row_keys") or []):
                if int(k) in by_ak:
                    want, src = by_ak[int(k)], "player_appear_data.part（部位码写死）"
                    break
        if want is None:
            nm = (it.get("name") or "").strip()
            if nm in by_mod:
                want, src = by_mod[nm], "player_module_appear_data.part（部位码写死）"
        if want is None:
            unresolved += 1
            it["part_source"] = "unresolved：无部位码可依"
            continue
        if it.get("part") != want:
            trans[(it.get("part"), want)] += 1
        it["part"] = want
        it["part_label"] = want
        it["part_bucket"] = [want]
        it["part_source"] = src

    print("分类迁移：", dict(trans.most_common(12)))
    print("无部位码可依：", unresolved, f"（{unresolved/len(items)*100:.1f}%）")
    print("迁移后分布：", dict(collections.Counter(i.get("part") for i in items)))

    if a.apply:
        meta = d.setdefault("meta", {})
        meta["part_rule"] = ("部位码写死：fashion_data.part_type/新ID前缀 → cloth衣服 hat头发 bag背包 "
                             "light荧光棒 suit整套；player_appear_data.part 1头发 2捏脸 3衣服(suit整套) "
                             "4背包 5荧光棒(light)/挂饰(pendant) 6戒指 7半感染者花苞；"
                             "player_module_appear_data.part 1头发 2头饰 20001面饰。不按名字判。")
        write_board_pair(BOARD, d)
        print("已写盘")
    else:
        print("（dry-run，未写盘）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
