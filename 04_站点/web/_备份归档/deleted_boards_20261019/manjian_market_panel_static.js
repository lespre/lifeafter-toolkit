window.WIKI_BOARD_manjian_market_panel_static = {
  "meta": {
    "name": "满减市场（活动族 + 灵笼满减补贴锚点链）",
    "category": "四、奖池 / （三）满减市场",
    "source_server": "简单生存服",
    "package_sha": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
    "generated": "2026-09-11",
    "evidence": "structure",
    "notes": "满减市场活动族：旧 ManJianHuoDong（2023-11~2024-06，goods 表 101 行=材料商品）与 新 DiscountMarketHD/满减补贴（2025-04~2026-06 各期，含 2026-04-16~30 灵笼满减补贴 key3402）。灵笼满减补贴锚点（用户验收）：白月魁交易盒/浮游炮/清镜识微/噬极=各名册行，链至活动注册；但 DiscountMarketHD 商品定价载体表静态缺失（模块名 0 命中 + 四锚点精确同现扫仅名册/公告/交易表），购买档位与规则=运行时；唯一直接活动引用=gift 136388 desc「灵笼满减活动结束后可交易」。本板不声明任何定价、补贴档位或当前售卖状态。",
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
      "id": "hd-2306",
      "name": "满减市场",
      "activity": "满减市场",
      "huodong_key": 2306,
      "hd_class": "ManJianHuoDong",
      "hd_type": "满减市场",
      "ui_class": "ManJianMarketUI",
      "start_date": "2023-11-23",
      "end_date": "2023-11-30",
      "sub_title": null,
      "server_scope": "旧满减市场（ManJianHuoDong）",
      "goods_carrier": "manjian_market_goods kj1/kjxq 101 行=材料类商品（2023-2024 轮）",
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "huodong_conf_data kj1 hd_class=ManJianHuoDong / DiscountMarketHD 活动行",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 27026,
            "file_id": "FB80FED51B8B4638",
            "decoded_sha256": "ef53cd565f852ea04ba78b9385555a4969613a805d7416c3ceaddd1aebd31719",
            "role": "FB80FED51B8B4638"
          },
          {
            "entry_index": 19427,
            "file_id": "B48257E8D36A5AD4",
            "decoded_sha256": "c3620cef26b169801e9c4c205f72c4396a3cce264220b145a9b6455d9b0e62fc",
            "role": "B48257E8D36A5AD4"
          }
        ],
        "table": "huodong_conf_data_auto_oversea_data_kj1",
        "row_key": 2306,
        "field_refs": [
          "hd_class=ManJianHuoDong",
          "name=满减市场",
          "start_ts/end_ts=1700679600/1701284398"
        ],
        "name_source": "huodong_conf_data name (activity roster label)"
      }
    },
    {
      "id": "hd-2478",
      "name": "满减市场",
      "activity": "满减市场",
      "huodong_key": 2478,
      "hd_class": "ManJianHuoDong",
      "hd_type": "满减市场",
      "ui_class": "ManJianMarketUI",
      "start_date": "2024-03-14",
      "end_date": "2024-03-21",
      "sub_title": "商品折扣减免",
      "server_scope": "旧满减市场（ManJianHuoDong）",
      "goods_carrier": "manjian_market_goods kj1/kjxq 101 行=材料类商品（2023-2024 轮）",
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "huodong_conf_data kj1 hd_class=ManJianHuoDong / DiscountMarketHD 活动行",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 27026,
            "file_id": "FB80FED51B8B4638",
            "decoded_sha256": "ef53cd565f852ea04ba78b9385555a4969613a805d7416c3ceaddd1aebd31719",
            "role": "FB80FED51B8B4638"
          },
          {
            "entry_index": 19427,
            "file_id": "B48257E8D36A5AD4",
            "decoded_sha256": "c3620cef26b169801e9c4c205f72c4396a3cce264220b145a9b6455d9b0e62fc",
            "role": "B48257E8D36A5AD4"
          }
        ],
        "table": "huodong_conf_data_auto_oversea_data_kj1",
        "row_key": 2478,
        "field_refs": [
          "hd_class=ManJianHuoDong",
          "name=满减市场",
          "start_ts/end_ts=1710356400/1710979198"
        ],
        "name_source": "huodong_conf_data name (activity roster label)"
      }
    },
    {
      "id": "hd-2562",
      "name": "满减市场",
      "activity": "满减市场",
      "huodong_key": 2562,
      "hd_class": "ManJianHuoDong",
      "hd_type": "满减市场",
      "ui_class": "ManJianMarketUI",
      "start_date": "2024-05-30",
      "end_date": "2024-06-06",
      "sub_title": "商品折扣减免",
      "server_scope": "旧满减市场（ManJianHuoDong）",
      "goods_carrier": "manjian_market_goods kj1/kjxq 101 行=材料类商品（2023-2024 轮）",
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "huodong_conf_data kj1 hd_class=ManJianHuoDong / DiscountMarketHD 活动行",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 27026,
            "file_id": "FB80FED51B8B4638",
            "decoded_sha256": "ef53cd565f852ea04ba78b9385555a4969613a805d7416c3ceaddd1aebd31719",
            "role": "FB80FED51B8B4638"
          },
          {
            "entry_index": 19427,
            "file_id": "B48257E8D36A5AD4",
            "decoded_sha256": "c3620cef26b169801e9c4c205f72c4396a3cce264220b145a9b6455d9b0e62fc",
            "role": "B48257E8D36A5AD4"
          }
        ],
        "table": "huodong_conf_data_auto_oversea_data_kj1",
        "row_key": 2562,
        "field_refs": [
          "hd_class=ManJianHuoDong",
          "name=满减市场",
          "start_ts/end_ts=1717009200.0/1717632000.0"
        ],
        "name_source": "huodong_conf_data name (activity roster label)"
      }
    },
    {
      "id": "hd-2964",
      "name": "南疆满减",
      "activity": "满减市场（满减补贴）",
      "huodong_key": 2964,
      "hd_class": "DiscountMarketHD",
      "hd_type": "新满减市场",
      "ui_class": "DiscountMarketHDUI",
      "start_date": "2025-04-17",
      "end_date": "2025-05-01",
      "sub_title": "满减购好礼",
      "server_scope": "新满减市场（DiscountMarketHD）",
      "goods_carrier": "DiscountMarketHD 商品定价载体表静态缺失（BA8 无该模块；价格/档位=运行时）",
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "huodong_conf_data kj1 hd_class=ManJianHuoDong / DiscountMarketHD 活动行",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 27026,
            "file_id": "FB80FED51B8B4638",
            "decoded_sha256": "ef53cd565f852ea04ba78b9385555a4969613a805d7416c3ceaddd1aebd31719",
            "role": "FB80FED51B8B4638"
          },
          {
            "entry_index": 19427,
            "file_id": "B48257E8D36A5AD4",
            "decoded_sha256": "c3620cef26b169801e9c4c205f72c4396a3cce264220b145a9b6455d9b0e62fc",
            "role": "B48257E8D36A5AD4"
          }
        ],
        "table": "huodong_conf_data_auto_oversea_data_kj1",
        "row_key": 2964,
        "field_refs": [
          "hd_class=DiscountMarketHD",
          "name=南疆满减",
          "start_ts/end_ts=1744848000.0/1746039600.0"
        ],
        "name_source": "huodong_conf_data name (activity roster label)"
      }
    },
    {
      "id": "hd-3014",
      "name": "流萤满减",
      "activity": "满减市场（满减补贴）",
      "huodong_key": 3014,
      "hd_class": "DiscountMarketHD",
      "hd_type": "新满减市场",
      "ui_class": "DiscountMarketHDUI",
      "start_date": "2025-06-12",
      "end_date": "2025-06-26",
      "sub_title": "满减购好礼",
      "server_scope": "新满减市场（DiscountMarketHD）",
      "goods_carrier": "DiscountMarketHD 商品定价载体表静态缺失（BA8 无该模块；价格/档位=运行时）",
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "huodong_conf_data kj1 hd_class=ManJianHuoDong / DiscountMarketHD 活动行",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 27026,
            "file_id": "FB80FED51B8B4638",
            "decoded_sha256": "ef53cd565f852ea04ba78b9385555a4969613a805d7416c3ceaddd1aebd31719",
            "role": "FB80FED51B8B4638"
          },
          {
            "entry_index": 19427,
            "file_id": "B48257E8D36A5AD4",
            "decoded_sha256": "c3620cef26b169801e9c4c205f72c4396a3cce264220b145a9b6455d9b0e62fc",
            "role": "B48257E8D36A5AD4"
          }
        ],
        "table": "huodong_conf_data_auto_oversea_data_kj1",
        "row_key": 3014,
        "field_refs": [
          "hd_class=DiscountMarketHD",
          "name=流萤满减",
          "start_ts/end_ts=1749686400.0/1750878000.0"
        ],
        "name_source": "huodong_conf_data name (activity roster label)"
      }
    },
    {
      "id": "hd-3115",
      "name": "青白满减补贴",
      "activity": "满减市场（满减补贴）",
      "huodong_key": 3115,
      "hd_class": "DiscountMarketHD",
      "hd_type": "新满减市场",
      "ui_class": "DiscountMarketHDUI",
      "start_date": "2025-08-28",
      "end_date": "2025-09-11",
      "sub_title": "青白传说共七夕",
      "server_scope": "新满减市场（DiscountMarketHD）",
      "goods_carrier": "DiscountMarketHD 商品定价载体表静态缺失（BA8 无该模块；价格/档位=运行时）",
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "huodong_conf_data kj1 hd_class=ManJianHuoDong / DiscountMarketHD 活动行",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 27026,
            "file_id": "FB80FED51B8B4638",
            "decoded_sha256": "ef53cd565f852ea04ba78b9385555a4969613a805d7416c3ceaddd1aebd31719",
            "role": "FB80FED51B8B4638"
          },
          {
            "entry_index": 19427,
            "file_id": "B48257E8D36A5AD4",
            "decoded_sha256": "c3620cef26b169801e9c4c205f72c4396a3cce264220b145a9b6455d9b0e62fc",
            "role": "B48257E8D36A5AD4"
          }
        ],
        "table": "huodong_conf_data_auto_oversea_data_kj1",
        "row_key": 3115,
        "field_refs": [
          "hd_class=DiscountMarketHD",
          "name=青白满减补贴",
          "start_ts/end_ts=1756339200.0/1757548799.0"
        ],
        "name_source": "huodong_conf_data name (activity roster label)"
      }
    },
    {
      "id": "hd-3145",
      "name": "丹枫满减补贴",
      "activity": "满减市场（满减补贴）",
      "huodong_key": 3145,
      "hd_class": "DiscountMarketHD",
      "hd_type": "新满减市场",
      "ui_class": "DiscountMarketHDUI",
      "start_date": "2025-10-02",
      "end_date": "2025-10-16",
      "sub_title": "红枫映月罗裙影",
      "server_scope": "新满减市场（DiscountMarketHD）",
      "goods_carrier": "DiscountMarketHD 商品定价载体表静态缺失（BA8 无该模块；价格/档位=运行时）",
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "huodong_conf_data kj1 hd_class=ManJianHuoDong / DiscountMarketHD 活动行",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 27026,
            "file_id": "FB80FED51B8B4638",
            "decoded_sha256": "ef53cd565f852ea04ba78b9385555a4969613a805d7416c3ceaddd1aebd31719",
            "role": "FB80FED51B8B4638"
          },
          {
            "entry_index": 19427,
            "file_id": "B48257E8D36A5AD4",
            "decoded_sha256": "c3620cef26b169801e9c4c205f72c4396a3cce264220b145a9b6455d9b0e62fc",
            "role": "B48257E8D36A5AD4"
          }
        ],
        "table": "huodong_conf_data_auto_oversea_data_kj1",
        "row_key": 3145,
        "field_refs": [
          "hd_class=DiscountMarketHD",
          "name=丹枫满减补贴",
          "start_ts/end_ts=1759363200.0/1760554800.0"
        ],
        "name_source": "huodong_conf_data name (activity roster label)"
      }
    },
    {
      "id": "hd-3215",
      "name": "鎏金满减补贴",
      "activity": "满减市场（满减补贴）",
      "huodong_key": 3215,
      "hd_class": "DiscountMarketHD",
      "hd_type": "新满减市场",
      "ui_class": "DiscountMarketHDUI",
      "start_date": "2025-11-27",
      "end_date": "2025-12-11",
      "sub_title": "闪耀舞夜流光",
      "server_scope": "新满减市场（DiscountMarketHD）",
      "goods_carrier": "DiscountMarketHD 商品定价载体表静态缺失（BA8 无该模块；价格/档位=运行时）",
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "huodong_conf_data kj1 hd_class=ManJianHuoDong / DiscountMarketHD 活动行",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 27026,
            "file_id": "FB80FED51B8B4638",
            "decoded_sha256": "ef53cd565f852ea04ba78b9385555a4969613a805d7416c3ceaddd1aebd31719",
            "role": "FB80FED51B8B4638"
          },
          {
            "entry_index": 19427,
            "file_id": "B48257E8D36A5AD4",
            "decoded_sha256": "c3620cef26b169801e9c4c205f72c4396a3cce264220b145a9b6455d9b0e62fc",
            "role": "B48257E8D36A5AD4"
          }
        ],
        "table": "huodong_conf_data_auto_oversea_data_kj1",
        "row_key": 3215,
        "field_refs": [
          "hd_class=DiscountMarketHD",
          "name=鎏金满减补贴",
          "start_ts/end_ts=1764201600.0/1765393200.0"
        ],
        "name_source": "huodong_conf_data name (activity roster label)"
      }
    },
    {
      "id": "hd-3402",
      "name": "灵笼满减补贴",
      "activity": "满减市场（满减补贴）",
      "huodong_key": 3402,
      "hd_class": "DiscountMarketHD",
      "hd_type": "新满减市场",
      "ui_class": "DiscountMarketHDUI",
      "start_date": "2026-04-16",
      "end_date": "2026-04-30",
      "sub_title": "希望如暗夜星辰",
      "server_scope": "新满减市场（DiscountMarketHD）",
      "goods_carrier": "DiscountMarketHD 商品定价载体表静态缺失（BA8 无该模块；价格/档位=运行时）",
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "huodong_conf_data kj1 hd_class=ManJianHuoDong / DiscountMarketHD 活动行；锚点商品为灵笼联动内容（用户验收），获取渠道证据=gift 136388 desc「灵笼满减活动结束后可交易」",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 27026,
            "file_id": "FB80FED51B8B4638",
            "decoded_sha256": "ef53cd565f852ea04ba78b9385555a4969613a805d7416c3ceaddd1aebd31719",
            "role": "FB80FED51B8B4638"
          },
          {
            "entry_index": 19427,
            "file_id": "B48257E8D36A5AD4",
            "decoded_sha256": "c3620cef26b169801e9c4c205f72c4396a3cce264220b145a9b6455d9b0e62fc",
            "role": "B48257E8D36A5AD4"
          },
          {
            "entry_index": 25337,
            "file_id": "EAA478C8DF60BD04",
            "decoded_sha256": "a1da44b4233511497c7b219680734c88039c143c775d825321dddb459b705499",
            "role": "EAA478C8DF60BD04"
          },
          {
            "entry_index": 1791,
            "file_id": "112DA9185C331789",
            "decoded_sha256": "e7ac2382c1b491bdd89d576647ef70a1b8ad621535d75bd6fe2d70da68702097",
            "role": "112DA9185C331789"
          },
          {
            "entry_index": 19394,
            "file_id": "B42760CCA41DBC25",
            "decoded_sha256": "a98006a644ae7e98ce09eea0d68e821ca0fa0c02f7cd4efa908aee602bd948f2",
            "role": "B42760CCA41DBC25"
          },
          {
            "entry_index": 3838,
            "file_id": "24947DBB72A943E5",
            "decoded_sha256": "73faff8a112ff4e4448caf981efebff6b04c4664f62129cd9f6eb6aa3ca3be80",
            "role": "24947DBB72A943E5"
          },
          {
            "entry_index": 11704,
            "file_id": "6CD197C9670A961C",
            "decoded_sha256": "78e203f0ea84ba1b84defc7895ad9d86d628f7fd1a6095d1eee2757958109afc",
            "role": "6CD197C9670A961C"
          },
          {
            "entry_index": 12772,
            "file_id": "765AB12F1D6EB0EA",
            "decoded_sha256": "b439ccc3cb761bbaea8695ebfbc44bdfc4d2536fc75e7893dd8ace13657c3837",
            "role": "765AB12F1D6EB0EA"
          }
        ],
        "table": "huodong_conf_data_auto_oversea_data_kj1",
        "row_key": 3402,
        "field_refs": [
          "hd_class=DiscountMarketHD",
          "name=灵笼满减补贴",
          "start_ts/end_ts=1776297600.0/1777507199.0",
          "锚点：白月魁交易盒=gift 136388（yk 通道增量 023502/001666，desc 直引灵笼满减活动）",
          "锚点：浮游炮=common_item 640041（+buff_data 伴身投影·浮游炮 1E23D0CBDFC4BEA7）",
          "锚点：清镜识微=player_appear 492700 face（+492701-492706 时限变体）",
          "锚点：噬极=weapon_skin 1110156 喷火器皮肤（噬髓腐蚀/噬炎蔓溢）"
        ],
        "name_source": "huodong_conf_data name (activity roster label)"
      },
      "锚点：白月魁交易盒": "gift_data_auto_oversea_data_yk（通道增量） key 136388 · 时装礼盒 · 打开礼包后，获得白月魁时装 1 份，包含头饰和身体；该交易盒可在灵笼满减活动结束后在跨服交易行进行交易。",
      "锚点：浮游炮（伴身投影）": "common_item_data_base key 640041 · 伴身投影道具 · 科技会研发的最新投影道具：源自灵笼科技，仅为外观装饰，不具备攻击效果。buff 名册：伴身投影·浮游炮。",
      "锚点：清镜识微": "player_module_appear_data key 492700 · 面饰（face，白月魁同款眼镜） · 白老板的同款眼镜，据说带上它就能于细微处洞见破局之机。「明日之后×灵笼」联动限定外观。",
      "锚点：噬极": "weapon_skin_data key 1110156 · 喷火器武器皮肤 · 腥荭素缠绕的血雾烈焰，吞噬一切生命源质的不详之火。「明日之后×灵笼」联动限定外观。"
    },
    {
      "id": "hd-3441",
      "name": "簪花满减补贴",
      "activity": "满减市场（满减补贴）",
      "huodong_key": 3441,
      "hd_class": "DiscountMarketHD",
      "hd_type": "新满减市场",
      "ui_class": "DiscountMarketHDUI",
      "start_date": "2026-05-21",
      "end_date": "2026-06-04",
      "sub_title": "簪花入鬓映芳华",
      "server_scope": "新满减市场（DiscountMarketHD）",
      "goods_carrier": "DiscountMarketHD 商品定价载体表静态缺失（BA8 无该模块；价格/档位=运行时）",
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "huodong_conf_data kj1 hd_class=ManJianHuoDong / DiscountMarketHD 活动行",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 27026,
            "file_id": "FB80FED51B8B4638",
            "decoded_sha256": "ef53cd565f852ea04ba78b9385555a4969613a805d7416c3ceaddd1aebd31719",
            "role": "FB80FED51B8B4638"
          },
          {
            "entry_index": 19427,
            "file_id": "B48257E8D36A5AD4",
            "decoded_sha256": "c3620cef26b169801e9c4c205f72c4396a3cce264220b145a9b6455d9b0e62fc",
            "role": "B48257E8D36A5AD4"
          }
        ],
        "table": "huodong_conf_data_auto_oversea_data_kj1",
        "row_key": 3441,
        "field_refs": [
          "hd_class=DiscountMarketHD",
          "name=簪花满减补贴",
          "start_ts/end_ts=1779321600.0/1780513200.0"
        ],
        "name_source": "huodong_conf_data name (activity roster label)"
      }
    },
    {
      "id": "hd-3590",
      "name": "银花满减补贴",
      "activity": "满减市场（满减补贴）",
      "huodong_key": 3590,
      "hd_class": "DiscountMarketHD",
      "hd_type": "新满减市场",
      "ui_class": "DiscountMarketHDUI",
      "start_date": "2026-09-17",
      "end_date": "2026-09-30",
      "sub_title": "点亮炽热与欢腾",
      "server_scope": "新满减市场（DiscountMarketHD）",
      "goods_carrier": "DiscountMarketHD 商品定价载体表静态缺失（BA8 无该模块；价格/档位=运行时）",
      "evidence": "structure",
      "evidence_level": "structure-only",
      "source": "huodong_conf_data kj1 hd_class=ManJianHuoDong / DiscountMarketHD 活动行",
      "provenance": {
        "source_lock_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
        "source_entries": [
          {
            "entry_index": 27026,
            "file_id": "FB80FED51B8B4638",
            "decoded_sha256": "ef53cd565f852ea04ba78b9385555a4969613a805d7416c3ceaddd1aebd31719",
            "role": "FB80FED51B8B4638"
          },
          {
            "entry_index": 19427,
            "file_id": "B48257E8D36A5AD4",
            "decoded_sha256": "c3620cef26b169801e9c4c205f72c4396a3cce264220b145a9b6455d9b0e62fc",
            "role": "B48257E8D36A5AD4"
          }
        ],
        "table": "huodong_conf_data_auto_oversea_data_kj1",
        "row_key": 3590,
        "field_refs": [
          "hd_class=DiscountMarketHD",
          "name=银花满减补贴",
          "start_ts/end_ts=1789603200.0/1790726399.0"
        ],
        "name_source": "huodong_conf_data name (activity roster label)"
      }
    }
  ],
  "stats": {
    "period_rows": 11,
    "anchor_rows": 4,
    "unbound": 26
  }
};
