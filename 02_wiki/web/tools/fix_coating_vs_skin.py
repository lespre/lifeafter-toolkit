# -*- coding: utf-8 -*-
"""纠正：涂装(coating) 与 皮肤(skin) 是两套系统。

- 10854 = 涂装物品「幻海典藏」(equip_coating_data key 105643, coating_icon ui/tuzhuang_icon/icon_tuzhuang_193.png)
- 1110189 是武器皮肤（传世），与 10854 涂装无关，名字仍未知
"""
from __future__ import annotations
import sys

import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

ROOT = pathlib.Path(PROJ)
BOARD = ROOT / "02_wiki/web/data/boards/weapon_skin_sfx_text_sources.json"
ATT = ROOT / "02_wiki/web/data/weapon_skin_audio_attachments.json"

NOTE = ("系统区分：皮肤(weapon_skin_data, skin_id→model_path) 与 涂装(equip_coating_data, coating_name→item_id) 是两套。"
        "10854 是涂装物品「幻海典藏」，不是皮肤 id；1110189 的皮肤位是 skin_1013_010，资源未下发。")


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    for it in d["items"]:
        if it["id"] != "1110189":
            continue
        it["name"] = None
        it["name_display"] = "未命名皮肤 · ID 1110189"
        it["name_status"] = "unresolved"
        it["name_resolution"] = {
            "state": "unresolved",
            "rule": "无同快照主数据行与道具行；10854 属涂装系统，不能用作皮肤名。",
        }
        it["official_name_status"] = "unresolved"
        it["variant_kind"] = "武器皮肤（skin），非涂装"
        it["variant_note"] = NOTE
        it.pop("equip_id", None)
        print("已回退 1110189 名称：", it["name_display"])

    d.setdefault("meta", {})["systems_note"] = (
        "本板只收录武器皮肤（skin）。涂装(coating) 另有系统：equip_coating_data，字段 coating_name/item_id/"
        "coating_icon，例：幻海典藏 → item_id 10854 → ui/tuzhuang_icon/icon_tuzhuang_193.png。两套不可混用。")
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")

    a = json.loads(ATT.read_text(encoding="utf-8"))
    rec = a["skins"].get("1110189")
    if rec:
        rec["name"] = "未命名皮肤 · ID 1110189"
        rec["evidence"] = rec.get("evidence", "").split(" ｜ 名称口径")[0]
        ATT.write_text(json.dumps(a, ensure_ascii=False, indent=1), encoding="utf-8")
    print("attachments 同步完成")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
