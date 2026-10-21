window.WIKI_BOARD_skin_behavior_preview = {
 "meta": {
  "name": "武器皮肤 · 未上线预告（已配名未上架 + 仅行为资源）",
  "category": "零、新更新与预告专栏（游戏未上线资源预告） / （1）武器皮肤 · 未上线预告",
  "source_server": "体验服 Documents BA8A 当前快照（root 仅版本对照）",
  "package_sha": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
  "generated": "2026-09-24",
  "evidence": "structure",
  "notes": "预告口径（两族，均自冻结源板行深拷贝，未重新解码）：①已配正式名未上架=皮肤行 sale_ts 晚于包快照日（快照时尚未到）；②仅行为资源=有 behavior_res 行但无父项/无道具行/无名称。均不表示上线、价格、概率或可得。",
  "provenance": {
   "contract_version": 3,
   "audit_status": "passed",
   "contract": "frozen-audited-artifact",
   "source_locks": [
    {
     "source_id": "weapon-skin-behavior-preview-adapter",
     "sha256": "eb14bca9542cc63eeeb16be61e344f5788ee312c104bb1c5bc028be0edae24ec",
     "role": "primary",
     "bytes": 0,
     "mtime_ns": 0
    }
   ],
   "source_scope": {
    "cross_source_policy": "no-cross-source-field-join",
    "integer_join_policy": "no-equal-integer-join",
    "runtime_final_policy": "unknown-unless-runtime-proven"
   }
  },
  "state_summary": {
   "unresolved": 6,
   "static config": 6,
   "verified": 0,
   "runtime final unknown": 6
  }
 },
 "items": [
  {
   "id": "1110185",
   "skin_id": 1110185,
   "catalog_layer": "current_parent",
   "name": "奇迹",
   "official_name_status": "verified",
   "name_status": "verified",
   "name_display": "奇迹",
   "official_desc": "六翼展、金焰引，一箭落定末世审判。「明日之后×斩神」联动限定外观。",
   "name_resolution": {
    "state": "verified",
    "name": "奇迹",
    "normalized_roots": [],
    "named_sfx_row_count": 0,
    "rule": "Current display name comes from the same-snapshot BA8 common_item_data_base row key==skin_id, field=name, with replayable CHS field/value slots. SFX text is never a name source."
   },
   "sfx_consensus_state": "insufficient_sfx_names",
   "version_status": "BA8 新增（相对 root 对照）",
   "model_path": "weapon/skin/skin_1007_011/skin_1007_011a/skin_1007_011a.gim",
   "field_provenance": {
    "aim_cross_functions": {
     "field_chs_slot": 23,
     "value_chs_slot": null,
     "scalar_type": "0x0b",
     "text": null
    },
    "extension_defeat_functions": {
     "field_chs_slot": 21,
     "value_chs_slot": null,
     "scalar_type": "0x0b",
     "text": null
    },
    "fire_sfx_path": {
     "field_chs_slot": 15,
     "value_chs_slot": 51,
     "scalar_type": "0x05",
     "text": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_kh_jc.sfx"
    },
    "hit_sfx_functions": {
     "field_chs_slot": 13,
     "value_chs_slot": null,
     "scalar_type": "0x0b",
     "text": null
    },
    "hold_functions": {
     "field_chs_slot": 34,
     "value_chs_slot": null,
     "scalar_type": "0x0b",
     "text": null
    },
    "jump_word_functions": {
     "field_chs_slot": 20,
     "value_chs_slot": null,
     "scalar_type": "0x0b",
     "text": null
    },
    "play_anim_moudle": {
     "field_chs_slot": 25,
     "value_chs_slot": null,
     "scalar_type": "0x0b",
     "text": null
    },
    "sale_ts": {
     "field_chs_slot": 11,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "skin_bullet_model_path": {
     "field_chs_slot": 27,
     "value_chs_slot": 77,
     "scalar_type": "0x05",
     "text": "weapon/skin/skin_1007_011/skin_1007_011a/skin_1007_011a_s01.gim"
    },
    "soft_bone_ids": {
     "field_chs_slot": 30,
     "value_chs_slot": null,
     "scalar_type": "0x0b",
     "text": null
    },
    "soft_bone_model_names": {
     "field_chs_slot": 31,
     "value_chs_slot": null,
     "scalar_type": "0x0b",
     "text": null
    },
    "soft_bone_socket_names": {
     "field_chs_slot": 32,
     "value_chs_slot": null,
     "scalar_type": "0x0b",
     "text": null
    },
    "sound_functions": {
     "field_chs_slot": 17,
     "value_chs_slot": null,
     "scalar_type": "0x0b",
     "text": null
    },
    "special_preview_model_path": {
     "field_chs_slot": 28,
     "value_chs_slot": 76,
     "scalar_type": "0x05",
     "text": "weapon/skin/skin_1007_011/skin_1007_011a/skin_1007_011a_preview.gim"
    },
    "trace_functions": {
     "field_chs_slot": 14,
     "value_chs_slot": null,
     "scalar_type": "0x0b",
     "text": null
    },
    "v2_soft_bone_ids": {
     "field_chs_slot": 33,
     "value_chs_slot": null,
     "scalar_type": "0x0b",
     "text": null
    },
    "yk_accessory_model_line_id": {
     "field_chs_slot": 12,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "camera_conf_id": {
     "field_chs_slot": 0,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "camera_conf_id_2": {
     "field_chs_slot": 1,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "charm_value": {
     "field_chs_slot": 2,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "jump_param": {
     "field_chs_slot": 3,
     "value_chs_slot": null,
     "scalar_type": "0x0b",
     "text": null
    },
    "level": {
     "field_chs_slot": 4,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "model_extra_position_offset": {
     "field_chs_slot": 5,
     "value_chs_slot": null,
     "scalar_type": "0x0b",
     "text": null
    },
    "model_extra_scale": {
     "field_chs_slot": 6,
     "value_chs_slot": null,
     "scalar_type": "0x22",
     "text": null
    },
    "model_path": {
     "field_chs_slot": 7,
     "value_chs_slot": 75,
     "scalar_type": "0x05",
     "text": "weapon/skin/skin_1007_011/skin_1007_011a/skin_1007_011a.gim"
    },
    "obtain_limit": {
     "field_chs_slot": 8,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "priority": {
     "field_chs_slot": 9,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "weapon_type": {
     "field_chs_slot": 10,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    }
   },
   "level": 5,
   "grade": "5典藏级",
   "sale_ts": 1790697600,
   "sale_date": "2026-09-29",
   "release_state": "upcoming",
   "weapon_type": 3,
   "weapon_type_label": "弓箭（3）",
   "weapon_type_state": "snapshot_field",
   "sfx_item_count": 8,
   "named_sfx_item_count": 1,
   "variant_item_count": 1,
   "behavior_resources": [
    {
     "field": "extension_defeat_sfx",
     "path": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_jisha.sfx",
     "text_provenance": {
      "field_chs_slot": 7,
      "value_chs_slot": 281,
      "scalar_type": "0x05",
      "text": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_jisha.sfx"
     },
     "kind": "sfx_path"
    },
    {
     "field": "fire_sfx_path",
     "path": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_kh_jc.sfx",
     "text_provenance": {
      "field_chs_slot": 0,
      "value_chs_slot": 282,
      "scalar_type": "0x05",
      "text": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_kh_jc.sfx"
     },
     "kind": "sfx_path"
    },
    {
     "field": "hit_sfx_path",
     "path": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_sj_jc.sfx",
     "text_provenance": {
      "field_chs_slot": 1,
      "value_chs_slot": 283,
      "scalar_type": "0x05",
      "text": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_sj_jc.sfx"
     },
     "kind": "sfx_path"
    },
    {
     "field": "hold_sfx_loop_path",
     "path": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_xuli.sfx",
     "text_provenance": {
      "field_chs_slot": 14,
      "value_chs_slot": 284,
      "scalar_type": "0x05",
      "text": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_xuli.sfx"
     },
     "kind": "sfx_path"
    },
    {
     "field": "hold_sfx_path",
     "path": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_xuli01_jc.sfx",
     "text_provenance": {
      "field_chs_slot": 10,
      "value_chs_slot": 285,
      "scalar_type": "0x05",
      "text": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_xuli01_jc.sfx"
     },
     "kind": "sfx_path"
    },
    {
     "field": "trajectory_path_real",
     "path": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_dd.sfx",
     "text_provenance": {
      "field_chs_slot": 3,
      "value_chs_slot": 98,
      "scalar_type": "0x05",
      "text": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_dd.sfx"
     },
     "kind": "sfx_path"
    },
    {
     "field": "trajectory_sfx_path",
     "path": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_dd.sfx",
     "text_provenance": {
      "field_chs_slot": 2,
      "value_chs_slot": 98,
      "scalar_type": "0x05",
      "text": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_dd.sfx"
     },
     "kind": "sfx_path"
    },
    {
     "field": "trajectory_sfx_path_nor",
     "path": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_dd_lx.sfx",
     "text_provenance": {
      "field_chs_slot": 4,
      "value_chs_slot": 278,
      "scalar_type": "0x05",
      "text": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_dd_lx.sfx"
     },
     "kind": "sfx_path"
    }
   ],
   "sfx_items": [
    {
     "id": "1120365",
     "row_key": 1120365,
     "display_name": "奇迹-命中",
     "sfx_name": null,
     "item_name": "奇迹-命中",
     "item_name_provenance": {
      "name": {
       "field_chs_slot": 4,
       "value_chs_slot": 31418,
       "scalar_type": "0x05",
       "text": "奇迹-命中"
      }
     },
     "sfx_type": 3,
     "sfx_type_label": "命中特效（3）",
     "sfx_params": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_sj_jc.sfx",
     "inline_groups": [],
     "raw_fields": {
      "sfx_params": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_sj_jc.sfx",
      "level": 5,
      "sfx_type": 3,
      "skin_id": 1110185
     },
     "evidence": "structure",
     "evidence_level": "structure-only",
     "source": "Current same-snapshot SFX configuration child; display text from same-key common_item_data_base 1120xxx item name when present; not activity, availability, price, probability, or combat-effect proof.",
     "text_provenance": {},
     "provenance": {
      "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
      "source_entries": [
       {
        "entry_index": 21883,
        "file_id": "B693DB548E5412B6",
        "decoded_sha256": "983b9f0b1652d2e198b54cf507a7c42d58965afedfba79ab3eeaeb2477634b13",
        "role": "weapon_skin_sfx_base"
       },
       {
        "entry_index": 11040,
        "file_id": "5C56D035B329BEBB",
        "decoded_sha256": "65040b06c143529d9a95352ab06bc01fe4abc64e85d58a3eba86240282779450",
        "role": "weapon_skin_sfx_chs"
       }
      ],
      "table": "weapon_skin_sfx_function_data (+ same-key common_item_data_base item name)",
      "row_key": 1120365,
      "field_refs": [
       "weapon_skin_sfx_function_data.key=1120365",
       "weapon_skin_sfx_function_data.skin_id=1110185",
       "common_item_data_base.key=1120365",
       "common_item_data_base.name",
       "common_item_data_base.name CHS field_slot=4 value_slot=31418"
      ],
      "name_source": "same-snapshot common_item_data_base row key==sfx row key name CHS replay"
     }
    },
    {
     "id": "1120366",
     "row_key": 1120366,
     "display_name": "奇迹-击杀",
     "sfx_name": null,
     "item_name": "奇迹-击杀",
     "item_name_provenance": {
      "name": {
       "field_chs_slot": 4,
       "value_chs_slot": 31416,
       "scalar_type": "0x05",
       "text": "奇迹-击杀"
      }
     },
     "sfx_type": 4,
     "sfx_type_label": "击败特效（4）",
     "sfx_params": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_jisha.sfx",
     "inline_groups": [],
     "raw_fields": {
      "defeat_args": "jump:122",
      "sfx_params": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_jisha.sfx",
      "unlock_items": "jump:96",
      "level": 5,
      "sfx_type": 4,
      "skin_id": 1110185
     },
     "evidence": "structure",
     "evidence_level": "structure-only",
     "source": "Current same-snapshot SFX configuration child; display text from same-key common_item_data_base 1120xxx item name when present; not activity, availability, price, probability, or combat-effect proof.",
     "text_provenance": {},
     "provenance": {
      "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
      "source_entries": [
       {
        "entry_index": 21883,
        "file_id": "B693DB548E5412B6",
        "decoded_sha256": "983b9f0b1652d2e198b54cf507a7c42d58965afedfba79ab3eeaeb2477634b13",
        "role": "weapon_skin_sfx_base"
       },
       {
        "entry_index": 11040,
        "file_id": "5C56D035B329BEBB",
        "decoded_sha256": "65040b06c143529d9a95352ab06bc01fe4abc64e85d58a3eba86240282779450",
        "role": "weapon_skin_sfx_chs"
       }
      ],
      "table": "weapon_skin_sfx_function_data (+ same-key common_item_data_base item name)",
      "row_key": 1120366,
      "field_refs": [
       "weapon_skin_sfx_function_data.key=1120366",
       "weapon_skin_sfx_function_data.skin_id=1110185",
       "common_item_data_base.key=1120366",
       "common_item_data_base.name",
       "common_item_data_base.name CHS field_slot=4 value_slot=31416"
      ],
      "name_source": "same-snapshot common_item_data_base row key==sfx row key name CHS replay"
     }
    },
    {
     "id": "1120367",
     "row_key": 1120367,
     "display_name": "奇迹-跳字",
     "sfx_name": null,
     "item_name": "奇迹-跳字",
     "item_name_provenance": {
      "name": {
       "field_chs_slot": 4,
       "value_chs_slot": 31421,
       "scalar_type": "0x05",
       "text": "奇迹-跳字"
      }
     },
     "sfx_type": 10,
     "sfx_type_label": "伤害跳字（10）",
     "sfx_params": null,
     "inline_groups": [
      {
       "kind": "0x01",
       "count": 2,
       "elements": [
        321890,
        60
       ]
      },
      {
       "kind": "0x01",
       "count": 2,
       "elements": [
        24574,
        15
       ]
      },
      {
       "kind": "0x01",
       "count": 2,
       "elements": [
        24575,
        5
       ]
      },
      {
       "kind": "0x0b",
       "count": 2,
       "elements": [
        "jump:103",
        "jump:110"
       ]
      },
      {
       "kind": "0x07",
       "count": 4,
       "elements": [
        {
         "type": "0x22",
         "value": 0.2
        },
        {
         "type": "0x0b",
         "value": "jump:117"
        },
        {
         "type": "0x01",
         "value": 10
        },
        {
         "type": "0x05",
         "value": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_dm_01.sfx",
         "value_chs_slot": 152
        }
       ]
      }
     ],
     "raw_fields": {
      "level": 5,
      "sfx_type": 10,
      "skin_id": 1110185
     },
     "evidence": "structure",
     "evidence_level": "structure-only",
     "source": "Current same-snapshot SFX configuration child; display text from same-key common_item_data_base 1120xxx item name when present; not activity, availability, price, probability, or combat-effect proof.",
     "text_provenance": {},
     "provenance": {
      "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
      "source_entries": [
       {
        "entry_index": 21883,
        "file_id": "B693DB548E5412B6",
        "decoded_sha256": "983b9f0b1652d2e198b54cf507a7c42d58965afedfba79ab3eeaeb2477634b13",
        "role": "weapon_skin_sfx_base"
       },
       {
        "entry_index": 11040,
        "file_id": "5C56D035B329BEBB",
        "decoded_sha256": "65040b06c143529d9a95352ab06bc01fe4abc64e85d58a3eba86240282779450",
        "role": "weapon_skin_sfx_chs"
       }
      ],
      "table": "weapon_skin_sfx_function_data (+ same-key common_item_data_base item name)",
      "row_key": 1120367,
      "field_refs": [
       "weapon_skin_sfx_function_data.key=1120367",
       "weapon_skin_sfx_function_data.skin_id=1110185",
       "common_item_data_base.key=1120367",
       "common_item_data_base.name",
       "common_item_data_base.name CHS field_slot=4 value_slot=31421"
      ],
      "name_source": "same-snapshot common_item_data_base row key==sfx row key name CHS replay"
     }
    },
    {
     "id": "1120368",
     "row_key": 1120368,
     "display_name": "奇迹-弹道",
     "sfx_name": "真实",
     "item_name": "奇迹-弹道",
     "item_name_provenance": {
      "name": {
       "field_chs_slot": 4,
       "value_chs_slot": 31419,
       "scalar_type": "0x05",
       "text": "奇迹-弹道"
      }
     },
     "sfx_type": 6,
     "sfx_type_label": "攻击弹道（6）",
     "sfx_params": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_dd_jc.sfx",
     "inline_groups": [],
     "raw_fields": {
      "sfx_name": "真实",
      "sfx_params": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_dd_jc.sfx",
      "level": 5,
      "sfx_type": 6,
      "skin_id": 1110185
     },
     "evidence": "structure",
     "evidence_level": "structure-only",
     "source": "Current same-snapshot SFX configuration child; display text from same-key common_item_data_base 1120xxx item name when present; not activity, availability, price, probability, or combat-effect proof.",
     "text_provenance": {
      "sfx_name": {
       "field_chs_slot": 7,
       "value_chs_slot": 271,
       "scalar_type": "0x05",
       "text": "真实"
      }
     },
     "provenance": {
      "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
      "source_entries": [
       {
        "entry_index": 21883,
        "file_id": "B693DB548E5412B6",
        "decoded_sha256": "983b9f0b1652d2e198b54cf507a7c42d58965afedfba79ab3eeaeb2477634b13",
        "role": "weapon_skin_sfx_base"
       },
       {
        "entry_index": 11040,
        "file_id": "5C56D035B329BEBB",
        "decoded_sha256": "65040b06c143529d9a95352ab06bc01fe4abc64e85d58a3eba86240282779450",
        "role": "weapon_skin_sfx_chs"
       }
      ],
      "table": "weapon_skin_sfx_function_data (+ same-key common_item_data_base item name)",
      "row_key": 1120368,
      "field_refs": [
       "weapon_skin_sfx_function_data.key=1120368",
       "weapon_skin_sfx_function_data.skin_id=1110185",
       "weapon_skin_sfx_function_data.sfx_name",
       "weapon_skin_sfx_function_data.sfx_name CHS field_slot=7 value_slot=271",
       "common_item_data_base.key=1120368",
       "common_item_data_base.name",
       "common_item_data_base.name CHS field_slot=4 value_slot=31419"
      ],
      "name_source": "same-snapshot common_item_data_base row key==sfx row key name CHS replay"
     }
    },
    {
     "id": "1120369",
     "row_key": 1120369,
     "display_name": "奇迹-音效",
     "sfx_name": null,
     "item_name": "奇迹-音效",
     "item_name_provenance": {
      "name": {
       "field_chs_slot": 4,
       "value_chs_slot": 31422,
       "scalar_type": "0x05",
       "text": "奇迹-音效"
      }
     },
     "sfx_type": 7,
     "sfx_type_label": "战斗音效（7）",
     "sfx_params": null,
     "inline_groups": [],
     "raw_fields": {
      "level": 5,
      "sfx_type": 7,
      "skin_id": 1110185
     },
     "evidence": "structure",
     "evidence_level": "structure-only",
     "source": "Current same-snapshot SFX configuration child; display text from same-key common_item_data_base 1120xxx item name when present; not activity, availability, price, probability, or combat-effect proof.",
     "text_provenance": {},
     "provenance": {
      "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
      "source_entries": [
       {
        "entry_index": 21883,
        "file_id": "B693DB548E5412B6",
        "decoded_sha256": "983b9f0b1652d2e198b54cf507a7c42d58965afedfba79ab3eeaeb2477634b13",
        "role": "weapon_skin_sfx_base"
       },
       {
        "entry_index": 11040,
        "file_id": "5C56D035B329BEBB",
        "decoded_sha256": "65040b06c143529d9a95352ab06bc01fe4abc64e85d58a3eba86240282779450",
        "role": "weapon_skin_sfx_chs"
       }
      ],
      "table": "weapon_skin_sfx_function_data (+ same-key common_item_data_base item name)",
      "row_key": 1120369,
      "field_refs": [
       "weapon_skin_sfx_function_data.key=1120369",
       "weapon_skin_sfx_function_data.skin_id=1110185",
       "common_item_data_base.key=1120369",
       "common_item_data_base.name",
       "common_item_data_base.name CHS field_slot=4 value_slot=31422"
      ],
      "name_source": "same-snapshot common_item_data_base row key==sfx row key name CHS replay"
     }
    },
    {
     "id": "1120370",
     "row_key": 1120370,
     "display_name": "奇迹-准星",
     "sfx_name": null,
     "item_name": "奇迹-准星",
     "item_name_provenance": {
      "name": {
       "field_chs_slot": 4,
       "value_chs_slot": 31415,
       "scalar_type": "0x05",
       "text": "奇迹-准星"
      }
     },
     "sfx_type": 9,
     "sfx_type_label": "攻击准星（9）",
     "sfx_params": "jump:55",
     "inline_groups": [],
     "raw_fields": {
      "sfx_params": "jump:55",
      "level": 5,
      "sfx_type": 9,
      "skin_id": 1110185
     },
     "evidence": "structure",
     "evidence_level": "structure-only",
     "source": "Current same-snapshot SFX configuration child; display text from same-key common_item_data_base 1120xxx item name when present; not activity, availability, price, probability, or combat-effect proof.",
     "text_provenance": {},
     "provenance": {
      "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
      "source_entries": [
       {
        "entry_index": 21883,
        "file_id": "B693DB548E5412B6",
        "decoded_sha256": "983b9f0b1652d2e198b54cf507a7c42d58965afedfba79ab3eeaeb2477634b13",
        "role": "weapon_skin_sfx_base"
       },
       {
        "entry_index": 11040,
        "file_id": "5C56D035B329BEBB",
        "decoded_sha256": "65040b06c143529d9a95352ab06bc01fe4abc64e85d58a3eba86240282779450",
        "role": "weapon_skin_sfx_chs"
       }
      ],
      "table": "weapon_skin_sfx_function_data (+ same-key common_item_data_base item name)",
      "row_key": 1120370,
      "field_refs": [
       "weapon_skin_sfx_function_data.key=1120370",
       "weapon_skin_sfx_function_data.skin_id=1110185",
       "common_item_data_base.key=1120370",
       "common_item_data_base.name",
       "common_item_data_base.name CHS field_slot=4 value_slot=31415"
      ],
      "name_source": "same-snapshot common_item_data_base row key==sfx row key name CHS replay"
     }
    },
    {
     "id": "1120371",
     "row_key": 1120371,
     "display_name": "奇迹-蓄力",
     "sfx_name": null,
     "item_name": "奇迹-蓄力",
     "item_name_provenance": {
      "name": {
       "field_chs_slot": 4,
       "value_chs_slot": 31420,
       "scalar_type": "0x05",
       "text": "奇迹-蓄力"
      }
     },
     "sfx_type": 14,
     "sfx_type_label": "蓄力特效（14）",
     "sfx_params": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_xuli01_jc.sfx",
     "inline_groups": [
      {
       "kind": "0x01",
       "count": 1,
       "elements": [
        41
       ]
      }
     ],
     "raw_fields": {
      "sfx_params": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_xuli01_jc.sfx",
      "level": 5,
      "sfx_type": 14,
      "skin_id": 1110185
     },
     "evidence": "structure",
     "evidence_level": "structure-only",
     "source": "Current same-snapshot SFX configuration child; display text from same-key common_item_data_base 1120xxx item name when present; not activity, availability, price, probability, or combat-effect proof.",
     "text_provenance": {},
     "provenance": {
      "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
      "source_entries": [
       {
        "entry_index": 21883,
        "file_id": "B693DB548E5412B6",
        "decoded_sha256": "983b9f0b1652d2e198b54cf507a7c42d58965afedfba79ab3eeaeb2477634b13",
        "role": "weapon_skin_sfx_base"
       },
       {
        "entry_index": 11040,
        "file_id": "5C56D035B329BEBB",
        "decoded_sha256": "65040b06c143529d9a95352ab06bc01fe4abc64e85d58a3eba86240282779450",
        "role": "weapon_skin_sfx_chs"
       }
      ],
      "table": "weapon_skin_sfx_function_data (+ same-key common_item_data_base item name)",
      "row_key": 1120371,
      "field_refs": [
       "weapon_skin_sfx_function_data.key=1120371",
       "weapon_skin_sfx_function_data.skin_id=1110185",
       "common_item_data_base.key=1120371",
       "common_item_data_base.name",
       "common_item_data_base.name CHS field_slot=4 value_slot=31420"
      ],
      "name_source": "same-snapshot common_item_data_base row key==sfx row key name CHS replay"
     }
    },
    {
     "id": "1120372",
     "row_key": 1120372,
     "display_name": "奇迹-动作替换模组",
     "sfx_name": null,
     "item_name": "奇迹-动作替换模组",
     "item_name_provenance": {
      "name": {
       "field_chs_slot": 4,
       "value_chs_slot": 31417,
       "scalar_type": "0x05",
       "text": "奇迹-动作替换模组"
      }
     },
     "sfx_type": 15,
     "sfx_type_label": "专属战斗动作（15）",
     "sfx_params": "ChangeColor",
     "inline_groups": [],
     "raw_fields": {
      "sfx_params": "ChangeColor",
      "level": 5,
      "sfx_type": 15,
      "skin_id": 1110185
     },
     "evidence": "structure",
     "evidence_level": "structure-only",
     "source": "Current same-snapshot SFX configuration child; display text from same-key common_item_data_base 1120xxx item name when present; not activity, availability, price, probability, or combat-effect proof.",
     "text_provenance": {},
     "provenance": {
      "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
      "source_entries": [
       {
        "entry_index": 21883,
        "file_id": "B693DB548E5412B6",
        "decoded_sha256": "983b9f0b1652d2e198b54cf507a7c42d58965afedfba79ab3eeaeb2477634b13",
        "role": "weapon_skin_sfx_base"
       },
       {
        "entry_index": 11040,
        "file_id": "5C56D035B329BEBB",
        "decoded_sha256": "65040b06c143529d9a95352ab06bc01fe4abc64e85d58a3eba86240282779450",
        "role": "weapon_skin_sfx_chs"
       }
      ],
      "table": "weapon_skin_sfx_function_data (+ same-key common_item_data_base item name)",
      "row_key": 1120372,
      "field_refs": [
       "weapon_skin_sfx_function_data.key=1120372",
       "weapon_skin_sfx_function_data.skin_id=1110185",
       "common_item_data_base.key=1120372",
       "common_item_data_base.name",
       "common_item_data_base.name CHS field_slot=4 value_slot=31417"
      ],
      "name_source": "same-snapshot common_item_data_base row key==sfx row key name CHS replay"
     }
    }
   ],
   "variant_items": [
    {
     "id": "11101851",
     "skin_id": 11101851,
     "catalog_layer": "time_limit_variant",
     "main_skin_id": 1110185,
     "display_name": "奇迹（7天）",
     "name": "奇迹（7天）",
     "official_name_status": "verified",
     "name_status": "verified",
     "name_display": "奇迹（7天）",
     "official_desc": null,
     "name_resolution": {
      "state": "verified",
      "name": "奇迹（7天）",
      "rule": "same-snapshot common_item_data_base row name"
     },
     "sfx_consensus_state": "no_sfx_text",
     "version_status": "BA8 新增（相对 root 对照）",
     "model_path": "weapon/skin/skin_1007_011/skin_1007_011a/skin_1007_011a.gim",
     "level": 5,
     "grade": "5典藏级",
     "sale_ts": 1790697600,
     "sale_date": "2026-09-29",
     "release_state": "upcoming",
     "field_provenance": {
      "fire_sfx_path": {
       "field_chs_slot": 15,
       "value_chs_slot": 51,
       "scalar_type": "0x05",
       "text": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_kh_jc.sfx"
      },
      "hold_functions": {
       "field_chs_slot": 34,
       "value_chs_slot": null,
       "scalar_type": "0x0b",
       "text": null
      },
      "play_anim_moudle": {
       "field_chs_slot": 25,
       "value_chs_slot": null,
       "scalar_type": "0x0b",
       "text": null
      },
      "sale_ts": {
       "field_chs_slot": 11,
       "value_chs_slot": null,
       "scalar_type": "0x01",
       "text": null
      },
      "skin_bullet_model_path": {
       "field_chs_slot": 27,
       "value_chs_slot": 77,
       "scalar_type": "0x05",
       "text": "weapon/skin/skin_1007_011/skin_1007_011a/skin_1007_011a_s01.gim"
      },
      "soft_bone_ids": {
       "field_chs_slot": 30,
       "value_chs_slot": null,
       "scalar_type": "0x0b",
       "text": null
      },
      "soft_bone_model_names": {
       "field_chs_slot": 31,
       "value_chs_slot": null,
       "scalar_type": "0x0b",
       "text": null
      },
      "soft_bone_socket_names": {
       "field_chs_slot": 32,
       "value_chs_slot": null,
       "scalar_type": "0x0b",
       "text": null
      },
      "special_preview_model_path": {
       "field_chs_slot": 28,
       "value_chs_slot": 76,
       "scalar_type": "0x05",
       "text": "weapon/skin/skin_1007_011/skin_1007_011a/skin_1007_011a_preview.gim"
      },
      "v2_soft_bone_ids": {
       "field_chs_slot": 33,
       "value_chs_slot": null,
       "scalar_type": "0x0b",
       "text": null
      },
      "yk_accessory_model_line_id": {
       "field_chs_slot": 12,
       "value_chs_slot": null,
       "scalar_type": "0x01",
       "text": null
      },
      "camera_conf_id": {
       "field_chs_slot": 0,
       "value_chs_slot": null,
       "scalar_type": "0x01",
       "text": null
      },
      "camera_conf_id_2": {
       "field_chs_slot": 1,
       "value_chs_slot": null,
       "scalar_type": "0x01",
       "text": null
      },
      "charm_value": {
       "field_chs_slot": 2,
       "value_chs_slot": null,
       "scalar_type": "0x01",
       "text": null
      },
      "jump_param": {
       "field_chs_slot": 3,
       "value_chs_slot": null,
       "scalar_type": "0x0b",
       "text": null
      },
      "level": {
       "field_chs_slot": 4,
       "value_chs_slot": null,
       "scalar_type": "0x01",
       "text": null
      },
      "model_extra_position_offset": {
       "field_chs_slot": 5,
       "value_chs_slot": null,
       "scalar_type": "0x0b",
       "text": null
      },
      "model_extra_scale": {
       "field_chs_slot": 6,
       "value_chs_slot": null,
       "scalar_type": "0x22",
       "text": null
      },
      "model_path": {
       "field_chs_slot": 7,
       "value_chs_slot": 75,
       "scalar_type": "0x05",
       "text": "weapon/skin/skin_1007_011/skin_1007_011a/skin_1007_011a.gim"
      },
      "obtain_limit": {
       "field_chs_slot": 8,
       "value_chs_slot": null,
       "scalar_type": "0x01",
       "text": null
      },
      "priority": {
       "field_chs_slot": 9,
       "value_chs_slot": null,
       "scalar_type": "0x01",
       "text": null
      },
      "weapon_type": {
       "field_chs_slot": 10,
       "value_chs_slot": null,
       "scalar_type": "0x01",
       "text": null
      }
     },
     "weapon_type": 3,
     "weapon_type_label": "弓箭（3）",
     "weapon_type_state": "snapshot_field",
     "sfx_item_count": 0,
     "named_sfx_item_count": 0,
     "sfx_items": [],
     "reference_fields": {
      "source_kind": "no_user_reference_row",
      "source_path": "data/reference_inputs/weapon_skin_catalog_user_reference_v3_2.csv",
      "source_sha256": "827935d81e276c90559ae69401aed9a4e7cf7d75633a96f1ddc7277874998456",
      "row_key": 11101851,
      "name": "",
      "model_path": "",
      "version_status": "",
      "grade": "",
      "weapon_type": "",
      "description": "",
      "ip": "",
      "battle_action": "",
      "idle_action": "",
      "battle_effect_names": ""
     },
     "evidence": "structure",
     "evidence_level": "current-snapshot-verified",
     "source": "Current Documents BA8 weapon_skin_data time-limit variant row nested under its main skin; formal name from same-snapshot common_item_data_base when a row exists. Time-limit membership context is user real-machine knowledge.",
     "provenance": {
      "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
      "source_entries": [
       {
        "entry_index": 14250,
        "file_id": "765AB12F1D6EB0EA",
        "decoded_sha256": "5f0165ad7c7423be500532c35a4b3414b59967da93896b9c09918ba2d71cfbbe",
        "role": "weapon_skin_base"
       },
       {
        "entry_index": 25394,
        "file_id": "D35E3103168889D2",
        "decoded_sha256": "faf102d513b0900c476787bb41dc85f262ed923b9b5774ec881b5e0803caded1",
        "role": "weapon_skin_chs"
       },
       {
        "entry_index": 21883,
        "file_id": "B693DB548E5412B6",
        "decoded_sha256": "983b9f0b1652d2e198b54cf507a7c42d58965afedfba79ab3eeaeb2477634b13",
        "role": "weapon_skin_sfx_base"
       },
       {
        "entry_index": 11040,
        "file_id": "5C56D035B329BEBB",
        "decoded_sha256": "65040b06c143529d9a95352ab06bc01fe4abc64e85d58a3eba86240282779450",
        "role": "weapon_skin_sfx_chs"
       },
       {
        "entry_index": 49069,
        "file_id": "765AB12F1D6EB0EA",
        "decoded_sha256": "f26f931848b9b4264d47d3fe54143b26496acaaa165a55a6d25156a635a9e917",
        "role": "root_weapon_skin_base"
       },
       {
        "entry_index": 87558,
        "file_id": "D35E3103168889D2",
        "decoded_sha256": "fc7806c9f1200edf276ea776354aaadad853af4a9929bdacefe91702763dd24f",
        "role": "root_weapon_skin_chs"
       },
       {
        "entry_index": 21601,
        "file_id": "B42760CCA41DBC25",
        "decoded_sha256": "26fe910d01078b2b4c303bceff039ef9f42a0140d5bb90e1ca91f068286d86bd",
        "role": "common_item_base"
       },
       {
        "entry_index": 28668,
        "file_id": "EF3A8474A5E5F7A4",
        "decoded_sha256": "09c286b210c4e484cfc9a6b0d66bb38892575b614bedec518cc03d58b2bb90bb",
        "role": "common_item_chs"
       }
      ],
      "table": "weapon_skin_data + common_item_data_base (when present)",
      "row_key": 11101851,
      "field_refs": [
       "common_item_data_base.key=11101851",
       "common_item_data_base.name",
       "common_item_data_base.name CHS field_slot=4 value_slot=31423"
      ],
      "name_source": "same-snapshot BA8 common_item_data_base row key==11101851 field=name CHS field_slot=4 value_slot=31423",
      "member_sfx_row_keys": [],
      "business_chain": {
       "chain": "weapon_skin_data.key -> common_item_data_base.key (variant item row) -> name CHS replay",
       "item_row_key": 11101851,
       "proves": "same-snapshot formal item name exists for this time-limit variant id"
      },
      "root_comparison": {
       "source_lock_sha256": "0f824b35120f42e310a6f42e4ea20200d9465ad34c2e98f47c8ecaf9853b03b7",
       "comparison": "key-presence only; never used as current display-name source",
       "root_row_present": false
      }
     },
     "variant_type": "timed",
     "permanent_skin_id": 1110185,
     "variant_relation_state": "verified_runtime_rule",
     "variant_relation_target": "permanent_skin_id=1110185",
     "variant_relation_target_state": "resolved",
     "variant_relation_rule": "get_perm_skin_id(timed_id) = timed_id // 10（运行时代码证据）"
    }
   ],
   "reference_fields": {
    "source_kind": "no_user_reference_row",
    "source_path": "data/reference_inputs/weapon_skin_catalog_user_reference_v3_2.csv",
    "source_sha256": "827935d81e276c90559ae69401aed9a4e7cf7d75633a96f1ddc7277874998456",
    "row_key": 1110185,
    "name": "",
    "model_path": "",
    "version_status": "",
    "grade": "",
    "weapon_type": "",
    "description": "",
    "ip": "",
    "battle_action": "",
    "idle_action": "",
    "battle_effect_names": ""
   },
   "evidence": "structure",
   "evidence_level": "current-snapshot-verified",
   "source": "Current Documents BA8 weapon_skin_data parent; formal name/desc from same-snapshot common_item_data_base. Static table presence does not prove activity, availability, price, probability, or combat effect.",
   "provenance": {
    "source_lock_sha256": "eb14bca9542cc63eeeb16be61e344f5788ee312c104bb1c5bc028be0edae24ec",
    "source_entries": [
     {
      "entry_index": 14250,
      "file_id": "765AB12F1D6EB0EA",
      "decoded_sha256": "5f0165ad7c7423be500532c35a4b3414b59967da93896b9c09918ba2d71cfbbe",
      "role": "weapon_skin_base"
     },
     {
      "entry_index": 25394,
      "file_id": "D35E3103168889D2",
      "decoded_sha256": "faf102d513b0900c476787bb41dc85f262ed923b9b5774ec881b5e0803caded1",
      "role": "weapon_skin_chs"
     },
     {
      "entry_index": 21883,
      "file_id": "B693DB548E5412B6",
      "decoded_sha256": "983b9f0b1652d2e198b54cf507a7c42d58965afedfba79ab3eeaeb2477634b13",
      "role": "weapon_skin_sfx_base"
     },
     {
      "entry_index": 11040,
      "file_id": "5C56D035B329BEBB",
      "decoded_sha256": "65040b06c143529d9a95352ab06bc01fe4abc64e85d58a3eba86240282779450",
      "role": "weapon_skin_sfx_chs"
     },
     {
      "entry_index": 49069,
      "file_id": "765AB12F1D6EB0EA",
      "decoded_sha256": "f26f931848b9b4264d47d3fe54143b26496acaaa165a55a6d25156a635a9e917",
      "role": "root_weapon_skin_base"
     },
     {
      "entry_index": 87558,
      "file_id": "D35E3103168889D2",
      "decoded_sha256": "fc7806c9f1200edf276ea776354aaadad853af4a9929bdacefe91702763dd24f",
      "role": "root_weapon_skin_chs"
     },
     {
      "entry_index": 21601,
      "file_id": "B42760CCA41DBC25",
      "decoded_sha256": "26fe910d01078b2b4c303bceff039ef9f42a0140d5bb90e1ca91f068286d86bd",
      "role": "common_item_base"
     },
     {
      "entry_index": 28668,
      "file_id": "EF3A8474A5E5F7A4",
      "decoded_sha256": "09c286b210c4e484cfc9a6b0d66bb38892575b614bedec518cc03d58b2bb90bb",
      "role": "common_item_chs"
     }
    ],
    "table": "weapon_skin_data + common_item_data_base + weapon_skin_sfx_function_data; root weapon_skin_data comparison only",
    "row_key": 1110185,
    "field_refs": [
     "weapon_skin_data.key=1110185",
     "common_item_data_base.key=1110185",
     "common_item_data_base.name",
     "common_item_data_base.name CHS field_slot=4 value_slot=31414",
     "common_item_data_base.desc",
     "common_item_data_base.desc CHS field_slot=6 value_slot=9494",
     "weapon_skin_sfx_function_data.key=1120365",
     "weapon_skin_sfx_function_data.key=1120366",
     "weapon_skin_sfx_function_data.key=1120367",
     "weapon_skin_sfx_function_data.key=1120368",
     "weapon_skin_sfx_function_data.key=1120369",
     "weapon_skin_sfx_function_data.key=1120370",
     "weapon_skin_sfx_function_data.key=1120371",
     "weapon_skin_sfx_function_data.key=1120372",
     "weapon_skin_data.key=11101851",
     "weapon_skin_behavior_res_data.key=1110185",
     "weapon_skin_data.sale_ts (晚于快照日 → upcoming)",
     "common_item_data_base.key=skin_id (正式名)"
    ],
    "name_source": "same-snapshot common_item_data_base row (verified formal name); release not yet reached per skin row sale_ts",
    "member_sfx_row_keys": [
     1120365,
     1120366,
     1120367,
     1120368,
     1120369,
     1120370,
     1120371,
     1120372
    ],
    "member_variant_row_keys": [
     11101851
    ],
    "business_chain": {
     "chain": "weapon_skin_data.key -> common_item_data_base.key (item row) -> name/desc CHS replay",
     "item_row_key": 1110185,
     "proves": "same-snapshot formal item name exists for this skin id; not activity/availability proof"
    },
    "root_comparison": {
     "source_lock_sha256": "0f824b35120f42e310a6f42e4ea20200d9465ad34c2e98f47c8ecaf9853b03b7",
     "comparison": "key-presence only; never used as current display-name source",
     "root_row_present": false
    },
    "source_id": "weapon-skin-behavior-preview-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 14250,
     "file_id": "765AB12F1D6EB0EA",
     "decoded_sha256": "5f0165ad7c7423be500532c35a4b3414b59967da93896b9c09918ba2d71cfbbe",
     "role": "weapon_skin_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "weapon-skin-behavior-preview-adapter",
       "table": "weapon_skin_data + common_item_data_base + weapon_skin_sfx_function_data; root weapon_skin_data comparison only",
       "row_key": 1110185,
       "field_refs": [
        "weapon_skin_data.key=1110185",
        "common_item_data_base.key=1110185",
        "common_item_data_base.name",
        "common_item_data_base.name CHS field_slot=4 value_slot=31414",
        "common_item_data_base.desc",
        "common_item_data_base.desc CHS field_slot=6 value_slot=9494",
        "weapon_skin_sfx_function_data.key=1120365",
        "weapon_skin_sfx_function_data.key=1120366",
        "weapon_skin_sfx_function_data.key=1120367",
        "weapon_skin_sfx_function_data.key=1120368",
        "weapon_skin_sfx_function_data.key=1120369",
        "weapon_skin_sfx_function_data.key=1120370",
        "weapon_skin_sfx_function_data.key=1120371",
        "weapon_skin_sfx_function_data.key=1120372",
        "weapon_skin_data.key=11101851",
        "weapon_skin_behavior_res_data.key=1110185",
        "weapon_skin_data.sale_ts (晚于快照日 → upcoming)",
        "common_item_data_base.key=skin_id (正式名)"
       ]
      }
     ]
    }
   },
   "ip_now": "斩神",
   "es_registry_row_key": null,
   "combat_panel": [
    {
     "cat": "命中效果",
     "name": "奇迹-命中",
     "src": "sfx"
    },
    {
     "cat": "击败特效",
     "name": "奇迹-击杀",
     "src": "sfx"
    },
    {
     "cat": "伤害跳字",
     "name": "奇迹-跳字",
     "src": "sfx"
    },
    {
     "cat": "攻击弹道",
     "name": "奇迹-弹道",
     "src": "sfx"
    },
    {
     "cat": "战斗音效",
     "name": "奇迹-音效",
     "src": "sfx"
    },
    {
     "cat": "攻击准星",
     "name": "奇迹-准星",
     "src": "sfx"
    },
    {
     "cat": "蓄力效果",
     "name": "奇迹-蓄力",
     "src": "sfx"
    }
   ],
   "ui_combat_short_names": [],
   "ui_short_name_es_key": null,
   "ui_short_name_match": "none",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "preview_group": "upcoming_named",
   "preview_note": "包内已配正式名「奇迹」与上架时间 2026-09-29（晚于包快照日），快照时尚未上架；不表示到期必上、不代表价格/概率。"
  },
  {
   "id": "1110186",
   "skin_id": 1110186,
   "catalog_layer": "current_parent",
   "name": "星辰刀",
   "official_name_status": "verified",
   "name_status": "verified",
   "name_display": "星辰刀",
   "official_desc": "星辰入刃，为末世守夜人斩尽长夜。「明日之后×斩神」联动限定外观。",
   "name_resolution": {
    "state": "verified",
    "name": "星辰刀",
    "normalized_roots": [],
    "named_sfx_row_count": 0,
    "rule": "Current display name comes from the same-snapshot BA8 common_item_data_base row key==skin_id, field=name, with replayable CHS field/value slots. SFX text is never a name source."
   },
   "sfx_consensus_state": "sfx_consensus_unpromoted",
   "version_status": "BA8 新增（相对 root 对照）",
   "model_path": "weapon/skin/skin_2003_031/skin_2003_031.gim",
   "field_provenance": {
    "coldarm_types": {
     "field_chs_slot": 19,
     "value_chs_slot": null,
     "scalar_type": "0x0b",
     "text": null
    },
    "fire_sfx_path": {
     "field_chs_slot": 15,
     "value_chs_slot": 57,
     "scalar_type": "0x05",
     "text": "effect/fx/weapon/skin/skin_2003_031/fx_skin_2003_031_dg.sfx"
    },
    "hit_sfx_functions": {
     "field_chs_slot": 13,
     "value_chs_slot": null,
     "scalar_type": "0x0b",
     "text": null
    },
    "sale_ts": {
     "field_chs_slot": 11,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "trace_functions": {
     "field_chs_slot": 14,
     "value_chs_slot": null,
     "scalar_type": "0x0b",
     "text": null
    },
    "yk_accessory_model_line_id": {
     "field_chs_slot": 12,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "camera_conf_id": {
     "field_chs_slot": 0,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "camera_conf_id_2": {
     "field_chs_slot": 1,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "charm_value": {
     "field_chs_slot": 2,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "jump_param": {
     "field_chs_slot": 3,
     "value_chs_slot": null,
     "scalar_type": "0x0b",
     "text": null
    },
    "level": {
     "field_chs_slot": 4,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "model_extra_position_offset": {
     "field_chs_slot": 5,
     "value_chs_slot": null,
     "scalar_type": "0x0b",
     "text": null
    },
    "model_extra_scale": {
     "field_chs_slot": 6,
     "value_chs_slot": null,
     "scalar_type": "0x22",
     "text": null
    },
    "model_path": {
     "field_chs_slot": 7,
     "value_chs_slot": 82,
     "scalar_type": "0x05",
     "text": "weapon/skin/skin_2003_031/skin_2003_031.gim"
    },
    "obtain_limit": {
     "field_chs_slot": 8,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "priority": {
     "field_chs_slot": 9,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "weapon_type": {
     "field_chs_slot": 10,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    }
   },
   "level": 4,
   "grade": "4紫皮级",
   "sale_ts": 1790697600,
   "sale_date": "2026-09-29",
   "release_state": "upcoming",
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "weapon_type_state": "snapshot_field",
   "sfx_item_count": 2,
   "named_sfx_item_count": 2,
   "variant_item_count": 1,
   "behavior_resources": [
    {
     "field": "fire_sfx_path",
     "path": "effect/fx/weapon/skin/skin_2003_031/fx_skin_2003_031_dg.sfx",
     "text_provenance": {
      "field_chs_slot": 0,
      "value_chs_slot": 379,
      "scalar_type": "0x05",
      "text": "effect/fx/weapon/skin/skin_2003_031/fx_skin_2003_031_dg.sfx"
     },
     "kind": "sfx_path"
    },
    {
     "field": "hit_sfx_path",
     "path": "effect/fx/weapon/skin/skin_2003_031/fx_skin_2003_031_sj.sfx",
     "text_provenance": {
      "field_chs_slot": 1,
      "value_chs_slot": 380,
      "scalar_type": "0x05",
      "text": "effect/fx/weapon/skin/skin_2003_031/fx_skin_2003_031_sj.sfx"
     },
     "kind": "sfx_path"
    }
   ],
   "sfx_items": [
    {
     "id": "1120360",
     "row_key": 1120360,
     "display_name": "星辰刀弹道",
     "sfx_name": "斩神-星辰刀",
     "item_name": "星辰刀弹道",
     "item_name_provenance": {
      "name": {
       "field_chs_slot": 4,
       "value_chs_slot": 38676,
       "scalar_type": "0x05",
       "text": "星辰刀弹道"
      }
     },
     "sfx_type": 6,
     "sfx_type_label": "挥砍特效（6）",
     "sfx_params": "effect/fx/weapon/skin/skin_2003_031/fx_skin_2003_031_dg.sfx",
     "inline_groups": [],
     "raw_fields": {
      "sfx_name": "斩神-星辰刀",
      "sfx_params": "effect/fx/weapon/skin/skin_2003_031/fx_skin_2003_031_dg.sfx",
      "level": 4,
      "sfx_type": 6,
      "skin_id": 1110186
     },
     "evidence": "structure",
     "evidence_level": "structure-only",
     "source": "Current same-snapshot SFX configuration child; display text from same-key common_item_data_base 1120xxx item name when present; not activity, availability, price, probability, or combat-effect proof.",
     "text_provenance": {
      "sfx_name": {
       "field_chs_slot": 7,
       "value_chs_slot": 58,
       "scalar_type": "0x05",
       "text": "斩神-星辰刀"
      }
     },
     "provenance": {
      "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
      "source_entries": [
       {
        "entry_index": 21883,
        "file_id": "B693DB548E5412B6",
        "decoded_sha256": "983b9f0b1652d2e198b54cf507a7c42d58965afedfba79ab3eeaeb2477634b13",
        "role": "weapon_skin_sfx_base"
       },
       {
        "entry_index": 11040,
        "file_id": "5C56D035B329BEBB",
        "decoded_sha256": "65040b06c143529d9a95352ab06bc01fe4abc64e85d58a3eba86240282779450",
        "role": "weapon_skin_sfx_chs"
       }
      ],
      "table": "weapon_skin_sfx_function_data (+ same-key common_item_data_base item name)",
      "row_key": 1120360,
      "field_refs": [
       "weapon_skin_sfx_function_data.key=1120360",
       "weapon_skin_sfx_function_data.skin_id=1110186",
       "weapon_skin_sfx_function_data.sfx_name",
       "weapon_skin_sfx_function_data.sfx_name CHS field_slot=7 value_slot=58",
       "common_item_data_base.key=1120360",
       "common_item_data_base.name",
       "common_item_data_base.name CHS field_slot=4 value_slot=38676"
      ],
      "name_source": "same-snapshot common_item_data_base row key==sfx row key name CHS replay"
     }
    },
    {
     "id": "1120361",
     "row_key": 1120361,
     "display_name": "星辰刀命中",
     "sfx_name": "斩神-星辰刀",
     "item_name": "星辰刀命中",
     "item_name_provenance": {
      "name": {
       "field_chs_slot": 4,
       "value_chs_slot": 38675,
       "scalar_type": "0x05",
       "text": "星辰刀命中"
      }
     },
     "sfx_type": 3,
     "sfx_type_label": "命中特效（3）",
     "sfx_params": "effect/fx/weapon/skin/skin_2003_031/fx_skin_2003_031_sj.sfx",
     "inline_groups": [],
     "raw_fields": {
      "sfx_name": "斩神-星辰刀",
      "sfx_params": "effect/fx/weapon/skin/skin_2003_031/fx_skin_2003_031_sj.sfx",
      "level": 4,
      "sfx_type": 3,
      "skin_id": 1110186
     },
     "evidence": "structure",
     "evidence_level": "structure-only",
     "source": "Current same-snapshot SFX configuration child; display text from same-key common_item_data_base 1120xxx item name when present; not activity, availability, price, probability, or combat-effect proof.",
     "text_provenance": {
      "sfx_name": {
       "field_chs_slot": 7,
       "value_chs_slot": 58,
       "scalar_type": "0x05",
       "text": "斩神-星辰刀"
      }
     },
     "provenance": {
      "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
      "source_entries": [
       {
        "entry_index": 21883,
        "file_id": "B693DB548E5412B6",
        "decoded_sha256": "983b9f0b1652d2e198b54cf507a7c42d58965afedfba79ab3eeaeb2477634b13",
        "role": "weapon_skin_sfx_base"
       },
       {
        "entry_index": 11040,
        "file_id": "5C56D035B329BEBB",
        "decoded_sha256": "65040b06c143529d9a95352ab06bc01fe4abc64e85d58a3eba86240282779450",
        "role": "weapon_skin_sfx_chs"
       }
      ],
      "table": "weapon_skin_sfx_function_data (+ same-key common_item_data_base item name)",
      "row_key": 1120361,
      "field_refs": [
       "weapon_skin_sfx_function_data.key=1120361",
       "weapon_skin_sfx_function_data.skin_id=1110186",
       "weapon_skin_sfx_function_data.sfx_name",
       "weapon_skin_sfx_function_data.sfx_name CHS field_slot=7 value_slot=58",
       "common_item_data_base.key=1120361",
       "common_item_data_base.name",
       "common_item_data_base.name CHS field_slot=4 value_slot=38675"
      ],
      "name_source": "same-snapshot common_item_data_base row key==sfx row key name CHS replay"
     }
    }
   ],
   "variant_items": [
    {
     "id": "11101861",
     "skin_id": 11101861,
     "catalog_layer": "time_limit_variant",
     "main_skin_id": 1110186,
     "display_name": "星辰刀（7天）",
     "name": "星辰刀（7天）",
     "official_name_status": "verified",
     "name_status": "verified",
     "name_display": "星辰刀（7天）",
     "official_desc": null,
     "name_resolution": {
      "state": "verified",
      "name": "星辰刀（7天）",
      "rule": "same-snapshot common_item_data_base row name"
     },
     "sfx_consensus_state": "no_sfx_text",
     "version_status": "BA8 新增（相对 root 对照）",
     "model_path": "weapon/skin/skin_2003_031/skin_2003_031.gim",
     "level": 4,
     "grade": "4紫皮级",
     "sale_ts": 1790697600,
     "sale_date": "2026-09-29",
     "release_state": "upcoming",
     "field_provenance": {
      "coldarm_types": {
       "field_chs_slot": 19,
       "value_chs_slot": null,
       "scalar_type": "0x0b",
       "text": null
      },
      "fire_sfx_path": {
       "field_chs_slot": 15,
       "value_chs_slot": 57,
       "scalar_type": "0x05",
       "text": "effect/fx/weapon/skin/skin_2003_031/fx_skin_2003_031_dg.sfx"
      },
      "sale_ts": {
       "field_chs_slot": 11,
       "value_chs_slot": null,
       "scalar_type": "0x01",
       "text": null
      },
      "yk_accessory_model_line_id": {
       "field_chs_slot": 12,
       "value_chs_slot": null,
       "scalar_type": "0x01",
       "text": null
      },
      "camera_conf_id": {
       "field_chs_slot": 0,
       "value_chs_slot": null,
       "scalar_type": "0x01",
       "text": null
      },
      "camera_conf_id_2": {
       "field_chs_slot": 1,
       "value_chs_slot": null,
       "scalar_type": "0x01",
       "text": null
      },
      "charm_value": {
       "field_chs_slot": 2,
       "value_chs_slot": null,
       "scalar_type": "0x01",
       "text": null
      },
      "jump_param": {
       "field_chs_slot": 3,
       "value_chs_slot": null,
       "scalar_type": "0x0b",
       "text": null
      },
      "level": {
       "field_chs_slot": 4,
       "value_chs_slot": null,
       "scalar_type": "0x01",
       "text": null
      },
      "model_extra_position_offset": {
       "field_chs_slot": 5,
       "value_chs_slot": null,
       "scalar_type": "0x0b",
       "text": null
      },
      "model_extra_scale": {
       "field_chs_slot": 6,
       "value_chs_slot": null,
       "scalar_type": "0x22",
       "text": null
      },
      "model_path": {
       "field_chs_slot": 7,
       "value_chs_slot": 82,
       "scalar_type": "0x05",
       "text": "weapon/skin/skin_2003_031/skin_2003_031.gim"
      },
      "obtain_limit": {
       "field_chs_slot": 8,
       "value_chs_slot": null,
       "scalar_type": "0x01",
       "text": null
      },
      "priority": {
       "field_chs_slot": 9,
       "value_chs_slot": null,
       "scalar_type": "0x01",
       "text": null
      },
      "weapon_type": {
       "field_chs_slot": 10,
       "value_chs_slot": null,
       "scalar_type": "0x01",
       "text": null
      }
     },
     "weapon_type": 50,
     "weapon_type_label": "冷兵器（50）",
     "weapon_type_state": "snapshot_field",
     "sfx_item_count": 0,
     "named_sfx_item_count": 0,
     "sfx_items": [],
     "reference_fields": {
      "source_kind": "no_user_reference_row",
      "source_path": "data/reference_inputs/weapon_skin_catalog_user_reference_v3_2.csv",
      "source_sha256": "827935d81e276c90559ae69401aed9a4e7cf7d75633a96f1ddc7277874998456",
      "row_key": 11101861,
      "name": "",
      "model_path": "",
      "version_status": "",
      "grade": "",
      "weapon_type": "",
      "description": "",
      "ip": "",
      "battle_action": "",
      "idle_action": "",
      "battle_effect_names": ""
     },
     "evidence": "structure",
     "evidence_level": "current-snapshot-verified",
     "source": "Current Documents BA8 weapon_skin_data time-limit variant row nested under its main skin; formal name from same-snapshot common_item_data_base when a row exists. Time-limit membership context is user real-machine knowledge.",
     "provenance": {
      "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
      "source_entries": [
       {
        "entry_index": 14250,
        "file_id": "765AB12F1D6EB0EA",
        "decoded_sha256": "5f0165ad7c7423be500532c35a4b3414b59967da93896b9c09918ba2d71cfbbe",
        "role": "weapon_skin_base"
       },
       {
        "entry_index": 25394,
        "file_id": "D35E3103168889D2",
        "decoded_sha256": "faf102d513b0900c476787bb41dc85f262ed923b9b5774ec881b5e0803caded1",
        "role": "weapon_skin_chs"
       },
       {
        "entry_index": 21883,
        "file_id": "B693DB548E5412B6",
        "decoded_sha256": "983b9f0b1652d2e198b54cf507a7c42d58965afedfba79ab3eeaeb2477634b13",
        "role": "weapon_skin_sfx_base"
       },
       {
        "entry_index": 11040,
        "file_id": "5C56D035B329BEBB",
        "decoded_sha256": "65040b06c143529d9a95352ab06bc01fe4abc64e85d58a3eba86240282779450",
        "role": "weapon_skin_sfx_chs"
       },
       {
        "entry_index": 49069,
        "file_id": "765AB12F1D6EB0EA",
        "decoded_sha256": "f26f931848b9b4264d47d3fe54143b26496acaaa165a55a6d25156a635a9e917",
        "role": "root_weapon_skin_base"
       },
       {
        "entry_index": 87558,
        "file_id": "D35E3103168889D2",
        "decoded_sha256": "fc7806c9f1200edf276ea776354aaadad853af4a9929bdacefe91702763dd24f",
        "role": "root_weapon_skin_chs"
       },
       {
        "entry_index": 21601,
        "file_id": "B42760CCA41DBC25",
        "decoded_sha256": "26fe910d01078b2b4c303bceff039ef9f42a0140d5bb90e1ca91f068286d86bd",
        "role": "common_item_base"
       },
       {
        "entry_index": 28668,
        "file_id": "EF3A8474A5E5F7A4",
        "decoded_sha256": "09c286b210c4e484cfc9a6b0d66bb38892575b614bedec518cc03d58b2bb90bb",
        "role": "common_item_chs"
       }
      ],
      "table": "weapon_skin_data + common_item_data_base (when present)",
      "row_key": 11101861,
      "field_refs": [
       "common_item_data_base.key=11101861",
       "common_item_data_base.name",
       "common_item_data_base.name CHS field_slot=4 value_slot=38677"
      ],
      "name_source": "same-snapshot BA8 common_item_data_base row key==11101861 field=name CHS field_slot=4 value_slot=38677",
      "member_sfx_row_keys": [],
      "business_chain": {
       "chain": "weapon_skin_data.key -> common_item_data_base.key (variant item row) -> name CHS replay",
       "item_row_key": 11101861,
       "proves": "same-snapshot formal item name exists for this time-limit variant id"
      },
      "root_comparison": {
       "source_lock_sha256": "0f824b35120f42e310a6f42e4ea20200d9465ad34c2e98f47c8ecaf9853b03b7",
       "comparison": "key-presence only; never used as current display-name source",
       "root_row_present": false
      }
     },
     "variant_type": "timed",
     "permanent_skin_id": 1110186,
     "variant_relation_state": "verified_runtime_rule",
     "variant_relation_target": "permanent_skin_id=1110186",
     "variant_relation_target_state": "resolved",
     "variant_relation_rule": "get_perm_skin_id(timed_id) = timed_id // 10（运行时代码证据）"
    }
   ],
   "reference_fields": {
    "source_kind": "user-provided-historical-catalog",
    "source_path": "data/reference_inputs/weapon_skin_catalog_user_reference_v3_2.csv",
    "source_sha256": "827935d81e276c90559ae69401aed9a4e7cf7d75633a96f1ddc7277874998456",
    "row_key": 1110186,
    "name": "",
    "model_path": "weapon/skin/skin_2003_031/skin_2003_031.gim",
    "version_status": "★8-29新增(仅行为资源)",
    "grade": "5 典藏",
    "weapon_type": "50 冷兵器",
    "description": "刀光fx_skin_2003_031_dg.sfx；命中fx_skin_2003_031_sj.sfx（无核芯）",
    "ip": "",
    "battle_action": "",
    "idle_action": "",
    "battle_effect_names": ""
   },
   "evidence": "structure",
   "evidence_level": "current-snapshot-verified",
   "source": "Current Documents BA8 weapon_skin_data parent; formal name/desc from same-snapshot common_item_data_base. Static table presence does not prove activity, availability, price, probability, or combat effect.",
   "provenance": {
    "source_lock_sha256": "eb14bca9542cc63eeeb16be61e344f5788ee312c104bb1c5bc028be0edae24ec",
    "source_entries": [
     {
      "entry_index": 14250,
      "file_id": "765AB12F1D6EB0EA",
      "decoded_sha256": "5f0165ad7c7423be500532c35a4b3414b59967da93896b9c09918ba2d71cfbbe",
      "role": "weapon_skin_base"
     },
     {
      "entry_index": 25394,
      "file_id": "D35E3103168889D2",
      "decoded_sha256": "faf102d513b0900c476787bb41dc85f262ed923b9b5774ec881b5e0803caded1",
      "role": "weapon_skin_chs"
     },
     {
      "entry_index": 21883,
      "file_id": "B693DB548E5412B6",
      "decoded_sha256": "983b9f0b1652d2e198b54cf507a7c42d58965afedfba79ab3eeaeb2477634b13",
      "role": "weapon_skin_sfx_base"
     },
     {
      "entry_index": 11040,
      "file_id": "5C56D035B329BEBB",
      "decoded_sha256": "65040b06c143529d9a95352ab06bc01fe4abc64e85d58a3eba86240282779450",
      "role": "weapon_skin_sfx_chs"
     },
     {
      "entry_index": 49069,
      "file_id": "765AB12F1D6EB0EA",
      "decoded_sha256": "f26f931848b9b4264d47d3fe54143b26496acaaa165a55a6d25156a635a9e917",
      "role": "root_weapon_skin_base"
     },
     {
      "entry_index": 87558,
      "file_id": "D35E3103168889D2",
      "decoded_sha256": "fc7806c9f1200edf276ea776354aaadad853af4a9929bdacefe91702763dd24f",
      "role": "root_weapon_skin_chs"
     },
     {
      "entry_index": 21601,
      "file_id": "B42760CCA41DBC25",
      "decoded_sha256": "26fe910d01078b2b4c303bceff039ef9f42a0140d5bb90e1ca91f068286d86bd",
      "role": "common_item_base"
     },
     {
      "entry_index": 28668,
      "file_id": "EF3A8474A5E5F7A4",
      "decoded_sha256": "09c286b210c4e484cfc9a6b0d66bb38892575b614bedec518cc03d58b2bb90bb",
      "role": "common_item_chs"
     }
    ],
    "table": "weapon_skin_data + common_item_data_base + weapon_skin_sfx_function_data; root weapon_skin_data comparison only",
    "row_key": 1110186,
    "field_refs": [
     "weapon_skin_data.key=1110186",
     "common_item_data_base.key=1110186",
     "common_item_data_base.name",
     "common_item_data_base.name CHS field_slot=4 value_slot=38674",
     "common_item_data_base.desc",
     "common_item_data_base.desc CHS field_slot=6 value_slot=10836",
     "weapon_skin_sfx_function_data.key=1120360",
     "weapon_skin_sfx_function_data.key=1120361",
     "weapon_skin_data.key=11101861",
     "weapon_skin_behavior_res_data.key=1110186",
     "weapon_skin_data.sale_ts (晚于快照日 → upcoming)",
     "common_item_data_base.key=skin_id (正式名)"
    ],
    "name_source": "same-snapshot common_item_data_base row (verified formal name); release not yet reached per skin row sale_ts",
    "member_sfx_row_keys": [
     1120360,
     1120361
    ],
    "member_variant_row_keys": [
     11101861
    ],
    "business_chain": {
     "chain": "weapon_skin_data.key -> common_item_data_base.key (item row) -> name/desc CHS replay",
     "item_row_key": 1110186,
     "proves": "same-snapshot formal item name exists for this skin id; not activity/availability proof"
    },
    "root_comparison": {
     "source_lock_sha256": "0f824b35120f42e310a6f42e4ea20200d9465ad34c2e98f47c8ecaf9853b03b7",
     "comparison": "key-presence only; never used as current display-name source",
     "root_row_present": false
    },
    "source_id": "weapon-skin-behavior-preview-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 14250,
     "file_id": "765AB12F1D6EB0EA",
     "decoded_sha256": "5f0165ad7c7423be500532c35a4b3414b59967da93896b9c09918ba2d71cfbbe",
     "role": "weapon_skin_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "weapon-skin-behavior-preview-adapter",
       "table": "weapon_skin_data + common_item_data_base + weapon_skin_sfx_function_data; root weapon_skin_data comparison only",
       "row_key": 1110186,
       "field_refs": [
        "weapon_skin_data.key=1110186",
        "common_item_data_base.key=1110186",
        "common_item_data_base.name",
        "common_item_data_base.name CHS field_slot=4 value_slot=38674",
        "common_item_data_base.desc",
        "common_item_data_base.desc CHS field_slot=6 value_slot=10836",
        "weapon_skin_sfx_function_data.key=1120360",
        "weapon_skin_sfx_function_data.key=1120361",
        "weapon_skin_data.key=11101861",
        "weapon_skin_behavior_res_data.key=1110186",
        "weapon_skin_data.sale_ts (晚于快照日 → upcoming)",
        "common_item_data_base.key=skin_id (正式名)"
       ]
      }
     ]
    }
   },
   "ip_now": "斩神",
   "es_registry_row_key": null,
   "combat_panel": [
    {
     "cat": "攻击弹道",
     "name": "星辰刀弹道",
     "src": "sfx"
    },
    {
     "cat": "命中效果",
     "name": "星辰刀命中",
     "src": "sfx"
    }
   ],
   "ui_combat_short_names": [],
   "ui_short_name_es_key": null,
   "ui_short_name_match": "none",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "preview_group": "upcoming_named",
   "preview_note": "包内已配正式名「星辰刀」与上架时间 2026-09-29（晚于包快照日），快照时尚未上架；不表示到期必上、不代表价格/概率。"
  },
  {
   "id": "1110187",
   "skin_id": 1110187,
   "catalog_layer": "current_parent",
   "name": "前方禁行",
   "official_name_status": "verified",
   "name_status": "verified",
   "name_display": "前方禁行",
   "official_desc": "警示为刃，前方禁行，一牌镇尽废土妖邪。「明日之后×斩神」联动限定外观。",
   "name_resolution": {
    "state": "verified",
    "name": "前方禁行",
    "normalized_roots": [],
    "named_sfx_row_count": 0,
    "rule": "Current display name comes from the same-snapshot BA8 common_item_data_base row key==skin_id, field=name, with replayable CHS field/value slots. SFX text is never a name source."
   },
   "sfx_consensus_state": "no_sfx_text",
   "version_status": "BA8 新增（相对 root 对照）",
   "model_path": "weapon/skin/skin_2003_032/skin_2003_032.gim",
   "field_provenance": {
    "coldarm_types": {
     "field_chs_slot": 19,
     "value_chs_slot": null,
     "scalar_type": "0x0b",
     "text": null
    },
    "sale_ts": {
     "field_chs_slot": 11,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "yk_accessory_model_line_id": {
     "field_chs_slot": 12,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "camera_conf_id": {
     "field_chs_slot": 0,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "camera_conf_id_2": {
     "field_chs_slot": 1,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "charm_value": {
     "field_chs_slot": 2,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "jump_param": {
     "field_chs_slot": 3,
     "value_chs_slot": null,
     "scalar_type": "0x0b",
     "text": null
    },
    "level": {
     "field_chs_slot": 4,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "model_extra_position_offset": {
     "field_chs_slot": 5,
     "value_chs_slot": null,
     "scalar_type": "0x0b",
     "text": null
    },
    "model_extra_scale": {
     "field_chs_slot": 6,
     "value_chs_slot": null,
     "scalar_type": "0x22",
     "text": null
    },
    "model_path": {
     "field_chs_slot": 7,
     "value_chs_slot": 232,
     "scalar_type": "0x05",
     "text": "weapon/skin/skin_2003_032/skin_2003_032.gim"
    },
    "obtain_limit": {
     "field_chs_slot": 8,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "priority": {
     "field_chs_slot": 9,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "weapon_type": {
     "field_chs_slot": 10,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    }
   },
   "level": 3,
   "grade": "3直售级",
   "sale_ts": 1790697600,
   "sale_date": "2026-09-29",
   "release_state": "upcoming",
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "weapon_type_state": "snapshot_field",
   "sfx_item_count": 0,
   "named_sfx_item_count": 0,
   "variant_item_count": 0,
   "behavior_resources": [],
   "sfx_items": [],
   "variant_items": [],
   "reference_fields": {
    "source_kind": "no_user_reference_row",
    "source_path": "data/reference_inputs/weapon_skin_catalog_user_reference_v3_2.csv",
    "source_sha256": "827935d81e276c90559ae69401aed9a4e7cf7d75633a96f1ddc7277874998456",
    "row_key": 1110187,
    "name": "",
    "model_path": "",
    "version_status": "",
    "grade": "",
    "weapon_type": "",
    "description": "",
    "ip": "",
    "battle_action": "",
    "idle_action": "",
    "battle_effect_names": ""
   },
   "evidence": "structure",
   "evidence_level": "current-snapshot-verified",
   "source": "Current Documents BA8 weapon_skin_data parent; formal name/desc from same-snapshot common_item_data_base. Static table presence does not prove activity, availability, price, probability, or combat effect.",
   "provenance": {
    "source_lock_sha256": "eb14bca9542cc63eeeb16be61e344f5788ee312c104bb1c5bc028be0edae24ec",
    "source_entries": [
     {
      "entry_index": 14250,
      "file_id": "765AB12F1D6EB0EA",
      "decoded_sha256": "5f0165ad7c7423be500532c35a4b3414b59967da93896b9c09918ba2d71cfbbe",
      "role": "weapon_skin_base"
     },
     {
      "entry_index": 25394,
      "file_id": "D35E3103168889D2",
      "decoded_sha256": "faf102d513b0900c476787bb41dc85f262ed923b9b5774ec881b5e0803caded1",
      "role": "weapon_skin_chs"
     },
     {
      "entry_index": 21883,
      "file_id": "B693DB548E5412B6",
      "decoded_sha256": "983b9f0b1652d2e198b54cf507a7c42d58965afedfba79ab3eeaeb2477634b13",
      "role": "weapon_skin_sfx_base"
     },
     {
      "entry_index": 11040,
      "file_id": "5C56D035B329BEBB",
      "decoded_sha256": "65040b06c143529d9a95352ab06bc01fe4abc64e85d58a3eba86240282779450",
      "role": "weapon_skin_sfx_chs"
     },
     {
      "entry_index": 49069,
      "file_id": "765AB12F1D6EB0EA",
      "decoded_sha256": "f26f931848b9b4264d47d3fe54143b26496acaaa165a55a6d25156a635a9e917",
      "role": "root_weapon_skin_base"
     },
     {
      "entry_index": 87558,
      "file_id": "D35E3103168889D2",
      "decoded_sha256": "fc7806c9f1200edf276ea776354aaadad853af4a9929bdacefe91702763dd24f",
      "role": "root_weapon_skin_chs"
     },
     {
      "entry_index": 21601,
      "file_id": "B42760CCA41DBC25",
      "decoded_sha256": "26fe910d01078b2b4c303bceff039ef9f42a0140d5bb90e1ca91f068286d86bd",
      "role": "common_item_base"
     },
     {
      "entry_index": 28668,
      "file_id": "EF3A8474A5E5F7A4",
      "decoded_sha256": "09c286b210c4e484cfc9a6b0d66bb38892575b614bedec518cc03d58b2bb90bb",
      "role": "common_item_chs"
     }
    ],
    "table": "weapon_skin_data + common_item_data_base + weapon_skin_sfx_function_data; root weapon_skin_data comparison only",
    "row_key": 1110187,
    "field_refs": [
     "weapon_skin_data.key=1110187",
     "common_item_data_base.key=1110187",
     "common_item_data_base.name",
     "common_item_data_base.name CHS field_slot=4 value_slot=26804",
     "common_item_data_base.desc",
     "common_item_data_base.desc CHS field_slot=6 value_slot=50591",
     "weapon_skin_data.sale_ts (晚于快照日 → upcoming)",
     "common_item_data_base.key=skin_id (正式名)"
    ],
    "name_source": "same-snapshot common_item_data_base row (verified formal name); release not yet reached per skin row sale_ts",
    "member_sfx_row_keys": [],
    "member_variant_row_keys": [],
    "business_chain": {
     "chain": "weapon_skin_data.key -> common_item_data_base.key (item row) -> name/desc CHS replay",
     "item_row_key": 1110187,
     "proves": "same-snapshot formal item name exists for this skin id; not activity/availability proof"
    },
    "root_comparison": {
     "source_lock_sha256": "0f824b35120f42e310a6f42e4ea20200d9465ad34c2e98f47c8ecaf9853b03b7",
     "comparison": "key-presence only; never used as current display-name source",
     "root_row_present": false
    },
    "source_id": "weapon-skin-behavior-preview-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 14250,
     "file_id": "765AB12F1D6EB0EA",
     "decoded_sha256": "5f0165ad7c7423be500532c35a4b3414b59967da93896b9c09918ba2d71cfbbe",
     "role": "weapon_skin_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "weapon-skin-behavior-preview-adapter",
       "table": "weapon_skin_data + common_item_data_base + weapon_skin_sfx_function_data; root weapon_skin_data comparison only",
       "row_key": 1110187,
       "field_refs": [
        "weapon_skin_data.key=1110187",
        "common_item_data_base.key=1110187",
        "common_item_data_base.name",
        "common_item_data_base.name CHS field_slot=4 value_slot=26804",
        "common_item_data_base.desc",
        "common_item_data_base.desc CHS field_slot=6 value_slot=50591",
        "weapon_skin_data.sale_ts (晚于快照日 → upcoming)",
        "common_item_data_base.key=skin_id (正式名)"
       ]
      }
     ]
    }
   },
   "ip_now": "斩神",
   "es_registry_row_key": null,
   "combat_panel": [],
   "ui_combat_short_names": [],
   "ui_short_name_es_key": null,
   "ui_short_name_match": "none",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "preview_group": "upcoming_named",
   "preview_note": "包内已配正式名「前方禁行」与上架时间 2026-09-29（晚于包快照日），快照时尚未上架；不表示到期必上、不代表价格/概率。"
  },
  {
   "id": "1110198",
   "skin_id": 1110198,
   "catalog_layer": "current_parent",
   "name": "拟化鳞渊",
   "official_name_status": "verified",
   "name_status": "verified",
   "name_display": "拟化鳞渊",
   "official_desc": "逆鳞震颤时，躯体深处的轰鸣倾覆苍穹。",
   "name_resolution": {
    "state": "verified",
    "name": "拟化鳞渊",
    "normalized_roots": [],
    "named_sfx_row_count": 0,
    "rule": "Current display name comes from the same-snapshot BA8 common_item_data_base row key==skin_id, field=name, with replayable CHS field/value slots. SFX text is never a name source."
   },
   "sfx_consensus_state": "no_sfx_text",
   "version_status": "BA8 新增（相对 root 对照）",
   "model_path": "weapon/skin/skin_1012_005/skin_1012_005.gim",
   "field_provenance": {
    "sale_ts": {
     "field_chs_slot": 11,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "skin_replace_anims": {
     "field_chs_slot": 16,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "camera_conf_id": {
     "field_chs_slot": 0,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "camera_conf_id_2": {
     "field_chs_slot": 1,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "charm_value": {
     "field_chs_slot": 2,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "jump_param": {
     "field_chs_slot": 3,
     "value_chs_slot": null,
     "scalar_type": "0x0b",
     "text": null
    },
    "level": {
     "field_chs_slot": 4,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "model_extra_position_offset": {
     "field_chs_slot": 5,
     "value_chs_slot": null,
     "scalar_type": "0x0b",
     "text": null
    },
    "model_extra_scale": {
     "field_chs_slot": 6,
     "value_chs_slot": null,
     "scalar_type": "0x22",
     "text": null
    },
    "model_path": {
     "field_chs_slot": 7,
     "value_chs_slot": 194,
     "scalar_type": "0x05",
     "text": "weapon/skin/skin_1012_005/skin_1012_005.gim"
    },
    "obtain_limit": {
     "field_chs_slot": 8,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "priority": {
     "field_chs_slot": 9,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "weapon_type": {
     "field_chs_slot": 10,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    }
   },
   "level": 3,
   "grade": "3直售级",
   "sale_ts": 1790697600,
   "sale_date": "2026-09-29",
   "release_state": "upcoming",
   "weapon_type": 7,
   "weapon_type_label": "榴弹炮（7）",
   "weapon_type_state": "snapshot_field",
   "sfx_item_count": 0,
   "named_sfx_item_count": 0,
   "variant_item_count": 0,
   "behavior_resources": [],
   "sfx_items": [],
   "variant_items": [],
   "reference_fields": {
    "source_kind": "no_user_reference_row",
    "source_path": "data/reference_inputs/weapon_skin_catalog_user_reference_v3_2.csv",
    "source_sha256": "827935d81e276c90559ae69401aed9a4e7cf7d75633a96f1ddc7277874998456",
    "row_key": 1110198,
    "name": "",
    "model_path": "",
    "version_status": "",
    "grade": "",
    "weapon_type": "",
    "description": "",
    "ip": "",
    "battle_action": "",
    "idle_action": "",
    "battle_effect_names": ""
   },
   "evidence": "structure",
   "evidence_level": "current-snapshot-verified",
   "source": "Current Documents BA8 weapon_skin_data parent; formal name/desc from same-snapshot common_item_data_base. Static table presence does not prove activity, availability, price, probability, or combat effect.",
   "provenance": {
    "source_lock_sha256": "eb14bca9542cc63eeeb16be61e344f5788ee312c104bb1c5bc028be0edae24ec",
    "source_entries": [
     {
      "entry_index": 14250,
      "file_id": "765AB12F1D6EB0EA",
      "decoded_sha256": "5f0165ad7c7423be500532c35a4b3414b59967da93896b9c09918ba2d71cfbbe",
      "role": "weapon_skin_base"
     },
     {
      "entry_index": 25394,
      "file_id": "D35E3103168889D2",
      "decoded_sha256": "faf102d513b0900c476787bb41dc85f262ed923b9b5774ec881b5e0803caded1",
      "role": "weapon_skin_chs"
     },
     {
      "entry_index": 21883,
      "file_id": "B693DB548E5412B6",
      "decoded_sha256": "983b9f0b1652d2e198b54cf507a7c42d58965afedfba79ab3eeaeb2477634b13",
      "role": "weapon_skin_sfx_base"
     },
     {
      "entry_index": 11040,
      "file_id": "5C56D035B329BEBB",
      "decoded_sha256": "65040b06c143529d9a95352ab06bc01fe4abc64e85d58a3eba86240282779450",
      "role": "weapon_skin_sfx_chs"
     },
     {
      "entry_index": 49069,
      "file_id": "765AB12F1D6EB0EA",
      "decoded_sha256": "f26f931848b9b4264d47d3fe54143b26496acaaa165a55a6d25156a635a9e917",
      "role": "root_weapon_skin_base"
     },
     {
      "entry_index": 87558,
      "file_id": "D35E3103168889D2",
      "decoded_sha256": "fc7806c9f1200edf276ea776354aaadad853af4a9929bdacefe91702763dd24f",
      "role": "root_weapon_skin_chs"
     },
     {
      "entry_index": 21601,
      "file_id": "B42760CCA41DBC25",
      "decoded_sha256": "26fe910d01078b2b4c303bceff039ef9f42a0140d5bb90e1ca91f068286d86bd",
      "role": "common_item_base"
     },
     {
      "entry_index": 28668,
      "file_id": "EF3A8474A5E5F7A4",
      "decoded_sha256": "09c286b210c4e484cfc9a6b0d66bb38892575b614bedec518cc03d58b2bb90bb",
      "role": "common_item_chs"
     }
    ],
    "table": "weapon_skin_data + common_item_data_base + weapon_skin_sfx_function_data; root weapon_skin_data comparison only",
    "row_key": 1110198,
    "field_refs": [
     "weapon_skin_data.key=1110198",
     "common_item_data_base.key=1110198",
     "common_item_data_base.name",
     "common_item_data_base.name CHS field_slot=4 value_slot=36613",
     "common_item_data_base.desc",
     "common_item_data_base.desc CHS field_slot=6 value_slot=52096",
     "weapon_skin_data.sale_ts (晚于快照日 → upcoming)",
     "common_item_data_base.key=skin_id (正式名)"
    ],
    "name_source": "same-snapshot common_item_data_base row (verified formal name); release not yet reached per skin row sale_ts",
    "member_sfx_row_keys": [],
    "member_variant_row_keys": [],
    "business_chain": {
     "chain": "weapon_skin_data.key -> common_item_data_base.key (item row) -> name/desc CHS replay",
     "item_row_key": 1110198,
     "proves": "same-snapshot formal item name exists for this skin id; not activity/availability proof"
    },
    "root_comparison": {
     "source_lock_sha256": "0f824b35120f42e310a6f42e4ea20200d9465ad34c2e98f47c8ecaf9853b03b7",
     "comparison": "key-presence only; never used as current display-name source",
     "root_row_present": false
    },
    "source_id": "weapon-skin-behavior-preview-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 14250,
     "file_id": "765AB12F1D6EB0EA",
     "decoded_sha256": "5f0165ad7c7423be500532c35a4b3414b59967da93896b9c09918ba2d71cfbbe",
     "role": "weapon_skin_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "weapon-skin-behavior-preview-adapter",
       "table": "weapon_skin_data + common_item_data_base + weapon_skin_sfx_function_data; root weapon_skin_data comparison only",
       "row_key": 1110198,
       "field_refs": [
        "weapon_skin_data.key=1110198",
        "common_item_data_base.key=1110198",
        "common_item_data_base.name",
        "common_item_data_base.name CHS field_slot=4 value_slot=36613",
        "common_item_data_base.desc",
        "common_item_data_base.desc CHS field_slot=6 value_slot=52096",
        "weapon_skin_data.sale_ts (晚于快照日 → upcoming)",
        "common_item_data_base.key=skin_id (正式名)"
       ]
      }
     ]
    }
   },
   "ip_now": null,
   "es_registry_row_key": null,
   "combat_panel": [],
   "ui_combat_short_names": [],
   "ui_short_name_es_key": null,
   "ui_short_name_match": "none",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "preview_group": "upcoming_named",
   "preview_note": "包内已配正式名「拟化鳞渊」与上架时间 2026-09-29（晚于包快照日），快照时尚未上架；不表示到期必上、不代表价格/概率。"
  },
  {
   "id": "1110199",
   "skin_id": 1110199,
   "catalog_layer": "current_parent",
   "name": "拟化幽瞳",
   "official_name_status": "verified",
   "name_status": "verified",
   "name_display": "拟化幽瞳",
   "official_desc": "瞳孔锁定的刹那，在猎物心口刻下归途。",
   "name_resolution": {
    "state": "verified",
    "name": "拟化幽瞳",
    "normalized_roots": [],
    "named_sfx_row_count": 0,
    "rule": "Current display name comes from the same-snapshot BA8 common_item_data_base row key==skin_id, field=name, with replayable CHS field/value slots. SFX text is never a name source."
   },
   "sfx_consensus_state": "no_sfx_text",
   "version_status": "BA8 新增（相对 root 对照）",
   "model_path": "weapon/skin/skin_1003_007/skin_1003_007.gim",
   "field_provenance": {
    "sale_ts": {
     "field_chs_slot": 11,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "yk_accessory_model_line_id": {
     "field_chs_slot": 12,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "camera_conf_id": {
     "field_chs_slot": 0,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "camera_conf_id_2": {
     "field_chs_slot": 1,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "charm_value": {
     "field_chs_slot": 2,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "jump_param": {
     "field_chs_slot": 3,
     "value_chs_slot": null,
     "scalar_type": "0x0b",
     "text": null
    },
    "level": {
     "field_chs_slot": 4,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "model_extra_position_offset": {
     "field_chs_slot": 5,
     "value_chs_slot": null,
     "scalar_type": "0x0b",
     "text": null
    },
    "model_extra_scale": {
     "field_chs_slot": 6,
     "value_chs_slot": null,
     "scalar_type": "0x22",
     "text": null
    },
    "model_path": {
     "field_chs_slot": 7,
     "value_chs_slot": 143,
     "scalar_type": "0x05",
     "text": "weapon/skin/skin_1003_007/skin_1003_007.gim"
    },
    "obtain_limit": {
     "field_chs_slot": 8,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "priority": {
     "field_chs_slot": 9,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    },
    "weapon_type": {
     "field_chs_slot": 10,
     "value_chs_slot": null,
     "scalar_type": "0x01",
     "text": null
    }
   },
   "level": 3,
   "grade": "3直售级",
   "sale_ts": 1790697600,
   "sale_date": "2026-09-29",
   "release_state": "upcoming",
   "weapon_type": 6,
   "weapon_type_label": "手枪（6）",
   "weapon_type_state": "snapshot_field",
   "sfx_item_count": 0,
   "named_sfx_item_count": 0,
   "variant_item_count": 0,
   "behavior_resources": [],
   "sfx_items": [],
   "variant_items": [],
   "reference_fields": {
    "source_kind": "no_user_reference_row",
    "source_path": "data/reference_inputs/weapon_skin_catalog_user_reference_v3_2.csv",
    "source_sha256": "827935d81e276c90559ae69401aed9a4e7cf7d75633a96f1ddc7277874998456",
    "row_key": 1110199,
    "name": "",
    "model_path": "",
    "version_status": "",
    "grade": "",
    "weapon_type": "",
    "description": "",
    "ip": "",
    "battle_action": "",
    "idle_action": "",
    "battle_effect_names": ""
   },
   "evidence": "structure",
   "evidence_level": "current-snapshot-verified",
   "source": "Current Documents BA8 weapon_skin_data parent; formal name/desc from same-snapshot common_item_data_base. Static table presence does not prove activity, availability, price, probability, or combat effect.",
   "provenance": {
    "source_lock_sha256": "eb14bca9542cc63eeeb16be61e344f5788ee312c104bb1c5bc028be0edae24ec",
    "source_entries": [
     {
      "entry_index": 14250,
      "file_id": "765AB12F1D6EB0EA",
      "decoded_sha256": "5f0165ad7c7423be500532c35a4b3414b59967da93896b9c09918ba2d71cfbbe",
      "role": "weapon_skin_base"
     },
     {
      "entry_index": 25394,
      "file_id": "D35E3103168889D2",
      "decoded_sha256": "faf102d513b0900c476787bb41dc85f262ed923b9b5774ec881b5e0803caded1",
      "role": "weapon_skin_chs"
     },
     {
      "entry_index": 21883,
      "file_id": "B693DB548E5412B6",
      "decoded_sha256": "983b9f0b1652d2e198b54cf507a7c42d58965afedfba79ab3eeaeb2477634b13",
      "role": "weapon_skin_sfx_base"
     },
     {
      "entry_index": 11040,
      "file_id": "5C56D035B329BEBB",
      "decoded_sha256": "65040b06c143529d9a95352ab06bc01fe4abc64e85d58a3eba86240282779450",
      "role": "weapon_skin_sfx_chs"
     },
     {
      "entry_index": 49069,
      "file_id": "765AB12F1D6EB0EA",
      "decoded_sha256": "f26f931848b9b4264d47d3fe54143b26496acaaa165a55a6d25156a635a9e917",
      "role": "root_weapon_skin_base"
     },
     {
      "entry_index": 87558,
      "file_id": "D35E3103168889D2",
      "decoded_sha256": "fc7806c9f1200edf276ea776354aaadad853af4a9929bdacefe91702763dd24f",
      "role": "root_weapon_skin_chs"
     },
     {
      "entry_index": 21601,
      "file_id": "B42760CCA41DBC25",
      "decoded_sha256": "26fe910d01078b2b4c303bceff039ef9f42a0140d5bb90e1ca91f068286d86bd",
      "role": "common_item_base"
     },
     {
      "entry_index": 28668,
      "file_id": "EF3A8474A5E5F7A4",
      "decoded_sha256": "09c286b210c4e484cfc9a6b0d66bb38892575b614bedec518cc03d58b2bb90bb",
      "role": "common_item_chs"
     }
    ],
    "table": "weapon_skin_data + common_item_data_base + weapon_skin_sfx_function_data; root weapon_skin_data comparison only",
    "row_key": 1110199,
    "field_refs": [
     "weapon_skin_data.key=1110199",
     "common_item_data_base.key=1110199",
     "common_item_data_base.name",
     "common_item_data_base.name CHS field_slot=4 value_slot=36610",
     "common_item_data_base.desc",
     "common_item_data_base.desc CHS field_slot=6 value_slot=45087",
     "weapon_skin_data.sale_ts (晚于快照日 → upcoming)",
     "common_item_data_base.key=skin_id (正式名)"
    ],
    "name_source": "same-snapshot common_item_data_base row (verified formal name); release not yet reached per skin row sale_ts",
    "member_sfx_row_keys": [],
    "member_variant_row_keys": [],
    "business_chain": {
     "chain": "weapon_skin_data.key -> common_item_data_base.key (item row) -> name/desc CHS replay",
     "item_row_key": 1110199,
     "proves": "same-snapshot formal item name exists for this skin id; not activity/availability proof"
    },
    "root_comparison": {
     "source_lock_sha256": "0f824b35120f42e310a6f42e4ea20200d9465ad34c2e98f47c8ecaf9853b03b7",
     "comparison": "key-presence only; never used as current display-name source",
     "root_row_present": false
    },
    "source_id": "weapon-skin-behavior-preview-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 14250,
     "file_id": "765AB12F1D6EB0EA",
     "decoded_sha256": "5f0165ad7c7423be500532c35a4b3414b59967da93896b9c09918ba2d71cfbbe",
     "role": "weapon_skin_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "weapon-skin-behavior-preview-adapter",
       "table": "weapon_skin_data + common_item_data_base + weapon_skin_sfx_function_data; root weapon_skin_data comparison only",
       "row_key": 1110199,
       "field_refs": [
        "weapon_skin_data.key=1110199",
        "common_item_data_base.key=1110199",
        "common_item_data_base.name",
        "common_item_data_base.name CHS field_slot=4 value_slot=36610",
        "common_item_data_base.desc",
        "common_item_data_base.desc CHS field_slot=6 value_slot=45087",
        "weapon_skin_data.sale_ts (晚于快照日 → upcoming)",
        "common_item_data_base.key=skin_id (正式名)"
       ]
      }
     ]
    }
   },
   "ip_now": null,
   "es_registry_row_key": null,
   "combat_panel": [],
   "ui_combat_short_names": [],
   "ui_short_name_es_key": null,
   "ui_short_name_match": "none",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "preview_group": "upcoming_named",
   "preview_note": "包内已配正式名「拟化幽瞳」与上架时间 2026-09-29（晚于包快照日），快照时尚未上架；不表示到期必上、不代表价格/概率。"
  },
  {
   "id": "1110192",
   "skin_id": 1110192,
   "catalog_layer": "behavior_preview_only",
   "name": null,
   "sale_ts": 0,
   "sale_date": null,
   "release_state": "behavior_only",
   "display_name": "未命名皮肤 · ID 1110192",
   "official_name_status": "no_item_row",
   "name_status": "unresolved",
   "name_status_note": "仅行为资源、无同快照道具行名、无可回放候选名",
   "name_display": "未命名皮肤 · ID 1110192",
   "official_desc": null,
   "name_resolution": {
    "state": "behavior_preview_no_current_name_source",
    "name": null,
    "rule": "A current behavior-resource row proves only static effect-path configuration. No weapon_skin_data parent row and no common_item_data_base item row exist for this id; never named from a historical reference."
   },
   "version_status": "仅当前 BA8 行为资源；无 weapon_skin_data 父项、无道具行",
   "model_path": "",
   "field_provenance": {
    "fire_sfx_path": {
     "field_chs_slot": 0,
     "value_chs_slot": 304,
     "scalar_type": "0x05",
     "text": "effect/fx/weapon/skin/skin_1008_007/fx_skin_1008_007_kh.sfx"
    },
    "hit_sfx_path": {
     "field_chs_slot": 1,
     "value_chs_slot": 303,
     "scalar_type": "0x05",
     "text": "effect/fx/weapon/skin/skin_1008_007/fx_skin_1008_007_hit.sfx"
    },
    "trajectory_path_real": {
     "field_chs_slot": 3,
     "value_chs_slot": 299,
     "scalar_type": "0x05",
     "text": "effect/fx/weapon/skin/skin_1008_007/fx_skin_1008_007_dd.sfx"
    },
    "trajectory_path_special": {
     "field_chs_slot": 8,
     "value_chs_slot": 301,
     "scalar_type": "0x05",
     "text": "effect/fx/weapon/skin/skin_1008_007/fx_skin_1008_007_dd_ydx.sfx"
    },
    "trajectory_sfx_path": {
     "field_chs_slot": 2,
     "value_chs_slot": 300,
     "scalar_type": "0x05",
     "text": "effect/fx/weapon/skin/skin_1008_007/fx_skin_1008_007_dd_lx.sfx"
    },
    "trajectory_sfx_path_nor": {
     "field_chs_slot": 4,
     "value_chs_slot": 279,
     "scalar_type": "0x05",
     "text": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_dd_lx_jc_01.sfx"
    },
    "trajectory_sfx_path_trace": {
     "field_chs_slot": 9,
     "value_chs_slot": 302,
     "scalar_type": "0x05",
     "text": "effect/fx/weapon/skin/skin_1008_007/fx_skin_1008_007_dd_ydx_rh.sfx"
    }
   },
   "level": null,
   "grade": "未配置",
   "weapon_type": 8,
   "weapon_type_label": "电磁机枪（8）",
   "weapon_type_state": "candidate_asset_path_convention",
   "weapon_type_inference": {
    "state": "candidate_asset_path_convention",
    "type_code": 8,
    "type_name": "电磁机枪",
    "matched_path": "effect/fx/weapon/skin/skin_1008_007/fx_skin_1008_007_kh.sfx",
    "rule": "资源路径/模型名 token skin_<4位模型前缀>_<3位序号> → 前缀表映射到 weapon_type；同一 token 亦出现在 model_path",
    "same_snapshot_agreement": "113/113（既有 token 又有真实 weapon_type_label 的行，0 反例）",
    "not_a_name_source": true
   },
   "sfx_item_count": 0,
   "named_sfx_item_count": 0,
   "sfx_items": [],
   "behavior_resources": [
    {
     "field": "fire_sfx_path",
     "path": "effect/fx/weapon/skin/skin_1008_007/fx_skin_1008_007_kh.sfx",
     "text_provenance": {
      "field_chs_slot": 0,
      "value_chs_slot": 304,
      "scalar_type": "0x05",
      "text": "effect/fx/weapon/skin/skin_1008_007/fx_skin_1008_007_kh.sfx"
     },
     "kind": "sfx_path"
    },
    {
     "field": "hit_sfx_path",
     "path": "effect/fx/weapon/skin/skin_1008_007/fx_skin_1008_007_hit.sfx",
     "text_provenance": {
      "field_chs_slot": 1,
      "value_chs_slot": 303,
      "scalar_type": "0x05",
      "text": "effect/fx/weapon/skin/skin_1008_007/fx_skin_1008_007_hit.sfx"
     },
     "kind": "sfx_path"
    },
    {
     "field": "trajectory_path_real",
     "path": "effect/fx/weapon/skin/skin_1008_007/fx_skin_1008_007_dd.sfx",
     "text_provenance": {
      "field_chs_slot": 3,
      "value_chs_slot": 299,
      "scalar_type": "0x05",
      "text": "effect/fx/weapon/skin/skin_1008_007/fx_skin_1008_007_dd.sfx"
     },
     "kind": "sfx_path"
    },
    {
     "field": "trajectory_path_special",
     "path": "effect/fx/weapon/skin/skin_1008_007/fx_skin_1008_007_dd_ydx.sfx",
     "text_provenance": {
      "field_chs_slot": 8,
      "value_chs_slot": 301,
      "scalar_type": "0x05",
      "text": "effect/fx/weapon/skin/skin_1008_007/fx_skin_1008_007_dd_ydx.sfx"
     },
     "kind": "sfx_path"
    },
    {
     "field": "trajectory_sfx_path",
     "path": "effect/fx/weapon/skin/skin_1008_007/fx_skin_1008_007_dd_lx.sfx",
     "text_provenance": {
      "field_chs_slot": 2,
      "value_chs_slot": 300,
      "scalar_type": "0x05",
      "text": "effect/fx/weapon/skin/skin_1008_007/fx_skin_1008_007_dd_lx.sfx"
     },
     "kind": "sfx_path"
    },
    {
     "field": "trajectory_sfx_path_nor",
     "path": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_dd_lx_jc_01.sfx",
     "text_provenance": {
      "field_chs_slot": 4,
      "value_chs_slot": 279,
      "scalar_type": "0x05",
      "text": "effect/fx/weapon/skin/skin_1007_011/fx_skin_1007_011_dd_lx_jc_01.sfx"
     },
     "kind": "sfx_path"
    },
    {
     "field": "trajectory_sfx_path_trace",
     "path": "effect/fx/weapon/skin/skin_1008_007/fx_skin_1008_007_dd_ydx_rh.sfx",
     "text_provenance": {
      "field_chs_slot": 9,
      "value_chs_slot": 302,
      "scalar_type": "0x05",
      "text": "effect/fx/weapon/skin/skin_1008_007/fx_skin_1008_007_dd_ydx_rh.sfx"
     },
     "kind": "sfx_path"
    }
   ],
   "reference_fields": {
    "source_kind": "no_user_reference_row",
    "source_path": "data/reference_inputs/weapon_skin_catalog_user_reference_v3_2.csv",
    "source_sha256": "827935d81e276c90559ae69401aed9a4e7cf7d75633a96f1ddc7277874998456",
    "row_key": 1110192,
    "name": "",
    "model_path": "",
    "version_status": "",
    "grade": "",
    "weapon_type": "",
    "description": "",
    "ip": "",
    "battle_action": "",
    "idle_action": "",
    "battle_effect_names": ""
   },
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Current Documents BA8 weapon_skin_behavior_res_data resource-only row; it proves static behavior-resource paths only and does not prove a formal skin parent, activity, availability, price, probability, or combat effect.",
   "provenance": {
    "source_lock_sha256": "eb14bca9542cc63eeeb16be61e344f5788ee312c104bb1c5bc028be0edae24ec",
    "source_entries": [
     {
      "entry_index": 19129,
      "file_id": "9F445AE2AA87D880",
      "decoded_sha256": "ba082014eb2bededc37d3b8da3b28c25020ff8c3e70abdf48ddecbf7b64fb243",
      "role": "weapon_skin_behavior_base"
     },
     {
      "entry_index": 27554,
      "file_id": "E59CCA1F31417C6A",
      "decoded_sha256": "82b1af7a5904994831f217a9638d128c051249a4ea7513a9ddcbc43d5cc2c4a0",
      "role": "weapon_skin_behavior_chs"
     }
    ],
    "table": "weapon_skin_behavior_res_data",
    "row_key": 1110192,
    "field_refs": [
     "weapon_skin_behavior_res_data.key=1110192",
     "weapon_skin_behavior_res_data.fire_sfx_path",
     "weapon_skin_behavior_res_data.hit_sfx_path",
     "weapon_skin_behavior_res_data.trajectory_path_real",
     "weapon_skin_behavior_res_data.trajectory_path_special",
     "weapon_skin_behavior_res_data.trajectory_sfx_path",
     "weapon_skin_behavior_res_data.trajectory_sfx_path_nor",
     "weapon_skin_behavior_res_data.trajectory_sfx_path_trace",
     "weapon_skin_data.absent_parent_row",
     "common_item_data_base.absent_item_row"
    ],
    "name_source": "no item row in the current snapshot; preview layer stays unfilled (no name claim)",
    "source_id": "weapon-skin-behavior-preview-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 19129,
     "file_id": "9F445AE2AA87D880",
     "decoded_sha256": "ba082014eb2bededc37d3b8da3b28c25020ff8c3e70abdf48ddecbf7b64fb243",
     "role": "weapon_skin_behavior_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "weapon-skin-behavior-preview-adapter",
       "table": "weapon_skin_behavior_res_data",
       "row_key": 1110192,
       "field_refs": [
        "weapon_skin_behavior_res_data.key=1110192",
        "weapon_skin_behavior_res_data.fire_sfx_path",
        "weapon_skin_behavior_res_data.hit_sfx_path",
        "weapon_skin_behavior_res_data.trajectory_path_real",
        "weapon_skin_behavior_res_data.trajectory_path_special",
        "weapon_skin_behavior_res_data.trajectory_sfx_path",
        "weapon_skin_behavior_res_data.trajectory_sfx_path_nor",
        "weapon_skin_behavior_res_data.trajectory_sfx_path_trace",
        "weapon_skin_data.absent_parent_row",
        "common_item_data_base.absent_item_row"
       ]
      }
     ]
    }
   },
   "ip_now": null,
   "es_registry_row_key": null,
   "combat_panel": [],
   "ui_combat_short_names": [],
   "ui_short_name_es_key": null,
   "ui_short_name_match": "none",
   "status_tags": [
    "unresolved",
    "static config"
   ],
   "preview_group": "behavior_only_no_name",
   "preview_note": "仅行为资源行：无 weapon_skin_data 父项、无道具行，故无正式名与品级。"
  }
 ]
};
