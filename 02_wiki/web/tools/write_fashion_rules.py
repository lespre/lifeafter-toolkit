import sys
# -*- coding: utf-8 -*-
"""把时装补图/去重/单性别的规则沉淀进板级技术详情（meta.notes）。"""
import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import BOARDS_DIR  # noqa: E402

BOARD = pathlib.Path(BOARDS_DIR / "fashion_wardrobe.json")

RULES = """

【图标命名与取图规则（2026-10-25 实证，补图必读）】
① 命名结构  icon_<部位>_<性别>_<model><序号><尺寸档>
   部位  b=衣服  h=头饰  bag=背包  light=光源  suit=整套
   性别  f=女  m=男      序号 001 起（同套多件递增）
   尺寸  _b 大图 300×150 ｜ _s 小图 154×78（同一张图的两个档，不是两张图）
② 取图顺序（按命中率）
   1) 卡上 icons_all 里登记的路径，补 _b / _s 再试
   2) 按 model + 部位 + 性别 直造候选：icon_<部位>_<f|m>_<model>001_b
   3) 表里该 model 的 icons 组（仅当 fashion_data 有该部位行时才有）
③ 去重  同 base 去掉 _b/_s 后相同即视为同一张图，只保留一张（优先 _b）
④ 单性别款   player_appear_data 该 model 带 force_gender ⇒ 游戏只做一种性别（如 不湮之花、白月魁、嘉心予梦、贝极星愿、琳夜柔歌），不追另一性别，卡面标注「仅单性别」
⑤ 已证不存在的路径  部分卡 icons_all 登记的 icon_* 在 182 个包内查无实体（如 icon_h_f_3002005_b、icon_366053_1_b、icon_mvp06），属未下发资源，不要反复重试
⑥ 男图口径  背包/挂件本不分性别；真正待补的只有衣服与头饰
"""


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    notes = str(d["meta"].get("notes") or "")
    if "图标命名与取图规则" not in notes:
        d["meta"]["notes"] = notes.rstrip() + RULES
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("技术详情已写入取图规则，notes 长度", len(d["meta"]["notes"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
