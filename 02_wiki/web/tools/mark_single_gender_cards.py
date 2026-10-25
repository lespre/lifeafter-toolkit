# -*- coding: utf-8 -*-
"""单性别款的卡：把 gender 统一标成「仅女款」，并保留原始字段。"""
import json
import pathlib

BOARD = pathlib.Path("E:/la拆包项目/02_wiki/web/data/boards/fashion_wardrobe.json")


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    n = 0
    for it in d["items"]:
        if not it.get("gender_scope"):
            continue
        it.setdefault("gender_raw", it.get("gender"))
        it["gender"] = "仅女款"
        it["gender_scope_note"] = ("%s：player_appear_data 该 model 带 force_gender，游戏只做女款，"
                                   "因此没有男装图" % it.get("gender_scope"))
        n += 1
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("单性别卡标注为「仅女款」%d 张" % n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
