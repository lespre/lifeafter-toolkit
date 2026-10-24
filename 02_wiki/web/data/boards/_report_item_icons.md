# 道具总表图标补齐报告（item_master_v01）

- 生成：2026-10-19
- 板：`data/boards/item_master_v01.json`（1189 条）
- 图标目录：`assets/item_icons/`（456 个 PNG）

## 总数 / 有图 / 未下发

| 项 | 条数 |
| --- | --- |
| 总条数 | 1189 |
| 有图（已导出） | 901 |
| 未下发 | 277 |
| 未解出（解码失败/无 PNG） | 0 |
| 无图标字段 | 11 |

## 双源命中

| 来源 | 条数 | 说明 |
| --- | --- | --- |
| PE .ktx | 891 | `icon`+`_b`/`_s`+`.ktx` → fid → pe_index(pack,row) → 解压/解码 |
| PC .bc7 | 10 | PE 未命中者再查 hit_table(path→pkg,row) → E:/mrzh/res 解 BC7 |
| 未下发 | 277 | 两源均无该路径 |

去重口径：不同 icon 路径 632 条（PE 有落点 446、PC 补 10），实际写盘 PNG 456 个（多 item 共用同一图只写一次）。

## 失败原因分类

| 原因 | 条数 |
| --- | --- |
| PE(174 包) 与 PC(hit_table 133k) 均无该路径 | 277 |
| 源表无该 item 行或 icon 字段为空 | 11 |

### 未下发集中度（按 icon 路径聚合）

| icon 路径 | 道具数 |
| --- | --- |
| `ui/item_icon/icon_150035` | 42 |
| `ui/item_icon/icon_zhekouquan_xingyunlihe_2` | 27 |
| `ui/ui/building_icon/icon_90043_b.png` | 9 |
| `ui/item_icon/icon_152270` | 8 |
| `ui/item_icon/icon_ksq_0008` | 7 |
| `ui/item_icon/icon_122336` | 5 |
| `ui/ui/building_icon/icon_90113_b.png` | 4 |
| `ui/item_icon/icon_jiajulihegaojijiquan` | 4 |
| `ui/item_icon/icon_120002` | 2 |
| `ui/item_icon/icon_170004` | 2 |

未下发样例：资源(7000)、冷兵器(7002)、护甲(7003)、投掷物(7004)、陷阱(7006)、一句歌词(122174)、一句歌词(122175)、一句歌词(122176)、一句歌词(122177)、一句歌词(122178)

## 已知现象（非缺陷）

- 白模图标 9 条：包内 RGB 全白、只有 alpha 形状（动作/舞蹈类道具），运行时按色值染色；板上以 `icon_note` 标注，未做任何重上色。
- 源表路径含重复 `ui/ui/` 段的 4 条：仅去掉重复段后同名资源确实存在才采用，记录 `_media.images[0].path_normalized_from`；未改 icon 名。

PE 导出运行计数：`{"png_written": 446}`

PC 导出运行计数：`{"png_written": 10}`

## 口径说明

- 图标字段与 item_master 同表同记录：`com\cdata\common_item_data_base.py` 的 `icon`，不做跨表字段 join。
- `_media.images[i]` 记录 `png/base/suffix/pack/row/fid/resolved_path/width/height/via`，可逐条回溯到包内行。
- 未下发项 `_media.images=[]`、`icon_state="未下发"`；未使用 APK npk 图库或同名/同 id 图标兜底（其 fid 口径与路径哈希不通，按图匹配无法建立 1:1 归属）。
- `evidence / evidence_level / status_tags / provenance` 原样保留（status_tags 取值域由 publication_policy 冻结）。
