window.WIKI_BOARD_weapon_attrs_schema_static = {
 "meta": {
  "name": "all_equips → schema 6109 原始属性关系",
  "category": "三、战力类 / （一）武器",
  "source_server": "体验服 Documents BA8A239A 快照",
  "package_sha": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
  "generated": "2026-09-04",
  "evidence": "structure",
  "notes": "每项是当前同包 all_equips 的原始 row key 到 attrs 对象的关系，保留 attrs 绝对 offset 与 schema6109 的第 23/35 字段原值。schema 字符串标签为 hurt/power；此处不把它们扩展为业务公式、数值比较、装备归属或显示名称。名称回填（2026-09-04）：name 槽=无标点短文本的 154 行直读为名（name-slot）；name 槽=长描述且首句点名的 15 行经人工清单提取（desc-first-map：生产台/AWP狙击步枪/UZI冲锋枪/光盾无人机/蝶影双枪/雷明顿霰弹枪/KSG霰弹枪/G3式自动步枪/仿生菌焰喷火器，及极速之神/奶龙/红色气球）；其余 27 行 name 槽为诗句/路径/限用句或非点名描述，保持匿名占位（name_raw 原样可见）；all_equips 的 row_key/id 不与 common_item item_id 做跨表同号回填。",
  "provenance": {
   "audit_status": "passed",
   "source_locks": [
    {
     "source_id": "all-equips-attrs",
     "sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "role": "primary",
     "bytes": 0,
     "mtime_ns": 0
    }
   ],
   "contract_version": 3,
   "dual_source": {
    "mode": "dual-version-dual-server",
    "primary_source_id": "documents-py314-current",
    "comparison_source_id": "lifeafter-classic-current",
    "primary_server_branch": "简单生存服（体验服）",
    "comparison_server_branch": "经典服",
    "coverage": "source-scope-complement; item fields remain single-source",
    "cross_source_policy": "no-cross-source-field-join",
    "calibration_ref": "data/external_refs/dual_source_calibration.json"
   },
   "standardization_status": "v2-structure-upgraded",
   "contract": "frozen-audited-artifact",
   "source_scope": {
    "cross_source_policy": "no-cross-source-field-join",
    "integer_join_policy": "no-equal-integer-join",
    "runtime_final_policy": "unknown-unless-runtime-proven"
   }
  },
  "state_summary": {
   "static config": 196
  }
 },
 "items": [
  {
   "id": "10001",
   "row_key": 10001,
   "attrs_offset": 191384,
   "name": "未回填（all_equips key=10001）",
   "name_raw": "animator/helicopter/aircraft_linglong.xml",
   "name_evidence": "unresolved",
   "type_hint": "飞行器（路径名行，非武器）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 58,
   "schema6109_field35_power": 1.3,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10001,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10001,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10002",
   "row_key": 10002,
   "attrs_offset": 190993,
   "name": "生产台",
   "name_raw": "PVE中使用的生产台,可以制作各种子弹和通用药品。",
   "name_evidence": "desc-first-map",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 55,
   "schema6109_field35_power": 1.1,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10002,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10002,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10005",
   "row_key": 10005,
   "attrs_offset": 668929,
   "name": "夏尔魅影",
   "name_raw": "夏尔魅影",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 68,
   "schema6109_field35_power": 1.4,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10005,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10005,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10026",
   "row_key": 10026,
   "attrs_offset": 213705,
   "name": "未回填（all_equips key=10026）",
   "name_raw": "animator/helicopter/aircraft_new.xml",
   "name_evidence": "unresolved",
   "type_hint": "飞行器（路径名行，非武器）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 35,
   "schema6109_field35_power": 0.9,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10026,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10026,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10027",
   "row_key": 10027,
   "attrs_offset": 682950,
   "name": "未回填（all_equips key=10027）",
   "name_raw": "流云缱绻舒卷，见证着与你的承诺。粉色的花朵甘作永不枯萎的书页，为你记录下热烈又深情的故事。",
   "name_evidence": "unresolved",
   "type_hint": "时装/挂件/载具外观（诗体 desc 行）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 47,
   "schema6109_field35_power": 1.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10027,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10027,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10029",
   "row_key": 10029,
   "attrs_offset": 326905,
   "name": "UMP9雨战先锋",
   "name_raw": "UMP9雨战先锋",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 45,
   "schema6109_field35_power": 1.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10029,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10029,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10030",
   "row_key": 10030,
   "attrs_offset": 685236,
   "name": "95式突击步枪",
   "name_raw": "95式突击步枪",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 49,
   "schema6109_field35_power": 1.1,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10030,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10030,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10031",
   "row_key": 10031,
   "attrs_offset": 435331,
   "name": "MP5冲锋枪",
   "name_raw": "MP5冲锋枪",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 70,
   "schema6109_field35_power": 1.4,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10031,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10031,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10052",
   "row_key": 10052,
   "attrs_offset": 399366,
   "name": "A2榴弹突击枪",
   "name_raw": "A2榴弹突击枪",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 40,
   "schema6109_field35_power": 1.3,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10052,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10052,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10058",
   "row_key": 10058,
   "attrs_offset": 246325,
   "name": "残破的狙击枪",
   "name_raw": "残破的狙击枪",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 9,
   "schema6109_field35_power": 3.8,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10058,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10058,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10059",
   "row_key": 10059,
   "attrs_offset": 246325,
   "name": "未回填（all_equips key=10059）",
   "name_raw": "该火把只能在暮雪孤峰使用",
   "name_evidence": "unresolved",
   "type_hint": "限用/补给句行",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 9,
   "schema6109_field35_power": 3.8,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10059,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10059,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10062",
   "row_key": 10062,
   "attrs_offset": 457993,
   "name": "砰砰火箭筒",
   "name_raw": "砰砰火箭筒",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 76,
   "schema6109_field35_power": 1.4,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10062,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10062,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10063",
   "row_key": 10063,
   "attrs_offset": 414808,
   "name": "AWP狙击步枪",
   "name_raw": "AWP狙击步枪，远距离、高精度瞄准，一枪制敌#r#r生产于20世纪80年代，服役于各大战争，被认为是最经典的狙击枪。由于远距离狙击不适用于应对如潮的感染者，因此未被普及使用。#r#r随着“新时代”营地间的冲突逐渐升级，超远距离的准确射击再次成为影响战局的关键因素，AWP也因此被大量制造和使用。",
   "name_evidence": "desc-first-map",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 78,
   "schema6109_field35_power": 1.46,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10063,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10063,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10072",
   "row_key": 10072,
   "attrs_offset": 376240,
   "name": "AN94雨战版",
   "name_raw": "AN94雨战版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 95,
   "schema6109_field35_power": 1.55,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10072,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10072,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10076",
   "row_key": 10076,
   "attrs_offset": 368724,
   "name": "G36C雪地版",
   "name_raw": "G36C雪地版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 92,
   "schema6109_field35_power": 1.4,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10076,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10076,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10077",
   "row_key": 10077,
   "attrs_offset": 189407,
   "name": "电能榴弹炮雨战版",
   "name_raw": "电能榴弹炮雨战版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 103,
   "schema6109_field35_power": 1.55,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10077,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10077,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10079",
   "row_key": 10079,
   "attrs_offset": 191384,
   "name": "未回填（all_equips key=10079）",
   "name_raw": "当钢铁开始共鸣，沉默的心跳也有了回声。#r挂在身上有神奇的效果。",
   "name_evidence": "unresolved",
   "type_hint": "时装/挂件/载具外观（诗体 desc 行）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 58,
   "schema6109_field35_power": 1.3,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10079,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10079,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10080",
   "row_key": 10080,
   "attrs_offset": 191384,
   "name": "彩虹T",
   "name_raw": "彩虹T",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 58,
   "schema6109_field35_power": 1.3,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10080,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10080,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10084",
   "row_key": 10084,
   "attrs_offset": 355466,
   "name": "红耳",
   "name_raw": "红耳",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 107,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10084,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10084,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10088",
   "row_key": 10088,
   "attrs_offset": 183369,
   "name": "未回填（all_equips key=10088）",
   "name_raw": "雾气氤氲的石板路上，铃音清脆，玫瑰蔓延盛开，彷佛永不凋败一般。",
   "name_evidence": "unresolved",
   "type_hint": "时装/挂件/载具外观（诗体 desc 行）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 30,
   "schema6109_field35_power": 0.8,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10088,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10088,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10090",
   "row_key": 10090,
   "attrs_offset": 348087,
   "name": "FAMAS雪地版",
   "name_raw": "FAMAS雪地版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 122,
   "schema6109_field35_power": 1.85,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10090,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10090,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10097",
   "row_key": 10097,
   "attrs_offset": 463393,
   "name": "轻型枪口",
   "name_raw": "轻型枪口",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 133,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10097,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10097,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10125",
   "row_key": 10125,
   "attrs_offset": 367064,
   "name": "M24狙击α版",
   "name_raw": "M24狙击α版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 80,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10125,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10125,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10129",
   "row_key": 10129,
   "attrs_offset": 355466,
   "name": "红色气球",
   "name_raw": "红色气球",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 107,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10129,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10129,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10134",
   "row_key": 10134,
   "attrs_offset": 463393,
   "name": "迎春萌虎",
   "name_raw": "迎春萌虎",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 133,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10134,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10134,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10137",
   "row_key": 10137,
   "attrs_offset": 215007,
   "name": "EM-1电磁雨战版",
   "name_raw": "EM-1电磁雨战版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 69,
   "schema6109_field35_power": 1.6,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10137,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10137,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10138",
   "row_key": 10138,
   "attrs_offset": 245934,
   "name": "EM-2电磁机枪",
   "name_raw": "EM-2电磁机枪",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 108,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10138,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10138,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10139",
   "row_key": 10139,
   "attrs_offset": 244514,
   "name": "EM-3电磁机枪",
   "name_raw": "EM-3电磁机枪",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 134,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10139,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10139,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10140",
   "row_key": 10140,
   "attrs_offset": 188583,
   "name": "EM-4电磁典藏版",
   "name_raw": "EM-4电磁典藏版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 147,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10140,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10140,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10145",
   "row_key": 10145,
   "attrs_offset": 187047,
   "name": "蒙尘的步枪",
   "name_raw": "蒙尘的步枪",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 172,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10145,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10145,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10200",
   "row_key": 10200,
   "attrs_offset": 191384,
   "name": "AN94典藏版",
   "name_raw": "AN94典藏版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 58,
   "schema6109_field35_power": 1.3,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10200,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10200,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10201",
   "row_key": 10201,
   "attrs_offset": 191384,
   "name": "AN94突榴α版",
   "name_raw": "AN94突榴α版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 58,
   "schema6109_field35_power": 1.3,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10201,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10201,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10202",
   "row_key": 10202,
   "attrs_offset": 191384,
   "name": "AK47突击体验版",
   "name_raw": "AK47突击体验版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 58,
   "schema6109_field35_power": 1.3,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10202,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10202,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10210",
   "row_key": 10210,
   "attrs_offset": 190993,
   "name": "Mark.06",
   "name_raw": "Mark.06",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 55,
   "schema6109_field35_power": 1.1,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10210,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10210,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10211",
   "row_key": 10211,
   "attrs_offset": 190993,
   "name": "生产台",
   "name_raw": "PVE中使用的生产台。",
   "name_evidence": "desc-first-map",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 55,
   "schema6109_field35_power": 1.1,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10211,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10211,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10212",
   "row_key": 10212,
   "attrs_offset": 190993,
   "name": "MP5冲锋枪体验版",
   "name_raw": "MP5冲锋枪体验版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 55,
   "schema6109_field35_power": 1.1,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10212,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10212,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10220",
   "row_key": 10220,
   "attrs_offset": 668929,
   "name": "墨绿逃生包",
   "name_raw": "墨绿逃生包",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 68,
   "schema6109_field35_power": 1.4,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10220,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10220,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10221",
   "row_key": 10221,
   "attrs_offset": 668929,
   "name": "未回填（all_equips key=10221）",
   "name_raw": "处于信号区中，信标会持续上传。上传期间会持续增加阵营积分，信号上传完成后会一次性增加大量阵营积分",
   "name_evidence": "unresolved",
   "type_hint": "营地工具/杂物行",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 68,
   "schema6109_field35_power": 1.4,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10221,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10221,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10222",
   "row_key": 10222,
   "attrs_offset": 668929,
   "name": "增强型弓弦",
   "name_raw": "增强型弓弦",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 68,
   "schema6109_field35_power": 1.4,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10222,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10222,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10270",
   "row_key": 10270,
   "attrs_offset": 213705,
   "name": "X10A型扩散器",
   "name_raw": "X10A型扩散器",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 35,
   "schema6109_field35_power": 0.9,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10270,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10270,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10271",
   "row_key": 10271,
   "attrs_offset": 213705,
   "name": "XM25榴弹α版",
   "name_raw": "XM25榴弹α版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 35,
   "schema6109_field35_power": 0.9,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10271,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10271,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10272",
   "row_key": 10272,
   "attrs_offset": 213705,
   "name": "UZI冲锋枪幸存者版",
   "name_raw": "UZI冲锋枪幸存者版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 35,
   "schema6109_field35_power": 0.9,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10272,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10272,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10280",
   "row_key": 10280,
   "attrs_offset": 682950,
   "name": "汽油桶",
   "name_raw": "汽油桶",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 47,
   "schema6109_field35_power": 1.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10280,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10280,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10281",
   "row_key": 10281,
   "attrs_offset": 682950,
   "name": "沙漠武装",
   "name_raw": "沙漠武装",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 47,
   "schema6109_field35_power": 1.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10281,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10281,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10282",
   "row_key": 10282,
   "attrs_offset": 682950,
   "name": "未回填（all_equips key=10282）",
   "name_raw": "汪汪抬来的端午弹药箱，外头还挂着几个粽子。",
   "name_evidence": "unresolved",
   "type_hint": "营地工具/杂物行",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 47,
   "schema6109_field35_power": 1.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10282,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10282,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10300",
   "row_key": 10300,
   "attrs_offset": 326905,
   "name": "UZI典藏版",
   "name_raw": "UZI典藏版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 45,
   "schema6109_field35_power": 1.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10300,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10300,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10301",
   "row_key": 10301,
   "attrs_offset": 326905,
   "name": "UZI冲锋枪",
   "name_raw": "UZI冲锋枪专为雨天作战推出的试验版本，拥有比原型版本更高的耐久度，但由于是试验品，所以无法在维修台维修，也无法进行拆解。",
   "name_evidence": "desc-first-map",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 45,
   "schema6109_field35_power": 1.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10301,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10301,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10302",
   "row_key": 10302,
   "attrs_offset": 326905,
   "name": "UMP9冲锋枪新手体验版",
   "name_raw": "UMP9冲锋枪新手体验版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 45,
   "schema6109_field35_power": 1.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10302,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10302,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10310",
   "row_key": 10310,
   "attrs_offset": 685236,
   "name": "590M霰弹α版",
   "name_raw": "590M霰弹α版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 49,
   "schema6109_field35_power": 1.1,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10310,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10310,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10311",
   "row_key": 10311,
   "attrs_offset": 685236,
   "name": "5级冲击手雷",
   "name_raw": "5级冲击手雷",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 49,
   "schema6109_field35_power": 1.1,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10311,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10311,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10312",
   "row_key": 10312,
   "attrs_offset": 685236,
   "name": "590M雪地精英",
   "name_raw": "590M雪地精英",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 49,
   "schema6109_field35_power": 1.1,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10312,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10312,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10320",
   "row_key": 10320,
   "attrs_offset": 435331,
   "name": "MP5典藏版",
   "name_raw": "MP5典藏版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 70,
   "schema6109_field35_power": 1.4,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10320,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10320,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10321",
   "row_key": 10321,
   "attrs_offset": 435331,
   "name": "MP5冲锋枪α版",
   "name_raw": "MP5冲锋枪α版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 70,
   "schema6109_field35_power": 1.4,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10321,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10321,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10322",
   "row_key": 10322,
   "attrs_offset": 435331,
   "name": "M416步枪α版",
   "name_raw": "M416步枪α版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 70,
   "schema6109_field35_power": 1.4,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10322,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10322,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10350",
   "row_key": 10350,
   "attrs_offset": 399366,
   "name": "9级基础护盾",
   "name_raw": "9级基础护盾",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 40,
   "schema6109_field35_power": 1.3,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10350,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10350,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10351",
   "row_key": 10351,
   "attrs_offset": 399366,
   "name": "9级磺骨护盾",
   "name_raw": "9级磺骨护盾",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 40,
   "schema6109_field35_power": 1.3,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10351,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10351,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10352",
   "row_key": 10352,
   "attrs_offset": 399366,
   "name": "95式远星版",
   "name_raw": "95式远星版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 40,
   "schema6109_field35_power": 1.3,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10352,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10352,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10380",
   "row_key": 10380,
   "attrs_offset": 457993,
   "name": "石镐-武器皮肤",
   "name_raw": "石镐-武器皮肤",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 76,
   "schema6109_field35_power": 1.4,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10380,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10380,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10381",
   "row_key": 10381,
   "attrs_offset": 457993,
   "name": "矿物采集器",
   "name_raw": "矿物采集器",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 76,
   "schema6109_field35_power": 1.4,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10381,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10381,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10382",
   "row_key": 10382,
   "attrs_offset": 457993,
   "name": "石斧-武器皮肤",
   "name_raw": "石斧-武器皮肤",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 76,
   "schema6109_field35_power": 1.4,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10382,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10382,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10390",
   "row_key": 10390,
   "attrs_offset": 414808,
   "name": "AK47典藏版",
   "name_raw": "AK47典藏版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 78,
   "schema6109_field35_power": 1.46,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10390,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10390,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10391",
   "row_key": 10391,
   "attrs_offset": 414808,
   "name": "AK47步枪α版",
   "name_raw": "AK47步枪α版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 78,
   "schema6109_field35_power": 1.46,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10391,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10391,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10392",
   "row_key": 10392,
   "attrs_offset": 414808,
   "name": "A2突击雨战版",
   "name_raw": "A2突击雨战版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 78,
   "schema6109_field35_power": 1.46,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10392,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10392,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10400",
   "row_key": 10400,
   "attrs_offset": 376240,
   "name": "AS50典藏版",
   "name_raw": "AS50典藏版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 95,
   "schema6109_field35_power": 1.55,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10400,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10400,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10401",
   "row_key": 10401,
   "attrs_offset": 376240,
   "name": "AS50狙击α版",
   "name_raw": "AS50狙击α版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 95,
   "schema6109_field35_power": 1.55,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10401,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10401,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10402",
   "row_key": 10402,
   "attrs_offset": 376240,
   "name": "AN94突榴枪",
   "name_raw": "AN94突榴枪",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 95,
   "schema6109_field35_power": 1.55,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10402,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10402,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10409",
   "row_key": 10409,
   "attrs_offset": 368724,
   "name": "G3式步枪体验版",
   "name_raw": "G3式步枪体验版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 92,
   "schema6109_field35_power": 1.4,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10409,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10409,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10410",
   "row_key": 10410,
   "attrs_offset": 368724,
   "name": "G3式自动步枪典藏版",
   "name_raw": "G3式自动步枪典藏版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 92,
   "schema6109_field35_power": 1.4,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10410,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10410,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10411",
   "row_key": 10411,
   "attrs_offset": 368724,
   "name": "G36C突击体验版",
   "name_raw": "G36C突击体验版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 92,
   "schema6109_field35_power": 1.4,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10411,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10411,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10412",
   "row_key": 10412,
   "attrs_offset": 367064,
   "name": "KSG霰弹α版",
   "name_raw": "KSG霰弹α版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 80,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10412,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10412,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10413",
   "row_key": 10413,
   "attrs_offset": 367064,
   "name": "M24典藏版",
   "name_raw": "M24典藏版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 80,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10413,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10413,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10414",
   "row_key": 10414,
   "attrs_offset": 367064,
   "name": "KSG雪地版",
   "name_raw": "KSG雪地版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 80,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10414,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10414,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10415",
   "row_key": 10415,
   "attrs_offset": 189407,
   "name": "电能榴弹炮雪地版",
   "name_raw": "电能榴弹炮雪地版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 103,
   "schema6109_field35_power": 1.55,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10415,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10415,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10416",
   "row_key": 10416,
   "attrs_offset": 189407,
   "name": "电锯",
   "name_raw": "电锯",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 103,
   "schema6109_field35_power": 1.55,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10416,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10416,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10417",
   "row_key": 10417,
   "attrs_offset": 189407,
   "name": "电能榴弹炮典藏版",
   "name_raw": "电能榴弹炮典藏版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 103,
   "schema6109_field35_power": 1.55,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10417,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10417,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10422",
   "row_key": 10422,
   "attrs_offset": 361693,
   "name": "巨蛇霰弹雨战版",
   "name_raw": "巨蛇霰弹雨战版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 40,
   "schema6109_field35_power": 2.8,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10422,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10422,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10423",
   "row_key": 10423,
   "attrs_offset": 361693,
   "name": "巨蛇霰弹雪地版",
   "name_raw": "巨蛇霰弹雪地版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 40,
   "schema6109_field35_power": 2.8,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10423,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10423,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10424",
   "row_key": 10424,
   "attrs_offset": 361693,
   "name": "左轮手枪雨战版",
   "name_raw": "左轮手枪雨战版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 40,
   "schema6109_field35_power": 2.8,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10424,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10424,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10432",
   "row_key": 10432,
   "attrs_offset": 355466,
   "name": "红色电塔",
   "name_raw": "红色电塔",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 107,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10432,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10432,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10433",
   "row_key": 10433,
   "attrs_offset": 355466,
   "name": "红色气球",
   "name_raw": "红色的气球。当你放手后，它会飞向天空。#r[玩具]通过限时活动获得。",
   "name_evidence": "desc-first-map",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 107,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10433,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10433,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10434",
   "row_key": 10434,
   "attrs_offset": 355466,
   "name": "未回填（all_equips key=10434）",
   "name_raw": "结霜的鹿角化为冬日最尖锐的利刃，樱色的花瓣染上身经百战的车体，无论赛道还是战场，它以最可爱的姿态载你凯旋而归。",
   "name_evidence": "unresolved",
   "type_hint": "时装/挂件/载具外观（诗体 desc 行）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 107,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10434,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10434,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10435",
   "row_key": 10435,
   "attrs_offset": 353862,
   "name": "未回填（all_equips key=10435）",
   "name_raw": "[明日之后×小王子]联动限定物品。#r不管在哪个星球，人都不会拥有至高无上的权力。#r[玩具]通过限时活动获得。",
   "name_evidence": "unresolved",
   "type_hint": "时装/挂件/载具外观（诗体 desc 行）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 110,
   "schema6109_field35_power": 6.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10435,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10435,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10436",
   "row_key": 10436,
   "attrs_offset": 353862,
   "name": "未回填（all_equips key=10436）",
   "name_raw": "[明日之后×小王子]联动限定物品。#r尽管世界上有无数朵玫瑰花，但他星球上那朵，仍然是独一无二的。",
   "name_evidence": "unresolved",
   "type_hint": "时装/挂件/载具外观（诗体 desc 行）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 110,
   "schema6109_field35_power": 6.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10436,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10436,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10437",
   "row_key": 10437,
   "attrs_offset": 353862,
   "name": "Z5左轮雪地版",
   "name_raw": "Z5左轮雪地版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 110,
   "schema6109_field35_power": 6.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10437,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10437,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10440",
   "row_key": 10440,
   "attrs_offset": 183369,
   "name": "未回填（all_equips key=10440）",
   "name_raw": "需要战斗熟练度等级100才能使用#r具有独特的转轮结构的霰弹枪，高伤害近距离武器。相比于其他版本，具有更强大的威力。",
   "name_evidence": "unresolved",
   "type_hint": "武器本体（desc 未点名短名）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 30,
   "schema6109_field35_power": 0.8,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10440,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10440,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10441",
   "row_key": 10441,
   "attrs_offset": 183369,
   "name": "未回填（all_equips key=10441）",
   "name_raw": "需要战斗熟练度等级100才能使用#r具有独特的转轮结构的霰弹枪，高伤害近距离武器。相比于普通版本，攻击力更高，且在大雪天气下能够更好的发挥实力。",
   "name_evidence": "unresolved",
   "type_hint": "武器本体（desc 未点名短名）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 30,
   "schema6109_field35_power": 0.8,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10441,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10441,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10442",
   "row_key": 10442,
   "attrs_offset": 183369,
   "name": "雷魂怒钧",
   "name_raw": "雷魂怒钧",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 30,
   "schema6109_field35_power": 0.8,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10442,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10442,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10446",
   "row_key": 10446,
   "attrs_offset": 348087,
   "name": "Foodpanda",
   "name_raw": "Foodpanda",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 122,
   "schema6109_field35_power": 1.85,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10446,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10446,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10447",
   "row_key": 10447,
   "attrs_offset": 348087,
   "name": "G36C典藏版",
   "name_raw": "G36C典藏版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 122,
   "schema6109_field35_power": 1.85,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10447,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10447,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10448",
   "row_key": 10448,
   "attrs_offset": 348087,
   "name": "FAMAS雨战版",
   "name_raw": "FAMAS雨战版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 122,
   "schema6109_field35_power": 1.85,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10448,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10448,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10453",
   "row_key": 10453,
   "attrs_offset": 463393,
   "name": "运兵车",
   "name_raw": "运兵车",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 133,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10453,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10453,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10454",
   "row_key": 10454,
   "attrs_offset": 463393,
   "name": "运输箱",
   "name_raw": "运输箱",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 133,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10454,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10454,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10455",
   "row_key": 10455,
   "attrs_offset": 463393,
   "name": "迎春福至兔子灯",
   "name_raw": "迎春福至兔子灯",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 133,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10455,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10455,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10463",
   "row_key": 10463,
   "attrs_offset": 223321,
   "name": "巴克的撕裂电锯",
   "name_raw": "巴克的撕裂电锯",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 76,
   "schema6109_field35_power": 1.7,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10463,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10463,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10464",
   "row_key": 10464,
   "attrs_offset": 223321,
   "name": "巴雷特典藏版",
   "name_raw": "巴雷特典藏版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 76,
   "schema6109_field35_power": 1.7,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10464,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10464,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10465",
   "row_key": 10465,
   "attrs_offset": 223321,
   "name": "未回填（all_equips key=10465）",
   "name_raw": "帝国军营战役专用补给。在暴风雪天气下战斗时，多一处篝火应能让你的境况好上一些。#r退出战役场景时会被回收。#r#r“新时代”的人们为了搜集资源，不得不面对陌生的大自然。利用自然与自然对抗，成了脱离现代文明的人们在“新时代”需要学习的第一课。#r#r“将自然放入篝火中，你会得到神的馈赠。将宝剑插入篝火中，你会得到神的庇佑。”——《宗教卷一·第五章·灵魂的黑暗面》",
   "name_evidence": "unresolved",
   "type_hint": "限用/补给句行",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 76,
   "schema6109_field35_power": 1.7,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10465,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10465,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10512",
   "row_key": 10512,
   "attrs_offset": 361693,
   "name": "左轮手枪雪地版",
   "name_raw": "左轮手枪雪地版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 40,
   "schema6109_field35_power": 2.8,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10512,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10512,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10513",
   "row_key": 10513,
   "attrs_offset": 361693,
   "name": "巨蛇霰弹樱花版",
   "name_raw": "巨蛇霰弹樱花版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 40,
   "schema6109_field35_power": 2.8,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10513,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10513,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10521",
   "row_key": 10521,
   "attrs_offset": 215007,
   "name": "EM-2电磁α版",
   "name_raw": "EM-2电磁α版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 69,
   "schema6109_field35_power": 1.6,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10521,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10521,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10522",
   "row_key": 10522,
   "attrs_offset": 215007,
   "name": "EM-2电磁典藏版",
   "name_raw": "EM-2电磁典藏版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 69,
   "schema6109_field35_power": 1.6,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10522,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10522,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10523",
   "row_key": 10523,
   "attrs_offset": 215007,
   "name": "EM-1电磁雪地版",
   "name_raw": "EM-1电磁雪地版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 69,
   "schema6109_field35_power": 1.6,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10523,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10523,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10524",
   "row_key": 10524,
   "attrs_offset": 245934,
   "name": "EM-3电磁α版",
   "name_raw": "EM-3电磁α版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 108,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10524,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10524,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10525",
   "row_key": 10525,
   "attrs_offset": 245934,
   "name": "EM-3电磁典藏版",
   "name_raw": "EM-3电磁典藏版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 108,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10525,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10525,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10526",
   "row_key": 10526,
   "attrs_offset": 245934,
   "name": "EM-2电磁雨战版",
   "name_raw": "EM-2电磁雨战版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 108,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10526,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10526,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10527",
   "row_key": 10527,
   "attrs_offset": 244514,
   "name": "EM-4电磁α版",
   "name_raw": "EM-4电磁α版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 134,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10527,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10527,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10528",
   "row_key": 10528,
   "attrs_offset": 244514,
   "name": "EM-4电磁体验版",
   "name_raw": "EM-4电磁体验版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 134,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10528,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10528,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10529",
   "row_key": 10529,
   "attrs_offset": 244514,
   "name": "EM-3电磁雨战版",
   "name_raw": "EM-3电磁雨战版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 134,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10529,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10529,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10530",
   "row_key": 10530,
   "attrs_offset": 188583,
   "name": "EMP干扰弹",
   "name_raw": "EMP干扰弹",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 147,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10530,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10530,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10531",
   "row_key": 10531,
   "attrs_offset": 188583,
   "name": "光盾无人机",
   "name_raw": "EVANGELION联动典藏涂装版光盾无人机，可以在主人当前位置生成一个光盾屏障，光盾护住主人，为主人抵挡外部伤害。#r「明日之后×EVANGELION」联动限定物品。",
   "name_evidence": "desc-first-map",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 147,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10531,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10531,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10532",
   "row_key": 10532,
   "attrs_offset": 188583,
   "name": "EM-4电磁雨战版",
   "name_raw": "EM-4电磁雨战版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 147,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10532,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10532,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10545",
   "row_key": 10545,
   "attrs_offset": 401601,
   "name": "擎天巨兽-攻壳机动队",
   "name_raw": "擎天巨兽-攻壳机动队",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 10,
   "schema6109_field35_power": 0.585,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10545,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10545,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10546",
   "row_key": 10546,
   "attrs_offset": 420013,
   "name": "未回填（all_equips key=10546）",
   "name_raw": "收集营地各种税收的机器。#r1.市民在营地内外的行为，将会为营地带来一定税收，并储存在此；#r2.每天晚上，营地需要自动上缴一定数量的税收，作为明天营地的运作开支；#r3.连续成功缴纳一定天数，营地的生产效率提升；#r4.税款只有市长有权取出另作他用。",
   "name_evidence": "unresolved",
   "type_hint": "营地工具/杂物行",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 1000,
   "schema6109_field35_power": 0.585,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10546,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10546,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10547",
   "row_key": 10547,
   "attrs_offset": 188212,
   "name": "AWM典藏版",
   "name_raw": "AWM典藏版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 148,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10547,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10547,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10548",
   "row_key": 10548,
   "attrs_offset": 188212,
   "name": "AWM狙击α版",
   "name_raw": "AWM狙击α版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 148,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10548,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10548,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10549",
   "row_key": 10549,
   "attrs_offset": 188212,
   "name": "AUG突击雨战版",
   "name_raw": "AUG突击雨战版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 148,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10549,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10549,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10572",
   "row_key": 10572,
   "attrs_offset": 183369,
   "name": "雷明顿α版",
   "name_raw": "雷明顿α版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 30,
   "schema6109_field35_power": 0.8,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10572,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10572,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10573",
   "row_key": 10573,
   "attrs_offset": 187449,
   "name": "斯泰尔狙击枪雪地版",
   "name_raw": "斯泰尔狙击枪雪地版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 161,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10573,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10573,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10574",
   "row_key": 10574,
   "attrs_offset": 187449,
   "name": "斯通纳狙击体验版",
   "name_raw": "斯通纳狙击体验版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 161,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10574,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10574,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10575",
   "row_key": 10575,
   "attrs_offset": 187449,
   "name": "斯泰尔狙击枪典藏版",
   "name_raw": "斯泰尔狙击枪典藏版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 161,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10575,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10575,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10579",
   "row_key": 10579,
   "attrs_offset": 231235,
   "name": "未回填（all_equips key=10579）",
   "name_raw": "它像一位在月夜中翩翩起舞的舞者，优雅而动人，时刻展示出它无与伦比的风采。当它穿梭在山林中，月光铺洒在银白色的车身上熠熠生辉，只有在这一刻，它才真正展现出自己的魅力，舞动着它的身姿，带领你跳跃在星河汇聚而成的舞台上。",
   "name_evidence": "unresolved",
   "type_hint": "时装/挂件/载具外观（诗体 desc 行）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 170,
   "schema6109_field35_power": 6.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10579,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10579,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10580",
   "row_key": 10580,
   "attrs_offset": 231235,
   "name": "未回填（all_equips key=10580）",
   "name_raw": "娱乐模式体验版护盾，可以提供一定的护盾值和35%的突击步枪伤害减免。当护盾被击破后，特定武器伤害减免将同时失效。",
   "name_evidence": "unresolved",
   "type_hint": "护盾道具行",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 170,
   "schema6109_field35_power": 6.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10580,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10580,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10581",
   "row_key": 10581,
   "attrs_offset": 231235,
   "name": "未回填（all_equips key=10581）",
   "name_raw": "娱乐模式体验版护盾，可以提供一定的护盾值和35%的榴弹、狙击伤害减免。当护盾被击破后，特定武器伤害减免将同时失效。",
   "name_evidence": "unresolved",
   "type_hint": "护盾道具行",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 170,
   "schema6109_field35_power": 6.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10581,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10581,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10589",
   "row_key": 10589,
   "attrs_offset": 183369,
   "name": "未回填（all_equips key=10589）",
   "name_raw": "需要战斗熟练度30级才可以使用#r可以提供一定的护盾值。",
   "name_evidence": "unresolved",
   "type_hint": "护盾道具行",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 30,
   "schema6109_field35_power": 0.8,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10589,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10589,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10609",
   "row_key": 10609,
   "attrs_offset": 396875,
   "name": "汤姆逊α版",
   "name_raw": "汤姆逊α版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 25,
   "schema6109_field35_power": 0.8,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10609,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10609,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10611",
   "row_key": 10611,
   "attrs_offset": 395124,
   "name": "未回填（all_equips key=10611）",
   "name_raw": "制作各种夹层。#r夹层可以被使用在部分装备上。",
   "name_evidence": "unresolved",
   "type_hint": "营地工具/杂物行",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 22,
   "schema6109_field35_power": 0.8,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10611,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10611,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10614",
   "row_key": 10614,
   "attrs_offset": 183369,
   "name": "雷托霰弹福兔版",
   "name_raw": "雷托霰弹福兔版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 30,
   "schema6109_field35_power": 0.8,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10614,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10614,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10621",
   "row_key": 10621,
   "attrs_offset": 183369,
   "name": "雷托霰弹雪地版",
   "name_raw": "雷托霰弹雪地版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 30,
   "schema6109_field35_power": 0.8,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10621,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10621,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10627",
   "row_key": 10627,
   "attrs_offset": 159383,
   "name": "蝶影双枪",
   "name_raw": "蝶影双枪，诞生于方舟市，方舟骑士们用它成功守护了自己的城市。",
   "name_evidence": "desc-first-map",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 42,
   "schema6109_field35_power": 2.8,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10627,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10627,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10628",
   "row_key": 10628,
   "attrs_offset": 159383,
   "name": "蝶影左轮雨战版",
   "name_raw": "蝶影左轮雨战版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 42,
   "schema6109_field35_power": 2.8,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10628,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10628,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10629",
   "row_key": 10629,
   "attrs_offset": 159383,
   "name": "蝶影左轮雪地版",
   "name_raw": "蝶影左轮雪地版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 42,
   "schema6109_field35_power": 2.8,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10629,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10629,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10631",
   "row_key": 10631,
   "attrs_offset": 159383,
   "name": "警用卫衣",
   "name_raw": "警用卫衣",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 42,
   "schema6109_field35_power": 2.8,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10631,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10631,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10635",
   "row_key": 10635,
   "attrs_offset": 187047,
   "name": "蓝晶木斧",
   "name_raw": "蓝晶木斧",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 172,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10635,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10635,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10636",
   "row_key": 10636,
   "attrs_offset": 187047,
   "name": "蓝珀战甲",
   "name_raw": "蓝珀战甲",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 172,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10636,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10636,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10637",
   "row_key": 10637,
   "attrs_offset": 187047,
   "name": "蓝晶战甲",
   "name_raw": "蓝晶战甲",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 172,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10637,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10637,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10638",
   "row_key": 10638,
   "attrs_offset": 186640,
   "name": "大型野兽特制地雷",
   "name_raw": "大型野兽特制地雷",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 174,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10638,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10638,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10639",
   "row_key": 10639,
   "attrs_offset": 186640,
   "name": "未回填（all_equips key=10639）",
   "name_raw": "大尸潮专用",
   "name_evidence": "unresolved",
   "type_hint": "限用/补给句行",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 174,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10639,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10639,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10640",
   "row_key": 10640,
   "attrs_offset": 186640,
   "name": "夜幕铁甲",
   "name_raw": "夜幕铁甲",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 174,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10640,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10640,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10647",
   "row_key": 10647,
   "attrs_offset": 183369,
   "name": "雷明顿霰弹枪",
   "name_raw": "雷明顿霰弹枪的试验版本，拥有比原型版本更高的耐久度，但由于是试验品，所以无法在维修台维修，也无法进行拆解。",
   "name_evidence": "desc-first-map",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 30,
   "schema6109_field35_power": 0.8,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10647,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10647,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10674",
   "row_key": 10674,
   "attrs_offset": 393862,
   "name": "MP5冲锋枪",
   "name_raw": "MP5冲锋枪",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 37,
   "schema6109_field35_power": 1.1,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10674,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10674,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10675",
   "row_key": 10675,
   "attrs_offset": 393862,
   "name": "A2榴弹突击枪",
   "name_raw": "A2榴弹突击枪",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 37,
   "schema6109_field35_power": 1.1,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10675,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10675,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10677",
   "row_key": 10677,
   "attrs_offset": 413662,
   "name": "未回填（all_equips key=10677）",
   "name_raw": "animator/helicopter/dragon_aircraft.xml",
   "name_evidence": "unresolved",
   "type_hint": "飞行器（路径名行，非武器）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 37,
   "schema6109_field35_power": 1.3,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10677,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10677,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10680",
   "row_key": 10680,
   "attrs_offset": 203186,
   "name": "夜骐",
   "name_raw": "夜骐",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 41,
   "schema6109_field35_power": 1.3,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10680,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10680,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10695",
   "row_key": 10695,
   "attrs_offset": 383007,
   "name": "KSG霰弹枪",
   "name_raw": "KSG霰弹枪，无托结构的双管弹仓泵动霰弹枪，高伤害近距离武器。",
   "name_evidence": "desc-first-map",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 37,
   "schema6109_field35_power": 1.4,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10695,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10695,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10696",
   "row_key": 10696,
   "attrs_offset": 383007,
   "name": "红耳",
   "name_raw": "红耳",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 37,
   "schema6109_field35_power": 1.4,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10696,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10696,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10701",
   "row_key": 10701,
   "attrs_offset": 202784,
   "name": "极速之神",
   "name_raw": "蓝色的极速之神，劈开巨浪，带你一往无前。",
   "name_evidence": "desc-first-map",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 41,
   "schema6109_field35_power": 1.4,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10701,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10701,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10729",
   "row_key": 10729,
   "attrs_offset": 186215,
   "name": "M24狙击步枪",
   "name_raw": "M24狙击步枪",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 187,
   "schema6109_field35_power": 2.16,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10729,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10729,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10730",
   "row_key": 10730,
   "attrs_offset": 186215,
   "name": "G3式自动步枪",
   "name_raw": "G3式自动步枪，采用半自由枪机式工作原理，并且配备了光学瞄准镜，保证了在各种距离的作战中优秀的稳定性和安全性。",
   "name_evidence": "desc-first-map",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 187,
   "schema6109_field35_power": 2.16,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10730,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10730,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10731",
   "row_key": 10731,
   "attrs_offset": 186215,
   "name": "KFC全家桶联动弹药箱",
   "name_raw": "KFC全家桶联动弹药箱",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 187,
   "schema6109_field35_power": 2.16,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10731,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10731,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10732",
   "row_key": 10732,
   "attrs_offset": 186215,
   "name": "G3式自动步枪雪地版",
   "name_raw": "G3式自动步枪雪地版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 187,
   "schema6109_field35_power": 2.16,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10732,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10732,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10743",
   "row_key": 10743,
   "attrs_offset": 185402,
   "name": "未回填（all_equips key=10743）",
   "name_raw": "泵动式霰弹枪，高性能的近距离武器，此款是市民防卫用的粗制简易版。因为直升机坠机破损，已几乎要坏掉。",
   "name_evidence": "unresolved",
   "type_hint": "武器本体（desc 未点名短名）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 190,
   "schema6109_field35_power": 6.2,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10743,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10743,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10745",
   "row_key": 10745,
   "attrs_offset": 185402,
   "name": "治疗扩散器",
   "name_raw": "治疗扩散器",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 190,
   "schema6109_field35_power": 6.2,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10745,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10745,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10746",
   "row_key": 10746,
   "attrs_offset": 185402,
   "name": "泡泡彩带枪",
   "name_raw": "泡泡彩带枪",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 190,
   "schema6109_field35_power": 6.2,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10746,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10746,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10747",
   "row_key": 10747,
   "attrs_offset": 185402,
   "name": "治疗减伤",
   "name_raw": "治疗减伤",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 190,
   "schema6109_field35_power": 6.2,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10747,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10747,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10759",
   "row_key": 10759,
   "attrs_offset": 188583,
   "name": "EM-4电磁机枪",
   "name_raw": "EM-4电磁机枪",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 147,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10759,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10759,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10760",
   "row_key": 10760,
   "attrs_offset": 188212,
   "name": "AUG突击步枪",
   "name_raw": "AUG突击步枪",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 148,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10760,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10760,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10762",
   "row_key": 10762,
   "attrs_offset": 187449,
   "name": "斯泰尔狙击枪α版",
   "name_raw": "斯泰尔狙击枪α版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 161,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10762,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10762,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10767",
   "row_key": 10767,
   "attrs_offset": 186640,
   "name": "多纳尔电磁雪地版",
   "name_raw": "多纳尔电磁雪地版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 174,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10767,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10767,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10768",
   "row_key": 10768,
   "attrs_offset": 186215,
   "name": "G3式自动步枪雨战版",
   "name_raw": "G3式自动步枪雨战版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 187,
   "schema6109_field35_power": 2.16,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10768,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10768,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10774",
   "row_key": 10774,
   "attrs_offset": 223321,
   "name": "巨蛇霰弹龙吟版",
   "name_raw": "巨蛇霰弹龙吟版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 76,
   "schema6109_field35_power": 1.7,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10774,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10774,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10781",
   "row_key": 10781,
   "attrs_offset": 183784,
   "name": "MP5冲锋枪",
   "name_raw": "MP5冲锋枪",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 100,
   "schema6109_field35_power": 1.3,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10781,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10781,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10782",
   "row_key": 10782,
   "attrs_offset": 183784,
   "name": "A2榴弹突击枪",
   "name_raw": "A2榴弹突击枪",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 100,
   "schema6109_field35_power": 1.3,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10782,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10782,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10784",
   "row_key": 10784,
   "attrs_offset": 183784,
   "name": "未回填（all_equips key=10784）",
   "name_raw": "animator/helicopter/dragon_aircraft.xml",
   "name_evidence": "unresolved",
   "type_hint": "飞行器（路径名行，非武器）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 100,
   "schema6109_field35_power": 1.3,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10784,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10784,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10787",
   "row_key": 10787,
   "attrs_offset": 339179,
   "name": "夜骐",
   "name_raw": "夜骐",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 100,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10787,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10787,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10800",
   "row_key": 10800,
   "attrs_offset": 183784,
   "name": "95式突击步枪",
   "name_raw": "95式突击步枪",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 100,
   "schema6109_field35_power": 1.3,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10800,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10800,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10803",
   "row_key": 10803,
   "attrs_offset": 339179,
   "name": "红耳",
   "name_raw": "红耳",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 100,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10803,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10803,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10808",
   "row_key": 10808,
   "attrs_offset": 183784,
   "name": "极速之神",
   "name_raw": "蓝色的极速之神，劈开巨浪，带你一往无前。",
   "name_evidence": "desc-first-map",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 100,
   "schema6109_field35_power": 1.3,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10808,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10808,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10836",
   "row_key": 10836,
   "attrs_offset": 223321,
   "name": "未回填（all_equips key=10836）",
   "name_raw": "已损坏，需要维修……",
   "name_evidence": "unresolved",
   "type_hint": "营地工具/杂物行",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 76,
   "schema6109_field35_power": 1.7,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10836,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10836,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10850",
   "row_key": 10850,
   "attrs_offset": 166007,
   "name": "碧海拾花",
   "name_raw": "碧海拾花",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 44,
   "schema6109_field35_power": 5.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10850,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10850,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10855",
   "row_key": 10855,
   "attrs_offset": 166007,
   "name": "碧焰",
   "name_raw": "碧焰",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 44,
   "schema6109_field35_power": 5.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10855,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10855,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10856",
   "row_key": 10856,
   "attrs_offset": 166007,
   "name": "碳素蜘蛛弓",
   "name_raw": "碳素蜘蛛弓",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 44,
   "schema6109_field35_power": 5.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10856,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10856,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10857",
   "row_key": 10857,
   "attrs_offset": 166007,
   "name": "碧影",
   "name_raw": "碧影",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 44,
   "schema6109_field35_power": 5.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10857,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10857,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10869",
   "row_key": 10869,
   "attrs_offset": 210591,
   "name": "仿生蛛酶步枪精校版",
   "name_raw": "仿生蛛酶步枪精校版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 78,
   "schema6109_field35_power": 1.3,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10869,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10869,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10870",
   "row_key": 10870,
   "attrs_offset": 210591,
   "name": "仿生蛛酶玲珑版",
   "name_raw": "仿生蛛酶玲珑版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 78,
   "schema6109_field35_power": 1.3,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10870,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10870,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10871",
   "row_key": 10871,
   "attrs_offset": 210591,
   "name": "仿生蛛酶东京喰种版",
   "name_raw": "仿生蛛酶东京喰种版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 78,
   "schema6109_field35_power": 1.3,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10871,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10871,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10880",
   "row_key": 10880,
   "attrs_offset": 171222,
   "name": "奶龙",
   "name_raw": "哼~谁要做你的最佳拍档！「明日之后×奶龙nailong」联动限定外观。#r挂在身上有神奇的效果。",
   "name_evidence": "desc-first-map",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 194,
   "schema6109_field35_power": 2.12,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10880,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10880,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10881",
   "row_key": 10881,
   "attrs_offset": 171222,
   "name": "商店灭火器",
   "name_raw": "商店灭火器",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 194,
   "schema6109_field35_power": 2.12,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10881,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10881,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10882",
   "row_key": 10882,
   "attrs_offset": 171222,
   "name": "未回填（all_equips key=10882）",
   "name_raw": "商队队员给你的一个瓶子，扔到帝国士兵面前，可以吸引他们的注意力。",
   "name_evidence": "unresolved",
   "type_hint": "营地工具/杂物行",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 194,
   "schema6109_field35_power": 2.12,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10882,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10882,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10883",
   "row_key": 10883,
   "attrs_offset": 171222,
   "name": "哨戒炮台",
   "name_raw": "哨戒炮台",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 194,
   "schema6109_field35_power": 2.12,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10883,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10883,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10889",
   "row_key": 10889,
   "attrs_offset": 171222,
   "name": "哨兵战术霰弹雪地版",
   "name_raw": "哨兵战术霰弹雪地版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 194,
   "schema6109_field35_power": 2.12,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10889,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10889,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10937",
   "row_key": 10937,
   "attrs_offset": 274340,
   "name": "仿生瞬豹霰弹枪雪地版",
   "name_raw": "仿生瞬豹霰弹枪雪地版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 79,
   "schema6109_field35_power": 1.7,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10937,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10937,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10938",
   "row_key": 10938,
   "attrs_offset": 274340,
   "name": "仿生菌焰喷火器",
   "name_raw": "仿生菌焰喷火器，在生物科技的加持下，持续攻击会对敌人造成高额的腐蚀伤害。",
   "name_evidence": "desc-first-map",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 79,
   "schema6109_field35_power": 1.7,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10938,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10938,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10939",
   "row_key": 10939,
   "attrs_offset": 274340,
   "name": "仿生蛛螯典藏版",
   "name_raw": "仿生蛛螯典藏版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 79,
   "schema6109_field35_power": 1.7,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10939,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10939,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "10940",
   "row_key": 10940,
   "attrs_offset": 274340,
   "name": "仿生菌焰喷火器精校版",
   "name_raw": "仿生菌焰喷火器精校版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 79,
   "schema6109_field35_power": 1.7,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 10940,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 10940,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "11001",
   "row_key": 11001,
   "attrs_offset": 215007,
   "name": "未回填（all_equips key=11001）",
   "name_raw": "animator/helicopter/dragon_aircraft.xml",
   "name_evidence": "unresolved",
   "type_hint": "飞行器（路径名行，非武器）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 69,
   "schema6109_field35_power": 1.6,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 11001,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 11001,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "11002",
   "row_key": 11002,
   "attrs_offset": 245934,
   "name": "EM-2电磁雪地版",
   "name_raw": "EM-2电磁雪地版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 108,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 11002,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 11002,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "11003",
   "row_key": 11003,
   "attrs_offset": 244514,
   "name": "EM-3电磁雪地版",
   "name_raw": "EM-3电磁雪地版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 134,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 11003,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 11003,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "11004",
   "row_key": 11004,
   "attrs_offset": 188583,
   "name": "EM-4电磁雪地版",
   "name_raw": "EM-4电磁雪地版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 147,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 11004,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 11004,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "11005",
   "row_key": 11005,
   "attrs_offset": 188212,
   "name": "AUG突击雪地版",
   "name_raw": "AUG突击雪地版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 148,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 11005,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 11005,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "11010",
   "row_key": 11010,
   "attrs_offset": 187449,
   "name": "斯泰尔狙击枪雨战版",
   "name_raw": "斯泰尔狙击枪雨战版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 161,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 11010,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 11010,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "11015",
   "row_key": 11015,
   "attrs_offset": 187047,
   "name": "极速之神",
   "name_raw": "蓝色的极速之神，劈开巨浪，带你一往无前。",
   "name_evidence": "desc-first-map",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 172,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 11015,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 11015,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "11016",
   "row_key": 11016,
   "attrs_offset": 186640,
   "name": "夜骐",
   "name_raw": "夜骐",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 174,
   "schema6109_field35_power": 2.0,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 11016,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 11016,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "11019",
   "row_key": 11019,
   "attrs_offset": 223321,
   "name": "仿生猎鲨锋刃",
   "name_raw": "仿生猎鲨锋刃",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 76,
   "schema6109_field35_power": 1.7,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 11019,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 11019,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "11020",
   "row_key": 11020,
   "attrs_offset": 204128,
   "name": "必胜闪电",
   "name_raw": "必胜闪电",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 39,
   "schema6109_field35_power": 0.8,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 11020,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 11020,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "11021",
   "row_key": 11021,
   "attrs_offset": 204128,
   "name": "弹道测试1",
   "name_raw": "弹道测试1",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 39,
   "schema6109_field35_power": 0.8,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 11021,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 11021,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "11022",
   "row_key": 11022,
   "attrs_offset": 204128,
   "name": "弹道测试2",
   "name_raw": "弹道测试2",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 39,
   "schema6109_field35_power": 0.8,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 11022,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 11022,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  },
  {
   "id": "11023",
   "row_key": 11023,
   "attrs_offset": 204128,
   "name": "弧光电磁雪地版",
   "name_raw": "弧光电磁雪地版",
   "name_evidence": "name-slot",
   "type_hint": "",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "current Documents all_equips row to attrs(schema6109) relation; name backfill 2026-09-04: name-slot short-name read / desc-first human map; no formula or availability claim",
   "schema6109_field23_hurt": 39,
   "schema6109_field35_power": 0.8,
   "provenance": {
    "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "source_entries": [
     {
      "entry_index": 16135,
      "file_id": "A130A31532FAF63C",
      "decoded_sha256": "8573bbe83f2c7be839f072ceb39e3e77bf642ef34a2837f4990a06ac13d2e516",
      "role": "all_equips_base"
     },
     {
      "entry_index": 14847,
      "file_id": "94AB0B3FD057EF01",
      "decoded_sha256": "b57a2f3eb688cf2235c5b5e9f1c476b2b07f46c81ca7c7ee0a290f8c1a65a73f",
      "role": "all_equips_chs"
     }
    ],
    "table": "com\\cdata\\all_equips_data.py",
    "row_key": 11023,
    "field_refs": [
     "id",
     "row_key",
     "attrs_offset",
     "name",
     "name_raw",
     "name_evidence",
     "type_hint",
     "evidence"
    ],
    "name_source": "com\\cdata\\all_equips_data_chs.py#name",
    "source_id": "all-equips-attrs",
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "all-equips-attrs",
       "table": "com\\cdata\\all_equips_data.py",
       "row_key": 11023,
       "field_refs": [
        "id",
        "row_key",
        "attrs_offset",
        "name",
        "name_raw",
        "name_evidence",
        "type_hint",
        "evidence"
       ]
      }
     ]
    },
    "upstream": {
     "package_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
     "entry_index": null,
     "file_id": null,
     "decoded_sha256": null,
     "role": "com\\cdata\\all_equips_data.py"
    }
   },
   "status_tags": [
    "static config"
   ]
  }
 ]
};
