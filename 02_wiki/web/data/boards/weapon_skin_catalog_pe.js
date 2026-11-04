window.WIKI_BOARD_weapon_skin_catalog_pe = {
 "meta": {
  "name": "（二）武器皮肤 · 当前包图鉴",
  "category": "一、时装类 / （二）武器皮肤",
  "generated": "2026-11-04",
  "evidence": "structure",
  "source_server": "PE 体验服客户端 script.py314.lc.npk（雷电 11-03 热更后）",
  "package_sha": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
  "id_label": "皮肤ID",
  "hide_media": true,
  "card_mode": "roster",
  "filters": [
   {
    "key": "weapon_type_label",
    "label": "武器类型"
   },
   {
    "key": "grade_level",
    "label": "品级"
   }
  ],
  "card_summary": [
   [
    "name",
    "名称"
   ],
   [
    "weapon_type_label",
    "武器类型"
   ],
   [
    "grade_level",
    "品级"
   ],
   [
    "sale_date",
    "上架"
   ],
   [
    "sfx_count",
    "音效条数"
   ]
  ],
  "field_labels": {
   "name": "名称",
   "skin_id": "皮肤ID",
   "weapon_type": "武器类型码",
   "weapon_type_label": "武器类型",
   "name_status": "命名状态",
   "grade_level": "品级",
   "sale_date": "上架日期",
   "sfx_count": "音效条数",
   "has_item_row": "有道具行",
   "version_status": "版本状态"
  },
  "hide_fields": [
   "source",
   "id",
   "provenance",
   "evidence",
   "evidence_level",
   "status_tags",
   "sale_ts",
   "name_source"
  ],
  "state_summary": {
   "条目": 145,
   "有道具行": 143,
   "有音效": 84
  },
  "notes": "只读 PE 客户端包；不依赖历史基线（基线容器本机不存在）⇒ 版本状态一律「无基线（不可比）」。名字优先 common_item_data，缺行时退回表内名并标 has_item_row=false。",
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
     "source_id": "pe-client-script-npk",
     "role": "primary",
     "sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "bytes": 250112428,
     "mtime_ns": 1793735183127945400,
     "path": "E:\\la拆包项目\\90_临时\\pe_client\\Documents\\script.py314.lc.npk",
     "desc": "PE 体验服客户端脚本包（雷电 g66/Documents）"
    }
   ]
  }
 },
 "periods": [],
 "items": [
  {
   "id": "1110202",
   "skin_id": 1110202,
   "name": "皮肤 1110202",
   "name_source": "none",
   "grade_level": 4,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "unresolved",
   "sale_ts": 1793894400,
   "sale_date": "2026-11-06",
   "has_item_row": false,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110202,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "weapon_skin_data#skin_name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110202,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110203",
   "skin_id": 1110203,
   "name": "皮肤 1110203",
   "name_source": "none",
   "grade_level": 4,
   "weapon_type": 5,
   "weapon_type_label": "狙击枪（5）",
   "name_status": "unresolved",
   "sale_ts": 1793894400,
   "sale_date": "2026-11-06",
   "has_item_row": false,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110203,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "weapon_skin_data#skin_name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110203,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110189",
   "skin_id": 1110189,
   "name": "浪漫过载",
   "name_source": "common_item",
   "grade_level": 5,
   "weapon_type": 20,
   "weapon_type_label": "喷火器（20）",
   "name_status": "verified",
   "sale_ts": 1793808000,
   "sale_date": "2026-11-05",
   "has_item_row": true,
   "sfx_count": 6,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110189,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110189,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110194",
   "skin_id": 1110194,
   "name": "青瓷鉴心",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 5,
   "weapon_type_label": "狙击枪（5）",
   "name_status": "verified",
   "sale_ts": 1793808000,
   "sale_date": "2026-11-05",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110194,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110194,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110188",
   "skin_id": 1110188,
   "name": "一魂共鸣",
   "name_source": "common_item",
   "grade_level": 5,
   "weapon_type": 1,
   "weapon_type_label": "突击步枪（1）",
   "name_status": "verified",
   "sale_ts": 1792598400,
   "sale_date": "2026-10-22",
   "has_item_row": true,
   "sfx_count": 8,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110188,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110188,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110191",
   "skin_id": 1110191,
   "name": "紧急预案",
   "name_source": "common_item",
   "grade_level": 2,
   "weapon_type": 6,
   "weapon_type_label": "手枪（6）",
   "name_status": "verified",
   "sale_ts": 1792598400,
   "sale_date": "2026-10-22",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110191,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110191,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110192",
   "skin_id": 1110192,
   "name": "第十三页",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 8,
   "weapon_type_label": "电磁机枪（8）",
   "name_status": "verified",
   "sale_ts": 1792598400,
   "sale_date": "2026-10-22",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110192,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110192,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110185",
   "skin_id": 1110185,
   "name": "奇迹",
   "name_source": "common_item",
   "grade_level": 5,
   "weapon_type": 3,
   "weapon_type_label": "弓箭（3）",
   "name_status": "verified",
   "sale_ts": 1790697600,
   "sale_date": "2026-09-30",
   "has_item_row": true,
   "sfx_count": 8,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110185,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110185,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "11101851",
   "skin_id": 11101851,
   "name": "奇迹（7天）",
   "name_source": "common_item",
   "grade_level": 5,
   "weapon_type": 3,
   "weapon_type_label": "弓箭（3）",
   "name_status": "verified",
   "sale_ts": 1790697600,
   "sale_date": "2026-09-30",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 11101851,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 11101851,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110186",
   "skin_id": 1110186,
   "name": "星辰刀",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1790697600,
   "sale_date": "2026-09-30",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110186,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110186,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "11101861",
   "skin_id": 11101861,
   "name": "星辰刀（7天）",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1790697600,
   "sale_date": "2026-09-30",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 11101861,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 11101861,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110187",
   "skin_id": 1110187,
   "name": "前方禁行",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1790697600,
   "sale_date": "2026-09-30",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110187,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110187,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110198",
   "skin_id": 1110198,
   "name": "拟化鳞渊",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 7,
   "weapon_type_label": "榴弹炮（7）",
   "name_status": "verified",
   "sale_ts": 1790697600,
   "sale_date": "2026-09-30",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110198,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110198,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110199",
   "skin_id": 1110199,
   "name": "拟化幽瞳",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 6,
   "weapon_type_label": "手枪（6）",
   "name_status": "verified",
   "sale_ts": 1790697600,
   "sale_date": "2026-09-30",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110199,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110199,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110184",
   "skin_id": 1110184,
   "name": "星火永传",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1789574400,
   "sale_date": "2026-09-17",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110184,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110184,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110190",
   "skin_id": 1110190,
   "name": "佳期如梦",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 4,
   "weapon_type_label": "霰弹枪（4）",
   "name_status": "verified",
   "sale_ts": 1789574400,
   "sale_date": "2026-09-17",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110190,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110190,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110181",
   "skin_id": 1110181,
   "name": "疾影枪",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 6,
   "weapon_type_label": "手枪（6）",
   "name_status": "verified",
   "sale_ts": 1788364800,
   "sale_date": "2026-09-03",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110181,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110181,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "11101811",
   "skin_id": 11101811,
   "name": "疾影枪（7天）",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 6,
   "weapon_type_label": "手枪（6）",
   "name_status": "verified",
   "sale_ts": 1788364800,
   "sale_date": "2026-09-03",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 11101811,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 11101811,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110182",
   "skin_id": 1110182,
   "name": "火刑裁决",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 7,
   "weapon_type_label": "榴弹炮（7）",
   "name_status": "verified",
   "sale_ts": 1788364800,
   "sale_date": "2026-09-03",
   "has_item_row": true,
   "sfx_count": 3,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110182,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110182,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110183",
   "skin_id": 1110183,
   "name": "战神烈火剑",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1788364800,
   "sale_date": "2026-09-03",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110183,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110183,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "11101831",
   "skin_id": 11101831,
   "name": "战神烈火剑（7天）",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1788364800,
   "sale_date": "2026-09-03",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 11101831,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 11101831,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110177",
   "skin_id": 1110177,
   "name": "极光剑",
   "name_source": "common_item",
   "grade_level": 5,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1787155200,
   "sale_date": "2026-08-20",
   "has_item_row": true,
   "sfx_count": 10,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110177,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110177,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "11101771",
   "skin_id": 11101771,
   "name": "极光剑（7天）",
   "name_source": "common_item",
   "grade_level": 5,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1787155200,
   "sale_date": "2026-08-20",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 11101771,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 11101771,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110178",
   "skin_id": 1110178,
   "name": "帝皇裁决",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 1,
   "weapon_type_label": "突击步枪（1）",
   "name_status": "verified",
   "sale_ts": 1787155200,
   "sale_date": "2026-08-20",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110178,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110178,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "11101781",
   "skin_id": 11101781,
   "name": "帝皇裁决（7天）",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 1,
   "weapon_type_label": "突击步枪（1）",
   "name_status": "verified",
   "sale_ts": 1787155200,
   "sale_date": "2026-08-20",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 11101781,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 11101781,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110197",
   "skin_id": 1110197,
   "name": "极光盾",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 51,
   "weapon_type_label": "护臂/盾（51）",
   "name_status": "verified",
   "sale_ts": 1787155200,
   "sale_date": "2026-08-20",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110197,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110197,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110167",
   "skin_id": 1110167,
   "name": "粉息鸣弦",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 3,
   "weapon_type_label": "弓箭（3）",
   "name_status": "verified",
   "sale_ts": 1785945600,
   "sale_date": "2026-08-06",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110167,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110167,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110173",
   "skin_id": 1110173,
   "name": "水晶玫瑰",
   "name_source": "common_item",
   "grade_level": 6,
   "weapon_type": 7,
   "weapon_type_label": "榴弹炮（7）",
   "name_status": "verified",
   "sale_ts": 1784822400,
   "sale_date": "2026-07-24",
   "has_item_row": true,
   "sfx_count": 10,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110173,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110173,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110174",
   "skin_id": 1110174,
   "name": "水晶玫瑰",
   "name_source": "common_item",
   "grade_level": 6,
   "weapon_type": 7,
   "weapon_type_label": "榴弹炮（7）",
   "name_status": "verified",
   "sale_ts": 1784822400,
   "sale_date": "2026-07-24",
   "has_item_row": true,
   "sfx_count": 10,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110174,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110174,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110175",
   "skin_id": 1110175,
   "name": "水晶玫瑰",
   "name_source": "common_item",
   "grade_level": 6,
   "weapon_type": 7,
   "weapon_type_label": "榴弹炮（7）",
   "name_status": "verified",
   "sale_ts": 1784822400,
   "sale_date": "2026-07-24",
   "has_item_row": true,
   "sfx_count": 10,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110175,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110175,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110176",
   "skin_id": 1110176,
   "name": "晶棘",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 8,
   "weapon_type_label": "电磁机枪（8）",
   "name_status": "verified",
   "sale_ts": 1784822400,
   "sale_date": "2026-07-24",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110176,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110176,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110180",
   "skin_id": 1110180,
   "name": "西瓜脆脆冰",
   "name_source": "common_item",
   "grade_level": 2,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1784822400,
   "sale_date": "2026-07-24",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110180,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110180,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110172",
   "skin_id": 1110172,
   "name": "缄默",
   "name_source": "common_item",
   "grade_level": 2,
   "weapon_type": 5,
   "weapon_type_label": "狙击枪（5）",
   "name_status": "verified",
   "sale_ts": 1783526400,
   "sale_date": "2026-07-09",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110172,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110172,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110179",
   "skin_id": 1110179,
   "name": "往哪看呢",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 5,
   "weapon_type_label": "狙击枪（5）",
   "name_status": "verified",
   "sale_ts": 1783526400,
   "sale_date": "2026-07-09",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110179,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110179,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110168",
   "skin_id": 1110168,
   "name": "云上铃",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 1,
   "weapon_type_label": "突击步枪（1）",
   "name_status": "verified",
   "sale_ts": 1782316800,
   "sale_date": "2026-06-25",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110168,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110168,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "11101681",
   "skin_id": 11101681,
   "name": "云上铃（14天）",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 1,
   "weapon_type_label": "突击步枪（1）",
   "name_status": "verified",
   "sale_ts": 1782316800,
   "sale_date": "2026-06-25",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 11101681,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 11101681,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110169",
   "skin_id": 1110169,
   "name": "灰色协议",
   "name_source": "common_item",
   "grade_level": 5,
   "weapon_type": 5,
   "weapon_type_label": "狙击枪（5）",
   "name_status": "verified",
   "sale_ts": 1782316800,
   "sale_date": "2026-06-25",
   "has_item_row": true,
   "sfx_count": 6,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110169,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110169,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "11101691",
   "skin_id": 11101691,
   "name": "灰色协议（14天）",
   "name_source": "common_item",
   "grade_level": 5,
   "weapon_type": 5,
   "weapon_type_label": "狙击枪（5）",
   "name_status": "verified",
   "sale_ts": 1782316800,
   "sale_date": "2026-06-25",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 11101691,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 11101691,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110170",
   "skin_id": 1110170,
   "name": "红太狼之怒",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1782316800,
   "sale_date": "2026-06-25",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110170,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110170,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "11101701",
   "skin_id": 11101701,
   "name": "红太狼之怒（14天）",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1782316800,
   "sale_date": "2026-06-25",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 11101701,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 11101701,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110171",
   "skin_id": 1110171,
   "name": "光影咏叹调",
   "name_source": "common_item",
   "grade_level": 5,
   "weapon_type": 6,
   "weapon_type_label": "手枪（6）",
   "name_status": "verified",
   "sale_ts": 1782316800,
   "sale_date": "2026-06-25",
   "has_item_row": true,
   "sfx_count": 8,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110171,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110171,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110166",
   "skin_id": 1110166,
   "name": "专业护理",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 5,
   "weapon_type_label": "狙击枪（5）",
   "name_status": "verified",
   "sale_ts": 1781107200,
   "sale_date": "2026-06-11",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110166,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110166,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110165",
   "skin_id": 1110165,
   "name": "墨隐麒麟",
   "name_source": "common_item",
   "grade_level": 5,
   "weapon_type": 4,
   "weapon_type_label": "霰弹枪（4）",
   "name_status": "verified",
   "sale_ts": 1779984000,
   "sale_date": "2026-05-29",
   "has_item_row": true,
   "sfx_count": 6,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110165,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110165,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110162",
   "skin_id": 1110162,
   "name": "嗷嗷奶龙",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1778688000,
   "sale_date": "2026-05-14",
   "has_item_row": true,
   "sfx_count": 3,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110162,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110162,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110163",
   "skin_id": 1110163,
   "name": "砰砰奶龙",
   "name_source": "common_item",
   "grade_level": 2,
   "weapon_type": 6,
   "weapon_type_label": "手枪（6）",
   "name_status": "verified",
   "sale_ts": 1778688000,
   "sale_date": "2026-05-14",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110163,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110163,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110164",
   "skin_id": 1110164,
   "name": "霜鳞·皇带",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1778688000,
   "sale_date": "2026-05-14",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110164,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110164,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110157",
   "skin_id": 1110157,
   "name": "夜明",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 7,
   "weapon_type_label": "榴弹炮（7）",
   "name_status": "verified",
   "sale_ts": 1777478400,
   "sale_date": "2026-04-30",
   "has_item_row": true,
   "sfx_count": 3,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110157,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110157,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110158",
   "skin_id": 1110158,
   "name": "特殊关怀",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1777478400,
   "sale_date": "2026-04-30",
   "has_item_row": true,
   "sfx_count": 1,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110158,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110158,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110159",
   "skin_id": 1110159,
   "name": "沙海月鸣",
   "name_source": "common_item",
   "grade_level": 6,
   "weapon_type": 1,
   "weapon_type_label": "突击步枪（1）",
   "name_status": "verified",
   "sale_ts": 1777478400,
   "sale_date": "2026-04-30",
   "has_item_row": true,
   "sfx_count": 10,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110159,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110159,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110160",
   "skin_id": 1110160,
   "name": "沙海月鸣",
   "name_source": "common_item",
   "grade_level": 6,
   "weapon_type": 1,
   "weapon_type_label": "突击步枪（1）",
   "name_status": "verified",
   "sale_ts": 1777478400,
   "sale_date": "2026-04-30",
   "has_item_row": true,
   "sfx_count": 10,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110160,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110160,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110161",
   "skin_id": 1110161,
   "name": "沙海月鸣",
   "name_source": "common_item",
   "grade_level": 6,
   "weapon_type": 1,
   "weapon_type_label": "突击步枪（1）",
   "name_status": "verified",
   "sale_ts": 1777478400,
   "sale_date": "2026-04-30",
   "has_item_row": true,
   "sfx_count": 10,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110161,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110161,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110156",
   "skin_id": 1110156,
   "name": "噬极",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 20,
   "weapon_type_label": "喷火器（20）",
   "name_status": "verified",
   "sale_ts": 1776268800,
   "sale_date": "2026-04-16",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110156,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110156,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110151",
   "skin_id": 1110151,
   "name": "阿赖耶识",
   "name_source": "common_item",
   "grade_level": 5,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1775059200,
   "sale_date": "2026-04-02",
   "has_item_row": true,
   "sfx_count": 8,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110151,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110151,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110152",
   "skin_id": 1110152,
   "name": "灵态诱导",
   "name_source": "common_item",
   "grade_level": 5,
   "weapon_type": 7,
   "weapon_type_label": "榴弹炮（7）",
   "name_status": "verified",
   "sale_ts": 1775059200,
   "sale_date": "2026-04-02",
   "has_item_row": true,
   "sfx_count": 6,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110152,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110152,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110153",
   "skin_id": 1110153,
   "name": "定格日常",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 1,
   "weapon_type_label": "突击步枪（1）",
   "name_status": "verified",
   "sale_ts": 1775059200,
   "sale_date": "2026-04-02",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110153,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110153,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110154",
   "skin_id": 1110154,
   "name": "重力震爆",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 4,
   "weapon_type_label": "霰弹枪（4）",
   "name_status": "verified",
   "sale_ts": 1775059200,
   "sale_date": "2026-04-02",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110154,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110154,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110155",
   "skin_id": 1110155,
   "name": "绯樱轻扬",
   "name_source": "common_item",
   "grade_level": 2,
   "weapon_type": 5,
   "weapon_type_label": "狙击枪（5）",
   "name_status": "verified",
   "sale_ts": 1775059200,
   "sale_date": "2026-04-02",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110155,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110155,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110149",
   "skin_id": 1110149,
   "name": "鎏金淬火",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 20,
   "weapon_type_label": "喷火器（20）",
   "name_status": "verified",
   "sale_ts": 1773849600,
   "sale_date": "2026-03-19",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110149,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110149,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110150",
   "skin_id": 1110150,
   "name": "铃兰之约",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1773849600,
   "sale_date": "2026-03-19",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110150,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110150,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110130",
   "skin_id": 1110130,
   "name": "粉色剧目",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 8,
   "weapon_type_label": "电磁机枪（8）",
   "name_status": "verified",
   "sale_ts": 1772035200,
   "sale_date": "2026-02-26",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110130,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110130,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110012",
   "skin_id": 1110012,
   "name": "腾云",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 20,
   "weapon_type_label": "喷火器（20）",
   "name_status": "verified",
   "sale_ts": 1770912000,
   "sale_date": "2026-02-13",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110012,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110012,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110145",
   "skin_id": 1110145,
   "name": "天马行空",
   "name_source": "common_item",
   "grade_level": 5,
   "weapon_type": 1,
   "weapon_type_label": "突击步枪（1）",
   "name_status": "verified",
   "sale_ts": 1770825600,
   "sale_date": "2026-02-12",
   "has_item_row": true,
   "sfx_count": 6,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110145,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110145,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "11101451",
   "skin_id": 11101451,
   "name": "天马行空（14天）",
   "name_source": "common_item",
   "grade_level": 5,
   "weapon_type": 1,
   "weapon_type_label": "突击步枪（1）",
   "name_status": "verified",
   "sale_ts": 1770825600,
   "sale_date": "2026-02-12",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 11101451,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 11101451,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110146",
   "skin_id": 1110146,
   "name": "龙渊永寂",
   "name_source": "common_item",
   "grade_level": 5,
   "weapon_type": 5,
   "weapon_type_label": "狙击枪（5）",
   "name_status": "verified",
   "sale_ts": 1770825600,
   "sale_date": "2026-02-12",
   "has_item_row": true,
   "sfx_count": 6,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110146,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110146,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110148",
   "skin_id": 1110148,
   "name": "马到福来",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 7,
   "weapon_type_label": "榴弹炮（7）",
   "name_status": "verified",
   "sale_ts": 1770825600,
   "sale_date": "2026-02-12",
   "has_item_row": true,
   "sfx_count": 1,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110148,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110148,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110142",
   "skin_id": 1110142,
   "name": "金乌负日",
   "name_source": "common_item",
   "grade_level": 6,
   "weapon_type": 3,
   "weapon_type_label": "弓箭（3）",
   "name_status": "verified",
   "sale_ts": 1769616000,
   "sale_date": "2026-01-29",
   "has_item_row": true,
   "sfx_count": 10,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110142,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110142,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110143",
   "skin_id": 1110143,
   "name": "金乌负日",
   "name_source": "common_item",
   "grade_level": 6,
   "weapon_type": 3,
   "weapon_type_label": "弓箭（3）",
   "name_status": "verified",
   "sale_ts": 1769616000,
   "sale_date": "2026-01-29",
   "has_item_row": true,
   "sfx_count": 10,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110143,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110143,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110144",
   "skin_id": 1110144,
   "name": "金乌负日",
   "name_source": "common_item",
   "grade_level": 6,
   "weapon_type": 3,
   "weapon_type_label": "弓箭（3）",
   "name_status": "verified",
   "sale_ts": 1769616000,
   "sale_date": "2026-01-29",
   "has_item_row": true,
   "sfx_count": 10,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110144,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110144,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110140",
   "skin_id": 1110140,
   "name": "雪吻双星",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 6,
   "weapon_type_label": "手枪（6）",
   "name_status": "verified",
   "sale_ts": 1768406400,
   "sale_date": "2026-01-15",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110140,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110140,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110147",
   "skin_id": 1110147,
   "name": "可盐可甜",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1768406400,
   "sale_date": "2026-01-15",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110147,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110147,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110139",
   "skin_id": 1110139,
   "name": "吃喵一爪",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1767110400,
   "sale_date": "2025-12-31",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110139,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110139,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110138",
   "skin_id": 1110138,
   "name": "雪夜绮礼",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 7,
   "weapon_type_label": "榴弹炮（7）",
   "name_status": "verified",
   "sale_ts": 1765987200,
   "sale_date": "2025-12-18",
   "has_item_row": true,
   "sfx_count": 3,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110138,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110138,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110137",
   "skin_id": 1110137,
   "name": "焚古龙息",
   "name_source": "common_item",
   "grade_level": 5,
   "weapon_type": 20,
   "weapon_type_label": "喷火器（20）",
   "name_status": "verified",
   "sale_ts": 1764864000,
   "sale_date": "2025-12-05",
   "has_item_row": true,
   "sfx_count": 4,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110137,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110137,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110131",
   "skin_id": 1110131,
   "name": "炽日耀斑",
   "name_source": "common_item",
   "grade_level": 6,
   "weapon_type": 4,
   "weapon_type_label": "霰弹枪（4）",
   "name_status": "verified",
   "sale_ts": 1762444800,
   "sale_date": "2025-11-07",
   "has_item_row": true,
   "sfx_count": 10,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110131,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110131,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110132",
   "skin_id": 1110132,
   "name": "炽日耀斑",
   "name_source": "common_item",
   "grade_level": 6,
   "weapon_type": 4,
   "weapon_type_label": "霰弹枪（4）",
   "name_status": "verified",
   "sale_ts": 1762444800,
   "sale_date": "2025-11-07",
   "has_item_row": true,
   "sfx_count": 10,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110132,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110132,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110133",
   "skin_id": 1110133,
   "name": "炽日耀斑",
   "name_source": "common_item",
   "grade_level": 6,
   "weapon_type": 4,
   "weapon_type_label": "霰弹枪（4）",
   "name_status": "verified",
   "sale_ts": 1762444800,
   "sale_date": "2025-11-07",
   "has_item_row": true,
   "sfx_count": 10,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110133,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110133,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110135",
   "skin_id": 1110135,
   "name": "神翼曙光",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 8,
   "weapon_type_label": "电磁机枪（8）",
   "name_status": "verified",
   "sale_ts": 1762444800,
   "sale_date": "2025-11-07",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110135,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110135,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110136",
   "skin_id": 1110136,
   "name": "时光溯流",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 1,
   "weapon_type_label": "突击步枪（1）",
   "name_status": "verified",
   "sale_ts": 1762444800,
   "sale_date": "2025-11-07",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110136,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110136,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110129",
   "skin_id": 1110129,
   "name": "熔炉寒霜",
   "name_source": "common_item",
   "grade_level": 5,
   "weapon_type": 1,
   "weapon_type_label": "突击步枪（1）",
   "name_status": "verified",
   "sale_ts": 1761148800,
   "sale_date": "2025-10-23",
   "has_item_row": true,
   "sfx_count": 5,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110129,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110129,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110134",
   "skin_id": 1110134,
   "name": "罚罪审判",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 3,
   "weapon_type_label": "弓箭（3）",
   "name_status": "verified",
   "sale_ts": 1761148800,
   "sale_date": "2025-10-23",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110134,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110134,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "11101341",
   "skin_id": 11101341,
   "name": "罚罪审判（14天）",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 3,
   "weapon_type_label": "弓箭（3）",
   "name_status": "verified",
   "sale_ts": 1761148800,
   "sale_date": "2025-10-23",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 11101341,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 11101341,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110127",
   "skin_id": 1110127,
   "name": "湮没星空",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 20,
   "weapon_type_label": "喷火器（20）",
   "name_status": "verified",
   "sale_ts": 1758124800,
   "sale_date": "2025-09-18",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110127,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110127,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110122",
   "skin_id": 1110122,
   "name": "极限节拍",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 1,
   "weapon_type_label": "突击步枪（1）",
   "name_status": "verified",
   "sale_ts": 1755705600,
   "sale_date": "2025-08-21",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110122,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110122,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110123",
   "skin_id": 1110123,
   "name": "泰坦剑",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1755705600,
   "sale_date": "2025-08-21",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110123,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110123,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110121",
   "skin_id": 1110121,
   "name": "极狐破坏者",
   "name_source": "common_item",
   "grade_level": 5,
   "weapon_type": 6,
   "weapon_type_label": "手枪（6）",
   "name_status": "verified",
   "sale_ts": 1754928000,
   "sale_date": "2025-08-12",
   "has_item_row": true,
   "sfx_count": 4,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110121,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110121,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110126",
   "skin_id": 1110126,
   "name": "极狐终结刃",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1754928000,
   "sale_date": "2025-08-12",
   "has_item_row": true,
   "sfx_count": 1,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110126,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110126,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110124",
   "skin_id": 1110124,
   "name": "未来刻印",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 5,
   "weapon_type_label": "狙击枪（5）",
   "name_status": "verified",
   "sale_ts": 1753891200,
   "sale_date": "2025-07-31",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110124,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110124,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "11101241",
   "skin_id": 11101241,
   "name": "未来刻印（14天）",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 5,
   "weapon_type_label": "狙击枪（5）",
   "name_status": "verified",
   "sale_ts": 1753891200,
   "sale_date": "2025-07-31",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 11101241,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 11101241,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110125",
   "skin_id": 1110125,
   "name": "霓虹裂空",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 20,
   "weapon_type_label": "喷火器（20）",
   "name_status": "verified",
   "sale_ts": 1753891200,
   "sale_date": "2025-07-31",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110125,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110125,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110089",
   "skin_id": 1110089,
   "name": "粒子沙暴",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 6,
   "weapon_type_label": "手枪（6）",
   "name_status": "verified",
   "sale_ts": 1752768000,
   "sale_date": "2025-07-18",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110089,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110089,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110115",
   "skin_id": 1110115,
   "name": "赤月晶魄",
   "name_source": "common_item",
   "grade_level": 6,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1752768000,
   "sale_date": "2025-07-18",
   "has_item_row": true,
   "sfx_count": 7,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110115,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110115,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110116",
   "skin_id": 1110116,
   "name": "赤月晶魄",
   "name_source": "common_item",
   "grade_level": 6,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1752768000,
   "sale_date": "2025-07-18",
   "has_item_row": true,
   "sfx_count": 7,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110116,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110116,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110117",
   "skin_id": 1110117,
   "name": "赤月晶魄",
   "name_source": "common_item",
   "grade_level": 6,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1752768000,
   "sale_date": "2025-07-18",
   "has_item_row": true,
   "sfx_count": 7,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110117,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110117,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110118",
   "skin_id": 1110118,
   "name": "玫焰流华",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 7,
   "weapon_type_label": "榴弹炮（7）",
   "name_status": "verified",
   "sale_ts": 1752768000,
   "sale_date": "2025-07-18",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110118,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110118,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110119",
   "skin_id": 1110119,
   "name": "拟化磁星",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 8,
   "weapon_type_label": "电磁机枪（8）",
   "name_status": "verified",
   "sale_ts": 1752768000,
   "sale_date": "2025-07-18",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110119,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110119,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110120",
   "skin_id": 1110120,
   "name": "拟化磬翼",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 3,
   "weapon_type_label": "弓箭（3）",
   "name_status": "verified",
   "sale_ts": 1752768000,
   "sale_date": "2025-07-18",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110120,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110120,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110114",
   "skin_id": 1110114,
   "name": "像素涂鸦",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 1,
   "weapon_type_label": "突击步枪（1）",
   "name_status": "verified",
   "sale_ts": 1751472000,
   "sale_date": "2025-07-03",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110114,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110114,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "11101141",
   "skin_id": 11101141,
   "name": "像素涂鸦（30天）",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 1,
   "weapon_type_label": "突击步枪（1）",
   "name_status": "verified",
   "sale_ts": 1751472000,
   "sale_date": "2025-07-03",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 11101141,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 11101141,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110090",
   "skin_id": 1110090,
   "name": "心动狂飙",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 4,
   "weapon_type_label": "霰弹枪（4）",
   "name_status": "verified",
   "sale_ts": 1750867200,
   "sale_date": "2025-06-26",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110090,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110090,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "11100901",
   "skin_id": 11100901,
   "name": "心动狂飙（14天）",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 4,
   "weapon_type_label": "霰弹枪（4）",
   "name_status": "verified",
   "sale_ts": 1750867200,
   "sale_date": "2025-06-26",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 11100901,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 11100901,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110058",
   "skin_id": 1110058,
   "name": "黯夜乐手",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1747238400,
   "sale_date": "2025-05-15",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110058,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110058,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110035",
   "skin_id": 1110035,
   "name": "霓虹狂潮",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 4,
   "weapon_type_label": "霰弹枪（4）",
   "name_status": "verified",
   "sale_ts": 1745510400,
   "sale_date": "2025-04-25",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110035,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110035,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110036",
   "skin_id": 1110036,
   "name": "森林之主",
   "name_source": "common_item",
   "grade_level": 5,
   "weapon_type": 3,
   "weapon_type_label": "弓箭（3）",
   "name_status": "verified",
   "sale_ts": 1745510400,
   "sale_date": "2025-04-25",
   "has_item_row": true,
   "sfx_count": 8,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110036,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110036,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110034",
   "skin_id": 1110034,
   "name": "千蝶一梦",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 5,
   "weapon_type_label": "狙击枪（5）",
   "name_status": "verified",
   "sale_ts": 1744819200,
   "sale_date": "2025-04-17",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110034,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110034,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110030",
   "skin_id": 1110030,
   "name": "黄油裂镐",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1743004800,
   "sale_date": "2025-03-27",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110030,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110030,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110032",
   "skin_id": 1110032,
   "name": "九霄狐啸",
   "name_source": "common_item",
   "grade_level": 5,
   "weapon_type": 20,
   "weapon_type_label": "喷火器（20）",
   "name_status": "verified",
   "sale_ts": 1743004800,
   "sale_date": "2025-03-27",
   "has_item_row": true,
   "sfx_count": 5,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110032,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110032,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110033",
   "skin_id": 1110033,
   "name": "金芒裁决",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 3,
   "weapon_type_label": "弓箭（3）",
   "name_status": "verified",
   "sale_ts": 1743004800,
   "sale_date": "2025-03-27",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110033,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110033,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110031",
   "skin_id": 1110031,
   "name": "沧鳞破浪",
   "name_source": "common_item",
   "grade_level": 5,
   "weapon_type": 1,
   "weapon_type_label": "突击步枪（1）",
   "name_status": "verified",
   "sale_ts": 1741795200,
   "sale_date": "2025-03-13",
   "has_item_row": true,
   "sfx_count": 6,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110031,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110031,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110028",
   "skin_id": 1110028,
   "name": "玉华碎雪",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1740585600,
   "sale_date": "2025-02-27",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110028,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110028,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "11100281",
   "skin_id": 11100281,
   "name": "玉华碎雪（14天）",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1740585600,
   "sale_date": "2025-02-27",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 11100281,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 11100281,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110027",
   "skin_id": 1110027,
   "name": "猫猫出击",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 6,
   "weapon_type_label": "手枪（6）",
   "name_status": "verified",
   "sale_ts": 1739376000,
   "sale_date": "2025-02-13",
   "has_item_row": true,
   "sfx_count": 3,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110027,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110027,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "11100271",
   "skin_id": 11100271,
   "name": "猫猫出击（14天）",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 6,
   "weapon_type_label": "手枪（6）",
   "name_status": "verified",
   "sale_ts": 1739376000,
   "sale_date": "2025-02-13",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 11100271,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 11100271,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110141",
   "skin_id": 1110141,
   "name": "沙场点兵",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1738080000,
   "sale_date": "2025-01-29",
   "has_item_row": true,
   "sfx_count": 5,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110141,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110141,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110022",
   "skin_id": 1110022,
   "name": "赤蛇御火",
   "name_source": "common_item",
   "grade_level": 5,
   "weapon_type": 3,
   "weapon_type_label": "弓箭（3）",
   "name_status": "verified",
   "sale_ts": 1737561600,
   "sale_date": "2025-01-23",
   "has_item_row": true,
   "sfx_count": 7,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110022,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110022,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110023",
   "skin_id": 1110023,
   "name": "玉饮琼花",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 1,
   "weapon_type_label": "突击步枪（1）",
   "name_status": "verified",
   "sale_ts": 1737561600,
   "sale_date": "2025-01-23",
   "has_item_row": true,
   "sfx_count": 4,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110023,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110023,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "11100231",
   "skin_id": 11100231,
   "name": "玉饮琼花（14天）",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 1,
   "weapon_type_label": "突击步枪（1）",
   "name_status": "verified",
   "sale_ts": 1737561600,
   "sale_date": "2025-01-23",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 11100231,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 11100231,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110024",
   "skin_id": 1110024,
   "name": "金蟒啸焰",
   "name_source": "common_item",
   "grade_level": 5,
   "weapon_type": 4,
   "weapon_type_label": "霰弹枪（4）",
   "name_status": "verified",
   "sale_ts": 1737561600,
   "sale_date": "2025-01-23",
   "has_item_row": true,
   "sfx_count": 6,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110024,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110024,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110026",
   "skin_id": 1110026,
   "name": "祥鲤",
   "name_source": "common_item",
   "grade_level": 2,
   "weapon_type": 5,
   "weapon_type_label": "狙击枪（5）",
   "name_status": "verified",
   "sale_ts": 1737561600,
   "sale_date": "2025-01-23",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110026,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110026,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110019",
   "skin_id": 1110019,
   "name": "霓虹狂想",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 8,
   "weapon_type_label": "电磁机枪（8）",
   "name_status": "verified",
   "sale_ts": 1736352000,
   "sale_date": "2025-01-09",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110019,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110019,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110020",
   "skin_id": 1110020,
   "name": "掘墓锹",
   "name_source": "common_item",
   "grade_level": 2,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1736352000,
   "sale_date": "2025-01-09",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110020,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110020,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110021",
   "skin_id": 1110021,
   "name": "紫焰蛇矛",
   "name_source": "common_item",
   "grade_level": 5,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1736352000,
   "sale_date": "2025-01-09",
   "has_item_row": true,
   "sfx_count": 6,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110021,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110021,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110025",
   "skin_id": 1110025,
   "name": "冰蕊银华",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 4,
   "weapon_type_label": "霰弹枪（4）",
   "name_status": "verified",
   "sale_ts": 1736352000,
   "sale_date": "2025-01-09",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110025,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110025,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110016",
   "skin_id": 1110016,
   "name": "冬雪绮愿",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 6,
   "weapon_type_label": "手枪（6）",
   "name_status": "verified",
   "sale_ts": 1734537600,
   "sale_date": "2024-12-19",
   "has_item_row": true,
   "sfx_count": 3,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110016,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110016,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110017",
   "skin_id": 1110017,
   "name": "一支圣诞树",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1734537600,
   "sale_date": "2024-12-19",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110017,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110017,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110018",
   "skin_id": 1110018,
   "name": "冰城小霸王",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 20,
   "weapon_type_label": "喷火器（20）",
   "name_status": "verified",
   "sale_ts": 1734537600,
   "sale_date": "2024-12-19",
   "has_item_row": true,
   "sfx_count": 1,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110018,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110018,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110128",
   "skin_id": 1110128,
   "name": "诡秘之颅",
   "name_source": "common_item",
   "grade_level": 5,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1734537600,
   "sale_date": "2024-12-19",
   "has_item_row": true,
   "sfx_count": 6,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110128,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110128,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110013",
   "skin_id": 1110013,
   "name": "幻影狩蝎",
   "name_source": "common_item",
   "grade_level": 5,
   "weapon_type": 4,
   "weapon_type_label": "霰弹枪（4）",
   "name_status": "verified",
   "sale_ts": 1730908800,
   "sale_date": "2024-11-07",
   "has_item_row": true,
   "sfx_count": 6,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110013,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110013,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110014",
   "skin_id": 1110014,
   "name": "碎晶",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 3,
   "weapon_type_label": "弓箭（3）",
   "name_status": "verified",
   "sale_ts": 1730908800,
   "sale_date": "2024-11-07",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110014,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110014,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110015",
   "skin_id": 1110015,
   "name": "蓝火",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 7,
   "weapon_type_label": "榴弹炮（7）",
   "name_status": "verified",
   "sale_ts": 1730908800,
   "sale_date": "2024-11-07",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110015,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110015,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110011",
   "skin_id": 1110011,
   "name": "鎏金锐鹰",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 6,
   "weapon_type_label": "手枪（6）",
   "name_status": "verified",
   "sale_ts": 1729699200,
   "sale_date": "2024-10-24",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110011,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110011,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110010",
   "skin_id": 1110010,
   "name": "一镰幽梦",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1728489600,
   "sale_date": "2024-10-10",
   "has_item_row": true,
   "sfx_count": 3,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110010,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110010,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110007",
   "skin_id": 1110007,
   "name": "金箍棒",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1727452800,
   "sale_date": "2024-09-28",
   "has_item_row": true,
   "sfx_count": 1,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110007,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110007,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110008",
   "skin_id": 1110008,
   "name": "庆典绯梦",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 1,
   "weapon_type_label": "突击步枪（1）",
   "name_status": "verified",
   "sale_ts": 1727452800,
   "sale_date": "2024-09-28",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110008,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110008,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "11100081",
   "skin_id": 11100081,
   "name": "庆典绯梦（14天）",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 1,
   "weapon_type_label": "突击步枪（1）",
   "name_status": "verified",
   "sale_ts": 1727452800,
   "sale_date": "2024-09-28",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 11100081,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 11100081,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110009",
   "skin_id": 1110009,
   "name": "加油！少年",
   "name_source": "common_item",
   "grade_level": 2,
   "weapon_type": 7,
   "weapon_type_label": "榴弹炮（7）",
   "name_status": "verified",
   "sale_ts": 1727452800,
   "sale_date": "2024-09-28",
   "has_item_row": true,
   "sfx_count": 1,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110009,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110009,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110006",
   "skin_id": 1110006,
   "name": "傲隼睨视",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 5,
   "weapon_type_label": "狙击枪（5）",
   "name_status": "verified",
   "sale_ts": 1726156800,
   "sale_date": "2024-09-13",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110006,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110006,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "11100061",
   "skin_id": 11100061,
   "name": "傲隼睨视（14天）",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 5,
   "weapon_type_label": "狙击枪（5）",
   "name_status": "verified",
   "sale_ts": 1726156800,
   "sale_date": "2024-09-13",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 11100061,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 11100061,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110001",
   "skin_id": 1110001,
   "name": "鎏金锐魄",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 1,
   "weapon_type_label": "突击步枪（1）",
   "name_status": "verified",
   "sale_ts": 1724860800,
   "sale_date": "2024-08-29",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110001,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110001,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110002",
   "skin_id": 1110002,
   "name": "鎏金狙魂",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 5,
   "weapon_type_label": "狙击枪（5）",
   "name_status": "verified",
   "sale_ts": 1724860800,
   "sale_date": "2024-08-29",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110002,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110002,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110003",
   "skin_id": 1110003,
   "name": "鎏金锋刃",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": 1724860800,
   "sale_date": "2024-08-29",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110003,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110003,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110004",
   "skin_id": 1110004,
   "name": "萌豚霰击",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 4,
   "weapon_type_label": "霰弹枪（4）",
   "name_status": "verified",
   "sale_ts": 1724860800,
   "sale_date": "2024-08-29",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110004,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110004,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "11100041",
   "skin_id": 11100041,
   "name": "萌豚霰击（14天）",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 4,
   "weapon_type_label": "霰弹枪（4）",
   "name_status": "verified",
   "sale_ts": 1724860800,
   "sale_date": "2024-08-29",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 11100041,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 11100041,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110005",
   "skin_id": 1110005,
   "name": "深蓝之影",
   "name_source": "common_item",
   "grade_level": 2,
   "weapon_type": 6,
   "weapon_type_label": "手枪（6）",
   "name_status": "verified",
   "sale_ts": 1724860800,
   "sale_date": "2024-08-29",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110005,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110005,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110087",
   "skin_id": 1110087,
   "name": "彩虹过载",
   "name_source": "common_item",
   "grade_level": 4,
   "weapon_type": 7,
   "weapon_type_label": "榴弹炮（7）",
   "name_status": "verified",
   "sale_ts": null,
   "sale_date": "",
   "has_item_row": true,
   "sfx_count": 2,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110087,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110087,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  },
  {
   "id": "1110088",
   "skin_id": 1110088,
   "name": "全糖暴击",
   "name_source": "common_item",
   "grade_level": 3,
   "weapon_type": 50,
   "weapon_type_label": "冷兵器（50）",
   "name_status": "verified",
   "sale_ts": null,
   "sale_date": "",
   "has_item_row": true,
   "sfx_count": 0,
   "version_status": "无基线（不可比）",
   "evidence": "structure",
   "evidence_level": "structure-only",
   "status_tags": [
    "static config",
    "runtime final unknown"
   ],
   "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
   "provenance": {
    "source_id": "pe-client-script-npk",
    "table": "weapon_skin_data",
    "row_key": 1110088,
    "field_refs": [
     "name",
     "level",
     "weapon_type",
     "sale_ts"
    ],
    "name_source": "common_item_data#name",
    "locator_chain": {
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "pe-client-script-npk",
       "table": "weapon_skin_data",
       "row_key": 1110088,
       "field_refs": [
        "name",
        "level",
        "weapon_type",
        "sale_ts"
       ]
      }
     ],
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true
    },
    "source_lock_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
    "upstream": {
     "package_sha256": "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6",
     "entry_index": null,
     "file_id": null
    }
   }
  }
 ]
};
