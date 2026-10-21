window.WIKI_BOARD_lottery_emperor_panel_static = {
  "meta": {
    "name": "帝皇铠甲（一期） · 双分支定位",
    "category": "四、奖池 / （一）抽奖、转盘、不放回抽奖",
    "source_server": "双分支：经典服=super_fashion 主表 key223/224/230（与正式服同 FID）；简单生存服=BA8 kj1 覆盖 key224/230",
    "package_sha": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
    "generated": "2026-09-06",
    "evidence": "structure",
    "notes": "帝皇铠甲（一期）双分支定位，与二期（刑天/飞影）板隔离。实例 cohort=广播「帝皇铠甲活动」+exp 2027-01-17（1800143999）。主表（两服同 FID）key223/224/230 → 391513/391514/391762；BA8 kj1 覆盖 key224/230 → 391535/391767（key223 无 kj1 行）。孤儿候选池 390699/390716/391760/660078 有帝皇广播行但无配置行引用。无用户验收锚点：不宣称任何池为当前发奖池；prob 均来自 prob_note 配置原文；极光盾/帝皇腰带未在此轮池行命中。",
    "provenance": {
      "audit_status": "passed",
      "source_locks": [
        {
          "sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
          "bytes": 270106156,
          "mtime_ns": 1788266451099903500,
          "path_hint": "mrzh/Documents/script.py314.lc.npk (simple-survival test snapshot)"
        }
      ]
    }
  },
  "items": [
    {
      "id": "emperor-classic",
      "name": "帝皇铠甲 · 经典服分支",
      "activity": "帝皇铠甲（一期）",
      "server_branch": "经典服",
      "branch_source": "super_fashion_lottery_conf_data 主表 key223/224/230（与正式服包同 FID 7E5A5A83B1F07D31=同一文件）",
      "panel_rows": 0,
      "rewards": [],
      "pools": [
        {
          "pool_id": 391513,
          "name": "lottery 池（主表 key223 引用；帝皇期 7 行）",
          "rows": [
            {
              "slot": 0,
              "name": "涂装：极光护卫",
              "display_name": "涂装：极光护卫",
              "source_internal_marker": "涂装：极光护卫",
              "prob": 0.00197,
              "prob_note": "0.00197",
              "config_exp": "2027-01-17",
              "item_id": 103020,
              "quantity": 1,
              "leaf": [
                103020,
                1
              ],
              "broadcast_content": "恭喜{0}鸿运当头，在帝皇铠甲活动中获得{1:format_item_name}",
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 455166,
                "pool_slot_encoding": {
                  "blob_offset": 455208,
                  "bytes": "270102d9f217"
                },
                "field_refs": [
                  "reward_pool_data_base.key=455166",
                  "pool_id=391513 slot=0",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 1,
              "name": "涂装:仿生蛛螯典藏版",
              "display_name": "涂装:仿生蛛螯典藏版",
              "source_internal_marker": "涂装:仿生蛛螯典藏版",
              "prob": 0.0018,
              "prob_note": "0.0018",
              "config_exp": "2027-01-17",
              "item_id": 105743,
              "quantity": 1,
              "leaf": [
                105743,
                1
              ],
              "broadcast_content": "恭喜{0}鸿运当头，在帝皇铠甲活动中获得{1:format_item_name}",
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 118959,
                "pool_slot_encoding": {
                  "blob_offset": 119002,
                  "bytes": "270102d9f217"
                },
                "field_refs": [
                  "reward_pool_data_base.key=118959",
                  "pool_id=391513 slot=1",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 2,
              "name": "配方:医疗无人机",
              "display_name": "配方:医疗无人机",
              "source_internal_marker": "配方:医疗无人机",
              "prob": 0.00577,
              "prob_note": "0.00577",
              "config_exp": "2027-01-17",
              "item_id": 103018,
              "quantity": 1,
              "leaf": [
                103018,
                1
              ],
              "broadcast_content": "恭喜{0}鸿运当头，在帝皇铠甲活动中获得{1:format_item_name}",
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 119040,
                "pool_slot_encoding": {
                  "blob_offset": 119076,
                  "bytes": "270102d9f217"
                },
                "field_refs": [
                  "reward_pool_data_base.key=119040",
                  "pool_id=391513 slot=2",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 3,
              "name": "涂装:仿生蛛螯雨战版",
              "display_name": "涂装:仿生蛛螯雨战版",
              "source_internal_marker": "涂装:仿生蛛螯雨战版",
              "prob": 0.00206,
              "prob_note": "0.00206",
              "config_exp": "2027-01-17",
              "item_id": 105741,
              "quantity": 1,
              "leaf": [
                105741,
                1
              ],
              "broadcast_content": "恭喜{0}鸿运当头，在帝皇铠甲活动中获得{1:format_item_name}",
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 119115,
                "pool_slot_encoding": {
                  "blob_offset": 119156,
                  "bytes": "270102d9f217"
                },
                "field_refs": [
                  "reward_pool_data_base.key=119115",
                  "pool_id=391513 slot=3",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 5,
              "name": "典藏涂装：暗夜精灵",
              "display_name": "典藏涂装：暗夜精灵",
              "source_internal_marker": "典藏涂装：暗夜精灵",
              "prob": 0.00157,
              "prob_note": "0.00157",
              "config_exp": "2027-01-17",
              "item_id": 103087,
              "quantity": 1,
              "leaf": [
                103087,
                1
              ],
              "broadcast_content": "恭喜{0}鸿运当头，在帝皇铠甲活动中获得{1:format_item_name}",
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 454806,
                "pool_slot_encoding": {
                  "blob_offset": 454853,
                  "bytes": "270102d9f217"
                },
                "field_refs": [
                  "reward_pool_data_base.key=454806",
                  "pool_id=391513 slot=5",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 6,
              "name": "待取名",
              "display_name": "待取名",
              "source_internal_marker": "待取名",
              "prob": 0.02084,
              "prob_note": "0.02084",
              "config_exp": "2027-01-17",
              "item_id": 391763,
              "quantity": 1,
              "leaf": [
                391763,
                1
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 454186,
                "pool_slot_encoding": {
                  "blob_offset": 454234,
                  "bytes": "270102d9f217"
                },
                "field_refs": [
                  "reward_pool_data_base.key=454186",
                  "pool_id=391513 slot=6",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 7,
              "name": "涂装：银月白鸽",
              "display_name": "涂装：银月白鸽",
              "source_internal_marker": "涂装：银月白鸽",
              "prob": 0.00375,
              "prob_note": "0.00375",
              "config_exp": "2027-01-17",
              "item_id": 103019,
              "quantity": 1,
              "leaf": [
                103019,
                1
              ],
              "broadcast_content": "恭喜{0}鸿运当头，在帝皇铠甲活动中获得{1:format_item_name}",
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 454401,
                "pool_slot_encoding": {
                  "blob_offset": 454443,
                  "bytes": "270102d9f217"
                },
                "field_refs": [
                  "reward_pool_data_base.key=454401",
                  "pool_id=391513 slot=7",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            }
          ]
        },
        {
          "pool_id": 391514,
          "name": "lottery 池（主表 key224 引用；帝皇期 6 行；含帝皇铠甲/铠骑/极光剑/战翼交易盒）",
          "rows": [
            {
              "slot": 1,
              "name": "帝皇铠骑交易盒",
              "display_name": "帝皇铠骑交易盒",
              "source_internal_marker": "帝皇铠骑交易盒",
              "prob": 0.13333,
              "prob_note": "0.13333",
              "config_exp": "2027-01-17",
              "item_id": 139262,
              "quantity": 1,
              "leaf": [
                139262,
                1
              ],
              "broadcast_content": "恭喜{0}鸿运当头，在帝皇铠甲活动中获得{1:format_item_name}",
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 300220,
                "pool_slot_encoding": {
                  "blob_offset": 300277,
                  "bytes": "270102daf217"
                },
                "field_refs": [
                  "reward_pool_data_base.key=300220",
                  "pool_id=391514 slot=1",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 10,
              "name": "异变核芯-电极效应",
              "display_name": "异变核芯-电极效应",
              "source_internal_marker": "异变核芯-电极效应",
              "prob": 0.27331,
              "prob_note": "0.27331",
              "config_exp": "2027-01-17",
              "item_id": 660066,
              "quantity": 1,
              "leaf": [
                660066,
                1
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 531271,
                "pool_slot_encoding": {
                  "blob_offset": 531302,
                  "bytes": "270102daf217"
                },
                "field_refs": [
                  "reward_pool_data_base.key=531271",
                  "pool_id=391514 slot=10",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 12,
              "name": "极光剑交易盒",
              "display_name": "极光剑交易盒",
              "source_internal_marker": "极光剑交易盒",
              "prob": 0.20833,
              "prob_note": "0.20833",
              "config_exp": "2027-01-17",
              "item_id": 139263,
              "quantity": 1,
              "leaf": [
                139263,
                1
              ],
              "broadcast_content": "恭喜{0}鸿运当头，在帝皇铠甲活动中获得{1:format_item_name}",
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 495171,
                "pool_slot_encoding": {
                  "blob_offset": 495227,
                  "bytes": "270102daf217"
                },
                "field_refs": [
                  "reward_pool_data_base.key=495171",
                  "pool_id=391514 slot=12",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 13,
              "name": "异变核芯-凝华效应",
              "display_name": "异变核芯-凝华效应",
              "source_internal_marker": "异变核芯-凝华效应",
              "prob": 0.22776,
              "prob_note": "0.22776",
              "config_exp": "2027-01-17",
              "item_id": 660078,
              "quantity": 1,
              "leaf": [
                660078,
                1
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 495032,
                "pool_slot_encoding": {
                  "blob_offset": 495063,
                  "bytes": "270102daf217"
                },
                "field_refs": [
                  "reward_pool_data_base.key=495032",
                  "pool_id=391514 slot=13",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 14,
              "name": "帝皇铠甲交易盒",
              "display_name": "帝皇铠甲交易盒",
              "source_internal_marker": "帝皇铠甲交易盒",
              "prob": 0.14815,
              "prob_note": "0.14815",
              "config_exp": "2027-01-17",
              "item_id": 139261,
              "quantity": 1,
              "leaf": [
                139261,
                1
              ],
              "broadcast_content": "恭喜{0}鸿运当头，在帝皇铠甲活动中获得{1:format_item_name}",
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 424558,
                "pool_slot_encoding": {
                  "blob_offset": 424629,
                  "bytes": "270102daf217"
                },
                "field_refs": [
                  "reward_pool_data_base.key=424558",
                  "pool_id=391514 slot=14",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 15,
              "name": "帝皇战翼交易盒",
              "display_name": "帝皇战翼交易盒",
              "source_internal_marker": "帝皇战翼交易盒",
              "prob": 0.00911,
              "prob_note": "0.00911",
              "config_exp": "2027-01-17",
              "item_id": 139264,
              "quantity": 1,
              "leaf": [
                139264,
                1
              ],
              "broadcast_content": "恭喜{0}鸿运当头，在帝皇铠甲活动中获得{1:format_item_name}",
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 495388,
                "pool_slot_encoding": {
                  "blob_offset": 495432,
                  "bytes": "270102daf217"
                },
                "field_refs": [
                  "reward_pool_data_base.key=495388",
                  "pool_id=391514 slot=15",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            }
          ]
        },
        {
          "pool_id": 391762,
          "name": "lottery 池（主表 key230 引用；帝皇期 18 行；含帝皇裁决/瑞昭交易盒+普通奖励完整结构）",
          "rows": [
            {
              "slot": 6,
              "name": "配方:仿生蛛螯步枪",
              "display_name": "配方:仿生蛛螯步枪",
              "source_internal_marker": "配方:仿生蛛螯步枪",
              "prob": 0.0125,
              "prob_note": "0.0125",
              "config_exp": "2027-01-17",
              "item_id": 105740,
              "quantity": 1,
              "leaf": [
                105740,
                1
              ],
              "broadcast_content": "恭喜{0}鸿运当头，在帝皇铠甲活动中获得{1:format_item_name}",
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 5470,
                "pool_slot_encoding": {
                  "blob_offset": 5517,
                  "bytes": "270102d2f417"
                },
                "field_refs": [
                  "reward_pool_data_base.key=5470",
                  "pool_id=391762 slot=6",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 8,
              "name": "异变核芯-电极效应",
              "display_name": "异变核芯-电极效应",
              "source_internal_marker": "异变核芯-电极效应",
              "prob": 0.00208,
              "prob_note": "0.00208",
              "config_exp": "2027-01-17",
              "item_id": 660066,
              "quantity": 1,
              "leaf": [
                660066,
                1
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 5426,
                "pool_slot_encoding": {
                  "blob_offset": 5470,
                  "bytes": "270102d2f417"
                },
                "field_refs": [
                  "reward_pool_data_base.key=5426",
                  "pool_id=391762 slot=8",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 9,
              "name": "异变核芯-凝华效应",
              "display_name": "异变核芯-凝华效应",
              "source_internal_marker": "异变核芯-凝华效应",
              "prob": 0.00208,
              "prob_note": "0.00208",
              "config_exp": "2027-01-17",
              "item_id": 660078,
              "quantity": 1,
              "leaf": [
                660078,
                1
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 5382,
                "pool_slot_encoding": {
                  "blob_offset": 5426,
                  "bytes": "270102d2f417"
                },
                "field_refs": [
                  "reward_pool_data_base.key=5382",
                  "pool_id=391762 slot=9",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 10,
              "name": "银翼号背包礼盒",
              "display_name": "银翼号背包礼盒",
              "source_internal_marker": "银翼号背包礼盒",
              "prob": 0.00417,
              "prob_note": "0.00417",
              "config_exp": "2027-01-17",
              "item_id": 131216,
              "quantity": 1,
              "leaf": [
                131216,
                1
              ],
              "broadcast_content": "恭喜{0}鸿运当头，在帝皇铠甲活动中获得{1:format_item_name}",
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 30648,
                "pool_slot_encoding": {
                  "blob_offset": 5382,
                  "bytes": "270102d2f417"
                },
                "field_refs": [
                  "reward_pool_data_base.key=30648",
                  "pool_id=391762 slot=10",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 11,
              "name": "帝皇裁决交易盒",
              "display_name": "帝皇裁决交易盒",
              "source_internal_marker": "帝皇裁决交易盒",
              "prob": 0.0067,
              "prob_note": "0.0067",
              "config_exp": "2027-01-17",
              "item_id": 139265,
              "quantity": 1,
              "leaf": [
                139265,
                1
              ],
              "broadcast_content": "恭喜{0}鸿运当头，在帝皇铠甲活动中获得{1:format_item_name}",
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 5291,
                "pool_slot_encoding": {
                  "blob_offset": 5340,
                  "bytes": "270102d2f417"
                },
                "field_refs": [
                  "reward_pool_data_base.key=5291",
                  "pool_id=391762 slot=11",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 12,
              "name": "帝皇瑞昭交易盒",
              "display_name": "帝皇瑞昭交易盒",
              "source_internal_marker": "帝皇瑞昭交易盒",
              "prob": 0.0067,
              "prob_note": "0.0067",
              "config_exp": "2027-01-17",
              "item_id": 139266,
              "quantity": 1,
              "leaf": [
                139266,
                1
              ],
              "broadcast_content": "恭喜{0}鸿运当头，在帝皇铠甲活动中获得{1:format_item_name}",
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 5236,
                "pool_slot_encoding": {
                  "blob_offset": 5291,
                  "bytes": "270102d2f417"
                },
                "field_refs": [
                  "reward_pool_data_base.key=5236",
                  "pool_id=391762 slot=12",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 13,
              "name": "待取名",
              "display_name": "待取名",
              "source_internal_marker": "待取名",
              "prob": 0.01875,
              "prob_note": "0.01875",
              "config_exp": "2027-01-17",
              "item_id": 139277,
              "quantity": 1,
              "leaf": [
                139277,
                1
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 29189,
                "pool_slot_encoding": {
                  "blob_offset": 5236,
                  "bytes": "270102d2f417"
                },
                "field_refs": [
                  "reward_pool_data_base.key=29189",
                  "pool_id=391762 slot=13",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 14,
              "name": "能量电池",
              "display_name": "能量电池",
              "source_internal_marker": "能量电池",
              "prob": 0.01384,
              "prob_note": "0.01384",
              "config_exp": "2027-01-17",
              "item_id": 151994,
              "quantity": 10,
              "leaf": [
                151994,
                10
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 5143,
                "pool_slot_encoding": {
                  "blob_offset": 5190,
                  "bytes": "270102d2f417"
                },
                "field_refs": [
                  "reward_pool_data_base.key=5143",
                  "pool_id=391762 slot=14",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 15,
              "name": "稀有微晶",
              "display_name": "稀有微晶",
              "source_internal_marker": "稀有微晶",
              "prob": 0.01471,
              "prob_note": "0.01471",
              "config_exp": "2027-01-17",
              "item_id": 151646,
              "quantity": 100,
              "leaf": [
                151646,
                100
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 5099,
                "pool_slot_encoding": {
                  "blob_offset": 5143,
                  "bytes": "270102d2f417"
                },
                "field_refs": [
                  "reward_pool_data_base.key=5099",
                  "pool_id=391762 slot=15",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 16,
              "name": "1型记忆材料",
              "display_name": "1型记忆材料",
              "source_internal_marker": "1型记忆材料",
              "prob": 0.01471,
              "prob_note": "0.01471",
              "config_exp": "2027-01-17",
              "item_id": 151784,
              "quantity": 5,
              "leaf": [
                151784,
                5
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 5060,
                "pool_slot_encoding": {
                  "blob_offset": 5099,
                  "bytes": "270102d2f417"
                },
                "field_refs": [
                  "reward_pool_data_base.key=5060",
                  "pool_id=391762 slot=16",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 17,
              "name": "稀有微晶",
              "display_name": "稀有微晶",
              "source_internal_marker": "稀有微晶",
              "prob": 0.02586,
              "prob_note": "0.02586",
              "config_exp": "2027-01-17",
              "item_id": 151646,
              "quantity": 100,
              "leaf": [
                151646,
                100
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 5023,
                "pool_slot_encoding": {
                  "blob_offset": 5060,
                  "bytes": "270102d2f417"
                },
                "field_refs": [
                  "reward_pool_data_base.key=5023",
                  "pool_id=391762 slot=17",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 18,
              "name": "1型记忆材料",
              "display_name": "1型记忆材料",
              "source_internal_marker": "1型记忆材料",
              "prob": 0.02586,
              "prob_note": "0.02586",
              "config_exp": "2027-01-17",
              "item_id": 151784,
              "quantity": 5,
              "leaf": [
                151784,
                5
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 4986,
                "pool_slot_encoding": {
                  "blob_offset": 5023,
                  "bytes": "270102d2f417"
                },
                "field_refs": [
                  "reward_pool_data_base.key=4986",
                  "pool_id=391762 slot=18",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 19,
              "name": "配方残页",
              "display_name": "配方残页",
              "source_internal_marker": "配方残页",
              "prob": 0.11618,
              "prob_note": "0.11618",
              "config_exp": "2027-01-17",
              "item_id": 150059,
              "quantity": 20,
              "leaf": [
                150059,
                20
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 4948,
                "pool_slot_encoding": {
                  "blob_offset": 4986,
                  "bytes": "270102d2f417"
                },
                "field_refs": [
                  "reward_pool_data_base.key=4948",
                  "pool_id=391762 slot=19",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 20,
              "name": "配方残页",
              "display_name": "配方残页",
              "source_internal_marker": "配方残页",
              "prob": 0.11618,
              "prob_note": "0.11618",
              "config_exp": "2027-01-17",
              "item_id": 150059,
              "quantity": 20,
              "leaf": [
                150059,
                20
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 4948,
                "pool_slot_encoding": {
                  "blob_offset": 4979,
                  "bytes": "270102d2f417"
                },
                "field_refs": [
                  "reward_pool_data_base.key=4948",
                  "pool_id=391762 slot=20",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 21,
              "name": "配方残页",
              "display_name": "配方残页",
              "source_internal_marker": "配方残页",
              "prob": 0.23235,
              "prob_note": "0.23235",
              "config_exp": "2027-01-17",
              "item_id": 150059,
              "quantity": 10,
              "leaf": [
                150059,
                10
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 4917,
                "pool_slot_encoding": {
                  "blob_offset": 4948,
                  "bytes": "270102d2f417"
                },
                "field_refs": [
                  "reward_pool_data_base.key=4917",
                  "pool_id=391762 slot=21",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 22,
              "name": "纳米塑材自选箱",
              "display_name": "纳米塑材自选箱",
              "source_internal_marker": "纳米塑材自选箱",
              "prob": 0.14522,
              "prob_note": "0.14522",
              "config_exp": "2027-01-17",
              "item_id": 240116,
              "quantity": 1,
              "leaf": [
                240116,
                1
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 4878,
                "pool_slot_encoding": {
                  "blob_offset": 4917,
                  "bytes": "270102d2f417"
                },
                "field_refs": [
                  "reward_pool_data_base.key=4878",
                  "pool_id=391762 slot=22",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 23,
              "name": "待取名",
              "display_name": "待取名",
              "source_internal_marker": "待取名",
              "prob": 0.07435,
              "prob_note": "0.07435",
              "config_exp": "2027-01-17",
              "item_id": 241006,
              "quantity": 1,
              "leaf": [
                241006,
                1
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 4847,
                "pool_slot_encoding": {
                  "blob_offset": 4878,
                  "bytes": "270102d2f417"
                },
                "field_refs": [
                  "reward_pool_data_base.key=4847",
                  "pool_id=391762 slot=23",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 24,
              "name": "待取名",
              "display_name": "待取名",
              "source_internal_marker": "待取名",
              "prob": 0.17211,
              "prob_note": "0.17211",
              "config_exp": "2027-01-17",
              "item_id": 241007,
              "quantity": 1,
              "leaf": [
                241007,
                1
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 4816,
                "pool_slot_encoding": {
                  "blob_offset": 4847,
                  "bytes": "270102d2f417"
                },
                "field_refs": [
                  "reward_pool_data_base.key=4816",
                  "pool_id=391762 slot=24",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            }
          ]
        }
      ],
      "activity_pool_refs": [
        {
          "pool_id": 391513,
          "role": "lottery_id(主表 key223)",
          "status": "referenced",
          "note": "帝皇期实例行 exp 2027-01-17；含待取名 leaf 391763（帝皇铠甲本体候选，39xxxx 触发物）"
        },
        {
          "pool_id": 391514,
          "role": "lottery_id(主表 key224)",
          "status": "referenced",
          "note": "帝皇铠甲/铠骑/极光剑/战翼 4 交易盒在此池；主表面板 [106427,105276,241867,131216] 与池内容部分重叠=复用池多活动共享行，档位未逐行对齐"
        },
        {
          "pool_id": 391762,
          "role": "lottery_id(主表 key230)",
          "status": "referenced",
          "note": "fortune_bag_dct jump:342 -> {335:391764}；391764 帝皇期仅 1 行且广播=宸世臻藏（青龙涂装）→ fortune 指向非帝皇内容，语义待续"
        },
        {
          "pool_id": 391764,
          "role": "fortune_bag_dct(主表 key230)={335:391764}",
          "status": "unresolved",
          "note": "指向宸世臻藏青龙池；不是帝皇内容池，勿当帝皇福袋"
        }
      ],
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "classic branch = main config row chain; no user anchor for phase 1; activation and complete odds are not claimed",
      "provenance": {
        "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
        "source_entries": [
          {
            "entry_index": 12591,
            "file_id": "7E5A5A83B1F07D31",
            "decoded_sha256": "fb03a5e22ec85e42e4ed5ddcccff33b081cd6d8d04265a07205d3b4490d8ce8a",
            "role": "super_base"
          },
          {
            "entry_index": 7953,
            "file_id": "512C733C3B263D37",
            "decoded_sha256": "e2fef4b7cb187584639699ec9c8b7548adf197f35610bc3d2626fff88fb8a6a7",
            "role": "super_chs"
          },
          {
            "entry_index": 21380,
            "file_id": "D558884A36C972C5",
            "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
            "role": "reward_base"
          },
          {
            "entry_index": 10496,
            "file_id": "69E58821939CB515",
            "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
            "role": "reward_chs"
          }
        ],
        "table": "super_fashion_lottery_conf_data + reward_pool_data_base",
        "row_key": "223/224/230",
        "field_refs": [
          "super_fashion key223.lottery_id=391513",
          "super_fashion key224.lottery_id=391514",
          "super_fashion key230.lottery_id=391762",
          "reward_pool pools 391513/391514/391762 rows exp=1800143999"
        ],
        "name_source": "reward note as source_internal_marker"
      }
    },
    {
      "id": "emperor-simple",
      "name": "帝皇铠甲 · 简单生存服分支",
      "activity": "帝皇铠甲（一期）",
      "server_branch": "简单生存服",
      "branch_source": "BA8 专属 kj1/kjxq 覆盖通道 key224/230（正式服包无此变体；key223 无 kj1 行）",
      "panel_rows": 0,
      "rewards": [],
      "pools": [
        {
          "pool_id": 391535,
          "name": "lottery 池（kj1 key224 引用；帝皇期 4 行）",
          "rows": [
            {
              "slot": 2,
              "name": "帝皇铠甲交易盒",
              "display_name": "帝皇铠甲交易盒",
              "source_internal_marker": "帝皇铠甲交易盒",
              "prob": 0.15686,
              "prob_note": "0.15686",
              "config_exp": "2027-01-17",
              "item_id": 139261,
              "quantity": 1,
              "leaf": [
                139261,
                1
              ],
              "broadcast_content": "恭喜{0}鸿运当头，在帝皇铠甲活动中获得{1:format_item_name}",
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 457634,
                "pool_slot_encoding": {
                  "blob_offset": 457692,
                  "bytes": "270102eff217"
                },
                "field_refs": [
                  "reward_pool_data_base.key=457634",
                  "pool_id=391535 slot=2",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 12,
              "name": "极光剑交易盒",
              "display_name": "极光剑交易盒",
              "source_internal_marker": "极光剑交易盒",
              "prob": 0.18519,
              "prob_note": "0.18519",
              "config_exp": "2027-01-17",
              "item_id": 139263,
              "quantity": 1,
              "leaf": [
                139263,
                1
              ],
              "broadcast_content": "恭喜{0}鸿运当头，在帝皇铠甲活动中获得{1:format_item_name}",
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 539034,
                "pool_slot_encoding": {
                  "blob_offset": 539076,
                  "bytes": "270102eff217"
                },
                "field_refs": [
                  "reward_pool_data_base.key=539034",
                  "pool_id=391535 slot=12",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 14,
              "name": "异变核芯-凝华效应",
              "display_name": "异变核芯-凝华效应",
              "source_internal_marker": "异变核芯-凝华效应",
              "prob": 0.23413,
              "prob_note": "0.23413",
              "config_exp": "2027-01-17",
              "item_id": 660078,
              "quantity": 1,
              "leaf": [
                660078,
                1
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 538453,
                "pool_slot_encoding": {
                  "blob_offset": 538484,
                  "bytes": "270102eff217"
                },
                "field_refs": [
                  "reward_pool_data_base.key=538453",
                  "pool_id=391535 slot=14",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 15,
              "name": "异变核芯-电极效应",
              "display_name": "异变核芯-电极效应",
              "source_internal_marker": "异变核芯-电极效应",
              "prob": 0.28096,
              "prob_note": "0.28096",
              "config_exp": "2027-01-17",
              "item_id": 660066,
              "quantity": 1,
              "leaf": [
                660066,
                1
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 539228,
                "pool_slot_encoding": {
                  "blob_offset": 539259,
                  "bytes": "270102eff217"
                },
                "field_refs": [
                  "reward_pool_data_base.key=539228",
                  "pool_id=391535 slot=15",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            }
          ]
        },
        {
          "pool_id": 391767,
          "name": "lottery 池（kj1 key230 引用；帝皇期 3 行普通奖励）",
          "rows": [
            {
              "slot": 16,
              "name": "1型记忆材料",
              "display_name": "1型记忆材料",
              "source_internal_marker": "1型记忆材料",
              "prob": 0.02586,
              "prob_note": "0.02586",
              "config_exp": "2027-01-17",
              "item_id": 151784,
              "quantity": 5,
              "leaf": [
                151784,
                5
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 4478,
                "pool_slot_encoding": {
                  "blob_offset": 4520,
                  "bytes": "270102d7f417"
                },
                "field_refs": [
                  "reward_pool_data_base.key=4478",
                  "pool_id=391767 slot=16",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 17,
              "name": "重构分子",
              "display_name": "重构分子",
              "source_internal_marker": "重构分子",
              "prob": 0.07201,
              "prob_note": "0.07201",
              "config_exp": "2027-01-17",
              "item_id": 151783,
              "quantity": 50,
              "leaf": [
                151783,
                50
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 4979,
                "pool_slot_encoding": {
                  "blob_offset": 4478,
                  "bytes": "270102d7f417"
                },
                "field_refs": [
                  "reward_pool_data_base.key=4979",
                  "pool_id=391767 slot=17",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 18,
              "name": "配方残页",
              "display_name": "配方残页",
              "source_internal_marker": "配方残页",
              "prob": 0.11607,
              "prob_note": "0.11607",
              "config_exp": "2027-01-17",
              "item_id": 150059,
              "quantity": 20,
              "leaf": [
                150059,
                20
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 4405,
                "pool_slot_encoding": {
                  "blob_offset": 4436,
                  "bytes": "270102d7f417"
                },
                "field_refs": [
                  "reward_pool_data_base.key=4405",
                  "pool_id=391767 slot=18",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            }
          ]
        },
        {
          "pool_id": 390699,
          "name": "孤儿候选池 · 活动引用未闭合（帝皇广播 9 行+同期普通 9 行）",
          "rows": [
            {
              "slot": 4,
              "name": "配方残页",
              "display_name": "配方残页",
              "source_internal_marker": "配方残页",
              "prob": 0.23215,
              "prob_note": "0.23215",
              "config_exp": "2027-01-17",
              "item_id": 150059,
              "quantity": 10,
              "leaf": [
                150059,
                10
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 31200,
                "pool_slot_encoding": {
                  "blob_offset": 31231,
                  "bytes": "270102abec17"
                },
                "field_refs": [
                  "reward_pool_data_base.key=31200",
                  "pool_id=390699 slot=4",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 5,
              "name": "纳米塑材自选箱",
              "display_name": "纳米塑材自选箱",
              "source_internal_marker": "纳米塑材自选箱",
              "prob": 0.14509,
              "prob_note": "0.14509",
              "config_exp": "2027-01-17",
              "item_id": 240116,
              "quantity": 1,
              "leaf": [
                240116,
                1
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 31087,
                "pool_slot_encoding": {
                  "blob_offset": 31119,
                  "bytes": "270102abec17"
                },
                "field_refs": [
                  "reward_pool_data_base.key=31087",
                  "pool_id=390699 slot=5",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 6,
              "name": "待取名",
              "display_name": "待取名",
              "source_internal_marker": "待取名",
              "prob": 0.07429,
              "prob_note": "0.07429",
              "config_exp": "2027-01-17",
              "item_id": 241006,
              "quantity": 1,
              "leaf": [
                241006,
                1
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 31000,
                "pool_slot_encoding": {
                  "blob_offset": 31031,
                  "bytes": "270102abec17"
                },
                "field_refs": [
                  "reward_pool_data_base.key=31000",
                  "pool_id=390699 slot=6",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 7,
              "name": "待取名",
              "display_name": "待取名",
              "source_internal_marker": "待取名",
              "prob": 0.17196,
              "prob_note": "0.17196",
              "config_exp": "2027-01-17",
              "item_id": 241007,
              "quantity": 1,
              "leaf": [
                241007,
                1
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 30919,
                "pool_slot_encoding": {
                  "blob_offset": 30950,
                  "bytes": "270102abec17"
                },
                "field_refs": [
                  "reward_pool_data_base.key=30919",
                  "pool_id=390699 slot=7",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 8,
              "name": "待取名",
              "display_name": "待取名",
              "source_internal_marker": "待取名",
              "prob": 0.02084,
              "prob_note": "0.02084",
              "config_exp": "2027-01-17",
              "item_id": 391768,
              "quantity": 1,
              "leaf": [
                391768,
                1
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 310137,
                "pool_slot_encoding": {
                  "blob_offset": 310192,
                  "bytes": "270102abec17"
                },
                "field_refs": [
                  "reward_pool_data_base.key=310137",
                  "pool_id=390699 slot=8",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 9,
              "name": "涂装：极光护卫",
              "display_name": "涂装：极光护卫",
              "source_internal_marker": "涂装：极光护卫",
              "prob": 0.00187,
              "prob_note": "0.00187",
              "config_exp": "2027-01-17",
              "item_id": 103020,
              "quantity": 1,
              "leaf": [
                103020,
                1
              ],
              "broadcast_content": "恭喜{0}鸿运当头，在帝皇铠甲活动中获得{1:format_item_name}",
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 362171,
                "pool_slot_encoding": {
                  "blob_offset": 362222,
                  "bytes": "270102abec17"
                },
                "field_refs": [
                  "reward_pool_data_base.key=362171",
                  "pool_id=390699 slot=9",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 10,
              "name": "涂装：银月白鸽",
              "display_name": "涂装：银月白鸽",
              "source_internal_marker": "涂装：银月白鸽",
              "prob": 0.00375,
              "prob_note": "0.00375",
              "config_exp": "2027-01-17",
              "item_id": 103019,
              "quantity": 1,
              "leaf": [
                103019,
                1
              ],
              "broadcast_content": "恭喜{0}鸿运当头，在帝皇铠甲活动中获得{1:format_item_name}",
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 333197,
                "pool_slot_encoding": {
                  "blob_offset": 333239,
                  "bytes": "270102abec17"
                },
                "field_refs": [
                  "reward_pool_data_base.key=333197",
                  "pool_id=390699 slot=10",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 11,
              "name": "配方:医疗无人机",
              "display_name": "配方:医疗无人机",
              "source_internal_marker": "配方:医疗无人机",
              "prob": 0.00625,
              "prob_note": "0.00625",
              "config_exp": "2027-01-17",
              "item_id": 103018,
              "quantity": 1,
              "leaf": [
                103018,
                1
              ],
              "broadcast_content": "恭喜{0}鸿运当头，在帝皇铠甲活动中获得{1:format_item_name}",
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 309898,
                "pool_slot_encoding": {
                  "blob_offset": 309934,
                  "bytes": "270102abec17"
                },
                "field_refs": [
                  "reward_pool_data_base.key=309898",
                  "pool_id=390699 slot=11",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 16,
              "name": "待取名",
              "display_name": "待取名",
              "source_internal_marker": "待取名",
              "prob": 0.00234,
              "prob_note": "0.00234",
              "config_exp": "2027-01-17",
              "item_id": 660078,
              "quantity": 1,
              "leaf": [
                660078,
                1
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 30727,
                "pool_slot_encoding": {
                  "blob_offset": 30764,
                  "bytes": "270102abec17"
                },
                "field_refs": [
                  "reward_pool_data_base.key=30727",
                  "pool_id=390699 slot=16",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 18,
              "name": "帝皇裁决交易盒",
              "display_name": "帝皇裁决交易盒",
              "source_internal_marker": "帝皇裁决交易盒",
              "prob": 0.00625,
              "prob_note": "0.00625",
              "config_exp": "2027-01-17",
              "item_id": 139265,
              "quantity": 1,
              "leaf": [
                139265,
                1
              ],
              "broadcast_content": "恭喜{0}鸿运当头，在帝皇铠甲活动中获得{1:format_item_name}",
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 30459,
                "pool_slot_encoding": {
                  "blob_offset": 30501,
                  "bytes": "270102abec17"
                },
                "field_refs": [
                  "reward_pool_data_base.key=30459",
                  "pool_id=390699 slot=18",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 19,
              "name": "帝皇瑞昭交易盒",
              "display_name": "帝皇瑞昭交易盒",
              "source_internal_marker": "帝皇瑞昭交易盒",
              "prob": 0.00625,
              "prob_note": "0.00625",
              "config_exp": "2027-01-17",
              "item_id": 139266,
              "quantity": 1,
              "leaf": [
                139266,
                1
              ],
              "broadcast_content": "恭喜{0}鸿运当头，在帝皇铠甲活动中获得{1:format_item_name}",
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 30280,
                "pool_slot_encoding": {
                  "blob_offset": 30322,
                  "bytes": "270102abec17"
                },
                "field_refs": [
                  "reward_pool_data_base.key=30280",
                  "pool_id=390699 slot=19",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 20,
              "name": "涂装:苍风",
              "display_name": "涂装:苍风",
              "source_internal_marker": "涂装:苍风",
              "prob": 0.00197,
              "prob_note": "0.00197",
              "config_exp": "2027-01-17",
              "item_id": 103223,
              "quantity": 1,
              "leaf": [
                103223,
                1
              ],
              "broadcast_content": "恭喜{0}鸿运当头，在帝皇铠甲活动中获得{1:format_item_name}",
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 432890,
                "pool_slot_encoding": {
                  "blob_offset": 432930,
                  "bytes": "270102abec17"
                },
                "field_refs": [
                  "reward_pool_data_base.key=432890",
                  "pool_id=390699 slot=20",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 21,
              "name": "涂装:青翼",
              "display_name": "涂装:青翼",
              "source_internal_marker": "涂装:青翼",
              "prob": 0.00375,
              "prob_note": "0.00375",
              "config_exp": "2027-01-17",
              "item_id": 103222,
              "quantity": 1,
              "leaf": [
                103222,
                1
              ],
              "broadcast_content": "恭喜{0}鸿运当头，在帝皇铠甲活动中获得{1:format_item_name}",
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 30033,
                "pool_slot_encoding": {
                  "blob_offset": 30080,
                  "bytes": "270102abec17"
                },
                "field_refs": [
                  "reward_pool_data_base.key=30033",
                  "pool_id=390699 slot=21",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 22,
              "name": "配方:盾甲金牛",
              "display_name": "配方:盾甲金牛",
              "source_internal_marker": "配方:盾甲金牛",
              "prob": 0.00625,
              "prob_note": "0.00625",
              "config_exp": "2027-01-17",
              "item_id": 103221,
              "quantity": 1,
              "leaf": [
                103221,
                1
              ],
              "broadcast_content": "恭喜{0}鸿运当头，在帝皇铠甲活动中获得{1:format_item_name}",
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 361760,
                "pool_slot_encoding": {
                  "blob_offset": 361796,
                  "bytes": "270102abec17"
                },
                "field_refs": [
                  "reward_pool_data_base.key=361760",
                  "pool_id=390699 slot=22",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 23,
              "name": "异变核芯-电极效应",
              "display_name": "异变核芯-电极效应",
              "source_internal_marker": "异变核芯-电极效应",
              "prob": 0.00234,
              "prob_note": "0.00234",
              "config_exp": "2027-01-17",
              "item_id": 660066,
              "quantity": 1,
              "leaf": [
                660066,
                1
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 310782,
                "pool_slot_encoding": {
                  "blob_offset": 310820,
                  "bytes": "270102abec17"
                },
                "field_refs": [
                  "reward_pool_data_base.key=310782",
                  "pool_id=390699 slot=23",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 29,
              "name": "能量电池",
              "display_name": "能量电池",
              "source_internal_marker": "能量电池",
              "prob": 0.0225,
              "prob_note": "0.0225",
              "config_exp": "2027-01-17",
              "item_id": 151994,
              "quantity": 10,
              "leaf": [
                151994,
                10
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 29115,
                "pool_slot_encoding": {
                  "blob_offset": 29150,
                  "bytes": "270102abec17"
                },
                "field_refs": [
                  "reward_pool_data_base.key=29115",
                  "pool_id=390699 slot=29",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 30,
              "name": "稀有微晶",
              "display_name": "稀有微晶",
              "source_internal_marker": "稀有微晶",
              "prob": 0.01471,
              "prob_note": "0.01471",
              "config_exp": "2027-01-17",
              "item_id": 151646,
              "quantity": 100,
              "leaf": [
                151646,
                100
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 29030,
                "pool_slot_encoding": {
                  "blob_offset": 29069,
                  "bytes": "270102abec17"
                },
                "field_refs": [
                  "reward_pool_data_base.key=29030",
                  "pool_id=390699 slot=30",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            },
            {
              "slot": 31,
              "name": "1型记忆材料",
              "display_name": "1型记忆材料",
              "source_internal_marker": "1型记忆材料",
              "prob": 0.01471,
              "prob_note": "0.01471",
              "config_exp": "2027-01-17",
              "item_id": 151784,
              "quantity": 5,
              "leaf": [
                151784,
                5
              ],
              "broadcast_content": null,
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 28945,
                "pool_slot_encoding": {
                  "blob_offset": 28984,
                  "bytes": "270102abec17"
                },
                "field_refs": [
                  "reward_pool_data_base.key=28945",
                  "pool_id=390699 slot=31",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            }
          ]
        },
        {
          "pool_id": 390716,
          "name": "孤儿候选池 · 活动引用未闭合（帝皇铠骑交易盒 1 行）",
          "rows": [
            {
              "slot": 9,
              "name": "帝皇铠骑交易盒",
              "display_name": "帝皇铠骑交易盒",
              "source_internal_marker": "帝皇铠骑交易盒",
              "prob": 0.14286,
              "prob_note": "0.14286",
              "config_exp": "2027-01-17",
              "item_id": 139262,
              "quantity": 1,
              "leaf": [
                139262,
                1
              ],
              "broadcast_content": "恭喜{0}鸿运当头，在帝皇铠甲活动中获得{1:format_item_name}",
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 310144,
                "pool_slot_encoding": {
                  "blob_offset": 464633,
                  "bytes": "270102bcec17"
                },
                "field_refs": [
                  "reward_pool_data_base.key=310144",
                  "pool_id=390716 slot=9",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            }
          ]
        },
        {
          "pool_id": 391760,
          "name": "孤儿候选池 · 活动引用未闭合（仿生蛛螯雪地版 1 行）",
          "rows": [
            {
              "slot": 16,
              "name": "涂装:仿生蛛螯雪地版",
              "display_name": "涂装:仿生蛛螯雪地版",
              "source_internal_marker": "涂装:仿生蛛螯雪地版",
              "prob": 0.00206,
              "prob_note": "0.00206",
              "config_exp": "2027-01-17",
              "item_id": 105742,
              "quantity": 1,
              "leaf": [
                105742,
                1
              ],
              "broadcast_content": "恭喜{0}鸿运当头，在帝皇铠甲活动中获得{1:format_item_name}",
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 5517,
                "pool_slot_encoding": {
                  "blob_offset": 5581,
                  "bytes": "270102d0f417"
                },
                "field_refs": [
                  "reward_pool_data_base.key=5517",
                  "pool_id=391760 slot=16",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            }
          ]
        },
        {
          "pool_id": 660078,
          "name": "孤儿候选池 · 活动引用未闭合（银翼号背包礼盒 1 行）",
          "rows": [
            {
              "slot": 1,
              "name": "银翼号背包礼盒",
              "display_name": "银翼号背包礼盒",
              "source_internal_marker": "银翼号背包礼盒",
              "prob": 0.00417,
              "prob_note": "0.00417",
              "config_exp": "2027-01-17",
              "item_id": 131216,
              "quantity": 1,
              "leaf": [
                131216,
                1
              ],
              "broadcast_content": "恭喜{0}鸿运当头，在帝皇铠甲活动中获得{1:format_item_name}",
              "evidence": "structure-only",
              "source": "reward_pool_data_base same-snapshot row via [pool_id,slot] marker; prob_note verbatim; not server-side odds",
              "provenance": {
                "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
                "source_entries": [
                  {
                    "entry_index": 21380,
                    "file_id": "D558884A36C972C5",
                    "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
                    "role": "reward_base"
                  },
                  {
                    "entry_index": 10496,
                    "file_id": "69E58821939CB515",
                    "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
                    "role": "reward_chs"
                  }
                ],
                "table": "reward_pool_data_base",
                "row_key": 30648,
                "pool_slot_encoding": {
                  "blob_offset": 5389,
                  "bytes": "270102eea428"
                },
                "field_refs": [
                  "reward_pool_data_base.key=30648",
                  "pool_id=660078 slot=1",
                  "reward_pool_data_base.note / prob_note / reward"
                ],
                "name_source": "reward_pool_data_base.note (source_internal_marker)"
              }
            }
          ]
        }
      ],
      "activity_pool_refs": [
        {
          "pool_id": 391535,
          "role": "lottery_id(kj1 key224)",
          "status": "referenced",
          "note": "kj1 覆盖 key224；帝皇铠甲/极光剑交易盒+双核芯；kj1 面板 [106426,132121,241787,133298] 与主表面板不同"
        },
        {
          "pool_id": 391767,
          "role": "lottery_id(kj1 key230)",
          "status": "referenced",
          "note": "帝皇期仅普通奖励 3 行（记忆材料/重构分子/配方残页）；slot19 游隼典藏=二期期(1801353599)复用行不展开"
        },
        {
          "pool_id": null,
          "role": "key223 覆盖",
          "status": "absent-in-kj1",
          "note": "kj1 行集无 key223（主表独有行）→ 简单服侧 223 配置缺失"
        },
        {
          "pool_id": 390699,
          "role": "reward_pool 孤儿候选",
          "status": "candidate-only",
          "note": "帝皇广播 9 行（裁决/瑞昭交易盒+苍风/青翼/盾甲金牛/医疗无人机/极光护卫/白鸽）+无广播普通行；无配置行引用"
        },
        {
          "pool_id": 390716,
          "role": "reward_pool 孤儿候选",
          "status": "candidate-only",
          "note": "帝皇铠骑交易盒 0.14286"
        },
        {
          "pool_id": 391760,
          "role": "reward_pool 孤儿候选",
          "status": "candidate-only",
          "note": "仿生蛛螯雪地版 0.00206"
        },
        {
          "pool_id": 660078,
          "role": "reward_pool 孤儿候选",
          "status": "candidate-only",
          "note": "银翼号背包礼盒 0.00417（660000 核芯段同 ID 空间）"
        }
      ],
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "simple branch = BA8 kj1 overlay chain; orphan candidate pools are NOT claimed as live simple-server pools",
      "provenance": {
        "source_lock_sha256": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
        "source_entries": [
          {
            "entry_index": 12545,
            "file_id": "7DDCFA4A4BF8050C",
            "decoded_sha256": "6920d9318022d724103bedbc927c2d420ed5ff12758921521b44037295add7a4",
            "role": "kj1_base"
          },
          {
            "entry_index": 9828,
            "file_id": "636E4A12A344E22F",
            "decoded_sha256": "9ce03f3f114a0439e52cb95056e95e3a3cdc0c148c58a1b432c9d0fb4ba56768",
            "role": "kj1_chs"
          },
          {
            "entry_index": 21380,
            "file_id": "D558884A36C972C5",
            "decoded_sha256": "1674b41b823c4a8c6b8e3cf88b13e1c87365025a0420e63e8578928261f99b10",
            "role": "reward_base"
          },
          {
            "entry_index": 10496,
            "file_id": "69E58821939CB515",
            "decoded_sha256": "1f2750097d5d619d9631f9b5fb7149ccef0b751d748c170dbc8ddb179339ce3f",
            "role": "reward_chs"
          }
        ],
        "table": "super_fashion_lottery_conf_data_auto_oversea_data_kj1 + reward_pool_data_base",
        "row_key": "224/230",
        "field_refs": [
          "kj1 key224.lottery_id=391535",
          "kj1 key230.lottery_id=391767",
          "reward_pool pools 391535/391767/390699/390716/391760/660078 rows exp=1800143999"
        ],
        "name_source": "reward note as source_internal_marker"
      }
    }
  ]
};
