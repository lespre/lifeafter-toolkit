window.WIKI_BOARD_future_lottery_preview = {
 "meta": {
  "name": "新奖池活动（未来档预告）",
  "category": "零、新更新与预告专栏（游戏未上线资源预告） / （2）新奖池活动",
  "source_server": "简单生存服",
  "package_sha": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
  "generated": "2026-09-24",
  "evidence": "structure",
  "notes": "BA8 快照（2026-09-10）中过期时间晚于快照日期的活动实例清单（时间窗至 2027-12）。含历史活动返场排期与未来新档；是否为测试服独有新内容需对照《明日之后完整历史更新汇总》逐条判定，本板不做该断言。已排除已发布主题（帝皇铠甲/铠甲再临/宸世臻藏等）与测试行。活动实例=广播活动名+expiration 聚类，池集合可能含跨活动共享行。",
  "provenance": {
   "contract_version": 3,
   "audit_status": "passed",
   "contract": "frozen-audited-artifact",
   "source_locks": [
    {
     "source_id": "future-lottery-preview-live-scan-adapter",
     "sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
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
   "unresolved": 36,
   "static config": 36,
   "verified": 0,
   "runtime final unknown": 36
  }
 },
 "items": [
  {
   "id": "樱灵狐梦-1789171199",
   "name": "樱灵狐梦",
   "activity": "樱灵狐梦",
   "instance_exp_date": "2026-09-12",
   "instance_exp_ts": 1789171199,
   "rows_in_window": 3,
   "pool_count": 3,
   "pools": [
    390530,
    391566,
    1221232
   ],
   "note_samples": [
    "樱灵狐梦",
    "心月狐",
    "幻樱狐尾"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 83343,
    "field_refs": [
     "reward_pool_data_base.key=83343",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 83343,
       "field_refs": [
        "reward_pool_data_base.key=83343",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "磁聚轰雷-1789257599",
   "name": "磁聚轰雷",
   "activity": "磁聚轰雷",
   "instance_exp_date": "2026-09-13",
   "instance_exp_ts": 1789257599,
   "rows_in_window": 18,
   "pool_count": 3,
   "pools": [
    391580,
    391828,
    391829
   ],
   "note_samples": [
    "盈樱春意背包礼盒",
    "密林树屋主题方案礼盒",
    "配方:仿生瞬豹霰弹枪",
    "配方:仿生深潜火箭筒"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 32967,
    "field_refs": [
     "reward_pool_data_base.key=32967",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 32967,
       "field_refs": [
        "reward_pool_data_base.key=32967",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "砂海遗珠-1790467199",
   "name": "砂海遗珠",
   "activity": "砂海遗珠",
   "instance_exp_date": "2026-09-27",
   "instance_exp_ts": 1790467199,
   "rows_in_window": 22,
   "pool_count": 6,
   "pools": [
    390566,
    390815,
    391595,
    391596,
    391615,
    660017
   ],
   "note_samples": [
    "涂装：黄袍",
    "双龙啸焰",
    "虎跃龙腾主题方案",
    "配方:仿生猎鲨锋刃"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 28459,
    "field_refs": [
     "reward_pool_data_base.key=28459",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 28459,
       "field_refs": [
        "reward_pool_data_base.key=28459",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "凝华效应-1791676799",
   "name": "凝华效应",
   "activity": "凝华效应",
   "instance_exp_date": "2026-10-11",
   "instance_exp_ts": 1791676799,
   "rows_in_window": 18,
   "pool_count": 4,
   "pools": [
    390590,
    390839,
    391639,
    391642
   ],
   "note_samples": [
    "配方:菌焰喷火器",
    "配方:仿生蛛螯步枪",
    "荷塘月色背包礼盒",
    "终焉之花主题方案"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 24501,
    "field_refs": [
     "reward_pool_data_base.key=24501",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 24501,
       "field_refs": [
        "reward_pool_data_base.key=24501",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "盛夏惠选-1792713599",
   "name": "盛夏惠选",
   "activity": "盛夏惠选",
   "instance_exp_date": "2026-10-23",
   "instance_exp_ts": 1792713599,
   "rows_in_window": 1,
   "pool_count": 1,
   "pools": [
    391745
   ],
   "note_samples": [
    "铠甲合体"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 12572,
    "field_refs": [
     "reward_pool_data_base.key=12572",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 12572,
       "field_refs": [
        "reward_pool_data_base.key=12572",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "学院企划-1792972799",
   "name": "学院企划",
   "activity": "学院企划",
   "instance_exp_date": "2026-10-26",
   "instance_exp_ts": 1792972799,
   "rows_in_window": 16,
   "pool_count": 3,
   "pools": [
    390608,
    390637,
    570009
   ],
   "note_samples": [
    "熊熊背包背包礼盒",
    "进化头盔自选箱",
    "学园·樱花信笺时装礼包",
    "涂装:巨蛇霰弹雨战版"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 65999,
    "field_refs": [
     "reward_pool_data_base.key=65999",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 65999,
       "field_refs": [
        "reward_pool_data_base.key=65999",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "溶蚀机枪-1792972799",
   "name": "溶蚀机枪",
   "activity": "溶蚀机枪",
   "instance_exp_date": "2026-10-26",
   "instance_exp_ts": 1792972799,
   "rows_in_window": 32,
   "pool_count": 5,
   "pools": [
    390424,
    390541,
    390553,
    390790,
    390802
   ],
   "note_samples": [
    "冰河旧梦主题方案礼盒",
    "涂装：银月白鸽",
    "涂装：青翼",
    "涂装：极光护卫"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 75397,
    "field_refs": [
     "reward_pool_data_base.key=75397",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 75397,
       "field_refs": [
        "reward_pool_data_base.key=75397",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "幻海旖旎-1794095999",
   "name": "幻海旖旎",
   "activity": "幻海旖旎",
   "instance_exp_date": "2026-11-08",
   "instance_exp_ts": 1794095999,
   "rows_in_window": 16,
   "pool_count": 7,
   "pools": [
    390625,
    390646,
    391437,
    391442,
    391687,
    391691,
    796345
   ],
   "note_samples": [
    "涂装:弧光电磁雪地版",
    "涂装:弧光电磁雨战版",
    "水母摆摆",
    "待取名"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 70617,
    "field_refs": [
     "reward_pool_data_base.key=70617",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 70617,
       "field_refs": [
        "reward_pool_data_base.key=70617",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "羊狼寻宝-1795305599",
   "name": "羊狼寻宝",
   "activity": "羊狼寻宝",
   "instance_exp_date": "2026-11-22",
   "instance_exp_ts": 1795305599,
   "rows_in_window": 9,
   "pool_count": 5,
   "pools": [
    390655,
    390897,
    391699,
    570238,
    1221341
   ],
   "note_samples": [
    "涂装:仿生蛛酶雨战版",
    "涂装:仿生蛛酶典藏版",
    "待取名",
    "战虎-皎月"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 17686,
    "field_refs": [
     "reward_pool_data_base.key=17686",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 17686,
       "field_refs": [
        "reward_pool_data_base.key=17686",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "夏日香氛-1796515199",
   "name": "夏日香氛",
   "activity": "夏日香氛",
   "instance_exp_date": "2026-12-06",
   "instance_exp_ts": 1796515199,
   "rows_in_window": 14,
   "pool_count": 3,
   "pools": [
    390413,
    390415,
    391467
   ],
   "note_samples": [
    "配方：疾风狡兔",
    "涂装：黑金",
    "进化头盔自选箱",
    "晴空泡泡"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 237495,
    "field_refs": [
     "reward_pool_data_base.key=237495",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 237495,
       "field_refs": [
        "reward_pool_data_base.key=237495",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "瞬豹弧光-1796515199",
   "name": "瞬豹弧光",
   "activity": "瞬豹弧光",
   "instance_exp_date": "2026-12-06",
   "instance_exp_ts": 1796515199,
   "rows_in_window": 18,
   "pool_count": 7,
   "pools": [
    390412,
    390661,
    390765,
    391264,
    391464,
    391538,
    391712
   ],
   "note_samples": [
    "青鸟号背包礼盒",
    "终焉之花主题方案",
    "涂装:弧光电磁雪地版",
    "配方:弧光电磁机枪"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 17042,
    "field_refs": [
     "reward_pool_data_base.key=17042",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 17042,
       "field_refs": [
        "reward_pool_data_base.key=17042",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "不湮之花-1797811199",
   "name": "不湮之花",
   "activity": "不湮之花",
   "instance_exp_date": "2026-12-21",
   "instance_exp_ts": 1797811199,
   "rows_in_window": 30,
   "pool_count": 13,
   "pools": [
    390421,
    390422,
    390428,
    390429,
    390670,
    390671,
    390677,
    390678,
    391473,
    391721,
    391722,
    391727,
    1110142
   ],
   "note_samples": [
    "兔随福至挂饰礼盒",
    "涂装:仿生火箭筒典藏版",
    "待取名",
    "待取名"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 14995,
    "field_refs": [
     "reward_pool_data_base.key=14995",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 14995,
       "field_refs": [
        "reward_pool_data_base.key=14995",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "无人机琉光晶蝶抽奖-1797811199",
   "name": "无人机琉光晶蝶抽奖",
   "activity": "无人机琉光晶蝶抽奖",
   "instance_exp_date": "2026-12-21",
   "instance_exp_ts": 1797811199,
   "rows_in_window": 26,
   "pool_count": 4,
   "pools": [
    390420,
    390664,
    390669,
    391472
   ],
   "note_samples": [
    "典藏涂装：碧辉",
    "涂装：绯影",
    "典藏涂装：碧辉",
    "涂装:流光"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 36423,
    "field_refs": [
     "reward_pool_data_base.key=36423",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 36423,
       "field_refs": [
        "reward_pool_data_base.key=36423",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "琥珀追猎-1798934399",
   "name": "琥珀追猎",
   "activity": "琥珀追猎",
   "instance_exp_date": "2027-01-03",
   "instance_exp_ts": 1798934399,
   "rows_in_window": 14,
   "pool_count": 4,
   "pools": [
    390435,
    390684,
    460260,
    460500
   ],
   "note_samples": [
    "蝶影左轮典藏版",
    "涂装:琥珀护臂典藏版",
    "蝶影左轮典藏版",
    "涂装:琥珀护臂雨战版"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 41481,
    "field_refs": [
     "reward_pool_data_base.key=41481",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 41481,
       "field_refs": [
        "reward_pool_data_base.key=41481",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "一溪风月-1799366399",
   "name": "一溪风月",
   "activity": "一溪风月",
   "instance_exp_date": "2027-01-08",
   "instance_exp_ts": 1799366399,
   "rows_in_window": 1,
   "pool_count": 1,
   "pools": [
    391577
   ],
   "note_samples": [
    "玉兔夜游船"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 268084,
    "field_refs": [
     "reward_pool_data_base.key=268084",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 268084,
       "field_refs": [
        "reward_pool_data_base.key=268084",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "夏夜派对-1799366399",
   "name": "夏夜派对",
   "activity": "夏夜派对",
   "instance_exp_date": "2027-01-08",
   "instance_exp_ts": 1799366399,
   "rows_in_window": 4,
   "pool_count": 6,
   "pools": [
    391591,
    391821,
    391824,
    660022,
    1221016,
    1221017
   ],
   "note_samples": [
    "星夜绮梦书",
    "星绮树",
    "星夜绮梦瓶",
    "绮境色彩"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 2976,
    "field_refs": [
     "reward_pool_data_base.key=2976",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 2976,
       "field_refs": [
        "reward_pool_data_base.key=2976",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "秋庄惠选-1799366399",
   "name": "秋庄惠选",
   "activity": "秋庄惠选",
   "instance_exp_date": "2027-01-08",
   "instance_exp_ts": 1799366399,
   "rows_in_window": 8,
   "pool_count": 7,
   "pools": [
    390584,
    390585,
    391029,
    391271,
    391576,
    391824,
    391825
   ],
   "note_samples": [
    "引蝶灯",
    "刀剑冢",
    "花影漂流亭",
    "舞影门楼"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 2684,
    "field_refs": [
     "reward_pool_data_base.key=2684",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 2684,
       "field_refs": [
        "reward_pool_data_base.key=2684",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "一溪风月-1799366400",
   "name": "一溪风月",
   "activity": "一溪风月",
   "instance_exp_date": "2027-01-08",
   "instance_exp_ts": 1799366400,
   "rows_in_window": 1,
   "pool_count": 1,
   "pools": [
    391577
   ],
   "note_samples": [
    "广寒清辉灯"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 267878,
    "field_refs": [
     "reward_pool_data_base.key=267878",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 267878,
       "field_refs": [
        "reward_pool_data_base.key=267878",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "一溪风月-1799366401",
   "name": "一溪风月",
   "activity": "一溪风月",
   "instance_exp_date": "2027-01-08",
   "instance_exp_ts": 1799366401,
   "rows_in_window": 1,
   "pool_count": 1,
   "pools": [
    391577
   ],
   "note_samples": [
    "悠闲采药小兔"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 268370,
    "field_refs": [
     "reward_pool_data_base.key=268370",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 268370,
       "field_refs": [
        "reward_pool_data_base.key=268370",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "一溪风月-1799366402",
   "name": "一溪风月",
   "activity": "一溪风月",
   "instance_exp_date": "2027-01-08",
   "instance_exp_ts": 1799366402,
   "rows_in_window": 1,
   "pool_count": 1,
   "pools": [
    391577
   ],
   "note_samples": [
    "认真捣药小兔"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 268240,
    "field_refs": [
     "reward_pool_data_base.key=268240",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 268240,
       "field_refs": [
        "reward_pool_data_base.key=268240",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "一溪风月-1799366403",
   "name": "一溪风月",
   "activity": "一溪风月",
   "instance_exp_date": "2027-01-08",
   "instance_exp_ts": 1799366403,
   "rows_in_window": 1,
   "pool_count": 1,
   "pools": [
    391577
   ],
   "note_samples": [
    "勤劳搬运小兔"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 267274,
    "field_refs": [
     "reward_pool_data_base.key=267274",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 267274,
       "field_refs": [
        "reward_pool_data_base.key=267274",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "暗夜蛛螯-1800143999",
   "name": "暗夜蛛螯",
   "activity": "暗夜蛛螯",
   "instance_exp_date": "2027-01-17",
   "instance_exp_ts": 1800143999,
   "rows_in_window": 10,
   "pool_count": 5,
   "pools": [
    390442,
    390691,
    391510,
    391511,
    640035
   ],
   "note_samples": [
    "冰河旧梦主题方案礼盒",
    "涂装：极光护卫",
    "涂装:仿生蛛螯雨战版",
    "配方:仿生蛛螯步枪"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 40258,
    "field_refs": [
     "reward_pool_data_base.key=40258",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 40258,
       "field_refs": [
        "reward_pool_data_base.key=40258",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "天赏石-1800403199",
   "name": "天赏石",
   "activity": "天赏石",
   "instance_exp_date": "2027-01-20",
   "instance_exp_ts": 1800403199,
   "rows_in_window": 4,
   "pool_count": 2,
   "pools": [
    390277,
    391329
   ],
   "note_samples": [
    "涂装：翡翠",
    "涂装：卧虎",
    "天蝎座",
    "待取名"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 626071,
    "field_refs": [
     "reward_pool_data_base.key=626071",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 626071,
       "field_refs": [
        "reward_pool_data_base.key=626071",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "喵不可言-1801353599",
   "name": "喵不可言",
   "activity": "喵不可言",
   "instance_exp_date": "2027-01-31",
   "instance_exp_ts": 1801353599,
   "rows_in_window": 18,
   "pool_count": 16,
   "pools": [
    390199,
    390257,
    390470,
    390483,
    390719,
    390732,
    391190,
    391522,
    391551,
    391659,
    391770,
    391771,
    391783,
    391784,
    470540,
    492500
   ],
   "note_samples": [
    "待取名",
    "银翼号背包礼盒",
    "白巧喵耳",
    "配方:狂沙镭蛇"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 7763,
    "field_refs": [
     "reward_pool_data_base.key=7763",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 7763,
       "field_refs": [
        "reward_pool_data_base.key=7763",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "弧光游隼-1801353599",
   "name": "弧光游隼",
   "activity": "弧光游隼",
   "instance_exp_date": "2027-01-31",
   "instance_exp_ts": 1801353599,
   "rows_in_window": 16,
   "pool_count": 10,
   "pools": [
    390353,
    390469,
    390676,
    390718,
    390976,
    391186,
    391218,
    391521,
    391767,
    391770
   ],
   "note_samples": [
    "奋进号背包",
    "配方:仿生游隼狙击枪",
    "涂装:弧光电磁雨战版",
    "涂装:弧光电磁典藏版"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 9793,
    "field_refs": [
     "reward_pool_data_base.key=9793",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 9793,
       "field_refs": [
        "reward_pool_data_base.key=9793",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "无人机模组信号猎手-1802563199",
   "name": "无人机模组信号猎手",
   "activity": "无人机模组信号猎手",
   "instance_exp_date": "2027-02-14",
   "instance_exp_ts": 1802563199,
   "rows_in_window": 32,
   "pool_count": 16,
   "pools": [
    390185,
    390203,
    390490,
    390538,
    390539,
    390665,
    390739,
    391012,
    391253,
    391302,
    391575,
    391636,
    391799,
    391807,
    391808,
    391825
   ],
   "note_samples": [
    "配方：无羁奔马",
    "涂装：黑金",
    "涂装：霜蹄",
    "涂装：黄袍"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 5794,
    "field_refs": [
     "reward_pool_data_base.key=5794",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 5794,
       "field_refs": [
        "reward_pool_data_base.key=5794",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "羊村伙伴-1808351999",
   "name": "羊村伙伴",
   "activity": "羊村伙伴",
   "instance_exp_date": "2027-04-22",
   "instance_exp_ts": 1808351999,
   "rows_in_window": 1,
   "pool_count": 2,
   "pools": [
    390903,
    391161
   ],
   "note_samples": [
    "遇到困难睡大觉摆件（SR+）"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 319262,
    "field_refs": [
     "reward_pool_data_base.key=319262",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 319262,
       "field_refs": [
        "reward_pool_data_base.key=319262",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "趴趴小宠-1808351999",
   "name": "趴趴小宠",
   "activity": "趴趴小宠",
   "instance_exp_date": "2027-04-22",
   "instance_exp_ts": 1808351999,
   "rows_in_window": 1,
   "pool_count": 2,
   "pools": [
    391407,
    1221154
   ],
   "note_samples": [
    "欧皇豹豹趴趴玩偶（SR+）"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 710338,
    "field_refs": [
     "reward_pool_data_base.key=710338",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 710338,
       "field_refs": [
        "reward_pool_data_base.key=710338",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "冬庄惠选-1809734399",
   "name": "冬庄惠选",
   "activity": "冬庄惠选",
   "instance_exp_date": "2027-05-08",
   "instance_exp_ts": 1809734399,
   "rows_in_window": 18,
   "pool_count": 13,
   "pools": [
    390254,
    390270,
    390272,
    390404,
    390405,
    390406,
    390909,
    390910,
    391199,
    391260,
    391261,
    391706,
    570245
   ],
   "note_samples": [
    "小雪人热气球SR",
    "落梅惊梦",
    "冷霜卧榻SR",
    "霜雪露鹿SSR"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 301618,
    "field_refs": [
     "reward_pool_data_base.key=301618",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 301618,
       "field_refs": [
        "reward_pool_data_base.key=301618",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "春苑惠选-1809734399",
   "name": "春苑惠选",
   "activity": "春苑惠选",
   "instance_exp_date": "2027-05-08",
   "instance_exp_ts": 1809734399,
   "rows_in_window": 18,
   "pool_count": 17,
   "pools": [
    390014,
    390200,
    390252,
    390264,
    390360,
    390526,
    390573,
    390575,
    390647,
    390700,
    390966,
    391095,
    391548,
    391565,
    391656,
    391797,
    580181
   ],
   "note_samples": [
    "仙踪落地钟",
    "仙踪奇境",
    "仙踪书架",
    "仙踪树洞床"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 83555,
    "field_refs": [
     "reward_pool_data_base.key=83555",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 83555,
       "field_refs": [
        "reward_pool_data_base.key=83555",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "初夏惠选-1816387199",
   "name": "初夏惠选",
   "activity": "初夏惠选",
   "instance_exp_date": "2027-07-24",
   "instance_exp_ts": 1816387199,
   "rows_in_window": 9,
   "pool_count": 10,
   "pools": [
    390624,
    390639,
    391434,
    391435,
    391682,
    391683,
    391684,
    570019,
    570020,
    1221295
   ],
   "note_samples": [
    "绿庭三角钢琴",
    "绿庭加冕王座",
    "海底水晶石",
    "纪念日舞台"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 19861,
    "field_refs": [
     "reward_pool_data_base.key=19861",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 19861,
       "field_refs": [
        "reward_pool_data_base.key=19861",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "幻夜神谕-1816646399",
   "name": "幻夜神谕",
   "activity": "幻夜神谕",
   "instance_exp_date": "2027-07-27",
   "instance_exp_ts": 1816646399,
   "rows_in_window": 31,
   "pool_count": 20,
   "pools": [
    390232,
    390738,
    391009,
    391011,
    391019,
    391036,
    391054,
    391572,
    391574,
    391582,
    391599,
    391774,
    391806,
    391820,
    391821,
    391831,
    391832,
    660076,
    1110185,
    633170140
   ],
   "note_samples": [
    "诸神精神病院装扮礼包",
    "奇迹",
    "幻夜星轮（倪克斯）",
    "迎春萌虎挂饰礼盒"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 4,
    "field_refs": [
     "reward_pool_data_base.key=4",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 4,
       "field_refs": [
        "reward_pool_data_base.key=4",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "神谕童话-1816646399",
   "name": "神谕童话",
   "activity": "神谕童话",
   "instance_exp_date": "2027-07-27",
   "instance_exp_ts": 1816646399,
   "rows_in_window": 1,
   "pool_count": 2,
   "pools": [
    390653,
    391571
   ],
   "note_samples": [
    "炽天之冕"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 77382,
    "field_refs": [
     "reward_pool_data_base.key=77382",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 77382,
       "field_refs": [
        "reward_pool_data_base.key=77382",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "青春变奏曲-1816646399",
   "name": "青春变奏曲",
   "activity": "青春变奏曲",
   "instance_exp_date": "2027-07-27",
   "instance_exp_ts": 1816646399,
   "rows_in_window": 18,
   "pool_count": 6,
   "pools": [
    390678,
    391023,
    391580,
    391815,
    391819,
    660069
   ],
   "note_samples": [
    "配方:灵鼠守卫",
    "手枪盾牌雪地自选",
    "手枪盾牌雨战自选",
    "青春变奏曲自选箱"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 4770,
    "field_refs": [
     "reward_pool_data_base.key=4770",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 4770,
       "field_refs": [
        "reward_pool_data_base.key=4770",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "临渊对决-1819583999",
   "name": "临渊对决",
   "activity": "临渊对决",
   "instance_exp_date": "2027-08-30",
   "instance_exp_ts": 1819583999,
   "rows_in_window": 11,
   "pool_count": 4,
   "pools": [
    390425,
    390674,
    570057,
    570060
   ],
   "note_samples": [
    "涂装:獠牙",
    "涂装:流光",
    "涂装:菌焰喷火器雪地版",
    "涂装:赤影"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 51990,
    "field_refs": [
     "reward_pool_data_base.key=51990",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 51990,
       "field_refs": [
        "reward_pool_data_base.key=51990",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  },
  {
   "id": "盛夏惠选-1824249599",
   "name": "盛夏惠选",
   "activity": "盛夏惠选",
   "instance_exp_date": "2027-10-23",
   "instance_exp_ts": 1824249599,
   "rows_in_window": 14,
   "pool_count": 11,
   "pools": [
    390426,
    390458,
    390675,
    390678,
    391191,
    391494,
    391496,
    391511,
    391742,
    391743,
    391744
   ],
   "note_samples": [
    "浪漫紫藤树",
    "浪漫紫藤树",
    "云海鲜花船",
    "云海瀑布"
   ],
   "evidence": "structure",
   "evidence_level": "structure-only",
   "source": "reward_pool_data_base rows with future expiration broadcast 该活动名；活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属",
   "provenance": {
    "source_lock_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
    "source_entries": [
     {
      "entry_index": 25636,
      "file_id": "D558884A36C972C5",
      "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
      "role": "reward_base"
     },
     {
      "entry_index": 12708,
      "file_id": "69E58821939CB515",
      "decoded_sha256": "4476b10fd1293978d4ecce5caf777bb7f2da09c631cd5b94dbdb6f7b527b1113",
      "role": "reward_chs"
     }
    ],
    "table": "reward_pool_data_base",
    "row_key": 13429,
    "field_refs": [
     "reward_pool_data_base.key=13429",
     "reward_pool_data_base.broadcast_content",
     "reward_pool_data_base.expiration_time",
     "reward_pool_data_base.reward"
    ],
    "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
    "source_id": "future-lottery-preview-live-scan-adapter",
    "upstream": {
     "package_sha256": "cb85b4d1ed44b2e0a47af7e9ea947dc0065120d69f758933b8149576deb20ac8",
     "entry_index": 25636,
     "file_id": "D558884A36C972C5",
     "decoded_sha256": "22be75ba5f2c274a3bdf42b2260db325ac83230971f578a63bd5fe8b48ca74a2",
     "role": "reward_base"
    },
    "locator_chain": {
     "chain_status": "replayed-structural",
     "scope": "record",
     "no_cross_source_field_join": true,
     "steps": [
      {
       "kind": "decoded-table-row",
       "source_id": "future-lottery-preview-live-scan-adapter",
       "table": "reward_pool_data_base",
       "row_key": 13429,
       "field_refs": [
        "reward_pool_data_base.key=13429",
        "reward_pool_data_base.broadcast_content",
        "reward_pool_data_base.expiration_time",
        "reward_pool_data_base.reward"
       ]
      }
     ]
    }
   },
   "status_tags": [
    "unresolved",
    "static config"
   ]
  }
 ],
 "stats": {
  "activity_instances": 36,
  "unbound_rows": 0
 }
};
