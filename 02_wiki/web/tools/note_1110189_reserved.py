# -*- coding: utf-8 -*-
"""把 1110189 的穷举负证据写进卡面与报告，避免以后再挖一遍。"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path("E:/la拆包项目")
BOARD = ROOT / "02_wiki/web/data/boards/weapon_skin_sfx_text_sources.json"
MD = ROOT / "01_索引与产物/30_分析/1110189_穷举结论_20261025.md"

EVID = [
    "全表扫描：经典服 cdata 12,451 张 + oversea 关键词表 1,508 张，仅 weapon_skin_behavior_res_data 一行命中 key=1110189。",
    "区域皮肤表：oversea 下 12 张 weapon_skin_data_auto_oversea_data_*.py 全是 ~310 B 桩，均无该行。",
    "第二源藏宝阁（cbg game_auto_config.js，25 MB）：有 1110187 前方禁行 / 1110188 一魂共鸣 / 1110190 佳期如梦，**没有 1110189**。",
    "资源侧：skin_1013_010 在 names_join 0 命中；icon_1110189_s/_b 0 命中。",
    "结论：预留条目（未发布）。不是资源没下完，而是主表与道具行都没配。",
]

MD_TXT = "# 1110189 穷举结论（2026-10-25）\n\n" + "\n".join("- " + e for e in EVID) + "\n"


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    for it in d["items"]:
        if it["id"] != "1110189":
            continue
        it["name_status"] = "reserved_unreleased"
        it["evidence_level"] = "structure-only"
        it["reserved_note"] = " | ".join(EVID)
        it["name_resolution"] = {
            "state": "reserved_unreleased",
            "rule": "主表/道具行/资源/第二源四处同时缺失 ⇒ 预留条目；名字无从得出，禁猜。",
        }
        print("已写卡面：", it["name_display"], "|", it["name_status"])
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    MD.write_text(MD_TXT, encoding="utf-8")
    print("报告", MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
