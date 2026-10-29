# -*- coding: utf-8 -*-
"""重写 README「效果预览」为 8 张新截图（顺序按用户指定）。"""
from __future__ import annotations

import pathlib
import re

P = pathlib.Path("E:/la拆包项目/README.md")

NEW = """## 效果预览

**① Wiki 首页** —— 31 个公开板块、170,144 条记录，按四类档案归档，顶部展示构建版本与部署信息；
搜索框可直接跳板块，快捷入口直达武器皮肤 / 异变核芯 / 载具

![Wiki 首页](00_规范与工具/治理/手册/images/web-wiki.jpg)

**② 人物时装** —— 2,899 件候选（含捏脸、戒指、半感染者花苞等小类），默认勾选「仅显示玩家可使用时装」
过滤混入的开发名，可取消勾选查看全量；部位 / 品级 / 性别 / 编号多维筛选，卡面标品级、魅力值、model

![人物时装](00_规范与工具/治理/手册/images/web-fashion.jpg)

**③ 武器皮肤** —— 122 款，卡片直出 3D 渲染；弹窗内可看特效与战斗表现（游戏内正式名 + 备注名）
与**皮肤音效逐条试听**（含开火 / 命中 / 击败 / 切枪语音）

![武器皮肤](00_规范与工具/治理/手册/images/web-weapon-skin.jpg)

**④ 载具** —— 174 辆，按类型（跑车 / 摩托车 / 特色载具 / 吉普车 / 飞行载具 / 马匹）与子类筛选；
卡面给出**速度上限、加速度、生命值、氮气、专属特性 tag**，含联动 IP 与编号

![载具](00_规范与工具/治理/手册/images/web-vehicle.jpg)

**⑤ 子卡对比** —— 任意卡片「弹出大子卡」查看全量信息；点「钉住对比」置右，左侧再选一张即可
双卡并列对比（←/→ 切换，Esc 退出）

![子卡对比](00_规范与工具/治理/手册/images/web-compare.jpg)

**⑥ 异变核芯** —— 132 条，核芯与 5★ / 9★ / 12★ 特技合并展示；品级、星上限、专属特技逐条标注，
支持经典服范围的 12 星

![异变核芯](00_规范与工具/治理/手册/images/web-core.jpg)

**⑦ 战术芯片** —— 按类型（进攻 / 防御）与编号筛选；弹窗内按档位（1–12 档）列出熟练度与
`base_params` 数值，并高亮当前档位

![战术芯片](00_规范与工具/治理/手册/images/web-chip.jpg)

**⑧ 伤害场景平衡** —— 573 行场景加成档位，可按服型（经典服 / 简单生存服）、来源类型、PvP/PvE 筛选；
给出加成上下限、加成区间与生效最低攻击

![场景平衡](00_规范与工具/治理/手册/images/web-scene.jpg)
"""


def main() -> int:
    s = P.read_text(encoding="utf-8")
    start = s.index("## 效果预览")
    end = s.index("---\n\n## 三线三带")
    s = s[:start] + NEW + "\n" + s[end:]
    s = s.replace("- **32 个板块 / 168,866 条数据**", "- **31 个板块 / 170,144 条数据**")
    P.write_text(s, encoding="utf-8")
    imgs = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", NEW)
    print("新版效果预览图片数", len(imgs))
    for p in imgs:
        f = pathlib.Path(p)
        print("  ", "OK " if f.is_file() else "缺 ", p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
