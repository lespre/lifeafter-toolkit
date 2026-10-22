# Wiki 全量核对报告（2026-10-22）

## 范围

42 个板块 / 163,530 条，检查项：

```
meta 必填（name / category / package_sha / evidence）
item id 唯一性
provenance 八字段（source_id / source_lock_sha256 / table / row_key / field_refs / name_source / upstream / locator_chain）
evidence_level / status_tags 是否齐
配图文件是否真实存在
manifest 计数是否与板块一致
```

## 结果

```
板块        42
条目        163,530
manifest    计数全部一致
媒体缺失    0
问题板块    8 → 已修 3，剩余 5
```

## 已修（逐条对表核验后才补，不编）

| 板块 | 条数 | 核验方式 | 结果 |
|---|---|---|---|
| nucleus_entry_slots | 87 | 解码 `nucleus_entry_data`，entry_id 逐条比对 | 87/87 命中 |
| nucleus_item_catalog | 130 | item_id 对 `common_item_data`（经 item_master_full） | 130/130 命中 |
| text_notice_catalog | 1 | 补 `row_key` | 已补 |

回填内容包含真实表名、row_key、字段清单与定位链，`source_lock_sha256` 取自当前包锁。

## 未修（有明确原因，不伪造 provenance）

| 板块 | 条数 | 为什么现在补不了 |
|---|---|---|
| shop_static_candidates | 1,757 | `common_exchange_shop_data` 解析不出可用 key（0 条） |
| vehicle_catalog | 125 | `vehicle_basic_conf` 解码失败：`not a supported 0x76 index tail: 56055163` |
| nucleus | 108 | 只有 32 条 item_id 能在 item_master 里对上；其余是按 conf 维度组织的条目，缺行级键 |
| fashion_face | 180 | 来源是面饰专池（BA entry010816/009169）的名字池，无行键 |
| fashion_kaijia | 9 | 同上（主外观表 + 面饰池混合） |

这 5 个板块的条目目前只有 `source` 文本描述，没有可机读定位链。
正确做法不是填假 provenance，而是：

```
① 修 common_exchange_shop_data 的 0x76 索引变体解码
② 修 vehicle_basic_conf 的索引变体（0x56055163 尾巴）
③ fashion 类补「池 → 行」的映射表
④ nucleus 补 conf 维度到 item 的关联字段
```

## 产物

- 机器报告：`03_执行/30_分析/wiki_full_audit_20261022.json`
- 核对脚本：`04_站点/web/tools/audit_wiki_full.py`
- 回填脚本：`04_站点/web/tools/backfill_provenance.py`
