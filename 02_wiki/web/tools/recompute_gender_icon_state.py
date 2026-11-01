# -*- coding: utf-8 -*-
r"""重算 gender_icon_state（缺男图/缺女图/缺图），按「实际有没有图 + 该部件是否本来就分性别」。

现有 bug（repair_fashion_posters.py 拼串所致）：
  缺图图 133 ｜ 缺女/男图 130 —— 空性别/双缺被拼进标签
  176 张标「缺女图」、169 张标「缺男图」，实际男女图都没有 ⇒ 应标「缺图」
  单性别款（仅女/仅男）不该被标缺另一侧

判定：
  has_f / has_m 看 _media.images 的文件名（_f_ / _m_）
  期望性别：gender_scope=仅女→女；仅男→男；双版→女+男；通用/空→看现有图，不要求成对
  → 双版：缺一侧标缺那侧，都没有标「缺图」
  → 单版：缺自己那侧标缺那侧，其余不标
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re

PROJ = pathlib.Path("E:/la拆包项目")
BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
sys_path = PROJ / "02_wiki/web/tools"


def main() -> int:
    import sys
    sys.path.insert(0, str(sys_path))
    from board_io import write_board_pair  # noqa: E402
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]
    before = collections.Counter(i.get("gender_icon_state") or "(无)" for i in items)
    after = collections.Counter()
    changed = 0

    for it in items:
        imgs = ((it.get("_media") or {}).get("images") or [])
        blob = " ".join(str(im.get("png", "")) for im in imgs)
        # 图自带 label：女 / 男（文件名不可靠：多数卡两张图都不带性别后缀）
        labels = [str(im.get("label") or "") for im in imgs]
        label_list = labels
        has_f = any("女" in x for x in labels)
        has_m = any("男" in x for x in labels)
        if not imgs:
            has_f = has_m = False

        scope = (it.get("gender_scope") or "").strip()
        gender = (it.get("gender") or "").strip()
        want_f = want_m = False
        if scope == "仅女" or gender == "女":
            want_f = True
        elif scope == "仅男" or gender == "男":
            want_m = True
        elif scope == "双版" or gender == "女/男":
            want_f = want_m = True
        else:
            # 通用/未知：有图就不要求成对，没图就记「缺图」
            want_f = want_m = False

        generic = any(("图示" in x or "图标" in x or not x) for x in labels) if label_list else False
        if not imgs:
            state = "缺图"
        elif want_f and want_m:
            if has_f and has_m:
                state = None
            elif has_f:
                state = "缺男图"
            elif has_m:
                state = "缺女图"
            else:
                state = None          # 只有通用图，无法判断缺哪一侧
        elif want_f:
            state = None if has_f else ("缺女图" if not has_m else "缺女图")
        elif want_m:
            state = None if has_m else ("缺男图" if not has_f else "缺男图")
        else:
            state = None

        old = it.get("gender_icon_state")
        if state is None:
            if old:
                it.pop("gender_icon_state", None)
                changed += 1
        elif old != state:
            it["gender_icon_state"] = state
            changed += 1
        after[it.get("gender_icon_state") or "(无)"] += 1

    print("改前", dict(before))
    print("改后", dict(after))
    print("变化卡数", changed)
    if a.apply:
        write_board_pair(BOARD, d)
        print("已写盘")
    else:
        print("（dry-run，未写盘）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
