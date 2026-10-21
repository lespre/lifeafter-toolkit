window.WIKI_BOARD_chip_lottery_guarantee_panel_static = {
  "meta": {
    "name": "限定芯片抽奖 · 每期全部芯片/研制池内容（半闭合）",
    "category": "四、奖池 / （六）限定芯片保底",
    "source_server": "简单生存服",
    "package_sha": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
    "generated": "2026-09-11",
    "evidence": "structure",
    "notes": "芯片保底 conf/rule 与 huodong 期次；当前期启用 conf 无静态 selector；保底次数为配置语义非当前期承诺。芯片板=每期 conf 配置一子卡（当期 UP 返厂组/新芯片/保底物全名单）。**双服差异（用户校准 2026-09-06）**：芯片返厂名单两服不同——本板 conf 来自 BA8（简单生存服测试包），如 30 期=连环暴击（简单服无破盾强攻故替换）；经典服同期名单由服务端下发且不同（30 期经典=破盾强攻）。正式服包（79c0d06f）0 命中 special_chip 表=conf 为 BA8 专属打包；经典服名单不可静态读。核芯板=期次+研制池族内容。静态行级 0 unbound；当前期启用与 UP 本体=运行时 selector；本板不用历史期序预测当期内容，不声明保底承诺或当前概率。",
    "provenance": {
      "audit_status": "passed",
      "source_locks": [
        {
          "sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
          "bytes": 188064088,
          "mtime_ns": 1789049072167514500,
          "path_hint": "mrzh/Documents/script.py314.lc.npk (simple-survival test snapshot)"
        }
      ]
    }
  },
  "items": [
    {
      "id": "chip-period-1",
      "name": "芯片期 1（2023-05-25~2023-06-07 · ui8 · 保底 170）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 8,
      "当期芯片（UP 返厂组）": "330014(连环暴击), 331013(从容不迫)",
      "新芯片组": "（空）",
      "保底奖励": "240807(连环暴击自选箱)",
      "活动池": "[3]",
      "金芯片保底数": 80,
      "总保底数": 170,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 1,
        "field_refs": [
          "conf key 1 ui_id=8",
          "rule_ids=[1, 2]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "2023-05-25~2023-06-07",
      "activity_subtitle": "芯片系统首期·连环暴击/从容不迫登场",
      "time_source": "官方更新公告锚（mrzh.163.com）/用户实机锚/首期推定"
    },
    {
      "id": "chip-period-2",
      "name": "芯片期 2（时间待校准 · ui9 · 保底 170）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 9,
      "当期芯片（UP 返厂组）": "330013(雷霆一击), 331018(坚韧不拔)",
      "新芯片组": "（空）",
      "保底奖励": "240834(雷霆一击自选箱)",
      "活动池": "[4]",
      "金芯片保底数": 80,
      "总保底数": 170,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 2,
        "field_refs": [
          "conf key 2 ui_id=9",
          "rule_ids=[3, 4]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "（时间待校准：2025-07+ 公告不再宣传/官网清档，勿用行序猜测）",
      "activity_subtitle": "待校准",
      "time_source": "待校准（无公告/用户锚）"
    },
    {
      "id": "chip-period-3",
      "name": "芯片期 3（时间待校准 · ui10 · 保底 170）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 10,
      "当期芯片（UP 返厂组）": "331025(以攻为守), 330014(连环暴击)",
      "新芯片组": "331025(以攻为守)",
      "保底奖励": "240851(以攻为守自选箱)",
      "活动池": "[5]",
      "金芯片保底数": 80,
      "总保底数": 170,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 3,
        "field_refs": [
          "conf key 3 ui_id=10",
          "rule_ids=[5, 6]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "（时间待校准：2025-07+ 公告不再宣传/官网清档，勿用行序猜测）",
      "activity_subtitle": "待校准",
      "time_source": "待校准（无公告/用户锚）"
    },
    {
      "id": "chip-period-4",
      "name": "芯片期 4（时间待校准 · ui11 · 保底 170）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 11,
      "当期芯片（UP 返厂组）": "330034(定点击破), 331012(全副武装)",
      "新芯片组": "330034(定点击破)",
      "保底奖励": "240983(定点击破自选箱)",
      "活动池": "[6]",
      "金芯片保底数": 80,
      "总保底数": 170,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 4,
        "field_refs": [
          "conf key 4 ui_id=11",
          "rule_ids=[7, 8]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "（时间待校准：2025-07+ 公告不再宣传/官网清档，勿用行序猜测）",
      "activity_subtitle": "待校准",
      "time_source": "待校准（无公告/用户锚）"
    },
    {
      "id": "chip-period-5",
      "name": "芯片期 5（时间待校准 · ui12 · 保底 170）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 12,
      "当期芯片（UP 返厂组）": "330025(异变赋能), 331015(荆棘护盾)",
      "新芯片组": "（空）",
      "保底奖励": "241011(异变赋能自选箱)",
      "活动池": "[7]",
      "金芯片保底数": 80,
      "总保底数": 170,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 5,
        "field_refs": [
          "conf key 5 ui_id=12",
          "rule_ids=[9, 10]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "（时间待校准：2025-07+ 公告不再宣传/官网清档，勿用行序猜测）",
      "activity_subtitle": "待校准",
      "time_source": "待校准（无公告/用户锚）"
    },
    {
      "id": "chip-period-6",
      "name": "芯片期 6（时间待校准 · ui13 · 保底 170）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 13,
      "当期芯片（UP 返厂组）": "330021(高能弹匣), 331025(以攻为守)",
      "新芯片组": "（空）",
      "保底奖励": "241039(高能弹匣自选箱)",
      "活动池": "[8]",
      "金芯片保底数": 80,
      "总保底数": 170,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 6,
        "field_refs": [
          "conf key 6 ui_id=13",
          "rule_ids=[11, 12]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "（时间待校准：2025-07+ 公告不再宣传/官网清档，勿用行序猜测）",
      "activity_subtitle": "待校准",
      "time_source": "待校准（无公告/用户锚）"
    },
    {
      "id": "chip-period-7",
      "name": "芯片期 7（时间待校准 · ui14 · 保底 170）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 14,
      "当期芯片（UP 返厂组）": "330035(强击连发), 331013(从容不迫)",
      "新芯片组": "330035(强击连发)",
      "保底奖励": "241052(强击连发自选箱)",
      "活动池": "[9]",
      "金芯片保底数": 80,
      "总保底数": 170,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 7,
        "field_refs": [
          "conf key 7 ui_id=14",
          "rule_ids=[13, 14]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "（时间待校准：2025-07+ 公告不再宣传/官网清档，勿用行序猜测）",
      "activity_subtitle": "待校准",
      "time_source": "待校准（无公告/用户锚）"
    },
    {
      "id": "chip-period-8",
      "name": "芯片期 8（时间待校准 · ui15 · 保底 170）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 15,
      "当期芯片（UP 返厂组）": "330032(异能压制), 331020(应急防御)",
      "新芯片组": "330032(异能压制)",
      "保底奖励": "241183(异能压制自选箱)",
      "活动池": "[10]",
      "金芯片保底数": 80,
      "总保底数": 170,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 8,
        "field_refs": [
          "conf key 8 ui_id=15",
          "rule_ids=[15, 16]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "（时间待校准：2025-07+ 公告不再宣传/官网清档，勿用行序猜测）",
      "activity_subtitle": "待校准",
      "time_source": "待校准（无公告/用户锚）"
    },
    {
      "id": "chip-period-9",
      "name": "芯片期 9（2024-06-13~2024-06-27 · ui16 · 保底 170）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 16,
      "当期芯片（UP 返厂组）": "331026(坚如磐石), 330016(格斗大师)",
      "新芯片组": "331026(坚如磐石)",
      "保底奖励": "241191(坚如磐石自选箱)",
      "活动池": "[11]",
      "金芯片保底数": 80,
      "总保底数": 170,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 9,
        "field_refs": [
          "conf key 9 ui_id=16",
          "rule_ids=[17, 18]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "2024-06-13~2024-06-27",
      "activity_subtitle": "坚如磐石/格斗大师登场",
      "time_source": "官方更新公告锚（mrzh.163.com）/用户实机锚/首期推定"
    },
    {
      "id": "chip-period-10",
      "name": "芯片期 10（2024-07-11~2024-07-25 · ui17 · 保底 170）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 17,
      "当期芯片（UP 返厂组）": "330013(雷霆一击), 331018(坚韧不拔)",
      "新芯片组": "（空）",
      "保底奖励": "241206(雷霆一击自选箱)",
      "活动池": "[12]",
      "金芯片保底数": 80,
      "总保底数": 170,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 10,
        "field_refs": [
          "conf key 10 ui_id=17",
          "rule_ids=[19, 20]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "2024-07-11~2024-07-25",
      "activity_subtitle": "雷霆一击/坚韧不拔登场",
      "time_source": "官方更新公告锚（mrzh.163.com）/用户实机锚/首期推定"
    },
    {
      "id": "chip-period-11",
      "name": "芯片期 11（2024-08-08~2024-08-22 · ui18 · 保底 170）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 18,
      "当期芯片（UP 返厂组）": "330037(爆裂收割), 331012(全副武装)",
      "新芯片组": "330037(爆裂收割), 330038(高压弹匣)",
      "保底奖励": "241368(爆裂收割自选箱)",
      "活动池": "[13]",
      "金芯片保底数": 80,
      "总保底数": 170,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 11,
        "field_refs": [
          "conf key 11 ui_id=18",
          "rule_ids=[21, 22]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "2024-08-08~2024-08-22",
      "activity_subtitle": "爆裂收割/全副武装登场",
      "time_source": "官方更新公告锚（mrzh.163.com）/用户实机锚/首期推定"
    },
    {
      "id": "chip-period-12",
      "name": "芯片期 12（2024-09-12~2024-09-26 · ui19 · 保底 170）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 19,
      "当期芯片（UP 返厂组）": "331027(寒霜守护), 330035(强击连发)",
      "新芯片组": "331027(寒霜守护), 331028(?)",
      "保底奖励": "241384(寒霜守护自选箱)",
      "活动池": "[14]",
      "金芯片保底数": 80,
      "总保底数": 170,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 12,
        "field_refs": [
          "conf key 12 ui_id=19",
          "rule_ids=[23, 24]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "2024-09-12~2024-09-26",
      "activity_subtitle": "寒霜守护/强击连发登场",
      "time_source": "官方更新公告锚（mrzh.163.com）/用户实机锚/首期推定"
    },
    {
      "id": "chip-period-13",
      "name": "芯片期 13（2024-10-10~2024-10-24 · ui20 · 保底 180）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 20,
      "当期芯片（UP 返厂组）": "330013(雷霆一击), 330014(连环暴击), 331015(荆棘护盾), 330025(异变赋能), 330021(高能弹匣), 331018(坚韧不拔), 331025(以攻为守), 331026(坚如磐石)",
      "新芯片组": "（空）",
      "保底奖励": "241405(限定特级芯片自选箱)；241405(限定特级芯片自选箱)",
      "活动池": "[15]",
      "金芯片保底数": 450,
      "总保底数": 180,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 13,
        "field_refs": [
          "conf key 13 ui_id=20",
          "rule_ids=[25, 26]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "2024-10-10~2024-10-24",
      "activity_subtitle": "8款返场·坚韧不拔/坚如磐石",
      "time_source": "官方更新公告锚（mrzh.163.com）/用户实机锚/首期推定"
    },
    {
      "id": "chip-period-14",
      "name": "芯片期 14（2024-11-21~2024-12-06 · ui21 · 保底 170）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 21,
      "当期芯片（UP 返厂组）": "330040(势如破竹), 331020(应急防御)",
      "新芯片组": "330040(势如破竹), 330039(不屈战意)",
      "保底奖励": "241429(势如破竹自选箱)",
      "活动池": "[16]",
      "金芯片保底数": 80,
      "总保底数": 170,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 14,
        "field_refs": [
          "conf key 14 ui_id=21",
          "rule_ids=[27, 28]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "2024-11-21~2024-12-06",
      "activity_subtitle": "势如破竹/应急防御登场",
      "time_source": "官方更新公告锚（mrzh.163.com）/用户实机锚/首期推定"
    },
    {
      "id": "chip-period-15",
      "name": "芯片期 15（2025-01-09~2025-02-13 · ui20 · 保底 180）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 20,
      "当期芯片（UP 返厂组）": "330014(连环暴击), 330032(异能压制), 330025(异变赋能), 330016(格斗大师), 330015(战术换弹), 331015(荆棘护盾), 331012(全副武装), 331013(从容不迫)",
      "新芯片组": "（空）",
      "保底奖励": "241513(限定特级芯片自选箱)；241513(限定特级芯片自选箱)",
      "活动池": "[17]",
      "金芯片保底数": 450,
      "总保底数": 180,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 15,
        "field_refs": [
          "conf key 15 ui_id=20",
          "rule_ids=[29, 30]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "2025-01-09~2025-02-13",
      "activity_subtitle": "8款返场·连环暴击/格斗大师",
      "time_source": "官方更新公告锚（mrzh.163.com）/用户实机锚/首期推定"
    },
    {
      "id": "chip-period-16",
      "name": "芯片期 16（2025-03-06~2025-03-20 · ui22 · 保底 170）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 22,
      "当期芯片（UP 返厂组）": "330041(蓄势待发), 331018(坚韧不拔)",
      "新芯片组": "330041(蓄势待发)",
      "保底奖励": "241545(蓄势待发自选箱)",
      "活动池": "[18]",
      "金芯片保底数": 80,
      "总保底数": 170,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 16,
        "field_refs": [
          "conf key 16 ui_id=22",
          "rule_ids=[31, 32]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "2025-03-06~2025-03-20",
      "activity_subtitle": "蓄势待发登场",
      "time_source": "官方更新公告锚（mrzh.163.com）/用户实机锚/首期推定"
    },
    {
      "id": "chip-period-17",
      "name": "芯片期 17（2025-04-17~2025-05-01 · ui20 · 保底 180）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 20,
      "当期芯片（UP 返厂组）": "330037(爆裂收割), 330026(狂猛奔袭), 330014(连环暴击), 330017(愈战愈勇), 331026(坚如磐石), 331020(应急防御), 331014(意识防护), 331027(寒霜守护)",
      "新芯片组": "（空）",
      "保底奖励": "241580(限定特级芯片自选箱)；241580(限定特级芯片自选箱)",
      "活动池": "[19]",
      "金芯片保底数": 450,
      "总保底数": 180,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 17,
        "field_refs": [
          "conf key 17 ui_id=20",
          "rule_ids=[33, 34]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "2025-04-17~2025-05-01",
      "activity_subtitle": "8款返场·爆裂收割/寒霜守护",
      "time_source": "官方更新公告锚（mrzh.163.com）/用户实机锚/首期推定"
    },
    {
      "id": "chip-period-18",
      "name": "芯片期 18（2025-05-29~2025-06-12 · ui23 · 保底 170）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 23,
      "当期芯片（UP 返厂组）": "330042(好事成双), 330034(定点击破)",
      "新芯片组": "330042(好事成双)",
      "保底奖励": "241611(好事成双自选箱)",
      "活动池": "[20]",
      "金芯片保底数": 80,
      "总保底数": 170,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 18,
        "field_refs": [
          "conf key 18 ui_id=23",
          "rule_ids=[35, 36]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "2025-05-29~2025-06-12",
      "activity_subtitle": "好事成双/定点击破登场",
      "time_source": "官方更新公告锚（mrzh.163.com）/用户实机锚/首期推定"
    },
    {
      "id": "chip-period-19",
      "name": "芯片期 19（2025-06-19~2025-07-03 · ui20 · 保底 180）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 20,
      "当期芯片（UP 返厂组）": "330014(连环暴击), 330013(雷霆一击), 330035(强击连发), 330021(高能弹匣), 331012(全副武装), 331013(从容不迫), 331025(以攻为守), 331015(荆棘护盾)",
      "新芯片组": "（空）",
      "保底奖励": "241622(限定特级芯片自选箱)；241622(限定特级芯片自选箱)",
      "活动池": "[21]",
      "金芯片保底数": 450,
      "总保底数": 180,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 19,
        "field_refs": [
          "conf key 19 ui_id=20",
          "rule_ids=[37, 38]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "2025-06-19~2025-07-03",
      "activity_subtitle": "8款返场·连环暴击/全副武装",
      "time_source": "官方更新公告锚（mrzh.163.com）/用户实机锚/首期推定"
    },
    {
      "id": "chip-period-20",
      "name": "芯片期 20（时间待校准 · ui20 · 保底 180）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 20,
      "当期芯片（UP 返厂组）": "330040(势如破竹), 330032(异能压制), 330014(连环暴击), 330026(狂猛奔袭), 331018(坚韧不拔), 331026(坚如磐石), 331027(寒霜守护), 331014(意识防护)",
      "新芯片组": "（空）",
      "保底奖励": "241645(限定特级芯片自选箱)；241645(限定特级芯片自选箱)",
      "活动池": "[22]",
      "金芯片保底数": 450,
      "总保底数": 180,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 20,
        "field_refs": [
          "conf key 20 ui_id=20",
          "rule_ids=[39, 40]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "（时间待校准：2025-07+ 公告不再宣传/官网清档，勿用行序猜测）",
      "activity_subtitle": "待校准",
      "time_source": "待校准（无公告/用户锚）"
    },
    {
      "id": "chip-period-21",
      "name": "芯片期 21（2025-09-18~2025-10-02 · ui24 · 保底 170）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 24,
      "当期芯片（UP 返厂组）": "331021(重整旗鼓), 330037(爆裂收割)",
      "新芯片组": "331021(重整旗鼓)",
      "保底奖励": "241678(重整旗鼓自选箱)",
      "活动池": "[23]",
      "金芯片保底数": 80,
      "总保底数": 170,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 21,
        "field_refs": [
          "conf key 21 ui_id=24",
          "rule_ids=[41, 42]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "2025-09-18~2025-10-02",
      "activity_subtitle": "重整旗鼓登场·ui24",
      "time_source": "官方更新公告锚（mrzh.163.com）/用户实机锚/首期推定"
    },
    {
      "id": "chip-period-22",
      "name": "芯片期 22（时间待校准 · ui20 · 保底 180）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 20,
      "当期芯片（UP 返厂组）": "330041(蓄势待发), 330024(全神贯注), 330035(强击连发), 330013(雷霆一击), 331015(荆棘护盾), 331020(应急防御), 331025(以攻为守), 331012(全副武装)",
      "新芯片组": "（空）",
      "保底奖励": "241710(限定特级芯片自选箱)；241710(限定特级芯片自选箱)",
      "活动池": "[24]",
      "金芯片保底数": 450,
      "总保底数": 180,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 22,
        "field_refs": [
          "conf key 22 ui_id=20",
          "rule_ids=[43, 44]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "（时间待校准：2025-07+ 公告不再宣传/官网清档，勿用行序猜测）",
      "activity_subtitle": "待校准",
      "time_source": "待校准（无公告/用户锚）"
    },
    {
      "id": "chip-period-23",
      "name": "芯片期 23（时间待校准 · ui25 · 保底 180）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 25,
      "当期芯片（UP 返厂组）": "330013(雷霆一击), 330025(异变赋能), 330016(格斗大师), 330032(异能压制), 331012(全副武装), 331013(从容不迫), 331018(坚韧不拔), 331020(应急防御)",
      "新芯片组": "（空）",
      "保底奖励": "241718(限定特级芯片自选箱)；241718(限定特级芯片自选箱)",
      "活动池": "[25]",
      "金芯片保底数": 450,
      "总保底数": 180,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 23,
        "field_refs": [
          "conf key 23 ui_id=25",
          "rule_ids=[45, 46]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "（时间待校准：2025-07+ 公告不再宣传/官网清档，勿用行序猜测）",
      "activity_subtitle": "待校准",
      "time_source": "待校准（无公告/用户锚）"
    },
    {
      "id": "chip-period-24",
      "name": "芯片期 24（时间待校准 · ui20 · 保底 180）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 20,
      "当期芯片（UP 返厂组）": "330042(好事成双), 330034(定点击破), 330016(格斗大师), 330014(连环暴击), 331013(从容不迫), 331014(意识防护), 331018(坚韧不拔), 331027(寒霜守护)",
      "新芯片组": "（空）",
      "保底奖励": "241736(限定特级芯片自选箱)；241736(限定特级芯片自选箱)",
      "活动池": "[26]",
      "金芯片保底数": 450,
      "总保底数": 180,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 24,
        "field_refs": [
          "conf key 24 ui_id=20",
          "rule_ids=[47, 48]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "（时间待校准：2025-07+ 公告不再宣传/官网清档，勿用行序猜测）",
      "activity_subtitle": "待校准",
      "time_source": "待校准（无公告/用户锚）"
    },
    {
      "id": "chip-period-25",
      "name": "芯片期 25（时间待校准 · ui20 · 保底 180）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 20,
      "当期芯片（UP 返厂组）": "330040(势如破竹), 330013(雷霆一击), 330017(愈战愈勇), 330041(蓄势待发), 331021(重整旗鼓), 331012(全副武装), 331015(荆棘护盾), 331026(坚如磐石)",
      "新芯片组": "（空）",
      "保底奖励": "241768(限定特级芯片自选箱)；241768(限定特级芯片自选箱)",
      "活动池": "[27]",
      "金芯片保底数": 450,
      "总保底数": 180,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 25,
        "field_refs": [
          "conf key 25 ui_id=20",
          "rule_ids=[49, 50]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "（时间待校准：2025-07+ 公告不再宣传/官网清档，勿用行序猜测）",
      "activity_subtitle": "待校准",
      "time_source": "待校准（无公告/用户锚）"
    },
    {
      "id": "chip-period-26",
      "name": "芯片期 26（时间待校准 · ui26 · 保底 170）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 26,
      "当期芯片（UP 返厂组）": "330044(覆盖打击), 331018(坚韧不拔)",
      "新芯片组": "330044(覆盖打击)",
      "保底奖励": "241800(覆盖打击自选箱)",
      "活动池": "[28]",
      "金芯片保底数": 80,
      "总保底数": 170,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 26,
        "field_refs": [
          "conf key 26 ui_id=26",
          "rule_ids=[51, 52]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "（时间待校准：2025-07+ 公告不再宣传/官网清档，勿用行序猜测）",
      "activity_subtitle": "待校准",
      "time_source": "待校准（无公告/用户锚）"
    },
    {
      "id": "chip-period-27",
      "name": "芯片期 27（2026-02-12~2026-03-04 · ui20 · 保底 180）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 20,
      "当期芯片（UP 返厂组）": "330014(连环暴击), 330035(强击连发), 330042(好事成双), 330040(势如破竹), 331012(全副武装), 331014(意识防护), 331018(坚韧不拔), 331027(寒霜守护)",
      "新芯片组": "（空）",
      "保底奖励": "241849(限定特级芯片自选箱)；241849(限定特级芯片自选箱)",
      "活动池": "[29]",
      "金芯片保底数": 450,
      "总保底数": 180,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 27,
        "field_refs": [
          "conf key 27 ui_id=20",
          "rule_ids=[53, 54]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "2026-02-12~2026-03-04",
      "activity_subtitle": "8款返场",
      "time_source": "官方更新公告锚（mrzh.163.com）/用户实机锚/首期推定"
    },
    {
      "id": "chip-period-28",
      "name": "芯片期 28（时间待校准 · ui27 · 保底 170）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 27,
      "当期芯片（UP 返厂组）": "330043(疾刃强斩), 331021(重整旗鼓)",
      "新芯片组": "330043(疾刃强斩)",
      "保底奖励": "241883(疾刃强斩自选箱)",
      "活动池": "[30]",
      "金芯片保底数": 80,
      "总保底数": 170,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 28,
        "field_refs": [
          "conf key 28 ui_id=27",
          "rule_ids=[55, 56]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "（时间待校准：2025-07+ 公告不再宣传/官网清档，勿用行序猜测）",
      "activity_subtitle": "待校准",
      "time_source": "待校准（无公告/用户锚）"
    },
    {
      "id": "chip-period-29",
      "name": "芯片期 29（2026-05-21~2026-06-04 · ui20 · 保底 180）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 20,
      "当期芯片（UP 返厂组）": "330037(爆裂收割), 330026(狂猛奔袭), 330014(连环暴击), 330017(愈战愈勇), 331026(坚如磐石), 331020(应急防御), 331014(意识防护), 331027(寒霜守护)",
      "新芯片组": "（空）",
      "保底奖励": "241580(限定特级芯片自选箱)；241580(限定特级芯片自选箱)",
      "活动池": "[31]",
      "金芯片保底数": 450,
      "总保底数": 180,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 29,
        "field_refs": [
          "conf key 29 ui_id=20",
          "rule_ids=[57, 58]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "2026-05-21~2026-06-04",
      "activity_subtitle": "8款返场·爆裂收割组",
      "time_source": "官方更新公告锚（mrzh.163.com）/用户实机锚/首期推定"
    },
    {
      "id": "chip-period-30",
      "name": "芯片期 30（2026-07-16~2026-08-05 · ui20 · 保底 180）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 20,
      "当期芯片（UP 返厂组）": "330014(连环暴击), 330044(覆盖打击), 330042(好事成双), 330040(势如破竹), 331012(全副武装), 331026(坚如磐石), 331018(坚韧不拔), 331015(荆棘护盾)",
      "新芯片组": "（空）",
      "保底奖励": "241931(限定特级芯片自选箱)；241931(限定特级芯片自选箱)",
      "活动池": "[32]",
      "金芯片保底数": 450,
      "总保底数": 180,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 30,
        "field_refs": [
          "conf key 30 ui_id=20",
          "rule_ids=[59, 60]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "2026-07-16~2026-08-05",
      "activity_subtitle": "破盾强攻返场(经典期名)/连环暴击UP(简单服)",
      "time_source": "官方更新公告锚（mrzh.163.com）/用户实机锚/首期推定"
    },
    {
      "id": "chip-period-31",
      "name": "芯片期 31（时间待校准 · ui20 · 保底 180）",
      "activity": "限定芯片抽奖（当期全部芯片）",
      "ui_id": 20,
      "当期芯片（UP 返厂组）": "330043(疾刃强斩), 330032(异能压制), 330034(定点击破), 330021(高能弹匣), 331025(以攻为守), 331013(从容不迫), 331014(意识防护), 331021(重整旗鼓)",
      "新芯片组": "（空）",
      "保底奖励": "241965(限定特级芯片自选箱)；241965(限定特级芯片自选箱)",
      "活动池": "[33]",
      "金芯片保底数": 450,
      "总保底数": 180,
      "折扣率": 0.9,
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 10546,
            "file_id": "628CEBDC133329C4",
            "decoded_sha256": "b03f8f516f529ca55260ae4c124941126abc15ab12649aa921657b6be9db430d",
            "role": "628CEBDC133329C4"
          },
          {
            "entry_index": 7448,
            "file_id": "46375D1E8EE4FB1E",
            "decoded_sha256": "29d64f85a6e4b94ffe7d8558112e4c051f8dbd9d7f757962995c8ad7369d2182",
            "role": "46375D1E8EE4FB1E"
          },
          {
            "entry_index": 23601,
            "file_id": "DA71481ED763F75B",
            "decoded_sha256": "d4ad10ef2270090bce207a1d6571c5357e93696a56291cff259a32403be1c75d",
            "role": "DA71481ED763F75B"
          },
          {
            "entry_index": 1724,
            "file_id": "1086806F30F390F1",
            "decoded_sha256": "03a95f7fcc03d94be7bfb8b0ab5e0c202321b5d8746901b0e943fb7f88b276e0",
            "role": "1086806F30F390F1"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 25794,
            "file_id": "EF3A8474A5E5F7A4",
            "decoded_sha256": "f10e0a16a7c4295c68d0c5fde26f5510c278cc01d50d71f3deb6478a5a647261",
            "role": "EF3A8474A5E5F7A4"
          }
        ],
        "table": "special_chip_lottery_hd_conf",
        "row_key": 31,
        "field_refs": [
          "conf key 31 ui_id=20",
          "rule_ids=[61, 62]",
          "up_chips/new_chips/active_pool_ids jump 组",
          "common_item 名册 join（33xxxx/24xxxx）"
        ],
        "name_source": "common_item name（名册层）；未命中 id 原样保留"
      },
      "activity_period": "（时间待校准：2025-07+ 公告不再宣传/官网清档，勿用行序猜测）",
      "activity_subtitle": "待校准",
      "time_source": "待校准（无公告/用户锚）"
    }
  ],
  "stats": {
    "period_rows": 31,
    "unbound": 0
  }
};
