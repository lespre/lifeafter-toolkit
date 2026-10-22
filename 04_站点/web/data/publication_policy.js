window.WIKI_PUBLICATION_POLICY = {
  "schema": "lifeafter-wiki-publication-policy-v2",
  "generated": "2026-09-10",
  "policy": "默认拒绝。Wiki v0.1 允许既有非冲突已验板，以及通过 P4 简化总验收的四个冻结产物板；unresolved/quarantined 不得伪装为 verified，runtime final 未证明即 unknown。",
  "boards": {
    "chip_item_catalog": {
      "publication_status": "published_hidden",
      "category": "三、战力类 / （四）芯片",
      "reason": "芯片图鉴 v2：chip_type 池 003278 中文短名 65 全集（=游戏图鉴同源，用户 UI 65 实证）；id 挂接=common_item 道具行 56 + USER 锚 conf 引用 2（坚如磐石=331026/坚韧不拔=331018）+9 配置名无道具行（id 静态不可得 6+未知 3）。品级/效果文本无静态源。",
      "items": 65,
      "superseded_by": "tactical_chip_full",
      "note": "已被 tactical_chip_full 取代，保留直链，不进首页导航"
    },
    "fashion_face": {
      "publication_status": "quarantined",
      "reason": "从两个 legacy CHS 全池以正则筛选名称，未建立 table row→name/part/time 关系；池内字符串存在不等于该字符串是面饰记录。"
    },
    "fashion_kaijia": {
      "publication_status": "quarantined",
      "reason": "以预先手写的联动名集合从启发式时装字符串中命中；未保存逐行 key、字段位置、同包名称来源，不能作为联动外观或缺项结论。"
    },
    "fashion_wardrobe": {
      "publication_status": "published",
      "reason": "★ 2026-09-28 解除隔离并转 published。原隔离理由两条已解：① 「名字/部件取整行 CHS 字符串的正则启发式」→ 改用【表结构解析产物】的 name / part_type 字段（BinDict 按 schema 逐行解出，非正则）；② 「聚合后丢失原表 row key，不能回溯」→ 每条带 row_keys（该外观的全部 row_key，可回溯）。★ join 口径 = 归一名字（剥部件后缀 / 剥「·XXX」/ 剥时效包装）；禁用 model_id —— 旧板与表的 model_id 交集 0，数字相等是巧合（实测 76.9% 假命中）。★ 名字只从 fashion_data 来（玩家可见表）；player_appear_data 是部件工程表，只作 desc 补源（混入会把「005high套（女）」「100级甲」等内部工程名当时装名，实测踩过）。覆盖 1253 件 / desc 1224 件（97.7%）/ row_keys 100%。证据等级 = structure（静态度量，非运行时可证）。",
      "category": "一、时装类 / （一）人物时装",
      "items": 1253
    },
    "gift_data_text_sources": {
      "publication_status": "published",
      "reason": "当前 Documents BA8 包的 gift_data base/CHS 同快照行级文字表。每条名称与说明均保留 row key、字段 CHS 槽位、文本值 CHS 槽位与 decoded payload SHA；仅为文本来源，不表示礼盒可得、可开启、奖励、价格、货币、限购或活动启用。",
      "category": "一、道具总表 / （二）礼盒"
    },
    "nucleus_cards_classic": {
      "publication_status": "published_hidden",
      "category": "三、战力类 / （三）核芯",
      "reason": "核芯卡定版（双服合并）：经典服 nucleus_build_data 主表(40949/34899)+kj1(9503/28181) 12 星体系 76 颗 + 简单生存服独有 1 颗（淬焰燃锋）；品级=经典服 kj1 common_item 覆盖 + BA8 660000 兜底；星级段 5/9/12 解锁点；武器类型=种类（码）同行。",
      "superseded_by": "mutation_core_full",
      "note": "已被 mutation_core_full 取代，保留直链，不进首页导航"
    },
    "nucleus_entry_slots": {
      "publication_status": "unpublished",
      "category": "三、战力类 / （2）异变核芯·词条",
      "reason": "2026-09-04 被核芯卡（双服合并版 nucleus_cards_classic）取代，数据 json 保留存档"
    },
    "nucleus_item_catalog": {
      "publication_status": "unpublished",
      "category": "三、战力类 / （2）异变核芯",
      "reason": "2026-09-04 被核芯卡（双服合并版 nucleus_cards_classic）取代，数据 json 保留存档"
    },
    "shop_static_candidates": {
      "publication_status": "quarantined",
      "reason": "静态 mapping/detail 无 runtime selector 和 consumer 字段语义，且元数据为旧 SHA 780363…；不能作为当前货架、价格、限购、限定核芯或芯片保底依据。"
    },
    "vehicle_catalog": {
      "publication_status": "quarantined",
      "reason": "all_equips 名称字段已确认跨记录错位，当前名称来自目录推断、同系列投票及语素白名单；这不是 item→name 的定位链。"
    },
    "weapon_skin_sfx_text_sources": {
      "publication_status": "published",
      "category": "二、时装类 / （七）武器皮肤",
      "items": 115,
      "reason": "武器皮肤图鉴：113 条 current_parent（正式名 113/113 verified，来自同快照 common_item_data_base row key==skin_id）+ 2 条仅行为资源行；含品级/武器类型/模型路径/SFX 子项/时限变体/上架状态（release_state：on_sale/upcoming/no_sale_field/behavior_only，正源=皮肤行 sale_ts）。静态存在不等于可得、价格、概率或战斗效果。"
    },
    "vehicle_garage_names": {
      "publication_status": "published_hidden",
      "reason": "47 辆实机车库锚（user-verified：用户截图+vehicle_ui_data 尾索引序 1:1）；型号/body_model=待 vehicle_ui 行级配对（27.114）；vehicle_catalog 模型板保持 quarantined",
      "superseded_by": "vehicle_full",
      "note": "已被 vehicle_full 取代，保留直链，不进首页导航"
    },
    "fashion_identity_unresolved_v01": {
      "publication_status": "published_hidden",
      "category": "二、时装类 / （一）时装静态记录（身份待解析）",
      "items": 31112,
      "reason": "P4-B frozen_unresolved：仅展示 record-level static 候选；verified fashion self-ID = 0。",
      "note": "身份待解析的历史记录，未达到发布标准"
    },
    "weapon_skin_structure_v01": {
      "publication_status": "published_hidden",
      "category": "二、时装类 / （七）武器皮肤（隐藏审计板：已证明结构）",
      "items": 3,
      "reason": "P4-C frozen_unresolved：只展示已冻结的函数级结构；verified weapon-skin self-ID = 0。首页收口 2026-09-12：改为隐藏审计板（数据保留、直链可达、不再单独占首页武器皮肤入口）。"
    },
    "weapon_skin_static_candidates_v01": {
      "publication_status": "published_hidden",
      "category": "二、时装类 / （七）武器皮肤（隐藏审计板：静态候选 / 身份未解析）",
      "items": 115,
      "reason": "P4-C 身份研究仍冻结；展示 126 条静态配置行与 3 条 behavior-only 行，全部 identity unresolved，旧整数补名和父项推断均未启用。"
    },
    "weapon_skin_active": {
      "publication_status": "published_hidden",
      "category": "（内部·审计）武器皮肤 active 投影（非图鉴入口）",
      "items": 126,
      "reason": "active 结构视图（111 main + 15 timed 顶层成行，基准 BA8A pre-09-10）。图鉴唯一入口 = weapon_skin_sfx_text_sources（115，当前包 328b8446 基准，FID 直读）。保留直链供审计/交叉核对，manifest/首页永不列出。",
      "internal_only": true
    },
    "vehicle_full": {
      "publication_status": "published",
      "reason": "载具全量总表：vehicle_ui_data 同快照 277 行逐行重放（205 严格 + 72 行尾内联变体宽容重放）；名称/描述/品牌/类型/数值全部同表内字段，图标按「UI 清单路径 → fid → gpk_loc0」逐图核验后从 pe_packs 解码。只证静态表内容与资源存在，不证业务启用/当前可获取。"
    },
    "tactical_chip_full": {
      "publication_status": "published",
      "category": "二、战力类 /（二）战术芯片",
      "reason": "战术芯片全量表：chip_type_data 71 枚（=道具行/图鉴同源）+ belt_chip_data 同名主键 852 行（71×12 档，属性 desc/参数/品质/拆解全部同表内字段）。道具行只按图标文件名编号匹配 common_item（不做等整数跨源拼接），奖池只读 chip_roll_weight_data.reward_id 参数组；图标按「UI 清单路径 → .ktx fid → gpk_loc0」逐图核验后从 pe_packs 解码。只证静态表内容与资源存在，不证业务启用/当前可获取。",
      "items": 71
    },
    "mutation_core_full": {
      "publication_status": "published",
      "category": "二、战力类 /（一）异变核芯",
      "items": 132,
      "reason": "核芯唯一总表：common_item 660xxx 段 132 行。经典服口径：品级色 蓝5星 / 紫9星 / 金12星；简单生存统一 5 星。卡面简略、详情展开。"
    },
    "server_types": {
      "publication_status": "published",
      "category": "四、资料层（道具总表 / 文本来源） / （四）服型"
    },
    "lottery_periods": {
      "publication_status": "published",
      "category": "三、活动类 / （一）限时主题类 / 1、当期&历史每期抽奖奖池"
    },
    "drone_catalog": {
      "publication_status": "published",
      "category": "二、战力类 / （六）无人机"
    },
    "upcoming_auto": {
      "publication_status": "published",
      "category": "零、新更新与预告专栏（游戏未上线资源预告）"
    },
    "item_master_full": {
      "publication_status": "published",
      "category": "一、道具总表 / （一）ITEM_MASTER v0.1",
      "items": 1189,
      "reason": "P4-A 冻结产物：1,189 条 verified item；hide_in_bag 缺席保持 unresolved。"
    },
    "activity_master": {
      "publication_status": "published",
      "category": "三、活动类 / （零）活动总表"
    },
    "skill_catalog": {
      "publication_status": "published",
      "category": "ok"
    },
    "title_catalog": {
      "publication_status": "published",
      "category": "ok"
    },
    "avatar_catalog": {
      "publication_status": "published",
      "category": "ok"
    },
    "talent_catalog": {
      "publication_status": "published_hidden",
      "category": "二、战力类",
      "note": "已被 talent_battle / talent_prof 拆分替代"
    },
    "edible_catalog": {
      "publication_status": "published",
      "category": "二、战力类"
    },
    "illustration_catalog": {
      "publication_status": "published",
      "category": "四、资料层（道具总表 / 文本来源）"
    },
    "recipe_catalog": {
      "publication_status": "published",
      "category": "四、资料层（道具总表 / 文本来源）"
    },
    "buff_catalog": {
      "publication_status": "published",
      "category": "二、战力类"
    },
    "entity_catalog": {
      "publication_status": "published",
      "category": "四、资料层（道具总表 / 文本来源）"
    },
    "desc_catalog": {
      "publication_status": "published",
      "category": "四、资料层（道具总表 / 文本来源）"
    },
    "text_notice_catalog": {
      "publication_status": "published",
      "category": "四、资料层（道具总表 / 文本来源）"
    },
    "gene_potential_catalog": {
      "publication_status": "published",
      "category": "二、战力类"
    },
    "talent_battle": {
      "publication_status": "published",
      "category": "二、战力类"
    },
    "talent_prof": {
      "publication_status": "published",
      "category": "二、战力类"
    },
    "scene_balance": {
      "publication_status": "published",
      "category": "三、活动类 / （四）PvP 场景平衡",
      "reason": "场景加成上下限：special_hurt_params_data(kj1) × space_data。按场景名合并，PvP 优先。",
      "items": 63
    },
    "kill_broadcast": {
      "publication_status": "published",
      "category": "三、活动类 / （五）击败播报",
      "reason": "播报文案 34 条（error_code_data 含「击败」）+ 击败特效 35 条（weapon_skin_sfx_function_data sfx_type=4）；播放器在 UI 代码里，无独立外观表。",
      "items": 69
    }
  }
};
