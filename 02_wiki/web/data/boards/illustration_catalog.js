window.WIKI_BOARD_illustration_catalog = {
 "meta": {
  "name": "图鉴收集总表",
  "category": "四、资料层 / （六）图鉴收集",
  "generated": "",
  "id_label": "条目ID",
  "source_server": "简单生存服（体验服 Documents 快照）",
  "evidence": "structure",
  "card_mode": "roster",
  "hide_media": true,
  "card_summary": [
   [
    "name",
    "条目"
   ],
   [
    "desc",
    "说明"
   ]
  ],
  "field_labels": {
   "item_id": "条目ID",
   "desc": "说明",
   "extra_desc": "补充"
  },
  "state_summary": {
   "条目": 373
  },
  "provenance": {
   "contract_version": 3,
   "audit_status": "passed",
   "contract": "frozen-audited-artifact",
   "source_locks": [
    {
     "source_id": "documents-py314-current",
     "role": "primary",
     "sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "bytes": 237984616,
     "mtime_ns": 0
    }
   ],
   "source_scope": {
    "cross_source_policy": "no-cross-source-field-join",
    "integer_join_policy": "no-equal-integer-join",
    "runtime_final_policy": "unknown-unless-runtime-proven"
   },
   "decode": {
    "kind": "vm-bytecode-exec+legacy-x-container",
    "tables": {
     "super_fashion_lottery_conf_data": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa",
     "special_chip_lottery_hd_conf_data": "8f727d9d651222990150403b94db1b90ce924f11203a0ed9bedbafa1be504e5f",
     "lottery_team_hd_conf_data": "638882b2364036f07d490246731da366507e127ece21022263d79d8633c9b862",
     "lottery_team_hd_reward_data": "e61444c3bc9f1ac8fc8a7d2297917b67450188f12575df82ca6da6f56d42ced7",
     "building_lottery_v2_conf_data": "95f24bb90f018ae3d4e04d4a03a56b307b4df17b37a2b4e4f1f783f1b4bb7582",
     "weapon_decomposition_base_conf_data": "5ba93c96f7fc41b35ca167048a81ea92018b913eea9e126ec944a29670e3e43f",
     "multi_optional_lottery_conf_data": "5ce4f3859abcc3f61935fee044473f49e7d1bdde3558e4696009e3d851398899",
     "vehicle_lottery_base_conf_data": "4bc364ea52d5aecc69492462782c03ae83b0f6514cec513dd671799c353e0a87",
     "falcon_strike_conf_data": "8cf75e62ff5d9c7d8d4d06c1057a1058f97d0844930e1a5bfb6cfeca48eb118b",
     "build_limit_nucleus_lottery_conf_data": "182f702d7e86a1ac2d7af828f8b872409b7affb9e62601ff511a7b5676e4671e",
     "limit_nucleus_lottery_conf_data": "8499eaa329440ae3e9409b7cca3762320a461fd2701a8870b58c9c846cc76dd3",
     "lottery_live_bonus_data": "143e1b343aed5c3e7de21313286529c6d64efc38a1f49a0fac4daa0adb14b770",
     "pigeon_wish_conf_data": "1ac2e02cc8c72e7011244d20e8579cd14268af2bee91d22cbafa72282dc5f206",
     "xi_yang_yang_lottery_reward_pool_conf_data": "571bc4db819ef949353de5dc38dd7f8961fff7d25bec7a95a7a6790f2ebfccda",
     "xi_yang_yang_lottery_conf_data": "8a0fd9f93210cb35deea0262520918a0da930718ddf07bddec61f84e7e0f81c0"
    },
    "table_file_id": "A703C08E329A6FE2",
    "replay": {
     "rows": 3535
    }
   }
  },
  "notes": "一行 = illustration_collect_item_data 一行。",
  "package_sha": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e"
 },
 "periods": [],
 "items": [
  {
   "id": "illus_4",
   "item_id": 4,
   "name": "再生之种",
   "kind": "图鉴",
   "desc": "向指定位置抛出大量孢子",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 4,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 4,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_138",
   "item_id": 138,
   "name": "再生之树",
   "kind": "图鉴",
   "desc": "拾取孢子进行充能，充能满值后可以使用持续14秒的【再生之树】",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 138,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 138,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_181",
   "item_id": 181,
   "name": "蔓藤绞杀",
   "kind": "图鉴",
   "desc": "对被【束缚蔓藤】的目标进行麻痹和绞杀",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 181,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 181,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_226",
   "item_id": 226,
   "name": "束缚蔓藤",
   "kind": "图鉴",
   "desc": "拾取孢子进行充能，充能满值后可以使用持续10秒的【束缚蔓藤】",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 226,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 226,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_271",
   "item_id": 271,
   "name": "浮莲追光苞",
   "kind": "图鉴",
   "desc": "从再生莲中释放追踪花粉，子株会释放花粉攻击敌人",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 271,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 271,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_316",
   "item_id": 316,
   "name": "花粉雾光球",
   "kind": "图鉴",
   "desc": "点击释放雾光花粉围绕自己，对附近的敌人造成伤害",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 316,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 316,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_361",
   "item_id": 361,
   "name": "粉爆弹",
   "kind": "图鉴",
   "desc": "点击释放花粉爆弹，对命中的敌人造成伤害",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 361,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 361,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_406",
   "item_id": 406,
   "name": "沼泥气爆弹",
   "kind": "图鉴",
   "desc": "点击蓄力形成爆弹，再次点击将释放攻击前方命中的敌人。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 406,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 406,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_451",
   "item_id": 451,
   "name": "涡流气旋盾",
   "kind": "图鉴",
   "desc": "释放漩涡气流格挡来自面前的伤害",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 451,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 451,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_496",
   "item_id": 496,
   "name": "焰星陨火雨",
   "kind": "图鉴",
   "desc": "点击按钮释引来一道陨星之火，对命中的敌人造成伤害。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 496,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 496,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_541",
   "item_id": 541,
   "name": "御虫术",
   "kind": "图鉴",
   "desc": "召唤芽虫攻击敌人",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 541,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 541,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_586",
   "item_id": 586,
   "name": "跃空寻踪球",
   "kind": "图鉴",
   "desc": "点击按钮投掷能量球，爆炸后会自动追踪敌人并造成伤害。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 586,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 586,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_631",
   "item_id": 631,
   "name": "雷鸣聚光箭",
   "kind": "图鉴",
   "desc": "点击按钮投掷能量剑，对命中的敌人造成大量伤害。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 631,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 631,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_676",
   "item_id": 676,
   "name": "莲株缚身藤",
   "kind": "图鉴",
   "desc": "点击按钮向前方抛出藤蔓，将缠绕命中的敌人并造成伤害。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 676,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 676,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_721",
   "item_id": 721,
   "name": "寒冰锥",
   "kind": "图鉴",
   "desc": "点击按钮投掷冰晶，将命中的敌人冻结。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 721,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 721,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_766",
   "item_id": 766,
   "name": "燃磷冷焰",
   "kind": "图鉴",
   "desc": "点击按钮投掷再生火焰，对范围内敌人造成伤害。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 766,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 766,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_811",
   "item_id": 811,
   "name": "狂暴爪击",
   "kind": "图鉴",
   "desc": "点击按钮施展连续爪击，对范围内敌人造成伤害。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 811,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 811,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_856",
   "item_id": 856,
   "name": "孢子跳跃",
   "kind": "图鉴",
   "desc": "点击按钮可以进行跳跃，该跳跃被强化。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 856,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 856,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_899",
   "item_id": 899,
   "name": "怪诞雷鸣球",
   "kind": "图鉴",
   "desc": "召唤数个电球，敌人接触到电球后会受到可观的伤害。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 899,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 899,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_944",
   "item_id": 944,
   "name": "惊鸣落雷击",
   "kind": "图鉴",
   "desc": "召唤威力强大的雷电攻击敌人",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 944,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 944,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_989",
   "item_id": 989,
   "name": "蚀骨烟雾",
   "kind": "图鉴",
   "desc": "在原地释放烟雾并后跳回避，接触到烟雾的敌人持续受到伤害。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 989,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 989,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_1034",
   "item_id": 1034,
   "name": "烟火再生莲",
   "kind": "图鉴",
   "desc": "从再生莲中取出子株放置于地面，子株会喷射酸液攻击敌人。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 1034,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 1034,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_1079",
   "item_id": 1079,
   "name": "追击花粉炮",
   "kind": "图鉴",
   "desc": "从再生莲释放花粉光球，光球会自动发射多枚光弹攻击敌人。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 1079,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 1079,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_1124",
   "item_id": 1124,
   "name": "扩散腐蚀波",
   "kind": "图鉴",
   "desc": "从再生莲中释放强力射线，对沿途的敌人造成伤害。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 1124,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 1124,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_1169",
   "item_id": 1169,
   "name": "跳跃突斩",
   "kind": "图鉴",
   "desc": "点击按钮使用蛮力重重砸地，并对范围内敌人造成伤害。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 1169,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 1169,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_1214",
   "item_id": 1214,
   "name": "定身丝弹",
   "kind": "图鉴",
   "desc": "点击按钮向前方抛出丝线，对命中的敌人造成定身效果和伤害。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 1214,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 1214,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_1259",
   "item_id": 1259,
   "name": "腐沼引爆",
   "kind": "图鉴",
   "desc": "点击按钮释放腐蚀液，对命中的敌人造成伤害。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 1259,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 1259,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_1304",
   "item_id": 1304,
   "name": "酸液猛掷",
   "kind": "图鉴",
   "desc": "点击按钮可释放一道酸液，对命中的敌人造成伤害。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 1304,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 1304,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_1349",
   "item_id": 1349,
   "name": "爆怨弹",
   "kind": "图鉴",
   "desc": "点击按钮爆炸，对范围内的敌人造成爆炸伤害。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 1349,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 1349,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_1394",
   "item_id": 1394,
   "name": "淤泥吼",
   "kind": "图鉴",
   "desc": "点击按钮释放一道攻击波，对命中的敌人造成伤害。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 1394,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 1394,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_1439",
   "item_id": 1439,
   "name": "聚雾弹",
   "kind": "图鉴",
   "desc": "点击按钮吐出烟雾，对范围内的敌人造成伤害。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 1439,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 1439,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_1484",
   "item_id": 1484,
   "name": "珍珠项链",
   "kind": "图鉴",
   "desc": "格瑞丝赠与你的骑士纪念物。她愿以旧世界价值连城的珠宝，从你手中换得丈夫勇气的明证。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 1484,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 1484,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_1519",
   "item_id": 1519,
   "name": "银哨",
   "kind": "图鉴",
   "desc": "兰斯洛特赠与你的骑士纪念物。这是骑士间信任的证明，以此向你为她送达的真相致谢。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 1519,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 1519,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_1554",
   "item_id": 1554,
   "name": "报纸专栏残页",
   "kind": "图鉴",
   "desc": "旧世界报纸《日出报》上的小专栏，用于公告那些已被逮捕落网的逃犯曾经的恶行，设此专栏的目的是引导市民遵纪守法，引以为戒。#r因为是不知名小报的栏目，出于销量的考量，在信息的取舍上有故意制造噱头的嫌疑。#r #r“红杉镇一男子偷窃数名果农邻居的园艺剪刀，被发现时正在使用失窃物品为自家的枣红马修脚，遭到调查员的当场逮捕。#r男子声称自己心爱的小马只接受园艺钳子的修剪，随行调查员立刻指出了男子行为的不当之处。#r在马棚的角落里找到已经被男子掩埋废弃的、严重折损的园艺剪刀。#r这些被偷来的园艺剪刀已经被强制没收，返还给受害邻居。”#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 1554,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 1554,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_1586",
   "item_id": 1586,
   "name": "报纸专栏残页",
   "kind": "图鉴",
   "desc": "旧世界报纸《日出报》上的小专栏，用于公告那些已被逮捕落网的逃犯曾经的恶行，设此专栏的目的是引导市民遵纪守法，引以为戒。#r因为是不知名小报的栏目，出于销量的考量，在信息的取舍上有故意制造噱头的嫌疑。#r #r“滨海新市一男子在后院挖掘巨大深坑。#r连夜降水后，坑内积水因发出臭味而被邻居举报。#r调查员前往勘探，未发现可疑物品。”#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 1586,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 1586,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_1620",
   "item_id": 1620,
   "name": "报纸专栏残页",
   "kind": "图鉴",
   "desc": "旧世界报纸《日出报》上的小专栏，用于公告那些已被逮捕落网的逃犯曾经的恶行，设此专栏的目的是引导市民遵纪守法，引以为戒。#r因为是不知名小报的栏目，出于销量的考量，在信息的取舍上有故意制造噱头的嫌疑。#r #r“双路市一男子蒙住双眼去镇上偷窃财物，被当场擒获。#r经询问得知，蒙眼的原因竟是不希望调查员看见自己。”#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 1620,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 1620,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_1654",
   "item_id": 1654,
   "name": "报纸专栏残页",
   "kind": "图鉴",
   "desc": "旧世界报纸《日出报》上的小专栏，用于公告那些已被逮捕落网的逃犯曾经的恶行，设此专栏的目的是引导市民遵纪守法，引以为戒。#r因为是不知名小报的栏目，出于销量的考量，在信息的取舍上有故意制造噱头的嫌疑。#r #r“接到圣托帕尼多名游客举报，附近有不法分子偷窃泳装和随身财物等。#r失窃泳装样式不一，作案取向与原因均不明。#r多番查证后，调查员终于捣毁了一处长期存在的伪装为异装俱乐部的诈骗窝点。”#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 1654,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 1654,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_1688",
   "item_id": 1688,
   "name": "报纸专栏残页",
   "kind": "图鉴",
   "desc": "旧世界报纸《日出报》上的小专栏，用于公告那些已被逮捕落网的逃犯曾经的恶行，设此专栏的目的是引导市民遵纪守法，引以为戒。#r因为是不知名小报的栏目，出于销量的考量，在信息的取舍上有故意制造噱头的嫌疑。#r #r“莱文市内一小作坊的打印机墨盒连番失窃。#r调查员经过长时间的守株待兔，终于锁定了嫌疑人男子的身份：员工托马斯。#r该男子使用墨粉将面孔涂污，于深夜时出现在街头小巷内惊吓行人。#r关于作案的原因，根据其同伴的推测：#r托马斯可能是办公压力实在太大，才会出此下策。”#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 1688,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 1688,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_1720",
   "item_id": 1720,
   "name": "胡桃夹子木偶",
   "kind": "图鉴",
   "desc": "旧世界大受青睐的玩偶系列，具有悠久的历史。#r在同名舞剧的塑造下，胡桃夹子成为了勇气的象征，是赠送给孩子们的礼物佳品。#r本系列玩偶在旧世界发售时，曾与其它商品捆绑销售，#r为了凑齐整套胡桃夹子，需要费上一番力气。#r字面意思：真的能够夹核桃。#r全套一共12个，据说集齐之后能够带来好运。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 1720,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 1720,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_1753",
   "item_id": 1753,
   "name": "《小猫瑞文历险记》",
   "kind": "图鉴",
   "desc": "《小猫瑞文历险记》是旧世界著名奇幻小说，与罗森波顿系列齐名，并称为奇幻小说双璧。#r此书为该系列的第八部《真相前夕》：#r船上频繁出现的反常现象令劳尔非常不安。#r跟随着梦中的指示，劳尔潜入了船只上层储存资料的密室。#r劳尔觉得自己不对劲，他记得自己明明不认识字的，如今却能够毫无障碍地阅读这些加密文件。#r——这些都是梅丽尔精神病院内患者的档案。#r显然这是一艘特殊的航船，除了押运的士兵之外，船上载满了精神病人。#r据档案显示：这些病人共同的症状是幻听。#r而这艘船只正在执行的秘密计划正是利用这些精神病人，利用他们的症状来记录来自深海的回声。#r外面突然传来的嘈杂声打断了劳尔的思绪，他急忙跑到外面试图混到安全的地方。#r然而摆在眼前的是如玻璃刀锋一般拍下的层层海浪。#r梦中的场景真的出现在了劳尔的眼前。#r士兵们惊恐地哭嚎着，眼泪如同初夏的泉水，正从一双泉眼中汩汩涌出。#r而那些往日沉默地晒着太阳的乘客们，却大笑着、手舞足蹈地向着海浪发出阵阵欢呼。#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 1753,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 1753,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_1787",
   "item_id": 1787,
   "name": "《小猫瑞文历险记》",
   "kind": "图鉴",
   "desc": "《小猫瑞文历险记》是旧世界著名奇幻小说，与罗森波顿系列齐名，并称为奇幻小说双璧。#r此书为该系列的第九部《猫咪救主》：#r海浪阵阵拍下，船只剧烈地摇晃着，劳尔只能勉强地就近抓住舷窗的窗棱，固定住自己的站位。#r猫咪瑞文从兜帽中探出头来，锋利的瓜子用力地勾住主人的帽衫，受到惊吓的它不安地对着海浪嘶叫。#r浪潮的拍击暂时止息。#r原本在空中盘旋的白色海鸥早已不知所踪，反而是不知道从哪里来的乌鸦开始攻击站在甲板上的众人。#r乌鸦急速冲击，尖利的喙成为它们绝佳的武器。#r在乌鸦们的激烈攻势下，试图趁机逃回下层船舱的劳尔被掀翻在地。#r正在此时，小猫瑞文立刻挣脱了劳尔的怀抱！#r它像勇敢的胡桃夹子一样，摆出战斗姿态嘶吼着与群鸦对峙。#r瑞文英勇地暂时击退了乌鸦们，劳尔立刻抓住机会，从甲板上迅速起身。#r他一把捞起警觉的瑞文，一人一猫，向着自己的藏身之处，狂奔而去！#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 1787,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 1787,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_1821",
   "item_id": 1821,
   "name": "黑匣子",
   "kind": "图鉴",
   "desc": "沉水的黑匣子，年代不详，解析后能得到一些神秘的信息。#r可惜能够捕捉到的电讯号断断续续，准度有限：#r“相比之下，海上的生活竟然还有点安稳。”#r“我之前在灯塔驻扎过一阵子。”#r“灯塔的引路人，最害怕夜晚。”#r“就像那些向着火光扑去、成群的飞蛾，那些‘东西’好像也有感光性似的。”#r“脚踩着对方，向着光源处爬去，我们躲在远处，连喘息都要小心翼翼……灯塔简直就像一根被蚜虫寄生的枝条。”#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 1821,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 1821,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_1853",
   "item_id": 1853,
   "name": "黑匣子",
   "kind": "图鉴",
   "desc": "沉水的黑匣子，年代不详，解析后能得到一些神秘的信息。#r可惜能够捕捉到的电讯号断断续续，准度有限：#r“有一件事我一直觉得很奇怪，我觉得……”#r“……好像很久没有见过蚊子了？”#r“以往之所以能够在海上见到蚊子……似乎也是因为蚊子会在近海港口处偷偷溜进船里……”#r“本身海洋上应该是没有蚊子的生存环境的。”#r“话虽如此，最近这一年似乎都没有见过蚊子了。”#r“甚至偶尔停靠在港口的时候，也完全回想不起来关于遇到蚊子的记忆了。”#r“虽然是好事，但为什么觉得有点不安呢？”#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 1853,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 1853,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_1885",
   "item_id": 1885,
   "name": "黑匣子",
   "kind": "图鉴",
   "desc": "沉水的黑匣子，年代不详，解析后能得到一些神秘的信息。#r可惜能够捕捉到的电讯号断断续续，准度有限：#r“一直以来，我都坚信地图测绘与地形勘测是非常神圣的工作。”#r“地图最重要的就是准确，它为旅行者带去保障。”#r“我随船只前往海洋各处，见识过各种各样的奇观。”#r“直到亲眼目睹了那仿佛大地的伤疤一般的存在……”#r“岩浆在海水下涌动着，夕阳黯然失色。”#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 1885,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 1885,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_1917",
   "item_id": 1917,
   "name": "黑匣子",
   "kind": "图鉴",
   "desc": "沉水的黑匣子，年代不详，解析后能得到一些神秘的信息。#r可惜能够捕捉到的电讯号断断续续，准度有限：#r“我和这些躲在船舱里瑟瑟发抖的虫豸可不一样。”#r“好奇心！可是人类用以对抗未知的最为强悍的力量。”#r“报刊上那些大惊小怪的观点，都只不过是弱者们的呓语罢了。”#r“等着瞧吧，穿过这片风浪，等待着我们抵达的必将是崭新的世界。”#r“我必将带回前无古人后无来者的重大发现。”#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 1917,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 1917,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_1949",
   "item_id": 1949,
   "name": "黄色橡皮鸭子",
   "kind": "图鉴",
   "desc": "橡胶材质的小黄鸭子，底部出现了破损，因此失去了浮水的能力。#r因为材质的原因，仍旧保留着较为光滑的表面。#r据说蚀礁海域的神秘生物拥有不逊色于人类的智力水平，它非常喜欢黄色物体，这似乎是此种橡胶制品大多见于污秽海域之中的原因所在。#r制作年代已不可考，朴拙但经久的工艺似乎暗示了其旧世界产物的身份。#r捡起这样的东西有什么用处呢？#r一只又一只未被捡起的小黄鸭子依旧孤零零地沉睡在海洋的深处。#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 1949,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 1949,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_1993",
   "item_id": 1993,
   "name": "报纸专栏残页",
   "kind": "图鉴",
   "desc": "旧世界报纸《日出报》上的小专栏，用于公告那些已被逮捕落网的逃犯曾经的恶行，设此专栏的目的是引导市民遵纪守法，引以为戒。#r因为是不知名小报的栏目，出于销量的考量，在信息的取舍上有故意制造噱头的嫌疑。#r #r“莱文市一男子全天候跟踪拍摄著名歌姬瑞贝卡，严重影响了对方的正常生活。#r该男子的行为一经曝光，便受到市民的强烈谴责。#r在采访中，市民们表示：瑞贝卡是大家的瑞贝卡。#r随后，某小报放出消息，称即将刊载该男子为其提供的独家消息。#r消息称，瑞贝卡并不是外交官克兰西的亲生女儿。#r其人性格多变，时而被拍摄到面色冷淡的样子，与平日里热情示人的温柔形象判若两人，很是有两副面孔。#r然而市民朋友们热情不减，表示自己依旧会继续支持瑞贝卡。#r涉事男子已被调查员控制起来，但有关瑞贝卡身份的种种猜测仍旧存在。”#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 1993,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 1993,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_2027",
   "item_id": 2027,
   "name": "罗波鱼的骨架",
   "kind": "图鉴",
   "desc": "旧世界广泛存在于海域内的鱼种，体型大小不等，有记载的体型最为巨大的罗波鱼甚至与现通行于海上的双体船的大小无异。#r肉质细嫩、口感如豆腐的罗波鱼曾经是重要而珍稀的海域鱼类资源。#r不同鱼类、不同体型的鱼本身所拥有的脊椎数目各不相同，但奇怪的是，罗波鱼的脊椎数目似乎绝大多数都是单数。#r“物以稀为贵”#r——旧世界的居民相信拥有偶数的鱼骨的罗波鱼能够带来好运。#r诸般际遇下，早已灭绝的古老生物，如今穿梭时间的长河，唯有其骸骨沉眠于深邃的海水之下一如往昔。#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 2027,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 2027,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_2071",
   "item_id": 2071,
   "name": "报纸专栏残页",
   "kind": "图鉴",
   "desc": "旧世界报纸《日出报》上的小专栏，用于公告那些已被逮捕落网的逃犯曾经的恶行，设此专栏的目的是引导市民遵纪守法，引以为戒。#r因为是不知名小报的栏目，出于销量的考量，在信息的取舍上有故意制造噱头的嫌疑。#r #r“著名歌姬瑞贝卡之父近日于莱文市大剧院前街遭到袭击，经及时治疗，现已脱离生命危险。#r调查员在逮捕疑犯时遭到对方的激烈抵抗，声称克兰西家族正蕴藏着天大的阴谋，呼吁市民们提高警惕。”#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 2071,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 2071,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_2105",
   "item_id": 2105,
   "name": "光滑的鹅卵石",
   "kind": "图鉴",
   "desc": "被打磨得相当光滑的鹅卵石石子。#r经过水流的搬运和磨蚀，已经失去了自己的棱角，但身上负载的纹路线理却成为了推算地质年代的重要依据。#r旧世界的沿海村落的渔民往往会将圆滚滚的鹅卵石捡回家去送给自己的孩子。#r小小石子，充满童趣。#r随着村落被感染者占领，只留下一堆堆鹅卵石继续见证着沧海桑田。#r存在，就是它的意义本身。#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 2105,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 2105,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_2149",
   "item_id": 2149,
   "name": "胡桃夹子木偶",
   "kind": "图鉴",
   "desc": "旧世界大受青睐的玩偶系列，具有悠久的历史。#r在同名舞剧的塑造下，胡桃夹子成为了勇气的象征，是赠送给孩子们的礼物佳品。#r本系列玩偶在旧世界发售时，曾与其它商品捆绑销售，#r为了凑齐整套胡桃夹子，需要费上一番力气。#r字面意思：真的能够夹核桃。#r全套一共12个，据说集齐之后能够带来好运。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 2149,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 2149,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_2182",
   "item_id": 2182,
   "name": "风干的鹦鹉螺壳",
   "kind": "图鉴",
   "desc": "鹦鹉螺依靠近乎等角螺线分布的壳室，调节其中的气体存量，以控制自身的运动浮潜，并利用自己的触手握住礁石来停留休息。#r当它逝去时，赖以栖身的壳脱离软体，随洋流裹挟，去往海域各处。#r曾经封闭的壳室，如今已经对整片海洋敞开。#r海水穿过壳身的缝隙，带起一阵细小的涡旋。#r世界上并没有两个完全一致的鹦鹉螺壳，尽管它们看起来实在是非常相似。#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 2182,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 2182,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_2226",
   "item_id": 2226,
   "name": "胡桃夹子木偶",
   "kind": "图鉴",
   "desc": "旧世界大受青睐的玩偶系列，具有悠久的历史。#r在同名舞剧的塑造下，胡桃夹子成为了勇气的象征，是赠送给孩子们的礼物佳品。#r本系列玩偶在旧世界发售时，曾与其它商品捆绑销售，#r为了凑齐整套胡桃夹子，需要费上一番力气。#r字面意思：真的能够夹核桃。#r全套一共12个，据说集齐之后能够带来好运。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 2226,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 2226,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_2259",
   "item_id": 2259,
   "name": "金枪鱼",
   "kind": "图鉴",
   "desc": "习性：肉食性咸水鱼#r有“海洋黄金”之称的珍贵海洋鱼类，肉质富含各种矿物质，做成生鱼片食用尤其美味。传闻在海岛部分区域的白天可以捕获。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 2259,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 2259,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_2297",
   "item_id": 2297,
   "name": "胡桃夹子木偶",
   "kind": "图鉴",
   "desc": "旧世界大受青睐的玩偶系列，具有悠久的历史。#r在同名舞剧的塑造下，胡桃夹子成为了勇气的象征，是赠送给孩子们的礼物佳品。#r本系列玩偶在旧世界发售时，曾与其它商品捆绑销售，#r为了凑齐整套胡桃夹子，需要费上一番力气。#r字面意思：真的能够夹核桃。#r全套一共12个，据说集齐之后能够带来好运。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 2297,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 2297,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_2330",
   "item_id": 2330,
   "name": "秋刀鱼",
   "kind": "图鉴",
   "desc": "习性：肉食性咸水鱼#r秋刀鱼体长而纤细，形似长刀而得名。适合多种方法烹饪，是不可多得的食材。似乎在夜晚更容易捕获。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 2330,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 2330,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_2368",
   "item_id": 2368,
   "name": "胡桃夹子木偶",
   "kind": "图鉴",
   "desc": "旧世界大受青睐的玩偶系列，具有悠久的历史。#r在同名舞剧的塑造下，胡桃夹子成为了勇气的象征，是赠送给孩子们的礼物佳品。#r本系列玩偶在旧世界发售时，曾与其它商品捆绑销售，#r为了凑齐整套胡桃夹子，需要费上一番力气。#r字面意思：真的能够夹核桃。#r全套一共12个，据说集齐之后能够带来好运。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 2368,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 2368,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_2401",
   "item_id": 2401,
   "name": "鳕鱼",
   "kind": "图鉴",
   "desc": "生活在海洋中的冷水性鱼类，秋季摄食最为旺盛。可用于烹饪。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 2401,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 2401,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_2439",
   "item_id": 2439,
   "name": "鲑鱼",
   "kind": "图鉴",
   "desc": "习性：杂食性咸水鱼#r鲑鱼体侧扁，鳞片细小，肉质紧密鲜美，肉色为粉红色并具有弹性，不可多得的食材，可用于烹饪。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 2439,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 2439,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_2477",
   "item_id": 2477,
   "name": "带鱼",
   "kind": "图鉴",
   "desc": "习性：肉食性咸水鱼#r一种凶猛的肉食鱼，白天浮在海水中层，晚上就降到海底，可用于烹饪。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 2477,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 2477,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_2515",
   "item_id": 2515,
   "name": "海带",
   "kind": "图鉴",
   "desc": "海带热量低、蛋白质适中、矿物质含量丰富，是一种理想的天然海洋食品。加入汤中还能为汤增加咸鲜味。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 2515,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 2515,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_2555",
   "item_id": 2555,
   "name": "胡桃夹子木偶",
   "kind": "图鉴",
   "desc": "旧世界大受青睐的玩偶系列，具有悠久的历史。#r在同名舞剧的塑造下，胡桃夹子成为了勇气的象征，是赠送给孩子们的礼物佳品。#r本系列玩偶在旧世界发售时，曾与其它商品捆绑销售，#r为了凑齐整套胡桃夹子，需要费上一番力气。#r字面意思：真的能够夹核桃。#r全套一共12个，据说集齐之后能够带来好运。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 2555,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 2555,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_2588",
   "item_id": 2588,
   "name": "深海鲑鱼",
   "kind": "图鉴",
   "desc": "生活在深海的鲑鱼，肉质鲜嫩肥美，口感极佳。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 2588,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 2588,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_2628",
   "item_id": 2628,
   "name": "《小猫瑞文历险记》",
   "kind": "图鉴",
   "desc": "《小猫瑞文历险记》是旧世界著名奇幻小说，与罗森波顿系列齐名，并称为奇幻小说双璧。#r此书为该系列的第一部 《海滨新生》：#r生活在海边的小伙子劳尔，在出海捕鱼时遇到了一艘救生艇，小小的船只上仅有一只瘦骨嶙峋的毛色斑驳的小猫。#r因为小猫的叫声听起来像乌鸦，善良的劳尔收养了这只海上来客，并为之起名为瑞文。#r相处之中，劳尔发现瑞文是一只聪明异常的小猫，小猫瑞文展示出的聪敏机警时常令劳尔大为惊奇。#r一人一猫相依为命，在海边过着平静的生活。#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 2628,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 2628,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_2662",
   "item_id": 2662,
   "name": "飞鱼",
   "kind": "图鉴",
   "desc": "飞鱼长相奇特，胸鳍特别发达，像鸟类的翅膀一样。可用于烹饪。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 2662,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 2662,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_7770",
   "item_id": 7770,
   "name": "奥兹帮突袭兵",
   "kind": "图鉴",
   "desc": "奥兹帮的成员都是一堆从监狱里逃出来的逃犯，或者说，疯子。他们狂热地围绕在奥兹周围，使用炸弹袭击敌人。啊！真是疯子！",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 7770,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 7770,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_7882",
   "item_id": 7882,
   "name": "母体：1号",
   "kind": "图鉴",
   "desc": "最初的母体之一，沉睡于莱文市的起源之地。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 7882,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 7882,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_7936",
   "item_id": 7936,
   "name": "奥兹帮狙击兵",
   "kind": "图鉴",
   "desc": "奥兹帮的成员都是一堆从监狱里逃出来的逃犯，或者说，疯子。他们狂热地围绕在奥兹周围，听从奥兹的一切指挥；从某种意义上说，他们比感染者更加危险。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 7936,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 7936,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_9359",
   "item_id": 9359,
   "name": "断刃武士",
   "kind": "图鉴",
   "desc": "本是最厌恶感染者的人，却在死后变为了感染者。不甘被他埋藏在残躯裂刃下，无时无刻不在渴望着解脱。一场公平的决斗，是对曾经的探险队英雄最大的尊重。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 9359,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 9359,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_9417",
   "item_id": 9417,
   "name": "叛誓感染者",
   "kind": "图鉴",
   "desc": "手中拿着长钉，吸收了海洋中的特殊结晶而拥有了不同的能力。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 9417,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 9417,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_9512",
   "item_id": 9512,
   "name": "殉道伏师",
   "kind": "图鉴",
   "desc": "曾经的探险队队长，进入巢穴殉道牺牲。她执念最深，走得最远，剧烈的感染让她变成了自己也会厌恶的怪物，配合伏师残存的符阵能力，不断污染着周围的土地与生物，渴望得到最后的安息。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 9512,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 9512,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_9756",
   "item_id": 9756,
   "name": "鬼新娘",
   "kind": "图鉴",
   "desc": "翅膀上长有两只巨大双眼的变异体，号哭时会从中喷出眼泪般的液球。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 9756,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 9756,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_9820",
   "item_id": 9820,
   "name": "报纸专栏残页",
   "kind": "图鉴",
   "desc": "旧世界报纸《日出报》上的小专栏，用于公告那些已被逮捕落网的逃犯曾经的恶行，设此专栏的目的是引导市民遵纪守法，引以为戒。#r因为是不知名小报的栏目，出于销量的考量，在信息的取舍上有故意制造噱头的嫌疑。#r #r“著名的莱辛港棒球队近日消息，多名成员称自己的球具被涂写上了不明神秘花纹。#r仓库管理员称自己目击到凯尔文——球队内一位常年坐冷板凳的球员，周末的时候曾独自前往俱乐部进行挥棒练习。#r双方还因为场地清理的问题而发生口角。#r警方立刻前往其住处进行调查，该名男子已经不知所踪。#r经过调查员的多日蹲守，该名队员最终被逮捕。”#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 9820,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 9820,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_9895",
   "item_id": 9895,
   "name": "完美奥兹",
   "kind": "图鉴",
   "desc": "窃取游匪奥兹的DNA复制出的超级士兵，曾伪装成无智战斗傀儡欺骗并暗杀了大量实验人员。因其过于危险无法控制且体内病毒浓度过高，被遗弃在实验室内。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 9895,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 9895,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_9947",
   "item_id": 9947,
   "name": "胡桃夹子木偶",
   "kind": "图鉴",
   "desc": "旧世界大受青睐的玩偶系列，具有悠久的历史。#r在同名舞剧的塑造下，胡桃夹子成为了勇气的象征，是赠送给孩子们的礼物佳品。#r本系列玩偶在旧世界发售时，曾与其它商品捆绑销售，#r为了凑齐整套胡桃夹子，需要费上一番力气。#r字面意思：真的能够夹核桃。#r全套一共12个，据说集齐之后能够带来好运。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 9947,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 9947,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_10021",
   "item_id": 10021,
   "name": "马图斯",
   "kind": "图鉴",
   "desc": "先天失明的孤儿，被修道院的神父带回修道院抚养，负责看守钟楼，虔诚无比。修道院的感染爆发后，马图斯即便失去了意识，也仍然一遍又一遍敲响钟声。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 10021,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 10021,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_10074",
   "item_id": 10074,
   "name": "报纸专栏残页",
   "kind": "图鉴",
   "desc": "旧世界报纸《日出报》上的小专栏，用于公告那些已被逮捕落网的逃犯曾经的恶行，设此专栏的目的是引导市民遵纪守法，引以为戒。#r因为是不知名小报的栏目，出于销量的考量，在信息的取舍上有故意制造噱头的嫌疑。#r #r“佛伦大学城一男子向报纸专栏投稿，称自己已经在传奇史诗残本《埃兰萨迦》中破解了古奥肯瑟帝国的遗迹所在。#r此言一出，立刻引发舆论轰动。#r该男子声称埃兰人早已掌控了海洋内的高维力量存在，古帝国的毁灭其实是出于外星人的意识。#r学界泰斗发文驳斥：全乃无稽之谈。#r该男子大举募捐善款，声称这笔巨额捐款将被用于带领全人类揭开自身族群的起源之谜。#r不久后卷款潜逃，踪迹全无。#r经过调查员长期的追踪，该嫌犯现已被逮捕。”#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 10074,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 10074,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_10106",
   "item_id": 10106,
   "name": "铁制的风向鸡",
   "kind": "图鉴",
   "desc": "所有的水都是水。#r据记载，为了证实世界上所有的水都是彼此相连的。#r旧德雷福斯治下，大富商阿尔弗莱德进行了这样一项疯狂的实验：#r他指挥自家船舶公司的成员们，利用往来的商船将船只上常见的指示风信的铁质风向鸡投向海域的各处，以证明水体相连。#r铺天盖地的报刊报导，令这项夸张的所谓的“科学”实验更像是哗众取宠的宣传活动。#r与此同时，神秘学爱好者则发文声称，选择风向鸡乃是出于某种压制邪祟的另外打算。#r然而这种无稽之谈很快就被市民们遗忘了。#r铁质的风向鸡外壳上镀有神秘的金属涂层，使其免于为海水所锈蚀。#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 10106,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 10106,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_10191",
   "item_id": 10191,
   "name": "吞世腐根",
   "kind": "图鉴",
   "desc": "排污区的虬结根系因过量吸收PRE系列废液后形成的病毒共生体。其气根疯狂吞噬地下结构，喷吐的朽烂泥浆将整片生态区腐蚀成毒潭，最终被焊死在废弃反应井中。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 10191,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 10191,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_10284",
   "item_id": 10284,
   "name": "序列体-守护者201",
   "kind": "图鉴",
   "desc": "被特殊改造过的序列体，双手是巨大的盾牌，防御力惊人。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 10284,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 10284,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_10416",
   "item_id": 10416,
   "name": "芒刺肿腹体",
   "kind": "图鉴",
   "desc": "背上长有坚硬芒刺的变异体，因未知原因，体态呈现出一种诡异的浮肿。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 10416,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 10416,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_10521",
   "item_id": 10521,
   "name": "芒刺跳蛛体",
   "kind": "图鉴",
   "desc": "四肢枯瘦，弹跳能力极强的变异体，小心它的迅猛攻势。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 10521,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 10521,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_10620",
   "item_id": 10620,
   "name": "蛇鹰变异体",
   "kind": "图鉴",
   "desc": "拥有鹰身蛇尾的特殊变异体，是占领天空的强大生物。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 10620,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 10620,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_10713",
   "item_id": 10713,
   "name": "角鳄变异体",
   "kind": "图鉴",
   "desc": "吸收火山能源而巨大化的角鳄变异体，拥有撼动山岭的强大力量。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 10713,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 10713,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_11138",
   "item_id": 11138,
   "name": "胡桃夹子木偶",
   "kind": "图鉴",
   "desc": "旧世界大受青睐的玩偶系列，具有悠久的历史。#r在同名舞剧的塑造下，胡桃夹子成为了勇气的象征，是赠送给孩子们的礼物佳品。#r本系列玩偶在旧世界发售时，曾与其它商品捆绑销售，#r为了凑齐整套胡桃夹子，需要费上一番力气。#r字面意思：真的能够夹核桃。#r全套一共12个，据说集齐之后能够带来好运。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 11138,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 11138,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_11171",
   "item_id": 11171,
   "name": "蓝飞鱼",
   "kind": "图鉴",
   "desc": "生活在海中的飞鱼，身体呈湛蓝色，为了逃避天敌的追捕可以跃出水面滑翔。烹饪后肉质紧实，口感极佳。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 11171,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 11171,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_11249",
   "item_id": 11249,
   "name": "胡桃夹子木偶",
   "kind": "图鉴",
   "desc": "旧世界大受青睐的玩偶系列，具有悠久的历史。#r在同名舞剧的塑造下，胡桃夹子成为了勇气的象征，是赠送给孩子们的礼物佳品。#r本系列玩偶在旧世界发售时，曾与其它商品捆绑销售，#r为了凑齐整套胡桃夹子，需要费上一番力气。#r字面意思：真的能够夹核桃。#r全套一共12个，据说集齐之后能够带来好运。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 11249,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 11249,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_11282",
   "item_id": 11282,
   "name": "花英斑",
   "kind": "图鉴",
   "desc": "又称花点石斑鱼，因身上有豹纹状的斑点而得名，肉质鲜美。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 11282,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 11282,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_12033",
   "item_id": 12033,
   "name": "鸡鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 12033,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 12033,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_12260",
   "item_id": 12260,
   "name": "瓶中船",
   "kind": "图鉴",
   "desc": "克里斯托弗赠与你的骑士纪念物。船扬起帆，驶入风暴，正如骑士走上不会回头的英雄之路。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 12260,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 12260,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_12691",
   "item_id": 12691,
   "name": "髓心体感染者",
   "kind": "图鉴",
   "desc": "手臂粗壮得令人惊叹的髓心体感染者，会跳向幸存者残忍地砸捶地面，与周围不断苏醒的感染者们解决任何轻视他的幸存者！",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 12691,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 12691,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_13119",
   "item_id": 13119,
   "name": "巨墙",
   "kind": "图鉴",
   "desc": "强壮的感染者，鲁莽地向前奔跑撞倒一切敌人，千万要小心被它撞倒抓住！",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 13119,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 13119,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_13441",
   "item_id": 13441,
   "name": "再生者狙击兵",
   "kind": "图鉴",
   "desc": "冷静而沉着的再生者狙击手，精准的狙击带来的伤害是危险的。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 13441,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 13441,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_13495",
   "item_id": 13495,
   "name": "帝国士兵",
   "kind": "图鉴",
   "desc": "手持突击步枪的帝国士兵，除了使用步枪射击外还会使用手雷、震爆弹进行辅助攻击；会追击出现在巡逻范围内的一切敌人。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 13495,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 13495,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_13571",
   "item_id": 13571,
   "name": "再生者机械师",
   "kind": "图鉴",
   "desc": "全副武装的再生者男性战士，熟练地使用各种机械武器。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 13571,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 13571,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_13753",
   "item_id": 13753,
   "name": "毕弗隆斯",
   "kind": "图鉴",
   "desc": "被修道院的神父抚养长大的孩子，因为母亲曾被感染影响，而在体内种下了感染的种子。毕弗隆斯食量惊人，随着年纪增长，逐渐膨胀成恐怖的怪物。据传言说，他就是那个导致修道院覆灭的祸因……",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 13753,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 13753,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_13814",
   "item_id": 13814,
   "name": "序列体-破坏者201",
   "kind": "图鉴",
   "desc": "海姆达尔的实验品，于暮雪孤峰中出现。会使用极低温度的炮弹将敌人冰冻。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 13814,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 13814,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_13892",
   "item_id": 13892,
   "name": "超维感染体",
   "kind": "图鉴",
   "desc": "质量危机中出现的超维感染体，拥有改变引力的能力！",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 13892,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 13892,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_13960",
   "item_id": 13960,
   "name": "巨型感染体",
   "kind": "图鉴",
   "desc": "绝境防线中出现的巨大感染体，注意它手中的大锤！",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 13960,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 13960,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_14020",
   "item_id": 14020,
   "name": "特殊感染体",
   "kind": "图鉴",
   "desc": "体型瘦小，动作灵巧敏捷，可以潜入沙土中攻击猎物，遇到敌人后会呼唤同伴。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 14020,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 14020,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_14171",
   "item_id": 14171,
   "name": "巨鳄感染体",
   "kind": "图鉴",
   "desc": "原生活在戈壁的绿洲中，后经特殊污染变得更加危险，经常出没在联盟行动的荒寂戈壁中。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 14171,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 14171,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_14223",
   "item_id": 14223,
   "name": "遗弃电厂电磁王",
   "kind": "图鉴",
   "desc": "在遗弃电厂中意外发现的特殊感染体，由于长期处于电厂中掌握了利用电磁能量进行战斗的方法，释放的电磁脉冲不但会对幸存者造成高额伤害，还会因电击而造成麻痹效果。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 14223,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 14223,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_14273",
   "item_id": 14273,
   "name": "利维坦",
   "kind": "图鉴",
   "desc": "科技会的最强武器，却因为程序错误叛逃到了多贝雪山；会召唤无人机对幸存者进行扫射和轰炸。#r叛逃的原因究竟何在？#r它在多贝雪山又在寻找什么？",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 14273,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 14273,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_14390",
   "item_id": 14390,
   "name": "热带鳄",
   "kind": "图鉴",
   "desc": "咸水鳄是世界上最危险的巨鳄，没有之一；要当心那些海岛上的巨鳄，它们的肌肉更健壮，牙齿更锋利，幸存者最好不要去招惹它们。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 14390,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 14390,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_14444",
   "item_id": 14444,
   "name": "帝国喷火兵",
   "kind": "图鉴",
   "desc": "手持喷火器的帝国士兵，使用喷火器对敌人进行灼烧攻击。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 14444,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 14444,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_14650",
   "item_id": 14650,
   "name": "医生",
   "kind": "图鉴",
   "desc": "断裂的吊扇，缠上锁链，拖曳在地上发出“哐当哐当”的可怕声音，有人说那是曾经的院长污染了，也有人说他听到的是—— 一个幸存者无助向外发出求救信号…… #r你，该相信谁呢？",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 14650,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 14650,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_15062",
   "item_id": 15062,
   "name": "帝国狙击手",
   "kind": "图鉴",
   "desc": "手持狙击步枪的帝国士兵，通常站在制高点进行观察监视，通过精准的射击对侵入者造成猛烈一击。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 15062,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 15062,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_15476",
   "item_id": 15476,
   "name": "莲株闪跃",
   "kind": "图鉴",
   "desc": "点击按钮在脚下放置一朵再生莲花，随后几秒内可以进行自由移动，可以再次点击按钮回到花朵旁。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 15476,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 15476,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_15521",
   "item_id": 15521,
   "name": "米哈伊尔",
   "kind": "图鉴",
   "desc": "帝国士兵中一支特殊势力的领导者，总是试图阻挠幸存者们执行任务。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 15521,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 15521,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_16032",
   "item_id": 16032,
   "name": "序列体-捕猎者201",
   "kind": "图鉴",
   "desc": "海姆达尔新型污染小队的高级成员，会使用瞬移和电击控制敌人。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 16032,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 16032,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_16146",
   "item_id": 16146,
   "name": "巨蝎",
   "kind": "图鉴",
   "desc": "由沙漠中的蝎子被污染而成的巨型特殊感染体，受到猛烈伤害时会逃窜到地下进行躲避。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 16146,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 16146,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_16320",
   "item_id": 16320,
   "name": "佣兵打手",
   "kind": "图鉴",
   "desc": "手持电击棍的佣兵，迅速的三连击能够电击麻痹幸存者，使幸存者失去抵抗能力。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 16320,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 16320,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_16470",
   "item_id": 16470,
   "name": "奥兹",
   "kind": "图鉴",
   "desc": "奥兹原本是亚瑟搜救小队的一员。在一次救援任务中奥兹所乘的飞机在莱文市坠落并被感染者埋伏袭击。目睹一切的奥兹精神受到重创。逃至莱文市监狱后，奥兹通过武力和威信统治了残存的逃犯，并领导这些监狱狂徒在莱文市捕猎感染者。#r“人类只有重新站在食物链顶端，才能夺回家园！”#r关于这点，奥兹深信不疑。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 16470,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 16470,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_16525",
   "item_id": 16525,
   "name": "髓心体感染者",
   "kind": "图鉴",
   "desc": "头上戴着红色的头盔面罩，手持钢棒的髓心体感染者，会发出巨大的嘶吼声，用手中的钢棒将幸存者打飞，污染成能使周围怪物苏醒的髓心体之后好像步伐都格外矫健了…",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 16525,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 16525,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_16764",
   "item_id": 16764,
   "name": "绿衫感染者",
   "kind": "图鉴",
   "desc": "身着绿色衬衫的感染者，会用锋利的爪子进行攻击。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 16764,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 16764,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_16948",
   "item_id": 16948,
   "name": "厨师",
   "kind": "图鉴",
   "desc": "手握利刃，溃烂的肥胖躯体中散发中危险的气息；遭受攻击时会呼唤出不计其数的感染者对幸存者进行围剿。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 16948,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 16948,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_17057",
   "item_id": 17057,
   "name": "深海领主",
   "kind": "图鉴",
   "desc": "深海中变异的章鱼，捕猎时会用触手捆住目标，是深海中当之无愧的霸主。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 17057,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 17057,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_17151",
   "item_id": 17151,
   "name": "鲑鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 17151,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 17151,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_17292",
   "item_id": 17292,
   "name": "季米特卡",
   "kind": "图鉴",
   "desc": "暮雪孤峰中坚决守护队友绝不退让的骄傲者。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 17292,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 17292,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_17535",
   "item_id": 17535,
   "name": "哀嚎感染者",
   "kind": "图鉴",
   "desc": "发出哀嚎的女性感染者，会利用手掌喷出污染气体进行攻击。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 17535,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 17535,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_17712",
   "item_id": 17712,
   "name": "溃灭感染者",
   "kind": "图鉴",
   "desc": "手中拿着旧日的镰刀，拥有者惊人的破坏力，刀中劈出的结晶可以对目标造成巨量伤害。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 17712,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 17712,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_17774",
   "item_id": 17774,
   "name": "鹦嘴鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 17774,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 17774,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_17870",
   "item_id": 17870,
   "name": "繁殖蛾",
   "kind": "图鉴",
   "desc": "绝境防线中出现的新型污染飞蛾，优雅而危险！",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 17870,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 17870,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_18129",
   "item_id": 18129,
   "name": "药剂师",
   "kind": "图鉴",
   "desc": "会熟练地使用各种药剂、污染液体进行战斗。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 18129,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 18129,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_18199",
   "item_id": 18199,
   "name": "再生者步枪兵",
   "kind": "图鉴",
   "desc": "再生者一族中的男性展示，手持着突击步枪，具有很强的远程攻击能力。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 18199,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 18199,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_18454",
   "item_id": 18454,
   "name": "变异珊瑚虫-鹿角珊瑚",
   "kind": "图鉴",
   "desc": "变异珊瑚虫的一个分支，擅长用粗壮的触手拍打猎物。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 18454,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 18454,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_18506",
   "item_id": 18506,
   "name": "经理",
   "kind": "图鉴",
   "desc": "盘踞在酒店的顶楼，释放出危险的雾气，袭击着每一个来酒店探求真相的幸存者。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 18506,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 18506,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_18657",
   "item_id": 18657,
   "name": "变异珊瑚虫-泡泡珊瑚",
   "kind": "图鉴",
   "desc": "变异珊瑚虫的一个分支，擅长从孔洞中喷射出泡泡困住猎物。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 18657,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 18657,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_19144",
   "item_id": 19144,
   "name": "霍华德",
   "kind": "图鉴",
   "desc": "暮雪孤峰中，冰冷噩梦深处巨大的白色身影。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 19144,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 19144,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_19207",
   "item_id": 19207,
   "name": "勾尾感染体",
   "kind": "图鉴",
   "desc": "质量危机中出现的新型感染体",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 19207,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 19207,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_19277",
   "item_id": 19277,
   "name": "蛮力连击",
   "kind": "图鉴",
   "desc": "积蓄力量使用手中的武器打击敌人",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 19277,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 19277,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_19495",
   "item_id": 19495,
   "name": "荒凉沙漠巨锤",
   "kind": "图鉴",
   "desc": "在荒凉沙漠中意外发现的特殊感染体，受感染物影响污染程度更加严重，也比巨锤更加强大。挥舞着巨大的铁锤，能够呼唤出成群的乌鸦和再生感染体，具有极高的危险性。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 19495,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 19495,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_19717",
   "item_id": 19717,
   "name": "意识-不完全体",
   "kind": "图鉴",
   "desc": "从意识-母体的身体中迸发出来的不完全感染体，对幸存者发起撕咬攻击#r会缓慢地向母体靠近，被母体吸收以后恢复母体的大量生命。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 19717,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 19717,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_19816",
   "item_id": 19816,
   "name": "变异珊瑚虫-招潮珊瑚",
   "kind": "图鉴",
   "desc": "变异珊瑚虫的一个分支，擅长召唤海浪协助捕捉猎物。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 19816,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 19816,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_19868",
   "item_id": 19868,
   "name": "《小猫瑞文历险记》",
   "kind": "图鉴",
   "desc": "《小猫瑞文历险记》是旧世界著名奇幻小说，与罗森波顿系列齐名，并称为奇幻小说双璧。#r此书为该系列的第十部《海洋之歌》：#r回到藏身之处的劳尔紧紧地抱住瑞文，思索着如何逃脱这个诡异之地。#r然而茫茫海上，如何逃离。#r正在劳尔焦虑地陷入苦恼之时#r——突然，响起一阵敲门声。#r“是我。”#r埃莱沙叩响了劳尔的舱门。#r劳尔战战兢兢地打开老旧的木板门，没有阻止对方的能力，他别无选择。#r埃莱沙不再使用那黑色的布条遮住自己异于常人的亮金色的双瞳。#r跟在她身后的众人，既有士兵也有梅丽尔病院的病人乘客们。#r尽管长相各异，但此刻，他们的脸上都沉默地挂着笑容，胸口处长出了珊瑚状的花朵，#r仿佛已经带上了独属于海洋的印记。#r见到劳尔开门的那一刻，众人齐齐张口，毛骨悚然地开始哼起了歌谣。#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 19868,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 19868,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_19903",
   "item_id": 19903,
   "name": "深海鳌虾",
   "kind": "图鉴",
   "desc": "生活在深海中的鳌虾，喜阴怕光，生存和繁殖能力很强，肉质鲜甜。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 19903,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 19903,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_19984",
   "item_id": 19984,
   "name": "吐丝感染者",
   "kind": "图鉴",
   "desc": "又是一种危险的感染者，从大大的嘴巴中吐出丝缠绕幸存者，让他们无法反抗。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 19984,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 19984,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_20092",
   "item_id": 20092,
   "name": "双枪教徒",
   "kind": "图鉴",
   "desc": "双手持有手枪的教徒，使用双枪点射对敌人进行攻击。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 20092,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 20092,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_20258",
   "item_id": 20258,
   "name": "野猪",
   "kind": "图鉴",
   "desc": "具有强大生存能力和适应能力的野猪，锋利的獠牙显示出了它的危险性，壮实的身躯冲起来会将幸存者撞翻在地。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 20258,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 20258,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_20312",
   "item_id": 20312,
   "name": "污染猎蝠",
   "kind": "图鉴",
   "desc": "质量危机中出现的新型感染体",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 20312,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 20312,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_20479",
   "item_id": 20479,
   "name": "灰兔",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 20479,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 20479,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_20531",
   "item_id": 20531,
   "name": "被污染章鱼",
   "kind": "图鉴",
   "desc": "污染战争前，为了研究不同生物对污染物的适应性，研究员在海底以八爪鱼进行活体实验。污染灾难来临之际，研究员在培养皿中投入镇静剂，使感染体从此陷入沉睡中，直到新的不速之客闯入将它唤醒。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 20531,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 20531,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_20692",
   "item_id": 20692,
   "name": "变异珊瑚虫-尖刺珊瑚",
   "kind": "图鉴",
   "desc": "变异珊瑚虫的一个分支，擅长用尖刺触手穿刺猎物。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 20692,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 20692,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_20744",
   "item_id": 20744,
   "name": "白兔",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 20744,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 20744,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_20798",
   "item_id": 20798,
   "name": "被污染奥兹",
   "kind": "图鉴",
   "desc": "逃至莱文市监狱后，奥兹通过武力和威信统治了残存的逃犯，并领导这些监狱狂徒在莱文市捕猎感染者。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 20798,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 20798,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_20998",
   "item_id": 20998,
   "name": "分裂感染者",
   "kind": "图鉴",
   "desc": "分裂感染者，被击倒时可能会发生自爆并腐化出蜘蛛，曾在辐射诡楼中出现。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 20998,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 20998,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_21104",
   "item_id": 21104,
   "name": "暴鸣感染体",
   "kind": "图鉴",
   "desc": "谜境诡林破败基地中日积月累形成的蜂巢守护者。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 21104,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 21104,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_21162",
   "item_id": 21162,
   "name": "奥兹帮步枪女兵",
   "kind": "图鉴",
   "desc": "奥兹帮的成员都是一堆从监狱里逃出来的逃犯，或者说，疯子。他们狂热地围绕在奥兹周围，听从奥兹的一切指挥；从某种意义上说，他们比感染者更加危险。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 21162,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 21162,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_21225",
   "item_id": 21225,
   "name": "沼泽水熊虫",
   "kind": "图鉴",
   "desc": "质量危机中出现的新型感染体",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 21225,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 21225,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_21536",
   "item_id": 21536,
   "name": "匿形感染者",
   "kind": "图鉴",
   "desc": "被蓝潮侵蚀而失去理智的村民，能够隐匿身形，请和它保持距离！",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 21536,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 21536,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_21706",
   "item_id": 21706,
   "name": "隐者",
   "kind": "图鉴",
   "desc": "白衬衫红领带的感染者，是具备隐身能力的特殊感染者。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 21706,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 21706,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_21848",
   "item_id": 21848,
   "name": "母体幼体",
   "kind": "图鉴",
   "desc": "星火塔阿尔法泄漏事故中，意外孕育出的母体幼体。没人能解释它如何诞生。它蜷伏于地底深处，持续释放着共鸣，试图侵蚀一切靠近者的意识。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 21848,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 21848,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_22047",
   "item_id": 22047,
   "name": "序列体-破坏者203",
   "kind": "图鉴",
   "desc": "海姆达尔的实验品，于暮雪孤峰中出现。会利用危险的暴风雪，与环境一起战斗。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 22047,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 22047,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_22170",
   "item_id": 22170,
   "name": "帝国重甲兵",
   "kind": "图鉴",
   "desc": "身披重甲的帝国士兵，使用重机枪或者榴弹炮，会连续地掷出三枚手雷进行攻击。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 22170,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 22170,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_22278",
   "item_id": 22278,
   "name": "《小猫瑞文历险记》",
   "kind": "图鉴",
   "desc": "《小猫瑞文历险记》是旧世界著名奇幻小说，与罗森波顿系列齐名，并称为奇幻小说双璧。#r此书为该系列的第三部《白色乘客》：#r被强行捉上军船的劳尔，开始了艰苦的劳役之路。#r清洗甲板、准备伙食、收拾船舱等等，这些杂活全都需要劳尔去做。#r除了那些行为粗鲁的匪兵之外，劳尔发现船上还有一些奇怪的乘客。#r这些穿着白色病号服的古怪乘客，不仅不需要干活，甚至还拥有相当程度的行动自由。#r就在劳尔满头大汗地洗刷甲板时，这些穿着白色病号服的乘客正一言不发地站在上面晒太阳。#r劳尔试图与其中的几位攀谈，却没有任何回应。#r白色的海鸥绕着船只静静地环行，四下阒然，唯有海浪拍打着船舷，发出单调的响声。#r孤独的劳尔悻悻地回到自己破旧的船舱，推开木门就看到枕头上团成一团的小猫，旁边还有一罐带有牙印的罐头。#r原来是瑞文特意从厨房偷来给劳尔加餐的罐头。#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 22278,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 22278,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_22313",
   "item_id": 22313,
   "name": "海鲈鱼",
   "kind": "图鉴",
   "desc": "生活在海里的鲈鱼，相比于淡水鲈鱼体形更大，蛋白质丰富，肉质鲜美。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 22313,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 22313,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_22393",
   "item_id": 22393,
   "name": "突变暴君",
   "kind": "图鉴",
   "desc": "使用进化后的丧尸病毒源株寄生改造的强力实验体，具有极强的破坏力和突变性。体内的寄生毒株可以同化其他的感染者或者幸存者。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 22393,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 22393,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_22446",
   "item_id": 22446,
   "name": "红罗非鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 22446,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 22446,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_22654",
   "item_id": 22654,
   "name": "芒刺巨臂体",
   "kind": "图鉴",
   "desc": "体型庞大的人形变异体，身披冰雪，背后的芒刺令人望而生畏。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 22654,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 22654,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_22754",
   "item_id": 22754,
   "name": "格拉西姆",
   "kind": "图鉴",
   "desc": "暮雪孤峰中被友人簇拥着的孤独的人偶师。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 22754,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 22754,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_22896",
   "item_id": 22896,
   "name": "巨狼斯库尔",
   "kind": "图鉴",
   "desc": "曾是灰犀·隆基努斯的坐骑，独自在再生冢等待着失踪的隆基努斯的归来。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 22896,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 22896,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_23055",
   "item_id": 23055,
   "name": "芒刺巨型体",
   "kind": "图鉴",
   "desc": "右臂被坚冰覆盖，腹部鼓胀，噩梦般的外形使人一见之下便会产生无数有关危险的联想。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 23055,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 23055,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_23148",
   "item_id": 23148,
   "name": "灰犀·隆基努斯",
   "kind": "图鉴",
   "desc": "曾是破晓的一员，却不知为何销声匿迹，直到在危难雪峰山巅殿堂中被海姆达尔发现并改造。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 23148,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 23148,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_23240",
   "item_id": 23240,
   "name": "高原牛",
   "kind": "图鉴",
   "desc": "高原牛是高原上的瑰宝，是非常优质的肉类来源；高原牛还拥有健壮的身躯，锋利的牛角，小心被高原牛顶飞哦。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 23240,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 23240,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_23401",
   "item_id": 23401,
   "name": "花粉吞噬者",
   "kind": "图鉴",
   "desc": "受到莱文市花粉影响而不断变强的感染体",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 23401,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 23401,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_23544",
   "item_id": 23544,
   "name": "序列体-扩散者101",
   "kind": "图鉴",
   "desc": "海姆达尔新型污染小队成员，有扩散花粉的能力。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 23544,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 23544,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_23643",
   "item_id": 23643,
   "name": "沙蜥变异体",
   "kind": "图鉴",
   "desc": "由沙漠中的蜥蜴变异而来，擅长潜伏在地下对猎物发动攻击。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 23643,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 23643,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_23823",
   "item_id": 23823,
   "name": "蛇妖",
   "kind": "图鉴",
   "desc": "残忍的女性感染者，既可以远程地攻击幸存者，也可以对范围内的所有感染者进行攻击。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 23823,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 23823,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_23956",
   "item_id": 23956,
   "name": "残瞳射手",
   "kind": "图鉴",
   "desc": "探险队内的神枪狙击手，为掩护团队撤退而感染牺牲。虽然双目受损，但狙击手的敏锐却让她仅凭本能就能锁定猎物。更可怕的是，还有一头感染的狼王跟随着她，成为她的眼睛和利爪。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 23956,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 23956,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_24138",
   "item_id": 24138,
   "name": "巨臂感染者",
   "kind": "图鉴",
   "desc": "手臂粗壮得令人惊叹的感染者，看起来估计是强壮感染者的加强版；会跳向幸存者残忍地砸捶地面，用强壮的手臂处决任何一个轻视他的幸存者。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 24138,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 24138,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_24280",
   "item_id": 24280,
   "name": "序列体-扩散者201",
   "kind": "图鉴",
   "desc": "海姆达尔新型污染小队的高级成员，有扩散花粉的能力。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 24280,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 24280,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_24398",
   "item_id": 24398,
   "name": "蛇后",
   "kind": "图鉴",
   "desc": "恐怖的女性感染者，发出令人恐惧的刺耳尖叫，幸存者可能会因此而眩晕昏阙。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 24398,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 24398,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_24576",
   "item_id": 24576,
   "name": "幻瞳夜蛾",
   "kind": "图鉴",
   "desc": "基于巨型飞蛾种基因改造的实验体，翅膀上诞生出神秘恐怖的巨大眼状图案，同时携带巨量的致命鳞粉，宛如优雅冷酷的杀手。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 24576,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 24576,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_24751",
   "item_id": 24751,
   "name": "泥浆",
   "kind": "图鉴",
   "desc": "荒无人烟的沼泽地里，潜伏着潮湿可怖的淤泥感染体。它拥有着在沼泽下面潜行的能力，还可以利用沼泽形成漩涡来束缚敌人，甚至会治愈自身生命，可以说是废土最不想碰到的噩梦之一。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 24751,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 24751,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_24883",
   "item_id": 24883,
   "name": "锯齿鲨",
   "kind": "图鉴",
   "desc": "体型巨大的鲨鱼变异体，掀动尾鳍便可引发小型海啸。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 24883,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 24883,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_25090",
   "item_id": 25090,
   "name": "序列体-捕猎者101",
   "kind": "图鉴",
   "desc": "海姆达尔新型污染小队成员，会使用瞬移和电击控制敌人。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 25090,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 25090,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_25212",
   "item_id": 25212,
   "name": "母体-意识",
   "kind": "图鉴",
   "desc": "从远古时代蛰伏至今的污染母体，依然残留在拉扎罗夫的意识之中盘踞为巢，散发着野蛮而原始的气息。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 25212,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 25212,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_25563",
   "item_id": 25563,
   "name": "龙虾王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 25563,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 25563,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_25707",
   "item_id": 25707,
   "name": "狂怒",
   "kind": "图鉴",
   "desc": "腰间的红色腰带是它最显著的特征，迅速的三连环攻击会大幅度地降低幸存者的健康值。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 25707,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 25707,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_25859",
   "item_id": 25859,
   "name": "雪猿凯撒",
   "kind": "图鉴",
   "desc": "感染爆发前莱文市动物园的明星猩猩“凯撒”，智商极高。后被超低温实验改造为白色巨猿，周身温度极低，甚至能轻易冻结空气。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 25859,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 25859,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_26090",
   "item_id": 26090,
   "name": "髓心体感染者",
   "kind": "图鉴",
   "desc": "拥有粗壮手臂的强壮髓心体感染者，可以将幸存者高高举起再狠狠地摔到地上；但是在被抓起前的瞬间可以通过蹲下进行躲避！同时注意受他影响苏醒的其他感染者！",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 26090,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 26090,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_26182",
   "item_id": 26182,
   "name": "潮须感染者",
   "kind": "图鉴",
   "desc": "身体附着茂密毛发，躲藏在蓝潮当中偷袭路过的生物。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 26182,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 26182,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_26300",
   "item_id": 26300,
   "name": "污染鲨鱼",
   "kind": "图鉴",
   "desc": "由于感染物泄露而被严重污染的鲨鱼，受到感染物的影响会从口中喷出污染液体攻击轮船上的幸存者，甚至会高高跃起将幸存者扑至水中。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 26300,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 26300,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_26541",
   "item_id": 26541,
   "name": "黑衣感染者",
   "kind": "图鉴",
   "desc": "身着黑色外套的感染者，会用锋利的爪子紧紧扼住幸存者，如果不能及时挣脱的话会受到严重伤害！",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 26541,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 26541,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_26816",
   "item_id": 26816,
   "name": "魅影感染者",
   "kind": "图鉴",
   "desc": "蓝潮附着神秘面具而生的感染体，通过蓝潮移动并用触手进行致命攻击。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 26816,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 26816,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_26876",
   "item_id": 26876,
   "name": "黄衫污染士兵",
   "kind": "图鉴",
   "desc": "被污染的帝国士兵，似乎还看得出它内心的痛苦和挣扎；但是要小心它引爆手榴弹的自爆袭击。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 26876,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 26876,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_26980",
   "item_id": 26980,
   "name": "巨型傀儡",
   "kind": "图鉴",
   "desc": "花狸制作的巨型傀儡，高逾20米，利用水压与电作战。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 26980,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 26980,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_27327",
   "item_id": 27327,
   "name": "重机枪精英",
   "kind": "图鉴",
   "desc": "具有健硕的肌肉和粗壮的手臂，手中的重机枪说明了他的危险性。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 27327,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 27327,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_27447",
   "item_id": 27447,
   "name": "帝国突击兵",
   "kind": "图鉴",
   "desc": "手持突击步枪的帝国士兵，除了使用步枪射击外还会使用手雷、震爆弹进行辅助攻击；会追击出现在巡逻范围内的一切敌人。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 27447,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 27447,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_27663",
   "item_id": 27663,
   "name": "黑衣污染士兵",
   "kind": "图鉴",
   "desc": "被污染的帝国士兵，似乎还看得出它内心的痛苦和挣扎。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 27663,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 27663,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_27764",
   "item_id": 27764,
   "name": "污沼感染体",
   "kind": "图鉴",
   "desc": "谜境诡林中从实验室里逃进森林的变异体，携带的孢子污染了整个河道。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 27764,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 27764,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_27828",
   "item_id": 27828,
   "name": "吐雾感染者",
   "kind": "图鉴",
   "desc": "吐出猩红色的浓烈污染气体；喷吐的污染气体会使幸存者和其他感染者进入亢奋状态。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 27828,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 27828,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_28006",
   "item_id": 28006,
   "name": "盾牌佣兵",
   "kind": "图鉴",
   "desc": "右手电击棍，左手持盾牌的装甲佣兵，盾牌挥击会击倒敌人，持盾冲锋可以把前方的敌人撞飞。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 28006,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 28006,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_28188",
   "item_id": 28188,
   "name": "雷娜莎",
   "kind": "图鉴",
   "desc": "护送小队的成员，因将稳定剂留给其他患者而失控。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 28188,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 28188,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_28312",
   "item_id": 28312,
   "name": "监禁污染大汉",
   "kind": "图鉴",
   "desc": "因为手臂过于巨大，攻击沉重但是比较缓慢。受到攻击时会将手臂当做盾牌，能阻挡绝大部分伤害。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 28312,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 28312,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_28432",
   "item_id": 28432,
   "name": "监禁感染者",
   "kind": "图鉴",
   "desc": "双手依然被捆绑在身后，但仍然会通过喷吐污染液体进行攻击，由于行动不便因此移动比较迟缓。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 28432,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 28432,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_28488",
   "item_id": 28488,
   "name": "序列体-捍卫者101",
   "kind": "图鉴",
   "desc": "海姆达尔新型污染小队成员，动作笨重，会使用吼叫令敌人减速。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 28488,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 28488,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_28556",
   "item_id": 28556,
   "name": "髓心体感染者",
   "kind": "图鉴",
   "desc": "强壮的髓心体感染者，鲁莽地向前奔跑撞倒一切敌人，千万要小心被它撞倒抓住！它会使周围的感染者苏醒将你团团围住！",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 28556,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 28556,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_28651",
   "item_id": 28651,
   "name": "强壮感染者",
   "kind": "图鉴",
   "desc": "拥有粗壮手臂的强壮感染者，可以将幸存者高高举起再狠狠地摔到地上；但是在被抓起前的瞬间可以通过蹲下进行躲避。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 28651,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 28651,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_28797",
   "item_id": 28797,
   "name": "髓心体感染者",
   "kind": "图鉴",
   "desc": "残忍的女性髓心体感染者，既可以远程地攻击幸存者，也可以对范围内的所有感染者进行攻击，还能使身边的怪物们苏醒，现在你发现她和原来哪里不一样了么？",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 28797,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 28797,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_29219",
   "item_id": 29219,
   "name": "髓心体感染者",
   "kind": "图鉴",
   "desc": "恐怖的女性髓心体感染者，发出令人恐惧的刺耳尖叫，幸存者可能会因此而眩晕昏阙，千万不要被她与众不同的外表迷惑！她会使怪物苏醒，让你苦不堪言！",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 29219,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 29219,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_29375",
   "item_id": 29375,
   "name": "体育老师",
   "kind": "图鉴",
   "desc": "壮硕的肱二头肌仍然在显示着他的力量，怒吼的咆哮宣泄着他的不屈和怨恨。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 29375,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 29375,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_29482",
   "item_id": 29482,
   "name": "污染古树",
   "kind": "图鉴",
   "desc": "悬赏狩猎中的危险目标，会对敌人施以沉重的挥击，也可以召唤危险生物协助自己。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 29482,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 29482,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_29698",
   "item_id": 29698,
   "name": "电棍佣兵",
   "kind": "图鉴",
   "desc": "手持电击棍的佣兵，迅速的三连击能够电击麻痹幸存者，使幸存者失去抵抗能力。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 29698,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 29698,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_29922",
   "item_id": 29922,
   "name": "蛛鳌",
   "kind": "图鉴",
   "desc": "是蜘蛛？还是感染者？总而言之是一种让人恐惧的怪物，释放出的蜘蛛丝对幸存者进行缠绕、拉扯，背部的刺对幸存者进行猛烈的攻击。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 29922,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 29922,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_30139",
   "item_id": 30139,
   "name": "悲鸣感染者",
   "kind": "图鉴",
   "desc": "常年徘徊在迷径海域中，利用天然的迷雾试图阻止所有靠近迷径海域的生物。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 30139,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 30139,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_30239",
   "item_id": 30239,
   "name": "特殊感染体",
   "kind": "图鉴",
   "desc": "危海寻晶中出现的特殊感染体，体型巨大，跳跃时会产生巨大的震波。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 30239,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 30239,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_30321",
   "item_id": 30321,
   "name": "红石斑鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 30321,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 30321,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_30463",
   "item_id": 30463,
   "name": "芒刺肿皱体",
   "kind": "图鉴",
   "desc": "头顶附着了坚硬的芒刺，看起来非常笨重的身体却有着不可小觑的攻击能力。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 30463,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 30463,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_30523",
   "item_id": 30523,
   "name": "芒刺污泥种",
   "kind": "图鉴",
   "desc": "污泥变异体的芒刺变种，肢体两端长有坚硬而肥厚的肉质苞片。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 30523,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 30523,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_30589",
   "item_id": 30589,
   "name": "皇冠狗头",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "产出水域",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 30589,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 30589,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_30701",
   "item_id": 30701,
   "name": "芒刺蛛螯体",
   "kind": "图鉴",
   "desc": "背后生成的硬质辅助肢帮助它形成了灵活且多变的攻防态势。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 30701,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 30701,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_30755",
   "item_id": 30755,
   "name": "芒刺雪蝎种",
   "kind": "图鉴",
   "desc": "巨蝎变异体的芒刺变种，双獒被冰雪覆盖，具有极强的攻击性。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 30755,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 30755,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_30815",
   "item_id": 30815,
   "name": "芒刺盘蚣种",
   "kind": "图鉴",
   "desc": "身形狭长的虫类变异体，以坚硬的外壳为武器，毫不费力地在地下穿梭，小心它突如其来的攻击。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 30815,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 30815,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_30875",
   "item_id": 30875,
   "name": "蓝鳃太阳鱼",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "产出水域",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 30875,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 30875,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_30982",
   "item_id": 30982,
   "name": "链刃感染体",
   "kind": "图鉴",
   "desc": "体型巨大的感染体，擅于利用手上的锁链和风扇进行大范围打击",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 30982,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 30982,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_31097",
   "item_id": 31097,
   "name": "紫海刺水母",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "产出水域",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 31097,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 31097,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_31207",
   "item_id": 31207,
   "name": "蓝祭司",
   "kind": "图鉴",
   "desc": "怀着巨大怨念诞生在蓝潮中的怪物，背上的女人总是喃喃低语诉说着什么。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 31207,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 31207,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_31273",
   "item_id": 31273,
   "name": "掘墓人",
   "kind": "图鉴",
   "desc": "散发着无尽恨意的感染体，终日游荡在地宫中，无差别攻击一切闯入者。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 31273,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 31273,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_31400",
   "item_id": 31400,
   "name": "病狼",
   "kind": "图鉴",
   "desc": "被黑影缠绕，让人看不清真身的巨大的狼。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 31400,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 31400,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_31495",
   "item_id": 31495,
   "name": "雷暴上尉",
   "kind": "图鉴",
   "desc": "原ISR特种部队上尉霍克，受迫参与“人体闪电耐受”项目，因无法适应高浓度病毒环境失去控制。枪械与血肉被电流熔铸，沦为实验室的”清道夫”。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 31495,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 31495,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_31549",
   "item_id": 31549,
   "name": "银鲳鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 31549,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 31549,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_31652",
   "item_id": 31652,
   "name": "战争双子",
   "kind": "图鉴",
   "desc": "侦察兵兄弟莱恩与凯恩，因潜入海姆达尔禁区被捕。控制器强行桥接二人神经回路，将二人的战场默契扭曲为杀戮意志。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 31652,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 31652,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_31825",
   "item_id": 31825,
   "name": "剧毒蛛鳌",
   "kind": "图鉴",
   "desc": "狼蛛基因和感染者结合的异常产物，极其疯狂残暴，多名研究人员命丧其手。擅长使用蛛丝捕获猎物，并使用背部巨大的螯爪穿刺攻击。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 31825,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 31825,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_31879",
   "item_id": 31879,
   "name": "大黄鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 31879,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 31879,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_32017",
   "item_id": 32017,
   "name": "守愿骑士",
   "kind": "图鉴",
   "desc": "职业探险队成员，自愿牺牲变为感染者，却再也没有回来。感染后，他收起了笑容，露出严肃的底色，但始终没有忘记自己的誓愿——紧握四把武器，守护团队，守护幸存者。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 32017,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 32017,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_32071",
   "item_id": 32071,
   "name": "成年鹿",
   "kind": "图鉴",
   "desc": "漂亮的成年鹿，曾经濒临灭绝，在污染战争后由于人类范围的缩减又繁育了起来；是非常优质的肉类来源。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 32071,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 32071,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_32147",
   "item_id": 32147,
   "name": "帝国霰弹兵",
   "kind": "图鉴",
   "desc": "手持霰弹枪的帝国士兵，除了使用霰弹枪射击外还会使用烟雾弹进行辅助攻击；会追击出现在巡逻范围内的一切敌人。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 32147,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 32147,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_32249",
   "item_id": 32249,
   "name": "污染龙蜥",
   "kind": "图鉴",
   "desc": "恐怖的龙蜥，巨大的尾巴可以横扫将幸存者击倒，更要当心它带有感染物的唾液。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 32249,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 32249,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_32419",
   "item_id": 32419,
   "name": "感染狼",
   "kind": "图鉴",
   "desc": "污染战争后，曾经濒临灭绝的感染狼如今遍布于世界各地，用它们的尖牙利爪威胁着幸存者的安危",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 32419,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 32419,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_32586",
   "item_id": 32586,
   "name": "帝国重甲兵",
   "kind": "图鉴",
   "desc": "身披重甲的帝国士兵，使用重机枪或者榴弹炮，会连续地掷出三枚手雷进行攻击。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 32586,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 32586,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_32734",
   "item_id": 32734,
   "name": "弓箭教徒",
   "kind": "图鉴",
   "desc": "手持弓箭的教徒，使用弓箭从远处对敌人造成猛烈打击。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 32734,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 32734,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_32812",
   "item_id": 32812,
   "name": "雪山绵羊",
   "kind": "图鉴",
   "desc": "生活在高地雪山上的绵羊，是不错的肉类来源；和营地饲养的绵羊的主要差别是雪山绵羊有角。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 32812,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 32812,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_32980",
   "item_id": 32980,
   "name": "双棍教徒",
   "kind": "图鉴",
   "desc": "双手持钢棍的教徒，使用迅捷无比的三连击对敌人进行击打，双棍突击可以电击麻痹敌人。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 32980,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 32980,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_33185",
   "item_id": 33185,
   "name": "秘鲁神仙",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "产出水域",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 33185,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 33185,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_33297",
   "item_id": 33297,
   "name": "沙漠狼",
   "kind": "图鉴",
   "desc": "栖息在沙漠戈壁之中的沙漠狼，竖立的大耳朵是它最显著的特征。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 33297,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 33297,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_33459",
   "item_id": 33459,
   "name": "重甲佣兵",
   "kind": "图鉴",
   "desc": "身披重甲的佣兵，使用重机枪或者榴弹炮，是比较危险的敌人。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 33459,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 33459,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_33597",
   "item_id": 33597,
   "name": "三间火箭",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "产出水域",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 33597,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 33597,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_33697",
   "item_id": 33697,
   "name": "荒原羚",
   "kind": "图鉴",
   "desc": "从沙漠到海岛都有分布的荒原羚，长长的犄角是它的标志；和远亲鹿不一样的是，受到惊吓时可能反而会发起攻击。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 33697,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 33697,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_33847",
   "item_id": 33847,
   "name": "佣兵狙击手",
   "kind": "图鉴",
   "desc": "身穿迷彩伪装的佣兵狙击手，使用狙击枪对敌人造成猛烈一击。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 33847,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 33847,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_34017",
   "item_id": 34017,
   "name": "红海黄金蝶",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "产出水域",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 34017,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 34017,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_34123",
   "item_id": 34123,
   "name": "石甲虫",
   "kind": "图鉴",
   "desc": "成群出没的恐怖甲虫，具有强大而有力的颚，极具破坏力；坚硬的外壳可以抵挡一切攻击。但是柔软的腹部是其最大的弱点，惧怕火焰，在火焰中会暴露出脆弱的腹部。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 34123,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 34123,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_34286",
   "item_id": 34286,
   "name": "突击佣兵",
   "kind": "图鉴",
   "desc": "手持突击步枪，头戴钢盔的佣兵，守卫巡逻着佣兵驻地，把一切入侵的敌人打成筛子。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 34286,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 34286,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_34530",
   "item_id": 34530,
   "name": "血红龙",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "产出水域",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 34530,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 34530,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_34647",
   "item_id": 34647,
   "name": "噬甲虫",
   "kind": "图鉴",
   "desc": "相较于近亲石甲虫而言比较稀少的噬甲虫，但危险程度有过之而无不及；噬甲虫会攻击幸存者的脸部使幸存者无法动弹，只有依靠队友的帮助才能脱困。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 34647,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 34647,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_34823",
   "item_id": 34823,
   "name": "霰弹佣兵",
   "kind": "图鉴",
   "desc": "头戴钢盔的佣兵，使用的武器是霰弹枪，开火速度比较慢。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 34823,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 34823,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_35185",
   "item_id": 35185,
   "name": "红剑",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "产出水域",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 35185,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 35185,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_35296",
   "item_id": 35296,
   "name": "灰鹫",
   "kind": "图鉴",
   "desc": "灰鹫对于求生的幸存者而言绝对是挥之不去的噩梦，它让你想到腐臭的荒野和绝望的气息；你绝对不想面对成群的灰鹫，如果非得要面对，请确认你的队友就在你的身边。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 35296,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 35296,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_35452",
   "item_id": 35452,
   "name": "幼鹿",
   "kind": "图鉴",
   "desc": "可爱的小鹿，蹦蹦跳跳天真无邪的样子让人回想起污染战争前的生活。啊！多美好啊！",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 35452,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 35452,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_35593",
   "item_id": 35593,
   "name": "幼年高原牛",
   "kind": "图鉴",
   "desc": "还没有长出锋利牛角的小高原牛，性格胆小只会逃跑，但是它的妈妈可不是好惹的！",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 35593,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 35593,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_36150",
   "item_id": 36150,
   "name": "红腹食人鲳",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "产出水域",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 36150,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 36150,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_36261",
   "item_id": 36261,
   "name": "猪崽子",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 36261,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 36261,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_36300",
   "item_id": 36300,
   "name": "鲥鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 36300,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 36300,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_36455",
   "item_id": 36455,
   "name": "奶牛",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 36455,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 36455,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_36502",
   "item_id": 36502,
   "name": "秋刀鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 36502,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 36502,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_36664",
   "item_id": 36664,
   "name": "绵羊",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 36664,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 36664,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_36769",
   "item_id": 36769,
   "name": "小鸡",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 36769,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 36769,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_36815",
   "item_id": 36815,
   "name": "火鼠鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 36815,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 36815,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_36971",
   "item_id": 36971,
   "name": "草鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 36971,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 36971,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_37068",
   "item_id": 37068,
   "name": "对虾王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 37068,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 37068,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_37106",
   "item_id": 37106,
   "name": "龙利鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 37106,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 37106,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_37273",
   "item_id": 37273,
   "name": "河蟹王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 37273,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 37273,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_37375",
   "item_id": 37375,
   "name": "鲤鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 37375,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 37375,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_37472",
   "item_id": 37472,
   "name": "河豚王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 37472,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 37472,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_37578",
   "item_id": 37578,
   "name": "鲶鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 37578,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 37578,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_37616",
   "item_id": 37616,
   "name": "小丑鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 37616,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 37616,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_37802",
   "item_id": 37802,
   "name": "鳜鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 37802,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 37802,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_37840",
   "item_id": 37840,
   "name": "带鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 37840,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 37840,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_37878",
   "item_id": 37878,
   "name": "帝国军团长",
   "kind": "图鉴",
   "desc": "全副武装，手持巨盾的帝国军团长，持着盾牌冲锋可以击飞幸存者，听他号令的帝国士兵存活时，军团长几乎不可能被击败。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 37878,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 37878,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_37975",
   "item_id": 37975,
   "name": "多宝鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 37975,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 37975,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_38013",
   "item_id": 38013,
   "name": "巨颚",
   "kind": "图鉴",
   "desc": "巨大的异形特殊感染体，拥有四片恐怖的锐利的颚；张开大嘴肆意喷射污染液体，假死时吸收污染幼体进行恢复。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 38013,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 38013,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_38138",
   "item_id": 38138,
   "name": "苏眉鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 38138,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 38138,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_38240",
   "item_id": 38240,
   "name": "蜂鸣",
   "kind": "图鉴",
   "desc": "在无人的天文观测台，还徘徊着另一个强大的感染体。不知道具体经历了什么折磨的事情？才让他丧失语言能力，并和同伴异化出新的交流方式——其他感染者会被它召唤而来。如果你发现它准备趴下，只有一个忠告——快跑！",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 38240,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 38240,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_38352",
   "item_id": 38352,
   "name": "蓝蜘蛛",
   "kind": "图鉴",
   "desc": "阴暗潮湿的洞穴中生长的蓝色蜘蛛，体型较大，会冲向幸存者对幸存者进行撕咬，危险性并不强烈，但谁也不想被蜘蛛咬上几口吧？",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 38352,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 38352,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_38501",
   "item_id": 38501,
   "name": "鱿鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 38501,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 38501,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_38597",
   "item_id": 38597,
   "name": "云斑海猪鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 38597,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 38597,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_38693",
   "item_id": 38693,
   "name": "海鳗王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 38693,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 38693,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_38789",
   "item_id": 38789,
   "name": "甲鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 38789,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 38789,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_38950",
   "item_id": 38950,
   "name": "梭子蟹王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 38950,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 38950,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_39105",
   "item_id": 39105,
   "name": "鲅鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 39105,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 39105,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_39266",
   "item_id": 39266,
   "name": "条纹鲈鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 39266,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 39266,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_39420",
   "item_id": 39420,
   "name": "虹鳟鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 39420,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 39420,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_39458",
   "item_id": 39458,
   "name": "蓝鳃太阳鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 39458,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 39458,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_39613",
   "item_id": 39613,
   "name": "鳙鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 39613,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 39613,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_39778",
   "item_id": 39778,
   "name": "雨鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 39778,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 39778,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_40016",
   "item_id": 40016,
   "name": "冰棘鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 40016,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 40016,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_40220",
   "item_id": 40220,
   "name": "蛇鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 40220,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 40220,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_40259",
   "item_id": 40259,
   "name": "步枪佣兵",
   "kind": "图鉴",
   "desc": "手持突击步枪的佣兵，守卫巡逻着佣兵驻地，把一切入侵的敌人打成筛子。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 40259,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 40259,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_40539",
   "item_id": 40539,
   "name": "红鲷鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 40539,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 40539,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_40695",
   "item_id": 40695,
   "name": "白条鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 40695,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 40695,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_40858",
   "item_id": 40858,
   "name": "金枪鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 40858,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 40858,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_40955",
   "item_id": 40955,
   "name": "魔鬼鱼王",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 40955,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 40955,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_41310",
   "item_id": 41310,
   "name": "镀金的弹壳",
   "kind": "图鉴",
   "desc": "贾斯提斯赠与你的骑士纪念物。弹壳在光下熠熠生辉，而他不再执着于曾经的使命。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 41310,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 41310,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_41598",
   "item_id": 41598,
   "name": "尖刺狂蜂",
   "kind": "图鉴",
   "desc": "谜境诡林中实验失败后失控的蜜蜂们，依然凭借本能在森林中收集孢子。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 41598,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 41598,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_41656",
   "item_id": 41656,
   "name": "再生者女兵",
   "kind": "图鉴",
   "desc": "再生者一族中的女性战士，手中虽然没有武器，但是在近身状态仍然有很强的攻击能力。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 41656,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 41656,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_41712",
   "item_id": 41712,
   "name": "黑匣子",
   "kind": "图鉴",
   "desc": "沉水的黑匣子，年代不详，解析后能得到一些神秘的信息。#r可惜能够捕捉到的电讯号断断续续，准度有限：#r“在海上执行任务这么多年，怪事也见了不少，从未遇见过这样奇怪的护航任务。”#r“嘴巴倒是都挺严的，费了挺大力气才打听到：竟然是护送一个方程式！”#r“神神秘秘的……干脆一个电报发过去不就好了么？”#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 41712,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 41712,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_41745",
   "item_id": 41745,
   "name": "青花鱼",
   "kind": "图鉴",
   "desc": "青花鱼整体呈纺锤形，游泳速度很快。烹饪后肉质紧实有嚼劲。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 41745,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 41745,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_41780",
   "item_id": 41780,
   "name": "再生者盾卫者",
   "kind": "图鉴",
   "desc": "再生者一族中的男性战士，手持着巨型盾牌，强壮而具有威慑力。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 41780,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 41780,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_41929",
   "item_id": 41929,
   "name": "黑匣子",
   "kind": "图鉴",
   "desc": "沉水的黑匣子，年代不详，解析后能得到一些神秘的信息。#r可惜能够捕捉到的电讯号断断续续，准度有限：#r“有必要向各位再次宣读航海守则——”#r“每名船员都必须时刻佩戴着测量装置。”#r“这个金属小盒子，可以探测到结晶的浓度……中间有个玻璃透盖的小孔，一旦里面开始闪烁红色的光芒……”#r“……必须立刻！及时！马上将危机讯号告知给其它同伴以及船只上的观测员！”#r“当浓度超过安全阈值，驾驶舱需立刻调整航向，离开危险海域！”#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 41929,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 41929,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_41962",
   "item_id": 41962,
   "name": "寄居蟹",
   "kind": "图鉴",
   "desc": "寄居蟹常寄居于死亡的软体动物壳中，它的外形介于虾和蟹之间，身体左右不对称，腹部柔软卷曲于壳中。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 41962,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 41962,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_42228",
   "item_id": 42228,
   "name": "多贝雪山",
   "kind": "图鉴",
   "desc": "特产：\n阔树叶,硅晶矿,黄麻杆,兽毛,金刚钻头\n\n动物：\n鹿,野猪,山羊,高原牛\n\n故事：\n在白树高地，我结识了几个帝国士兵。虽然有了交情，但白树高地事件之后，大家还是各忙各的，所以当安德烈联系我，希望我和他们一起前往多贝雪山的时候，我感到十分惊讶。#r跟随他们抵达多贝雪山后，我终于知道了当年发生的一切。#r科技会发现母体有两种不同状态。当它对人体有所影响，就会变得相对稳定，人类的性格也能反过来影响它。性格越稳定，母体的危害越小。当母体不再影响人体，则会变得十分危险，它会释放大量藤蔓一样的物质攻击所有出现在它附近的生物，藤蔓也能将人催眠，这也是让人感到不舒服的一个能力。#r白树高地那些士兵，因为在押送拉扎罗夫的路上长时间受母体影响，无法控制自己前往多贝雪山的冲动。#r因为没有其他控制母体的办法，帝国的士兵们决定牺牲自己，用人海战术来阻止母体的成长，他们认为士兵们的意志比常人更加坚定，即便被母体影响，也可以把危害降到最低。#r科技会为他们提供了相关技术，在他们的努力下，母体没有成长，却也没被彻底解决。#r可惜这一切最终败给了时间，当我们抵达多贝雪山的时候，已经没有人可以挡住母体的脚步了……就连最强大的利维坦战士，也变成了母体用来攻击我们的工具……安德烈、鲍里斯……大家最终都牺牲在了多贝雪山，虽然爆炸埋葬了一切，但我知道母体最终会卷土重来……没有人知道在那雪山深处埋葬了多少人，那些士兵们，曾经给我们所有人一个短暂的喘息时间。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 42228,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 42228,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_42756",
   "item_id": 42756,
   "name": "黑匣子",
   "kind": "图鉴",
   "desc": "沉水的黑匣子，年代不详，解析后能得到一些神秘的信息。#r可惜能够捕捉到的电讯号断断续续，准度有限：#r“这些东西放在船上还真是瘆得慌……”#r“本以为只不过是普通的药玻瓶，没想到里面摇晃的蓝色溶液竟然是用来制造军火的。”#r“提纯了那么多深海章鱼和蜘蛛的腺体……”#r“这么多，万一出个什么意外……”#r“头一次觉得留在船上竟然比深不见底的海洋还危险。”#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 42756,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 42756,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_42789",
   "item_id": 42789,
   "name": "海螺",
   "kind": "图鉴",
   "desc": "海螺主要栖息于浅海，活动较慢，主要以藻类为食。螺肉含有丰富的维生素A、蛋白质、铁和钙等营养元素。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 42789,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 42789,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_42876",
   "item_id": 42876,
   "name": "黑匣子",
   "kind": "图鉴",
   "desc": "沉水的黑匣子，年代不详，解析后能得到一些神秘的信息。#r可惜能够捕捉到的电讯号断断续续，准度有限：#r“船员们开始生病……”#r“排污管线传来奇怪的气泡声，就好像被什么东西堵住了似的；对附近的海水稍微进行了粗糙的采样，什么也没有发现呀！”#r“大家快被这声音搞疯了！船员们开始变得疑神疑鬼……”#r“一定有什么我们还未能发现的物质时刻扰动着海水。”#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 42876,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 42876,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_42909",
   "item_id": 42909,
   "name": "沙丁鱼",
   "kind": "图鉴",
   "desc": "沙丁鱼为群居鱼类，经常会成群行动来避免被捕食。烹饪后肉质鲜嫩，含脂肪高。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 42909,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 42909,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_43727",
   "item_id": 43727,
   "name": "白树高地",
   "kind": "图鉴",
   "desc": "特产：\n亚麻花瓣,兽角,柏树叶,银杏苗,蓝晶石\n\n动物：\n高原羊,高原鹿,高原高原牛,熊\n\n故事：\n为了救出被帝国士兵劫持的联盟成员，我来到了白树高地，可惜帝国军营守卫森严，救人任务困难重重。#r怎么说呢，只要思想不滑坡，办法总比困难多……我急中生智，弄到了一套军服，混入帝国兵团。#r在这里，我认识了安德烈、鲍里斯和维克多这三个士兵。#r安德烈看起来严肃苛刻，实际上人还不错；鲍里斯愣头愣脑，似乎十分贪吃，却有着不为人知的秘密；维克多让我想起大灾难之前的同学和朋友们……#r然而位于白树高地的帝国兵营，此时正经历着物资紧缺和疾病的侵袭。#r我之前并不了解帝国士兵，他们在我眼里是冷酷的敌人、纪律严明的士兵、装备先进的大佬……#r这一次的潜入，却让我看到帝国士兵们不为人知的一面，原来他们也有弱点，也有感情，并不是冷血无情的战争机器。#r在白树高地的兵营里有很多老兵，他们当年负责押送拉扎罗夫前往多贝雪山，这任务具体是什么，我还在调查。#r唯一可以确定的是，这些老兵归来时身心俱疲，很多人都因为这次任务成了残疾，曾经的传奇大兵谢洛科夫就因此失去了手臂。#r说起谢洛科夫，鲍里斯的秘密就和这个人有关。因为军营物资紧缺，谢洛科夫又是个脾气暴躁的患者，鲍里斯经常会去找东西给他作为额外的补给。#r我一开始十分奇怪，为什么鲍里斯对非亲非故的谢洛科夫忙前忙后，后来我才知道，鲍里斯一直把谢洛科夫视为自己的奋斗目标，一位偶像……#r可惜失去双手的谢洛科夫，好像已经完全变成了另外一个人。#r白树高地的老兵们，都被一种奇怪的病所困扰。#r根据我的调查，这疾病和拉扎罗夫密切相关，但和母体又有怎样的关系？我不得而之。#r但若问到当年的事，这些人却又遮遮掩掩，不肯深谈。#r最近一段时间，这些老兵的情况开始恶化，一些人失去了理智，被军营里的其他人解决掉了。#r谢洛科夫也在此时也变得疯狂，虽然在大家的帮助下，最终他醒悟并接受了消亡……#r谢洛科夫给他的战友们留下了线索，多贝雪山那里，似乎情况更糟，我要跟着他们继续前往雪山吗？",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 43727,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 43727,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_44504",
   "item_id": 44504,
   "name": "序列体-捍卫者201",
   "kind": "图鉴",
   "desc": "海姆达尔新型污染小队的高级成员，动作笨重，会使用吼叫令敌人减速。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 44504,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 44504,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_44877",
   "item_id": 44877,
   "name": "异种投手",
   "kind": "图鉴",
   "desc": "绝境防线中出现的新型感染体，会投掷其他的感染者！",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 44877,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 44877,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_45920",
   "item_id": 45920,
   "name": "蓝衫感染者",
   "kind": "图鉴",
   "desc": "身着蓝色衬衫的感染者，会用锋利的爪子紧紧扼住幸存者，如果不能及时挣脱的话会受到严重伤害！",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 45920,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 45920,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_46133",
   "item_id": 46133,
   "name": "污染伐木工头",
   "kind": "图鉴",
   "desc": "高大健壮的感染者，高高跃起的攻击会把幸存者砸飞。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 46133,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 46133,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_46419",
   "item_id": 46419,
   "name": "黄衫感染者",
   "kind": "图鉴",
   "desc": "身着黄色破烂背心的感染者，会用锋利的爪子进行攻击。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 46419,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 46419,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_46690",
   "item_id": 46690,
   "name": "背包感染者",
   "kind": "图鉴",
   "desc": "背着背包的感染者，迅速地跳向目标，一不小心就会被它扑倒。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 46690,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 46690,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_46867",
   "item_id": 46867,
   "name": "女性感染者",
   "kind": "图鉴",
   "desc": "看似柔弱的女性感染者，但是会捡起地上的石头狠狠地砸你的头。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 46867,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 46867,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_47030",
   "item_id": 47030,
   "name": "污染矿工工头",
   "kind": "图鉴",
   "desc": "高大健壮的感染者，高高跃起的攻击会把幸存者砸飞。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 47030,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 47030,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_47212",
   "item_id": 47212,
   "name": "肥胖感染者",
   "kind": "图鉴",
   "desc": "大腹便便的肥胖感染者，喷出体内的污染物攻击幸存者，被击倒时可能会发生自爆。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 47212,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 47212,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_47499",
   "item_id": 47499,
   "name": "憎恶",
   "kind": "图鉴",
   "desc": "由再生感染者吸收寄宿体进化而成的巨型感染者，巨大的吼叫声震耳欲聋，让人头晕目眩；当他用手保护自己的身体时可以规避绝大部分伤害；还要额外小心它的上勾拳把你打飞！",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 47499,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 47499,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_47618",
   "item_id": 47618,
   "name": "吸髓者",
   "kind": "图鉴",
   "desc": "出没在沼泽区域的吸髓者，会跳起攻击幸存者将幸存者扑倒扼住，还会用长长的蓝色的舌头卷住幸存者进行攻击。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 47618,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 47618,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_47775",
   "item_id": 47775,
   "name": "光头感染者",
   "kind": "图鉴",
   "desc": "身上缠着绷带的强壮感染者，手中会喷出污染气体进行攻击，会扑倒幸存者进行撕扯。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 47775,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 47775,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_47940",
   "item_id": 47940,
   "name": "钢盔感染者",
   "kind": "图鉴",
   "desc": "头上戴着红色的头盔面罩，手持钢棒的强壮感染者，会发出巨大的嘶吼，用手中的钢棒将幸存者打飞。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 47940,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 47940,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_48107",
   "item_id": 48107,
   "name": "沼泽污染触手",
   "kind": "图鉴",
   "desc": "藏匿在沼泽之中的污染触手，会对途径沼泽的幸存者发起攻击，将幸存者拖拽到沼泽深渊之中。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 48107,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 48107,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_48321",
   "item_id": 48321,
   "name": "污染老年村民",
   "kind": "图鉴",
   "desc": "手持火把和斧头的污染村民，会通过投掷火把来进行攻击；似乎还残存着某些信仰，会集体围在一起进行膜拜。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 48321,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 48321,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_48460",
   "item_id": 48460,
   "name": "污染青年村民",
   "kind": "图鉴",
   "desc": "手持火把和斧头的污染村民，会通过投掷火把来进行攻击；似乎还残存着某些信仰，会集体围在一起进行膜拜。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 48460,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 48460,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_48599",
   "item_id": 48599,
   "name": "污染护士",
   "kind": "图鉴",
   "desc": "被污染的医院护士，具有令人恐惧的巨大爪子，会用玻璃碎片对幸存者进行攻击。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 48599,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 48599,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_48722",
   "item_id": 48722,
   "name": "污染病人",
   "kind": "图鉴",
   "desc": "被污染的医院病人，会用锋利的爪子进行攻击。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 48722,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 48722,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_48867",
   "item_id": 48867,
   "name": "惊叫感染者",
   "kind": "图鉴",
   "desc": "身穿短裙的女性感染者，她的惊叫和嚎哭会引来附近的其他感染者。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 48867,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 48867,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_49022",
   "item_id": 49022,
   "name": "序列体-暴戾者",
   "kind": "图鉴",
   "desc": "海姆达尔制造的新型序列体感染者，倒地前会迸射出具有腐蚀能力的黏液。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 49022,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 49022,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_54654",
   "item_id": 54654,
   "name": "奥兹帮步枪士兵",
   "kind": "图鉴",
   "desc": "奥兹帮的成员都是一堆从监狱里逃出来的逃犯，或者说，疯子。他们狂热地围绕在奥兹周围，听从奥兹的一切指挥；从某种意义上说，他们比感染者更加危险。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 54654,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 54654,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_54781",
   "item_id": 54781,
   "name": "奥兹帮火炮手",
   "kind": "图鉴",
   "desc": "奥兹帮的成员都是一堆从监狱里逃出来的逃犯，或者说，疯子。他们狂热地围绕在奥兹周围，听从奥兹的一切指挥；从某种意义上说，他们比感染者更加危险。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 54781,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 54781,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_55790",
   "item_id": 55790,
   "name": "黄尾蓝魔",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "产出水域",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 55790,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 55790,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_55963",
   "item_id": 55963,
   "name": "吕宋棘海星",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "产出水域",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 55963,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 55963,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_56396",
   "item_id": 56396,
   "name": "鼹鼠",
   "kind": "图鉴",
   "desc": "受到严重感染而巨大化的鼹鼠感染体，保留了沙漠动物天性里的狡猾。进入畸化态后失去理智，变为一头狂暴的巨兽，用巨大的双爪撕碎一切",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 56396,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 56396,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_56460",
   "item_id": 56460,
   "name": "绿蜘蛛",
   "kind": "图鉴",
   "desc": "阴暗潮湿的洞穴中生长的绿色蜘蛛，能够在远处将污染液体喷射到幸存者身上，绿幽幽的颜色明确地告诉幸存者：我很危险。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 56460,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 56460,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_56649",
   "item_id": 56649,
   "name": "巨汉",
   "kind": "图鉴",
   "desc": "力大无比的巨型特殊感染体，运用自己超凡的力量对幸存者发起重击。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 56649,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 56649,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_56765",
   "item_id": 56765,
   "name": "红蜘蛛",
   "kind": "图鉴",
   "desc": "阴暗潮湿的洞穴中生长的红色蜘蛛，具有比较小的体型，靠近幸存者时会引发剧烈的爆炸，炸开的体液也能让幸存者苦不堪言。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 56765,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 56765,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_56900",
   "item_id": 56900,
   "name": "指挥官",
   "kind": "图鉴",
   "desc": "体型庞大的感染体手里拿着巨大红绿灯，在已经没有任何人类生机的城市十字路口上游荡着……没人知道它是如何迷路到森林里的。但从森林仓惶逃出的幸存者，在最后只带出了一个消息—— 它手中的红绿灯，是他心情的晴雨表。一旦红灯亮起，狂暴的感染体，会让人们觉得仿佛看到地狱的模样……",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 56900,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 56900,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_57042",
   "item_id": 57042,
   "name": "黑蜘蛛",
   "kind": "图鉴",
   "desc": "阴暗潮湿的洞穴中生长的黑色小蜘蛛，具有很强的跳跃能力，能够迅速地扑到幸存者脸上，具有比较高的危险性。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 57042,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 57042,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_57158",
   "item_id": 57158,
   "name": "巨锤",
   "kind": "图鉴",
   "desc": "阴冷压抑的莱文市监狱里冲出来一个体型庞大的特殊感染者，无人知道它是如何来到了野外。被蒙上的头套和手中笨重铁锤的背后，似乎说明在监狱深处还有其他未知的危险秘密……",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 57158,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 57158,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_57374",
   "item_id": 57374,
   "name": "园丁",
   "kind": "图鉴",
   "desc": "据调查先锋队的情报称，莱文市的公园迷宫般的植物园里，经常会传来一阵阵令人毛骨悚然的电锯声……错综复杂的植物迷宫里，使用电锯攻击的园丁一直在徘徊着。更棘手的是，在面对疯狂的电锯攻击时，幸存者们还需要同时应付迷宫内乌鸦的袭击。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 57374,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 57374,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_57618",
   "item_id": 57618,
   "name": "树妖",
   "kind": "图鉴",
   "desc": "树木因为吸食了感染者而污染形成的巨型特殊感染体，感染者的身躯隐藏在树干之中，具有顽强的生命力和强大的攻击性。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 57618,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 57618,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_57786",
   "item_id": 57786,
   "name": "重生",
   "kind": "图鉴",
   "desc": "发出撕心裂肺的嘶吼，尾部的利爪可以将幸存者卷起再狠狠地摔在地上。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 57786,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 57786,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_57928",
   "item_id": 57928,
   "name": "怨念",
   "kind": "图鉴",
   "desc": "痛苦所形成的深深的怨念羁留于心",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 57928,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 57928,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_58016",
   "item_id": 58016,
   "name": "蜘蛛母巢",
   "kind": "图鉴",
   "desc": "阴暗潮湿的洞穴中生长的蜘蛛母巢，静静地趴在岩壁上不会移动，释放出会爆炸的感染物孢子。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 58016,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 58016,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_58138",
   "item_id": 58138,
   "name": "暗种",
   "kind": "图鉴",
   "desc": "顽皮地肆意冲撞，喷洒污染液体，生气时会拍打地面。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 58138,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 58138,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_58284",
   "item_id": 58284,
   "name": "巨甲虫",
   "kind": "图鉴",
   "desc": "由甲虫被污染而成的巨型特殊感染体，全身坚硬无比，但弱点是柔软的腹部；畏怕火焰，持续的火焰灼烧会使它翻身暴露弱点。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 58284,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 58284,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_58432",
   "item_id": 58432,
   "name": "铁胆",
   "kind": "图鉴",
   "desc": "身被重炮，右手金属机械化的高级特殊感染体，世界各地均有目击报道；铁胆的存在对幸存者和营地的安全造成了巨大的威胁。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 58432,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 58432,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_58640",
   "item_id": 58640,
   "name": "鸭子",
   "kind": "图鉴",
   "desc": "",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 58640,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 58640,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_58738",
   "item_id": 58738,
   "name": "乌鸦",
   "kind": "图鉴",
   "desc": "乌鸦是一种聪明的鸟类，旧世界常称它是鸟类中的“智者”；污染战争之后这种精明的鸟类开始攻击幸存者了，这可不是什么好消息。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 58738,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 58738,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_58967",
   "item_id": 58967,
   "name": "幼年荒原羚",
   "kind": "图鉴",
   "desc": "还没有长角的小荒原羚，看起来和鹿差不多，但是没有斑点，不过也是非常的可爱。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 58967,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 58967,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_59075",
   "item_id": 59075,
   "name": "巨鳄",
   "kind": "图鉴",
   "desc": "潜伏的巨鳄是最危险的捕食者之一，拥有坚硬的甲胄，锋利的牙齿，常常栖息在沼泽或河流之中。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 59075,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 59075,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_59193",
   "item_id": 59193,
   "name": "狐狸",
   "kind": "图鉴",
   "desc": "狡黠是狐狸的标签，游荡在红杉镇郊外的草丛树林中，落单的幸存者很有可能会遭受它们的袭击。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 59193,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 59193,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_59318",
   "item_id": 59318,
   "name": "熊",
   "kind": "图鉴",
   "desc": "身型庞大的巨熊，厚实而有力的熊掌能把幸存者拍倒在地；由于巨熊喜欢吃蜂蜜，巨熊出没的区域往往也能找到蜂蜜。",
   "extra_desc": "简介",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 59318,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 59318,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_61376",
   "item_id": 61376,
   "name": "《小猫瑞文历险记》",
   "kind": "图鉴",
   "desc": "《小猫瑞文历险记》是旧世界著名奇幻小说，与罗森波顿系列齐名，并称为奇幻小说双璧。#r此书为该系列的第十二部《风暴终曲》：#r就像是无力挽回自己的主人的厄运一般，小猫瑞文凄厉地大叫一声，却没有回头。#r劳尔抚摸着自己开始结晶的手指，意识到发生了什么。#r他忍住泪水，继续向前跑去，一边对着停在原地的小猫大喊着：#r“跑呀，瑞文！我们可不能在这里就随便放弃！”#r……#r几个月后，《日出报》刊载了这样一则小消息：#r“稀奇真稀奇！不明结晶打造的小船，不明来历，船上仅有一只小猫！”#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 61376,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 61376,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_61411",
   "item_id": 61411,
   "name": "红歌鲤",
   "kind": "图鉴",
   "desc": "红歌鲤生活在海域，营养丰富，肉质鲜美。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 61411,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 61411,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_61508",
   "item_id": 61508,
   "name": "胡桃夹子木偶",
   "kind": "图鉴",
   "desc": "旧世界大受青睐的玩偶系列，具有悠久的历史。#r在同名舞剧的塑造下，胡桃夹子成为了勇气的象征，是赠送给孩子们的礼物佳品。#r本系列玩偶在旧世界发售时，曾与其它商品捆绑销售，#r为了凑齐整套胡桃夹子，需要费上一番力气。#r字面意思：真的能够夹核桃。#r全套一共12个，据说集齐之后能够带来好运。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 61508,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 61508,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_61582",
   "item_id": 61582,
   "name": "马头鱼",
   "kind": "图鉴",
   "desc": "头较大而高，有几分像马头，故被称为马头鱼。烹饪后虽然口味清淡却回味无穷。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 61582,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 61582,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_61679",
   "item_id": 61679,
   "name": "胡桃夹子木偶",
   "kind": "图鉴",
   "desc": "旧世界大受青睐的玩偶系列，具有悠久的历史。#r在同名舞剧的塑造下，胡桃夹子成为了勇气的象征，是赠送给孩子们的礼物佳品。#r本系列玩偶在旧世界发售时，曾与其它商品捆绑销售，#r为了凑齐整套胡桃夹子，需要费上一番力气。#r字面意思：真的能够夹核桃。#r全套一共12个，据说集齐之后能够带来好运。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 61679,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 61679,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_61753",
   "item_id": 61753,
   "name": "蓝龙虾",
   "kind": "图鉴",
   "desc": "蓝龙虾是龙虾的一种罕见基因变异现象，使得外壳呈现蓝色，十分稀有。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 61753,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 61753,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_67842",
   "item_id": 67842,
   "name": "黑匣子",
   "kind": "图鉴",
   "desc": "沉水的黑匣子，年代不详，解析后能得到一些神秘的信息。#r可惜能够捕捉到的电讯号断断续续，准度有限：#r“为了证实帝国的罪行，审判是必要的。”#r“指认的成功与否，取决于本次行动是否能够保护证人毫发无损地抵达目的地。”#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 67842,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 67842,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_67875",
   "item_id": 67875,
   "name": "面包蟹",
   "kind": "图鉴",
   "desc": "面包蟹的外壳较为隆起，常栖息于沙质或沙泥质海底。烹饪后肉质饱满，味道鲜甜。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 67875,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 67875,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_67909",
   "item_id": 67909,
   "name": "《小猫瑞文历险记》",
   "kind": "图鉴",
   "desc": "《小猫瑞文历险记》是旧世界著名奇幻小说，与罗森波顿系列齐名，并称为奇幻小说双璧。#r此书为该系列的第二部《搏命凶浪》：#r好景不长，就在劳尔照例外出捕鱼时，可怜的小伙子被路过的匪兵船只强行征召为航海向导。#r士兵们毁坏了劳尔的船只，将劳尔捉上军船，逼迫劳尔为他们带路。#r劳尔一心想逃回家乡，无奈茫茫海上风高浪急，无处可逃。#r幸好危机之下，小猫瑞文钻进了主人的帽子里，跟随劳尔一同来到海上。#r当看到瑞文敏捷地跳上自己的膝头时，被关在货舱仓库里的劳尔紧紧地抱住了自己的小猫，流下感动的泪水。#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 67909,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 67909,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_67944",
   "item_id": 67944,
   "name": "锦绣龙虾",
   "kind": "图鉴",
   "desc": "锦绣龙虾又称青龙虾，体色多彩明亮，肉质紧实弹牙。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 67944,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 67944,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_67979",
   "item_id": 67979,
   "name": "《小猫瑞文历险记》",
   "kind": "图鉴",
   "desc": "《小猫瑞文历险记》是旧世界著名奇幻小说，与罗森波顿系列齐名，并称为奇幻小说双璧。#r此书为该系列的第十一部《晶体囚牢》：#r大海将为诸众降下惩罚，而真正善良的人会得到祝福。#r“劳尔，别害怕。”#r“海面会被冻结如同澄澈的天空，它能支撑你奔跑。”#r“奔跑吧，劳尔！”#r“你一定要一直、一直向前跑，绝对不可以回头看。”#r“你的小猫会指引你抵达正确的位置。”#r“跟着它，一直跑到东方升起第一丝曙光。”#r在响起的歌声之中，乘客们和士兵纷纷被突然加速凝结的晶体牢牢裹住，束缚在一个个半透明的晶柱之内。#r勇敢的小猫瑞文四爪飞驰，紧紧跟在劳尔的后面。#r结晶燃烧爆裂，熊熊的火势如天上降下硫黄一般，把黑夜照亮如白昼。#r劳尔在奔跑。#r瑞文在奔跑。#r晶封的海面映出远处的火光，一人一猫，奔跑在明亮的夜里。#r眼见就要逃离险境。#r善良的劳尔却因为担心埃莱沙的安危，还是回头望了一眼。#r不幸发生了#r——他的身上霎时开始结晶。#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 67979,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 67979,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_68014",
   "item_id": 68014,
   "name": "巴浪鱼",
   "kind": "图鉴",
   "desc": "巴浪鱼生长速度很快，蛋白质含量较高，肉质紧实，咸鲜宜人。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 68014,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 68014,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_68049",
   "item_id": 68049,
   "name": "《小猫瑞文历险记》",
   "kind": "图鉴",
   "desc": "《小猫瑞文历险记》是旧世界著名奇幻小说，与罗森波顿系列齐名，并称为奇幻小说双璧。#r此书为该系列的第七部《暗夜惊魂》：#r又是满头大汗地从梦中惊醒，这一次劳尔却警觉地听见了逐渐靠近的脚步声。#r他本能地感受到强烈的威胁。#r劳尔立刻翻身下床，躲在床板下蜷缩起来，屏息凝视着门板被缓缓推开。#r月光洒进来。#r迟钝的脚步拍打着地板，发出嘎吱嘎吱的刺耳声音，鼻腔里萦绕着淤泥腥臭而潮湿的味道。#r不知道是什么人正在一步步走近，劳尔屏住呼吸，恐惧地闭紧了双眼。#r劳尔害怕极了，颤抖不止，就在他觉得自己已经抵达了几乎就要无法忍受的临界点，对方的声音停止了。#r他迟疑地睁开眼，正对上一双金色的瞳孔。#r劳尔立刻吓昏了过去。#r昏倒之后的劳尔意外地进入了甜美的梦乡，梦里似乎有人一直在唱着安宁的歌谣，声音就像瑞贝卡唱片里的那样清澈好听。#r第二天醒来，劳尔却毫发无损地躺在床上，瑞文窝在它的头上。#r出门一切正常，就像只有他一个人做了噩梦。#r直到阳光一闪晃到他的眼睛，劳尔定睛一看，发现走过的士兵后颈上出现了鳞片状的结晶。#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 68049,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 68049,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_68084",
   "item_id": 68084,
   "name": "花蟹",
   "kind": "图鉴",
   "desc": "花蟹因为外壳有花纹而得名，含有丰富的蛋白质、微量元素等，肉味鲜美，营养丰富。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 68084,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 68084,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_68119",
   "item_id": 68119,
   "name": "《小猫瑞文历险记》",
   "kind": "图鉴",
   "desc": "《小猫瑞文历险记》是旧世界著名奇幻小说，与罗森波顿系列齐名，并称为奇幻小说双璧。#r此书为该系列的第六部《古老传说》：#r目睹了可怕的景象之后，劳尔开始不停地做噩梦，梦里总是滔天的巨浪……#r高墙般的大浪重重拍下，将一切击碎湮灭。#r深沉而半透明的海水琥珀一般，嵌满了蚂蚁一样的密密麻麻的不明黑影。#r从噩梦中醒来的劳尔惊魂未定，想到自己悲惨的遭遇，不禁悲从中来，几欲落泪。#r蜷缩在劳尔身旁睡觉的小猫瑞文似乎感知到劳尔悲伤的情绪，#r一时失去了睡意的劳尔便揽过小猫，解闷似地开始对瑞文讲起儿时听到的传说：#r渔村里的长者从小就反复告诫劳尔不能哭泣——小儿夜啼，哭声会引来海啸。#r因此村子里的窗户全都要封死，不能让孩子夜里的哭声传出去被大海听到。#r“眼泪是咸的，因为流出来的是海水。我们的眼睛与大海紧密相连，我们都是大海的孩子。”#r“听到哭声的大海，会赶来将它的孩子带走。”#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 68119,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 68119,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_68154",
   "item_id": 68154,
   "name": "比目鱼",
   "kind": "图鉴",
   "desc": "比目鱼的身体扁平，眼睛生长在身体的同一侧。虽然它的长相十分奇特，但它的肉质鲜嫩，鱼刺也较少，适合多种方式食用。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 68154,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 68154,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_68189",
   "item_id": 68189,
   "name": "《小猫瑞文历险记》",
   "kind": "图鉴",
   "desc": "《小猫瑞文历险记》是旧世界著名奇幻小说，与罗森波顿系列齐名，并称为奇幻小说双璧。#r此书为该系列的第五部《善恶循环》：#r午后，就在劳尔惯例清洗甲板时，异变发生了。#r原本一边晒着太阳、一边沉默地游荡的乘客，突然就像从梦中惊醒一般，开始大喊大叫，嚷嚷着自己没有疯掉。#r站在附近的士兵立刻上前，用枪托击倒了这名乘客，并将其扔下了船只。#r一切发生得太快，惊呆在原地的劳尔根本来不及阻止。#r而几名罪魁祸首正忙着望向被扔下水的乘客大声地嘲笑着，全然没有注意到原本站在后面的女孩，已经摘下蒙在自己双眼上的黑色布条，一双金色的诡异眼眸牢牢盯住了他们。#r几乎是同时，几名士兵捂住胸口，不停地呕吐；用得力气大了，身体趔趄，跌入海中失去了踪影。#r一只白色海鸥坠落在甲板上，失去了声息。#r甲板上余下的众人，谁也没有再发出声音，唯有海浪声声。#r劳尔听见一丝几不可闻的冷哼，回头望向埃莱沙。#r只见她又蒙上了那块黑布，就如同刚才一切都是劳尔的错觉。#r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 68189,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 68189,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_68224",
   "item_id": 68224,
   "name": "基围虾",
   "kind": "图鉴",
   "desc": "基围虾体表有许多凹陷，甲壳粗糙，生长快，具有壳薄体肥、出肉率高、肉质鲜嫩弹牙的特点。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 68224,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 68224,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_68259",
   "item_id": 68259,
   "name": "《小猫瑞文历险记》",
   "kind": "图鉴",
   "desc": "《小猫瑞文历险记》是旧世界著名奇幻小说，与罗森波顿系列齐名，并称为奇幻小说双璧。#r此书为该系列的第四部《安宁歌谣》：#r可怜的劳尔每天都要在船上劳作，很快就记住了几乎所有人的样貌。#r在这些人中，有一名小女孩格外引起了劳尔的注意。#r这位年轻的乘客，眼睛上总是蒙着黑色的布条，本应视线受阻、但行动却如常人一般自在。#r劳尔提着水桶和墩布，四处擦洗，一次正巧碰到小女孩站在栏杆处哼着小调。#r与往日船上鸦雀无声的氛围相比，轻柔的旋律飘进劳尔的耳朵，令他心情大好。#r他一边擦洗舷窗，一边学着女孩随口哼唱，忽视了歌声早已在不知不觉间停止了。#r一回头，却发现不知何时女孩已经悄悄来到了他的背后，似乎已有小一阵子。#r“别唱了”。#r女孩冰冷的态度令劳尔莫名紧张，绷直了身体试图逃走。#r正在这时，似乎是感知到了主人的窘迫，小猫瑞文突然从劳尔的兜帽中探出头来。#r女孩面色缓和，告诫劳尔歌声有可能为他招来危险，让他不要再尝试了。#r“埃莱沙，我的名字。”#r说完便自顾自地离开。#r“劳尔！”#r“这是我的小猫瑞文！”#r望着女孩的背影，劳尔兴奋地大喊着自己的名字，惊喜于自己有可能终于在这艘可怕的大船上交到了第一个朋友。 #r",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 68259,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 68259,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_68294",
   "item_id": 68294,
   "name": "皇帝蟹",
   "kind": "图鉴",
   "desc": "经常被人和帝王蟹混淆，但两者长得有较大区别。皇帝蟹体型较重，身体和前鳌都十分巨大。烹饪后肉质紧实饱满，蟹膏醇厚浓郁。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 68294,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 68294,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_68329",
   "item_id": 68329,
   "name": "胡桃夹子木偶",
   "kind": "图鉴",
   "desc": "旧世界大受青睐的玩偶系列，具有悠久的历史。#r在同名舞剧的塑造下，胡桃夹子成为了勇气的象征，是赠送给孩子们的礼物佳品。#r本系列玩偶在旧世界发售时，曾与其它商品捆绑销售，#r为了凑齐整套胡桃夹子，需要费上一番力气。#r字面意思：真的能够夹核桃。#r全套一共12个，据说集齐之后能够带来好运。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 68329,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 68329,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  },
  {
   "id": "illus_68363",
   "item_id": 68363,
   "name": "三刀鱼",
   "kind": "图鉴",
   "desc": "由于身上有着三道条形的花纹，故被称为三刀鱼。烹饪后肉质十分鲜美。",
   "extra_desc": "",
   "evidence": "structure",
   "evidence_level": "static/candidate",
   "status_tags": [
    "static config"
   ],
   "source": "illustration_collect_item_data",
   "provenance": {
    "source_id": "documents-py314-current",
    "table": "illustration_collect_item_data",
    "row_key": 68363,
    "field_refs": [
     "name",
     "desc"
    ],
    "name_source": "item_master_full#name（item_id 查名）",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "documents-py314-current",
       "table": "illustration_collect_item_data",
       "row_key": 68363,
       "field_refs": [
        "name",
        "desc"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
    "upstream": {
     "package_sha256": "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e",
     "entry_index": null,
     "file_id": null,
     "role": "super_fashion_lottery_conf_data",
     "table_sha256": "910fb7c0c4cd8a22e9940305f14d16098ade4901b0a37faf7efde65c4c1548fa"
    }
   }
  }
 ]
};
