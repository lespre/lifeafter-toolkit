# -*- coding: utf-8 -*-
"""站点更新通知：补本轮改动（场景平衡表格化 / 外观合并 / 种族修订 / MVP 修复 / 树归一）。"""
from __future__ import annotations
import sys

import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import DATA_DIR  # noqa: E402

P = pathlib.Path(DATA_DIR / "updates.json")

NEW = [
    {
        "date": "2026-10-26",
        "title": "场景平衡改表格 + 场景类型筛选",
        "tag": "图鉴",
        "items": [
            "场景加成平衡子卡改为表格视图，表头可点击排序",
            "按 服型 / 来源类型 / 场景类型 三档筛选",
            "场景类型按 space_data.map_tag 分五档：PvP 对抗 56 · PvE 副本 199 · 开放世界 237 · 特殊活动 51 · 营地城镇 8（另有 22 条无场景号）",
            "删掉目录外孤立的静态表页，入口统一走板块页",
        ],
    },
    {
        "date": "2026-10-26",
        "title": "人物时装：其他外观并入 + 部位七类",
        "tag": "图鉴",
        "items": [
            "「其他外观」整板并入人物时装，按 part_code 归位：头饰 / 捏脸 / 衣服 / 背包 / 挂饰 / 戒指 / 半感染者花苞",
            "部位筛选补齐七类，另保留 光源 / 整套 两档",
            "默认只显示有图（1,751 / 2,807）；新增「仅玩家可见名」勾选，可一键隐藏 786 条开发名",
            "技术详情写入部位口径与显示口径",
        ],
    },
    {
        "date": "2026-10-26",
        "title": "种族潜能修订",
        "tag": "图鉴",
        "items": [
            "去掉「通用（无种族专属）」这个不存在的种族（15 条移出板面）",
            "现行「半感染者」对应数据里的械骨人；旧称再生者对应现在的半感染者",
            "保留：人类 18 · 半感染者 15 · 械骨人 15",
        ],
    },
    {
        "date": "2026-10-26",
        "title": "MVP 沙海月鸣补齐 + 数据树归一",
        "tag": "其他",
        "items": [
            "补齐 MVP 图标：0000.gpk 第 12735 行（300×150），立绘去黑底转透明",
            "删除男款结算截图；mvp_08 标注为仅女款（官方未做男款）",
            "cdata 三份合成一份（33,601 表），旧目录改名留档后清理",
            "PC 还原树停止维护并移除（36 GB），脚本层并入 PE 归一树",
        ],
    },
]


def main() -> int:
    d = json.loads(P.read_text(encoding="utf-8"))
    titles = {x.get("title") for x in d}
    added = 0
    for x in NEW:
        if x["title"] not in titles:
            d.insert(0, x)
            added += 1
    P.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print("新增通知 %d 条，当前共 %d 条" % (added, len(d)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
