# -*- coding: utf-8 -*-
"""给伤害三张板写入可渲染的公式块（meta.formula）。

公式全部来自各板 items 的「算法/数值」字段（PE 表实测值），不新增推断。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
sys.path.insert(0, str(WEB / "tools"))
from board_io import write_board_pair  # noqa: E402

F = {
    "damage_attack": [
        {"t": "① 基础攻击",
         "e": "A₁ = A₀ × (1 + hurt_ratio)",
         "n": "A₀=武器面板攻击，hurt_ratio=攻击力加成（表内 hurt_ratio 列）。"},
        {"t": "② 扣护甲",
         "e": "A₂ = A₁ − 护甲",
         "n": "护甲扣除发生在折线之前，不参与分段。"},
        {"t": "③ 分段折线（经典服 30/50/70/100）",
         "e": "0≤x<30: y=x ｜ 30≤x<50: y=0.7x+9 ｜ 50≤x<70: y=0.5x+19\n"
              "70≤x<100: y=0.3x+33 ｜ x≥100: y=0.1x+53",
         "n": "简单生存服断点 50/60/70/100：y=x｜0.7x+15｜0.5x+27｜0.3x+41｜0.1x+61。"
              "月卡服该表缺 source_hurt 列 ⇒ 不做折线这一步。"},
        {"t": "④ 下限",
         "e": "y = max(y, min(min_attack × M, min_attack))",
         "n": "经典服 min_attack=12、M=0.4 → 下限 4.8；简单生存 24、0.4 → 9.6；月卡默认 10、0.3 → 3.0。"},
        {"t": "⑤ 修正",
         "e": "y ← y × 无人机系数 × 战术系数",
         "n": "①②⑤ 三服同；差异只来自 ③ 的断点与 ④ 的 min_attack / M。"},
    ],
    "damage_bonus": [
        {"t": "① 加成桶求和",
         "e": "rate = 1 + Σ桶ᵢ",
         "n": "桶ᵢ 为各条伤害加成（装备/技能/称号/场景等），同类桶相加，不同类互乘由各自桶定义。"},
        {"t": "② PvP 配对项",
         "e": "rate ← rate + 攻方加成 − 守方减免",
         "n": "仅玩家对玩家加入；守方减免指 player_hurt_reduction_rate，是配对项，不是守方自身减伤桶。"},
        {"t": "③ 夹窗口",
         "e": "rate = min(上限, max(下限, rate))",
         "n": "夹的是 rate 本身，不是 delta。经典远星城 23 窗口 [0.75, 1.80]。"},
        {"t": "④ 分段折线（只作用于 delta）",
         "e": "delta = rate − 1 ；若 delta>0 或曲线首端≤0 ⇒ delta = k·delta + b",
         "n": "经典远星城 23：[0,0.2] 1x+0｜[0.2,0.4] 0.7x+0.06｜[0.4,0.6] 0.4x+0.18"
              "｜[0.6,1] 0.25x+0.27｜[1,∞] 0.1x+0.42。delta≤0 且首端>0 时原样返回。"},
        {"t": "⑤ 最终倍率与伤害",
         "e": "生效倍率 = 1 + delta ；伤害 = 攻击侧结果 × 生效倍率",
         "n": "算例：加成 1.6、减免 1.8 → net 0.80 → delta −0.20 → 生效 0.80（下限 0.80 托住）。"},
    ],
    "damage_defense": [
        {"t": "① 目标自身桶合成",
         "e": "t = ∏(1 + 目标增伤桶) × ∏(1 − 目标减伤桶)",
         "n": "这里的「目标减伤桶」属于守方自身属性，与加成环节的 player_hurt_reduction_rate 是两条不同的量。"},
        {"t": "② 过 b_class 折线",
         "e": "d = t − 1 ；d = k·d + b",
         "n": "b_class：(0,0.8) 1x+0｜(0.8,1.0) 0.6x+0.32｜(1.0,∞) 0.1x+0.82。三服逐值相同。"},
        {"t": "③ 作用到本次伤害",
         "e": "damage ← damage × (1 + d) + 额外伤害",
         "n": "额外伤害在乘算之后加，不受桶影响。"},
        {"t": "④ 上限与取整",
         "e": "damage = ceil(min(damage, 目标最大HP × c_class 上限))",
         "n": "c_class：(0,1.0) 1x+0｜(1.0,1.2) 0.6x+0.4｜(1.2,∞) 0.1x+1.0。"},
    ],
}


def main() -> int:
    for bid, rows in F.items():
        p = WEB / f"data/boards/{bid}.json"
        board = json.loads(p.read_text(encoding="utf-8"))
        board["meta"]["formula"] = rows
        write_board_pair(p, board)
        print(f"{bid}: 写入 {len(rows)} 条公式")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
