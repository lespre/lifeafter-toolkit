# -*- coding: utf-8 -*-
"""单性别款的卡：把 gender 统一标成「仅女款」，并保留原始字段。

2026-10-30：注记改为引用 gender_scope_note（由 mark_single_gender.py 写入，含具体证据：
force_gender 锁定 / 男款行未绑资源），不再在这里重复一套说法，避免两处口径漂移。
"""
import json
import pathlib

BOARD = pathlib.Path("E:/la拆包项目/02_wiki/web/data/boards/fashion_wardrobe.json")


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    n = 0
    for it in d["items"]:
        if not it.get("gender_scope"):
            continue
        if it.get("gender_raw") is None:
            it["gender_raw"] = it.get("gender")
        it["gender"] = "仅女款"
        n += 1
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("单性别卡标注为「仅女款」%d 张" % n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
