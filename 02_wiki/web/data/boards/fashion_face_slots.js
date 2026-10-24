window.WIKI_BOARD_fashion_face_slots = {
 "meta": {
  "name": "当前包 · 面饰/挂饰（face 槽）行级槽位复证",
  "category": "二、时装类 / （二）面饰/发饰",
  "source_server": "体验服 Documents 当前快照",
  "package_sha": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
  "generated": "2026-10-23T14:40:18Z",
  "evidence": "verified",
  "notes": [
   "player_module_appear_data（entry 003546 base + 010816 CHS，BA8 同快照）1131 行全量行级解码；name/desc 列级 0x05 槽位回放（此表 name 直接中文，非时装表的 int 文案 ID）。去 -N天 时限后缀聚合 180 条目=face 槽附件名册（眼镜/面具/帽子/挂饰，part_type 全 face），与旧池扫描 180 完全一致→名册正确性行级证实。desc=行级主题富文本（#f(5) 系列标题+描述，同主题多行共享同一池文本），按槽位原样回放不解释。valid_days=1/3/5/7/14/30 或永久。int name→外部文案表层与本表无关（25.5 待办②关闭）。"
  ],
  "provenance": {
   "audit_status": "passed",
   "source_locks": [
    {
     "sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
     "bytes": 196059988,
     "mtime_ns": 1792505574167464800,
     "path_hint": "Documents/script.py314.lc.npk"
    }
   ],
   "source_id": "documents-py314-current",
   "base_entry": {
    "entry_index": 4212,
    "file_id": "24947DBB72A943E5",
    "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
    "role": "player_module_appear_data_base"
   },
   "chs_entry": {
    "entry_index": 12702,
    "file_id": "6CD197C9670A961C",
    "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
    "role": "player_module_appear_data_chs"
   },
   "fid_lookup": true
  }
 },
 "items": [
  {
   "id": "face_260000",
   "row_key": 260000,
   "name": "粉红派对眼镜",
   "display_name": "粉红派对眼镜",
   "desc": "时装挂饰，可配戴在眼睛部位。在使用某些时装时无法佩戴。#r最长1天可用期",
   "icon": "item_icon/icon_260000",
   "part_type": null,
   "part_code": 1,
   "sort_key": null,
   "charm_value": null,
   "model_id": null,
   "valid_days": 1,
   "has_permanent": false,
   "duration_days": [
    1
   ],
   "all_row_keys": [
    260000
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 260000,
     "text": "粉红派对眼镜",
     "field_chs_slot": 7,
     "value_chs_slot": 1800,
     "duration_days": 1,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1800,
     "scalar_type": "0x05",
     "text": "粉红派对眼镜"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 37,
     "scalar_type": "0x05",
     "text": "时装挂饰，可配戴在眼睛部位。在使用某些时装时无法佩戴。#r最长1天可用期"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 260000,
    "field_refs": [
     "player_module_appear_data.row_key=260000",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1800",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=37"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_260010",
   "row_key": 260010,
   "name": "疯狂博士眼镜",
   "display_name": "疯狂博士眼镜",
   "desc": "时装挂饰，可配戴在眼睛部位。在使用某些时装时无法佩戴。#r最长1天可用期",
   "icon": "item_icon/icon_260010",
   "part_type": null,
   "part_code": 1,
   "sort_key": null,
   "charm_value": null,
   "model_id": null,
   "valid_days": 1,
   "has_permanent": false,
   "duration_days": [
    1
   ],
   "all_row_keys": [
    260010
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 260010,
     "text": "疯狂博士眼镜",
     "field_chs_slot": 7,
     "value_chs_slot": 1739,
     "duration_days": 1,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1739,
     "scalar_type": "0x05",
     "text": "疯狂博士眼镜"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 37,
     "scalar_type": "0x05",
     "text": "时装挂饰，可配戴在眼睛部位。在使用某些时装时无法佩戴。#r最长1天可用期"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 260010,
    "field_refs": [
     "player_module_appear_data.row_key=260010",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1739",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=37"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_260020",
   "row_key": 260020,
   "name": "爱心催眠眼镜",
   "display_name": "爱心催眠眼镜",
   "desc": "时装挂饰，可配戴在眼睛部位。在使用某些时装时无法佩戴。#r最长1天可用期",
   "icon": "item_icon/icon_260020",
   "part_type": null,
   "part_code": 1,
   "sort_key": null,
   "charm_value": null,
   "model_id": null,
   "valid_days": 1,
   "has_permanent": false,
   "duration_days": [
    1
   ],
   "all_row_keys": [
    260020
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 260020,
     "text": "爱心催眠眼镜",
     "field_chs_slot": 7,
     "value_chs_slot": 1666,
     "duration_days": 1,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1666,
     "scalar_type": "0x05",
     "text": "爱心催眠眼镜"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 37,
     "scalar_type": "0x05",
     "text": "时装挂饰，可配戴在眼睛部位。在使用某些时装时无法佩戴。#r最长1天可用期"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 260020,
    "field_refs": [
     "player_module_appear_data.row_key=260020",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1666",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=37"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_260030",
   "row_key": 260030,
   "name": "紫色派对帽子",
   "display_name": "紫色派对帽子",
   "desc": "时装挂饰，可配戴在头顶。在使用某些时装时无法佩戴。#r最长1天可用期",
   "icon": "item_icon/icon_260030",
   "part_type": null,
   "part_code": 2,
   "sort_key": null,
   "charm_value": null,
   "model_id": null,
   "valid_days": 1,
   "has_permanent": false,
   "duration_days": [
    1
   ],
   "all_row_keys": [
    260030
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 260030,
     "text": "紫色派对帽子",
     "field_chs_slot": 7,
     "value_chs_slot": 1801,
     "duration_days": 1,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1801,
     "scalar_type": "0x05",
     "text": "紫色派对帽子"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 39,
     "scalar_type": "0x05",
     "text": "时装挂饰，可配戴在头顶。在使用某些时装时无法佩戴。#r最长1天可用期"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 260030,
    "field_refs": [
     "player_module_appear_data.row_key=260030",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1801",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=39"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_260031",
   "row_key": 260031,
   "name": "冰雪派对帽子",
   "display_name": "冰雪派对帽子",
   "desc": "时装挂饰，可配戴在头顶。在使用某些时装时无法佩戴。#r最长1天可用期",
   "icon": "item_icon/icon_260031",
   "part_type": null,
   "part_code": 2,
   "sort_key": null,
   "charm_value": null,
   "model_id": null,
   "valid_days": 1,
   "has_permanent": false,
   "duration_days": [
    1
   ],
   "all_row_keys": [
    260031
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 260031,
     "text": "冰雪派对帽子",
     "field_chs_slot": 7,
     "value_chs_slot": 1245,
     "duration_days": 1,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1245,
     "scalar_type": "0x05",
     "text": "冰雪派对帽子"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 39,
     "scalar_type": "0x05",
     "text": "时装挂饰，可配戴在头顶。在使用某些时装时无法佩戴。#r最长1天可用期"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 260031,
    "field_refs": [
     "player_module_appear_data.row_key=260031",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1245",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=39"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_260032",
   "row_key": 260032,
   "name": "幸福派对帽子",
   "display_name": "幸福派对帽子",
   "desc": "时装挂饰，可配戴在头顶。在使用某些时装时无法佩戴。#r最长1天可用期",
   "icon": "item_icon/icon_260032",
   "part_type": null,
   "part_code": 2,
   "sort_key": null,
   "charm_value": null,
   "model_id": null,
   "valid_days": 1,
   "has_permanent": false,
   "duration_days": [
    1
   ],
   "all_row_keys": [
    260032
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 260032,
     "text": "幸福派对帽子",
     "field_chs_slot": 7,
     "value_chs_slot": 1385,
     "duration_days": 1,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1385,
     "scalar_type": "0x05",
     "text": "幸福派对帽子"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 39,
     "scalar_type": "0x05",
     "text": "时装挂饰，可配戴在头顶。在使用某些时装时无法佩戴。#r最长1天可用期"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 260032,
    "field_refs": [
     "player_module_appear_data.row_key=260032",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1385",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=39"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_260033",
   "row_key": 260033,
   "name": "西瓜派对帽子",
   "display_name": "西瓜派对帽子",
   "desc": "时装挂饰，可配戴在头顶。在使用某些时装时无法佩戴。#r最长1天可用期",
   "icon": "item_icon/icon_260033",
   "part_type": null,
   "part_code": 2,
   "sort_key": null,
   "charm_value": null,
   "model_id": null,
   "valid_days": 1,
   "has_permanent": false,
   "duration_days": [
    1
   ],
   "all_row_keys": [
    260033
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 260033,
     "text": "西瓜派对帽子",
     "field_chs_slot": 7,
     "value_chs_slot": 1959,
     "duration_days": 1,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1959,
     "scalar_type": "0x05",
     "text": "西瓜派对帽子"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 39,
     "scalar_type": "0x05",
     "text": "时装挂饰，可配戴在头顶。在使用某些时装时无法佩戴。#r最长1天可用期"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 260033,
    "field_refs": [
     "player_module_appear_data.row_key=260033",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1959",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=39"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_260034",
   "row_key": 260034,
   "name": "波点派对帽子",
   "display_name": "波点派对帽子",
   "desc": "时装挂饰，可配戴在头顶。在使用某些时装时无法佩戴。#r最长1天可用期",
   "icon": "item_icon/icon_260034",
   "part_type": null,
   "part_code": 2,
   "sort_key": null,
   "charm_value": null,
   "model_id": null,
   "valid_days": 1,
   "has_permanent": false,
   "duration_days": [
    1
   ],
   "all_row_keys": [
    260034
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 260034,
     "text": "波点派对帽子",
     "field_chs_slot": 7,
     "value_chs_slot": 1598,
     "duration_days": 1,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1598,
     "scalar_type": "0x05",
     "text": "波点派对帽子"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 39,
     "scalar_type": "0x05",
     "text": "时装挂饰，可配戴在头顶。在使用某些时装时无法佩戴。#r最长1天可用期"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 260034,
    "field_refs": [
     "player_module_appear_data.row_key=260034",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1598",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=39"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_260040",
   "row_key": 260040,
   "name": "恐怖兔子面具",
   "display_name": "恐怖兔子面具",
   "desc": "时装挂饰，可配戴在眼睛部位。在使用某些时装时无法佩戴。#r最长1天可用期",
   "icon": "item_icon/icon_260040",
   "part_type": null,
   "part_code": 1,
   "sort_key": null,
   "charm_value": null,
   "model_id": null,
   "valid_days": 1,
   "has_permanent": false,
   "duration_days": [
    1
   ],
   "all_row_keys": [
    260040
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 260040,
     "text": "恐怖兔子面具",
     "field_chs_slot": 7,
     "value_chs_slot": 1398,
     "duration_days": 1,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1398,
     "scalar_type": "0x05",
     "text": "恐怖兔子面具"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 37,
     "scalar_type": "0x05",
     "text": "时装挂饰，可配戴在眼睛部位。在使用某些时装时无法佩戴。#r最长1天可用期"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 260040,
    "field_refs": [
     "player_module_appear_data.row_key=260040",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1398",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=37"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_260041",
   "row_key": 260041,
   "name": "乐园兔子面具",
   "display_name": "乐园兔子面具",
   "desc": "时装挂饰，可配戴在眼睛部位。在使用某些时装时无法佩戴。#r最长1天可用期",
   "icon": "item_icon/icon_260041",
   "part_type": null,
   "part_code": 1,
   "sort_key": null,
   "charm_value": null,
   "model_id": null,
   "valid_days": 1,
   "has_permanent": false,
   "duration_days": [
    1
   ],
   "all_row_keys": [
    260041
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 260041,
     "text": "乐园兔子面具",
     "field_chs_slot": 7,
     "value_chs_slot": 1152,
     "duration_days": 1,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1152,
     "scalar_type": "0x05",
     "text": "乐园兔子面具"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 37,
     "scalar_type": "0x05",
     "text": "时装挂饰，可配戴在眼睛部位。在使用某些时装时无法佩戴。#r最长1天可用期"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 260041,
    "field_refs": [
     "player_module_appear_data.row_key=260041",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1152",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=37"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_260042",
   "row_key": 260042,
   "name": "兔子妹妹面具",
   "display_name": "兔子妹妹面具",
   "desc": "时装挂饰，可配戴在眼睛部位。在使用某些时装时无法佩戴。#r最长1天可用期",
   "icon": "item_icon/icon_260042",
   "part_type": null,
   "part_code": 1,
   "sort_key": null,
   "charm_value": null,
   "model_id": null,
   "valid_days": 1,
   "has_permanent": false,
   "duration_days": [
    1
   ],
   "all_row_keys": [
    260042
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 260042,
     "text": "兔子妹妹面具",
     "field_chs_slot": 7,
     "value_chs_slot": 1219,
     "duration_days": 1,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1219,
     "scalar_type": "0x05",
     "text": "兔子妹妹面具"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 37,
     "scalar_type": "0x05",
     "text": "时装挂饰，可配戴在眼睛部位。在使用某些时装时无法佩戴。#r最长1天可用期"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 260042,
    "field_refs": [
     "player_module_appear_data.row_key=260042",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1219",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=37"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_260050",
   "row_key": 260050,
   "name": "黑色舞会面具",
   "display_name": "黑色舞会面具",
   "desc": "时装挂饰，可配戴在眼睛部位。在使用某些时装时无法佩戴。#r最长1天可用期",
   "icon": "item_icon/icon_260050",
   "part_type": null,
   "part_code": 1,
   "sort_key": null,
   "charm_value": null,
   "model_id": null,
   "valid_days": 1,
   "has_permanent": false,
   "duration_days": [
    1
   ],
   "all_row_keys": [
    260050
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 260050,
     "text": "黑色舞会面具",
     "field_chs_slot": 7,
     "value_chs_slot": 2100,
     "duration_days": 1,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 2100,
     "scalar_type": "0x05",
     "text": "黑色舞会面具"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 37,
     "scalar_type": "0x05",
     "text": "时装挂饰，可配戴在眼睛部位。在使用某些时装时无法佩戴。#r最长1天可用期"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 260050,
    "field_refs": [
     "player_module_appear_data.row_key=260050",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=2100",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=37"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_260051",
   "row_key": 260051,
   "name": "金色舞会面具",
   "display_name": "金色舞会面具",
   "desc": "时装挂饰，可配戴在眼睛部位。在使用某些时装时无法佩戴。#r最长1天可用期",
   "icon": "item_icon/icon_260051",
   "part_type": null,
   "part_code": 1,
   "sort_key": null,
   "charm_value": null,
   "model_id": null,
   "valid_days": 1,
   "has_permanent": false,
   "duration_days": [
    1
   ],
   "all_row_keys": [
    260051
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 260051,
     "text": "金色舞会面具",
     "field_chs_slot": 7,
     "value_chs_slot": 2008,
     "duration_days": 1,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 2008,
     "scalar_type": "0x05",
     "text": "金色舞会面具"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 37,
     "scalar_type": "0x05",
     "text": "时装挂饰，可配戴在眼睛部位。在使用某些时装时无法佩戴。#r最长1天可用期"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 260051,
    "field_refs": [
     "player_module_appear_data.row_key=260051",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=2008",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=37"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_260052",
   "row_key": 260052,
   "name": "银色舞会面具",
   "display_name": "银色舞会面具",
   "desc": "时装挂饰，可配戴在眼睛部位。在使用某些时装时无法佩戴。#r最长1天可用期",
   "icon": "item_icon/icon_260052",
   "part_type": null,
   "part_code": 1,
   "sort_key": null,
   "charm_value": null,
   "model_id": null,
   "valid_days": 1,
   "has_permanent": false,
   "duration_days": [
    1
   ],
   "all_row_keys": [
    260052
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 260052,
     "text": "银色舞会面具",
     "field_chs_slot": 7,
     "value_chs_slot": 2009,
     "duration_days": 1,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 2009,
     "scalar_type": "0x05",
     "text": "银色舞会面具"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 37,
     "scalar_type": "0x05",
     "text": "时装挂饰，可配戴在眼睛部位。在使用某些时装时无法佩戴。#r最长1天可用期"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 260052,
    "field_refs": [
     "player_module_appear_data.row_key=260052",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=2009",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=37"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_260053",
   "row_key": 260053,
   "name": "海蓝舞会面具",
   "display_name": "海蓝舞会面具",
   "desc": "时装挂饰，可配戴在眼睛部位。在使用某些时装时无法佩戴。#r最长1天可用期",
   "icon": "item_icon/icon_260053",
   "part_type": null,
   "part_code": 1,
   "sort_key": null,
   "charm_value": null,
   "model_id": null,
   "valid_days": 1,
   "has_permanent": false,
   "duration_days": [
    1
   ],
   "all_row_keys": [
    260053
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 260053,
     "text": "海蓝舞会面具",
     "field_chs_slot": 7,
     "value_chs_slot": 1605,
     "duration_days": 1,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1605,
     "scalar_type": "0x05",
     "text": "海蓝舞会面具"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 37,
     "scalar_type": "0x05",
     "text": "时装挂饰，可配戴在眼睛部位。在使用某些时装时无法佩戴。#r最长1天可用期"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 260053,
    "field_refs": [
     "player_module_appear_data.row_key=260053",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1605",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=37"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_260054",
   "row_key": 260054,
   "name": "暗金舞会面具",
   "display_name": "暗金舞会面具",
   "desc": "时装挂饰，可配戴在眼睛部位。在使用某些时装时无法佩戴。#r最长1天可用期",
   "icon": "item_icon/icon_260054",
   "part_type": null,
   "part_code": 1,
   "sort_key": null,
   "charm_value": null,
   "model_id": null,
   "valid_days": 1,
   "has_permanent": false,
   "duration_days": [
    1
   ],
   "all_row_keys": [
    260054
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 260054,
     "text": "暗金舞会面具",
     "field_chs_slot": 7,
     "value_chs_slot": 1513,
     "duration_days": 1,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1513,
     "scalar_type": "0x05",
     "text": "暗金舞会面具"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 37,
     "scalar_type": "0x05",
     "text": "时装挂饰，可配戴在眼睛部位。在使用某些时装时无法佩戴。#r最长1天可用期"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 260054,
    "field_refs": [
     "player_module_appear_data.row_key=260054",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1513",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=37"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_260060",
   "row_key": 260060,
   "name": "国王的皇冠",
   "display_name": "国王的皇冠",
   "desc": "时装挂饰，可配戴在头顶。在使用某些时装时无法佩戴。#r最长1天可用期",
   "icon": "item_icon/icon_260060",
   "part_type": null,
   "part_code": 2,
   "sort_key": null,
   "charm_value": null,
   "model_id": null,
   "valid_days": 1,
   "has_permanent": false,
   "duration_days": [
    1
   ],
   "all_row_keys": [
    260060
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 260060,
     "text": "国王的皇冠",
     "field_chs_slot": 7,
     "value_chs_slot": 1318,
     "duration_days": 1,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1318,
     "scalar_type": "0x05",
     "text": "国王的皇冠"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 39,
     "scalar_type": "0x05",
     "text": "时装挂饰，可配戴在头顶。在使用某些时装时无法佩戴。#r最长1天可用期"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 260060,
    "field_refs": [
     "player_module_appear_data.row_key=260060",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1318",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=39"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_260070",
   "row_key": 260070,
   "name": "红蓝派对眼镜",
   "display_name": "红蓝派对眼镜",
   "desc": "时装挂饰，可配戴在眼睛部位。在使用某些时装时无法佩戴。#r最长1天可用期",
   "icon": "item_icon/icon_260070",
   "part_type": null,
   "part_code": 1,
   "sort_key": null,
   "charm_value": null,
   "model_id": null,
   "valid_days": 1,
   "has_permanent": false,
   "duration_days": [
    1
   ],
   "all_row_keys": [
    260070
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 260070,
     "text": "红蓝派对眼镜",
     "field_chs_slot": 7,
     "value_chs_slot": 1808,
     "duration_days": 1,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1808,
     "scalar_type": "0x05",
     "text": "红蓝派对眼镜"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 37,
     "scalar_type": "0x05",
     "text": "时装挂饰，可配戴在眼睛部位。在使用某些时装时无法佩戴。#r最长1天可用期"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 260070,
    "field_refs": [
     "player_module_appear_data.row_key=260070",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1808",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=37"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_260071",
   "row_key": 260071,
   "name": "兔子面具",
   "display_name": "兔子面具",
   "desc": "东京喰种联动面具，可以带在头部",
   "icon": "item_icon/icon_260071",
   "part_type": null,
   "part_code": 1,
   "sort_key": null,
   "charm_value": null,
   "model_id": null,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [],
   "all_row_keys": [
    260071
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 260071,
     "text": "兔子面具",
     "field_chs_slot": 7,
     "value_chs_slot": 1220,
     "duration_days": null,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1220,
     "scalar_type": "0x05",
     "text": "兔子面具"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 1145,
     "scalar_type": "0x05",
     "text": "东京喰种联动面具，可以带在头部"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 260071,
    "field_refs": [
     "player_module_appear_data.row_key=260071",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1220",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=1145"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_261000",
   "row_key": 261000,
   "name": "入侵者挂饰",
   "display_name": "入侵者挂饰",
   "desc": "时装挂饰，可配戴在头顶。在使用某些时装时无法佩戴。#r最长1天可用期",
   "icon": "item_icon/icon_261000",
   "part_type": null,
   "part_code": 2,
   "sort_key": null,
   "charm_value": null,
   "model_id": null,
   "valid_days": 1,
   "has_permanent": false,
   "duration_days": [
    1,
    7
   ],
   "all_row_keys": [
    261000,
    261003
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 261000,
     "text": "入侵者挂饰",
     "field_chs_slot": 7,
     "value_chs_slot": 1042,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 261003,
     "text": "入侵者挂饰",
     "field_chs_slot": 7,
     "value_chs_slot": 1042,
     "duration_days": 7,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1042,
     "scalar_type": "0x05",
     "text": "入侵者挂饰"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 39,
     "scalar_type": "0x05",
     "text": "时装挂饰，可配戴在头顶。在使用某些时装时无法佩戴。#r最长1天可用期"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 261000,
    "field_refs": [
     "player_module_appear_data.row_key=261000",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1042",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=39"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_261001",
   "row_key": 261001,
   "name": "救救我挂饰",
   "display_name": "救救我挂饰",
   "desc": "时装挂饰，可配戴在头顶。在使用某些时装时无法佩戴。#r最长1天可用期",
   "icon": "item_icon/icon_261001",
   "part_type": null,
   "part_code": 2,
   "sort_key": null,
   "charm_value": null,
   "model_id": null,
   "valid_days": 1,
   "has_permanent": false,
   "duration_days": [
    1,
    7
   ],
   "all_row_keys": [
    261001,
    261004
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 261001,
     "text": "救救我挂饰",
     "field_chs_slot": 7,
     "value_chs_slot": 1043,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 261004,
     "text": "救救我挂饰",
     "field_chs_slot": 7,
     "value_chs_slot": 1043,
     "duration_days": 7,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1043,
     "scalar_type": "0x05",
     "text": "救救我挂饰"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 39,
     "scalar_type": "0x05",
     "text": "时装挂饰，可配戴在头顶。在使用某些时装时无法佩戴。#r最长1天可用期"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 261001,
    "field_refs": [
     "player_module_appear_data.row_key=261001",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1043",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=39"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_269999",
   "row_key": 269999,
   "name": "明日世界的角色用圣诞帽",
   "display_name": "明日世界的角色用圣诞帽",
   "desc": "明日世界的角色用圣诞帽",
   "icon": "item_icon/icon_269999",
   "part_type": null,
   "part_code": 2,
   "sort_key": null,
   "charm_value": null,
   "model_id": null,
   "valid_days": 99,
   "has_permanent": false,
   "duration_days": [
    99
   ],
   "all_row_keys": [
    269999
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 269999,
     "text": "明日世界的角色用圣诞帽",
     "field_chs_slot": 7,
     "value_chs_slot": 1044,
     "duration_days": 99,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1044,
     "scalar_type": "0x05",
     "text": "明日世界的角色用圣诞帽"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 1044,
     "scalar_type": "0x05",
     "text": "明日世界的角色用圣诞帽"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 269999,
    "field_refs": [
     "player_module_appear_data.row_key=269999",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1044",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=1044"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_480670",
   "row_key": 480670,
   "name": "绮绚燃焰",
   "display_name": "绮绚燃焰",
   "desc": "#f(5)执天揽月主题面饰#n。#r舞起芳华绽，戟落震洪荒。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3395001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 3395,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    480670,
    480671,
    480672,
    480673,
    480674,
    480675,
    480676
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 480670,
     "text": "绮绚燃焰",
     "field_chs_slot": 7,
     "value_chs_slot": 984,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 480671,
     "text": "绮绚燃焰-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1828,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 480672,
     "text": "绮绚燃焰-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1830,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 480673,
     "text": "绮绚燃焰-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1831,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 480674,
     "text": "绮绚燃焰-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1832,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 480675,
     "text": "绮绚燃焰-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1827,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 480676,
     "text": "绮绚燃焰-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1829,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 984,
     "scalar_type": "0x05",
     "text": "绮绚燃焰"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 29,
     "scalar_type": "0x05",
     "text": "#f(5)执天揽月主题面饰#n。#r舞起芳华绽，戟落震洪荒。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 480670,
    "field_refs": [
     "player_module_appear_data.row_key=480670",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=984",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=29"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_480920",
   "row_key": 480920,
   "name": "绮绚燃焰-飒",
   "display_name": "绮绚燃焰-飒",
   "desc": "#f(5)执天揽月主题面饰#n。#r舞起芳华绽，戟落震洪荒。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3395002",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 3395,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    480920,
    480921,
    480922,
    480923,
    480924,
    480925,
    480926
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 480920,
     "text": "绮绚燃焰-飒",
     "field_chs_slot": 7,
     "value_chs_slot": 986,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 480921,
     "text": "绮绚燃焰-飒-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1840,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 480922,
     "text": "绮绚燃焰-飒-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1842,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 480923,
     "text": "绮绚燃焰-飒-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1843,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 480924,
     "text": "绮绚燃焰-飒-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1844,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 480925,
     "text": "绮绚燃焰-飒-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1839,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 480926,
     "text": "绮绚燃焰-飒-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1841,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 986,
     "scalar_type": "0x05",
     "text": "绮绚燃焰-飒"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 29,
     "scalar_type": "0x05",
     "text": "#f(5)执天揽月主题面饰#n。#r舞起芳华绽，戟落震洪荒。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 480920,
    "field_refs": [
     "player_module_appear_data.row_key=480920",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=986",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=29"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_481170",
   "row_key": 481170,
   "name": "绮绚燃焰-琉",
   "display_name": "绮绚燃焰-琉",
   "desc": "#f(5)执天揽月主题面饰#n。#r舞起芳华绽，戟落震洪荒。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3395003",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 3395,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    481170,
    481171,
    481172,
    481173,
    481174,
    481175,
    481176
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 481170,
     "text": "绮绚燃焰-琉",
     "field_chs_slot": 7,
     "value_chs_slot": 985,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 481171,
     "text": "绮绚燃焰-琉-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1834,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 481172,
     "text": "绮绚燃焰-琉-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1836,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 481173,
     "text": "绮绚燃焰-琉-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1837,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 481174,
     "text": "绮绚燃焰-琉-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1838,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 481175,
     "text": "绮绚燃焰-琉-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1833,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 481176,
     "text": "绮绚燃焰-琉-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1835,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 985,
     "scalar_type": "0x05",
     "text": "绮绚燃焰-琉"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 29,
     "scalar_type": "0x05",
     "text": "#f(5)执天揽月主题面饰#n。#r舞起芳华绽，戟落震洪荒。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 481170,
    "field_refs": [
     "player_module_appear_data.row_key=481170",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=985",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=29"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_481900",
   "row_key": 481900,
   "name": "不在线挂饰",
   "display_name": "不在线挂饰",
   "desc": "时装挂饰，可配戴在头顶。在使用某些时装时无法佩戴。#r最长7天可用期，重复获得会重置可用期为7天。",
   "icon": "ui/item_icon/icon_h_m_4007001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 1,
   "charm_value": 10,
   "model_id": 4007,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    261002,
    261005,
    481900,
    481901,
    481902,
    481903,
    481904,
    481905,
    481906
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 261002,
     "text": "不在线挂饰",
     "field_chs_slot": 7,
     "value_chs_slot": 38,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 261005,
     "text": "不在线挂饰",
     "field_chs_slot": 7,
     "value_chs_slot": 38,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 481900,
     "text": "不在线挂饰",
     "field_chs_slot": 7,
     "value_chs_slot": 38,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 481901,
     "text": "不在线挂饰-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1128,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 481902,
     "text": "不在线挂饰-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1130,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 481903,
     "text": "不在线挂饰-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1131,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 481904,
     "text": "不在线挂饰-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1132,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 481905,
     "text": "不在线挂饰-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1127,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 481906,
     "text": "不在线挂饰-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1129,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 38,
     "scalar_type": "0x05",
     "text": "不在线挂饰"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 919,
     "scalar_type": "0x05",
     "text": "时装挂饰，可配戴在头顶。在使用某些时装时无法佩戴。#r最长7天可用期，重复获得会重置可用期为7天。"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 481900,
    "field_refs": [
     "player_module_appear_data.row_key=481900",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=38",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=919"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_483100",
   "row_key": 483100,
   "name": "创世纪-日光",
   "display_name": "创世纪-日光",
   "desc": "#f(5)天枢龙将主题限定面饰#n。可配戴在面部的科技眼镜。在使用某些时装时无法佩戴。",
   "icon": "ui/item_icon/icon_h_m_4019001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 4019,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    483100,
    483101,
    483102,
    483103,
    483104,
    483105,
    483106
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 483100,
     "text": "创世纪-日光",
     "field_chs_slot": 7,
     "value_chs_slot": 880,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 483101,
     "text": "创世纪-日光-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1259,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 483102,
     "text": "创世纪-日光-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1261,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 483103,
     "text": "创世纪-日光-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1262,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 483104,
     "text": "创世纪-日光-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1263,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 483105,
     "text": "创世纪-日光-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1258,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 483106,
     "text": "创世纪-日光-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1260,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 880,
     "scalar_type": "0x05",
     "text": "创世纪-日光"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 35,
     "scalar_type": "0x05",
     "text": "#f(5)天枢龙将主题限定面饰#n。可配戴在面部的科技眼镜。在使用某些时装时无法佩戴。"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 483100,
    "field_refs": [
     "player_module_appear_data.row_key=483100",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=880",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=35"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_483200",
   "row_key": 483200,
   "name": "绷带侠",
   "display_name": "绷带侠",
   "desc": "#f(5)头号病人主题限定面饰#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4020001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4020,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    483200,
    483201,
    483202,
    483203,
    483204,
    483205,
    483206
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 483200,
     "text": "绷带侠",
     "field_chs_slot": 7,
     "value_chs_slot": 989,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 483201,
     "text": "绷带侠-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1858,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 483202,
     "text": "绷带侠-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1860,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 483203,
     "text": "绷带侠-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1861,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 483204,
     "text": "绷带侠-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1862,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 483205,
     "text": "绷带侠-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1857,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 483206,
     "text": "绷带侠-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1859,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 989,
     "scalar_type": "0x05",
     "text": "绷带侠"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 89,
     "scalar_type": "0x05",
     "text": "#f(5)头号病人主题限定面饰#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 483200,
    "field_refs": [
     "player_module_appear_data.row_key=483200",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=989",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=89"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_483300",
   "row_key": 483300,
   "name": "茱萸果果",
   "display_name": "茱萸果果",
   "desc": "#f(5)红果果，挂枝头。#n可配戴在头部的头饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4021001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4021,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    483300,
    483301,
    483302,
    483303,
    483304,
    483305,
    483306
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 483300,
     "text": "茱萸果果",
     "field_chs_slot": 7,
     "value_chs_slot": 996,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 483301,
     "text": "茱萸果果-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1900,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 483302,
     "text": "茱萸果果-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1902,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 483303,
     "text": "茱萸果果-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1903,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 483304,
     "text": "茱萸果果-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1904,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 483305,
     "text": "茱萸果果-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1899,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 483306,
     "text": "茱萸果果-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1901,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 996,
     "scalar_type": "0x05",
     "text": "茱萸果果"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 140,
     "scalar_type": "0x05",
     "text": "#f(5)红果果，挂枝头。#n可配戴在头部的头饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 483300,
    "field_refs": [
     "player_module_appear_data.row_key=483300",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=996",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=140"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_483350",
   "row_key": 483350,
   "name": "创世纪-冰霜",
   "display_name": "创世纪-冰霜",
   "desc": "#f(5)天枢龙将主题限定面饰#n。可配戴在面部的科技眼镜。在使用某些时装时无法佩戴。",
   "icon": "ui/item_icon/icon_h_m_4019002",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 4019,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    483350,
    483351,
    483352,
    483353,
    483354,
    483355,
    483356
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 483350,
     "text": "创世纪-冰霜",
     "field_chs_slot": 7,
     "value_chs_slot": 879,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 483351,
     "text": "创世纪-冰霜-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1253,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 483352,
     "text": "创世纪-冰霜-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1255,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 483353,
     "text": "创世纪-冰霜-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1256,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 483354,
     "text": "创世纪-冰霜-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1257,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 483355,
     "text": "创世纪-冰霜-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1252,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 483356,
     "text": "创世纪-冰霜-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1254,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 879,
     "scalar_type": "0x05",
     "text": "创世纪-冰霜"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 35,
     "scalar_type": "0x05",
     "text": "#f(5)天枢龙将主题限定面饰#n。可配戴在面部的科技眼镜。在使用某些时装时无法佩戴。"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 483350,
    "field_refs": [
     "player_module_appear_data.row_key=483350",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=879",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=35"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_483500",
   "row_key": 483500,
   "name": "炽热星星",
   "display_name": "炽热星星",
   "desc": "#f(5)佳期主题头饰#n。可配戴在头部的头饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4023001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4023,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    483500,
    483501,
    483502,
    483503,
    483504,
    483505,
    483506
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 483500,
     "text": "炽热星星",
     "field_chs_slot": 7,
     "value_chs_slot": 950,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 483501,
     "text": "炽热星星-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1643,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 483502,
     "text": "炽热星星-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1645,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 483503,
     "text": "炽热星星-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1646,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 483504,
     "text": "炽热星星-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1647,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 483505,
     "text": "炽热星星-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1642,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 483506,
     "text": "炽热星星-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1644,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 950,
     "scalar_type": "0x05",
     "text": "炽热星星"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 66,
     "scalar_type": "0x05",
     "text": "#f(5)佳期主题头饰#n。可配戴在头部的头饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 483500,
    "field_refs": [
     "player_module_appear_data.row_key=483500",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=950",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=66"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_483700",
   "row_key": 483700,
   "name": "一瞬光年",
   "display_name": "一瞬光年",
   "desc": "#f(5)仿佛置身于星辰大海，又似以光速跨越光年，探寻那些被时光掩埋的传奇秘事。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4025001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 4025,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    483700,
    483701,
    483702,
    483703,
    483704,
    483705,
    483706
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 483700,
     "text": "一瞬光年",
     "field_chs_slot": 7,
     "value_chs_slot": 855,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 483701,
     "text": "一瞬光年-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1122,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 483702,
     "text": "一瞬光年-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1124,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 483703,
     "text": "一瞬光年-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1125,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 483704,
     "text": "一瞬光年-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1126,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 483705,
     "text": "一瞬光年-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1121,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 483706,
     "text": "一瞬光年-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1123,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 855,
     "scalar_type": "0x05",
     "text": "一瞬光年"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 60,
     "scalar_type": "0x05",
     "text": "#f(5)仿佛置身于星辰大海，又似以光速跨越光年，探寻那些被时光掩埋的传奇秘事。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 483700,
    "field_refs": [
     "player_module_appear_data.row_key=483700",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=855",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=60"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_483800",
   "row_key": 483800,
   "name": "头顶花园",
   "display_name": "头顶花园",
   "desc": "#f(5)鲜花不止在枝头，更在发梢熠熠生辉。#n可配戴在头部的头饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4026001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 4026,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    483800,
    483801,
    483802,
    483803,
    483804,
    483805,
    483806
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 483800,
     "text": "头顶花园",
     "field_chs_slot": 7,
     "value_chs_slot": 895,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 483801,
     "text": "头顶花园-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1344,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 483802,
     "text": "头顶花园-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1346,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 483803,
     "text": "头顶花园-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1347,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 483804,
     "text": "头顶花园-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1348,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 483805,
     "text": "头顶花园-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1343,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 483806,
     "text": "头顶花园-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1345,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 895,
     "scalar_type": "0x05",
     "text": "头顶花园"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 157,
     "scalar_type": "0x05",
     "text": "#f(5)鲜花不止在枝头，更在发梢熠熠生辉。#n可配戴在头部的头饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 483800,
    "field_refs": [
     "player_module_appear_data.row_key=483800",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=895",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=157"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_483900",
   "row_key": 483900,
   "name": "假面狂欢",
   "display_name": "假面狂欢",
   "desc": "#f(5)周年庆限定面具赠礼：末日狂欢，假面登场！#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4027001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4027,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    483900,
    483901,
    483902,
    483903,
    483904,
    483905,
    483906
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 483900,
     "text": "假面狂欢",
     "field_chs_slot": 7,
     "value_chs_slot": 870,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 483901,
     "text": "假面狂欢-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1196,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 483902,
     "text": "假面狂欢-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1198,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 483903,
     "text": "假面狂欢-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1199,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 483904,
     "text": "假面狂欢-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1200,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 483905,
     "text": "假面狂欢-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1195,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 483906,
     "text": "假面狂欢-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1197,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 870,
     "scalar_type": "0x05",
     "text": "假面狂欢"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 79,
     "scalar_type": "0x05",
     "text": "#f(5)周年庆限定面具赠礼：末日狂欢，假面登场！#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 483900,
    "field_refs": [
     "player_module_appear_data.row_key=483900",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=870",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=79"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_484000",
   "row_key": 484000,
   "name": "好运加成",
   "display_name": "好运加成",
   "desc": "#f(5)一张可以带来好运加成的符咒，但事实是...#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4028001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4028,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    484000,
    484001,
    484002,
    484003,
    484004,
    484005,
    484006
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 484000,
     "text": "好运加成",
     "field_chs_slot": 7,
     "value_chs_slot": 896,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 484001,
     "text": "好运加成-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1350,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 484002,
     "text": "好运加成-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1352,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 484003,
     "text": "好运加成-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1353,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 484004,
     "text": "好运加成-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1354,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 484005,
     "text": "好运加成-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1349,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 484006,
     "text": "好运加成-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1351,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 896,
     "scalar_type": "0x05",
     "text": "好运加成"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 48,
     "scalar_type": "0x05",
     "text": "#f(5)一张可以带来好运加成的符咒，但事实是...#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 484000,
    "field_refs": [
     "player_module_appear_data.row_key=484000",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=896",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=48"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_484100",
   "row_key": 484100,
   "name": "入梦时分",
   "display_name": "入梦时分",
   "desc": "#f(5)绮遇回溯主题面饰，戴上它或许能进入光怪陆离的童话世界。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4029001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4029,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    484100,
    484101,
    484102,
    484103,
    484104,
    484105,
    484106
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 484100,
     "text": "入梦时分",
     "field_chs_slot": 7,
     "value_chs_slot": 874,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 484101,
     "text": "入梦时分-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1222,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 484102,
     "text": "入梦时分-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1224,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 484103,
     "text": "入梦时分-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1225,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 484104,
     "text": "入梦时分-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1226,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 484105,
     "text": "入梦时分-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1221,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 484106,
     "text": "入梦时分-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1223,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 874,
     "scalar_type": "0x05",
     "text": "入梦时分"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 142,
     "scalar_type": "0x05",
     "text": "#f(5)绮遇回溯主题面饰，戴上它或许能进入光怪陆离的童话世界。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 484100,
    "field_refs": [
     "player_module_appear_data.row_key=484100",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=874",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=142"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_484200",
   "row_key": 484200,
   "name": "雪境之光",
   "display_name": "雪境之光",
   "desc": "#f(5)在凛冽寒风中守护视野，赋予洞察雪境奥秘的锐利目光。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4030001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4030,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    484200,
    484201,
    484202,
    484203,
    484204,
    484205,
    484206
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 484200,
     "text": "雪境之光",
     "field_chs_slot": 7,
     "value_chs_slot": 1016,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 484201,
     "text": "雪境之光-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 2023,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 484202,
     "text": "雪境之光-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 2025,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 484203,
     "text": "雪境之光-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 2026,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 484204,
     "text": "雪境之光-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 2027,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 484205,
     "text": "雪境之光-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 2022,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 484206,
     "text": "雪境之光-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 2024,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1016,
     "scalar_type": "0x05",
     "text": "雪境之光"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 85,
     "scalar_type": "0x05",
     "text": "#f(5)在凛冽寒风中守护视野，赋予洞察雪境奥秘的锐利目光。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 484200,
    "field_refs": [
     "player_module_appear_data.row_key=484200",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1016",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=85"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_484250",
   "row_key": 484250,
   "name": "感染不侵",
   "display_name": "感染不侵",
   "desc": "#f(5)一张可以让人感染不侵的符咒，勇敢面对感染者吧！#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4028002",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4028,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    484250,
    484251,
    484252,
    484253,
    484254,
    484255,
    484256
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 484250,
     "text": "感染不侵",
     "field_chs_slot": 7,
     "value_chs_slot": 905,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 484251,
     "text": "感染不侵-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1406,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 484252,
     "text": "感染不侵-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1408,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 484253,
     "text": "感染不侵-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1409,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 484254,
     "text": "感染不侵-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1410,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 484255,
     "text": "感染不侵-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1405,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 484256,
     "text": "感染不侵-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1407,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 905,
     "scalar_type": "0x05",
     "text": "感染不侵"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 49,
     "scalar_type": "0x05",
     "text": "#f(5)一张可以让人感染不侵的符咒，勇敢面对感染者吧！#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 484250,
    "field_refs": [
     "player_module_appear_data.row_key=484250",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=905",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=49"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_484400",
   "row_key": 484400,
   "name": "冬青花语",
   "display_name": "冬青花语",
   "desc": "#f(5)它的花语是：爱意常青，生命坚韧。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4032001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4032,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    484400,
    484401,
    484402,
    484403,
    484404,
    484405,
    484406
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 484400,
     "text": "冬青花语",
     "field_chs_slot": 7,
     "value_chs_slot": 877,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 484401,
     "text": "冬青花语-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1240,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 484402,
     "text": "冬青花语-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1242,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 484403,
     "text": "冬青花语-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1243,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 484404,
     "text": "冬青花语-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1244,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 484405,
     "text": "冬青花语-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1239,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 484406,
     "text": "冬青花语-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1241,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 877,
     "scalar_type": "0x05",
     "text": "冬青花语"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 92,
     "scalar_type": "0x05",
     "text": "#f(5)它的花语是：爱意常青，生命坚韧。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 484400,
    "field_refs": [
     "player_module_appear_data.row_key=484400",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=877",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=92"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_484500",
   "row_key": 484500,
   "name": "心如止水",
   "display_name": "心如止水",
   "desc": "#f(5)一张令人心如止水的符咒，感觉心情真的平静下来了...#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4028003",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4028,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    484500,
    484501,
    484502,
    484503,
    484504,
    484505,
    484506
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 484500,
     "text": "心如止水",
     "field_chs_slot": 7,
     "value_chs_slot": 902,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 484501,
     "text": "心如止水-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1387,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 484502,
     "text": "心如止水-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1389,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 484503,
     "text": "心如止水-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1390,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 484504,
     "text": "心如止水-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1391,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 484505,
     "text": "心如止水-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1386,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 484506,
     "text": "心如止水-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1388,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 902,
     "scalar_type": "0x05",
     "text": "心如止水"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 47,
     "scalar_type": "0x05",
     "text": "#f(5)一张令人心如止水的符咒，感觉心情真的平静下来了...#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 484500,
    "field_refs": [
     "player_module_appear_data.row_key=484500",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=902",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=47"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_484700",
   "row_key": 484700,
   "name": "胡萝北",
   "display_name": "胡萝北",
   "desc": "#f(5)“我从来不说谎的！”#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4035001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4035,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    484700,
    484701,
    484702,
    484703,
    484704,
    484705,
    484706
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 484700,
     "text": "胡萝北",
     "field_chs_slot": 7,
     "value_chs_slot": 993,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 484701,
     "text": "胡萝北-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1882,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 484702,
     "text": "胡萝北-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1884,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 484703,
     "text": "胡萝北-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1885,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 484704,
     "text": "胡萝北-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1886,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 484705,
     "text": "胡萝北-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1881,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 484706,
     "text": "胡萝北-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1883,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 993,
     "scalar_type": "0x05",
     "text": "胡萝北"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 44,
     "scalar_type": "0x05",
     "text": "#f(5)“我从来不说谎的！”#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 484700,
    "field_refs": [
     "player_module_appear_data.row_key=484700",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=993",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=44"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_484750",
   "row_key": 484750,
   "name": "顶个雪人",
   "display_name": "顶个雪人",
   "desc": "#f(5)冬日信使，携萌而来。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4033001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4033,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    484750,
    484751,
    484752,
    484753,
    484754,
    484755,
    484756
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 484750,
     "text": "顶个雪人",
     "field_chs_slot": 7,
     "value_chs_slot": 1025,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 484751,
     "text": "顶个雪人-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 2065,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 484752,
     "text": "顶个雪人-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 2067,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 484753,
     "text": "顶个雪人-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 2068,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 484754,
     "text": "顶个雪人-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 2069,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 484755,
     "text": "顶个雪人-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 2064,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 484756,
     "text": "顶个雪人-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 2066,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1025,
     "scalar_type": "0x05",
     "text": "顶个雪人"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 73,
     "scalar_type": "0x05",
     "text": "#f(5)冬日信使，携萌而来。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 484750,
    "field_refs": [
     "player_module_appear_data.row_key=484750",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1025",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=73"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_484800",
   "row_key": 484800,
   "name": "大橘大利",
   "display_name": "大橘大利",
   "desc": "#f(5)大吉大利，情绪稳定。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4036001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4036,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    484800,
    484801,
    484802,
    484803,
    484804,
    484805,
    484806
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 484800,
     "text": "大橘大利",
     "field_chs_slot": 7,
     "value_chs_slot": 894,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 484801,
     "text": "大橘大利-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1338,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 484802,
     "text": "大橘大利-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1340,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 484803,
     "text": "大橘大利-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1341,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 484804,
     "text": "大橘大利-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1342,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 484805,
     "text": "大橘大利-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1337,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 484806,
     "text": "大橘大利-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1339,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 894,
     "scalar_type": "0x05",
     "text": "大橘大利"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 87,
     "scalar_type": "0x05",
     "text": "#f(5)大吉大利，情绪稳定。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 484800,
    "field_refs": [
     "player_module_appear_data.row_key=484800",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=894",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=87"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_484900",
   "row_key": 484900,
   "name": "晶光浮华",
   "display_name": "晶光浮华",
   "desc": "#f(5)宛如岁月长河里的璀璨遗珠，折射往昔风华。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4037001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 4037,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    484900,
    484901,
    484902,
    484903,
    484904,
    484905,
    484906
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 484900,
     "text": "晶光浮华",
     "field_chs_slot": 7,
     "value_chs_slot": 927,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 484901,
     "text": "晶光浮华-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1508,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 484902,
     "text": "晶光浮华-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1510,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 484903,
     "text": "晶光浮华-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1511,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 484904,
     "text": "晶光浮华-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1512,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 484905,
     "text": "晶光浮华-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1507,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 484906,
     "text": "晶光浮华-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1509,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 927,
     "scalar_type": "0x05",
     "text": "晶光浮华"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 93,
     "scalar_type": "0x05",
     "text": "#f(5)宛如岁月长河里的璀璨遗珠，折射往昔风华。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 484900,
    "field_refs": [
     "player_module_appear_data.row_key=484900",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=927",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=93"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_485000",
   "row_key": 485000,
   "name": "有头锦鲤",
   "display_name": "有头锦鲤",
   "desc": "#f(5)岁岁欢愉常相伴，年年有鱼绕身边。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4038001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4038,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    485000,
    485001,
    485002,
    485003,
    485004,
    485005,
    485006
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 485000,
     "text": "有头锦鲤",
     "field_chs_slot": 7,
     "value_chs_slot": 930,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 485001,
     "text": "有头锦鲤-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1521,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 485002,
     "text": "有头锦鲤-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1523,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 485003,
     "text": "有头锦鲤-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1524,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 485004,
     "text": "有头锦鲤-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1525,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 485005,
     "text": "有头锦鲤-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1520,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 485006,
     "text": "有头锦鲤-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1522,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 930,
     "scalar_type": "0x05",
     "text": "有头锦鲤"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 96,
     "scalar_type": "0x05",
     "text": "#f(5)岁岁欢愉常相伴，年年有鱼绕身边。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 485000,
    "field_refs": [
     "player_module_appear_data.row_key=485000",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=930",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=96"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_485100",
   "row_key": 485100,
   "name": "不见花",
   "display_name": "不见花",
   "desc": "#f(5)余光漏看，虽不见花；只见蝴蝶，飞舞翩翩。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4039001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 4039,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    485100,
    485101,
    485102,
    485103,
    485104,
    485105,
    485106
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 485100,
     "text": "不见花",
     "field_chs_slot": 7,
     "value_chs_slot": 859,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 485101,
     "text": "不见花-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1134,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 485102,
     "text": "不见花-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1136,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 485103,
     "text": "不见花-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1137,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 485104,
     "text": "不见花-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1138,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 485105,
     "text": "不见花-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1133,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 485106,
     "text": "不见花-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1135,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 859,
     "scalar_type": "0x05",
     "text": "不见花"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 64,
     "scalar_type": "0x05",
     "text": "#f(5)余光漏看，虽不见花；只见蝴蝶，飞舞翩翩。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 485100,
    "field_refs": [
     "player_module_appear_data.row_key=485100",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=859",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=64"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_485200",
   "row_key": 485200,
   "name": "福星高照",
   "display_name": "福星高照",
   "desc": "#f(5)福运满满，财神到家！#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4040001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4040,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    485200,
    485201,
    485202,
    485203,
    485204,
    485205,
    485206
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 485200,
     "text": "福星高照",
     "field_chs_slot": 7,
     "value_chs_slot": 976,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 485201,
     "text": "福星高照-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1783,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 485202,
     "text": "福星高照-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1785,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 485203,
     "text": "福星高照-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1786,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 485204,
     "text": "福星高照-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1787,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 485205,
     "text": "福星高照-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1782,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 485206,
     "text": "福星高照-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1784,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 976,
     "scalar_type": "0x05",
     "text": "福星高照"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 139,
     "scalar_type": "0x05",
     "text": "#f(5)福运满满，财神到家！#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 485200,
    "field_refs": [
     "player_module_appear_data.row_key=485200",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=976",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=139"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_485300",
   "row_key": 485300,
   "name": "簪好运",
   "display_name": "簪好运",
   "desc": "#f(5)新年簪花，好运当头。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4041001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4041,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    485300,
    485301,
    485302,
    485303,
    485304,
    485305,
    485306
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 485300,
     "text": "簪好运",
     "field_chs_slot": 7,
     "value_chs_slot": 978,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 485301,
     "text": "簪好运-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1795,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 485302,
     "text": "簪好运-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1797,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 485303,
     "text": "簪好运-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1798,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 485304,
     "text": "簪好运-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1799,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 485305,
     "text": "簪好运-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1794,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 485306,
     "text": "簪好运-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1796,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 978,
     "scalar_type": "0x05",
     "text": "簪好运"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 110,
     "scalar_type": "0x05",
     "text": "#f(5)新年簪花，好运当头。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 485300,
    "field_refs": [
     "player_module_appear_data.row_key=485300",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=978",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=110"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_485400",
   "row_key": 485400,
   "name": "见钱眼开",
   "display_name": "见钱眼开",
   "desc": "#f(5)“向钱看，还是向前看呢？”#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4042001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4042,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    485400,
    485401,
    485402,
    485403,
    485404,
    485405,
    485406
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 485400,
     "text": "见钱眼开",
     "field_chs_slot": 7,
     "value_chs_slot": 1007,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 485401,
     "text": "见钱眼开-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1967,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 485402,
     "text": "见钱眼开-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1969,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 485403,
     "text": "见钱眼开-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1970,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 485404,
     "text": "见钱眼开-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1971,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 485405,
     "text": "见钱眼开-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1966,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 485406,
     "text": "见钱眼开-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1968,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1007,
     "scalar_type": "0x05",
     "text": "见钱眼开"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 43,
     "scalar_type": "0x05",
     "text": "#f(5)“向钱看，还是向前看呢？”#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 485400,
    "field_refs": [
     "player_module_appear_data.row_key=485400",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1007",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=43"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_485470",
   "row_key": 485470,
   "name": "绒绒小麋鹿",
   "display_name": "绒绒小麋鹿",
   "desc": "#f(5)2023圣诞主题面饰#n。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3443001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 3443,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    485470,
    485471,
    485472,
    485473,
    485474,
    485475,
    485476
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 485470,
     "text": "绒绒小麋鹿",
     "field_chs_slot": 7,
     "value_chs_slot": 982,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 485471,
     "text": "绒绒小麋鹿-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1816,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 485472,
     "text": "绒绒小麋鹿-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1818,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 485473,
     "text": "绒绒小麋鹿-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1819,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 485474,
     "text": "绒绒小麋鹿-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1820,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 485475,
     "text": "绒绒小麋鹿-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1815,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 485476,
     "text": "绒绒小麋鹿-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1817,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 982,
     "scalar_type": "0x05",
     "text": "绒绒小麋鹿"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 31,
     "scalar_type": "0x05",
     "text": "#f(5)2023圣诞主题面饰#n。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 485470,
    "field_refs": [
     "player_module_appear_data.row_key=485470",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=982",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=31"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_485500",
   "row_key": 485500,
   "name": "一勺甜",
   "display_name": "一勺甜",
   "desc": "#f(5)元宵甜甜，快乐绵绵。吃上一口，日子甜甜。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4043001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4043,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    485500,
    485501,
    485502,
    485503,
    485504,
    485505,
    485506
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 485500,
     "text": "一勺甜",
     "field_chs_slot": 7,
     "value_chs_slot": 852,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 485501,
     "text": "一勺甜-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1104,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 485502,
     "text": "一勺甜-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1106,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 485503,
     "text": "一勺甜-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1107,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 485504,
     "text": "一勺甜-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1108,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 485505,
     "text": "一勺甜-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1103,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 485506,
     "text": "一勺甜-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1105,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 852,
     "scalar_type": "0x05",
     "text": "一勺甜"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 70,
     "scalar_type": "0x05",
     "text": "#f(5)元宵甜甜，快乐绵绵。吃上一口，日子甜甜。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 485500,
    "field_refs": [
     "player_module_appear_data.row_key=485500",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=852",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=70"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_485570",
   "row_key": 485570,
   "name": "萤绿小麋鹿",
   "display_name": "萤绿小麋鹿",
   "desc": "#f(5)2023圣诞主题面饰#n。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3444001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 3444,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    485570,
    485571,
    485572,
    485573,
    485574,
    485575,
    485576
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 485570,
     "text": "萤绿小麋鹿",
     "field_chs_slot": 7,
     "value_chs_slot": 999,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 485571,
     "text": "萤绿小麋鹿-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1918,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 485572,
     "text": "萤绿小麋鹿-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1920,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 485573,
     "text": "萤绿小麋鹿-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1921,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 485574,
     "text": "萤绿小麋鹿-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1922,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 485575,
     "text": "萤绿小麋鹿-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1917,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 485576,
     "text": "萤绿小麋鹿-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1919,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 999,
     "scalar_type": "0x05",
     "text": "萤绿小麋鹿"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 31,
     "scalar_type": "0x05",
     "text": "#f(5)2023圣诞主题面饰#n。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 485570,
    "field_refs": [
     "player_module_appear_data.row_key=485570",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=999",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=31"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_485700",
   "row_key": 485700,
   "name": "绒绒猫耳",
   "display_name": "绒绒猫耳",
   "desc": "#f(5)毛茸茸的白耳朵，很难忍住不揉一下。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4045001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4045,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    485700,
    485701,
    485702,
    485703,
    485704,
    485705,
    485706
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 485700,
     "text": "绒绒猫耳",
     "field_chs_slot": 7,
     "value_chs_slot": 983,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 485701,
     "text": "绒绒猫耳-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1822,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 485702,
     "text": "绒绒猫耳-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1824,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 485703,
     "text": "绒绒猫耳-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1825,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 485704,
     "text": "绒绒猫耳-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1826,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 485705,
     "text": "绒绒猫耳-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1821,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 485706,
     "text": "绒绒猫耳-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1823,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 983,
     "scalar_type": "0x05",
     "text": "绒绒猫耳"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 121,
     "scalar_type": "0x05",
     "text": "#f(5)毛茸茸的白耳朵，很难忍住不揉一下。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 485700,
    "field_refs": [
     "player_module_appear_data.row_key=485700",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=983",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=121"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_485800",
   "row_key": 485800,
   "name": "檐上华",
   "display_name": "檐上华",
   "desc": "#f(5)谒冬不争春色，自有琼华。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4046001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 4046,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    485800,
    485801,
    485802,
    485803,
    485804,
    485805,
    485806
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 485800,
     "text": "檐上华",
     "field_chs_slot": 7,
     "value_chs_slot": 938,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 485801,
     "text": "檐上华-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1569,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 485802,
     "text": "檐上华-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1571,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 485803,
     "text": "檐上华-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1572,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 485804,
     "text": "檐上华-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1573,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 485805,
     "text": "檐上华-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1568,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 485806,
     "text": "檐上华-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1570,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 938,
     "scalar_type": "0x05",
     "text": "檐上华"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 147,
     "scalar_type": "0x05",
     "text": "#f(5)谒冬不争春色，自有琼华。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 485800,
    "field_refs": [
     "player_module_appear_data.row_key=485800",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=938",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=147"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_485870",
   "row_key": 485870,
   "name": "新年龙龙角",
   "display_name": "新年龙龙角",
   "desc": "#f(5)2024新年主题面饰#n。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3447001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 3447,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    485870,
    485871,
    485872,
    485873,
    485874,
    485875,
    485876
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 485870,
     "text": "新年龙龙角",
     "field_chs_slot": 7,
     "value_chs_slot": 915,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 485871,
     "text": "新年龙龙角-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1448,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 485872,
     "text": "新年龙龙角-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1450,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 485873,
     "text": "新年龙龙角-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1451,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 485874,
     "text": "新年龙龙角-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1452,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 485875,
     "text": "新年龙龙角-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1447,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 485876,
     "text": "新年龙龙角-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1449,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 915,
     "scalar_type": "0x05",
     "text": "新年龙龙角"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 34,
     "scalar_type": "0x05",
     "text": "#f(5)2024新年主题面饰#n。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 485870,
    "field_refs": [
     "player_module_appear_data.row_key=485870",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=915",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=34"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_485900",
   "row_key": 485900,
   "name": "要开花芽",
   "display_name": "要开花芽",
   "desc": "#f(5)仿佛有晨露顺着花芽的弧线滑落#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4047001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4047,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    485900,
    485901,
    485902,
    485903,
    485904,
    485905,
    485906
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 485900,
     "text": "要开花芽",
     "field_chs_slot": 7,
     "value_chs_slot": 1006,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 485901,
     "text": "要开花芽-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1961,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 485902,
     "text": "要开花芽-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1963,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 485903,
     "text": "要开花芽-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1964,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 485904,
     "text": "要开花芽-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1965,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 485905,
     "text": "要开花芽-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1960,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 485906,
     "text": "要开花芽-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1962,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1006,
     "scalar_type": "0x05",
     "text": "要开花芽"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 59,
     "scalar_type": "0x05",
     "text": "#f(5)仿佛有晨露顺着花芽的弧线滑落#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 485900,
    "field_refs": [
     "player_module_appear_data.row_key=485900",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1006",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=59"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_485970",
   "row_key": 485970,
   "name": "星年龙龙尾",
   "display_name": "星年龙龙尾",
   "desc": "#f(5)2024新年主题面饰#n。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3448001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 3448,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    485970,
    485971,
    485972,
    485973,
    485974,
    485975,
    485976
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 485970,
     "text": "星年龙龙尾",
     "field_chs_slot": 7,
     "value_chs_slot": 922,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 485971,
     "text": "星年龙龙尾-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1484,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 485972,
     "text": "星年龙龙尾-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1486,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 485973,
     "text": "星年龙龙尾-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1487,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 485974,
     "text": "星年龙龙尾-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1488,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 485975,
     "text": "星年龙龙尾-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1483,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 485976,
     "text": "星年龙龙尾-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1485,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 922,
     "scalar_type": "0x05",
     "text": "星年龙龙尾"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 34,
     "scalar_type": "0x05",
     "text": "#f(5)2024新年主题面饰#n。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 485970,
    "field_refs": [
     "player_module_appear_data.row_key=485970",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=922",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=34"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_486000",
   "row_key": 486000,
   "name": "面具：惧",
   "display_name": "面具：惧",
   "desc": "#f(5)仿佛能够听到面具的低语，诉说着祈愿。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4048001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4048,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    486000,
    486001,
    486002,
    486003,
    486004,
    486005,
    486006
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 486000,
     "text": "面具：惧",
     "field_chs_slot": 7,
     "value_chs_slot": 1022,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 486001,
     "text": "面具：惧-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 2047,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 486002,
     "text": "面具：惧-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 2049,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 486003,
     "text": "面具：惧-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 2050,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 486004,
     "text": "面具：惧-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 2051,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 486005,
     "text": "面具：惧-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 2046,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 486006,
     "text": "面具：惧-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 2048,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1022,
     "scalar_type": "0x05",
     "text": "面具：惧"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 61,
     "scalar_type": "0x05",
     "text": "#f(5)仿佛能够听到面具的低语，诉说着祈愿。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 486000,
    "field_refs": [
     "player_module_appear_data.row_key=486000",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1022",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=61"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_486100",
   "row_key": 486100,
   "name": "面具：嗔",
   "display_name": "面具：嗔",
   "desc": "#f(5)带上面具，变如同化身神明，欲要起舞。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4049001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4049,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    486100,
    486101,
    486102,
    486103,
    486104,
    486105,
    486106
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 486100,
     "text": "面具：嗔",
     "field_chs_slot": 7,
     "value_chs_slot": 1021,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 486101,
     "text": "面具：嗔-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 2041,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 486102,
     "text": "面具：嗔-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 2043,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 486103,
     "text": "面具：嗔-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 2044,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 486104,
     "text": "面具：嗔-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 2045,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 486105,
     "text": "面具：嗔-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 2040,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 486106,
     "text": "面具：嗔-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 2042,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1021,
     "scalar_type": "0x05",
     "text": "面具：嗔"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 97,
     "scalar_type": "0x05",
     "text": "#f(5)带上面具，变如同化身神明，欲要起舞。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 486100,
    "field_refs": [
     "player_module_appear_data.row_key=486100",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1021",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=97"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_486200",
   "row_key": 486200,
   "name": "面具：贪",
   "display_name": "面具：贪",
   "desc": "#f(5)在鹭水村的萤火映照下，神秘而生动。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4050001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4050,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    486200,
    486201,
    486202,
    486203,
    486204,
    486205,
    486206
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 486200,
     "text": "面具：贪",
     "field_chs_slot": 7,
     "value_chs_slot": 1023,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 486201,
     "text": "面具：贪-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 2053,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 486202,
     "text": "面具：贪-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 2055,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 486203,
     "text": "面具：贪-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 2056,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 486204,
     "text": "面具：贪-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 2057,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 486205,
     "text": "面具：贪-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 2052,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 486206,
     "text": "面具：贪-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 2054,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1023,
     "scalar_type": "0x05",
     "text": "面具：贪"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 86,
     "scalar_type": "0x05",
     "text": "#f(5)在鹭水村的萤火映照下，神秘而生动。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 486200,
    "field_refs": [
     "player_module_appear_data.row_key=486200",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1023",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=86"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_486270",
   "row_key": 486270,
   "name": "狗狗的爱",
   "display_name": "狗狗的爱",
   "desc": "#f(5)2024情人节主题面饰#n。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3451001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 3451,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    486270,
    486271,
    486272,
    486273,
    486274,
    486275,
    486276
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 486270,
     "text": "狗狗的爱",
     "field_chs_slot": 7,
     "value_chs_slot": 955,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 486271,
     "text": "狗狗的爱-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1674,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 486272,
     "text": "狗狗的爱-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1676,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 486273,
     "text": "狗狗的爱-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1677,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 486274,
     "text": "狗狗的爱-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1678,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 486275,
     "text": "狗狗的爱-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1673,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 486276,
     "text": "狗狗的爱-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1675,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 955,
     "scalar_type": "0x05",
     "text": "狗狗的爱"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 33,
     "scalar_type": "0x05",
     "text": "#f(5)2024情人节主题面饰#n。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 486270,
    "field_refs": [
     "player_module_appear_data.row_key=486270",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=955",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=33"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_486300",
   "row_key": 486300,
   "name": "藕想开了",
   "display_name": "藕想开了",
   "desc": "#f(5)莲花开了，通常是藕想开了。「明日之后×非人哉」联动限定外观。#n在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4051001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4051,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    486300,
    486301,
    486302,
    486303,
    486304,
    486305,
    486306
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 486300,
     "text": "藕想开了",
     "field_chs_slot": 7,
     "value_chs_slot": 1002,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 486301,
     "text": "藕想开了-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1936,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 486302,
     "text": "藕想开了-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1938,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 486303,
     "text": "藕想开了-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1939,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 486304,
     "text": "藕想开了-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1940,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 486305,
     "text": "藕想开了-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1935,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 486306,
     "text": "藕想开了-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1937,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1002,
     "scalar_type": "0x05",
     "text": "藕想开了"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 144,
     "scalar_type": "0x05",
     "text": "#f(5)莲花开了，通常是藕想开了。「明日之后×非人哉」联动限定外观。#n在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 486300,
    "field_refs": [
     "player_module_appear_data.row_key=486300",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1002",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=144"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_486370",
   "row_key": 486370,
   "name": "猫猫的爱",
   "display_name": "猫猫的爱",
   "desc": "#f(5)2024情人节主题面饰#n。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3452001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 3452,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    486370,
    486371,
    486372,
    486373,
    486374,
    486375,
    486376
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 486370,
     "text": "猫猫的爱",
     "field_chs_slot": 7,
     "value_chs_slot": 958,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 486371,
     "text": "猫猫的爱-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1692,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 486372,
     "text": "猫猫的爱-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1694,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 486373,
     "text": "猫猫的爱-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1695,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 486374,
     "text": "猫猫的爱-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1696,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 486375,
     "text": "猫猫的爱-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1691,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 486376,
     "text": "猫猫的爱-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1693,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 958,
     "scalar_type": "0x05",
     "text": "猫猫的爱"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 33,
     "scalar_type": "0x05",
     "text": "#f(5)2024情人节主题面饰#n。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 486370,
    "field_refs": [
     "player_module_appear_data.row_key=486370",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=958",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=33"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_486500",
   "row_key": 486500,
   "name": "樱落三千",
   "display_name": "樱落三千",
   "desc": "#f(5)早春藏匿于发间的樱花，光芒中流转着关于神仙们的小小传说。「明日之后×非人哉」联动限定外观。#n在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4053001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 4053,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    486500,
    486501,
    486502,
    486503,
    486504,
    486505,
    486506
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 486500,
     "text": "樱落三千",
     "field_chs_slot": 7,
     "value_chs_slot": 937,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 486501,
     "text": "樱落三千-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1563,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 486502,
     "text": "樱落三千-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1565,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 486503,
     "text": "樱落三千-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1566,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 486504,
     "text": "樱落三千-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1567,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 486505,
     "text": "樱落三千-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1562,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 486506,
     "text": "樱落三千-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1564,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 937,
     "scalar_type": "0x05",
     "text": "樱落三千"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 111,
     "scalar_type": "0x05",
     "text": "#f(5)早春藏匿于发间的樱花，光芒中流转着关于神仙们的小小传说。「明日之后×非人哉」联动限定外观。#n在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 486500,
    "field_refs": [
     "player_module_appear_data.row_key=486500",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=937",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=111"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_486600",
   "row_key": 486600,
   "name": "叩灵",
   "display_name": "叩灵",
   "desc": "#f(5)月光凝成银铃，垂落眉心。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4054001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4054,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    486600,
    486601,
    486602,
    486603,
    486604,
    486605,
    486606
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 486600,
     "text": "叩灵",
     "field_chs_slot": 7,
     "value_chs_slot": 884,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 486601,
     "text": "叩灵-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1283,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 486602,
     "text": "叩灵-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1285,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 486603,
     "text": "叩灵-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1286,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 486604,
     "text": "叩灵-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1287,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 486605,
     "text": "叩灵-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1282,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 486606,
     "text": "叩灵-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1284,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 884,
     "scalar_type": "0x05",
     "text": "叩灵"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 113,
     "scalar_type": "0x05",
     "text": "#f(5)月光凝成银铃，垂落眉心。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 486600,
    "field_refs": [
     "player_module_appear_data.row_key=486600",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=884",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=113"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_486700",
   "row_key": 486700,
   "name": "翩如梦·火",
   "display_name": "翩如梦·火",
   "desc": "#f(5)眼尾跃动的火焰红蝶，每一次目光流转都带起滚烫热浪。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4055001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4055,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    486700,
    486701,
    486702,
    486703,
    486704,
    486705,
    486706
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 486700,
     "text": "翩如梦·火",
     "field_chs_slot": 7,
     "value_chs_slot": 990,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 486701,
     "text": "翩如梦·火-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1864,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 486702,
     "text": "翩如梦·火-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1866,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 486703,
     "text": "翩如梦·火-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1867,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 486704,
     "text": "翩如梦·火-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1868,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 486705,
     "text": "翩如梦·火-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1863,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 486706,
     "text": "翩如梦·火-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1865,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 990,
     "scalar_type": "0x05",
     "text": "翩如梦·火"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 138,
     "scalar_type": "0x05",
     "text": "#f(5)眼尾跃动的火焰红蝶，每一次目光流转都带起滚烫热浪。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 486700,
    "field_refs": [
     "player_module_appear_data.row_key=486700",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=990",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=138"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_486950",
   "row_key": 486950,
   "name": "翩如梦·黛",
   "display_name": "翩如梦·黛",
   "desc": "#f(5)柔粉蝶翼轻覆眼睫，仿佛春日樱花随风吻过眼眸。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4055002",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4055,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    486950,
    486951,
    486952,
    486953,
    486954,
    486955,
    486956
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 486950,
     "text": "翩如梦·黛",
     "field_chs_slot": 7,
     "value_chs_slot": 992,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 486951,
     "text": "翩如梦·黛-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1876,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 486952,
     "text": "翩如梦·黛-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1878,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 486953,
     "text": "翩如梦·黛-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1879,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 486954,
     "text": "翩如梦·黛-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1880,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 486955,
     "text": "翩如梦·黛-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1875,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 486956,
     "text": "翩如梦·黛-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1877,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 992,
     "scalar_type": "0x05",
     "text": "翩如梦·黛"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 119,
     "scalar_type": "0x05",
     "text": "#f(5)柔粉蝶翼轻覆眼睫，仿佛春日樱花随风吻过眼眸。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 486950,
    "field_refs": [
     "player_module_appear_data.row_key=486950",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=992",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=119"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_487000",
   "row_key": 487000,
   "name": "枝繁之环",
   "display_name": "枝繁之环",
   "desc": "#f(5)以枝为冕，冠承四季荣华，叶脉流转处，生生不息的流光自年轮深处漫溢。#n在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4058001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 4058,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    487000,
    487001,
    487002,
    487003,
    487004,
    487005,
    487006
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 487000,
     "text": "枝繁之环",
     "field_chs_slot": 7,
     "value_chs_slot": 932,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 487001,
     "text": "枝繁之环-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1533,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 487002,
     "text": "枝繁之环-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1535,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 487003,
     "text": "枝繁之环-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1536,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 487004,
     "text": "枝繁之环-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1537,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 487005,
     "text": "枝繁之环-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1532,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 487006,
     "text": "枝繁之环-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1534,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 932,
     "scalar_type": "0x05",
     "text": "枝繁之环"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 56,
     "scalar_type": "0x05",
     "text": "#f(5)以枝为冕，冠承四季荣华，叶脉流转处，生生不息的流光自年轮深处漫溢。#n在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 487000,
    "field_refs": [
     "player_module_appear_data.row_key=487000",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=932",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=56"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_487100",
   "row_key": 487100,
   "name": "九重紫",
   "display_name": "九重紫",
   "desc": "#f(5)以花为眼，见天地；以藤为魂，锁光阴。  #n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4059001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 4059,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    487100,
    487101,
    487102,
    487103,
    487104,
    487105,
    487106
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 487100,
     "text": "九重紫",
     "field_chs_slot": 7,
     "value_chs_slot": 862,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 487101,
     "text": "九重紫-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1154,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 487102,
     "text": "九重紫-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1156,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 487103,
     "text": "九重紫-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1157,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 487104,
     "text": "九重紫-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1158,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 487105,
     "text": "九重紫-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1153,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 487106,
     "text": "九重紫-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1155,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 862,
     "scalar_type": "0x05",
     "text": "九重紫"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 57,
     "scalar_type": "0x05",
     "text": "#f(5)以花为眼，见天地；以藤为魂，锁光阴。  #n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 487100,
    "field_refs": [
     "player_module_appear_data.row_key=487100",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=862",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=57"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_487200",
   "row_key": 487200,
   "name": "翩如梦·靛",
   "display_name": "翩如梦·靛",
   "desc": "#f(5)冰蓝蝶影缀于眉下，凝住一抹星空落入人间的清透。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4055003",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4055,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    487200,
    487201,
    487202,
    487203,
    487204,
    487205,
    487206
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 487200,
     "text": "翩如梦·靛",
     "field_chs_slot": 7,
     "value_chs_slot": 991,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 487201,
     "text": "翩如梦·靛-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1870,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 487202,
     "text": "翩如梦·靛-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1872,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 487203,
     "text": "翩如梦·靛-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1873,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 487204,
     "text": "翩如梦·靛-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1874,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 487205,
     "text": "翩如梦·靛-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1869,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 487206,
     "text": "翩如梦·靛-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1871,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 991,
     "scalar_type": "0x05",
     "text": "翩如梦·靛"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 74,
     "scalar_type": "0x05",
     "text": "#f(5)冰蓝蝶影缀于眉下，凝住一抹星空落入人间的清透。#n可配戴在头部的面饰。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 487200,
    "field_refs": [
     "player_module_appear_data.row_key=487200",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=991",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=74"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_487400",
   "row_key": 487400,
   "name": "兔兔甜巧",
   "display_name": "兔兔甜巧",
   "desc": "#f(5)鼻子颤颤，焦糖脆片缀满心尖尖。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4062001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4062,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    487400,
    487401,
    487402,
    487403,
    487404,
    487405,
    487406
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 487400,
     "text": "兔兔甜巧",
     "field_chs_slot": 7,
     "value_chs_slot": 873,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 487401,
     "text": "兔兔甜巧-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1214,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 487402,
     "text": "兔兔甜巧-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1216,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 487403,
     "text": "兔兔甜巧-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1217,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 487404,
     "text": "兔兔甜巧-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1218,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 487405,
     "text": "兔兔甜巧-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1213,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 487406,
     "text": "兔兔甜巧-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1215,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 873,
     "scalar_type": "0x05",
     "text": "兔兔甜巧"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 158,
     "scalar_type": "0x05",
     "text": "#f(5)鼻子颤颤，焦糖脆片缀满心尖尖。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 487400,
    "field_refs": [
     "player_module_appear_data.row_key=487400",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=873",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=158"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_487450",
   "row_key": 487450,
   "name": "鼠鼠慕斯",
   "display_name": "鼠鼠慕斯",
   "desc": "#f(5)抖抖耳朵，撒落甜甜的奶油糖霜。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4060001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4060,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    487450,
    487451,
    487452,
    487453,
    487454,
    487455,
    487456
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 487450,
     "text": "鼠鼠慕斯",
     "field_chs_slot": 7,
     "value_chs_slot": 1031,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 487451,
     "text": "鼠鼠慕斯-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 2102,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 487452,
     "text": "鼠鼠慕斯-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 2104,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 487453,
     "text": "鼠鼠慕斯-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 2105,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 487454,
     "text": "鼠鼠慕斯-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 2106,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 487455,
     "text": "鼠鼠慕斯-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 2101,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 487456,
     "text": "鼠鼠慕斯-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 2103,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1031,
     "scalar_type": "0x05",
     "text": "鼠鼠慕斯"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 108,
     "scalar_type": "0x05",
     "text": "#f(5)抖抖耳朵，撒落甜甜的奶油糖霜。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 487450,
    "field_refs": [
     "player_module_appear_data.row_key=487450",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1031",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=108"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_487500",
   "row_key": 487500,
   "name": "玫瑰契约",
   "display_name": "玫瑰契约",
   "desc": "#f(5)以骨为蕊，以血为瓣，轻覆眉眼间，将温柔碾碎成暗藏杀机的锋芒。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4063001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 4063,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    487500,
    487501,
    487502,
    487503,
    487504,
    487505,
    487506
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 487500,
     "text": "玫瑰契约",
     "field_chs_slot": 7,
     "value_chs_slot": 961,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 487501,
     "text": "玫瑰契约-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1710,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 487502,
     "text": "玫瑰契约-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1712,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 487503,
     "text": "玫瑰契约-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1713,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 487504,
     "text": "玫瑰契约-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1714,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 487505,
     "text": "玫瑰契约-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1709,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 487506,
     "text": "玫瑰契约-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1711,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 961,
     "scalar_type": "0x05",
     "text": "玫瑰契约"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 58,
     "scalar_type": "0x05",
     "text": "#f(5)以骨为蕊，以血为瓣，轻覆眉眼间，将温柔碾碎成暗藏杀机的锋芒。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 487500,
    "field_refs": [
     "player_module_appear_data.row_key=487500",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=961",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=58"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_487700",
   "row_key": 487700,
   "name": "坨坨彩虹",
   "display_name": "坨坨彩虹",
   "desc": "#f(5)极具弹性的彩虹小团子，不要轻易压扁它哦！（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4065001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4065,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    487700,
    487701,
    487702,
    487703,
    487704,
    487705,
    487706
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 487700,
     "text": "坨坨彩虹",
     "field_chs_slot": 7,
     "value_chs_slot": 891,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 487701,
     "text": "坨坨彩虹-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1320,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 487702,
     "text": "坨坨彩虹-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1322,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 487703,
     "text": "坨坨彩虹-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1323,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 487704,
     "text": "坨坨彩虹-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1324,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 487705,
     "text": "坨坨彩虹-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1319,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 487706,
     "text": "坨坨彩虹-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1321,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 891,
     "scalar_type": "0x05",
     "text": "坨坨彩虹"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 118,
     "scalar_type": "0x05",
     "text": "#f(5)极具弹性的彩虹小团子，不要轻易压扁它哦！（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 487700,
    "field_refs": [
     "player_module_appear_data.row_key=487700",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=891",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=118"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_487800",
   "row_key": 487800,
   "name": "蝉音",
   "display_name": "蝉音",
   "desc": "#f(5)蝉翼织羽，凝梦为音。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4066001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4066,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    487800,
    487801,
    487802,
    487803,
    487804,
    487805,
    487806
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 487800,
     "text": "蝉音",
     "field_chs_slot": 7,
     "value_chs_slot": 1003,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 487801,
     "text": "蝉音-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1942,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 487802,
     "text": "蝉音-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1944,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 487803,
     "text": "蝉音-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1945,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 487804,
     "text": "蝉音-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1946,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 487805,
     "text": "蝉音-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1941,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 487806,
     "text": "蝉音-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1943,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1003,
     "scalar_type": "0x05",
     "text": "蝉音"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 145,
     "scalar_type": "0x05",
     "text": "#f(5)蝉翼织羽，凝梦为音。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 487800,
    "field_refs": [
     "player_module_appear_data.row_key=487800",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1003",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=145"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_487900",
   "row_key": 487900,
   "name": "冒汗了",
   "display_name": "冒汗了",
   "desc": "#f(5)真是让人汗颜呢。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4067001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4067,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    487900,
    487901,
    487902,
    487903,
    487904,
    487905,
    487906
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 487900,
     "text": "冒汗了",
     "field_chs_slot": 7,
     "value_chs_slot": 875,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 487901,
     "text": "冒汗了-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1228,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 487902,
     "text": "冒汗了-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1230,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 487903,
     "text": "冒汗了-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1231,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 487904,
     "text": "冒汗了-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1232,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 487905,
     "text": "冒汗了-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1227,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 487906,
     "text": "冒汗了-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1229,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 875,
     "scalar_type": "0x05",
     "text": "冒汗了"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 137,
     "scalar_type": "0x05",
     "text": "#f(5)真是让人汗颜呢。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 487900,
    "field_refs": [
     "player_module_appear_data.row_key=487900",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=875",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=137"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_488000",
   "row_key": 488000,
   "name": "生气气",
   "display_name": "生气气",
   "desc": "#f(5)好生气哦，但还要保持微笑。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4068001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4068,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    488000,
    488001,
    488002,
    488003,
    488004,
    488005,
    488006
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 488000,
     "text": "生气气",
     "field_chs_slot": 7,
     "value_chs_slot": 967,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 488001,
     "text": "生气气-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1734,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 488002,
     "text": "生气气-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1736,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 488003,
     "text": "生气气-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1737,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 488004,
     "text": "生气气-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1738,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 488005,
     "text": "生气气-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1733,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 488006,
     "text": "生气气-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1735,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 967,
     "scalar_type": "0x05",
     "text": "生气气"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 90,
     "scalar_type": "0x05",
     "text": "#f(5)好生气哦，但还要保持微笑。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 488000,
    "field_refs": [
     "player_module_appear_data.row_key=488000",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=967",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=90"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_488100",
   "row_key": 488100,
   "name": "无语子",
   "display_name": "无语子",
   "desc": "#f(5)令人无话可说。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4069001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4069,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    488100,
    488101,
    488102,
    488103,
    488104,
    488105,
    488106
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 488100,
     "text": "无语子",
     "field_chs_slot": 7,
     "value_chs_slot": 916,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 488101,
     "text": "无语子-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1454,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 488102,
     "text": "无语子-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1456,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 488103,
     "text": "无语子-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1457,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 488104,
     "text": "无语子-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1458,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 488105,
     "text": "无语子-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1453,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 488106,
     "text": "无语子-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1455,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 916,
     "scalar_type": "0x05",
     "text": "无语子"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 55,
     "scalar_type": "0x05",
     "text": "#f(5)令人无话可说。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 488100,
    "field_refs": [
     "player_module_appear_data.row_key=488100",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=916",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=55"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_488200",
   "row_key": 488200,
   "name": "蹦跳音符",
   "display_name": "蹦跳音符",
   "desc": "#f(5)音符在帽尖上蹦跶，童话在梦里跃迁。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4070001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4070,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    488200,
    488201,
    488202,
    488203,
    488204,
    488205,
    488206
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 488200,
     "text": "蹦跳音符",
     "field_chs_slot": 7,
     "value_chs_slot": 1010,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 488201,
     "text": "蹦跳音符-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1985,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 488202,
     "text": "蹦跳音符-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1987,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 488203,
     "text": "蹦跳音符-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1988,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 488204,
     "text": "蹦跳音符-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1989,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 488205,
     "text": "蹦跳音符-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1984,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 488206,
     "text": "蹦跳音符-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1986,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1010,
     "scalar_type": "0x05",
     "text": "蹦跳音符"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 153,
     "scalar_type": "0x05",
     "text": "#f(5)音符在帽尖上蹦跶，童话在梦里跃迁。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 488200,
    "field_refs": [
     "player_module_appear_data.row_key=488200",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1010",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=153"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_488300",
   "row_key": 488300,
   "name": "海风为帆",
   "display_name": "海风为帆",
   "desc": "#f(5)成为海浪之上，永远勇敢前行的风帆吧！在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4071001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4071,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    488300,
    488301,
    488302,
    488303,
    488304,
    488305,
    488306
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 488300,
     "text": "海风为帆",
     "field_chs_slot": 7,
     "value_chs_slot": 944,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 488301,
     "text": "海风为帆-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1607,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 488302,
     "text": "海风为帆-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1609,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 488303,
     "text": "海风为帆-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1610,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 488304,
     "text": "海风为帆-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1611,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 488305,
     "text": "海风为帆-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1606,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 488306,
     "text": "海风为帆-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1608,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 944,
     "scalar_type": "0x05",
     "text": "海风为帆"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 101,
     "scalar_type": "0x05",
     "text": "#f(5)成为海浪之上，永远勇敢前行的风帆吧！在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 488300,
    "field_refs": [
     "player_module_appear_data.row_key=488300",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=944",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=101"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_488370",
   "row_key": 488370,
   "name": "戴柳",
   "display_name": "戴柳",
   "desc": "#f(5)把春天戴在头上！#n。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3472001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 3472,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    488370,
    488371,
    488372,
    488373,
    488374,
    488375,
    488376
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 488370,
     "text": "戴柳",
     "field_chs_slot": 7,
     "value_chs_slot": 908,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 488371,
     "text": "戴柳-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1418,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 488372,
     "text": "戴柳-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1420,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 488373,
     "text": "戴柳-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1421,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 488374,
     "text": "戴柳-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1422,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 488375,
     "text": "戴柳-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1417,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 488376,
     "text": "戴柳-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1419,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 908,
     "scalar_type": "0x05",
     "text": "戴柳"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 106,
     "scalar_type": "0x05",
     "text": "#f(5)把春天戴在头上！#n。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 488370,
    "field_refs": [
     "player_module_appear_data.row_key=488370",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=908",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=106"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_488500",
   "row_key": 488500,
   "name": "黑白方格",
   "display_name": "黑白方格",
   "desc": "#f(5)挥动旗帜，冲向胜利的终点！在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4073001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4073,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    488500,
    488501,
    488502,
    488503,
    488504,
    488505,
    488506
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 488500,
     "text": "黑白方格",
     "field_chs_slot": 7,
     "value_chs_slot": 1030,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 488501,
     "text": "黑白方格-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 2095,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 488502,
     "text": "黑白方格-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 2097,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 488503,
     "text": "黑白方格-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 2098,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 488504,
     "text": "黑白方格-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 2099,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 488505,
     "text": "黑白方格-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 2094,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 488506,
     "text": "黑白方格-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 2096,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1030,
     "scalar_type": "0x05",
     "text": "黑白方格"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 109,
     "scalar_type": "0x05",
     "text": "#f(5)挥动旗帜，冲向胜利的终点！在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 488500,
    "field_refs": [
     "player_module_appear_data.row_key=488500",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1030",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=109"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_488600",
   "row_key": 488600,
   "name": "汐海花环",
   "display_name": "汐海花环",
   "desc": "#f(5)珊瑚闪耀，海珍环绕。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4074001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 4074,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    488600,
    488601,
    488602,
    488603,
    488604,
    488605,
    488606
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 488600,
     "text": "汐海花环",
     "field_chs_slot": 7,
     "value_chs_slot": 942,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 488601,
     "text": "汐海花环-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1593,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 488602,
     "text": "汐海花环-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1595,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 488603,
     "text": "汐海花环-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1596,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 488604,
     "text": "汐海花环-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1597,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 488605,
     "text": "汐海花环-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1592,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 488606,
     "text": "汐海花环-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1594,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 942,
     "scalar_type": "0x05",
     "text": "汐海花环"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 133,
     "scalar_type": "0x05",
     "text": "#f(5)珊瑚闪耀，海珍环绕。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 488600,
    "field_refs": [
     "player_module_appear_data.row_key=488600",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=942",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=133"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_488700",
   "row_key": 488700,
   "name": "蟹蟹侬",
   "display_name": "蟹蟹侬",
   "desc": "#f(5)有钳有爱，人生灿烂。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4075001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4075,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    488700,
    488701,
    488702,
    488703,
    488704,
    488705,
    488706
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 488700,
     "text": "蟹蟹侬",
     "field_chs_slot": 7,
     "value_chs_slot": 1005,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 488701,
     "text": "蟹蟹侬-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1954,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 488702,
     "text": "蟹蟹侬-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1956,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 488703,
     "text": "蟹蟹侬-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1957,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 488704,
     "text": "蟹蟹侬-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1958,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 488705,
     "text": "蟹蟹侬-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1953,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 488706,
     "text": "蟹蟹侬-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1955,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1005,
     "scalar_type": "0x05",
     "text": "蟹蟹侬"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 117,
     "scalar_type": "0x05",
     "text": "#f(5)有钳有爱，人生灿烂。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 488700,
    "field_refs": [
     "player_module_appear_data.row_key=488700",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1005",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=117"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_488800",
   "row_key": 488800,
   "name": "极狐愿力",
   "display_name": "极狐愿力",
   "desc": "#f(5)和极狐一样，学会为愿望而不断努力吧。「明日之后×假面骑士」联动限定外观。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4076001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 200,
   "model_id": 4076,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    488800,
    488801,
    488802,
    488803,
    488804,
    488805,
    488806
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 488800,
     "text": "极狐愿力",
     "field_chs_slot": 7,
     "value_chs_slot": 931,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 488801,
     "text": "极狐愿力-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1527,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 488802,
     "text": "极狐愿力-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1529,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 488803,
     "text": "极狐愿力-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1530,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 488804,
     "text": "极狐愿力-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1531,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 488805,
     "text": "极狐愿力-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1526,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 488806,
     "text": "极狐愿力-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1528,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 931,
     "scalar_type": "0x05",
     "text": "极狐愿力"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 80,
     "scalar_type": "0x05",
     "text": "#f(5)和极狐一样，学会为愿望而不断努力吧。「明日之后×假面骑士」联动限定外观。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 488800,
    "field_refs": [
     "player_module_appear_data.row_key=488800",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=931",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=80"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_488900",
   "row_key": 488900,
   "name": "游戏开启",
   "display_name": "游戏开启",
   "desc": "#f(5)保证安全，做来自末日的假面骑士。「明日之后×假面骑士」联动限定外观。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4077001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 4077,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    488900,
    488901,
    488902,
    488903,
    488904,
    488905,
    488906
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 488900,
     "text": "游戏开启",
     "field_chs_slot": 7,
     "value_chs_slot": 946,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 488901,
     "text": "游戏开启-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1619,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 488902,
     "text": "游戏开启-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1621,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 488903,
     "text": "游戏开启-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1622,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 488904,
     "text": "游戏开启-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1623,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 488905,
     "text": "游戏开启-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1618,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 488906,
     "text": "游戏开启-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1620,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 946,
     "scalar_type": "0x05",
     "text": "游戏开启"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 68,
     "scalar_type": "0x05",
     "text": "#f(5)保证安全，做来自末日的假面骑士。「明日之后×假面骑士」联动限定外观。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 488900,
    "field_refs": [
     "player_module_appear_data.row_key=488900",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=946",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=68"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_489100",
   "row_key": 489100,
   "name": "雪国之镜",
   "display_name": "雪国之镜",
   "desc": "#f(5)颇具帝国势力风格的眼镜，在捷卡德林堡的军官间颇为流行。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4079001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4079,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    489100,
    489101,
    489102,
    489103,
    489104,
    489105,
    489106
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 489100,
     "text": "雪国之镜",
     "field_chs_slot": 7,
     "value_chs_slot": 1015,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 489101,
     "text": "雪国之镜-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 2017,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 489102,
     "text": "雪国之镜-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 2019,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 489103,
     "text": "雪国之镜-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 2020,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 489104,
     "text": "雪国之镜-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 2021,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 489105,
     "text": "雪国之镜-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 2016,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 489106,
     "text": "雪国之镜-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 2018,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1015,
     "scalar_type": "0x05",
     "text": "雪国之镜"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 155,
     "scalar_type": "0x05",
     "text": "#f(5)颇具帝国势力风格的眼镜，在捷卡德林堡的军官间颇为流行。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 489100,
    "field_refs": [
     "player_module_appear_data.row_key=489100",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1015",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=155"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_489200",
   "row_key": 489200,
   "name": "荆棘瑰冠",
   "display_name": "荆棘瑰冠",
   "desc": "#f(5)\"在我荒瘠的土地上，你是最后的玫瑰。\"在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4080001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 4080,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    489200,
    489201,
    489202,
    489203,
    489204,
    489205,
    489206
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 489200,
     "text": "荆棘瑰冠",
     "field_chs_slot": 7,
     "value_chs_slot": 997,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 489201,
     "text": "荆棘瑰冠-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1906,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 489202,
     "text": "荆棘瑰冠-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1908,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 489203,
     "text": "荆棘瑰冠-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1909,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 489204,
     "text": "荆棘瑰冠-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1910,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 489205,
     "text": "荆棘瑰冠-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1905,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 489206,
     "text": "荆棘瑰冠-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1907,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 997,
     "scalar_type": "0x05",
     "text": "荆棘瑰冠"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 42,
     "scalar_type": "0x05",
     "text": "#f(5)\"在我荒瘠的土地上，你是最后的玫瑰。\"在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 489200,
    "field_refs": [
     "player_module_appear_data.row_key=489200",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=997",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=42"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_489500",
   "row_key": 489500,
   "name": "云端约定",
   "display_name": "云端约定",
   "desc": "#f(5)载着回忆，向云端出发。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4083001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 4083,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    489500,
    489501,
    489502,
    489503,
    489504,
    489505,
    489506
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 489500,
     "text": "云端约定",
     "field_chs_slot": 7,
     "value_chs_slot": 863,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 489501,
     "text": "云端约定-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1160,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 489502,
     "text": "云端约定-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1162,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 489503,
     "text": "云端约定-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1163,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 489504,
     "text": "云端约定-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1164,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 489505,
     "text": "云端约定-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1159,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 489506,
     "text": "云端约定-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1161,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 863,
     "scalar_type": "0x05",
     "text": "云端约定"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 149,
     "scalar_type": "0x05",
     "text": "#f(5)载着回忆，向云端出发。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 489500,
    "field_refs": [
     "player_module_appear_data.row_key=489500",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=863",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=149"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_489600",
   "row_key": 489600,
   "name": "不见青",
   "display_name": "不见青",
   "desc": "#f(5)浮生如斯，谁知谁知。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4084001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4084,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    489600,
    489601,
    489602,
    489603,
    489604,
    489605,
    489606
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 489600,
     "text": "不见青",
     "field_chs_slot": 7,
     "value_chs_slot": 860,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 489601,
     "text": "不见青-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1140,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 489602,
     "text": "不见青-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1142,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 489603,
     "text": "不见青-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1143,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 489604,
     "text": "不见青-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1144,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 489605,
     "text": "不见青-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1139,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 489606,
     "text": "不见青-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1141,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 860,
     "scalar_type": "0x05",
     "text": "不见青"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 123,
     "scalar_type": "0x05",
     "text": "#f(5)浮生如斯，谁知谁知。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 489600,
    "field_refs": [
     "player_module_appear_data.row_key=489600",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=860",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=123"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_489700",
   "row_key": 489700,
   "name": "白蛇引",
   "display_name": "白蛇引",
   "desc": "#f(5)一日缘起，万般皆逃不过天命。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4085001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4085,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    489700,
    489701,
    489702,
    489703,
    489704,
    489705,
    489706
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 489700,
     "text": "白蛇引",
     "field_chs_slot": 7,
     "value_chs_slot": 969,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 489701,
     "text": "白蛇引-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1747,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 489702,
     "text": "白蛇引-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1749,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 489703,
     "text": "白蛇引-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1750,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 489704,
     "text": "白蛇引-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1751,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 489705,
     "text": "白蛇引-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1746,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 489706,
     "text": "白蛇引-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1748,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 969,
     "scalar_type": "0x05",
     "text": "白蛇引"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 51,
     "scalar_type": "0x05",
     "text": "#f(5)一日缘起，万般皆逃不过天命。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 489700,
    "field_refs": [
     "player_module_appear_data.row_key=489700",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=969",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=51"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_489800",
   "row_key": 489800,
   "name": "月相假面",
   "display_name": "月相假面",
   "desc": "#f(5)纵有阴晴圆缺，永刻赤色轮回。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4086001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4086,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    489800,
    489801,
    489802,
    489803,
    489804,
    489805,
    489806
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 489800,
     "text": "月相假面",
     "field_chs_slot": 7,
     "value_chs_slot": 929,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 489801,
     "text": "月相假面-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1515,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 489802,
     "text": "月相假面-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1517,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 489803,
     "text": "月相假面-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1518,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 489804,
     "text": "月相假面-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1519,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 489805,
     "text": "月相假面-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1514,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 489806,
     "text": "月相假面-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1516,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 929,
     "scalar_type": "0x05",
     "text": "月相假面"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 141,
     "scalar_type": "0x05",
     "text": "#f(5)纵有阴晴圆缺，永刻赤色轮回。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 489800,
    "field_refs": [
     "player_module_appear_data.row_key=489800",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=929",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=141"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_489900",
   "row_key": 489900,
   "name": "一口甜心",
   "display_name": "一口甜心",
   "desc": "#f(5)在TA的心里，你比冰淇淋更甜。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4087001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4087,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    489900,
    489901,
    489902,
    489903,
    489904,
    489905,
    489906
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 489900,
     "text": "一口甜心",
     "field_chs_slot": 7,
     "value_chs_slot": 853,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 489901,
     "text": "一口甜心-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1110,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 489902,
     "text": "一口甜心-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1112,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 489903,
     "text": "一口甜心-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1113,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 489904,
     "text": "一口甜心-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1114,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 489905,
     "text": "一口甜心-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1109,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 489906,
     "text": "一口甜心-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1111,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 853,
     "scalar_type": "0x05",
     "text": "一口甜心"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 84,
     "scalar_type": "0x05",
     "text": "#f(5)在TA的心里，你比冰淇淋更甜。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 489900,
    "field_refs": [
     "player_module_appear_data.row_key=489900",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=853",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=84"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_490000",
   "row_key": 490000,
   "name": "雪国之冕",
   "display_name": "雪国之冕",
   "desc": "#f(5)具有帝国势力标志的帽子，在捷卡德林堡的军官间颇为流行。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4088001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4088,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    490000,
    490001,
    490002,
    490003,
    490004,
    490005,
    490006
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 490000,
     "text": "雪国之冕",
     "field_chs_slot": 7,
     "value_chs_slot": 1014,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 490001,
     "text": "雪国之冕-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 2011,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 490002,
     "text": "雪国之冕-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 2013,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 490003,
     "text": "雪国之冕-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 2014,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 490004,
     "text": "雪国之冕-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 2015,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 490005,
     "text": "雪国之冕-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 2010,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 490006,
     "text": "雪国之冕-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 2012,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1014,
     "scalar_type": "0x05",
     "text": "雪国之冕"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 72,
     "scalar_type": "0x05",
     "text": "#f(5)具有帝国势力标志的帽子，在捷卡德林堡的军官间颇为流行。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 490000,
    "field_refs": [
     "player_module_appear_data.row_key=490000",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1014",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=72"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_490060",
   "row_key": 490060,
   "name": "赤焰翎羽",
   "display_name": "赤焰翎羽",
   "desc": "#f(5)赤焰风华主题限定面饰#n。可配戴在面部的翎羽面饰。在使用某些时装时无法佩戴。（赤焰翎羽面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3289001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 3289,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    490060,
    490061,
    490062,
    490063,
    490064,
    490065,
    490066
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 490060,
     "text": "赤焰翎羽",
     "field_chs_slot": 7,
     "value_chs_slot": 1008,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 490061,
     "text": "赤焰翎羽-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1973,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 490062,
     "text": "赤焰翎羽-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1975,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 490063,
     "text": "赤焰翎羽-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1976,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 490064,
     "text": "赤焰翎羽-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1977,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 490065,
     "text": "赤焰翎羽-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1972,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 490066,
     "text": "赤焰翎羽-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1974,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1008,
     "scalar_type": "0x05",
     "text": "赤焰翎羽"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 148,
     "scalar_type": "0x05",
     "text": "#f(5)赤焰风华主题限定面饰#n。可配戴在面部的翎羽面饰。在使用某些时装时无法佩戴。（赤焰翎羽面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 490060,
    "field_refs": [
     "player_module_appear_data.row_key=490060",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1008",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=148"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_490100",
   "row_key": 490100,
   "name": "梦里星尘",
   "display_name": "梦里星尘",
   "desc": "#f(5)把闪闪的星星和深蓝的天幕，编织成发间摇曳的思念。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4089001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 4089,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    490100,
    490101,
    490102,
    490103,
    490104,
    490105,
    490106
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 490100,
     "text": "梦里星尘",
     "field_chs_slot": 7,
     "value_chs_slot": 935,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 490101,
     "text": "梦里星尘-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1551,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 490102,
     "text": "梦里星尘-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1553,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 490103,
     "text": "梦里星尘-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1554,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 490104,
     "text": "梦里星尘-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1555,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 490105,
     "text": "梦里星尘-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1550,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 490106,
     "text": "梦里星尘-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1552,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 935,
     "scalar_type": "0x05",
     "text": "梦里星尘"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 107,
     "scalar_type": "0x05",
     "text": "#f(5)把闪闪的星星和深蓝的天幕，编织成发间摇曳的思念。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 490100,
    "field_refs": [
     "player_module_appear_data.row_key=490100",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=935",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=107"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_490200",
   "row_key": 490200,
   "name": "绒绒兔",
   "display_name": "绒绒兔",
   "desc": "#f(5)将月光与绒毛，缝成软糯童话。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4090001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4090,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    490200,
    490201,
    490202,
    490203,
    490204,
    490205,
    490206
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 490200,
     "text": "绒绒兔",
     "field_chs_slot": 7,
     "value_chs_slot": 981,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 490201,
     "text": "绒绒兔-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1810,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 490202,
     "text": "绒绒兔-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1812,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 490203,
     "text": "绒绒兔-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1813,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 490204,
     "text": "绒绒兔-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1814,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 490205,
     "text": "绒绒兔-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1809,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 490206,
     "text": "绒绒兔-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1811,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 981,
     "scalar_type": "0x05",
     "text": "绒绒兔"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 94,
     "scalar_type": "0x05",
     "text": "#f(5)将月光与绒毛，缝成软糯童话。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 490200,
    "field_refs": [
     "player_module_appear_data.row_key=490200",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=981",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=94"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_490300",
   "row_key": 490300,
   "name": "双子星",
   "display_name": "双子星",
   "desc": "#f(5)双子星闪烁，记录你我密语。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4091001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4091,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    490300,
    490301,
    490302,
    490303,
    490304,
    490305,
    490306
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 490300,
     "text": "双子星",
     "field_chs_slot": 7,
     "value_chs_slot": 883,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 490301,
     "text": "双子星-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1277,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 490302,
     "text": "双子星-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1279,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 490303,
     "text": "双子星-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1280,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 490304,
     "text": "双子星-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1281,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 490305,
     "text": "双子星-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1276,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 490306,
     "text": "双子星-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1278,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 883,
     "scalar_type": "0x05",
     "text": "双子星"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 77,
     "scalar_type": "0x05",
     "text": "#f(5)双子星闪烁，记录你我密语。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 490300,
    "field_refs": [
     "player_module_appear_data.row_key=490300",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=883",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=77"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_490400",
   "row_key": 490400,
   "name": "眸间契约",
   "display_name": "眸间契约",
   "desc": "纵使窥见爱的牢笼，亦甘愿坠入甜蜜的桎梏。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4092001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4092,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    490400,
    490401,
    490402,
    490403,
    490404,
    490405,
    490406
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 490400,
     "text": "眸间契约",
     "field_chs_slot": 7,
     "value_chs_slot": 971,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 490401,
     "text": "眸间契约-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1753,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 490402,
     "text": "眸间契约-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1755,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 490403,
     "text": "眸间契约-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1756,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 490404,
     "text": "眸间契约-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1757,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 490405,
     "text": "眸间契约-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1752,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 490406,
     "text": "眸间契约-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1754,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 971,
     "scalar_type": "0x05",
     "text": "眸间契约"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 980,
     "scalar_type": "0x05",
     "text": "纵使窥见爱的牢笼，亦甘愿坠入甜蜜的桎梏。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 490400,
    "field_refs": [
     "player_module_appear_data.row_key=490400",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=971",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=980"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_490500",
   "row_key": 490500,
   "name": "绯夜犄角",
   "display_name": "绯夜犄角",
   "desc": "#f(5)圣洁终有尽时，而恶魔的狂欢永不落幕。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4093001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4093,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    490500,
    490501,
    490502,
    490503,
    490504,
    490505,
    490506
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 490500,
     "text": "绯夜犄角",
     "field_chs_slot": 7,
     "value_chs_slot": 987,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 490501,
     "text": "绯夜犄角-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1846,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 490502,
     "text": "绯夜犄角-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1848,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 490503,
     "text": "绯夜犄角-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1849,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 490504,
     "text": "绯夜犄角-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1850,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 490505,
     "text": "绯夜犄角-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1845,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 490506,
     "text": "绯夜犄角-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1847,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 987,
     "scalar_type": "0x05",
     "text": "绯夜犄角"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 83,
     "scalar_type": "0x05",
     "text": "#f(5)圣洁终有尽时，而恶魔的狂欢永不落幕。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 490500,
    "field_refs": [
     "player_module_appear_data.row_key=490500",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=987",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=83"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_490570",
   "row_key": 490570,
   "name": "软萌兔兔",
   "display_name": "软萌兔兔",
   "desc": "#f(5)2024儿童节限定面饰#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3494001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 3494,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    490570,
    490571,
    490572,
    490573,
    490574,
    490575,
    490576
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 490570,
     "text": "软萌兔兔",
     "field_chs_slot": 7,
     "value_chs_slot": 1011,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 490571,
     "text": "软萌兔兔-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1991,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 490572,
     "text": "软萌兔兔-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1993,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 490573,
     "text": "软萌兔兔-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1994,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 490574,
     "text": "软萌兔兔-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1995,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 490575,
     "text": "软萌兔兔-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1990,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 490576,
     "text": "软萌兔兔-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1992,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1011,
     "scalar_type": "0x05",
     "text": "软萌兔兔"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 32,
     "scalar_type": "0x05",
     "text": "#f(5)2024儿童节限定面饰#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 490570,
    "field_refs": [
     "player_module_appear_data.row_key=490570",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1011",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=32"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_490600",
   "row_key": 490600,
   "name": "森森低语",
   "display_name": "森森低语",
   "desc": "#f(5)似是亡灵借你发梢攀望人间。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4094001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 4094,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    490600,
    490601,
    490602,
    490603,
    490604,
    490605,
    490606
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 490600,
     "text": "森森低语",
     "field_chs_slot": 7,
     "value_chs_slot": 936,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 490601,
     "text": "森森低语-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1557,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 490602,
     "text": "森森低语-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1559,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 490603,
     "text": "森森低语-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1560,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 490604,
     "text": "森森低语-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1561,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 490605,
     "text": "森森低语-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1556,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 490606,
     "text": "森森低语-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1558,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 936,
     "scalar_type": "0x05",
     "text": "森森低语"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 63,
     "scalar_type": "0x05",
     "text": "#f(5)似是亡灵借你发梢攀望人间。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 490600,
    "field_refs": [
     "player_module_appear_data.row_key=490600",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=936",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=63"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_490670",
   "row_key": 490670,
   "name": "甜心喵喵",
   "display_name": "甜心喵喵",
   "desc": "#f(5)2024儿童节限定面饰#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3495001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 3495,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    490670,
    490671,
    490672,
    490673,
    490674,
    490675,
    490676
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 490670,
     "text": "甜心喵喵",
     "field_chs_slot": 7,
     "value_chs_slot": 964,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 490671,
     "text": "甜心喵喵-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1722,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 490672,
     "text": "甜心喵喵-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1724,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 490673,
     "text": "甜心喵喵-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1725,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 490674,
     "text": "甜心喵喵-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1726,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 490675,
     "text": "甜心喵喵-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1721,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 490676,
     "text": "甜心喵喵-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1723,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 964,
     "scalar_type": "0x05",
     "text": "甜心喵喵"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 32,
     "scalar_type": "0x05",
     "text": "#f(5)2024儿童节限定面饰#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 490670,
    "field_refs": [
     "player_module_appear_data.row_key=490670",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=964",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=32"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_490700",
   "row_key": 490700,
   "name": "脑洞大开",
   "display_name": "脑洞大开",
   "desc": "#f(5)我好像……快裂开了。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4095001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4095,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    490700,
    490701,
    490702,
    490703,
    490704,
    490705,
    490706
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 490700,
     "text": "脑洞大开",
     "field_chs_slot": 7,
     "value_chs_slot": 995,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 490701,
     "text": "脑洞大开-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1894,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 490702,
     "text": "脑洞大开-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1896,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 490703,
     "text": "脑洞大开-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1897,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 490704,
     "text": "脑洞大开-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1898,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 490705,
     "text": "脑洞大开-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1893,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 490706,
     "text": "脑洞大开-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1895,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 995,
     "scalar_type": "0x05",
     "text": "脑洞大开"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 102,
     "scalar_type": "0x05",
     "text": "#f(5)我好像……快裂开了。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 490700,
    "field_refs": [
     "player_module_appear_data.row_key=490700",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=995",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=102"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_490770",
   "row_key": 490770,
   "name": "小天使-白",
   "display_name": "小天使-白",
   "desc": "#f(5)520限定面饰#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3496001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 3496,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    490770,
    490771,
    490772,
    490773,
    490774,
    490775,
    490776
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 490770,
     "text": "小天使-白",
     "field_chs_slot": 7,
     "value_chs_slot": 898,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 490771,
     "text": "小天使-白-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1362,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 490772,
     "text": "小天使-白-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1364,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 490773,
     "text": "小天使-白-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1365,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 490774,
     "text": "小天使-白-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1366,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 490775,
     "text": "小天使-白-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1361,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 490776,
     "text": "小天使-白-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1363,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 898,
     "scalar_type": "0x05",
     "text": "小天使-白"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 27,
     "scalar_type": "0x05",
     "text": "#f(5)520限定面饰#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 490770,
    "field_refs": [
     "player_module_appear_data.row_key=490770",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=898",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=27"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_490800",
   "row_key": 490800,
   "name": "蔽罪之瞳",
   "display_name": "蔽罪之瞳",
   "desc": "#f(5)众生罪孽不再入眼，唯余你唇间降下的赦免涤荡人间。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4096001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4096,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    490800,
    490801,
    490802,
    490803,
    490804,
    490805,
    490806
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 490800,
     "text": "蔽罪之瞳",
     "field_chs_slot": 7,
     "value_chs_slot": 1001,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 490801,
     "text": "蔽罪之瞳-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1930,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 490802,
     "text": "蔽罪之瞳-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1932,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 490803,
     "text": "蔽罪之瞳-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1933,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 490804,
     "text": "蔽罪之瞳-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1934,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 490805,
     "text": "蔽罪之瞳-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1929,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 490806,
     "text": "蔽罪之瞳-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1931,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1001,
     "scalar_type": "0x05",
     "text": "蔽罪之瞳"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 62,
     "scalar_type": "0x05",
     "text": "#f(5)众生罪孽不再入眼，唯余你唇间降下的赦免涤荡人间。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 490800,
    "field_refs": [
     "player_module_appear_data.row_key=490800",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1001",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=62"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_490900",
   "row_key": 490900,
   "name": "神明之眸",
   "display_name": "神明之眸",
   "desc": "#f(5)当神羽垂落眼帘，凡俗皆不可见我目。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4097001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 4097,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    490900,
    490901,
    490902,
    490903,
    490904,
    490905,
    490906
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 490900,
     "text": "神明之眸",
     "field_chs_slot": 7,
     "value_chs_slot": 975,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 490901,
     "text": "神明之眸-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1777,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 490902,
     "text": "神明之眸-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1779,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 490903,
     "text": "神明之眸-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1780,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 490904,
     "text": "神明之眸-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1781,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 490905,
     "text": "神明之眸-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1776,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 490906,
     "text": "神明之眸-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1778,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 975,
     "scalar_type": "0x05",
     "text": "神明之眸"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 99,
     "scalar_type": "0x05",
     "text": "#f(5)当神羽垂落眼帘，凡俗皆不可见我目。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 490900,
    "field_refs": [
     "player_module_appear_data.row_key=490900",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=975",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=99"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_491000",
   "row_key": 491000,
   "name": "狩猎界域",
   "display_name": "狩猎界域",
   "desc": "#f(5)目光交汇的刹那，你的结局早已注定。「明日之后×七日世界」联动限定外观。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4098001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4098,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    491000,
    491001,
    491002,
    491003,
    491004,
    491005,
    491006
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 491000,
     "text": "狩猎界域",
     "field_chs_slot": 7,
     "value_chs_slot": 956,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 491001,
     "text": "狩猎界域-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1680,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 491002,
     "text": "狩猎界域-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1682,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 491003,
     "text": "狩猎界域-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1683,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 491004,
     "text": "狩猎界域-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1684,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 491005,
     "text": "狩猎界域-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1679,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 491006,
     "text": "狩猎界域-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1681,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 956,
     "scalar_type": "0x05",
     "text": "狩猎界域"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 136,
     "scalar_type": "0x05",
     "text": "#f(5)目光交汇的刹那，你的结局早已注定。「明日之后×七日世界」联动限定外观。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 491000,
    "field_refs": [
     "player_module_appear_data.row_key=491000",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=956",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=136"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_491020",
   "row_key": 491020,
   "name": "小天使-粉",
   "display_name": "小天使-粉",
   "desc": "#f(5)520限定面饰#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3496002",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 3496,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    491020,
    491021,
    491022,
    491023,
    491024,
    491025,
    491026
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 491020,
     "text": "小天使-粉",
     "field_chs_slot": 7,
     "value_chs_slot": 899,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 491021,
     "text": "小天使-粉-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1368,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 491022,
     "text": "小天使-粉-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1370,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 491023,
     "text": "小天使-粉-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1371,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 491024,
     "text": "小天使-粉-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1372,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 491025,
     "text": "小天使-粉-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1367,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 491026,
     "text": "小天使-粉-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1369,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 899,
     "scalar_type": "0x05",
     "text": "小天使-粉"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 27,
     "scalar_type": "0x05",
     "text": "#f(5)520限定面饰#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 491020,
    "field_refs": [
     "player_module_appear_data.row_key=491020",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=899",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=27"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_491100",
   "row_key": 491100,
   "name": "狐聆惑心",
   "display_name": "狐聆惑心",
   "desc": "#f(5)凡被此耳蛊惑一瞬，便需以千世轮回，偿尽狐火中烙下的魂契。「明日之后×七日世界」联动限定外观。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4099001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4099,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    491100,
    491101,
    491102,
    491103,
    491104,
    491105,
    491106
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 491100,
     "text": "狐聆惑心",
     "field_chs_slot": 7,
     "value_chs_slot": 954,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 491101,
     "text": "狐聆惑心-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1668,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 491102,
     "text": "狐聆惑心-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1670,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 491103,
     "text": "狐聆惑心-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1671,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 491104,
     "text": "狐聆惑心-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1672,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 491105,
     "text": "狐聆惑心-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1667,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 491106,
     "text": "狐聆惑心-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1669,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 954,
     "scalar_type": "0x05",
     "text": "狐聆惑心"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 75,
     "scalar_type": "0x05",
     "text": "#f(5)凡被此耳蛊惑一瞬，便需以千世轮回，偿尽狐火中烙下的魂契。「明日之后×七日世界」联动限定外观。在使用某些时装时无法佩戴。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 491100,
    "field_refs": [
     "player_module_appear_data.row_key=491100",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=954",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=75"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_491200",
   "row_key": 491200,
   "name": "蝶之眸",
   "display_name": "蝶之眸",
   "desc": "#f(5)蝶翼轻颤，藏起一半对你的爱意。「明日之后×七日世界」联动限定外观。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4100001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 200,
   "model_id": 4100,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    491200,
    491201,
    491202,
    491203,
    491204,
    491205,
    491206
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 491200,
     "text": "蝶之眸",
     "field_chs_slot": 7,
     "value_chs_slot": 1004,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 491201,
     "text": "蝶之眸-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1948,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 491202,
     "text": "蝶之眸-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1950,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 491203,
     "text": "蝶之眸-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1951,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 491204,
     "text": "蝶之眸-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1952,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 491205,
     "text": "蝶之眸-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1947,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 491206,
     "text": "蝶之眸-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1949,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1004,
     "scalar_type": "0x05",
     "text": "蝶之眸"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 146,
     "scalar_type": "0x05",
     "text": "#f(5)蝶翼轻颤，藏起一半对你的爱意。「明日之后×七日世界」联动限定外观。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 491200,
    "field_refs": [
     "player_module_appear_data.row_key=491200",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1004",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=146"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_491270",
   "row_key": 491270,
   "name": "小天使-黑",
   "display_name": "小天使-黑",
   "desc": "#f(5)520限定面饰#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3496003",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 3496,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    491270,
    491271,
    491272,
    491273,
    491274,
    491275,
    491276
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 491270,
     "text": "小天使-黑",
     "field_chs_slot": 7,
     "value_chs_slot": 900,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 491271,
     "text": "小天使-黑-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1374,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 491272,
     "text": "小天使-黑-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1376,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 491273,
     "text": "小天使-黑-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1377,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 491274,
     "text": "小天使-黑-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1378,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 491275,
     "text": "小天使-黑-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1373,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 491276,
     "text": "小天使-黑-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1375,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 900,
     "scalar_type": "0x05",
     "text": "小天使-黑"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 27,
     "scalar_type": "0x05",
     "text": "#f(5)520限定面饰#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 491270,
    "field_refs": [
     "player_module_appear_data.row_key=491270",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=900",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=27"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_491300",
   "row_key": 491300,
   "name": "绵绵雪须",
   "display_name": "绵绵雪须",
   "desc": "#f(5)孩子们，要来点糖果吗？（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4101001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4101,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    491300,
    491301,
    491302,
    491303,
    491304,
    491305,
    491306
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 491300,
     "text": "绵绵雪须",
     "field_chs_slot": 7,
     "value_chs_slot": 988,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 491301,
     "text": "绵绵雪须-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1852,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 491302,
     "text": "绵绵雪须-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1854,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 491303,
     "text": "绵绵雪须-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1855,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 491304,
     "text": "绵绵雪须-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1856,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 491305,
     "text": "绵绵雪须-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1851,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 491306,
     "text": "绵绵雪须-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1853,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 988,
     "scalar_type": "0x05",
     "text": "绵绵雪须"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 91,
     "scalar_type": "0x05",
     "text": "#f(5)孩子们，要来点糖果吗？（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 491300,
    "field_refs": [
     "player_module_appear_data.row_key=491300",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=988",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=91"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_491400",
   "row_key": 491400,
   "name": "乌云快走开",
   "display_name": "乌云快走开",
   "desc": "#f(5)乌云乌云快走开，闪电闪电我自带。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4102001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4102,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    491400,
    491401,
    491402,
    491403,
    491404,
    491405,
    491406
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 491400,
     "text": "乌云快走开",
     "field_chs_slot": 7,
     "value_chs_slot": 861,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 491401,
     "text": "乌云快走开-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1147,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 491402,
     "text": "乌云快走开-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1149,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 491403,
     "text": "乌云快走开-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1150,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 491404,
     "text": "乌云快走开-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1151,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 491405,
     "text": "乌云快走开-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1146,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 491406,
     "text": "乌云快走开-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1148,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 861,
     "scalar_type": "0x05",
     "text": "乌云快走开"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 53,
     "scalar_type": "0x05",
     "text": "#f(5)乌云乌云快走开，闪电闪电我自带。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 491400,
    "field_refs": [
     "player_module_appear_data.row_key=491400",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=861",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=53"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_491500",
   "row_key": 491500,
   "name": "靶心引力",
   "display_name": "靶心引力",
   "desc": "#f(5)预备！瞄准！开火！（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4103001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4103,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    491500,
    491501,
    491502,
    491503,
    491504,
    491505,
    491506
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 491500,
     "text": "靶心引力",
     "field_chs_slot": 7,
     "value_chs_slot": 1024,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 491501,
     "text": "靶心引力-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 2059,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 491502,
     "text": "靶心引力-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 2061,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 491503,
     "text": "靶心引力-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 2062,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 491504,
     "text": "靶心引力-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 2063,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 491505,
     "text": "靶心引力-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 2058,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 491506,
     "text": "靶心引力-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 2060,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1024,
     "scalar_type": "0x05",
     "text": "靶心引力"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 154,
     "scalar_type": "0x05",
     "text": "#f(5)预备！瞄准！开火！（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 491500,
    "field_refs": [
     "player_module_appear_data.row_key=491500",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1024",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=154"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_491600",
   "row_key": 491600,
   "name": "永夜之光",
   "display_name": "永夜之光",
   "desc": "#f(5)保持清醒，不要温和地走入那个良夜。「传闻是探险者中颇为喜欢的款式」。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4104001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4104,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    491600,
    491601,
    491602,
    491603,
    491604,
    491605,
    491606
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 491600,
     "text": "永夜之光",
     "field_chs_slot": 7,
     "value_chs_slot": 941,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 491601,
     "text": "永夜之光-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1587,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 491602,
     "text": "永夜之光-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1589,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 491603,
     "text": "永夜之光-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1590,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 491604,
     "text": "永夜之光-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1591,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 491605,
     "text": "永夜之光-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1586,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 491606,
     "text": "永夜之光-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1588,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 941,
     "scalar_type": "0x05",
     "text": "永夜之光"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 67,
     "scalar_type": "0x05",
     "text": "#f(5)保持清醒，不要温和地走入那个良夜。「传闻是探险者中颇为喜欢的款式」。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 491600,
    "field_refs": [
     "player_module_appear_data.row_key=491600",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=941",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=67"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_491800",
   "row_key": 491800,
   "name": "星光玉雪",
   "display_name": "星光玉雪",
   "desc": "#f(5)俯首间碎星洒落，回眸间银河倾覆。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4106001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 4106,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    491800,
    491801,
    491802,
    491803,
    491804,
    491805,
    491806
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 491800,
     "text": "星光玉雪",
     "field_chs_slot": 7,
     "value_chs_slot": 921,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 491801,
     "text": "星光玉雪-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1478,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 491802,
     "text": "星光玉雪-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1480,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 491803,
     "text": "星光玉雪-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1481,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 491804,
     "text": "星光玉雪-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1482,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 491805,
     "text": "星光玉雪-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1477,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 491806,
     "text": "星光玉雪-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1479,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 921,
     "scalar_type": "0x05",
     "text": "星光玉雪"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 69,
     "scalar_type": "0x05",
     "text": "#f(5)俯首间碎星洒落，回眸间银河倾覆。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 491800,
    "field_refs": [
     "player_module_appear_data.row_key=491800",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=921",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=69"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_491870",
   "row_key": 491870,
   "name": "毕业啦",
   "display_name": "毕业啦",
   "desc": "#f(5)愿你前程似锦，愿你一帆风顺，愿你的人生之旅充满欢乐！#n。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3507001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 3507,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    491870,
    491871,
    491872,
    491873,
    491874,
    491875,
    491876
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 491870,
     "text": "毕业啦",
     "field_chs_slot": 7,
     "value_chs_slot": 939,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 491871,
     "text": "毕业啦-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1575,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 491872,
     "text": "毕业啦-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1577,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 491873,
     "text": "毕业啦-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1578,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 491874,
     "text": "毕业啦-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1579,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 491875,
     "text": "毕业啦-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1574,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 491876,
     "text": "毕业啦-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1576,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 939,
     "scalar_type": "0x05",
     "text": "毕业啦"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 100,
     "scalar_type": "0x05",
     "text": "#f(5)愿你前程似锦，愿你一帆风顺，愿你的人生之旅充满欢乐！#n。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 491870,
    "field_refs": [
     "player_module_appear_data.row_key=491870",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=939",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=100"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_491900",
   "row_key": 491900,
   "name": "喜乐甜甜",
   "display_name": "喜乐甜甜",
   "desc": "#f(5)烟火起，照人间；举杯，敬此年。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4107001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4107,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    491900,
    491901,
    491902,
    491903,
    491904,
    491905,
    491906
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 491900,
     "text": "喜乐甜甜",
     "field_chs_slot": 7,
     "value_chs_slot": 887,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 491901,
     "text": "喜乐甜甜-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1301,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 491902,
     "text": "喜乐甜甜-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1303,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 491903,
     "text": "喜乐甜甜-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1304,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 491904,
     "text": "喜乐甜甜-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1305,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 491905,
     "text": "喜乐甜甜-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1300,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 491906,
     "text": "喜乐甜甜-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1302,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 887,
     "scalar_type": "0x05",
     "text": "喜乐甜甜"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 126,
     "scalar_type": "0x05",
     "text": "#f(5)烟火起，照人间；举杯，敬此年。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 491900,
    "field_refs": [
     "player_module_appear_data.row_key=491900",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=887",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=126"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_492000",
   "row_key": 492000,
   "name": "水天一色",
   "display_name": "水天一色",
   "desc": "#f(5)向视线拂去雾霭，向瞳仁凝住水色。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4108001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 4108,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    492000,
    492001,
    492002,
    492003,
    492004,
    492005,
    492006
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 492000,
     "text": "水天一色",
     "field_chs_slot": 7,
     "value_chs_slot": 940,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 492001,
     "text": "水天一色-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1581,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 492002,
     "text": "水天一色-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1583,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 492003,
     "text": "水天一色-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1584,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 492004,
     "text": "水天一色-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1585,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 492005,
     "text": "水天一色-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1580,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 492006,
     "text": "水天一色-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1582,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 940,
     "scalar_type": "0x05",
     "text": "水天一色"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 78,
     "scalar_type": "0x05",
     "text": "#f(5)向视线拂去雾霭，向瞳仁凝住水色。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 492000,
    "field_refs": [
     "player_module_appear_data.row_key=492000",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=940",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=78"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_492100",
   "row_key": 492100,
   "name": "星霜冠冕",
   "display_name": "星霜冠冕",
   "desc": "#f(5)星芒为钻，冰霜为托，一场永不融化的加冕。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4109001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 4109,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    492100,
    492101,
    492102,
    492103,
    492104,
    492105,
    492106
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 492100,
     "text": "星霜冠冕",
     "field_chs_slot": 7,
     "value_chs_slot": 924,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 492101,
     "text": "星霜冠冕-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1496,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 492102,
     "text": "星霜冠冕-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1498,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 492103,
     "text": "星霜冠冕-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1499,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 492104,
     "text": "星霜冠冕-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1500,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 492105,
     "text": "星霜冠冕-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1495,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 492106,
     "text": "星霜冠冕-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1497,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 924,
     "scalar_type": "0x05",
     "text": "星霜冠冕"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 112,
     "scalar_type": "0x05",
     "text": "#f(5)星芒为钻，冰霜为托，一场永不融化的加冕。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 492100,
    "field_refs": [
     "player_module_appear_data.row_key=492100",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=924",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=112"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_492150",
   "row_key": 492150,
   "name": "烟火年年",
   "display_name": "烟火年年",
   "desc": "#f(5)烟花落，四季平；举杯，贺新年。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4107002",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4107,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    492150,
    492151,
    492152,
    492153,
    492154,
    492155,
    492156
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 492150,
     "text": "烟火年年",
     "field_chs_slot": 7,
     "value_chs_slot": 951,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 492151,
     "text": "烟火年年-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1649,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 492152,
     "text": "烟火年年-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1651,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 492153,
     "text": "烟火年年-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1652,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 492154,
     "text": "烟火年年-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1653,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 492155,
     "text": "烟火年年-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1648,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 492156,
     "text": "烟火年年-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1650,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 951,
     "scalar_type": "0x05",
     "text": "烟火年年"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 127,
     "scalar_type": "0x05",
     "text": "#f(5)烟花落，四季平；举杯，贺新年。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 492150,
    "field_refs": [
     "player_module_appear_data.row_key=492150",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=951",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=127"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_492200",
   "row_key": 492200,
   "name": "笑春风",
   "display_name": "笑春风",
   "desc": "#f(5)人面不知何处去，桃花依旧笑春风。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4110001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 4110,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    492200,
    492201,
    492202,
    492203,
    492204,
    492205,
    492206
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 492200,
     "text": "笑春风",
     "field_chs_slot": 7,
     "value_chs_slot": 977,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 492201,
     "text": "笑春风-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1789,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 492202,
     "text": "笑春风-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1791,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 492203,
     "text": "笑春风-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1792,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 492204,
     "text": "笑春风-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1793,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 492205,
     "text": "笑春风-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1788,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 492206,
     "text": "笑春风-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1790,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 977,
     "scalar_type": "0x05",
     "text": "笑春风"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 54,
     "scalar_type": "0x05",
     "text": "#f(5)人面不知何处去，桃花依旧笑春风。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 492200,
    "field_refs": [
     "player_module_appear_data.row_key=492200",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=977",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=54"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_492300",
   "row_key": 492300,
   "name": "马上有钱",
   "display_name": "马上有钱",
   "desc": "#f(5)有钱有花，人生繁华。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4111001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4111,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    492300,
    492301,
    492302,
    492303,
    492304,
    492305,
    492306
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 492300,
     "text": "马上有钱",
     "field_chs_slot": 7,
     "value_chs_slot": 1028,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 492301,
     "text": "马上有钱-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 2083,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 492302,
     "text": "马上有钱-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 2085,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 492303,
     "text": "马上有钱-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 2086,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 492304,
     "text": "马上有钱-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 2087,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 492305,
     "text": "马上有钱-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 2082,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 492306,
     "text": "马上有钱-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 2084,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1028,
     "scalar_type": "0x05",
     "text": "马上有钱"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 116,
     "scalar_type": "0x05",
     "text": "#f(5)有钱有花，人生繁华。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 492300,
    "field_refs": [
     "player_module_appear_data.row_key=492300",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1028",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=116"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_492400",
   "row_key": 492400,
   "name": "马上有爱",
   "display_name": "马上有爱",
   "desc": "#f(5)有你有爱，人生精彩。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4112001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4112,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    492400,
    492401,
    492402,
    492403,
    492404,
    492405,
    492406
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 492400,
     "text": "马上有爱",
     "field_chs_slot": 7,
     "value_chs_slot": 1027,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 492401,
     "text": "马上有爱-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 2077,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 492402,
     "text": "马上有爱-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 2079,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 492403,
     "text": "马上有爱-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 2080,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 492404,
     "text": "马上有爱-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 2081,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 492405,
     "text": "马上有爱-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 2076,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 492406,
     "text": "马上有爱-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 2078,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1027,
     "scalar_type": "0x05",
     "text": "马上有爱"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 115,
     "scalar_type": "0x05",
     "text": "#f(5)有你有爱，人生精彩。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 492400,
    "field_refs": [
     "player_module_appear_data.row_key=492400",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1027",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=115"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_492500",
   "row_key": 492500,
   "name": "白巧喵耳",
   "display_name": "白巧喵耳",
   "desc": "#f(5)一对会撒娇的云朵，撷取草莓融进白巧的甜吻。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4113001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 4113,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    492500,
    492501,
    492502,
    492503,
    492504,
    492505,
    492506
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 492500,
     "text": "白巧喵耳",
     "field_chs_slot": 7,
     "value_chs_slot": 968,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 492501,
     "text": "白巧喵耳-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1741,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 492502,
     "text": "白巧喵耳-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1743,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 492503,
     "text": "白巧喵耳-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1744,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 492504,
     "text": "白巧喵耳-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1745,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 492505,
     "text": "白巧喵耳-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1740,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 492506,
     "text": "白巧喵耳-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1742,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 968,
     "scalar_type": "0x05",
     "text": "白巧喵耳"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 46,
     "scalar_type": "0x05",
     "text": "#f(5)一对会撒娇的云朵，撷取草莓融进白巧的甜吻。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 492500,
    "field_refs": [
     "player_module_appear_data.row_key=492500",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=968",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=46"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_492570",
   "row_key": 492570,
   "name": "人鱼公主-蓝",
   "display_name": "人鱼公主-蓝",
   "desc": "#f(5)塞壬之歌主题限定面饰#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3514001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 3514,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    492570,
    492571,
    492572,
    492573,
    492574,
    492575,
    492576
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 492570,
     "text": "人鱼公主-蓝",
     "field_chs_slot": 7,
     "value_chs_slot": 867,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 492571,
     "text": "人鱼公主-蓝-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1184,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 492572,
     "text": "人鱼公主-蓝-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1186,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 492573,
     "text": "人鱼公主-蓝-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1187,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 492574,
     "text": "人鱼公主-蓝-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1188,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 492575,
     "text": "人鱼公主-蓝-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1183,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 492576,
     "text": "人鱼公主-蓝-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1185,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 867,
     "scalar_type": "0x05",
     "text": "人鱼公主-蓝"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 28,
     "scalar_type": "0x05",
     "text": "#f(5)塞壬之歌主题限定面饰#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 492570,
    "field_refs": [
     "player_module_appear_data.row_key=492570",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=867",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=28"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_492700",
   "row_key": 492700,
   "name": "清镜识微",
   "display_name": "清镜识微",
   "desc": "#f(5)白老板的同款眼镜，据说带上它就能于细微处洞见破局之机。「明日之后×灵笼」联动限定外观。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4115001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4115,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    492700,
    492701,
    492702,
    492703,
    492704,
    492705,
    492706
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 492700,
     "text": "清镜识微",
     "field_chs_slot": 7,
     "value_chs_slot": 945,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 492701,
     "text": "清镜识微-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1613,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 492702,
     "text": "清镜识微-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1615,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 492703,
     "text": "清镜识微-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1616,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 492704,
     "text": "清镜识微-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1617,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 492705,
     "text": "清镜识微-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1612,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 492706,
     "text": "清镜识微-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1614,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 945,
     "scalar_type": "0x05",
     "text": "清镜识微"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 134,
     "scalar_type": "0x05",
     "text": "#f(5)白老板的同款眼镜，据说带上它就能于细微处洞见破局之机。「明日之后×灵笼」联动限定外观。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 492700,
    "field_refs": [
     "player_module_appear_data.row_key=492700",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=945",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=134"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_492800",
   "row_key": 492800,
   "name": "元气时刻",
   "display_name": "元气时刻",
   "desc": "#f(5)白老板的同款面膜。深层沁养，舒缓维稳，维持绝佳状态直面一切危局。「明日之后×灵笼」联动限定外观。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4116001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4116,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    492800,
    492801,
    492802,
    492803,
    492804,
    492805,
    492806
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 492800,
     "text": "元气时刻",
     "field_chs_slot": 7,
     "value_chs_slot": 871,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 492801,
     "text": "元气时刻-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1202,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 492802,
     "text": "元气时刻-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1204,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 492803,
     "text": "元气时刻-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1205,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 492804,
     "text": "元气时刻-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1206,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 492805,
     "text": "元气时刻-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1201,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 492806,
     "text": "元气时刻-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1203,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 871,
     "scalar_type": "0x05",
     "text": "元气时刻"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 135,
     "scalar_type": "0x05",
     "text": "#f(5)白老板的同款面膜。深层沁养，舒缓维稳，维持绝佳状态直面一切危局。「明日之后×灵笼」联动限定外观。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 492800,
    "field_refs": [
     "player_module_appear_data.row_key=492800",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=871",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=135"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_492820",
   "row_key": 492820,
   "name": "人鱼公主-白",
   "display_name": "人鱼公主-白",
   "desc": "#f(5)塞壬之歌主题限定面饰#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3514002",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 3514,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    492820,
    492821,
    492822,
    492823,
    492824,
    492825,
    492826
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 492820,
     "text": "人鱼公主-白",
     "field_chs_slot": 7,
     "value_chs_slot": 865,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 492821,
     "text": "人鱼公主-白-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1172,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 492822,
     "text": "人鱼公主-白-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1174,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 492823,
     "text": "人鱼公主-白-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1175,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 492824,
     "text": "人鱼公主-白-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1176,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 492825,
     "text": "人鱼公主-白-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1171,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 492826,
     "text": "人鱼公主-白-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1173,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 865,
     "scalar_type": "0x05",
     "text": "人鱼公主-白"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 28,
     "scalar_type": "0x05",
     "text": "#f(5)塞壬之歌主题限定面饰#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 492820,
    "field_refs": [
     "player_module_appear_data.row_key=492820",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=865",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=28"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_493000",
   "row_key": 493000,
   "name": "心月狐",
   "display_name": "心月狐",
   "desc": "#f(5)嘘，细细聆听，樱花落下的声音…（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4118001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 4118,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    493000,
    493001,
    493002,
    493003,
    493004,
    493005,
    493006
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 493000,
     "text": "心月狐",
     "field_chs_slot": 7,
     "value_chs_slot": 903,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 493001,
     "text": "心月狐-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1393,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 493002,
     "text": "心月狐-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1395,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 493003,
     "text": "心月狐-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1396,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 493004,
     "text": "心月狐-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1397,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 493005,
     "text": "心月狐-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1392,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 493006,
     "text": "心月狐-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1394,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 903,
     "scalar_type": "0x05",
     "text": "心月狐"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 81,
     "scalar_type": "0x05",
     "text": "#f(5)嘘，细细聆听，樱花落下的声音…（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 493000,
    "field_refs": [
     "player_module_appear_data.row_key=493000",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=903",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=81"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_493070",
   "row_key": 493070,
   "name": "人鱼公主-粉",
   "display_name": "人鱼公主-粉",
   "desc": "#f(5)塞壬之歌主题限定面饰#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3514003",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 3514,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    493070,
    493071,
    493072,
    493073,
    493074,
    493075,
    493076
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 493070,
     "text": "人鱼公主-粉",
     "field_chs_slot": 7,
     "value_chs_slot": 866,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 493071,
     "text": "人鱼公主-粉-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1178,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 493072,
     "text": "人鱼公主-粉-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1180,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 493073,
     "text": "人鱼公主-粉-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1181,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 493074,
     "text": "人鱼公主-粉-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1182,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 493075,
     "text": "人鱼公主-粉-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1177,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 493076,
     "text": "人鱼公主-粉-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1179,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 866,
     "scalar_type": "0x05",
     "text": "人鱼公主-粉"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 28,
     "scalar_type": "0x05",
     "text": "#f(5)塞壬之歌主题限定面饰#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 493070,
    "field_refs": [
     "player_module_appear_data.row_key=493070",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=866",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=28"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_493200",
   "row_key": 493200,
   "name": "玉铃凝香",
   "display_name": "玉铃凝香",
   "desc": "#f(5)玉铃轻悬，芳韵萦绕；凝露含香，温婉如诗。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4120001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4120,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    493200,
    493201,
    493202,
    493203,
    493204,
    493205,
    493206
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 493200,
     "text": "玉铃凝香",
     "field_chs_slot": 7,
     "value_chs_slot": 959,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 493201,
     "text": "玉铃凝香-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1698,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 493202,
     "text": "玉铃凝香-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1700,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 493203,
     "text": "玉铃凝香-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1701,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 493204,
     "text": "玉铃凝香-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1702,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 493205,
     "text": "玉铃凝香-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1697,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 493206,
     "text": "玉铃凝香-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1699,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 959,
     "scalar_type": "0x05",
     "text": "玉铃凝香"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 132,
     "scalar_type": "0x05",
     "text": "#f(5)玉铃轻悬，芳韵萦绕；凝露含香，温婉如诗。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 493200,
    "field_refs": [
     "player_module_appear_data.row_key=493200",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=959",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=132"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_493300",
   "row_key": 493300,
   "name": "墨色风尚",
   "display_name": "墨色风尚",
   "desc": "#f(5)一抹深邃切分光影，锋芒戴于形色之上。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4121001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4121,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    493300,
    493301,
    493302,
    493303,
    493304,
    493305,
    493306
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 493300,
     "text": "墨色风尚",
     "field_chs_slot": 7,
     "value_chs_slot": 893,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 493301,
     "text": "墨色风尚-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1332,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 493302,
     "text": "墨色风尚-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1334,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 493303,
     "text": "墨色风尚-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1335,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 493304,
     "text": "墨色风尚-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1336,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 493305,
     "text": "墨色风尚-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1331,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 493306,
     "text": "墨色风尚-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1333,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 893,
     "scalar_type": "0x05",
     "text": "墨色风尚"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 50,
     "scalar_type": "0x05",
     "text": "#f(5)一抹深邃切分光影，锋芒戴于形色之上。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 493300,
    "field_refs": [
     "player_module_appear_data.row_key=493300",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=893",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=50"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_493400",
   "row_key": 493400,
   "name": "栗耳软软",
   "display_name": "栗耳软软",
   "desc": "#f(5)截住小熊猫在林间好奇张望的侧影，连同那抹蓬松一抖的憨萌，化作发间柔绒。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4122001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4122,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    493400,
    493401,
    493402,
    493403,
    493404,
    493405,
    493406
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 493400,
     "text": "栗耳软软",
     "field_chs_slot": 7,
     "value_chs_slot": 933,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 493401,
     "text": "栗耳软软-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1539,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 493402,
     "text": "栗耳软软-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1541,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 493403,
     "text": "栗耳软软-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1542,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 493404,
     "text": "栗耳软软-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1543,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 493405,
     "text": "栗耳软软-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1538,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 493406,
     "text": "栗耳软软-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1540,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 933,
     "scalar_type": "0x05",
     "text": "栗耳软软"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 103,
     "scalar_type": "0x05",
     "text": "#f(5)截住小熊猫在林间好奇张望的侧影，连同那抹蓬松一抖的憨萌，化作发间柔绒。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 493400,
    "field_refs": [
     "player_module_appear_data.row_key=493400",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=933",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=103"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_493500",
   "row_key": 493500,
   "name": "我是张博",
   "display_name": "我是张博",
   "desc": "#f(5)汪汪！汪汪汪汪！汪汪汪！（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4123001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4123,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    493500,
    493501,
    493502,
    493503,
    493504,
    493505,
    493506
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 493500,
     "text": "我是张博",
     "field_chs_slot": 7,
     "value_chs_slot": 906,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 493501,
     "text": "我是张博-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1412,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 493502,
     "text": "我是张博-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1414,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 493503,
     "text": "我是张博-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1415,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 493504,
     "text": "我是张博-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1416,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 493505,
     "text": "我是张博-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1411,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 493506,
     "text": "我是张博-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1413,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 906,
     "scalar_type": "0x05",
     "text": "我是张博"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 122,
     "scalar_type": "0x05",
     "text": "#f(5)汪汪！汪汪汪汪！汪汪汪！（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 493500,
    "field_refs": [
     "player_module_appear_data.row_key=493500",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=906",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=122"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_493600",
   "row_key": 493600,
   "name": "冠军荣耀之冕",
   "display_name": "冠军荣耀之冕",
   "desc": "#f(5)特战巅峰赛冠军限定头饰！#n时效持续至下一届冠军产生。#r同袍而生，战至天明。冠军之冕在黎明阳光下绽放金色光芒，承载着大陆文明新生的希望，是生存战意的最高象征（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4124001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": null,
   "model_id": 4124,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    493600,
    493601,
    493602,
    493603,
    493604,
    493605,
    493606
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 493600,
     "text": "冠军荣耀之冕",
     "field_chs_slot": 7,
     "value_chs_slot": 876,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 493601,
     "text": "冠军荣耀之冕-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1234,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 493602,
     "text": "冠军荣耀之冕-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1236,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 493603,
     "text": "冠军荣耀之冕-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1237,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 493604,
     "text": "冠军荣耀之冕-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1238,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 493605,
     "text": "冠军荣耀之冕-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1233,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 493606,
     "text": "冠军荣耀之冕-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1235,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 876,
     "scalar_type": "0x05",
     "text": "冠军荣耀之冕"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 129,
     "scalar_type": "0x05",
     "text": "#f(5)特战巅峰赛冠军限定头饰！#n时效持续至下一届冠军产生。#r同袍而生，战至天明。冠军之冕在黎明阳光下绽放金色光芒，承载着大陆文明新生的希望，是生存战意的最高象征（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 493600,
    "field_refs": [
     "player_module_appear_data.row_key=493600",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=876",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=129"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_493700",
   "row_key": 493700,
   "name": "明日镖客",
   "display_name": "明日镖客",
   "desc": "#f(5)废土尽头，寻一束光。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4125001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4125,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    493700,
    493701,
    493702,
    493703,
    493704,
    493705,
    493706
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 493700,
     "text": "明日镖客",
     "field_chs_slot": 7,
     "value_chs_slot": 920,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 493701,
     "text": "明日镖客-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1472,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 493702,
     "text": "明日镖客-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1474,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 493703,
     "text": "明日镖客-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1475,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 493704,
     "text": "明日镖客-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1476,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 493705,
     "text": "明日镖客-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1471,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 493706,
     "text": "明日镖客-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1473,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 920,
     "scalar_type": "0x05",
     "text": "明日镖客"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 98,
     "scalar_type": "0x05",
     "text": "#f(5)废土尽头，寻一束光。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 493700,
    "field_refs": [
     "player_module_appear_data.row_key=493700",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=920",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=98"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_493800",
   "row_key": 493800,
   "name": "半月琉璃",
   "display_name": "半月琉璃",
   "desc": "#f(5)月盈则亏，心作留白。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4126001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 4126,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    493800,
    493801,
    493802,
    493803,
    493804,
    493805,
    493806
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 493800,
     "text": "半月琉璃",
     "field_chs_slot": 7,
     "value_chs_slot": 882,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 493801,
     "text": "半月琉璃-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1271,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 493802,
     "text": "半月琉璃-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1273,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 493803,
     "text": "半月琉璃-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1274,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 493804,
     "text": "半月琉璃-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1275,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 493805,
     "text": "半月琉璃-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1270,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 493806,
     "text": "半月琉璃-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1272,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 882,
     "scalar_type": "0x05",
     "text": "半月琉璃"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 114,
     "scalar_type": "0x05",
     "text": "#f(5)月盈则亏，心作留白。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 493800,
    "field_refs": [
     "player_module_appear_data.row_key=493800",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=882",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=114"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_493850",
   "row_key": 493850,
   "name": "四强逐光之冕",
   "display_name": "四强逐光之冕",
   "desc": "#f(5)特战巅峰赛四强限定头饰！#n时效持续至下一届冠军产生。#r逐光而行，锋芒毕露。四强之冕见证着队伍在晋级路上的坚定与实力，是向最终荣耀冲刺的象征（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4124002",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": null,
   "model_id": 4124,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    493850,
    493851,
    493852,
    493853,
    493854,
    493855,
    493856
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 493850,
     "text": "四强逐光之冕",
     "field_chs_slot": 7,
     "value_chs_slot": 890,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 493851,
     "text": "四强逐光之冕-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1313,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 493852,
     "text": "四强逐光之冕-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1315,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 493853,
     "text": "四强逐光之冕-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1316,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 493854,
     "text": "四强逐光之冕-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1317,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 493855,
     "text": "四强逐光之冕-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1312,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 493856,
     "text": "四强逐光之冕-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1314,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 890,
     "scalar_type": "0x05",
     "text": "四强逐光之冕"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 131,
     "scalar_type": "0x05",
     "text": "#f(5)特战巅峰赛四强限定头饰！#n时效持续至下一届冠军产生。#r逐光而行，锋芒毕露。四强之冕见证着队伍在晋级路上的坚定与实力，是向最终荣耀冲刺的象征（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 493850,
    "field_refs": [
     "player_module_appear_data.row_key=493850",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=890",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=131"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_494100",
   "row_key": 494100,
   "name": "勇士锋芒之冕",
   "display_name": "勇士锋芒之冕",
   "desc": "#f(5)特战巅峰赛十六强限定头饰！#n时效持续至下一届冠军产生。#r破夜而出，锋芒初现。勇士之冕彰显着十六强队伍的无畏精神，是生存战意与团队实力的初次绽放。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4124003",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": null,
   "model_id": 4124,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    494100,
    494101,
    494102,
    494103,
    494104,
    494105,
    494106
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 494100,
     "text": "勇士锋芒之冕",
     "field_chs_slot": 7,
     "value_chs_slot": 881,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 494101,
     "text": "勇士锋芒之冕-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1265,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 494102,
     "text": "勇士锋芒之冕-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1267,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 494103,
     "text": "勇士锋芒之冕-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1268,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 494104,
     "text": "勇士锋芒之冕-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1269,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 494105,
     "text": "勇士锋芒之冕-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1264,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 494106,
     "text": "勇士锋芒之冕-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1266,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 881,
     "scalar_type": "0x05",
     "text": "勇士锋芒之冕"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 130,
     "scalar_type": "0x05",
     "text": "#f(5)特战巅峰赛十六强限定头饰！#n时效持续至下一届冠军产生。#r破夜而出，锋芒初现。勇士之冕彰显着十六强队伍的无畏精神，是生存战意与团队实力的初次绽放。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 494100,
    "field_refs": [
     "player_module_appear_data.row_key=494100",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=881",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=130"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_494700",
   "row_key": 494700,
   "name": "莲叶何田田",
   "display_name": "莲叶何田田",
   "desc": "#f(5)小荷才露尖尖角，早有露珠盈在头。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4135001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4135,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    494700,
    494701,
    494702,
    494703,
    494704,
    494705,
    494706
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 494700,
     "text": "莲叶何田田",
     "field_chs_slot": 7,
     "value_chs_slot": 998,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 494701,
     "text": "莲叶何田田-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1912,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 494702,
     "text": "莲叶何田田-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1914,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 494703,
     "text": "莲叶何田田-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1915,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 494704,
     "text": "莲叶何田田-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1916,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 494705,
     "text": "莲叶何田田-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1911,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 494706,
     "text": "莲叶何田田-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1913,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 998,
     "scalar_type": "0x05",
     "text": "莲叶何田田"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 95,
     "scalar_type": "0x05",
     "text": "#f(5)小荷才露尖尖角，早有露珠盈在头。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 494700,
    "field_refs": [
     "player_module_appear_data.row_key=494700",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=998",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=95"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_494800",
   "row_key": 494800,
   "name": "雪白使命",
   "display_name": "雪白使命",
   "desc": "#f(5)歪一点的护士帽，藏着最认真的处方。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4136001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4136,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    494800,
    494801,
    494802,
    494803,
    494804,
    494805,
    494806
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 494800,
     "text": "雪白使命",
     "field_chs_slot": 7,
     "value_chs_slot": 1017,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 494801,
     "text": "雪白使命-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 2029,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 494802,
     "text": "雪白使命-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 2031,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 494803,
     "text": "雪白使命-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 2032,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 494804,
     "text": "雪白使命-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 2033,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 494805,
     "text": "雪白使命-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 2028,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 494806,
     "text": "雪白使命-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 2030,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1017,
     "scalar_type": "0x05",
     "text": "雪白使命"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 120,
     "scalar_type": "0x05",
     "text": "#f(5)歪一点的护士帽，藏着最认真的处方。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 494800,
    "field_refs": [
     "player_module_appear_data.row_key=494800",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1017",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=120"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_495870",
   "row_key": 495870,
   "name": "逢考必过",
   "display_name": "逢考必过",
   "desc": "#f(5)2024开学季主题面饰#n。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3547001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 3547,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    495870,
    495871,
    495872,
    495873,
    495874,
    495875,
    495876
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 495870,
     "text": "逢考必过",
     "field_chs_slot": 7,
     "value_chs_slot": 1013,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 495871,
     "text": "逢考必过-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 2003,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 495872,
     "text": "逢考必过-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 2005,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 495873,
     "text": "逢考必过-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 2006,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 495874,
     "text": "逢考必过-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 2007,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 495875,
     "text": "逢考必过-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 2002,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 495876,
     "text": "逢考必过-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 2004,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1013,
     "scalar_type": "0x05",
     "text": "逢考必过"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 26,
     "scalar_type": "0x05",
     "text": "#f(5)2024开学季主题面饰#n。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 495870,
    "field_refs": [
     "player_module_appear_data.row_key=495870",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1013",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=26"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_495970",
   "row_key": 495970,
   "name": "你说得对",
   "display_name": "你说得对",
   "desc": "#f(5)2024开学季主题面饰#n。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3548001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 3548,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    495970,
    495971,
    495972,
    495973,
    495974,
    495975,
    495976
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 495970,
     "text": "你说得对",
     "field_chs_slot": 7,
     "value_chs_slot": 868,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 495971,
     "text": "你说得对-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1190,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 495972,
     "text": "你说得对-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1192,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 495973,
     "text": "你说得对-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1193,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 495974,
     "text": "你说得对-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1194,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 495975,
     "text": "你说得对-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1189,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 495976,
     "text": "你说得对-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1191,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 868,
     "scalar_type": "0x05",
     "text": "你说得对"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 26,
     "scalar_type": "0x05",
     "text": "#f(5)2024开学季主题面饰#n。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 495970,
    "field_refs": [
     "player_module_appear_data.row_key=495970",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=868",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=26"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_496070",
   "row_key": 496070,
   "name": "元气满满",
   "display_name": "元气满满",
   "desc": "#f(5)2024开学季主题面饰#n。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3549001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 3549,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    496070,
    496071,
    496072,
    496073,
    496074,
    496075,
    496076
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 496070,
     "text": "元气满满",
     "field_chs_slot": 7,
     "value_chs_slot": 872,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 496071,
     "text": "元气满满-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1208,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 496072,
     "text": "元气满满-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1210,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 496073,
     "text": "元气满满-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1211,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 496074,
     "text": "元气满满-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1212,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 496075,
     "text": "元气满满-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1207,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 496076,
     "text": "元气满满-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1209,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 872,
     "scalar_type": "0x05",
     "text": "元气满满"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 26,
     "scalar_type": "0x05",
     "text": "#f(5)2024开学季主题面饰#n。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 496070,
    "field_refs": [
     "player_module_appear_data.row_key=496070",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=872",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=26"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_496170",
   "row_key": 496170,
   "name": "并没在酸",
   "display_name": "并没在酸",
   "desc": "#f(5)魔法练习生主题面饰#n。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3550001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 3550,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    496170,
    496171,
    496172,
    496173,
    496174,
    496175,
    496176
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 496170,
     "text": "并没在酸",
     "field_chs_slot": 7,
     "value_chs_slot": 901,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 496171,
     "text": "并没在酸-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1380,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 496172,
     "text": "并没在酸-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1382,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 496173,
     "text": "并没在酸-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1383,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 496174,
     "text": "并没在酸-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1384,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 496175,
     "text": "并没在酸-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1379,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 496176,
     "text": "并没在酸-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1381,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 901,
     "scalar_type": "0x05",
     "text": "并没在酸"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 156,
     "scalar_type": "0x05",
     "text": "#f(5)魔法练习生主题面饰#n。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 496170,
    "field_refs": [
     "player_module_appear_data.row_key=496170",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=901",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=156"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_496360",
   "row_key": 496360,
   "name": "斩樱·樱华",
   "display_name": "斩樱·樱华",
   "desc": "#f(5)樱花主题限定面饰#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3352001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 3352,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    496360,
    496361,
    496362,
    496363,
    496364,
    496365,
    496366
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 496360,
     "text": "斩樱·樱华",
     "field_chs_slot": 7,
     "value_chs_slot": 911,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 496361,
     "text": "斩樱·樱华-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1424,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 496362,
     "text": "斩樱·樱华-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1426,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 496363,
     "text": "斩樱·樱华-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1427,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 496364,
     "text": "斩樱·樱华-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1428,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 496365,
     "text": "斩樱·樱华-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1423,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 496366,
     "text": "斩樱·樱华-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1425,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 911,
     "scalar_type": "0x05",
     "text": "斩樱·樱华"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 25,
     "scalar_type": "0x05",
     "text": "#f(5)樱花主题限定面饰#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 496360,
    "field_refs": [
     "player_module_appear_data.row_key=496360",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=911",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=25"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_496460",
   "row_key": 496460,
   "name": "斩樱·樱影",
   "display_name": "斩樱·樱影",
   "desc": "#f(5)樱花主题限定面饰#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3353001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 3353,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    496460,
    496461,
    496462,
    496463,
    496464,
    496465,
    496466
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 496460,
     "text": "斩樱·樱影",
     "field_chs_slot": 7,
     "value_chs_slot": 912,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 496461,
     "text": "斩樱·樱影-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1430,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 496462,
     "text": "斩樱·樱影-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1432,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 496463,
     "text": "斩樱·樱影-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1433,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 496464,
     "text": "斩樱·樱影-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1434,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 496465,
     "text": "斩樱·樱影-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1429,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 496466,
     "text": "斩樱·樱影-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1431,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 912,
     "scalar_type": "0x05",
     "text": "斩樱·樱影"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 25,
     "scalar_type": "0x05",
     "text": "#f(5)樱花主题限定面饰#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 496460,
    "field_refs": [
     "player_module_appear_data.row_key=496460",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=912",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=25"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_496560",
   "row_key": 496560,
   "name": "斩樱·樱舞",
   "display_name": "斩樱·樱舞",
   "desc": "#f(5)樱花主题限定面饰#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3354001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 3354,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    496560,
    496561,
    496562,
    496563,
    496564,
    496565,
    496566
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 496560,
     "text": "斩樱·樱舞",
     "field_chs_slot": 7,
     "value_chs_slot": 913,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 496561,
     "text": "斩樱·樱舞-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1436,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 496562,
     "text": "斩樱·樱舞-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1438,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 496563,
     "text": "斩樱·樱舞-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1439,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 496564,
     "text": "斩樱·樱舞-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1440,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 496565,
     "text": "斩樱·樱舞-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1435,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 496566,
     "text": "斩樱·樱舞-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1437,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 913,
     "scalar_type": "0x05",
     "text": "斩樱·樱舞"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 25,
     "scalar_type": "0x05",
     "text": "#f(5)樱花主题限定面饰#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 496560,
    "field_refs": [
     "player_module_appear_data.row_key=496560",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=913",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=25"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_496660",
   "row_key": 496660,
   "name": "斩樱·樱雨",
   "display_name": "斩樱·樱雨",
   "desc": "#f(5)樱花主题限定面饰#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3355001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 3355,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    496660,
    496661,
    496662,
    496663,
    496664,
    496665,
    496666
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 496660,
     "text": "斩樱·樱雨",
     "field_chs_slot": 7,
     "value_chs_slot": 914,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 496661,
     "text": "斩樱·樱雨-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1442,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 496662,
     "text": "斩樱·樱雨-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1444,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 496663,
     "text": "斩樱·樱雨-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1445,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 496664,
     "text": "斩樱·樱雨-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1446,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 496665,
     "text": "斩樱·樱雨-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1441,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 496666,
     "text": "斩樱·樱雨-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1443,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 914,
     "scalar_type": "0x05",
     "text": "斩樱·樱雨"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 25,
     "scalar_type": "0x05",
     "text": "#f(5)樱花主题限定面饰#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 496660,
    "field_refs": [
     "player_module_appear_data.row_key=496660",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=914",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=25"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_498760",
   "row_key": 498760,
   "name": "焰星·耀华",
   "display_name": "焰星·耀华",
   "desc": "#f(5)焰星庆佳节，愿神州繁荣，你我皆璀璨#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3376001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 3376,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    498760,
    498761,
    498762,
    498763,
    498764,
    498765,
    498766
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 498760,
     "text": "焰星·耀华",
     "field_chs_slot": 7,
     "value_chs_slot": 953,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 498761,
     "text": "焰星·耀华-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1661,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 498762,
     "text": "焰星·耀华-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1663,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 498763,
     "text": "焰星·耀华-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1664,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 498764,
     "text": "焰星·耀华-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1665,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 498765,
     "text": "焰星·耀华-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1660,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 498766,
     "text": "焰星·耀华-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1662,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 953,
     "scalar_type": "0x05",
     "text": "焰星·耀华"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 128,
     "scalar_type": "0x05",
     "text": "#f(5)焰星庆佳节，愿神州繁荣，你我皆璀璨#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 498760,
    "field_refs": [
     "player_module_appear_data.row_key=498760",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=953",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=128"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_498860",
   "row_key": 498860,
   "name": "超级幸运心",
   "display_name": "超级幸运心",
   "desc": "是无敌幸运的标记！可配戴在头部的发箍。在使用某些时装时无法佩戴。（发箍男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3377001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 3377,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    498860,
    498861,
    498862,
    498863,
    498864,
    498865,
    498866
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 498860,
     "text": "超级幸运心",
     "field_chs_slot": 7,
     "value_chs_slot": 1009,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 498861,
     "text": "超级幸运心-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1979,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 498862,
     "text": "超级幸运心-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1981,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 498863,
     "text": "超级幸运心-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1982,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 498864,
     "text": "超级幸运心-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1983,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 498865,
     "text": "超级幸运心-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1978,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 498866,
     "text": "超级幸运心-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1980,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1009,
     "scalar_type": "0x05",
     "text": "超级幸运心"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 925,
     "scalar_type": "0x05",
     "text": "是无敌幸运的标记！可配戴在头部的发箍。在使用某些时装时无法佩戴。（发箍男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 498860,
    "field_refs": [
     "player_module_appear_data.row_key=498860",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1009",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=925"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_498960",
   "row_key": 498960,
   "name": "焰星·囊萤",
   "display_name": "焰星·囊萤",
   "desc": "囊住萤火虫光，一闪一闪！可配戴在面部的面饰。在使用某些时装时无法佩戴。（发箍男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3378001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 3378,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    498960,
    498961,
    498962,
    498963,
    498964,
    498965,
    498966
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 498960,
     "text": "焰星·囊萤",
     "field_chs_slot": 7,
     "value_chs_slot": 952,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 498961,
     "text": "焰星·囊萤-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1655,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 498962,
     "text": "焰星·囊萤-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1657,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 498963,
     "text": "焰星·囊萤-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1658,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 498964,
     "text": "焰星·囊萤-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1659,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 498965,
     "text": "焰星·囊萤-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1654,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 498966,
     "text": "焰星·囊萤-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1656,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 952,
     "scalar_type": "0x05",
     "text": "焰星·囊萤"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 889,
     "scalar_type": "0x05",
     "text": "囊住萤火虫光，一闪一闪！可配戴在面部的面饰。在使用某些时装时无法佩戴。（发箍男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 498960,
    "field_refs": [
     "player_module_appear_data.row_key=498960",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=952",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=889"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_499060",
   "row_key": 499060,
   "name": "远星·皇冠",
   "display_name": "远星·皇冠",
   "desc": "#f(5)远星乱斗冠军专属面饰#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3379001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 3379,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    499060,
    499061,
    499062,
    499063,
    499064,
    499065,
    499066
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 499060,
     "text": "远星·皇冠",
     "field_chs_slot": 7,
     "value_chs_slot": 1012,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 499061,
     "text": "远星·皇冠-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1997,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 499062,
     "text": "远星·皇冠-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1999,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 499063,
     "text": "远星·皇冠-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 2000,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 499064,
     "text": "远星·皇冠-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 2001,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 499065,
     "text": "远星·皇冠-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1996,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 499066,
     "text": "远星·皇冠-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1998,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1012,
     "scalar_type": "0x05",
     "text": "远星·皇冠"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 150,
     "scalar_type": "0x05",
     "text": "#f(5)远星乱斗冠军专属面饰#n。可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 499060,
    "field_refs": [
     "player_module_appear_data.row_key=499060",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1012",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=150"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_499260",
   "row_key": 499260,
   "name": "破晓刃影",
   "display_name": "破晓刃影",
   "desc": "#f(5)青渊溯白主题面饰#n。#r风雪凛冽，刀锋不悔，我们终会以新生的姿态重逢。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3381001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 3381,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    499260,
    499261,
    499262,
    499263,
    499264,
    499265,
    499266
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 499260,
     "text": "破晓刃影",
     "field_chs_slot": 7,
     "value_chs_slot": 972,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 499261,
     "text": "破晓刃影-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1759,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 499262,
     "text": "破晓刃影-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1761,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 499263,
     "text": "破晓刃影-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1762,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 499264,
     "text": "破晓刃影-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1763,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 499265,
     "text": "破晓刃影-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1758,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 499266,
     "text": "破晓刃影-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1760,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 972,
     "scalar_type": "0x05",
     "text": "破晓刃影"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 30,
     "scalar_type": "0x05",
     "text": "#f(5)青渊溯白主题面饰#n。#r风雪凛冽，刀锋不悔，我们终会以新生的姿态重逢。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 499260,
    "field_refs": [
     "player_module_appear_data.row_key=499260",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=972",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=30"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_499510",
   "row_key": 499510,
   "name": "破晓刃影-炽",
   "display_name": "破晓刃影-炽",
   "desc": "#f(5)青渊溯白主题面饰#n。#r风雪凛冽，刀锋不悔，我们终会以新生的姿态重逢。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3381002",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 3381,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    499510,
    499511,
    499512,
    499513,
    499514,
    499515,
    499516
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 499510,
     "text": "破晓刃影-炽",
     "field_chs_slot": 7,
     "value_chs_slot": 974,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 499511,
     "text": "破晓刃影-炽-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1771,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 499512,
     "text": "破晓刃影-炽-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1773,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 499513,
     "text": "破晓刃影-炽-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1774,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 499514,
     "text": "破晓刃影-炽-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1775,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 499515,
     "text": "破晓刃影-炽-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1770,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 499516,
     "text": "破晓刃影-炽-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1772,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 974,
     "scalar_type": "0x05",
     "text": "破晓刃影-炽"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 30,
     "scalar_type": "0x05",
     "text": "#f(5)青渊溯白主题面饰#n。#r风雪凛冽，刀锋不悔，我们终会以新生的姿态重逢。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 499510,
    "field_refs": [
     "player_module_appear_data.row_key=499510",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=974",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=30"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_499760",
   "row_key": 499760,
   "name": "破晓刃影-墨",
   "display_name": "破晓刃影-墨",
   "desc": "#f(5)青渊溯白主题面饰#n。#r风雪凛冽，刀锋不悔，我们终会以新生的姿态重逢。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_3381003",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 3381,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    499760,
    499761,
    499762,
    499763,
    499764,
    499765,
    499766
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 499760,
     "text": "破晓刃影-墨",
     "field_chs_slot": 7,
     "value_chs_slot": 973,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 499761,
     "text": "破晓刃影-墨-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1765,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 499762,
     "text": "破晓刃影-墨-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1767,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 499763,
     "text": "破晓刃影-墨-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1768,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 499764,
     "text": "破晓刃影-墨-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1769,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 499765,
     "text": "破晓刃影-墨-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1764,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 499766,
     "text": "破晓刃影-墨-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1766,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 973,
     "scalar_type": "0x05",
     "text": "破晓刃影-墨"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 30,
     "scalar_type": "0x05",
     "text": "#f(5)青渊溯白主题面饰#n。#r风雪凛冽，刀锋不悔，我们终会以新生的姿态重逢。#r可配戴在面部的面饰。在使用某些时装时无法佩戴。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 499760,
    "field_refs": [
     "player_module_appear_data.row_key=499760",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=973",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=30"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_741270120",
   "row_key": 741270120,
   "name": "漫天星辰",
   "display_name": "漫天星辰",
   "desc": "#f(5)头上花如天上星，簪于鬓畔，远行人便不会迷路。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4127001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4127,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    741270120,
    741270121,
    741270122,
    741270123,
    741270124,
    741270125,
    741270126
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 741270120,
     "text": "漫天星辰",
     "field_chs_slot": 7,
     "value_chs_slot": 947,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 741270121,
     "text": "漫天星辰-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1625,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 741270122,
     "text": "漫天星辰-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1627,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 741270123,
     "text": "漫天星辰-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1628,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 741270124,
     "text": "漫天星辰-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1629,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 741270125,
     "text": "漫天星辰-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1624,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 741270126,
     "text": "漫天星辰-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1626,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 947,
     "scalar_type": "0x05",
     "text": "漫天星辰"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 88,
     "scalar_type": "0x05",
     "text": "#f(5)头上花如天上星，簪于鬓畔，远行人便不会迷路。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 741270120,
    "field_refs": [
     "player_module_appear_data.row_key=741270120",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=947",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=88"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_741280120",
   "row_key": 741280120,
   "name": "灰太狼的帽子",
   "display_name": "灰太狼的帽子",
   "desc": "一顶帽子补了又补，灰太狼说这是限量款。「明日之后×喜羊羊与灰太狼」联动限定外观（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4128001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 1,
   "charm_value": 10,
   "model_id": 4128,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    741280120,
    741280121,
    741280122,
    741280123,
    741280124,
    741280125,
    741280126
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 741280120,
     "text": "灰太狼的帽子",
     "field_chs_slot": 7,
     "value_chs_slot": 948,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 741280121,
     "text": "灰太狼的帽子-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1631,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 741280122,
     "text": "灰太狼的帽子-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1633,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 741280123,
     "text": "灰太狼的帽子-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1634,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 741280124,
     "text": "灰太狼的帽子-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1635,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 741280125,
     "text": "灰太狼的帽子-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1630,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 741280126,
     "text": "灰太狼的帽子-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1632,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 948,
     "scalar_type": "0x05",
     "text": "灰太狼的帽子"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 857,
     "scalar_type": "0x05",
     "text": "一顶帽子补了又补，灰太狼说这是限量款。「明日之后×喜羊羊与灰太狼」联动限定外观（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 741280120,
    "field_refs": [
     "player_module_appear_data.row_key=741280120",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=948",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=857"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_741290120",
   "row_key": 741290120,
   "name": "狼堡冠冕",
   "display_name": "狼堡冠冕",
   "desc": "皇冠一戴，气场全开。「明日之后×喜羊羊与灰太狼」联动限定外观（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4129001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 1,
   "charm_value": 50,
   "model_id": 4129,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    741290120,
    741290121,
    741290122,
    741290123,
    741290124,
    741290125,
    741290126
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 741290120,
     "text": "狼堡冠冕",
     "field_chs_slot": 7,
     "value_chs_slot": 957,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 741290121,
     "text": "狼堡冠冕-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1686,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 741290122,
     "text": "狼堡冠冕-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1688,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 741290123,
     "text": "狼堡冠冕-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1689,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 741290124,
     "text": "狼堡冠冕-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1690,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 741290125,
     "text": "狼堡冠冕-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1685,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 741290126,
     "text": "狼堡冠冕-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1687,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 957,
     "scalar_type": "0x05",
     "text": "狼堡冠冕"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 970,
     "scalar_type": "0x05",
     "text": "皇冠一戴，气场全开。「明日之后×喜羊羊与灰太狼」联动限定外观（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 741290120,
    "field_refs": [
     "player_module_appear_data.row_key=741290120",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=957",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=970"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_741320120",
   "row_key": 741320120,
   "name": "人间精灵",
   "display_name": "人间精灵",
   "desc": "#f(5)你是人间的精灵，踩着星光踏入我的梦境。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4132001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4132,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    741320120,
    741320121,
    741320122,
    741320123,
    741320124,
    741320125,
    741320126
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 741320120,
     "text": "人间精灵",
     "field_chs_slot": 7,
     "value_chs_slot": 864,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 741320121,
     "text": "人间精灵-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1166,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 741320122,
     "text": "人间精灵-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1168,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 741320123,
     "text": "人间精灵-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1169,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 741320124,
     "text": "人间精灵-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1170,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 741320125,
     "text": "人间精灵-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1165,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 741320126,
     "text": "人间精灵-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1167,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 864,
     "scalar_type": "0x05",
     "text": "人间精灵"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 65,
     "scalar_type": "0x05",
     "text": "#f(5)你是人间的精灵，踩着星光踏入我的梦境。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 741320120,
    "field_refs": [
     "player_module_appear_data.row_key=741320120",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=864",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=65"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_741330120",
   "row_key": 741330120,
   "name": "感到鸭力",
   "display_name": "感到鸭力",
   "desc": "#f(5)压力大的时候，不如看看本鸭吖。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4133001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4133,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    741330120,
    741330121,
    741330122,
    741330123,
    741330124,
    741330125,
    741330126
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 741330120,
     "text": "感到鸭力",
     "field_chs_slot": 7,
     "value_chs_slot": 904,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 741330121,
     "text": "感到鸭力-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1400,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 741330122,
     "text": "感到鸭力-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1402,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 741330123,
     "text": "感到鸭力-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1403,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 741330124,
     "text": "感到鸭力-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1404,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 741330125,
     "text": "感到鸭力-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1399,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 741330126,
     "text": "感到鸭力-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1401,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 904,
     "scalar_type": "0x05",
     "text": "感到鸭力"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 76,
     "scalar_type": "0x05",
     "text": "#f(5)压力大的时候，不如看看本鸭吖。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 741330120,
    "field_refs": [
     "player_module_appear_data.row_key=741330120",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=904",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=76"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_741340120",
   "row_key": 741340120,
   "name": "蓝蓝可海星",
   "display_name": "蓝蓝可海星",
   "desc": "#f(5)深水里来的，颜色比天还蓝。也不知道它怎么游到浅滩上来了，总之现在住在头顶上，看起来挺满意。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4134001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4134,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    741340120,
    741340121,
    741340122,
    741340123,
    741340124,
    741340125,
    741340126
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 741340120,
     "text": "蓝蓝可海星",
     "field_chs_slot": 7,
     "value_chs_slot": 1000,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 741340121,
     "text": "蓝蓝可海星-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1924,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 741340122,
     "text": "蓝蓝可海星-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1926,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 741340123,
     "text": "蓝蓝可海星-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1927,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 741340124,
     "text": "蓝蓝可海星-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1928,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 741340125,
     "text": "蓝蓝可海星-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1923,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 741340126,
     "text": "蓝蓝可海星-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1925,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1000,
     "scalar_type": "0x05",
     "text": "蓝蓝可海星"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 124,
     "scalar_type": "0x05",
     "text": "#f(5)深水里来的，颜色比天还蓝。也不知道它怎么游到浅滩上来了，总之现在住在头顶上，看起来挺满意。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 741340120,
    "field_refs": [
     "player_module_appear_data.row_key=741340120",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1000",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=124"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_741340220",
   "row_key": 741340220,
   "name": "黄黄可海星",
   "display_name": "黄黄可海星",
   "desc": "#f(5)金灿灿的，跟礁石颜色差不多，不留神就踩过去了。幸好没踩，捡起来一看，圆滚滚的，舍不得放回去。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4134002",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4134,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    741340220,
    741340221,
    741340222,
    741340223,
    741340224,
    741340225,
    741340226
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 741340220,
     "text": "黄黄可海星",
     "field_chs_slot": 7,
     "value_chs_slot": 1029,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 741340221,
     "text": "黄黄可海星-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 2089,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 741340222,
     "text": "黄黄可海星-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 2091,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 741340223,
     "text": "黄黄可海星-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 2092,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 741340224,
     "text": "黄黄可海星-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 2093,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 741340225,
     "text": "黄黄可海星-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 2088,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 741340226,
     "text": "黄黄可海星-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 2090,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1029,
     "scalar_type": "0x05",
     "text": "黄黄可海星"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 152,
     "scalar_type": "0x05",
     "text": "#f(5)金灿灿的，跟礁石颜色差不多，不留神就踩过去了。幸好没踩，捡起来一看，圆滚滚的，舍不得放回去。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 741340220,
    "field_refs": [
     "player_module_appear_data.row_key=741340220",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1029",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=152"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_741340320",
   "row_key": 741340320,
   "name": "红红可海星",
   "display_name": "红红可海星",
   "desc": "#f(5)退潮后礁石上晒太阳的小家伙，红得很显眼，老远就能瞧见。捡回来做了发饰——它好像也挺乐意的。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4134003",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4134,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    741340320,
    741340321,
    741340322,
    741340323,
    741340324,
    741340325,
    741340326
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 741340320,
     "text": "红红可海星",
     "field_chs_slot": 7,
     "value_chs_slot": 979,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 741340321,
     "text": "红红可海星-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1803,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 741340322,
     "text": "红红可海星-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1805,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 741340323,
     "text": "红红可海星-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1806,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 741340324,
     "text": "红红可海星-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1807,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 741340325,
     "text": "红红可海星-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1802,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 741340326,
     "text": "红红可海星-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1804,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 979,
     "scalar_type": "0x05",
     "text": "红红可海星"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 151,
     "scalar_type": "0x05",
     "text": "#f(5)退潮后礁石上晒太阳的小家伙，红得很显眼，老远就能瞧见。捡回来做了发饰——它好像也挺乐意的。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 741340320,
    "field_refs": [
     "player_module_appear_data.row_key=741340320",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=979",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=151"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_741370120",
   "row_key": 741370120,
   "name": "刑天面甲",
   "display_name": "刑天面甲",
   "desc": "承刑天不屈战意，绝境之中并肩坚守求生防线。「明日之后×铠甲勇士」联动限定外观（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4137001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4137,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    741370120,
    741370121,
    741370122,
    741370123,
    741370124,
    741370125,
    741370126
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 741370120,
     "text": "刑天面甲",
     "field_chs_slot": 7,
     "value_chs_slot": 878,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 741370121,
     "text": "刑天面甲-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1247,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 741370122,
     "text": "刑天面甲-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1249,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 741370123,
     "text": "刑天面甲-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1250,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 741370124,
     "text": "刑天面甲-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1251,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 741370125,
     "text": "刑天面甲-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1246,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 741370126,
     "text": "刑天面甲-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1248,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 878,
     "scalar_type": "0x05",
     "text": "刑天面甲"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 909,
     "scalar_type": "0x05",
     "text": "承刑天不屈战意，绝境之中并肩坚守求生防线。「明日之后×铠甲勇士」联动限定外观（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 741370120,
    "field_refs": [
     "player_module_appear_data.row_key=741370120",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=878",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=909"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_741380120",
   "row_key": 741380120,
   "name": "飞影锋眸",
   "display_name": "飞影锋眸",
   "desc": "佩戴此镜，可于疾行之时洞悉四方危机。「明日之后×铠甲勇士」联动限定外观（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4138001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4138,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    741380120,
    741380121,
    741380122,
    741380123,
    741380124,
    741380125,
    741380126
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 741380120,
     "text": "飞影锋眸",
     "field_chs_slot": 7,
     "value_chs_slot": 1026,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 741380121,
     "text": "飞影锋眸-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 2071,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 741380122,
     "text": "飞影锋眸-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 2073,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 741380123,
     "text": "飞影锋眸-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 2074,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 741380124,
     "text": "飞影锋眸-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 2075,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 741380125,
     "text": "飞影锋眸-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 2070,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 741380126,
     "text": "飞影锋眸-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 2072,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1026,
     "scalar_type": "0x05",
     "text": "飞影锋眸"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 869,
     "scalar_type": "0x05",
     "text": "佩戴此镜，可于疾行之时洞悉四方危机。「明日之后×铠甲勇士」联动限定外观（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 741380120,
    "field_refs": [
     "player_module_appear_data.row_key=741380120",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1026",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=869"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_741390120",
   "row_key": 741390120,
   "name": "瑞秋的头饰",
   "display_name": "瑞秋的头饰",
   "desc": "瑞秋用亲手摘的小草编成的发饰，有秋日森林里的味道。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4139001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4139,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    741390120,
    741390121,
    741390122,
    741390123,
    741390124,
    741390125,
    741390126
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 741390120,
     "text": "瑞秋的头饰",
     "field_chs_slot": 7,
     "value_chs_slot": 963,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 741390121,
     "text": "瑞秋的头饰-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1716,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 741390122,
     "text": "瑞秋的头饰-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1718,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 741390123,
     "text": "瑞秋的头饰-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1719,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 741390124,
     "text": "瑞秋的头饰-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1720,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 741390125,
     "text": "瑞秋的头饰-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1715,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 741390126,
     "text": "瑞秋的头饰-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1717,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 963,
     "scalar_type": "0x05",
     "text": "瑞秋的头饰"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 962,
     "scalar_type": "0x05",
     "text": "瑞秋用亲手摘的小草编成的发饰，有秋日森林里的味道。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 741390120,
    "field_refs": [
     "player_module_appear_data.row_key=741390120",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=963",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=962"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_741400120",
   "row_key": 741400120,
   "name": "旧日低语",
   "display_name": "旧日低语",
   "desc": "一顶硬邦邦的旧皮帽，边缘磨出了深色皮茬，帽檐上横着一道不深不浅的刀痕——老鬼说是某次\"价格没谈拢\"留下的纪念。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4140001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4140,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    741400120,
    741400121,
    741400122,
    741400123,
    741400124,
    741400125,
    741400126
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 741400120,
     "text": "旧日低语",
     "field_chs_slot": 7,
     "value_chs_slot": 917,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 741400121,
     "text": "旧日低语-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1460,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 741400122,
     "text": "旧日低语-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1462,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 741400123,
     "text": "旧日低语-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1463,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 741400124,
     "text": "旧日低语-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1464,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 741400125,
     "text": "旧日低语-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1459,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 741400126,
     "text": "旧日低语-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1461,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 917,
     "scalar_type": "0x05",
     "text": "旧日低语"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 858,
     "scalar_type": "0x05",
     "text": "一顶硬邦邦的旧皮帽，边缘磨出了深色皮茬，帽檐上横着一道不深不浅的刀痕——老鬼说是某次\"价格没谈拢\"留下的纪念。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 741400120,
    "field_refs": [
     "player_module_appear_data.row_key=741400120",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=917",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=858"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_741410120",
   "row_key": 741410120,
   "name": "旧日裂隙",
   "display_name": "旧日裂隙",
   "desc": "一副偏光墨镜，镜架一侧换过螺丝，拧得不太对称——老鬼自己修的。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4141001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4141,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    741410120,
    741410121,
    741410122,
    741410123,
    741410124,
    741410125,
    741410126
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 741410120,
     "text": "旧日裂隙",
     "field_chs_slot": 7,
     "value_chs_slot": 918,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 741410121,
     "text": "旧日裂隙-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1466,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 741410122,
     "text": "旧日裂隙-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1468,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 741410123,
     "text": "旧日裂隙-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1469,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 741410124,
     "text": "旧日裂隙-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1470,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 741410125,
     "text": "旧日裂隙-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1465,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 741410126,
     "text": "旧日裂隙-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1467,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 918,
     "scalar_type": "0x05",
     "text": "旧日裂隙"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 851,
     "scalar_type": "0x05",
     "text": "一副偏光墨镜，镜架一侧换过螺丝，拧得不太对称——老鬼自己修的。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 741410120,
    "field_refs": [
     "player_module_appear_data.row_key=741410120",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=918",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=851"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_741420120",
   "row_key": 741420120,
   "name": "咸水客眼镜",
   "display_name": "咸水客眼镜",
   "desc": "#f(5)一副偏光镜片的钓鱼眼镜，能有效过滤海面反光，让你在刺眼的日头下也能看清浮标的每一次颤动。暗港工坊出品，结实耐造，海风和盐雾都奈何不了它。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4142001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4142,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    741420120,
    741420121,
    741420122,
    741420123,
    741420124,
    741420125,
    741420126
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 741420120,
     "text": "咸水客眼镜",
     "field_chs_slot": 7,
     "value_chs_slot": 886,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 741420121,
     "text": "咸水客眼镜-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1295,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 741420122,
     "text": "咸水客眼镜-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1297,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 741420123,
     "text": "咸水客眼镜-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1298,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 741420124,
     "text": "咸水客眼镜-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1299,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 741420125,
     "text": "咸水客眼镜-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1294,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 741420126,
     "text": "咸水客眼镜-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1296,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 886,
     "scalar_type": "0x05",
     "text": "咸水客眼镜"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 45,
     "scalar_type": "0x05",
     "text": "#f(5)一副偏光镜片的钓鱼眼镜，能有效过滤海面反光，让你在刺眼的日头下也能看清浮标的每一次颤动。暗港工坊出品，结实耐造，海风和盐雾都奈何不了它。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 741420120,
    "field_refs": [
     "player_module_appear_data.row_key=741420120",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=886",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=45"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_741430120",
   "row_key": 741430120,
   "name": "咸水客便帽",
   "display_name": "咸水客便帽",
   "desc": "#f(5)一顶宽檐遮阳钓鱼帽，透气轻便，长时间海上作业也不闷热。帽檐够宽，晒不到脸；帽带够紧，海风吹不跑。暗港老手人手一顶，没什么花哨的——好用就行。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4143001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4143,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    741430120,
    741430121,
    741430122,
    741430123,
    741430124,
    741430125,
    741430126
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 741430120,
     "text": "咸水客便帽",
     "field_chs_slot": 7,
     "value_chs_slot": 885,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 741430121,
     "text": "咸水客便帽-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1289,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 741430122,
     "text": "咸水客便帽-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1291,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 741430123,
     "text": "咸水客便帽-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1292,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 741430124,
     "text": "咸水客便帽-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1293,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 741430125,
     "text": "咸水客便帽-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1288,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 741430126,
     "text": "咸水客便帽-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1290,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 885,
     "scalar_type": "0x05",
     "text": "咸水客便帽"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 52,
     "scalar_type": "0x05",
     "text": "#f(5)一顶宽檐遮阳钓鱼帽，透气轻便，长时间海上作业也不闷热。帽檐够宽，晒不到脸；帽带够紧，海风吹不跑。暗港老手人手一顶，没什么花哨的——好用就行。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 741430120,
    "field_refs": [
     "player_module_appear_data.row_key=741430120",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=885",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=52"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_741440120",
   "row_key": 741440120,
   "name": "霜棘窥光",
   "display_name": "霜棘窥光",
   "desc": "霜枝覆眼，棘影窥光。行过长夜之人，方知冷锋亦可照见归途。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4144001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 4144,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    741440120,
    741440121,
    741440122,
    741440123,
    741440124,
    741440125,
    741440126
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 741440120,
     "text": "霜棘窥光",
     "field_chs_slot": 7,
     "value_chs_slot": 1019,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 741440121,
     "text": "霜棘窥光-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 2035,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 741440122,
     "text": "霜棘窥光-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 2037,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 741440123,
     "text": "霜棘窥光-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 2038,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 741440124,
     "text": "霜棘窥光-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 2039,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 741440125,
     "text": "霜棘窥光-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 2034,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 741440126,
     "text": "霜棘窥光-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 2036,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 1019,
     "scalar_type": "0x05",
     "text": "霜棘窥光"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 1018,
     "scalar_type": "0x05",
     "text": "霜枝覆眼，棘影窥光。行过长夜之人，方知冷锋亦可照见归途。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 741440120,
    "field_refs": [
     "player_module_appear_data.row_key=741440120",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=1019",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=1018"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_741450120",
   "row_key": 741450120,
   "name": "流虹视界",
   "display_name": "流虹视界",
   "desc": "戴上它，前路被染成一场明亮的冒险。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4145001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4145,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    741450120,
    741450121,
    741450122,
    741450123,
    741450124,
    741450125,
    741450126
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 741450120,
     "text": "流虹视界",
     "field_chs_slot": 7,
     "value_chs_slot": 943,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 741450121,
     "text": "流虹视界-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1600,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 741450122,
     "text": "流虹视界-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1602,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 741450123,
     "text": "流虹视界-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1603,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 741450124,
     "text": "流虹视界-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1604,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 741450125,
     "text": "流虹视界-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1599,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 741450126,
     "text": "流虹视界-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1601,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 943,
     "scalar_type": "0x05",
     "text": "流虹视界"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 907,
     "scalar_type": "0x05",
     "text": "戴上它，前路被染成一场明亮的冒险。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 741450120,
    "field_refs": [
     "player_module_appear_data.row_key=741450120",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=943",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=907"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_741460120",
   "row_key": 741460120,
   "name": "王面面具",
   "display_name": "王面面具",
   "desc": "面具之下，另有乾坤。「明日之后×斩神」联动限定外观（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4146001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4146,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    741460120,
    741460121,
    741460122,
    741460123,
    741460124,
    741460125,
    741460126
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 741460120,
     "text": "王面面具",
     "field_chs_slot": 7,
     "value_chs_slot": 960,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 741460121,
     "text": "王面面具-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1704,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 741460122,
     "text": "王面面具-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1706,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 741460123,
     "text": "王面面具-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1707,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 741460124,
     "text": "王面面具-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1708,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 741460125,
     "text": "王面面具-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1703,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 741460126,
     "text": "王面面具-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1705,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 960,
     "scalar_type": "0x05",
     "text": "王面面具"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 1020,
     "scalar_type": "0x05",
     "text": "面具之下，另有乾坤。「明日之后×斩神」联动限定外观（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 741460120,
    "field_refs": [
     "player_module_appear_data.row_key=741460120",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=960",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=1020"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_741470120",
   "row_key": 741470120,
   "name": "星穹环冕",
   "display_name": "星穹环冕",
   "desc": "#f(5)光自寰宇溯来，为末世苍穹再点一颗夜神之星。「明日之后×斩神」联动限定外观（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4147001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 200,
   "model_id": 4147,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    741470120,
    741470121,
    741470122,
    741470123,
    741470124,
    741470125,
    741470126
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 741470120,
     "text": "星穹环冕",
     "field_chs_slot": 7,
     "value_chs_slot": 923,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 741470121,
     "text": "星穹环冕-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1490,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 741470122,
     "text": "星穹环冕-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1492,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 741470123,
     "text": "星穹环冕-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1493,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 741470124,
     "text": "星穹环冕-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1494,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 741470125,
     "text": "星穹环冕-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1489,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 741470126,
     "text": "星穹环冕-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1491,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 923,
     "scalar_type": "0x05",
     "text": "星穹环冕"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 71,
     "scalar_type": "0x05",
     "text": "#f(5)光自寰宇溯来，为末世苍穹再点一颗夜神之星。「明日之后×斩神」联动限定外观（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 741470120,
    "field_refs": [
     "player_module_appear_data.row_key=741470120",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=923",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=71"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_741480120",
   "row_key": 741480120,
   "name": "炽天之冕",
   "display_name": "炽天之冕",
   "desc": "#f(5)炽焰凝冕，神威加身，末世纷争自此定裁。「明日之后×斩神」联动限定外观（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4148001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 4148,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    741480120,
    741480121,
    741480122,
    741480123,
    741480124,
    741480125,
    741480126
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 741480120,
     "text": "炽天之冕",
     "field_chs_slot": 7,
     "value_chs_slot": 949,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 741480121,
     "text": "炽天之冕-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1637,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 741480122,
     "text": "炽天之冕-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1639,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 741480123,
     "text": "炽天之冕-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1640,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 741480124,
     "text": "炽天之冕-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1641,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 741480125,
     "text": "炽天之冕-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1636,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 741480126,
     "text": "炽天之冕-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1638,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 949,
     "scalar_type": "0x05",
     "text": "炽天之冕"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 125,
     "scalar_type": "0x05",
     "text": "#f(5)炽焰凝冕，神威加身，末世纷争自此定裁。「明日之后×斩神」联动限定外观（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 741480120,
    "field_refs": [
     "player_module_appear_data.row_key=741480120",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=949",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=125"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_741490120",
   "row_key": 741490120,
   "name": "晴空泡泡",
   "display_name": "晴空泡泡",
   "desc": "把晴天吹成一颗泡泡，轻轻飘进心里。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4149001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 100,
   "model_id": 4149,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    741490120,
    741490121,
    741490122,
    741490123,
    741490124,
    741490125,
    741490126
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 741490120,
     "text": "晴空泡泡",
     "field_chs_slot": 7,
     "value_chs_slot": 926,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 741490121,
     "text": "晴空泡泡-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1502,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 741490122,
     "text": "晴空泡泡-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1504,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 741490123,
     "text": "晴空泡泡-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1505,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 741490124,
     "text": "晴空泡泡-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1506,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 741490125,
     "text": "晴空泡泡-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1501,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 741490126,
     "text": "晴空泡泡-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1503,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 926,
     "scalar_type": "0x05",
     "text": "晴空泡泡"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 910,
     "scalar_type": "0x05",
     "text": "把晴天吹成一颗泡泡，轻轻飘进心里。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 741490120,
    "field_refs": [
     "player_module_appear_data.row_key=741490120",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=926",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=910"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_741500120",
   "row_key": 741500120,
   "name": "甜莓喵喵",
   "display_name": "甜莓喵喵",
   "desc": "甜莓圆圆，喵喵绵绵，把好心情挂在发间。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4150001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 15,
   "model_id": 4150,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    741500120,
    741500121,
    741500122,
    741500123,
    741500124,
    741500125,
    741500126
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 741500120,
     "text": "甜莓喵喵",
     "field_chs_slot": 7,
     "value_chs_slot": 965,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 741500121,
     "text": "甜莓喵喵-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1728,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 741500122,
     "text": "甜莓喵喵-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1730,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 741500123,
     "text": "甜莓喵喵-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1731,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 741500124,
     "text": "甜莓喵喵-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1732,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 741500125,
     "text": "甜莓喵喵-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1727,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 741500126,
     "text": "甜莓喵喵-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1729,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 965,
     "scalar_type": "0x05",
     "text": "甜莓喵喵"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 966,
     "scalar_type": "0x05",
     "text": "甜莓圆圆，喵喵绵绵，把好心情挂在发间。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 741500120,
    "field_refs": [
     "player_module_appear_data.row_key=741500120",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=965",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=966"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_741510120",
   "row_key": 741510120,
   "name": "垂垂兔耳",
   "display_name": "垂垂兔耳",
   "desc": "#f(5)困得睁不开眼，一只耳朵还想站岗，另一只已经先垂下来了。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4151001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4151,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    741510120,
    741510121,
    741510122,
    741510123,
    741510124,
    741510125,
    741510126
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 741510120,
     "text": "垂垂兔耳",
     "field_chs_slot": 7,
     "value_chs_slot": 892,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 741510121,
     "text": "垂垂兔耳-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1326,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 741510122,
     "text": "垂垂兔耳-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1328,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 741510123,
     "text": "垂垂兔耳-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1329,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 741510124,
     "text": "垂垂兔耳-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1330,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 741510125,
     "text": "垂垂兔耳-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1325,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 741510126,
     "text": "垂垂兔耳-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1327,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 892,
     "scalar_type": "0x05",
     "text": "垂垂兔耳"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 82,
     "scalar_type": "0x05",
     "text": "#f(5)困得睁不开眼，一只耳朵还想站岗，另一只已经先垂下来了。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 741510120,
    "field_refs": [
     "player_module_appear_data.row_key=741510120",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=892",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=82"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_741520120",
   "row_key": 741520120,
   "name": "桂影花枝",
   "display_name": "桂影花枝",
   "desc": "一缕甜香，萦落鬓边。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4152001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 50,
   "model_id": 4152,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    741520120,
    741520121,
    741520122,
    741520123,
    741520124,
    741520125,
    741520126
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 741520120,
     "text": "桂影花枝",
     "field_chs_slot": 7,
     "value_chs_slot": 934,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 741520121,
     "text": "桂影花枝-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1545,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 741520122,
     "text": "桂影花枝-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1547,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 741520123,
     "text": "桂影花枝-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1548,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 741520124,
     "text": "桂影花枝-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1549,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 741520125,
     "text": "桂影花枝-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1544,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 741520126,
     "text": "桂影花枝-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1546,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 934,
     "scalar_type": "0x05",
     "text": "桂影花枝"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 856,
     "scalar_type": "0x05",
     "text": "一缕甜香，萦落鬓边。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 741520120,
    "field_refs": [
     "player_module_appear_data.row_key=741520120",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=934",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=856"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_741540120",
   "row_key": 741540120,
   "name": "喵影星帷",
   "display_name": "喵影星帷",
   "desc": "月下猫影轻垂成帷，万圣夜的神秘悄然拉开——（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4154001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 350,
   "model_id": 4154,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    741540120,
    741540121,
    741540122,
    741540123,
    741540124,
    741540125,
    741540126
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 741540120,
     "text": "喵影星帷",
     "field_chs_slot": 7,
     "value_chs_slot": 888,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 741540121,
     "text": "喵影星帷-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1307,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 741540122,
     "text": "喵影星帷-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1309,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 741540123,
     "text": "喵影星帷-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1310,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 741540124,
     "text": "喵影星帷-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1311,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 741540125,
     "text": "喵影星帷-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1306,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 741540126,
     "text": "喵影星帷-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1308,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 888,
     "scalar_type": "0x05",
     "text": "喵影星帷"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 928,
     "scalar_type": "0x05",
     "text": "月下猫影轻垂成帷，万圣夜的神秘悄然拉开——（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 741540120,
    "field_refs": [
     "player_module_appear_data.row_key=741540120",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=888",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=928"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_741600120",
   "row_key": 741600120,
   "name": "寻宝雷达",
   "display_name": "寻宝雷达",
   "desc": "#f(5)戴上它，地图没看清，宝藏先看见。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4160001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4160,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    741600120,
    741600121,
    741600122,
    741600123,
    741600124,
    741600125,
    741600126
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 741600120,
     "text": "寻宝雷达",
     "field_chs_slot": 7,
     "value_chs_slot": 897,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 741600121,
     "text": "寻宝雷达-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1356,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 741600122,
     "text": "寻宝雷达-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1358,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 741600123,
     "text": "寻宝雷达-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1359,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 741600124,
     "text": "寻宝雷达-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1360,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 741600125,
     "text": "寻宝雷达-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1355,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 741600126,
     "text": "寻宝雷达-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1357,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 897,
     "scalar_type": "0x05",
     "text": "寻宝雷达"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 104,
     "scalar_type": "0x05",
     "text": "#f(5)戴上它，地图没看清，宝藏先看见。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 741600120,
    "field_refs": [
     "player_module_appear_data.row_key=741600120",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=897",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=104"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_741610120",
   "row_key": 741610120,
   "name": "胡风唤雨",
   "display_name": "胡风唤雨",
   "desc": "#f(5)戴上它，风浪听不听话不知道，至少看起来很会下令。（面饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4161001",
   "part_type": "face",
   "part_code": 20001,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4161,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    3,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    741610120,
    741610121,
    741610122,
    741610123,
    741610124,
    741610125,
    741610126
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 741610120,
     "text": "胡风唤雨",
     "field_chs_slot": 7,
     "value_chs_slot": 994,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 741610121,
     "text": "胡风唤雨-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1888,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 741610122,
     "text": "胡风唤雨-3天",
     "field_chs_slot": 7,
     "value_chs_slot": 1890,
     "duration_days": 3,
     "schema": 42
    },
    {
     "row_key": 741610123,
     "text": "胡风唤雨-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1891,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 741610124,
     "text": "胡风唤雨-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1892,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 741610125,
     "text": "胡风唤雨-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1887,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 741610126,
     "text": "胡风唤雨-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1889,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 994,
     "scalar_type": "0x05",
     "text": "胡风唤雨"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 105,
     "scalar_type": "0x05",
     "text": "#f(5)戴上它，风浪听不听话不知道，至少看起来很会下令。（面饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 741610120,
    "field_refs": [
     "player_module_appear_data.row_key=741610120",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=994",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=105"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  },
  {
   "id": "face_741620120",
   "row_key": 741620120,
   "name": "一团乱",
   "display_name": "一团乱",
   "desc": "#f(5)航线没看懂，造型也没看懂。（头饰男女表现不同，以穿戴效果为准）",
   "icon": "ui/item_icon/icon_h_m_4162001",
   "part_type": "face",
   "part_code": 2,
   "sort_key": 4,
   "charm_value": 10,
   "model_id": 4162,
   "valid_days": null,
   "has_permanent": true,
   "duration_days": [
    1,
    5,
    7,
    14,
    30
   ],
   "all_row_keys": [
    741620120,
    741620121,
    741620123,
    741620124,
    741620125,
    741620126
   ],
   "schema_refs": [
    42
   ],
   "variants": [
    {
     "row_key": 741620120,
     "text": "一团乱",
     "field_chs_slot": 7,
     "value_chs_slot": 854,
     "duration_days": null,
     "schema": 42
    },
    {
     "row_key": 741620121,
     "text": "一团乱-1天",
     "field_chs_slot": 7,
     "value_chs_slot": 1116,
     "duration_days": 1,
     "schema": 42
    },
    {
     "row_key": 741620123,
     "text": "一团乱-5天",
     "field_chs_slot": 7,
     "value_chs_slot": 1119,
     "duration_days": 5,
     "schema": 42
    },
    {
     "row_key": 741620124,
     "text": "一团乱-7天",
     "field_chs_slot": 7,
     "value_chs_slot": 1120,
     "duration_days": 7,
     "schema": 42
    },
    {
     "row_key": 741620125,
     "text": "一团乱-14天",
     "field_chs_slot": 7,
     "value_chs_slot": 1115,
     "duration_days": 14,
     "schema": 42
    },
    {
     "row_key": 741620126,
     "text": "一团乱-30天",
     "field_chs_slot": 7,
     "value_chs_slot": 1117,
     "duration_days": 30,
     "schema": 42
    }
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "Documents current-snapshot player_module_appear_data row text (column-level name/desc 0x05 slots); not availability or acquisition evidence",
   "text_provenance": {
    "name": {
     "field_chs_slot": 7,
     "value_chs_slot": 854,
     "scalar_type": "0x05",
     "text": "一团乱"
    },
    "desc": {
     "field_chs_slot": 1,
     "value_chs_slot": 143,
     "scalar_type": "0x05",
     "text": "#f(5)航线没看懂，造型也没看懂。（头饰男女表现不同，以穿戴效果为准）"
    }
   },
   "provenance": {
    "source_lock_sha256": "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9",
    "source_entries": [
     {
      "entry_index": 4212,
      "file_id": "24947DBB72A943E5",
      "decoded_sha256": "a7127f8675c48c4af7fa442ef931f5211427ad683aef8455c561f94d629c3f30",
      "role": "player_module_appear_data_base"
     },
     {
      "entry_index": 12702,
      "file_id": "6CD197C9670A961C",
      "decoded_sha256": "b9a6c1782a98500c5dab055c8d200a39e710d635db545001ce51aa2370949124",
      "role": "player_module_appear_data_chs"
     }
    ],
    "table": "player_module_appear_data",
    "row_key": 741620120,
    "field_refs": [
     "player_module_appear_data.row_key=741620120",
     "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
     "player_module_appear_data.name CHS field_slot=7 value_slot=854",
     "player_module_appear_data.desc CHS field_slot=1 value_slot=143"
    ],
    "name_source": "same-snapshot player_module_appear_data 0x05 CHS text replayed with field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
   }
  }
 ],
 "stats": {
  "source_rows": 1173,
  "named_rows": 1173,
  "unbound_rows": 0,
  "catalog_entries": 186
 }
};
