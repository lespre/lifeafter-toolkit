window.WIKI_BOARD_damage_defense = {
 "meta": {
  "name": "4、守方侧",
  "category": "二、战力类 / 2、伤害计算",
  "generated": "2026-11-04",
  "evidence": "structure",
  "source_server": "PE 测试服 · special_hurt_params_data / _kj1 / _yk / hurt_params_data（b_class、c_class 列）",
  "package_sha": "5e79176cb6136bd38b1cc0ad42914d0b90202ee4d5a9e966bf5c7eb56a5a7ae6",
  "card_mode": "roster",
  "id_label": "服型",
  "filters": [],
  "card_summary": [
   [
    "服型",
    "服型"
   ],
   [
    "结论",
    "结论"
   ]
  ],
  "hide_media": true,
  "notes": "守方侧是独立一段：目标自身增伤/减伤桶先乘成 t，d=t−1 过 b_class 后 snapshot 乘 (1+d)，再叠额外伤害，最后按目标最大 HP 百分比夹取并向上取整。三服的 b_class / c_class 逐值相同 —— 换服不会改变这一段，差异只可能来自玩家身上的桶本身。",
  "provenance": {
   "contract_version": 3,
   "audit_status": "passed",
   "contract": "frozen-audited-artifact",
   "source_scope": {
    "cross_source_policy": "no-cross-source-field-join",
    "integer_join_policy": "no-equal-integer-join",
    "runtime_final_policy": "unknown-unless-runtime-proven"
   },
   "source_locks": [
    {
     "source_id": "pe-script-hurtcalc",
     "role": "primary",
     "sha256": "62e10e5ed1e6759089750d4cc0e865c36a1ee22a420ba198b127566171e396ce",
     "bytes": 249746676,
     "mtime_ns": 1793370321325025700,
     "path": "E:\\la拆包项目\\01_索引与产物\\源包\\pe_hotfix\\20261030_2225\\script.py314.lc.npk",
     "desc": "PE 体验服脚本包（HurtCalc 反汇编来源）"
    },
    {
     "source_id": "pe-table-special-hurt-params",
     "role": "comparison",
     "sha256": "e97345ae662542fb21c94f500e558be6ad508d5db91aab510b2f1e55ad2e2cea",
     "bytes": 91326,
     "mtime_ns": 1792520582367349000,
     "path": "E:\\la拆包项目\\01_索引与产物\\41_还原树\\pe\\配置\\com\\cdata\\special_hurt_params_data.py",
     "desc": "special_hurt_params_data（经典服分场景伤害参数）"
    },
    {
     "source_id": "pe-table-hurt-params-global",
     "role": "comparison",
     "sha256": "7adfc76402696ad52e7a52279638373b848c61bd3cc2e021dba35e6c7011cffa",
     "bytes": 1667,
     "mtime_ns": 1792856006984819700,
     "path": "E:\\la拆包项目\\01_索引与产物\\41_还原树\\pe\\配置\\com\\cdata\\hurt_params_data.nxs",
     "desc": "hurt_params_data 全局默认（本树仅存 .nxs 体）"
    }
   ],
   "note": "溯源由 fill_damage_provenance.py 依条目自述来源补齐；结论本身由伤害系统那条线产出"
  },
  "state_summary": {
   "经典服": 1,
   "简单生存服": 1,
   "月卡服": 1
  },
  "formula": [
   {
    "t": "① 目标自身桶合成",
    "e": "t = ∏(1 + 目标增伤桶) × ∏(1 − 目标减伤桶)",
    "n": "这里的「目标减伤桶」属于守方自身属性，与加成环节的 player_hurt_reduction_rate 是两条不同的量。"
   },
   {
    "t": "② 过 b_class 折线",
    "e": "d = t − 1 ；d = k·d + b",
    "n": "b_class：(0,0.8) 1x+0｜(0.8,1.0) 0.6x+0.32｜(1.0,∞) 0.1x+0.82。三服逐值相同。"
   },
   {
    "t": "③ 作用到本次伤害",
    "e": "damage ← damage × (1 + d) + 额外伤害",
    "n": "额外伤害在乘算之后加，不受桶影响。"
   },
   {
    "t": "④ 上限与取整",
    "e": "damage = ceil(min(damage, 目标最大HP × c_class 上限))",
    "n": "c_class：(0,1.0) 1x+0｜(1.0,1.2) 0.6x+0.4｜(1.2,∞) 0.1x+1.0。"
   }
  ],
  "category_before": "二、战力类 / 4、守方侧"
 },
 "items": [
  {
   "id": "df01",
   "name": "经典服",
   "服型": "经典服",
   "server_type": "经典服",
   "结论": "b_class / c_class 与其他两服逐值相同；守方侧不是差异来源。",
   "算法": "t = ∏(1+目标增伤桶) × ∏(1−目标减伤桶) → d = t−1 → d = _apply_rate_factor(d, b_class) → snapshot ×= (1+d) → +额外伤害 → min(HP 百分比上限) → ceil",
   "数值": "b_class：(0,0.8,1,0)(0.8,1.0,0.6,0.32)(1.0,∞,0.1,0.82)；c_class：(0,1.0,1,0)(1.0,1.2,0.6,0.4)(1.2,∞,0.1,1.0)",
   "说明": "注意区分：加成环节里的「守方减免」是 player_hurt_reduction_rate（配对项，直接减 rate）；这里的「目标减伤桶」属于目标自身属性，乘成 t 后过 b_class，两条不同的量。",
   "依据": "_calc_target_hp_change byte 456-4234、4804 起；apply_target @3238",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "HurtCalc 反汇编 + b_class / c_class 列",
   "status_tags": [
    "static config"
   ],
   "provenance": {
    "source_id": "pe-table-special-hurt-params",
    "table": "special_hurt_params_data",
    "row_key": "table-wide",
    "field_refs": [
     "source_hurt_*",
     "p2p_*",
     "hurt_calc:byte456-4234"
    ],
    "name_source": "伤害系统自研结论（另一条线），本脚本只补溯源不改编排",
    "note": "代码依据 hurt_calc byte 456-4234",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-table-special-hurt-params",
       "table": "special_hurt_params_data",
       "row_key": "table-wide",
       "field_refs": [
        "source_hurt_*",
        "p2p_*",
        "hurt_calc:byte456-4234"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "e97345ae662542fb21c94f500e558be6ad508d5db91aab510b2f1e55ad2e2cea",
    "upstream": {
     "package_sha256": "62e10e5ed1e6759089750d4cc0e865c36a1ee22a420ba198b127566171e396ce",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "df02",
   "name": "简单生存服",
   "服型": "简单生存服",
   "server_type": "简单生存服",
   "结论": "与经典服逐值相同。",
   "算法": "同上；b_class 作用在 d=t−1 上，作用完再加 1",
   "数值": "b_class：(0,0.8,1,0)(0.8,1.0,0.6,0.32)(1.0,∞,0.1,0.82)；c_class：(0,1.0,1,0)(1.0,1.2,0.6,0.4)(1.2,∞,0.1,1.0)",
   "说明": "两服在夏尔镇 6 与 304/305 上逐值核过，无一处不同。",
   "依据": "同上；_kj1 b_class / c_class 列",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "HurtCalc 反汇编 + _kj1",
   "status_tags": [
    "static config"
   ],
   "provenance": {
    "source_id": "pe-table-special-hurt-params",
    "table": "special_hurt_params_data",
    "row_key": "table-wide",
    "field_refs": [
     "source_hurt_*"
    ],
    "name_source": "伤害系统自研结论（另一条线），本脚本只补溯源不改编排",
    "note": "代码依据 HurtCalc 反汇编",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-table-special-hurt-params",
       "table": "special_hurt_params_data",
       "row_key": "table-wide",
       "field_refs": [
        "source_hurt_*"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "e97345ae662542fb21c94f500e558be6ad508d5db91aab510b2f1e55ad2e2cea",
    "upstream": {
     "package_sha256": "62e10e5ed1e6759089750d4cc0e865c36a1ee22a420ba198b127566171e396ce",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "df03",
   "name": "月卡服",
   "服型": "月卡服",
   "server_type": "月卡服",
   "结论": "与另外两服逐值相同（取自全局默认行的 b_class / c_class）。",
   "算法": "同上",
   "数值": "b_class：(0,0.8,1,0)(0.8,1.0,0.6,0.32)(1.0,∞,0.1,0.82)；c_class：(0,1.0,1,0)(1.0,1.2,0.6,0.4)(1.2,∞,0.1,1.0)",
   "说明": "月卡在本场景无专属行，但 b_class / c_class 取到的仍是同一组值，所以守方侧结论不变。",
   "依据": "同上；hurt_params_data b_class / c_class 列",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "HurtCalc 反汇编 + hurt_params_data",
   "status_tags": [
    "static config"
   ],
   "provenance": {
    "source_id": "pe-table-special-hurt-params",
    "table": "special_hurt_params_data",
    "row_key": "table-wide",
    "field_refs": [
     "source_hurt_*"
    ],
    "name_source": "伤害系统自研结论（另一条线），本脚本只补溯源不改编排",
    "note": "代码依据 HurtCalc 反汇编",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-table-special-hurt-params",
       "table": "special_hurt_params_data",
       "row_key": "table-wide",
       "field_refs": [
        "source_hurt_*"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "e97345ae662542fb21c94f500e558be6ad508d5db91aab510b2f1e55ad2e2cea",
    "upstream": {
     "package_sha256": "62e10e5ed1e6759089750d4cc0e865c36a1ee22a420ba198b127566171e396ce",
     "entry_index": null,
     "file_id": null
    }
   }
  }
 ]
};
