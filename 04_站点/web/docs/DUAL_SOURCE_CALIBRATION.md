# 业务定位链双服双版本校准总表（DUAL SOURCE CALIBRATION v1）

> 2026-09-06 用户定版铁律「wiki 各种东西都要双版本双服校准」落地文件。
> 机器数据：`data/external_refs/dual_source_calibration.json`（tools/calibrate_business_chains.py 全链生成）
> 每表判定：同 FID=同文件=双源共享（经典服同读）；FID 正式 npk 无=BA8/简单服专属。
> 注意：kjxq「多 BA8 专属」非铁律（vehicle_lottery kjxq 003023=双源共享特例）——逐表以校准器输出为准。

## 链级总览

| 链 | 文件数 | 双源共享 | BA8专属 | 视角结论 |
|---|---|---|---|---|
| lottery（时装抽奖/奖池） | 127 | 46 | 81 | 主表双源（super_fashion 012591 等）；kj1/kjxq 覆盖=BA8 专属 |
| manjian（满减） | 15 | 0 | 15 | **满减市场=BA8/简单服视角**（goods 表 kjxq/kj1 全 BA8 专属） |
| mystery（神秘商店） | 0 | - | - | 无 random_discount 表名命中=商品表静态缺失实证（huodong 仅 3 期注册） |
| nucleus（核芯研制） | 39 | 7 | 32 | 主表 ykxq huodong 双源；nucleus_build 分服版本（经典 76/BA8 75） |
| chip（芯片保底） | 24 | 4 | 20 | conf/rule 双源共享同文件但启用不同（简单=连环暴击组/经典=破盾强攻组） |
| vehicle（载具） | 36 | 26 | 10 | 多双源（vehicle_lottery kjxq 003023=特例双源）；v2 新表 BA8 侧 |
| chenshi（宸世臻藏） | 60 | 23 | 37 | optional_hd_exchange 主表 002962/yk 005580 双源共享；kjxq 覆盖 BA8 |
| huodong（活动目录） | 56 | 14 | 42 | ykxq 全量双源；kj1/kjxq 覆盖层 BA8 |
| fashion（时装/外观名册） | 316 | 114 | 202 | 主表族多双源共享（fashion_data/player_appear/buff 等）；kj1/kjxq 变体 BA8 |

## 板→链映射与视角标注现状（20 已发布板）

| 板 | 链 | 双源标注现状 |
|---|---|---|
| lottery_kaijia_panel_static / future_lottery_preview | lottery | 备注含双源（主表共享/覆盖 BA8）——rebuild 轮统一加 meta.dual_source |
| nucleus_lottery_panel_static / nucleus_cards_classic | nucleus | classic 板已带 server_branch 筛选器（76+1）；期次板=ykyxq 双源共享+BA8 conf 覆盖=备注 |
| chip_lottery_guarantee_panel_static / chip_item_catalog | chip | 期次=公告/用户锚（双服）；conf 同文件双启用差异已注明 |
| manjian_market_panel_static | manjian | **BA8/简单服视角**（goods 全 BA8 专属）——标注为「简单服静态；经典服=运行时/内容不同」 |
| mystery_shop_panel_static | mystery | BA8 3 期注册+商品缺失=「BA8 静态注册；商品=运行时」 |
| exchange_static_structure | 通用兑换 | common_exchange_shop_data（**非宸世**，27.106 勘误） |
| fashion_*（wardrobe/face/bag/glow/projection/bestplay） | fashion | 主源多双源共享；待 rebuild 统一标注 |
| weapon_attrs_schema_static / weapon_skin_sfx_text_sources / skin_behavior_preview | fashion/武器 | schema 地基=双源共享结构；SFX 行为=BA8 视角 |
| common_item_text_sources / gift_data_text_sources | fashion/道具 | BA8 工作副本快照=简单服视角；正式服同 FID 处已注明 |

## 各链关键差异结论（校准器实证节选）

- **manjian**：manjian_market_goods kjxq/kj1 chs=全 BA8 专属→ 满减市场表=BA8 打包；经典服满减=
  服务端/另通道（勿默认同内容）。
- **vehicle**：vehicle_lottery_base_conf kjxq（003023）=**双源共享**（修正「kjxq=BA8 专属」绝对化）；
  new_vehicle_lottery_v2_conf_data=BA8 侧新表（海外壳 BA8 专属）——v2 抽奖=BA8/简单服新配置。
- **chenshi**：optional_hd_exchange_shop_data 主 002962/yk 005580=双源共享=经典服同读；kjxq 覆盖 BA8。
- **huodong**：ykxq（024329/F394516378015E27+021919/DACF87AE00F14120）=双源共享全量；
  kj1 025079/kjxq 001941=BA8 专属覆盖。
- **nucleus**：nucleus_build_data 分服版本不同（经典 40949/695 池 76 行 vs BA8 016783/519 池 75 行）；
  12 星段=经典专属（BA8 只到 5 星）。
- **lottery**：主表族（super_fashion/reward_pool 021380 等）双源共享；kj1/kjxq 覆盖=BA8 专属
  （铠甲类活动面板差异源）。

## 板级标注计划（rebuild 轮统一执行）

每个已发布板 rebuild 时 meta 增加 `dual_source` 字段：
- `shared-main`：主源表双源共享（经典/简单同读），差异=覆盖层 BA8 → 默认两服一致+覆盖差异注明
- `ba8-scope`：主源仅 BA8（manjian/mystery 商品类）→ 标注「简单服静态；经典服运行时」
- `split-branch`：分服版本不同（nucleus_build/conf 启用差异）→ 用 server_branch 筛选器或差异并列
对应板：manjian_market_panel_static=ba8-scope、mystery_shop_panel_static=ba8-scope、
nucleus_cards_classic=split-branch（已有筛选）、chip 期次板=split-branch（双服名单差异注明）、
fashion 各板=shared-main、lottery 板=shared-main（覆盖差异注）。
