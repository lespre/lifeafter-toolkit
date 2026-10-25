# -*- coding: utf-8 -*-
"""时装板：删掉「全量登记表」入口；把图标命名规律写进技术详情（meta.notes）。"""
from __future__ import annotations

import json
import pathlib

WEB = pathlib.Path("E:/la拆包项目/02_wiki/web")
BOARD = WEB / "data/boards/fashion_wardrobe.json"

NOTES = """全量重建：11,036 行 → 2,016 张卡（归一名字 + 部位 + model_id）。部位分布 {bag 500 / cloth 838 / suit 57 / hat 575 / light 227}。

【图标命名有两套，并存】
① 部位+性别式（2,124 个）：icon_<部位>_<f|m>_<model><序号>
   部位代码  b=衣服  h=头饰  bag=背包  light=光源  suit=整套
   例  icon_b_f_5004001（女衣服）/ icon_b_m_5004001（男衣服）
       icon_h_f_3331001（女头饰）/ icon_h_m_3331001（男头饰）
       icon_bag_f_3277001 / icon_bag_m_3277001
② 编号式（1,059 个）：icon_<num>_1（男）/ icon_<num>_2（女）
③ 纯编号（371 个）：icon_<num>，只有一张图

【取图规则】
· 实际文件一律带尺寸档后缀：_b（大图，300×150）/ _s（小图，154×78）
· 游戏取图入口 com/utils/UIHelpers.py → ui/item_icon/%s.png + 档位
· 男图只存在于部位+性别式或编号式两类；纯编号类本就没有性别区分

【已知缺口】
· 背包/挂件本不分性别（同一模型男女通用），不追男图属正常
· 部分外观只在 player_appear_data 登记、fashion_data 无行（如 不湮之花-头饰 行 1500401），此类条目在表里没有 icon 字段
· appear_id → equip_id 映射表（appear_id_2_equip_id）为 bindict 加密容器（0x7b + u32 长度 + 加密载荷），尚未解开"""


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    m = d["meta"]
    m.pop("registry", None)
    m["notes"] = NOTES
    m.pop("notes_hidden", None)
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("已删除 registry 入口，技术详情已写入 %d 字" % len(NOTES))

    for name in ("registry.html",):
        p = WEB / name
        if p.is_file():
            p.unlink()
            print("已删除", name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
