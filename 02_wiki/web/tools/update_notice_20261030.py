# -*- coding: utf-8 -*-
"""更新通知：移除 2026-10-25 已被取代的条目，写入 2026-10-30 本轮更新。"""
from __future__ import annotations

import json
import pathlib

P = pathlib.Path("E:/la拆包项目/02_wiki/web/data/updates.json")

NEW = [
    {
        "date": "2026-10-30",
        "title": "子卡详情大迭代：弹出式大子卡 + 双卡对比",
        "tag": "界面",
        "items": [
            "详情从「就地展开」改为「弹出大子卡」：信息更全，长列表不再把版面撑开",
            "新增大子卡「钉住对比」：点住后自动置于右侧，左侧再选一张即可双子卡并列对比",
            "对比态支持左右切换（←/→）、Esc 退出；对比中仍可继续筛选与搜索",
        ],
    },
    {
        "date": "2026-10-30",
        "title": "内容扩容：时装候选表、载具参数、核芯与芯片换源",
        "tag": "数据",
        "items": [
            "人物时装候选表大幅扩充，新增捏脸、戒指、半感染者花苞等小类；混入的开发名用「仅显示玩家可使用时装」过滤，可取消勾选看全量",
            "载具新增参数：速度上限、加速度、生命值、氮气、专属特性 tag 描述",
            "异变核芯 / 战术芯片更换数据源，覆盖到经典服 12 星（此前上限为简单生存服）",
            "头像、头像框、名片框渲染初步优化；动图与名片框仍是半成品，后续继续做",
            "新定位若干板块并标「内测版」tag：仅初步定位，未筛选与审查格式，数据可用性待维护",
        ],
    },
    {
        "date": "2026-10-30",
        "title": "武器皮肤：音效播放器优化 + 特效正式名",
        "tag": "武器皮肤",
        "items": [
            "2D 图定位与取图逻辑优化，取图命中率提升",
            "武器皮肤音频提取优化，播放器重做：开火 / 命中 / 击败 / 切枪语音逐条试听",
            "特效与战斗表现接入游戏内正式名（如「辉光绽放」「咏叹终章」），备注名与资源名保留",
            "README 效果预览换成八张实机截图：首页 / 时装 / 武器皮肤 / 载具 / 对比 / 核芯 / 芯片 / 场景平衡",
        ],
    },
]


def main() -> int:
    rows = json.loads(P.read_text(encoding="utf-8"))
    before = len(rows)
    rows = [r for r in rows if r.get("date") != "2026-10-25"]
    rows = NEW + rows
    P.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print("条目 %d → %d（删 %d 条 2026-10-25 旧条目，新增 %d 条 2026-10-30）"
          % (before, len(rows), before - len(rows) - len(NEW) + len(NEW), len(NEW)))
    for r in rows:
        print(" ", r["date"], r["title"], "·", len(r["items"]), "条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
