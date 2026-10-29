window.WIKI_BOARD_core_skill_12star = {
 "meta": {
  "name": "12 星全量特技表（极品核芯）",
  "category": "二、战力类 / （零）核芯类 / 12 星特技",
  "source_server": "经典服口径（极品 = 金，12 星）",
  "generated": "2026-10-22",
  "id_label": "核芯",
  "hide_media": false,
  "evidence": "structure",
  "card_mode": "roster",
  "package_sha": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
  "filters": [
   {
    "key": "weapon_type",
    "label": "武器类型"
   }
  ],
  "card_summary": [
   [
    "grade_label",
    "品级"
   ],
   [
    "weapon_type",
    "武器类型"
   ]
  ],
  "state_summary": {
   "极品核芯": 50,
   "有特技": 47,
   "有升星段": 50
  },
  "note": "极品（12 星）核芯的特技全表；升星段目前只有 5 星档文本（简单生存口径），经典服 12 档段位文本在未解表里，暂不虚标。",
  "provenance": {
   "contract_version": 3,
   "audit_status": "passed",
   "contract": "frozen-audited-artifact",
   "source_locks": [
    {
     "source_id": "documents-py314-current",
     "role": "primary",
     "path": "E:/mrzh/Documents/script.py314.lc.npk",
     "sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
     "bytes": 196059988,
     "mtime_ns": 1792505574167464800
    }
   ],
   "source_scope": {
    "cross_source_policy": "no-cross-source-field-join",
    "integer_join_policy": "no-equal-integer-join",
    "runtime_final_policy": "unknown-unless-runtime-proven"
   }
  }
 },
 "items": [
  {
   "id": "s12_660000",
   "item_id": 660000,
   "name": "疾影火刃",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "冷兵器",
   "skill_desc": "持冷兵器时，装配后可以#f(5)长按技能键，持刀蓄力以更快的速度向前冲刺#n，冲刺过程中可以划动操作转向。#r#r冲刺中每移动40距离，都会造成一次小范围伤害。#r松开攻击键或气力耗尽会结束冲刺并触发重斩，造成#f(5){0}#n伤害，对玩家造成的重斩伤害衰减#f(5)50%#n。#r#r冲刺时#f(5)气力消耗提升100%#n，使用重斩时会#f(5)基于冲刺距离回复至多40%气力#n，重斩命中会#f(5)额外回复少量气力#n。#r冲刺时可以点击左侧攻击键进行跳跃。",
   "rank_star_segments": {
    "12": "冲刺过程中(5)免疫「减速」、「击飞」、「麻痹」、「冰冻」、「定身」同时降低受到的非玩家伤害(5)50%。",
    "9": "每冲刺40距离，提升冲刺阶段(5)「移动速度」8%，上限为40%。",
    "5": "每冲刺40距离提升(5)重斩伤害8%，上限为60%。在达到上限时，重斩伤害额外造成(5)「击倒」效果。"
   },
   "icon": "ui/item_icon/icon_jin_huo",
   "desc": "特级异变核芯，装配后冷兵器长按蓄力可以向前冲锋接续强力火焰斩击。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660000",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660000",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_huo_b.ktx",
      "base": "ui/item_icon/icon_jin_huo_b",
      "ext": ".ktx",
      "pack": "0181.gpk",
      "row": 4175,
      "fid": "A33EE5A1B62F478B",
      "gpk_loc0_offset": 187195160,
      "pkgidx": 13,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_huo_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660001",
   "item_id": 660001,
   "name": "绝对零度",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "榴弹炮",
   "skill_desc": "装配后榴弹炮攻击时，在炮弹爆炸位置形成#f(5)持续10秒的冰冻区域#n，造成#f(5)50%的「减速」效果（对玩家减半）#n。#r#r炮弹#f(5)「命中」#n自身产生的冰冻区域时，会在冰冻区域上引发爆炸，造成一次#f(5){0}#n的额外#f(5)范围伤害#n。",
   "rank_star_segments": {
    "12": "目标每连续位于冰冻区域上0.5秒，其受到的(5)冰爆伤害和冰面持续伤害会提升(5)5%，该效果最多可叠加(5)6次。",
    "9": "目标位于冰场上时，(5)每秒受到一定的冰冻伤害。\n深潜重炮三段蓄力时，冰场持续伤害会(5)在基础上进行对应提升。",
    "5": "被冰爆命中的目标会被(5)「冰冻」1秒，在玩家的(5)爆炸伤害加成属性超过50%时(5)加长为2秒。\n\n「冰冻」效果对每个目标有(5)10秒内置冷却时间，且对玩家衰减70%。"
   },
   "icon": "ui/item_icon/icon_jin_bing",
   "desc": "特级异变核芯，装配后榴弹炮打出减速冰场，炮击再次命中冰场会产生冰爆。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660001",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660001",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_bing_b.ktx",
      "base": "ui/item_icon/icon_jin_bing_b",
      "ext": ".ktx",
      "pack": "0178.gpk",
      "row": 2959,
      "fid": "1A2EC9FD318A5906",
      "gpk_loc0_offset": 95726900,
      "pkgidx": 10,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_bing_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660002",
   "item_id": 660002,
   "name": "脉冲闪电",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "手枪/双枪",
   "skill_desc": "手枪累积#f(5)7次（双枪为10次）「子弹命中」#n后，下次射击会进入#f(5)持续0.8秒的脉冲扫射状态#n。#r#r脉冲扫射#f(5)基础射击速度提升为500%且不消耗子弹#n，每一击火力值为原火力值的#f(5){0}#n。#r#r#f(5)每90%的「暴击率」会增加0.1秒的脉冲扫射持续时长，总上限1.2秒#n。",
   "rank_star_segments": {
    "12": "脉冲扫射及弹射伤害每「暴击」1次，自身(5)暴击伤害增加4%，上限为(5)50%。脉冲扫射结束时重置。",
    "9": "脉冲扫射结束瞬间会(5)触发一次瞬间「自动换弹」。",
    "5": "脉冲扫射命中时随机对(5)100距离内的敌方进行(5)50%伤害的「弹射」。"
   },
   "icon": "ui/item_icon/icon_jin_dian",
   "desc": "特级异变核芯，装配后手枪命中7次后，下次射击向前打出极快速的多次射击。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660002",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660002",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_dian_b.ktx",
      "base": "ui/item_icon/icon_jin_dian_b",
      "ext": ".ktx",
      "pack": "0181.gpk",
      "row": 4174,
      "fid": "FAA6E15B55CFDCD1",
      "gpk_loc0_offset": 187184796,
      "pkgidx": 13,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_dian_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660023",
   "item_id": 660023,
   "name": "极光狙击",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": null,
   "skill_desc": "",
   "rank_star_segments": {
    "12": "对被自身造成的(5)易伤效果影响的目标射击时，造成一次(5)8%的「额外伤害」，该伤害在「命中弱点」时(5)提升为12%。",
    "9": "被自身造成的(5)易伤效果影响的目标，受到射击伤害时有(5)10%概率(5)视为「命中弱点」。",
    "5": "「命中弱点」后，射击伤害(5)在6秒内增加8%，该效果可以(5)叠加至多4次，在未「连续命中弱点」时重置。"
   },
   "icon": "ui/item_icon/icon_jin_dian",
   "desc": "特级异变核芯，装配后狙击概率锁头并可使目标易伤。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660023",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660023",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_dian_b.ktx",
      "base": "ui/item_icon/icon_jin_dian_b",
      "ext": ".ktx",
      "pack": "0181.gpk",
      "row": 4174,
      "fid": "FAA6E15B55CFDCD1",
      "gpk_loc0_offset": 187184796,
      "pkgidx": 13,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_dian_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）"
   }
  },
  {
   "id": "s12_660024",
   "item_id": 660024,
   "name": "极寒冰爆",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "霰弹枪",
   "skill_desc": "装配后，霰弹枪射击的#f(5)「弹片数量」增加两发#n，弹道分布方式变为基于准星#f(5)横向水平散布#n，总数量与射击对应的霰弹枪弹片数量一致。#r#r每个弹片造成#f(5){0}#n的伤害，并在「命中」时叠加1层#f(5)霜冻标记#n（至多150层）。若弹片「暴击」，则会额外叠加1层#f(5)霜冻标记#n。#r#r装配后，可使用#f(5)极寒冰爆#n来向准星方向打出一发爆裂冰弹，对被命中的目标造成#f(5)300%+8%*霜冻标记层数#n的伤害，并清除其层数。",
   "rank_star_segments": {
    "12": "「暴击」会在1.5秒内提升自身(5)0.4%「射速」，该效果可叠加至至多(5)12%。",
    "9": "目标每有1%的「已损失生命值」，极寒冰爆造成的伤害(5)提升1%，至多提升50%。且标记可叠加上限提升至200层。",
    "5": "自身每为目标添加20层霜冻层数，会对目标额外造成(5)100%伤害并使其在2秒内(5)「减速」25%。"
   },
   "icon": "ui/item_icon/icon_jin_bing",
   "desc": "特级异变核芯，装配后霰弹枪打出扇形弹道并可使用冰爆弹。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660024",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660024",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_bing_b.ktx",
      "base": "ui/item_icon/icon_jin_bing_b",
      "ext": ".ktx",
      "pack": "0178.gpk",
      "row": 2959,
      "fid": "1A2EC9FD318A5906",
      "gpk_loc0_offset": 95726900,
      "pkgidx": 10,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_bing_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660027",
   "item_id": 660027,
   "name": "炽热枪膛",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "电磁机枪",
   "skill_desc": "电磁机枪射击会#f(5)逐渐累积热能#n（累积速度受电磁机枪充能速度的数值影响），热能值会影响电磁机枪的射速和伤害，停止射击一小段时间后开始衰减。#r电磁机枪初始射速提升为400，射击初始造成40%伤害，随热能累积逐渐提升至#f(5){0}伤害#n。#r#r电磁机枪的「换弹」动作被替换为进行一轮至多10次的#f(5)爆燃射击#n同时换弹并清空热能，每次射击造成#f(5)135%#n的满热能值射击伤害。#r#f(5)爆燃射击#n对玩家造成的伤害衰减#f(5)25%#n。",
   "rank_star_segments": {
    "12": "爆燃射击每次命中时，后续爆燃射击的(5)伤害倍率提升1.5%，至多可叠加30层，在触发换弹时重置。",
    "9": "电磁机枪在热能为满值的状态下射击时(5)20%概率触发爆燃射击。",
    "5": "(5)弹匣容量提升25%，热能为满值时射击(5)35%概率不消耗弹药。"
   },
   "icon": "ui/item_icon/icon_jin_huo",
   "desc": "特级异变核芯，装配后电磁机枪伤害随射击提升并在换弹时打出燃烧射击。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660027",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660027",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_huo_b.ktx",
      "base": "ui/item_icon/icon_jin_huo_b",
      "ext": ".ktx",
      "pack": "0181.gpk",
      "row": 4175,
      "fid": "A33EE5A1B62F478B",
      "gpk_loc0_offset": 187195160,
      "pkgidx": 13,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_huo_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660030",
   "item_id": 660030,
   "name": "侵蚀效应",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "突击步枪",
   "skill_desc": "突击步枪在没有标记目标的情况下#f(5)累积命中「同一目标」5次后#n，会用#f(5)标记#n锁定该目标（#f(5)标记#n同时只存在一个。#r射击命中#f(5)标记#n锁定的目标时，造成伤害的#f(5){0}#n会被额外累积为酸溶值。#r#r#f(5)标记#n初始为一阶段，随#f(5)「子弹命中」#n会逐渐提升阶段，并基于阶段获得以下效果：#r一阶段及以上：「子弹命中」时8%概率触发#f(5)强酸#n效果，使该次射击穿透护盾直接造成「血量削减」。自身#f(5)每80%「暴击率」会提升强酸效果触发概率1%，至多提升至12%#n#r二阶段及以上：「子弹命中」时#f(5)20%概率使射速在0.5秒内提升200%#n（冷却时间2.5秒）#r三阶段：#f(5)3秒内射击不消耗子弹#n#r#r在#f(5)三阶段结束#n或#f(5)酸溶值超过目标剩余生命值+护盾值#n后，移除#f(5)标记#n并对其造成#f(5)100%*酸溶值#n的「触发伤害」。#r切换武器或10秒内未对目标造成伤害时也会移除#f(5)标记#n，此时造成#f(5)50%*酸溶值#n的「触发伤害」。",
   "rank_star_segments": {
    "12": "(5)标记阶段提升时，对(5)标记目标造成一次(5)20%*酸溶值的伤害并(5)「麻痹」目标1秒。",
    "9": "击败被(5)标记的目标时，(5)瞬间进行一次「自动换弹」并提升25%「射速」，持续4秒。",
    "5": "(5)强酸效果触发时，该次伤害(5)视为「命中弱点」。每触发一次(5)强酸效果，提升自身(5)4%移速，持续5秒，可叠加至多5层。"
   },
   "icon": "ui/item_icon/icon_jin_suan",
   "desc": "特级异变核芯，装配后突击步枪射击标记目标并累积酸液伤害",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660030",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660030",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_suan_b.ktx",
      "base": "ui/item_icon/icon_jin_suan_b",
      "ext": ".ktx",
      "pack": "0178.gpk",
      "row": 3296,
      "fid": "2713A9C2A45D28A4",
      "gpk_loc0_offset": 98170332,
      "pkgidx": 10,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_suan_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660031",
   "item_id": 660031,
   "name": "酸焰激流",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "喷火器",
   "skill_desc": "喷火器在命中目标时，会为目标叠加#f(5)酸焰#n层数，持续3秒，至多9层，每层酸焰层数会增加自身喷火器对目标造成的#f(5)伤害{0}#n。#r#f(5)酸焰#n层数叠加至9层的目标会以自身为中心产生半径40的#f(5)酸蚀圈#n，圈内目标会被减速25%。#r酸蚀圈中心的目标受到喷火器攻击时，有#f(5)20%概率产生酸蚀爆炸#n，对酸蚀圈内至多3个其他目标造成#f(5)60%的伤害#n。#r酸蚀圈内目标死亡时，#f(5)100%概率产生酸蚀爆炸#n。",
   "rank_star_segments": {
    "12": "被酸蚀圈影响的目标(5)受到35%的「恢复降低」，且降低部分会被(5)等比例转化为自身恢复。",
    "9": "300范围内每有一个来源于自身的酸蚀圈，喷火器(5)攻击频率提升3%，至多12%。",
    "5": "酸蚀圈中心的目标被酸蚀爆炸命中时，(5)有25%概率在0.1秒延迟后引发一次酸蚀爆炸。"
   },
   "icon": "ui/item_icon/icon_jin_suan",
   "desc": "特级异变核芯，装配后喷火器喷射酸焰灼烧目标造成额外伤害并减速",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660031",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660031",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_suan_b.ktx",
      "base": "ui/item_icon/icon_jin_suan_b",
      "ext": ".ktx",
      "pack": "0178.gpk",
      "row": 3296,
      "fid": "2713A9C2A45D28A4",
      "gpk_loc0_offset": 98170332,
      "pkgidx": 10,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_suan_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660043",
   "item_id": 660043,
   "name": "极限火力",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "榴弹炮",
   "skill_desc": "使用榴弹炮时，可以通过技能按键进入架设模式，#f(5)架设模式下不可移动#n。#r架设模式下，榴弹炮#f(5)射速提升25%，爆炸范围提升20%，弹道速度提升100%，射击造成{0}伤害#n。#r架设模式下榴弹炮#f(5)对玩家造成的伤害衰减为70%#n。#r使用深潜重炮时，深潜重炮#f(5)射击蓄力速度提升#n，且满蓄力炮击会产生火焰区域。",
   "rank_star_segments": {
    "12": "架设模式下，每次射击和溅射命中目标会提升自身(5)0.5%爆炸伤害加成，至多可叠加40层。退出架设模式时重置该加成。",
    "9": "架设模式弹匣容量恒定为1，(5)每次射击后会「自动换弹」并触发所有换弹效果。",
    "5": "架设模式下每次「射击」后，在命中范围内产生(5)共8次额外的15%「范围伤害」。"
   },
   "icon": "ui/item_icon/icon_jin_huo",
   "desc": "特级异变核芯，装配后可以进入架设模式，对更大范围的目标更快的进行轰炸。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660043",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660043",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_huo_b.ktx",
      "base": "ui/item_icon/icon_jin_huo_b",
      "ext": ".ktx",
      "pack": "0181.gpk",
      "row": 4175,
      "fid": "A33EE5A1B62F478B",
      "gpk_loc0_offset": 187195160,
      "pkgidx": 13,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_huo_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660044",
   "item_id": 660044,
   "name": "电掣双刀",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "冷兵器",
   "skill_desc": "#f(5)仅在副武器装备冷兵器时可以使用。#n#r使用冷兵器时，常规模式下每秒获得#f(5)5%#n「充能」。持续移动和攻击命中时会#f(5)额外获得充能#n。#r充能达到#f(5)70%#n时，可以激活技能#f(5)切换为双刀模式#n，同时对周围#f(5)50#n范围内的目标造成一次#f(5)50%#n的伤害。#r#r双刀模式下每秒消耗#f(5)5%#n能量，攻击时会同时使用主副武器进行#f(5)二连斩#n，共计造成#f(5){0}#n伤害（该伤害#f(5)对非玩家目标提升40%#n）（可触发「命中效果」）。#r双刀模式下获得#f(5)15%#n「移速提升」和每秒#f(5)2.5%#n的「护盾回复」。",
   "rank_star_segments": {
    "12": "双刀模式下，每秒获得(5)1.5%暴击率和(5)1.5%免暴率加成，最多叠加(5)12层。切换武器或退出双刀模式后消失。",
    "9": "双刀模式下挥砍命中回复(5)15气力，每击败一个目标回复(5)20%能量，突进斩击命中回复(5)10%能量。",
    "5": "双刀模式下解锁(5)突进技能，冷却时间(5)4秒。使用后向前方快速突进，造成一次(5)100%伤害的斩击并获得1.5秒的(5)40%「移速提升」。"
   },
   "icon": "ui/item_icon/icon_jin_dian",
   "desc": "特级异变核芯，装配后可以开启双刀模式，大幅提升机动性和作战能力。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660044",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660044",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_dian_b.ktx",
      "base": "ui/item_icon/icon_jin_dian_b",
      "ext": ".ktx",
      "pack": "0181.gpk",
      "row": 4174,
      "fid": "FAA6E15B55CFDCD1",
      "gpk_loc0_offset": 187184796,
      "pkgidx": 13,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_dian_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660047",
   "item_id": 660047,
   "name": "呼啸寒霜",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "喷火器",
   "skill_desc": "喷火器喷出冰雾，目标每次被命中会叠加一层#f(5)5秒#n的#f(5)冰雾#n效果，每层造成#f(5)5%「减速」#n，最多#f(5)3层#n，达到最高层后，目标进入#f(5)冻伤#n状态，持续#f(5)3秒#n，每秒受到#f(5){0}「持续伤害」#n（对非玩家伤害提升#f(5)100%#n），目标在冻伤状态期间被命中不会刷新冻伤持续时间，冻伤状态结束后清空冰雾层数。#r冰雾和冻伤均为「负面效果」",
   "rank_star_segments": {
    "12": "每次喷火器命中会延长冻伤状态的时长(5)0.5秒，最长(5)6秒，达到最长时间后冻伤附加(5)50%「回复降低」。",
    "9": "冻伤状态的目标受到的所有冰冻伤害增加(5)5%。",
    "5": "对冻伤状态的目标造成「暴击」时削弱其(5)2点护甲（视为「负面效果」），持续(5)0.5秒。"
   },
   "icon": "ui/item_icon/icon_jin_bing",
   "desc": "特级异变核芯，装配后喷火器攻击累积减速，并且造成持续伤害。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660047",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660047",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_bing_b.ktx",
      "base": "ui/item_icon/icon_jin_bing_b",
      "ext": ".ktx",
      "pack": "0178.gpk",
      "row": 2959,
      "fid": "1A2EC9FD318A5906",
      "gpk_loc0_offset": 95726900,
      "pkgidx": 10,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_bing_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660049",
   "item_id": 660049,
   "name": "刺骨冰锥",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "手枪/双枪",
   "skill_desc": "手枪/双枪射击动作改变，基础射速降低，射击造成#f(5){0}伤害#n，且副手射击伤害不再衰减。#r目标#f(5)每损失25%生命值，射击对其造成5%伤害的「追击」#n。#r对目标的每第4次命中会引发冰爆，冰爆造成#f(5)60%~90%伤害的「追击」（基于目标已损失生命值比例）#n。10秒内未命中该目标时，对目标的命中计数重置。#r具有“主宰”特技的双枪装配该核芯时，特技的副手射击伤害提升效果会以一定比例加成到基础射击伤害中。",
   "rank_star_segments": {
    "12": "射击命中冰冻状态的目标时，(5)直接触发冰爆效果。且冰爆命中除特殊感染体之外的感染体时，(5)有40%的概率「冰冻」目标1秒（该效果具有5秒内置冷却时间）。",
    "9": "射击触发冰爆时，该次射击的基础伤害在结算时(5)「暴击率」额外提升35%。",
    "5": "对目标触发冰爆效果后，下次射击有(5)12%的基础概率对其直接触发冰爆效果。该概率会随对目标造成冰爆的次数(5)逐渐提升至至多40%。"
   },
   "icon": "ui/item_icon/icon_jin_bing",
   "desc": "特级异变核芯，装配后双枪对残血目标造成额外伤害，连续命中引发冰爆造成高额伤害。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660049",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660049",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_bing_b.ktx",
      "base": "ui/item_icon/icon_jin_bing_b",
      "ext": ".ktx",
      "pack": "0178.gpk",
      "row": 2959,
      "fid": "1A2EC9FD318A5906",
      "gpk_loc0_offset": 95726900,
      "pkgidx": 10,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_bing_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660050",
   "item_id": 660050,
   "name": "连锁反应",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "霰弹枪",
   "skill_desc": "射击造成#f(5){0}#n伤害。#r#f(5)「射击命中」获得3点能量，「弹片命中」额外获得1点能量（命中玩家时获得2点）#n，上限100。停止射击1.5秒后持续损失能量，能量达到不同阶段时获得相应增益。#r一阶段（0-20）：无变化。#r二阶段（20-60）：#f(5)每5点能量提升5基础射速#n，同时减少4%伤害。#r三阶段（60-100）：进入#f(5)狂热状态#n，#f(5)基础射速提升20#n，伤害衰减至60%，#f(5)每发弹片命中有15%概率触发酸爆，造成10%伤害#n。#r能量充满：下次射击不消耗子弹，转而#f(5)消耗所有能量发射强力酸蚀爆弹，每发弹片命中后造成3次100%伤害，触发酸爆概率提升为40%#n。发射动作结束后自动触发「换弹」。#f(5)酸蚀爆弹对玩家伤害衰减至70%#n。#r切换武器后清空当前能量条。",
   "rank_star_segments": {
    "12": "酸蚀爆弹变为(5)快速二连发，(5)第二发弹片数量衰减为第一发的50%。",
    "9": "狂热状态下，(5)「弹片命中」使目标受到自身伤害增加0.3%，持续3秒，上限30层。",
    "5": "狂热状态下，每次射击(5)额外发射1枚弹片。"
   },
   "icon": "ui/item_icon/icon_jin_suan",
   "desc": "特级异变核芯，装配后霰弹枪随着能量积蓄提升射速，蓄满后打出狂暴一击。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660050",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660050",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_suan_b.ktx",
      "base": "ui/item_icon/icon_jin_suan_b",
      "ext": ".ktx",
      "pack": "0178.gpk",
      "row": 3296,
      "fid": "2713A9C2A45D28A4",
      "gpk_loc0_offset": 98170332,
      "pkgidx": 10,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_suan_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660051",
   "item_id": 660051,
   "name": "炽焰咆哮",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": null,
   "skill_desc": "",
   "rank_star_segments": {
    "12": "目标每有(5)1%「已损失生命值」，咆哮射击获得(5)0.1%「暴击率」和(5)0.25%「暴击伤害」加成。",
    "9": "(5)咆哮射击命中目标后，下次射击(5)蓄力速度加快25%。",
    "5": "(5)满蓄力命中目标为其附加(5)炽焰缠身效果，下次射击命中将其引爆并(5)触发15%伤害的「追击」。该效果最多同时存在(5)1个。"
   },
   "icon": "ui/item_icon/icon_jin_huo",
   "desc": "特级异变核芯，装配后可以锁定敌人并持续蓄力，发射大威力追踪子弹。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660051",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660051",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_huo_b.ktx",
      "base": "ui/item_icon/icon_jin_huo_b",
      "ext": ".ktx",
      "pack": "0181.gpk",
      "row": 4175,
      "fid": "A33EE5A1B62F478B",
      "gpk_loc0_offset": 187195160,
      "pkgidx": 13,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_huo_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）"
   }
  },
  {
   "id": "s12_660053",
   "item_id": 660053,
   "name": "冰凌龙息",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "电磁机枪",
   "skill_desc": "电磁机枪射击#f(5)不再消耗子弹#n，并在射击时每秒会#f(5)累积6%极寒值#n（结束射击后会逐渐衰减）。#r极寒值处于#f(5)50%以上#n时，射击造成#f(5){0}#n伤害。#r极寒值满时，下#f(5)3次#n射击会发射大威力的冰锥弹，造成#f(5)4次80%的射击伤害#n。#r冰锥弹触发后，电磁机枪需要重新积累射速，极寒值重置为40%。",
   "rank_star_segments": {
    "12": "(5)极寒值处于50%以下时，非射击状态也会持续积累极寒值。且冰锥弹(5)附加持续0.6秒的「冰冻」效果（内置冷却时间10秒）。",
    "9": "冰锥弹附加额外「追击」伤害，数值为目标(5)5秒内受自身造成冰冻伤害的12%（对怪物最大伤害为冰锥弹的200%，对玩家最大伤害为冰锥弹的50%）。",
    "5": "极寒值处于40%以上时，电磁机枪的(5)射速充能速度提升50%，(5)最大射速保持时间提升200%。"
   },
   "icon": "ui/item_icon/icon_jin_bing",
   "desc": "特级异变核芯，装配后射击不消耗弹药，连续射击累积极寒值造成更高伤害。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660053",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660053",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_bing_b.ktx",
      "base": "ui/item_icon/icon_jin_bing_b",
      "ext": ".ktx",
      "pack": "0178.gpk",
      "row": 2959,
      "fid": "1A2EC9FD318A5906",
      "gpk_loc0_offset": 95726900,
      "pkgidx": 10,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_bing_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660055",
   "item_id": 660055,
   "name": "裂变效应",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "突击步枪",
   "skill_desc": "突击步枪枪口处生成一台浮游炮，射击命中时有#f(5)20%#n概率(每#f(5)6%「射速」#n额外提升#f(5)1%#n概率，最多提升#f(5)10%#n）使其追加#f(5)1#n次#f(5){0}#n伤害的「追击」。每次触发#f(5)「追击」#n后提升#f(5)1%#n概率，至多提升至#f(5)40%#n，#f(5)3#n秒未触发则重置。#r触发#f(5)「追击」#n时获得#f(5)5#n点「充能」（对玩家为#f(5)10#n点）。充能达到#f(5)100#n后下次射击进入持续#f(5)5#n秒的#f(5)裂变爆发#n状态：每次射击#f(5)必定触发「追击」#n，且#f(5)有40%概率触发裂变#n使单次#f(5)「追击」#n同时发射#f(5)3#n颗子弹。#r裂变爆发状态结束后浮游炮失效#f(5)4#n秒，期间无法发射和充能，同时清空概率提升层数。",
   "rank_star_segments": {
    "12": "裂变爆发结束后，浮游炮(5)不再失效。",
    "9": "裂变爆发状态下，(5)触发裂变概率翻倍。",
    "5": "进入裂变爆发状态时，(5)瞬间补满弹匣。"
   },
   "icon": "ui/item_icon/icon_jin_huo",
   "desc": "特级异变核芯，装配后可以生成熔岩浮游炮对目标造成额外打击",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660055",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660055",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_huo_b.ktx",
      "base": "ui/item_icon/icon_jin_huo_b",
      "ext": ".ktx",
      "pack": "0181.gpk",
      "row": 4175,
      "fid": "A33EE5A1B62F478B",
      "gpk_loc0_offset": 187195160,
      "pkgidx": 13,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_huo_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660056",
   "item_id": 660056,
   "name": "球状闪电",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "喷火器",
   "skill_desc": "喷火器射击不造成伤害，变为生成#f(5)球状闪电#n，球状闪电将持续#f(5)「牵引」敌人#n并每#f(5)0.25秒#n对其造成#f(5)100%#n伤害（「牵引」效果和伤害受#f(5)「射速」#n影响，#f(5)晶化感染体#n受到的「牵引」效果翻倍）。连续射击时球状闪电会不断强化，最多可提升#f(5){0}#n伤害，连续射击5秒后达到最大值。",
   "rank_star_segments": {
    "12": "磁暴基础伤害提升为100%，球状闪电每次造成伤害会提升自身的(5)0.2%「暴击率」和(5)0.2%「暴击伤害」（最多叠加(5)20层），磁暴后加成效果重置。",
    "9": "球状闪电磁暴会使敌人(5)「麻痹」0.8秒（对同一目标6秒内仅生效一次）并使其(5)4秒内获得的(5)「护盾回复降低」60%。",
    "5": "球状闪电每次命中会降低敌方(5)0.1护甲且获得(5)5点电量，最多叠加(5)20次；电量达到100后产生一次磁暴，造成(5)30%的额外伤害（对玩家衰减50%）。"
   },
   "icon": "ui/item_icon/icon_jin_dian",
   "desc": "特级异变核芯，装配后可以生成球状闪电对敌人造成牵引和破甲效果。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660056",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660056",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_dian_b.ktx",
      "base": "ui/item_icon/icon_jin_dian_b",
      "ext": ".ktx",
      "pack": "0181.gpk",
      "row": 4174,
      "fid": "FAA6E15B55CFDCD1",
      "gpk_loc0_offset": 187184796,
      "pkgidx": 13,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_dian_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660060",
   "item_id": 660060,
   "name": "贯通战术",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "弓箭",
   "skill_desc": "给箭头附着强酸，命中目标时额外造成3秒该次伤害#f(5){0}的强酸「持续伤害」#n（无法叠加），蓄力完成后强酸箭矢可以#f(5)穿透路径上的目标和障碍物#n（最多8个），每穿透一个障碍物箭矢威力下降50%，每穿透一个目标箭矢威力下降10%（威力最低降至20%），穿透障碍物后箭矢最多再飞行15米。",
   "rank_star_segments": {
    "12": "二段蓄力完成后射出的箭矢穿透障碍物和暴击时留下持续5秒的(5)酸雾，酸雾中的目标受到(5)【腐蚀】效果，离开酸雾3秒后(5)【腐蚀】效果消失。",
    "9": "暴击会额外造成3秒(5)【腐蚀】效果：(5)附加30%「护盾恢复降低」并造成(5)每秒40%「持续伤害」。",
    "5": "蓄力完成后可以进行1秒的(5)二段蓄力，二段蓄力使箭矢的(5)威力增强（最多增强50%）并且二段蓄力完成后(5)穿透目标不再使箭矢威力下降（穿透障碍物依然会使箭矢威力下降）。"
   },
   "icon": "ui/item_icon/icon_jin_suan",
   "desc": "特级异变核芯，装配后蓄力射出的箭矢可以穿透所有障碍物和目标。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660060",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660060",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_suan_b.ktx",
      "base": "ui/item_icon/icon_jin_suan_b",
      "ext": ".ktx",
      "pack": "0178.gpk",
      "row": 3296,
      "fid": "2713A9C2A45D28A4",
      "gpk_loc0_offset": 98170332,
      "pkgidx": 10,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_suan_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660061",
   "item_id": 660061,
   "name": "流光疾射",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "弓箭",
   "skill_desc": "弓箭射击变为二连射，每箭造成#f(5){0}#n伤害并能够触发「命中效果」。#r将移动摇杆拖动到疾跑响应区域（即左侧摇杆的外圈范围）或输入疾跑指令（默认快捷键shift+方向键）时，射击会被替换为快速#f(5)向摇杆方向位移的滑步射击#n。#r滑步射击的过程中，可以实时输入移动指令来微调移动的方向。#r#f(5)移动速度#n会影响滑步射击的速度和频率，且滑步射击会#f(5)额外消耗少量气力#n。",
   "rank_star_segments": {
    "12": "被「减速」（移动速度加成为负）时，(5)滑步射击的速度和频率不会降低。",
    "9": "每次触发(5)滑步射击时增加自身(5)2%「移动速度」（可叠加至至多20%），持续3秒。",
    "5": "射击在5秒内多次命中目标时，基于命中次数会附加(5)每层1.5%（至多叠加至15%）的电磁属性「追击」伤害。"
   },
   "icon": "ui/item_icon/icon_jin_dian",
   "desc": "特级异变核芯，装配后射击会发出两支箭矢，且射击后可以接续快速移动。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660061",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660061",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_dian_b.ktx",
      "base": "ui/item_icon/icon_jin_dian_b",
      "ext": ".ktx",
      "pack": "0181.gpk",
      "row": 4174,
      "fid": "FAA6E15B55CFDCD1",
      "gpk_loc0_offset": 187184796,
      "pkgidx": 13,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_dian_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660066",
   "item_id": 660066,
   "name": "电极效应",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "突击步枪",
   "skill_desc": "突击步枪会以每秒40%的速度充入电能。电能会在「射击」后0.5秒内暂停回复，随后1.5秒内以每秒18%的速度缓慢恢复，随后进入快速回复状态。#f(5)「换弹」或使用「配件技能」后电能会立刻快速回复#n。#r具有电能时，「射击」消耗5%电能。消耗电能的「射击」命中时，#f(5)有45%概率触发【电震射击】（视为「射击」，消耗子弹，但不消耗电能），造成{0}伤害#n。#r不消耗电能的「射击」，触发【电震射击】的概率降低为8%。#r【电震射击】会按不消耗电能的概率触发【电震射击】，但最多触发1次。",
   "rank_star_segments": {
    "12": "【电震射击】附加(5)1秒「麻痹」效果（内置冷却12秒）。对「麻痹」效果中的目标，消耗电能的射击触发【电震射击】的概率提升至60%。",
    "9": "使用「配件技能」后立即回复50%电能，且视为触发一次「换弹」。",
    "5": "【电震射击】(5)有20%概率「视为命中弱点」（对非玩家为100%），且(5)对50%生命值以下的目标伤害提升30%。"
   },
   "icon": "ui/item_icon/icon_jin_dian",
   "desc": "特级异变核芯，装配后持续充入电能，射击消耗电能触发额外电震射击。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660066",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660066",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_dian_b.ktx",
      "base": "ui/item_icon/icon_jin_dian_b",
      "ext": ".ktx",
      "pack": "0181.gpk",
      "row": 4174,
      "fid": "FAA6E15B55CFDCD1",
      "gpk_loc0_offset": 187184796,
      "pkgidx": 13,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_dian_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660068",
   "item_id": 660068,
   "name": "鸣闪火花",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "霰弹枪",
   "skill_desc": "霰弹枪在弹片「命中」目标时，会为目标附加#f(5)持续5秒的【火花】效果#n。【火花】效果初始为1级，每#f(5)「命中」20发弹片会使【火花】效果升级#n，至多5级。#r目标存在【火花】效果时，基于火花的等级，#f(5)每0.4~0.11秒（随火花等级缩短）造成{0}的「持续伤害」（基准值取所有弹片对该目标造成的平均伤害）#n。#r弹片命中存在满级【火花】的目标后，下次射击会#f(5)额外追加一发【爆焰弹】#n。【爆焰弹】的弹片数量为射击的25%，单个弹片伤害为射击的100%。#r追加【爆焰弹】的射击命中目标时，【爆焰弹】必定命中目标。",
   "rank_star_segments": {
    "12": "击败目标时下3次射击(5)基础射速提升66%，且叠加火花效率翻倍。",
    "9": "火花累积造成25次伤害后会(5)提升自身3%射速，至多可叠加6层。10秒未叠加时效果消失。",
    "5": "火花爆炸时，有5%~25%的概率（随火花等级提升）(5)使该次火花爆炸伤害提升100%。"
   },
   "icon": "ui/item_icon/icon_jin_huo",
   "desc": "特级异变核芯，装配后霰弹枪射击附加火花持续造成伤害，火花叠满后射击追加爆焰弹。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660068",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660068",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_huo_b.ktx",
      "base": "ui/item_icon/icon_jin_huo_b",
      "ext": ".ktx",
      "pack": "0181.gpk",
      "row": 4175,
      "fid": "A33EE5A1B62F478B",
      "gpk_loc0_offset": 187195160,
      "pkgidx": 13,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_huo_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660072",
   "item_id": 660072,
   "name": "凝滞侵袭",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "狙击枪",
   "skill_desc": "狙击枪#f(5)射速提升10%#n，射击可以#f(5)凝滞#n命中的部位#f(5)6#n秒并且#f(5)根据部位#n造成不同#f(5)负面效果#n，命中已凝滞#f(5)弱点#n时，凝滞效果会随机侵袭其他部位（优先未凝滞部位）。#r命中目标时，若目标有已凝滞部位，造成#f(5){0}追击伤害#n（对怪物为1.5倍）。#r#f(5)开镜#n时可以观察到#f(5)瞄准目标#n的#f(5)凝滞状态效果#n。#r#f(5)玩家#n有#f(5)3#n个可凝滞部位：凝滞腿部降低#f(5)20%#n移动速度，凝滞身躯（含手部）降低#f(5)10%#n射击和挥砍速度，凝滞头部降低#f(5)15%#n生命护盾回复和#f(5)10%#n头部伤害减免。#r#f(5)怪物#n有#f(5)2#n个可凝滞部位：凝滞非弱点降低#f(5)20%#n移动速度，凝滞弱点降低#f(5)15%#n生命回复和#f(5)10%#n头部伤害减免。",
   "rank_star_segments": {
    "12": "命中目标时，若目标所有部位被凝滞，额外造成(5)2秒「冰冻」效果（对玩家衰减50%），同一个目标(5)5秒内只会受到一次此效果。",
    "9": "命中已凝滞部位有(5)20%概率(5)视为「命中弱点」，若未触发，则下一次触发概率增加(5)10%。",
    "5": "命中(5)任意已凝滞部位时，凝滞效果将会随机侵袭其他部位（优先未凝滞部位），目标每有1个已凝滞部位，有(5)30%概率(5)额外追击1次。"
   },
   "icon": "ui/item_icon/icon_jin_bing",
   "desc": "特级异变核芯，装配后凝滞命中部位并根据部位造成负面影响，并对凝滞目标进行追击。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660072",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660072",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_bing_b.ktx",
      "base": "ui/item_icon/icon_jin_bing_b",
      "ext": ".ktx",
      "pack": "0178.gpk",
      "row": 2959,
      "fid": "1A2EC9FD318A5906",
      "gpk_loc0_offset": 95726900,
      "pkgidx": 10,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_bing_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660073",
   "item_id": 660073,
   "name": "燎原炽焰",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "喷火器",
   "skill_desc": "喷火器射击命中有25%概率#f(5)点燃#n目标1秒（目标被自身重复施加该效果时，#f(5)可叠加至至多10秒#n），每0.5秒造成#f(5){0}的「持续伤害」#n并#f(5)充能1%#n。#r在喷火器的充能累积至满时，在下次尝试开火时会立即装填一个弹匣（可触发所有换弹效果）并#f(5)使下个弹匣的射击喷射【炽焰】。#r【炽焰】同时可命中数量增加2个，射速增加20%（【炽焰】伤害频率受射速提升影响）#n。#r【炽焰】状态最多持续20秒，使用按键进行换弹或使用弹药箱补弹时，会立即退出炽焰效果。",
   "rank_star_segments": {
    "12": "喷火器命中或点燃(5)击败目标时获得10%充能（在炽焰状态则为填充10%弹药）。",
    "9": "目标受到(5)点燃伤害时，(5)有25%概率额外点燃40距离内的一个其他敌人。",
    "5": "炽焰附加点燃的概率提升至35%，且(5)附加点燃时额外结算一次点燃伤害。"
   },
   "icon": "ui/item_icon/icon_jin_huo",
   "desc": "特级异变核芯，装配后射击点燃目标并充能，充能后喷射炽焰猛烈攻击。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660073",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660073",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_huo_b.ktx",
      "base": "ui/item_icon/icon_jin_huo_b",
      "ext": ".ktx",
      "pack": "0181.gpk",
      "row": 4175,
      "fid": "A33EE5A1B62F478B",
      "gpk_loc0_offset": 187195160,
      "pkgidx": 13,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_huo_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660074",
   "item_id": 660074,
   "name": "决斗时刻",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "手枪/双枪",
   "skill_desc": "射速提升#f(5){0}#n，根据#f(5)副手当前使用武器#n获得增益。获得#f(5)【决斗时刻】#n技能，可使用主副手当前武器发起联动攻击，每次联动射击造成140%伤害（受射速加成影响）。#H(0.5)副手#f(5)使用手枪#n时，#f(5)增益#n：副手射击暴击时，额外提升下次射击射速15%；#f(5)技能#n：对周围50距离（空中释放时为前方200距离）内最多2目标发动5次射击。#H(0.5)副手#f(5)展开盾牌#n时，#f(5)增益#n：受到的来自正面的伤害降低10%；#f(5)技能#n：格挡50距离内第一个攻击自身的目标，将其击倒并对准星方向进行4次快速射击。#H(0.5)副手#f(5)使用冷兵器#n时，#f(5)增益#n：挥砍造成伤害后，3秒内火力提升15%；#f(5)技能#n：斩击击退正面50距离内的目标并对准星方向进行4次快速射击。#H(0.5)副手#f(5)未使用武器#n时，#f(5)增益#n：移动速度提升6%，射击命中弱点时额外提升12%；#f(5)技能#n：对准星方向进行4次快速射击，每命中1次获得2秒20%移速加成。#H(0.5)联动射击对怪物造成2倍伤害。",
   "rank_star_segments": {
    "12": "【决斗时刻】成功造成伤害时，(5)冷却时间缩短50%。",
    "9": "使用【决斗时刻】技能后，6秒内(5)移动速度提升20%。",
    "5": "【决斗时刻】技能过程中，自身可以(5)免疫一次击倒、击飞、麻痹、冰冻控制效果，且(5)受到伤害降低30%。"
   },
   "icon": "ui/item_icon/icon_jin_huo",
   "desc": "特级异变核芯，装配后根据副手武器变化被动效果与强力技能。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660074",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660074",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_huo_b.ktx",
      "base": "ui/item_icon/icon_jin_huo_b",
      "ext": ".ktx",
      "pack": "0181.gpk",
      "row": 4175,
      "fid": "A33EE5A1B62F478B",
      "gpk_loc0_offset": 187195160,
      "pkgidx": 13,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_huo_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660076",
   "item_id": 660076,
   "name": "余烬流火",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "弓箭",
   "skill_desc": "每次射击会依次射出#f(5)三根40%伤害的箭矢#n，箭矢间隔为0.1秒，后续两根箭矢不受蓄力影响。箭矢命中目标时特制箭头将会碎裂，在目标身上#f(5)附着1-2层持续5秒的余烬#n（最多7层），箭矢命中时可以引燃余烬造成#f(5)层数*{0}#n的伤害，每次引燃消耗一层余烬。#r箭矢间隔会影响射击速度。",
   "rank_star_segments": {
    "12": "击败目标后5秒内，箭矢命中(5)额外附着1层余烬，期间再次击败刷新时长。",
    "9": "三根箭矢(5)间隔缩短至0.08秒，射速加成越高间隔越短，最短间隔为0.06秒。",
    "5": "余烬上限增加至10层，目标余烬超过7层时，有50%几率触发(5)多次引燃直至剩余6层余烬。"
   },
   "icon": "ui/item_icon/icon_jin_huo",
   "desc": "特级异变核芯，装配后每次连续射出三支箭矢，命中时留下可引燃的余烬。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660076",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660076",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_huo_b.ktx",
      "base": "ui/item_icon/icon_jin_huo_b",
      "ext": ".ktx",
      "pack": "0181.gpk",
      "row": 4175,
      "fid": "A33EE5A1B62F478B",
      "gpk_loc0_offset": 187195160,
      "pkgidx": 13,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_huo_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660077",
   "item_id": 660077,
   "name": "穿心极雷",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "霰弹枪",
   "skill_desc": "霰弹枪射击#f(5)变为发射单发电磁弹#n，电磁弹会在#f(5)飞行60距离或直接命中目标#n后爆散成为霰弹弹片（弹片数量和伤害与常规霰弹射击一致）。弹片在命中时有10%概率附带#f(5){0}伤害的磁暴（视为非弱点「命中」）#n。#r电磁弹直接命中目标时，视为弹片全部命中该位置，且自身#f(5)进入持续5秒的【电能充盈】状态#n。#r【电能充盈】状态下，射速提升10%，移动速度提升10%，磁暴触发概率提升至15%，磁暴对非玩家伤害提升100%。",
   "rank_star_segments": {
    "12": "敌方玩家的(5)护盾值在电场内归0时会触发一次250%的伤害（对同一目标内置冷却时间15秒），并(5)附加5秒「护盾失效」。",
    "9": "电场存在时，射空的弹片会(5)被电场磁化吸回并储存。电场内有敌方目标时，(5)每0.2秒消耗1发储存弹片对目标造成1次磁暴伤害。",
    "5": "【电能充盈】状态下自身周围会产生60范围的电场，弹片附带磁暴概率提升至25%。\n敌方玩家在电场内(5)触发护盾恢复（不包含自然恢复）时会(5)触发1次磁暴打击（同一目标内置冷却1秒）。敌方目标每累计回复20%最大护盾值时，会(5)额外触发2次磁暴打击（无内置冷却）。"
   },
   "icon": "ui/item_icon/icon_jin_dian",
   "desc": "特级异变核芯，装配后霰弹枪射击发射单发电磁弹，直接命中或一段距离后爆散为弹片。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660077",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660077",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_dian_b.ktx",
      "base": "ui/item_icon/icon_jin_dian_b",
      "ext": ".ktx",
      "pack": "0181.gpk",
      "row": 4174,
      "fid": "FAA6E15B55CFDCD1",
      "gpk_loc0_offset": 187184796,
      "pkgidx": 13,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_dian_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660078",
   "item_id": 660078,
   "name": "凝华效应",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "突击步枪",
   "skill_desc": "突击步枪射击「命中」时，会额外#f(5)附带1发【冰凌】「追击」，对目标造成造成{0}伤害#n。#r【冰凌】命中目标时，有8%概率使目标进入【凝华】状态3秒，该状态下#f(5)突击步枪射击「命中」目标时，会额外产生1发【冰凌】「追击」#n。#r不同幸存者造成的【凝华】状态效果共享，重复触发时刷新持续时间。",
   "rank_star_segments": {
    "12": "自身施加【凝华】时，额外附带持续3秒的20%「减速」，且【凝华】概率提升至10%，伤害额外提升5%。",
    "9": "触发【凝华】效果时，会在1秒内(5)以0.25秒/发的间隔持续向目标额外发射【冰凌】。",
    "5": "自身对【凝华】状态下的目标再次触发【凝华】效果时，额外(5)产生一次100%伤害的冰爆。"
   },
   "icon": "ui/item_icon/icon_jin_bing",
   "desc": "特级异变核芯，装配后突击步枪射击附带冰凌追击，命中时概率冻伤目标增幅后续命中。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660078",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660078",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_bing_b.ktx",
      "base": "ui/item_icon/icon_jin_bing_b",
      "ext": ".ktx",
      "pack": "0178.gpk",
      "row": 2959,
      "fid": "1A2EC9FD318A5906",
      "gpk_loc0_offset": 95726900,
      "pkgidx": 10,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_bing_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660079",
   "item_id": 660079,
   "name": "蓄势寒锋",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "冷兵器",
   "skill_desc": "使用冷兵器时#f(5)火力提升至{0}#n，并获得#f(5)10%概率正面#n#f(1249)「伤害抵御」#n。#r战斗状态下，每秒获得3%「充能」，且在触发#f(1249)「伤害抵御」#n时，额外获得5%「充能」和2%「护盾回复」（内置冷却1.5秒）。#r#f(5)充能达到50%后，可以开启技能进入【寒锋】状态，改变攻击形态，每秒消耗4%「充能」#n，且#f(5)攻击过程中获得50%概率正面#n#f(1249)「伤害抵御」#n。#r50%能量：攻击变为【重刃】，按下攻击键时每秒消耗18%能量并蓄力，过程中持续对附近敌人造成20%「减速」，释放后向前爆发出100%-180%基于蓄力时间提升（至多1.5秒，「挥砍速度提升」可以缩短蓄力时间）的斩击并造成至多40%「减速」。#r100%能量：攻击变为【连斩】，按下攻击键时每秒消耗18%能量并快速连续斩击敌人，每一击造成70%伤害并附加可叠加至至多40%的「减速」。能量消耗空时会在周围引发爆气，造成120%的冷兵器伤害和1秒40%「减速」。",
   "rank_star_segments": {
    "12": "【寒锋】开启时的(5)「击退」替换为1秒「冰冻」（同目标内置冷却15秒），且(5)可再次使用技能来退出【寒锋】。",
    "9": "【寒锋】状态下(5)每触发1次冷兵器「命中」、「伤害抵御」、「格挡」，提升自身1%「挥砍速度」与0.5%「移速」，可叠加40层。",
    "5": "冷兵器(5)「命中」时可触发核芯的「伤害抵御」效果，且(5)【寒锋】状态下「伤害抵御」可触发获得充能。"
   },
   "icon": "ui/item_icon/icon_jin_bing",
   "desc": "特级异变核芯，装配后冷兵器可在战斗中充能蓄势，充能后可进入强力攻击模式。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660079",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660079",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_bing_b.ktx",
      "base": "ui/item_icon/icon_jin_bing_b",
      "ext": ".ktx",
      "pack": "0178.gpk",
      "row": 2959,
      "fid": "1A2EC9FD318A5906",
      "gpk_loc0_offset": 95726900,
      "pkgidx": 10,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_bing_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660080",
   "item_id": 660080,
   "name": "磁聚轰雷",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "榴弹炮",
   "skill_desc": "榴弹炮弹匣固定为#f(5)2#n 发，换弹速度提升#f(5)50%#n。每次#f(5)换弹#n后，当前炮弹类型在#f(5)正电荷炮弹#n与#f(5)负电荷炮弹#n之间依次交替切换。#r命中目标时，对目标附加炮弹对应属性的电荷 #r当目标身上同时携带#f(5)正电荷#n与#f(5)负电荷#n时，消耗目标身上全部电荷层数，触发一次基础伤害为#f(5){0}#n的磁暴。每消耗#f(5)1#n 层电荷，目标所受的#f(5)磁暴伤害#n提升#f(5)5%#n。",
   "rank_star_segments": {
    "12": "(5)充能炮弹「命中」敌人时，对附近3个目标触发(5)25%伤害的连锁电击。",
    "9": "当榴弹炮打空弹匣时(5)触发瞬间自动换弹，并获得10%的充能。",
    "5": "磁暴消耗电荷时随消耗层数积累充能。每因磁暴而消耗(5)1 层电荷，获得(5)2% 充能。\n满充能后(5)下2次射击发射(5)110%伤害的充能炮弹，充能炮弹不消耗弹匣的弹药，且命中时(5)直接触发磁暴。"
   },
   "icon": "ui/item_icon/icon_jin_dian",
   "desc": "特级异变核芯，装配后榴弹炮命中附带正、负电荷；目标同时存在正、负电荷时触发磁暴",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660080",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660080",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_dian_b.ktx",
      "base": "ui/item_icon/icon_jin_dian_b",
      "ext": ".ktx",
      "pack": "0181.gpk",
      "row": 4174,
      "fid": "FAA6E15B55CFDCD1",
      "gpk_loc0_offset": 187184796,
      "pkgidx": 13,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_dian_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660081",
   "item_id": 660081,
   "name": "淬焰燃锋",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "冷兵器",
   "skill_desc": "使用冷兵器时，命中有#f(5)20%的概率#n对目标#f(5)额外造成一次{0}伤害#n，每0.9秒最多触发1次。#r处于#f(5)战斗状态#n且满足以下#f(5)条件#n时，可获得对应增益效果：#f(5)累计命中5次#n，命中目标造成额外伤害的#f(5)概率#n提升至#f(5)40%；#n #r#f(5)持续战斗10秒#n，冷兵器#f(5)命中#n目标时#f(5)回复1%最大生命值，每秒最多触发3次；#n #r#f(5)累计移动70米#n，命中目标触发#f(5)额外伤害#n时，使目标#f(5)减速30%，持续2秒。#n #r战斗状态下，#f(5)切换武器#n将清空累计进度；重新装备装有此核芯的冷兵器时，已激活的强化效果自动恢复，无需重新触发。#r手持装有此核芯的冷兵器时，强化效果生效；#f(5)脱离战斗10秒#n后效果#f(5)失效。#n",
   "rank_star_segments": {
    "5": "(5)所有效果激活后获得(5)免控效果。可(5)免疫一次击倒、击飞、麻痹、冰冻控制效果，触发免控效果时获得1.5秒的35%移动速度加成。\n(5)免控效果触发后进入(5)15秒冷却。冷却期间(5)冷兵器每次造成伤害缩短1秒冷却时间，当剩余冷却时间小于7秒时，冷兵器造成伤害不再缩短冷却时间。"
   },
   "icon": "ui/item_icon/icon_jin_huo",
   "desc": "特级异变核芯，装配后在战斗中进行强化，获得增益。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660081",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660081",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_huo_b.ktx",
      "base": "ui/item_icon/icon_jin_huo_b",
      "ext": ".ktx",
      "pack": "0181.gpk",
      "row": 4175,
      "fid": "A33EE5A1B62F478B",
      "gpk_loc0_offset": 187195160,
      "pkgidx": 13,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_huo_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660082",
   "item_id": 660082,
   "name": "深蚀追猎",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "手枪/双枪",
   "skill_desc": "使用手枪/双枪时，射击造成#f(5){0}#n的伤害。每次命中目标叠加【酸蚀渗透】层数，当射程内存在【酸蚀渗透】大于#f(5)6层#n的目标时，可对层数最高者发动【处决射击】。#r#f(5)【酸蚀渗透】#n：每次命中加#f(5)1层#n（暴击额外加2层），持续#f(5)10秒#n（命中刷新持续时间），上限叠#f(5)20层#n。命中有【酸蚀渗透】的目标，附加每层#f(5)1%#n酸液属性追击伤害。#r#f(5)【处决射击】#n：消耗所有层数，锁定攻击范围内【酸蚀渗透】层数最高的目标，射出#f(5)3发#n自动瞄准的子弹，共造成#f(5)120%+15%×层数#n伤害（对非幸存者伤害翻倍）。若目标离开射击范围则无法命中。冷却时间#f(5)12秒#n。",
   "rank_star_segments": {
    "12": "【处决射击】触发追击伤害，并降低命中目标的(5)30%生命回复（持续(5)5秒）。",
    "9": "暴击命中目标时，有概率触发一次额外追击伤害。\n额外追击伤害触发概率：(5)6层时10%，此后每叠1层【酸蚀渗透】，触发概率提升(5)2%，最高(5)58%。\n【处决射击】的处决过程中，(5)每次暴击命中使下一发处决子弹伤害提升(5)30%（连续暴击可叠加）。",
    "5": "【酸蚀渗透】最高可叠至30层。叠至(5)6层及以上时，目标生命回复降低(5)30%"
   },
   "icon": "ui/item_icon/icon_jin_suan",
   "desc": "特级异变核芯，装配后手枪命中累计酸蚀渗透层数，叠至6层可发动技能，对单体目标造成大量伤害。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660082",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660082",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_suan_b.ktx",
      "base": "ui/item_icon/icon_jin_suan_b",
      "ext": ".ktx",
      "pack": "0178.gpk",
      "row": 3296,
      "fid": "2713A9C2A45D28A4",
      "gpk_loc0_offset": 98170332,
      "pkgidx": 10,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_suan_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660100",
   "item_id": 660100,
   "name": "疾影火刃",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "冷兵器",
   "skill_desc": "持冷兵器时，装配后可以#f(5)长按技能键，持刀蓄力以更快的速度向前冲刺#n，冲刺过程中可以划动操作转向。#r#r冲刺中每移动40距离，都会造成一次小范围伤害。#r松开攻击键或气力耗尽会结束冲刺并触发重斩，造成#f(5){0}#n伤害，对玩家造成的重斩伤害衰减#f(5)50%#n。#r#r冲刺时#f(5)气力消耗提升100%#n，使用重斩时会#f(5)基于冲刺距离回复至多40%气力#n，重斩命中会#f(5)额外回复少量气力#n。#r冲刺时可以点击左侧攻击键进行跳跃。",
   "rank_star_segments": {
    "12": "冲刺过程中(5)免疫「减速」、「击飞」、「麻痹」、「冰冻」、「定身」同时降低受到的非玩家伤害(5)50%。",
    "9": "每冲刺40距离，提升冲刺阶段(5)「移动速度」8%，上限为40%。",
    "5": "每冲刺40距离提升(5)重斩伤害8%，上限为60%。在达到上限时，重斩伤害额外造成(5)「击倒」效果。"
   },
   "icon": "ui/item_icon/icon_jin_huo",
   "desc": "特级异变核芯，装配后冷兵器长按蓄力可以向前冲锋接续强力火焰斩击。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660100",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660100",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_huo_b.ktx",
      "base": "ui/item_icon/icon_jin_huo_b",
      "ext": ".ktx",
      "pack": "0181.gpk",
      "row": 4175,
      "fid": "A33EE5A1B62F478B",
      "gpk_loc0_offset": 187195160,
      "pkgidx": 13,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_huo_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660101",
   "item_id": 660101,
   "name": "绝对零度",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "榴弹炮",
   "skill_desc": "装配后榴弹炮攻击时，在炮弹爆炸位置形成#f(5)持续10秒的冰冻区域#n，造成#f(5)50%的「减速」效果（对玩家减半）#n。#r#r炮弹#f(5)「命中」#n自身产生的冰冻区域时，会在冰冻区域上引发爆炸，造成一次#f(5){0}#n的额外#f(5)范围伤害#n。",
   "rank_star_segments": {
    "12": "目标每连续位于冰冻区域上0.5秒，其受到的(5)冰爆伤害和冰面持续伤害会提升(5)5%，该效果最多可叠加(5)6次。",
    "9": "目标位于冰场上时，(5)每秒受到一定的冰冻伤害。\n深潜重炮三段蓄力时，冰场持续伤害会(5)在基础上进行对应提升。",
    "5": "被冰爆命中的目标会被(5)「冰冻」1秒，在玩家的(5)爆炸伤害加成属性超过50%时(5)加长为2秒。\n\n「冰冻」效果对每个目标有(5)10秒内置冷却时间，且对玩家衰减70%。"
   },
   "icon": "ui/item_icon/icon_jin_bing",
   "desc": "特级异变核芯，装配后榴弹炮打出减速冰场，炮击再次命中冰场会产生冰爆。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660101",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660101",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_bing_b.ktx",
      "base": "ui/item_icon/icon_jin_bing_b",
      "ext": ".ktx",
      "pack": "0178.gpk",
      "row": 2959,
      "fid": "1A2EC9FD318A5906",
      "gpk_loc0_offset": 95726900,
      "pkgidx": 10,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_bing_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660102",
   "item_id": 660102,
   "name": "脉冲闪电",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "手枪/双枪",
   "skill_desc": "手枪累积#f(5)7次（双枪为10次）「子弹命中」#n后，下次射击会进入#f(5)持续0.8秒的脉冲扫射状态#n。#r#r脉冲扫射#f(5)基础射击速度提升为500%且不消耗子弹#n，每一击火力值为原火力值的#f(5){0}#n。#r#r#f(5)每90%的「暴击率」会增加0.1秒的脉冲扫射持续时长，总上限1.2秒#n。",
   "rank_star_segments": {
    "12": "脉冲扫射及弹射伤害每「暴击」1次，自身(5)暴击伤害增加4%，上限为(5)50%。脉冲扫射结束时重置。",
    "9": "脉冲扫射结束瞬间会(5)触发一次瞬间「自动换弹」。",
    "5": "脉冲扫射命中时随机对(5)100距离内的敌方进行(5)50%伤害的「弹射」。"
   },
   "icon": "ui/item_icon/icon_jin_dian",
   "desc": "特级异变核芯，装配后手枪命中7次后，下次射击向前打出极快速的多次射击。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660102",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660102",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_dian_b.ktx",
      "base": "ui/item_icon/icon_jin_dian_b",
      "ext": ".ktx",
      "pack": "0181.gpk",
      "row": 4174,
      "fid": "FAA6E15B55CFDCD1",
      "gpk_loc0_offset": 187184796,
      "pkgidx": 13,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_dian_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660112",
   "item_id": 660112,
   "name": "极光狙击",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": null,
   "skill_desc": "",
   "rank_star_segments": {
    "12": "对被自身造成的(5)易伤效果影响的目标射击时，造成一次(5)8%的「额外伤害」，该伤害在「命中弱点」时(5)提升为12%。",
    "9": "被自身造成的(5)易伤效果影响的目标，受到射击伤害时有(5)10%概率(5)视为「命中弱点」。",
    "5": "「命中弱点」后，射击伤害(5)在6秒内增加8%，该效果可以(5)叠加至多4次，在未「连续命中弱点」时重置。"
   },
   "icon": "ui/item_icon/icon_jin_dian",
   "desc": "特级异变核芯，装配后狙击概率锁头并可使目标易伤。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660112",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660112",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_dian_b.ktx",
      "base": "ui/item_icon/icon_jin_dian_b",
      "ext": ".ktx",
      "pack": "0181.gpk",
      "row": 4174,
      "fid": "FAA6E15B55CFDCD1",
      "gpk_loc0_offset": 187184796,
      "pkgidx": 13,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_dian_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）"
   }
  },
  {
   "id": "s12_660113",
   "item_id": 660113,
   "name": "极寒冰爆",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "霰弹枪",
   "skill_desc": "装配后，霰弹枪射击的#f(5)「弹片数量」增加两发#n，弹道分布方式变为基于准星#f(5)横向水平散布#n，总数量与射击对应的霰弹枪弹片数量一致。#r#r每个弹片造成#f(5){0}#n的伤害，并在「命中」时叠加1层#f(5)霜冻标记#n（至多150层）。若弹片「暴击」，则会额外叠加1层#f(5)霜冻标记#n。#r#r装配后，可使用#f(5)极寒冰爆#n来向准星方向打出一发爆裂冰弹，对被命中的目标造成#f(5)300%+8%*霜冻标记层数#n的伤害，并清除其层数。",
   "rank_star_segments": {
    "12": "「暴击」会在1.5秒内提升自身(5)0.4%「射速」，该效果可叠加至至多(5)12%。",
    "9": "目标每有1%的「已损失生命值」，极寒冰爆造成的伤害(5)提升1%，至多提升50%。且标记可叠加上限提升至200层。",
    "5": "自身每为目标添加20层霜冻层数，会对目标额外造成(5)100%伤害并使其在2秒内(5)「减速」25%。"
   },
   "icon": "ui/item_icon/icon_jin_bing",
   "desc": "特级异变核芯，装配后霰弹枪打出扇形弹道并可使用冰爆弹。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660113",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660113",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_bing_b.ktx",
      "base": "ui/item_icon/icon_jin_bing_b",
      "ext": ".ktx",
      "pack": "0178.gpk",
      "row": 2959,
      "fid": "1A2EC9FD318A5906",
      "gpk_loc0_offset": 95726900,
      "pkgidx": 10,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_bing_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660116",
   "item_id": 660116,
   "name": "炽热枪膛",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "电磁机枪",
   "skill_desc": "电磁机枪射击会#f(5)逐渐累积热能#n（累积速度受电磁机枪充能速度的数值影响），热能值会影响电磁机枪的射速和伤害，停止射击一小段时间后开始衰减。#r电磁机枪初始射速提升为400，射击初始造成40%伤害，随热能累积逐渐提升至#f(5){0}伤害#n。#r#r电磁机枪的「换弹」动作被替换为进行一轮至多10次的#f(5)爆燃射击#n同时换弹并清空热能，每次射击造成#f(5)135%#n的满热能值射击伤害。#r#f(5)爆燃射击#n对玩家造成的伤害衰减#f(5)25%#n。",
   "rank_star_segments": {
    "12": "爆燃射击每次命中时，后续爆燃射击的(5)伤害倍率提升1.5%，至多可叠加30层，在触发换弹时重置。",
    "9": "电磁机枪在热能为满值的状态下射击时(5)20%概率触发爆燃射击。",
    "5": "(5)弹匣容量提升25%，热能为满值时射击(5)35%概率不消耗弹药。"
   },
   "icon": "ui/item_icon/icon_jin_huo",
   "desc": "特级异变核芯，装配后电磁机枪伤害随射击提升并在换弹时打出燃烧射击。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660116",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660116",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_huo_b.ktx",
      "base": "ui/item_icon/icon_jin_huo_b",
      "ext": ".ktx",
      "pack": "0181.gpk",
      "row": 4175,
      "fid": "A33EE5A1B62F478B",
      "gpk_loc0_offset": 187195160,
      "pkgidx": 13,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_huo_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660118",
   "item_id": 660118,
   "name": "侵蚀效应",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "突击步枪",
   "skill_desc": "突击步枪在没有标记目标的情况下#f(5)累积命中「同一目标」5次后#n，会用#f(5)标记#n锁定该目标（#f(5)标记#n同时只存在一个。#r射击命中#f(5)标记#n锁定的目标时，造成伤害的#f(5){0}#n会被额外累积为酸溶值。#r#r#f(5)标记#n初始为一阶段，随#f(5)「子弹命中」#n会逐渐提升阶段，并基于阶段获得以下效果：#r一阶段及以上：「子弹命中」时8%概率触发#f(5)强酸#n效果，使该次射击穿透护盾直接造成「血量削减」。自身#f(5)每80%「暴击率」会提升强酸效果触发概率1%，至多提升至12%#n#r二阶段及以上：「子弹命中」时#f(5)20%概率使射速在0.5秒内提升200%#n（冷却时间2.5秒）#r三阶段：#f(5)3秒内射击不消耗子弹#n#r#r在#f(5)三阶段结束#n或#f(5)酸溶值超过目标剩余生命值+护盾值#n后，移除#f(5)标记#n并对其造成#f(5)100%*酸溶值#n的「触发伤害」。#r切换武器或10秒内未对目标造成伤害时也会移除#f(5)标记#n，此时造成#f(5)50%*酸溶值#n的「触发伤害」。",
   "rank_star_segments": {
    "12": "(5)标记阶段提升时，对(5)标记目标造成一次(5)20%*酸溶值的伤害并(5)「麻痹」目标1秒。",
    "9": "击败被(5)标记的目标时，(5)瞬间进行一次「自动换弹」并提升25%「射速」，持续4秒。",
    "5": "(5)强酸效果触发时，该次伤害(5)视为「命中弱点」。每触发一次(5)强酸效果，提升自身(5)4%移速，持续5秒，可叠加至多5层。"
   },
   "icon": "ui/item_icon/icon_jin_suan",
   "desc": "特级异变核芯，装配后突击步枪射击标记目标并累积酸液伤害",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660118",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660118",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_suan_b.ktx",
      "base": "ui/item_icon/icon_jin_suan_b",
      "ext": ".ktx",
      "pack": "0178.gpk",
      "row": 3296,
      "fid": "2713A9C2A45D28A4",
      "gpk_loc0_offset": 98170332,
      "pkgidx": 10,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_suan_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660119",
   "item_id": 660119,
   "name": "酸焰激流",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "喷火器",
   "skill_desc": "喷火器在命中目标时，会为目标叠加#f(5)酸焰#n层数，持续3秒，至多9层，每层酸焰层数会增加自身喷火器对目标造成的#f(5)伤害{0}#n。#r#f(5)酸焰#n层数叠加至9层的目标会以自身为中心产生半径40的#f(5)酸蚀圈#n，圈内目标会被减速25%。#r酸蚀圈中心的目标受到喷火器攻击时，有#f(5)20%概率产生酸蚀爆炸#n，对酸蚀圈内至多3个其他目标造成#f(5)60%的伤害#n。#r酸蚀圈内目标死亡时，#f(5)100%概率产生酸蚀爆炸#n。",
   "rank_star_segments": {
    "12": "被酸蚀圈影响的目标(5)受到35%的「恢复降低」，且降低部分会被(5)等比例转化为自身恢复。",
    "9": "300范围内每有一个来源于自身的酸蚀圈，喷火器(5)攻击频率提升3%，至多12%。",
    "5": "酸蚀圈中心的目标被酸蚀爆炸命中时，(5)有25%概率在0.1秒延迟后引发一次酸蚀爆炸。"
   },
   "icon": "ui/item_icon/icon_jin_suan",
   "desc": "特级异变核芯，装配后喷火器喷射酸焰灼烧目标造成额外伤害并减速",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660119",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660119",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_suan_b.ktx",
      "base": "ui/item_icon/icon_jin_suan_b",
      "ext": ".ktx",
      "pack": "0178.gpk",
      "row": 3296,
      "fid": "2713A9C2A45D28A4",
      "gpk_loc0_offset": 98170332,
      "pkgidx": 10,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_suan_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660125",
   "item_id": 660125,
   "name": "极限火力",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "榴弹炮",
   "skill_desc": "使用榴弹炮时，可以通过技能按键进入架设模式，#f(5)架设模式下不可移动#n。#r架设模式下，榴弹炮#f(5)射速提升25%，爆炸范围提升20%，弹道速度提升100%，射击造成{0}伤害#n。#r架设模式下榴弹炮#f(5)对玩家造成的伤害衰减为70%#n。#r使用深潜重炮时，深潜重炮#f(5)射击蓄力速度提升#n，且满蓄力炮击会产生火焰区域。",
   "rank_star_segments": {
    "12": "架设模式下，每次射击和溅射命中目标会提升自身(5)0.5%爆炸伤害加成，至多可叠加40层。退出架设模式时重置该加成。",
    "9": "架设模式弹匣容量恒定为1，(5)每次射击后会「自动换弹」并触发所有换弹效果。",
    "5": "架设模式下每次「射击」后，在命中范围内产生(5)共8次额外的15%「范围伤害」。"
   },
   "icon": "ui/item_icon/icon_jin_huo",
   "desc": "特级异变核芯，装配后可以进入架设模式，对更大范围的目标更快的进行轰炸。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660125",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660125",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_huo_b.ktx",
      "base": "ui/item_icon/icon_jin_huo_b",
      "ext": ".ktx",
      "pack": "0181.gpk",
      "row": 4175,
      "fid": "A33EE5A1B62F478B",
      "gpk_loc0_offset": 187195160,
      "pkgidx": 13,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_huo_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660126",
   "item_id": 660126,
   "name": "电掣双刀",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "冷兵器",
   "skill_desc": "#f(5)仅在副武器装备冷兵器时可以使用。#n#r使用冷兵器时，常规模式下每秒获得#f(5)5%#n「充能」。持续移动和攻击命中时会#f(5)额外获得充能#n。#r充能达到#f(5)70%#n时，可以激活技能#f(5)切换为双刀模式#n，同时对周围#f(5)50#n范围内的目标造成一次#f(5)50%#n的伤害。#r#r双刀模式下每秒消耗#f(5)5%#n能量，攻击时会同时使用主副武器进行#f(5)二连斩#n，共计造成#f(5){0}#n伤害（该伤害#f(5)对非玩家目标提升40%#n）（可触发「命中效果」）。#r双刀模式下获得#f(5)15%#n「移速提升」和每秒#f(5)2.5%#n的「护盾回复」。",
   "rank_star_segments": {
    "12": "双刀模式下，每秒获得(5)1.5%暴击率和(5)1.5%免暴率加成，最多叠加(5)12层。切换武器或退出双刀模式后消失。",
    "9": "双刀模式下挥砍命中回复(5)15气力，每击败一个目标回复(5)20%能量，突进斩击命中回复(5)10%能量。",
    "5": "双刀模式下解锁(5)突进技能，冷却时间(5)4秒。使用后向前方快速突进，造成一次(5)100%伤害的斩击并获得1.5秒的(5)40%「移速提升」。"
   },
   "icon": "ui/item_icon/icon_jin_dian",
   "desc": "特级异变核芯，装配后可以开启双刀模式，大幅提升机动性和作战能力。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660126",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660126",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_dian_b.ktx",
      "base": "ui/item_icon/icon_jin_dian_b",
      "ext": ".ktx",
      "pack": "0181.gpk",
      "row": 4174,
      "fid": "FAA6E15B55CFDCD1",
      "gpk_loc0_offset": 187184796,
      "pkgidx": 13,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_dian_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660128",
   "item_id": 660128,
   "name": "呼啸寒霜",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "喷火器",
   "skill_desc": "喷火器喷出冰雾，目标每次被命中会叠加一层#f(5)5秒#n的#f(5)冰雾#n效果，每层造成#f(5)5%「减速」#n，最多#f(5)3层#n，达到最高层后，目标进入#f(5)冻伤#n状态，持续#f(5)3秒#n，每秒受到#f(5){0}「持续伤害」#n（对非玩家伤害提升#f(5)100%#n），目标在冻伤状态期间被命中不会刷新冻伤持续时间，冻伤状态结束后清空冰雾层数。#r冰雾和冻伤均为「负面效果」",
   "rank_star_segments": {
    "12": "每次喷火器命中会延长冻伤状态的时长(5)0.5秒，最长(5)6秒，达到最长时间后冻伤附加(5)50%「回复降低」。",
    "9": "冻伤状态的目标受到的所有冰冻伤害增加(5)5%。",
    "5": "对冻伤状态的目标造成「暴击」时削弱其(5)2点护甲（视为「负面效果」），持续(5)0.5秒。"
   },
   "icon": "ui/item_icon/icon_jin_bing",
   "desc": "特级异变核芯，装配后喷火器攻击累积减速，并且造成持续伤害。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660128",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660128",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_bing_b.ktx",
      "base": "ui/item_icon/icon_jin_bing_b",
      "ext": ".ktx",
      "pack": "0178.gpk",
      "row": 2959,
      "fid": "1A2EC9FD318A5906",
      "gpk_loc0_offset": 95726900,
      "pkgidx": 10,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_bing_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660130",
   "item_id": 660130,
   "name": "刺骨冰锥",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "手枪/双枪",
   "skill_desc": "手枪/双枪射击动作改变，基础射速降低，射击造成#f(5){0}伤害#n，且副手射击伤害不再衰减。#r目标#f(5)每损失25%生命值，射击对其造成5%伤害的「追击」#n。#r对目标的每第4次命中会引发冰爆，冰爆造成#f(5)60%~90%伤害的「追击」（基于目标已损失生命值比例）#n。10秒内未命中该目标时，对目标的命中计数重置。#r具有“主宰”特技的双枪装配该核芯时，特技的副手射击伤害提升效果会以一定比例加成到基础射击伤害中。",
   "rank_star_segments": {
    "12": "射击命中冰冻状态的目标时，(5)直接触发冰爆效果。且冰爆命中除特殊感染体之外的感染体时，(5)有40%的概率「冰冻」目标1秒（该效果具有5秒内置冷却时间）。",
    "9": "射击触发冰爆时，该次射击的基础伤害在结算时(5)「暴击率」额外提升35%。",
    "5": "对目标触发冰爆效果后，下次射击有(5)12%的基础概率对其直接触发冰爆效果。该概率会随对目标造成冰爆的次数(5)逐渐提升至至多40%。"
   },
   "icon": "ui/item_icon/icon_jin_bing",
   "desc": "特级异变核芯，装配后双枪对残血目标造成额外伤害，连续命中引发冰爆造成高额伤害。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660130",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660130",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_bing_b.ktx",
      "base": "ui/item_icon/icon_jin_bing_b",
      "ext": ".ktx",
      "pack": "0178.gpk",
      "row": 2959,
      "fid": "1A2EC9FD318A5906",
      "gpk_loc0_offset": 95726900,
      "pkgidx": 10,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_bing_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660131",
   "item_id": 660131,
   "name": "连锁反应",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "霰弹枪",
   "skill_desc": "射击造成#f(5){0}#n伤害。#r#f(5)「射击命中」获得3点能量，「弹片命中」额外获得1点能量（命中玩家时获得2点）#n，上限100。停止射击1.5秒后持续损失能量，能量达到不同阶段时获得相应增益。#r一阶段（0-20）：无变化。#r二阶段（20-60）：#f(5)每5点能量提升5基础射速#n，同时减少4%伤害。#r三阶段（60-100）：进入#f(5)狂热状态#n，#f(5)基础射速提升20#n，伤害衰减至60%，#f(5)每发弹片命中有15%概率触发酸爆，造成10%伤害#n。#r能量充满：下次射击不消耗子弹，转而#f(5)消耗所有能量发射强力酸蚀爆弹，每发弹片命中后造成3次100%伤害，触发酸爆概率提升为40%#n。发射动作结束后自动触发「换弹」。#f(5)酸蚀爆弹对玩家伤害衰减至70%#n。#r切换武器后清空当前能量条。",
   "rank_star_segments": {
    "12": "酸蚀爆弹变为(5)快速二连发，(5)第二发弹片数量衰减为第一发的50%。",
    "9": "狂热状态下，(5)「弹片命中」使目标受到自身伤害增加0.3%，持续3秒，上限30层。",
    "5": "狂热状态下，每次射击(5)额外发射1枚弹片。"
   },
   "icon": "ui/item_icon/icon_jin_suan",
   "desc": "特级异变核芯，装配后霰弹枪随着能量积蓄提升射速，蓄满后打出狂暴一击。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660131",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660131",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_suan_b.ktx",
      "base": "ui/item_icon/icon_jin_suan_b",
      "ext": ".ktx",
      "pack": "0178.gpk",
      "row": 3296,
      "fid": "2713A9C2A45D28A4",
      "gpk_loc0_offset": 98170332,
      "pkgidx": 10,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_suan_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660134",
   "item_id": 660134,
   "name": "裂变效应",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "突击步枪",
   "skill_desc": "突击步枪枪口处生成一台浮游炮，射击命中时有#f(5)20%#n概率(每#f(5)6%「射速」#n额外提升#f(5)1%#n概率，最多提升#f(5)10%#n）使其追加#f(5)1#n次#f(5){0}#n伤害的「追击」。每次触发#f(5)「追击」#n后提升#f(5)1%#n概率，至多提升至#f(5)40%#n，#f(5)3#n秒未触发则重置。#r触发#f(5)「追击」#n时获得#f(5)5#n点「充能」（对玩家为#f(5)10#n点）。充能达到#f(5)100#n后下次射击进入持续#f(5)5#n秒的#f(5)裂变爆发#n状态：每次射击#f(5)必定触发「追击」#n，且#f(5)有40%概率触发裂变#n使单次#f(5)「追击」#n同时发射#f(5)3#n颗子弹。#r裂变爆发状态结束后浮游炮失效#f(5)4#n秒，期间无法发射和充能，同时清空概率提升层数。",
   "rank_star_segments": {
    "12": "裂变爆发结束后，浮游炮(5)不再失效。",
    "9": "裂变爆发状态下，(5)触发裂变概率翻倍。",
    "5": "进入裂变爆发状态时，(5)瞬间补满弹匣。"
   },
   "icon": "ui/item_icon/icon_jin_huo",
   "desc": "特级异变核芯，装配后可以生成熔岩浮游炮对目标造成额外打击",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660134",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660134",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_huo_b.ktx",
      "base": "ui/item_icon/icon_jin_huo_b",
      "ext": ".ktx",
      "pack": "0181.gpk",
      "row": 4175,
      "fid": "A33EE5A1B62F478B",
      "gpk_loc0_offset": 187195160,
      "pkgidx": 13,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_huo_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660135",
   "item_id": 660135,
   "name": "球状闪电",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "喷火器",
   "skill_desc": "喷火器射击不造成伤害，变为生成#f(5)球状闪电#n，球状闪电将持续#f(5)「牵引」敌人#n并每#f(5)0.25秒#n对其造成#f(5)100%#n伤害（「牵引」效果和伤害受#f(5)「射速」#n影响，#f(5)晶化感染体#n受到的「牵引」效果翻倍）。连续射击时球状闪电会不断强化，最多可提升#f(5){0}#n伤害，连续射击5秒后达到最大值。",
   "rank_star_segments": {
    "12": "磁暴基础伤害提升为100%，球状闪电每次造成伤害会提升自身的(5)0.2%「暴击率」和(5)0.2%「暴击伤害」（最多叠加(5)20层），磁暴后加成效果重置。",
    "9": "球状闪电磁暴会使敌人(5)「麻痹」0.8秒（对同一目标6秒内仅生效一次）并使其(5)4秒内获得的(5)「护盾回复降低」60%。",
    "5": "球状闪电每次命中会降低敌方(5)0.1护甲且获得(5)5点电量，最多叠加(5)20次；电量达到100后产生一次磁暴，造成(5)30%的额外伤害（对玩家衰减50%）。"
   },
   "icon": "ui/item_icon/icon_jin_dian",
   "desc": "特级异变核芯，装配后可以生成球状闪电对敌人造成牵引和破甲效果。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660135",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660135",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_dian_b.ktx",
      "base": "ui/item_icon/icon_jin_dian_b",
      "ext": ".ktx",
      "pack": "0181.gpk",
      "row": 4174,
      "fid": "FAA6E15B55CFDCD1",
      "gpk_loc0_offset": 187184796,
      "pkgidx": 13,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_dian_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660139",
   "item_id": 660139,
   "name": "贯通战术",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "弓箭",
   "skill_desc": "给箭头附着强酸，命中目标时额外造成3秒该次伤害#f(5){0}的强酸「持续伤害」#n（无法叠加），蓄力完成后强酸箭矢可以#f(5)穿透路径上的目标和障碍物#n（最多8个），每穿透一个障碍物箭矢威力下降50%，每穿透一个目标箭矢威力下降10%（威力最低降至20%），穿透障碍物后箭矢最多再飞行15米。",
   "rank_star_segments": {
    "12": "二段蓄力完成后射出的箭矢穿透障碍物和暴击时留下持续5秒的(5)酸雾，酸雾中的目标受到(5)【腐蚀】效果，离开酸雾3秒后(5)【腐蚀】效果消失。",
    "9": "暴击会额外造成3秒(5)【腐蚀】效果：(5)附加30%「护盾恢复降低」并造成(5)每秒40%「持续伤害」。",
    "5": "蓄力完成后可以进行1秒的(5)二段蓄力，二段蓄力使箭矢的(5)威力增强（最多增强50%）并且二段蓄力完成后(5)穿透目标不再使箭矢威力下降（穿透障碍物依然会使箭矢威力下降）。"
   },
   "icon": "ui/item_icon/icon_jin_suan",
   "desc": "特级异变核芯，装配后蓄力射出的箭矢可以穿透所有障碍物和目标。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660139",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660139",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_suan_b.ktx",
      "base": "ui/item_icon/icon_jin_suan_b",
      "ext": ".ktx",
      "pack": "0178.gpk",
      "row": 3296,
      "fid": "2713A9C2A45D28A4",
      "gpk_loc0_offset": 98170332,
      "pkgidx": 10,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_suan_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660140",
   "item_id": 660140,
   "name": "流光疾射",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "弓箭",
   "skill_desc": "弓箭射击变为二连射，每箭造成#f(5){0}#n伤害并能够触发「命中效果」。#r将移动摇杆拖动到疾跑响应区域（即左侧摇杆的外圈范围）或输入疾跑指令（默认快捷键shift+方向键）时，射击会被替换为快速#f(5)向摇杆方向位移的滑步射击#n。#r滑步射击的过程中，可以实时输入移动指令来微调移动的方向。#r#f(5)移动速度#n会影响滑步射击的速度和频率，且滑步射击会#f(5)额外消耗少量气力#n。",
   "rank_star_segments": {
    "12": "被「减速」（移动速度加成为负）时，(5)滑步射击的速度和频率不会降低。",
    "9": "每次触发(5)滑步射击时增加自身(5)2%「移动速度」（可叠加至至多20%），持续3秒。",
    "5": "射击在5秒内多次命中目标时，基于命中次数会附加(5)每层1.5%（至多叠加至15%）的电磁属性「追击」伤害。"
   },
   "icon": "ui/item_icon/icon_jin_dian",
   "desc": "特级异变核芯，装配后射击会发出两支箭矢，且射击后可以接续快速移动。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660140",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660140",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_dian_b.ktx",
      "base": "ui/item_icon/icon_jin_dian_b",
      "ext": ".ktx",
      "pack": "0181.gpk",
      "row": 4174,
      "fid": "FAA6E15B55CFDCD1",
      "gpk_loc0_offset": 187184796,
      "pkgidx": 13,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_dian_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660144",
   "item_id": 660144,
   "name": "电极效应",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "突击步枪",
   "skill_desc": "突击步枪会以每秒40%的速度充入电能。电能会在「射击」后0.5秒内暂停回复，随后1.5秒内以每秒18%的速度缓慢恢复，随后进入快速回复状态。#f(5)「换弹」或使用「配件技能」后电能会立刻快速回复#n。#r具有电能时，「射击」消耗5%电能。消耗电能的「射击」命中时，#f(5)有45%概率触发【电震射击】（视为「射击」，消耗子弹，但不消耗电能），造成{0}伤害#n。#r不消耗电能的「射击」，触发【电震射击】的概率降低为8%。#r【电震射击】会按不消耗电能的概率触发【电震射击】，但最多触发1次。",
   "rank_star_segments": {
    "12": "【电震射击】附加(5)1秒「麻痹」效果（内置冷却12秒）。对「麻痹」效果中的目标，消耗电能的射击触发【电震射击】的概率提升至60%。",
    "9": "使用「配件技能」后立即回复50%电能，且视为触发一次「换弹」。",
    "5": "【电震射击】(5)有20%概率「视为命中弱点」（对非玩家为100%），且(5)对50%生命值以下的目标伤害提升30%。"
   },
   "icon": "ui/item_icon/icon_jin_dian",
   "desc": "特级异变核芯，装配后持续充入电能，射击消耗电能触发额外电震射击。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660144",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660144",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_dian_b.ktx",
      "base": "ui/item_icon/icon_jin_dian_b",
      "ext": ".ktx",
      "pack": "0181.gpk",
      "row": 4174,
      "fid": "FAA6E15B55CFDCD1",
      "gpk_loc0_offset": 187184796,
      "pkgidx": 13,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_dian_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  },
  {
   "id": "s12_660146",
   "item_id": 660146,
   "name": "鸣闪火花",
   "grade_label": "极品（12 星）",
   "grade_name": "极品",
   "grade_color": "金",
   "max_star": 12,
   "weapon_type": "霰弹枪",
   "skill_desc": "霰弹枪在弹片「命中」目标时，会为目标附加#f(5)持续5秒的【火花】效果#n。【火花】效果初始为1级，每#f(5)「命中」20发弹片会使【火花】效果升级#n，至多5级。#r目标存在【火花】效果时，基于火花的等级，#f(5)每0.4~0.11秒（随火花等级缩短）造成{0}的「持续伤害」（基准值取所有弹片对该目标造成的平均伤害）#n。#r弹片命中存在满级【火花】的目标后，下次射击会#f(5)额外追加一发【爆焰弹】#n。【爆焰弹】的弹片数量为射击的25%，单个弹片伤害为射击的100%。#r追加【爆焰弹】的射击命中目标时，【爆焰弹】必定命中目标。",
   "rank_star_segments": {
    "12": "击败目标时下3次射击(5)基础射速提升66%，且叠加火花效率翻倍。",
    "9": "火花累积造成25次伤害后会(5)提升自身3%射速，至多可叠加6层。10秒未叠加时效果消失。",
    "5": "火花爆炸时，有5%~25%的概率（随火花等级提升）(5)使该次火花爆炸伤害提升100%。"
   },
   "icon": "ui/item_icon/icon_jin_huo",
   "desc": "特级异变核芯，装配后霰弹枪射击附加火花持续造成伤害，火花叠满后射击追加爆焰弹。",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config"
   ],
   "source": "mutation_core_full / common_item 660xxx",
   "provenance": {
    "source_id": "documents-py314-current",
    "source_lock_sha256": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
    "table": "com\\cdata\\common_item_data.py",
    "row_key": "mcore_660146",
    "field_refs": [
     "name",
     "desc",
     "icon"
    ],
    "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
    "gift_link": "gift_data.name 去掉「（禁交易）」后与本体 name 精确相等（不做整数 join）",
    "card_link": "nucleus_cards.name == common_item.name（同名关联，card_item_id 单列保存）",
    "upstream": {
     "package_sha256": "4ba3e18d98558f44162cbfe545f8b006588505a93bae4e305fcf18c2bb1c8539",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "common_item 660xxx"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "com\\cdata\\common_item_data.py",
       "row_key": "mcore_660146",
       "field_refs": [
        "name",
        "desc",
        "icon"
       ]
      }
     ]
    },
    "table_fixed_from": "oversea\\common_item_data_auto_oversea_data_kj1.py",
    "row_key_kind": "synthetic",
    "row_key_note": "板侧合成 id；真实行身份用 item_id 回查",
    "table_raw": "com\\cdata\\common_item_data.py"
   },
   "_media": {
    "total": 1,
    "images": [
     {
      "file": "ui/item_icon/icon_jin_huo_b.ktx",
      "base": "ui/item_icon/icon_jin_huo_b",
      "ext": ".ktx",
      "pack": "0181.gpk",
      "row": 4175,
      "fid": "A33EE5A1B62F478B",
      "gpk_loc0_offset": 187195160,
      "pkgidx": 13,
      "gpk_loc0": true,
      "suffix": "_b",
      "kind": "品级×属性",
      "png": "assets/core_icons/item_icon_jin_huo_b.png",
      "px": [
       300,
       150
      ],
      "source": "表内字段路径 → .ktx fid → pe_file_index/gpk_loc0 精确命中 → pe_packs 解码 RGBA",
      "label": "品级图·大"
     }
    ],
    "note": "item = 表内 icon 字段的「品级×属性」图标（16 种，被同名/同属性核芯共用）；skill = 核芯卡 skill_icon（每核芯一张，48×48）",
    "slimmed": true
   }
  }
 ]
};
